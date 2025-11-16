from enum import Enum
from typing import Dict


class SafetyMode(str, Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def mode_defaults(mode: SafetyMode) -> Dict[str, bool]:
    if mode == SafetyMode.STRICT:
        return {"block_on_any": True}
    if mode == SafetyMode.BALANCED:
        return {"block_on_injection_or_policy": True}
    if mode == SafetyMode.PERMISSIVE:
        return {"block_on_injection_only": True}
    return {}
