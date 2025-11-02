from rich import print
from vla.utils.config import load_config
from vla.scripts.eval_suite import evaluate
from vla.utils.metrics import Metrics

def main():
    cfg = load_config("defaults")
    agent = str(cfg["agent"]["name"])
    episodes = int(cfg["eval"]["episodes"])
    seed = int(cfg["seed"])

    m = Metrics(project="vla-lite", run_name=f"{agent}-e{episodes}-s{seed}", config=cfg)
    m.start()
    rate, success = evaluate(agent=agent, episodes=episodes, seed=seed, split="compositional")
    m.log({"success_rate": rate, "episodes": episodes, "seed": seed, "agent": agent})
    m.finish()
    print(f"{agent} success on held-out order: {rate:.2%}")

if __name__ == "__main__":
    main()
