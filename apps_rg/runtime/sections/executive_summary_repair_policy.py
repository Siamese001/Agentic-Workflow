"""Release repair policy for executive_summary — bounded same-authority only."""

from __future__ import annotations

import os

# Product path: no SRFS template finalizer, judge-safe rewrite, or density micro-expansion.
RELEASE_SRFS_LLM_REPAIR_ENABLED = False
RELEASE_SRFS_EMERGENCY_FINALIZER_ENABLED = False
RELEASE_SRFS_JUDGE_SAFE_REPAIR_ENABLED = False
RELEASE_SRFS_DENSITY_MICRO_EXPANSION_ENABLED = False

# Bounded same-authority synthesis regen (retry_qwen_for_synthesis).
RELEASE_SYNTHESIS_REGENERATION_ENABLED = True
SYNTHESIS_REGEN_MAX_ATTEMPTS = 2
SYNTHESIS_REGEN_MAX_ATTEMPTS_HARD_CAP = 3

# Graph-only path may deterministically reformat from allowed facts (not template finalizer).
RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED = True


def synthesis_regeneration_enabled() -> bool:
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN", "1").strip().lower()
    return RELEASE_SYNTHESIS_REGENERATION_ENABLED and raw not in ("0", "false", "no", "off")


def synthesis_regen_max_attempts() -> int:
    """Bounded LLM regen attempts (default 2, hard cap 3)."""
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS",
        str(SYNTHESIS_REGEN_MAX_ATTEMPTS),
    ).strip()
    try:
        n = int(raw)
    except ValueError:
        n = SYNTHESIS_REGEN_MAX_ATTEMPTS
    return max(1, min(n, SYNTHESIS_REGEN_MAX_ATTEMPTS_HARD_CAP))


# Post-X1D same-authority regen when X2 passed but judge quorum/median signals synthesis gap.
JUDGE_REGEN_MAX_ATTEMPTS = 1
RELEASE_JUDGE_REGENERATION_ENABLED = False


def judge_regeneration_enabled() -> bool:
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "0").strip().lower()
    return RELEASE_JUDGE_REGENERATION_ENABLED and raw in ("1", "true", "yes", "on")


def judge_safe_prefilter_enabled() -> bool:
    """Deterministic prose tighten before LLM judge regen (SRFS only)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_SAFE_PREFILTER", "0").strip().lower()
    return RELEASE_SRFS_JUDGE_SAFE_REPAIR_ENABLED and raw in ("1", "true", "yes", "on")
