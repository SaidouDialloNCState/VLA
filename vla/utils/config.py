from pathlib import Path
from typing import Any, Dict
from omegaconf import OmegaConf

def _extract_selections(cfg_dict: Dict[str, Any]) -> Dict[str, str]:
    sel = {}
    defaults = cfg_dict.get("defaults", [])
    for item in defaults:
        if isinstance(item, dict):
            sel.update(item)  # e.g., {"env": "gridworld", "agent": "planner", "eval": "default"}
    # allow explicit keys to override
    for k in ("env", "agent", "eval"):
        if k in cfg_dict and isinstance(cfg_dict[k], str):
            sel[k] = cfg_dict[k]
    # sensible fallbacks
    sel.setdefault("env", "gridworld")
    sel.setdefault("agent", "planner")
    sel.setdefault("eval", "default")
    return sel

def load_config(config_name: str = "defaults") -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[2]  # repo root
    conf_dir = root / "conf"
    base = OmegaConf.load(conf_dir / f"{config_name}.yaml")
    base_dict = OmegaConf.to_container(base, resolve=True)  # plain dict

    sel = _extract_selections(base_dict)

    env_cfg = OmegaConf.load(conf_dir / "env" / f"{sel['env']}.yaml")
    agent_cfg = OmegaConf.load(conf_dir / "agent" / f"{sel['agent']}.yaml")
    eval_cfg = OmegaConf.load(conf_dir / "eval" / f"{sel['eval']}.yaml")

    merged = {
        "seed": base_dict.get("seed", 0),
        "instruction": base_dict.get("instruction", "pick red then blue into bin"),
        "env": OmegaConf.to_container(env_cfg, resolve=True),
        "agent": OmegaConf.to_container(agent_cfg, resolve=True),
        "eval": OmegaConf.to_container(eval_cfg, resolve=True),
    }
    return merged
