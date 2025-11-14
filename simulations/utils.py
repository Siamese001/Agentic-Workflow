"""Utility helpers for simulation subsystem."""

from typing import Any, Dict


def model_to_payload(model: Any) -> Dict[str, Any]:
    """Return a dict of public fields from a pydantic model."""

    if model is None:
        return {}
    data = {}
    for key, value in getattr(model, "__dict__", {}).items():
        if key.startswith("__"):
            continue
        data[key] = value
    return data
