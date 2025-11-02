from typing import Iterator
from vla.schema.actions import Action, call_to_action
from vla.envs.gridworld import GridWorld
from vla.agents.llm_api import plan_step_function_call

def plan(env: GridWorld, instruction: str) -> Iterator[Action]:
    obs = env.observe()
    for _ in range(200):  # hard step cap
        call = plan_step_function_call(obs, instruction)   # function-calling stub or real LLM
        action = call_to_action(call)                      # strict validation

        # STEP FIRST, then yield so callers see post-step state
        obs = env.step(action)
        yield action

        if all(o["delivered"] for o in obs["objects"].values()):
            break
