from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError

# ---- Function-calling style ----
class Call(BaseModel):
    name: Literal["move","pick","place"]
    arguments: Dict[str, Any]

# ---- Concrete actions (strict, typed) ----
class ActMove(BaseModel):
    type: Literal["move"] = "move"
    direction: Literal["N","S","E","W"]

class ActPick(BaseModel):
    type: Literal["pick"] = "pick"
    color: Literal["red","blue"]

class ActPlace(BaseModel):
    type: Literal["place"] = "place"
    where: Literal["bin"]

Action = ActMove | ActPick | ActPlace

def parse_action(raw: dict) -> Action:
    """Validate a dict that already looks like {'type': 'move', ...}"""
    t = raw.get("type")
    try:
        if t == "move":
            return ActMove(**raw)
        if t == "pick":
            return ActPick(**raw)
        if t == "place":
            return ActPlace(**raw)
        raise ValueError(f"Unknown action type: {t}")
    except ValidationError as e:
        raise ValueError(f"Invalid action payload: {e}") from e

def call_to_action_dict(call: Call) -> Dict[str, Any]:
    """Convert function-call shape to our strict action dict."""
    if call.name == "move":
        d = call.arguments.get("direction")
        return {"type": "move", "direction": d}
    if call.name == "pick":
        c = call.arguments.get("color")
        return {"type": "pick", "color": c}
    if call.name == "place":
        w = call.arguments.get("where")
        return {"type": "place", "where": w}
    raise ValueError(f"Unknown call.name: {call.name}")

def call_to_action(call: Call) -> Action:
    """Call → strict Action model."""
    return parse_action(call_to_action_dict(call))
