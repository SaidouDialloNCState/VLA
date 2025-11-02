import json
import typer
from rich import print
from vla.envs.gridworld import GridWorld
from vla.utils.trace import TraceLogger
from vla.agents.heuristic import plan as heuristic_plan
from vla.agents.planner import plan as planner_plan

app = typer.Typer()

@app.command()
def main(instruction: str = "pick red then blue into bin",
         agent: str = "planner",
         seed: int = 0):
    env = GridWorld(seed=seed)
    logger = TraceLogger()

    print(f"[bold]Instruction:[/bold] {instruction}")
    print(f"[bold]Agent:[/bold] {agent}")

    obs = env.observe()
    logger.log(event="reset", obs=obs, instruction=instruction, agent=agent, seed=seed)

    planner = planner_plan if agent=="planner" else heuristic_plan

    for t, act in enumerate(planner(env, instruction), start=1):
        step = {"t": t, "action": act.model_dump() if hasattr(act,"model_dump") else act.__dict__}
        logger.log(event="act", **step)
        obs = env.observe()
        logger.log(event="obs", obs=obs)

    # outcome
    delivered = {c: int(o["delivered"]) for c,o in obs["objects"].items()}
    print("[green]Delivered:[/green]", delivered)
    logger.log(event="done", delivered=delivered)
    logger.close()

if __name__ == "__main__":
    app()
