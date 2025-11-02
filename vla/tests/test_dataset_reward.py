import json
from pathlib import Path
from vla.utils.reward import sequence_success

def test_sequence_success_ok():
    assert sequence_success(["red","blue"], ("red","blue")) == 1
    assert sequence_success(["blue","red"], ("red","blue")) == 0

def test_dataset_files_exist_and_nonempty():
    train = Path("data/instructions_train.jsonl")
    test = Path("data/instructions_test.jsonl")
    assert train.exists() and test.exists()
    assert train.stat().st_size > 0 and test.stat().st_size > 0
    # basic schema check on one line
    line = next(open(train, "r", encoding="utf-8"))
    obj = json.loads(line)
    assert "instruction" in obj and "order" in obj
