import re


def is_valid_tx_hash(tx_hash: str) -> bool:
    pattern = r"^0x[a-fA-F0-9]{64}$"
    return bool(re.match(pattern, tx_hash))
