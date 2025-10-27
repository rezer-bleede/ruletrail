import hashlib
from typing import Iterable


def compute_checksum(values: Iterable[str]) -> str:
    sha = hashlib.sha256()
    for value in values:
        sha.update(value.encode("utf-8"))
    return sha.hexdigest()
