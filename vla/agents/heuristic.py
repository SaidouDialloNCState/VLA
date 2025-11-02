from typing import List, Iterator
from vla.schema.actions import ActMove, ActPick, ActPlace, Action
from vla.envs.gridworld import GridWorld

def parse_instruction(text: str) -> List[str]:
    t = text.lower()
    # detect order of colors, with "then" handling
    have_red, have_blue = ("red" in t), ("blue" in t)
    if "then" in t and have_red and have_blue:
        return ["red","blue"] if t.index("red") < t.index("blue") else ["blue","red"]
    # default if only one or none explicitly found
    order = []
    if have_red: order.append("red")
    if have_blue: order.append("blue")
    return order or ["red","blue"]

def go_to(env: GridWorld, target):
    # generate ActMove steps from current agent pos to target (no env side-effects)
    ax, ay = env.agent.pos
    tx, ty = target
    while ax < tx: ax+=1; yield ActMove(direction="E")
    while ax > tx: ax-=1; yield ActMove(direction="W")
    while ay < ty: ay+=1; yield ActMove(direction="S")
    while ay > ty: ay-=1; yield ActMove(direction="N")

def plan(env: GridWorld, instruction: str) -> Iterator[Action]:
    order = parse_instruction(instruction)
    for color in order:
        obj = env.objs[color]

        # Move to object, stepping env BEFORE yielding so observers see post-step state
        for a in go_to(env, obj.pos):
            env.step(a)
            yield a

        a = ActPick(color=color)
        env.step(a)
        yield a

        # Move to bin
        for a in go_to(env, env.bin):
            env.step(a)
            yield a

        a = ActPlace(where="bin")
        env.step(a)
        yield a
