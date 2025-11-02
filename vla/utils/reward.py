from typing import Iterable, Tuple

def sequence_success(delivered_seq: Iterable[str], required: Tuple[str,str]) -> int:
    """Return 1 if delivered sequence matches required order exactly, else 0."""
    return int(tuple(delivered_seq) == tuple(required))
