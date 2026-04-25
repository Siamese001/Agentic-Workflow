"""Taxonomy resolver — derives capability vs regression class for a scorecard row.

SSOT for taxonomy-aware regression tolerance, per
apps_eval/config/eval_policies.yaml `taxonomy_aware_regression_policy` block.

Added 2026-04-25 per runtime-gate-coverage-hardening-7e3f1a (G9 gap).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

_log = logging.getLogger(__name__)

_DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "eval_policies.yaml"

# Hard-coded fallback so callers degrade gracefully if YAML is missing or malformed.
# Mirrors the legacy single-threshold behaviour (0.05) but classifies as `regression`.
_FALLBACK_POLICY: dict[str, Any] = {
    "capability": {
        "tolerance_delta": 0.05,
        "verdicts": {
            "PASS": {"max_delta": 0.02},
            "WARN": {"max_delta": 0.05},
            "REGRESSION": {"min_delta": 0.05},
        },
    },
    "regression": {
        "tolerance_delta": 0.005,
        "verdicts": {
            "PASS": {"max_delta": 0.002},
            "WARN": {"max_delta": 0.005},
            "REGRESSION": {"min_delta": 0.005},
        },
    },
    "default_class": "regression",
    "suite_id_prefix_map": {
        "cap_": "capability",
        "capability_": "capability",
        "reg_": "regression",
        "regression_": "regression",
    },
}


def load_taxonomy_policy(path: Path | None = None) -> dict[str, Any]:
    """Load taxonomy-aware regression policy from YAML, with fallback.

    Args:
        path: Override path to eval_policies.yaml. If None, uses the SSOT.

    Returns:
        The `taxonomy_aware_regression_policy` block, or _FALLBACK_POLICY if missing.
    """
    target = path or _DEFAULT_POLICY_PATH
    if not target.exists():
        _log.warning("[taxonomy] policy file %s missing; using fallback", target)
        return dict(_FALLBACK_POLICY)
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        _log.warning("[taxonomy] could not parse %s: %s; using fallback", target, exc)
        return dict(_FALLBACK_POLICY)
    block = raw.get("taxonomy_aware_regression_policy")
    if not isinstance(block, dict):
        _log.warning("[taxonomy] no `taxonomy_aware_regression_policy` block; using fallback")
        return dict(_FALLBACK_POLICY)
    return block


def resolve_taxonomy_class(
    *,
    explicit_class: str = "",
    suite_id: str = "",
    policy: dict[str, Any] | None = None,
) -> str:
    """Resolve taxonomy class: explicit > suite_id prefix > default.

    Args:
        explicit_class: An explicit class hint (e.g. ScorecardRow.taxonomy_class).
        suite_id: The originating suite_id; matched against `suite_id_prefix_map`.
        policy: Pre-loaded policy block (avoids repeated file reads).

    Returns:
        Either "capability" or "regression". Never returns empty.
    """
    pol = policy or load_taxonomy_policy()
    if explicit_class in ("capability", "regression"):
        return explicit_class
    if suite_id:
        prefix_map = pol.get("suite_id_prefix_map", {}) or {}
        for prefix, klass in prefix_map.items():
            if suite_id.startswith(prefix) and klass in ("capability", "regression"):
                return klass
    default = pol.get("default_class", "regression")
    return str(default) if default in ("capability", "regression") else "regression"


def tolerance_for_class(
    klass: str,
    policy: dict[str, Any] | None = None,
) -> float:
    """Return the regression tolerance_delta for a given taxonomy class."""
    pol = policy or load_taxonomy_policy()
    block = pol.get(klass, {}) if isinstance(pol.get(klass), dict) else {}
    delta = block.get("tolerance_delta")
    if isinstance(delta, (int, float)) and delta >= 0:
        return float(delta)
    # Fall through to fallback values if YAML is missing the field.
    fb = _FALLBACK_POLICY.get(klass, {})
    return float(fb.get("tolerance_delta", 0.05))
