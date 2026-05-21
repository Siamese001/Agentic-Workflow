"""apps_rg retrieval requirements profile loader.

W1: apps_rg owns the required_source_classes declaration.
This module must NOT import from agentic_core.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W1
"""
from __future__ import annotations

import functools
from pathlib import Path
import yaml

_PROFILE_PATH = (
    Path(__file__).parents[3]
    / "config"
    / "domain_contract"
    / "retrieval_requirements_profile.resume_generation.v1.yaml"
)

# Fallback tuple — matches c0_binding hardcoded default.
_FALLBACK_SOURCE_CLASSES: tuple[str, ...] = (
    "candidate_profile",
    "project_evidence",
    "approved_examples",
    "rubrics",
    "governance_docs",
    "receipts",
)


@functools.lru_cache(maxsize=1)
def load_retrieval_requirements_profile() -> dict:
    """Load and return the full retrieval requirements profile as a dict.

    Cached via lru_cache.  Call ``load_retrieval_requirements_profile.cache_clear()``
    to force reload (useful in tests).

    Returns
    -------
    dict
        The parsed YAML profile, or an empty dict on failure.
    """
    try:
        return yaml.safe_load(_PROFILE_PATH.read_text(encoding="utf-8")) or {}
    except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        return {}


def get_normative_source_classes() -> tuple[str, ...]:
    """Return the normative source classes declared in the profile YAML.

    Falls back to a hardcoded tuple if the YAML cannot be loaded so that
    tests and production code degrade gracefully.

    Returns
    -------
    tuple[str, ...]
        Ordered tuple of source class name strings.
    """
    try:
        data = yaml.safe_load(_PROFILE_PATH.read_text(encoding="utf-8"))
        classes = data.get("normative_source_classes") or data.get("required_source_classes", [])
        return tuple(str(c) for c in classes)
    except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        return _FALLBACK_SOURCE_CLASSES


def get_required_source_classes() -> tuple[str, ...]:
    """Return the full required_source_classes tuple from the profile."""
    try:
        data = yaml.safe_load(_PROFILE_PATH.read_text(encoding="utf-8"))
        classes = data.get("required_source_classes", [])
        return tuple(str(c) for c in classes)
    except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        return _FALLBACK_SOURCE_CLASSES


def get_briefing_modes() -> tuple[str, ...]:
    """Return the declared briefing modes from the profile."""
    try:
        data = yaml.safe_load(_PROFILE_PATH.read_text(encoding="utf-8"))
        return tuple(str(m) for m in data.get("briefing_modes", []))
    except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        return ("UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE")
