from enum import Enum
from typing import Dict


class SafetyMode(Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def mode_defaults(mode: SafetyMode) -> Dict[str, object]:
    """Return deterministic blocking defaults for the given safety mode."""

    if mode == SafetyMode.STRICT:
        return {"block_on": ["violation", "injection", "policy_denied"]}
    if mode == SafetyMode.BALANCED:
        return {"block_on": ["injection", "policy_denied"]}
    return {"block_on": ["injection"]}
