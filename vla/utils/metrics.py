import os, csv, time, json
from pathlib import Path
from typing import Any, Dict

class Metrics:
    def __init__(self, project: str = "vla-lite", run_name: str = None, config: Dict[str,Any] = None):
        self.mode = "csv"
        self.csv_path = None
        self.wandb = None
        self.started = False
        self.project = project
        self.run_name = run_name or time.strftime("%Y%m%d-%H%M%S")
        self.config = config or {}

    def start(self):
        use_wandb = os.environ.get("VLA_USE_WANDB", "0") == "1"
        if use_wandb:
            try:
                import wandb
                self.wandb = wandb
                self.wandb.init(project=self.project, name=self.run_name, config=self.config)
                self.mode = "wandb"
            except Exception:
                self._setup_csv()
        else:
            self._setup_csv()
        self.started = True

    def _setup_csv(self):
        Path("runs").mkdir(parents=True, exist_ok=True)
        self.csv_path = Path("runs") / "metrics.csv"
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=["ts","run","key","value"]).writeheader()

    def log(self, payload: Dict[str,Any]):
        assert self.started, "Call start() first"
        if self.mode == "wandb":
            self.wandb.log(payload)
        else:
            ts = int(time.time())
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["ts","run","key","value"])
                for k,v in payload.items():
                    w.writerow({"ts": ts, "run": self.run_name, "key": k, "value": json.dumps(v)})

    def finish(self):
        if self.mode == "wandb" and self.wandb:
            try: self.wandb.finish()
            except: pass
