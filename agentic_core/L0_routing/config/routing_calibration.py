"""SSOT loader for routing-calibration thresholds.

Plan: ``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` phase
W2.P1. Consolidates two scalar literals that lived as magic-numbers in
``abstain_contract.py`` (``DEFAULT_ABSTAIN_THRESHOLD``) and
``semantic_cache_manager.py`` (``similarity_threshold=0.98``).

Override order (highest priority first):

1. Explicit kwarg passed by caller.
2. Environment variable override:

   * ``AGENTIC_ABSTAIN_THRESHOLD`` for abstain floor.
   * ``AGENTIC_SIMILARITY_THRESHOLD`` for semantic-cache floor.

3. YAML SSOT at ``config/routing_calibration.yaml``.
4. Hardcoded last-resort fallback defined here (kept in sync with the
   YAML so unit tests that patch YAML off still pass).

The loader caches the parsed YAML per-process via ``functools.lru_cache``
so the hot path (every ``plan_abstain`` call) does not re-read disk. Call
:func:`reset_cache` from tests that mutate the YAML.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

# Hardcoded fallbacks — used ONLY when the YAML is missing or unparseable.
# Keep in sync with ``config/routing_calibration.yaml``.
_FALLBACK_ABSTAIN_THRESHOLD = 0.50
_FALLBACK_SIMILARITY_THRESHOLD = 0.98

_ENV_ABSTAIN = "AGENTIC_ABSTAIN_THRESHOLD"
_ENV_SIMILARITY = "AGENTIC_SIMILARITY_THRESHOLD"

# Repo-root-relative YAML location. Resolved once at import time.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML_PATH = _REPO_ROOT / "config" / "routing_calibration.yaml"


@lru_cache(maxsize=1)
def _load_yaml() -> dict[str, Any]:
    """Parse the YAML SSOT once per process. Empty dict on any read error."""
    if not _YAML_PATH.exists():
        return {}
    try:
        import yaml  # lazy — many pure-logic callers should not pay the import cost
    except ImportError:
        return {}
    try:
        raw = yaml.safe_load(_YAML_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return raw if isinstance(raw, dict) else {}


def reset_cache() -> None:
    """Clear the parsed-YAML cache. Intended for tests that mutate the YAML."""
    _load_yaml.cache_clear()


def _coerce_threshold(raw: Any, fallback: float) -> float:
    """Parse a threshold value; ignore malformed entries (return fallback)."""
    if isinstance(raw, (int, float)):
        value = float(raw)
    elif isinstance(raw, str):
        try:
            value = float(raw.strip())
        except ValueError:
            return fallback
    else:
        return fallback
    # Clamp into the documented closed interval; anything outside is a
    # config bug, not a runtime recovery path.
    if not 0.0 <= value <= 1.0:
        return fallback
    return value


def get_abstain_threshold() -> float:
    """Return the current abstain-decision floor.

    Order: ``AGENTIC_ABSTAIN_THRESHOLD`` env → YAML → fallback.
    """
    env = os.environ.get(_ENV_ABSTAIN)
    if env is not None:
        return _coerce_threshold(env, _FALLBACK_ABSTAIN_THRESHOLD)
    cfg = _load_yaml().get("abstain") or {}
    return _coerce_threshold(
        cfg.get("default_threshold"),
        _FALLBACK_ABSTAIN_THRESHOLD,
    )


def get_similarity_threshold(namespace: str | None = None) -> float:
    """Return the semantic-cache similarity floor.

    Order: ``AGENTIC_SIMILARITY_THRESHOLD`` env → YAML per-namespace map →
    YAML global similarity_threshold → fallback.

    ``namespace`` is threaded through so the per-namespace map added in
    Wave W3.P3 is a pure-config change with no call-site impact.
    """
    env = os.environ.get(_ENV_SIMILARITY)
    if env is not None:
        return _coerce_threshold(env, _FALLBACK_SIMILARITY_THRESHOLD)
    cfg = _load_yaml().get("semantic_cache") or {}
    # Per-namespace override (W3.P3 placeholder — currently empty by default).
    if namespace:
        per_ns = cfg.get("per_namespace_thresholds") or {}
        if isinstance(per_ns, dict) and namespace in per_ns:
            return _coerce_threshold(
                per_ns[namespace],
                _FALLBACK_SIMILARITY_THRESHOLD,
            )
    return _coerce_threshold(
        cfg.get("similarity_threshold"),
        _FALLBACK_SIMILARITY_THRESHOLD,
    )


# -----------------------------------------------------------------------------
# v12 L0 Routing thresholds — see
# docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v12.md §4.2.
#
# Additive getters that read the ``v12_routing:`` block in the same YAML SSOT.
# Env override pattern: AGENTIC_V12_<UPPER_SNAKE_NAME>.
# -----------------------------------------------------------------------------

_V12_FALLBACKS: dict[str, float] = {
    "classifier_surface_threshold": 0.72,
    "classifier_dominance_delta": 0.12,
    "r1b_semantic_match_threshold": 0.88,
    "r_casc_escalation_threshold": 0.55,
    "r_loop_quality_threshold": 0.85,
    "cold_start_conservative_threshold": 0.50,
    "loop_guard_efficiency_threshold": 0.40,
}

# Non-threshold ints (guardrail ceilings). Not clamped to [0,1].
_V12_INT_FALLBACKS: dict[str, int] = {
    "min_spans_for_loop_guard": 5,
    "r_casc_max_depth": 3,
    "r_loop_max_iterations": 3,
}


def _coerce_positive_int(raw: Any, fallback: int) -> int:
    """Parse a positive integer; fall back on malformed or non-positive input."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return fallback
    if value < 1:
        return fallback
    return value


def get_v12_threshold(name: str) -> float:
    """Return a v12 routing threshold in [0, 1].

    Raises KeyError for unknown names so typos are caught at dev time.
    """
    if name not in _V12_FALLBACKS:
        raise KeyError(f"unknown v12 routing threshold: {name!r}")
    env = os.environ.get(f"AGENTIC_V12_{name.upper()}")
    fallback = _V12_FALLBACKS[name]
    if env is not None:
        return _coerce_threshold(env, fallback)
    cfg = _load_yaml().get("v12_routing") or {}
    return _coerce_threshold(cfg.get(name), fallback)


def get_v12_int(name: str) -> int:
    """Return a v12 routing integer guardrail (e.g. max_depth, max_iterations).

    Raises KeyError for unknown names.
    """
    if name not in _V12_INT_FALLBACKS:
        raise KeyError(f"unknown v12 routing int param: {name!r}")
    env = os.environ.get(f"AGENTIC_V12_{name.upper()}")
    fallback = _V12_INT_FALLBACKS[name]
    if env is not None:
        return _coerce_positive_int(env, fallback)
    cfg = _load_yaml().get("v12_routing") or {}
    return _coerce_positive_int(cfg.get(name), fallback)


__all__ = [
    "get_abstain_threshold",
    "get_similarity_threshold",
    "get_v12_int",
    "get_v12_threshold",
    "reset_cache",
]
