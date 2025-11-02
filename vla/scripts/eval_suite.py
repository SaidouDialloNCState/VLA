import random
import statistics as stats
import typer
from typing import List, Tuple
from vla.envs.gridworld import GridWorld
from vla.agents.heuristic import plan as heuristic_plan, parse_instruction
from vla.agents.planner import plan as planner_plan

app = typer.Typer()

def make_instruction(order: Tuple[str,str]) -> str:
    return f"pick {order[0]} then {order[1]} into bin"

def evaluate(agent: str, episodes: int, seed: int=0, split: str="compositional"):
    rng = random.Random(seed)
    orders = [("red","blue"),("blue","red")]
    # Compositional split: train sees RB, test evaluates BR (or vice versa).
    if split == "compositional":
        train_order, test_order = orders[0], orders[1]
    else:
        train_order = rng.choice(orders); test_order = rng.choice(orders)

    success = []
    for i in range(episodes):
        env = GridWorld(seed=seed+i)
        instr = make_instruction(test_order)
        planner = planner_plan if agent=="planner" else heuristic_plan

        delivered_seq = []
        for act in planner(env, instr):
            # track delivered order for strict sequence success
            obs = env.observe()
            for c, o in obs["objects"].items():
                if o["delivered"] and c not in delivered_seq:
                    delivered_seq.append(c)

        # strict sequence success
        success.append(tuple(delivered_seq) == test_order)

    rate = sum(success)/len(success) if success else 0.0
    return rate, success

@app.command()
def main(agent: str = "planner", episodes: int = 50, seed: int = 0):
    rate, _ = evaluate(agent=agent, episodes=episodes, seed=seed, split="compositional")
    print(f"{agent} success on held-out order: {rate:.2%}")

if __name__ == "__main__":
    app()
