"""
World Model Contracts

Defines deterministic schemas for world-model facts and helpers to normalize
incoming data into canonical structures.
"""
from __future__ import annotations

from typing import Any, Dict, List

_ALLOWED_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_ORIGINS = {"retrieval", "user", "system"}


def _coerce_category(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_CATEGORIES:
        return value
    return "entity"


def _coerce_origin(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_ORIGINS:
        return value
    return "system"


def _coerce_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    return "" if value is None else str(value)


def normalize_world_facts(facts: List[dict]) -> List[Dict[str, Any]]:
    """Normalize a list of world facts into the deterministic schema."""

    normalized: List[Dict[str, Any]] = []
    for fact in facts or []:
        if isinstance(fact, dict):
            fact_copy: Dict[str, Any] = dict(fact)
        else:
            fact_copy = {"content": _coerce_content(fact)}

        fact_copy["category"] = _coerce_category(fact_copy.get("category"))
        fact_copy["origin"] = _coerce_origin(fact_copy.get("origin"))
        fact_copy["content"] = _coerce_content(fact_copy.get("content"))
        normalized.append(fact_copy)

    return normalized
