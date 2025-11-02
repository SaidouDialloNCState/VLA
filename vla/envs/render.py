from typing import Tuple, Dict
import numpy as np
from PIL import Image, ImageDraw

COLORS = {
    "bg": (255,255,255),
    "grid": (230,230,230),
    "agent": (0,0,0),
    "bin": (160,160,160),
    "red": (220,50,50),
    "blue": (40,80,220),
    "obstacle": (90,90,90),
}

def render_symbolic(obs: Dict, cell=32, margin=2) -> np.ndarray:
    w = max(obs.get("w", 5), 1)
    h = max(obs.get("h", 5), 1)
    W, H = w*cell, h*cell
    img = Image.new("RGB", (W, H), COLORS["bg"])
    drw = ImageDraw.Draw(img)

    # grid
    for x in range(0, W, cell):
        drw.line([(x,0), (x,H)], fill=COLORS["grid"])
    for y in range(0, H, cell):
        drw.line([(0,y), (W,y)], fill=COLORS["grid"])

    # obstacles (optional)
    for p in obs.get("obstacles", []):
        x,y = p
        drw.rectangle([x*cell+margin,y*cell+margin,(x+1)*cell-margin,(y+1)*cell-margin], fill=COLORS["obstacle"])

    # bin
    bx,by = tuple(obs["bin"])
    drw.rectangle([bx*cell+margin,by*cell+margin,(bx+1)*cell-margin,(by+1)*cell-margin], outline=COLORS["bin"], width=3)

    # objects
    for color, o in obs["objects"].items():
        if not o["delivered"]:
            x,y = tuple(o["pos"])
            drw.ellipse([x*cell+margin,y*cell+margin,(x+1)*cell-margin,(y+1)*cell-margin], fill=COLORS[color])

    # agent
    ax,ay = tuple(obs["agent"]["pos"])
    drw.ellipse([ax*cell+margin,ay*cell+margin,(ax+1)*cell-margin,(ay+1)*cell-margin], outline=COLORS["agent"], width=3)

    return np.array(img)
