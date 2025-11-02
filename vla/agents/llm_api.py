import os
from typing import Dict, Any, Tuple
from vla.schema.actions import Call
from vla.agents.heuristic import parse_instruction

def _t2(p) -> Tuple[int,int]:
    # robustly coerce list/tuple -> tuple[int,int]
    x, y = p
    return (int(x), int(y))

def _stub(observation: Dict[str, Any], goal: str) -> Call:
    agent = observation["agent"]; binpos = _t2(observation["bin"])
    holding = agent["holding"]; ax, ay = _t2(agent["pos"])

    if holding:
        bx, by = binpos
        if (ax, ay) == binpos:
            return Call(name="place", arguments={"where": "bin"})
        if ax < bx: return Call(name="move", arguments={"direction": "E"})
        if ax > bx: return Call(name="move", arguments={"direction": "W"})
        if ay < by: return Call(name="move", arguments={"direction": "S"})
        return Call(name="move", arguments={"direction": "N"})

    order = parse_instruction(goal)
    for color in order:
        obj = observation["objects"][color]
        if not obj["delivered"]:
            tx, ty = _t2(obj["pos"])
            if (ax, ay) == (tx, ty):
                return Call(name="pick", arguments={"color": color})
            if ax < tx: return Call(name="move", arguments={"direction": "E"})
            if ax > tx: return Call(name="move", arguments={"direction": "W"})
            if ay < ty: return Call(name="move", arguments={"direction": "S"})
            return Call(name="move", arguments={"direction": "N"})

    # Fallback
    return Call(name="move", arguments={"direction": "E"})

def plan_step_function_call(observation: Dict[str, Any], goal: str) -> Call:
    use_openai = os.environ.get("VLA_USE_OPENAI", "0") == "1"
    if not use_openai:
        return _stub(observation, goal)
    try:
        from vla.agents.llm_api_openai import plan_step_function_call_openai
        return plan_step_function_call_openai(observation, goal)
    except Exception:
        return _stub(observation, goal)
