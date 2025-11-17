"""
World Model Contracts — v10_9

Defines:
  • Deterministic schemas for world-model “facts”
  • Canonical normalization routines
  • Merge helpers for RAG + reasoning layers
  • Provenance and categorization rules
  • Side-effect-free transformations

This module is used by:
  • L1 Reasoning (context enrichment, fact grounding)
  • L2 Execution (RAG/tool results → world facts)
  • L3 Orchestration (state propagation)
  • L4 Memory (normalize_world_facts, prune)
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator


# ======================================================================
# CONSTANTS
# ======================================================================

_ALLOWED_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_ORIGINS = {"retrieval", "user", "system"}
_DEFAULT_CATEGORY = "entity"
_DEFAULT_ORIGIN = "system"


# ======================================================================
# MODELS
# ======================================================================

class WorldFact(BaseModel):
    """
    Canonical representation of a world-model fact.

    Fields:
      • category: "entity" | "event" | "relation"
      • origin:   "retrieval" | "user" | "system"
      • content:  normalized string payload
      • metadata: optional structured detail
    """

    category: str = Field(default=_DEFAULT_CATEGORY)
    origin: str = Field(default=_DEFAULT_ORIGIN)
    content: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "ignore"

    # ---------------------
    # Validation
    # ---------------------

    @validator("category")
    def validate_category(cls, v: str) -> str:
        if v not in _ALLOWED_CATEGORIES:
            return _DEFAULT_CATEGORY
        return v

    @validator("origin")
    def validate_origin(cls, v: str) -> str:
        if v not in _ALLOWED_ORIGINS:
            return _DEFAULT_ORIGIN
        return v

    @validator("content")
    def validate_content(cls, v: Any) -> str:
        if isinstance(v, str):
            return v
        if v is None:
            return ""
        return str(v)


# ======================================================================
# NORMALIZATION
# ======================================================================

def _coerce_category(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_CATEGORIES:
        return value
    return _DEFAULT_CATEGORY


def _coerce_origin(value: Any) -> str:
    if isinstance(value, str) and value in _ALLOWED_ORIGINS:
        return value
    return _DEFAULT_ORIGIN


def _coerce_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    return "" if value is None else str(value)


def normalize_world_facts(facts: List[dict]) -> List[Dict[str, Any]]:
    """
    Normalize world facts into deterministic dictionaries.

    This is L4 Memory's primary entry point.
    It returns raw dicts (not Pydantic models) to avoid state pollution.
    """

    normalized: List[Dict[str, Any]] = []

    for fact in facts or []:
        if isinstance(fact, dict):
            f: Dict[str, Any] = dict(fact)
        else:
            f = {"content": _coerce_content(fact)}

        fact_clean = {
            "category": _coerce_category(f.get("category")),
            "origin": _coerce_origin(f.get("origin")),
            "content": _coerce_content(f.get("content")),
            "metadata": f.get("metadata", {}) if isinstance(f.get("metadata"), dict) else {},
        }

        normalized.append(fact_clean)

    return normalized


# ======================================================================
# MERGE HELPERS
# ======================================================================

def merge_world_facts(existing: List[dict], new: List[dict]) -> List[dict]:
    """
    Merge and normalize two sets of world facts deterministically.
    Duplicate exact facts are deduplicated by (category, origin, content).
    """

    combined = normalize_world_facts(existing) + normalize_world_facts(new)

    # Deduplicate
    seen = set()
    deduped: List[dict] = []

    for f in combined:
        key = (f["category"], f["origin"], f["content"])
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    return deduped
