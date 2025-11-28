"""
Utilities — Patch Helpers

Deterministic utilities for applying nested state patches. The helpers avoid
side effects by working on deep copies and respect "__delete__" directives for
removing keys.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

from utils_types import StatePatch


def _merge_dict(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge dictionaries with deterministic ordering."""

    result = copy.deepcopy(base)
    for key in sorted(patch.keys()):
        value = patch[key]
        if isinstance(value, dict) and value.get("__delete__") is True:
            result.pop(key, None)
            continue

        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def apply_patch(state: Dict[str, Any], patch: StatePatch) -> Dict[str, Any]:
    """Apply a StatePatch to a state dictionary deterministically.

    The function returns a new state without mutating the original input.
    """

    if not isinstance(patch, dict):
        raise TypeError("StatePatch must be a dictionary")

    return _merge_dict(state, patch)
