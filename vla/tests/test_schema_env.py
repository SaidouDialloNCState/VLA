from vla.schema.actions import parse_action
from vla.envs.gridworld import GridWorld
from vla.agents.heuristic import plan as heuristic_plan

def test_action_schema_ok():
    a = parse_action({"type":"move","direction":"N"})
    b = parse_action({"type":"pick","color":"red"})
    c = parse_action({"type":"place","where":"bin"})
    assert a.direction == "N" and b.color == "red" and c.where == "bin"

def test_env_deliver_one():
    env = GridWorld(seed=123)
    instr = "pick red into bin"
    # planners step internally; just iterate actions
    for _ in heuristic_plan(env, instr):
        if env.objs["red"].delivered:
            break
    assert env.objs["red"].delivered is True
