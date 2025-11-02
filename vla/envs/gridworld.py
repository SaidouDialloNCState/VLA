from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Optional, List
import numpy as np
from vla.schema.actions import Action, ActMove, ActPick, ActPlace

@dataclass
class Obj:
    color: str
    pos: Tuple[int,int]
    delivered: bool = False

@dataclass
class AgentState:
    pos: Tuple[int,int]
    holding: Optional[str] = None

class GridWorld:
    def __init__(self, w=5, h=5, seed: int = 0, obstacle_prob: float = 0.0, size_jitter: int = 0):
        """
        obstacle_prob: probability per-cell of placing an obstacle (excludes agent start, objects, bin)
        size_jitter: sample w and h from [w-size_jitter, w+size_jitter] and [h-size_jitter, h+size_jitter]
        """
        self._base_w, self._base_h = w, h
        self.obstacle_prob = float(obstacle_prob)
        self.size_jitter = int(size_jitter)
        self.rng = np.random.default_rng(seed)
        # bin defined after size is set in reset
        self.bin = None
        self.reset(seed)

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        # jitter size if requested
        self.w = max(3, int(self._base_w + self.rng.integers(-self.size_jitter, self.size_jitter+1))) if self.size_jitter>0 else self._base_w
        self.h = max(3, int(self._base_h + self.rng.integers(-self.size_jitter, self.size_jitter+1))) if self.size_jitter>0 else self._base_h

        self.bin = (self.w-1, self.h-1)
        self.agent = AgentState(pos=(0,0), holding=None)

        red_pos = (int(self.rng.integers(0,self.w)), int(self.rng.integers(0,self.h)))
        blue_pos = (int(self.rng.integers(0,self.w)), int(self.rng.integers(0,self.h)))
        if red_pos == self.bin: red_pos = (0, self.h-1)
        if blue_pos == self.bin: blue_pos = (self.w-1, 0)
        self.objs = {
            "red": Obj("red", red_pos, False),
            "blue": Obj("blue", blue_pos, False),
        }

        # obstacles
        self.obstacles: List[Tuple[int,int]] = []
        if self.obstacle_prob > 0:
            for x in range(self.w):
                for y in range(self.h):
                    if (x,y) in [self.agent.pos, self.bin, red_pos, blue_pos]:
                        continue
                    if self.rng.random() < self.obstacle_prob:
                        self.obstacles.append((x,y))

        self.steps = 0
        return self.observe()

    def in_bounds(self, p): 
        x,y = p; return 0 <= x < self.w and 0 <= y < self.h

    def blocked(self, p):
        return p in self.obstacles

    def observe(self) -> Dict:
        return {
            "w": self.w, "h": self.h,
            "agent": {"pos": self.agent.pos, "holding": self.agent.holding},
            "objects": {c: {"pos": o.pos, "delivered": o.delivered} for c,o in self.objs.items()},
            "bin": self.bin,
            "obstacles": list(self.obstacles),
        }

    def step(self, a: Action) -> Dict:
        self.steps += 1
        if isinstance(a, ActMove):
            dx,dy = {"N":(0,-1),"S":(0,1),"E":(1,0),"W":(-1,0)}[a.direction]
            x,y = self.agent.pos
            np_pos = (x+dx, y+dy)
            if self.in_bounds(np_pos) and not self.blocked(np_pos):
                self.agent.pos = np_pos
        elif isinstance(a, ActPick):
            obj = self.objs[a.color]
            if self.agent.holding is None and obj.pos == self.agent.pos and not obj.delivered:
                self.agent.holding = a.color
        elif isinstance(a, ActPlace):
            if self.agent.holding is not None and self.agent.pos == self.bin:
                self.objs[self.agent.holding].delivered = True
                self.agent.holding = None
        return self.observe()

    def is_success_sequence(self, required: list[str]) -> bool:
        return all(self.objs[c].delivered for c in required)
