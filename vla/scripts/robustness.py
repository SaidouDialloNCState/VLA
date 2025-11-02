import csv
from pathlib import Path
from typing import List, Tuple
import numpy as np
from vla.envs.gridworld import GridWorld
from vla.agents.planner import plan as planner_plan

def bootstrap_ci(success_bools: List[bool], iters: int = 2000, alpha: float = 0.05):
    arr = np.array(success_bools, dtype=float)
    n = len(arr)
    stats = []
    rng = np.random.default_rng(0)
    for _ in range(iters):
        idx = rng.integers(0, n, size=n)
        stats.append(arr[idx].mean())
    low = np.quantile(stats, alpha/2)
    high = np.quantile(stats, 1 - alpha/2)
    return float(low), float(high)

def eval_setting(episodes: int, seed: int, obstacle_prob: float, size_jitter: int):
    order = ("blue","red")
    instr = f"pick {order[0]} then {order[1]} into bin"
    success = []
    for i in range(episodes):
        env = GridWorld(seed=seed+i, obstacle_prob=obstacle_prob, size_jitter=size_jitter)
        delivered_seq = []
        for act in planner_plan(env, instr):
            obs = env.observe()
            for c, o in obs["objects"].items():
                if o["delivered"] and c not in delivered_seq:
                    delivered_seq.append(c)
        success.append(tuple(delivered_seq) == order)
    rate = sum(success)/len(success)
    lo, hi = bootstrap_ci(success)
    return rate, lo, hi

def main(episodes=80, seed=0, out_csv="runs/robustness.csv"):
    Path("runs").mkdir(parents=True, exist_ok=True)
    rows = []
    settings = [
        {"obstacle_prob": 0.0, "size_jitter": 0},
        {"obstacle_prob": 0.1, "size_jitter": 0},
        {"obstacle_prob": 0.2, "size_jitter": 0},
        {"obstacle_prob": 0.0, "size_jitter": 1},
        {"obstacle_prob": 0.0, "size_jitter": 2},
    ]
    for s in settings:
        rate, lo, hi = eval_setting(episodes, seed, s["obstacle_prob"], s["size_jitter"])
        print(f"robustness {s}: {rate:.2%} (95% [{lo:.2%}, {hi:.2%}])")
        srow = dict(s); srow.update({"episodes": episodes, "seed": seed, "success_rate": f"{rate:.4f}", "ci_low": f"{lo:.4f}", "ci_high": f"{hi:.4f}"})
        rows.append(srow)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {out_csv}")

if __name__ == "__main__":
    main()
