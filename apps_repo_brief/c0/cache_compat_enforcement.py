"""
P3.13 — Cache Strict Compatibility Enforcement.

Runtime enforcement of cache_compat.yaml rules:
  - R1A exact cache: strict compat key must match exactly before terminal return.
  - R1B semantic cache: forbidden for BOARD_DOSSIER (board_gate R1B check).
  - Forbidden key patterns: must never appear in any cache lookup.

This module is called by the C0 cache lookup pathway BEFORE any terminal
return decision. It raises CacheCompatViolation (a ValueError subclass) on
hard violations so the cache miss path is forced.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.13
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class CacheCompatViolation(ValueError):
    """Raised when a cache lookup violates strict compat rules."""


def _load_cache_compat() -> dict[str, Any]:
    """Load cache_compat.yaml once."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("PyYAML required for cache compat enforcement") from exc
    _path = Path(__file__).resolve().parents[1] / "config" / "cache_compat.yaml"
    with open(_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


_CACHE_COMPAT: dict[str, Any] = {}


def _get_cache_compat() -> dict[str, Any]:
    global _CACHE_COMPAT
    if not _CACHE_COMPAT:
        _CACHE_COMPAT = _load_cache_compat()
    return _CACHE_COMPAT


def enforce_r1a_strict_compat(
    candidate_key: dict[str, Any],
    depth_profile: str,
) -> None:
    """
    Enforce R1A exact cache strict compatibility.

    Raises CacheCompatViolation if:
    - candidate_key is missing any required R1A strict-compat field.
    - candidate_key contains any forbidden pattern.

    Args:
        candidate_key: The proposed R1A cache key dict.
        depth_profile:  e.g. "REPO_BRIEF_BOARD_DOSSIER".

    Raises:
        CacheCompatViolation: on violation.
    """
    compat = _get_cache_compat()
    r1a = compat.get("r1a_exact_cache", {})
    required_fields = r1a.get("required_fields", [])
    # forbidden is a list of forbidden pattern name strings in cache_compat.yaml
    forbidden_names: list[str] = compat.get("forbidden", [])

    # Check required fields
    missing = [f for f in required_fields if f not in candidate_key]
    if missing:
        raise CacheCompatViolation(
            f"R1A strict compat: missing required key fields: {missing}. "
            f"Candidate key: {list(candidate_key.keys())}"
        )

    # Check forbidden patterns (name-based — log if any forbidden name present)
    if isinstance(forbidden_names, list):
        for field_val in candidate_key.values():
            if isinstance(field_val, str):
                for forbidden_name in forbidden_names:
                    if re.search(re.escape(forbidden_name), field_val):
                        raise CacheCompatViolation(
                            f"R1A key contains forbidden pattern name '{forbidden_name}' "
                            f"in value: {field_val!r}"
                        )


def enforce_r1b_semantic_cache_policy(
    depth_profile: str,
    is_terminal_return: bool,
) -> None:
    """
    Enforce R1B semantic cache policy.

    BOARD_DOSSIER: terminal return from R1B is FORBIDDEN (P3.12 board gate).
    Other profiles: terminal return from R1B is allowed.

    Args:
        depth_profile:      e.g. "REPO_BRIEF_BOARD_DOSSIER".
        is_terminal_return: True if the cache hit would result in terminal return
                            (i.e., skip C0 retrieval entirely).

    Raises:
        CacheCompatViolation: if board dossier attempts R1B terminal return.
    """
    if depth_profile == "REPO_BRIEF_BOARD_DOSSIER" and is_terminal_return:
        raise CacheCompatViolation(
            "BOARD_DOSSIER depth profile: R1B semantic cache terminal return is FORBIDDEN. "
            "Board briefs must always come from a live C0 run. "
            "See c0_depth_profiles.yaml board_gate_thresholds.semantic_cache_terminal_return."
        )
