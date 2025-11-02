from vla.schema.actions import Call, call_to_action, parse_action
from vla.agents.llm_api import plan_step_function_call

def test_call_to_action_roundtrip():
    c = Call(name="move", arguments={"direction":"N"})
    a = call_to_action(c)
    assert a.type == "move" and a.direction == "N"

def test_llm_stub_produces_valid_calls():
    obs = {"agent":{"pos":(0,0),"holding":None}, "objects":{"red":{"pos":(1,0),"delivered":False},"blue":{"pos":(4,4),"delivered":False}}, "bin":(4,4)}
    call = plan_step_function_call(obs, "pick red then blue into bin")
    # should be a valid function-call that converts to a valid action
    act = call_to_action(call)
    assert parse_action(act.model_dump()).type in {"move","pick","place"}
