from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError

# Base "function-call" style message
class Call(BaseModel):
    name: str
    arguments: dict

# Concrete actions (strict, typed)
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
    """Strictly validate any proposed action dict against schema."""
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
