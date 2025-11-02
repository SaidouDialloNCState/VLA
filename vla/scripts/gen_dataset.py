from pathlib import Path
import json
from typing import Iterable, Tuple

# Keep strict compositional split: train=(red,blue), test=(blue,red)
ORDERS = [("red","blue"), ("blue","red")]
SYN_A = ["pick", "grab", "collect"]
SYN_B = ["then", "and then", "after that"]
SYN_BIN = ["bin", "basket"]
SYN_PLACE = ["place", "put", "drop"]

def variants(order: Tuple[str,str]) -> Iterable[str]:
    a, b = order
    for verb in SYN_A:
        for glue in SYN_B:
            for into in SYN_PLACE:
                for obj in SYN_BIN:
                    yield f"{verb} {a} {glue} {b} into {obj}"
                    yield f"{into} {a} then {b} into the {obj}"
                    yield f"first {a}, {glue} {b} into {obj}"

def write_split(path: Path, order: Tuple[str,str]):
    with open(path, "w", encoding="utf-8") as f:
        for s in variants(order):
            f.write(json.dumps({"instruction": s, "order": order})+"\n")

def main(out_dir="data"):
    od = Path(out_dir); od.mkdir(parents=True, exist_ok=True)
    train_order, test_order = ORDERS[0], ORDERS[1]
    write_split(od/"instructions_train.jsonl", train_order)
    write_split(od/"instructions_test.jsonl", test_order)
    print("Wrote train/test with compositional split and synonyms.")

if __name__ == "__main__":
    main()
