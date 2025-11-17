"""
Metadata helpers for routing permissions.
"""
from __future__ import annotations

from typing import Any, Dict, Set

PERMITTED_MODELS: Set[str] = {"gpt-4o", "gpt-4o-mini"}
PERMITTED_ENDPOINTS: Set[str] = {"default", "fast"}


def evaluate_routing_permissions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return metadata describing routing allowance for the payload."""

    model = str(payload.get("model", "")).strip()
    endpoint = str(payload.get("endpoint", "")).strip()

    return {
        "model": model or None,
        "endpoint": endpoint or None,
        "model_allowed": bool(model) and model in PERMITTED_MODELS,
        "endpoint_allowed": bool(endpoint) and endpoint in PERMITTED_ENDPOINTS,
    }
