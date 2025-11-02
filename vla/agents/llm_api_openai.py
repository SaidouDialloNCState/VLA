import json, os, re
from typing import Dict, Any
from vla.schema.actions import Call

# Minimal JSON extractor
_JSON_RE = re.compile(r'\{.*\}', re.DOTALL)

SYSTEM_PROMPT = """You are a function-calling planner for a 2D grid robot.
Output ONLY a single JSON object with this exact schema:
{"name": "<move|pick|place>", "arguments": {...}}
- For move: {"direction": "N"|"S"|"E"|"W"}
- For pick: {"color": "red"|"blue"}
- For place: {"where": "bin"}
Do not add text, code fences, or comments. Only the JSON object."""

def _to_call(obj: Dict[str, Any]) -> Call:
    # Pydantic will validate values when constructing Call
    return Call(name=obj["name"], arguments=obj["arguments"])

def plan_step_function_call_openai(observation: Dict[str, Any], goal: str) -> Call:
    # Requires: pip install openai, and OPENAI_API_KEY in env
    # Optional model override via VLA_OPENAI_MODEL, defaults to gpt-4o-mini
    model = os.environ.get("VLA_OPENAI_MODEL", "gpt-4o-mini")
    try:
        from openai import OpenAI
        client = OpenAI()
        content = {
            "goal": goal,
            "observation": {
                "agent": observation["agent"],     # pos, holding
                "objects": observation["objects"], # positions, delivered
                "bin": observation["bin"],
            }
        }
        msg = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(content, ensure_ascii=False)}
            ]
        )
        text = msg.choices[0].message.content or ""
        # Extract JSON block
        m = _JSON_RE.search(text.strip())
        if not m:
            raise ValueError("No JSON found in LLM output")
        obj = json.loads(m.group(0))
        return _to_call(obj)
    except Exception:
        # If anything goes wrong (no key, bad output), return a safe N step east move
        return Call(name="move", arguments={"direction": "E"})
