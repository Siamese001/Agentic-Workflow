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


# Post-X1D same-authority regen when X2 passed but dimension/holistic signals synthesis gap.
# Default 1 Qwen cycle; post-regen rescores soft-failed judges only (not full 3-judge panel).
JUDGE_REGEN_MAX_ATTEMPTS = 1
JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP = 3
POST_REGEN_JUDGE_RESCORE_SOFT_ONLY = "soft_failed_only"
POST_REGEN_JUDGE_RESCORE_FULL_PANEL = "full_panel"
# Opt-in via APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1 after X2 pass (bounded, same-authority).
RELEASE_JUDGE_REGENERATION_ENABLED = True


def _truthy_env(raw: str) -> bool:
    return str(raw or "").strip().lower() in ("1", "true", "yes", "on")


def judge_regen_max_attempts() -> int:
    """Bounded judge-regen cycles per run (one Qwen rewrite + re-judge soft fails each)."""
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS",
        str(JUDGE_REGEN_MAX_ATTEMPTS),
    ).strip()
    try:
        n = int(raw)
    except ValueError:
        n = JUDGE_REGEN_MAX_ATTEMPTS
    return max(1, min(n, JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP))


def post_regen_judge_rescore_mode() -> str:
    """After judge-regen Qwen rewrite: rescore only soft fails (cheap) vs full panel (expensive)."""
    raw = str(os.environ.get("APPS_RG_EXEC_SUMMARY_POST_REGEN_JUDGE_MODE", "") or "").strip().lower()
    if raw in ("full_panel", "full", "all", "refresh_all"):
        return POST_REGEN_JUDGE_RESCORE_FULL_PANEL
    return POST_REGEN_JUDGE_RESCORE_SOFT_ONLY


def judge_regeneration_enabled() -> bool:
    if not RELEASE_JUDGE_REGENERATION_ENABLED:
        return False
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    if raw in ("1", "true", "yes", "on"):
        return True
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if product_fail_closed_runtime():
        return True
    return _truthy_env(raw)


def judge_safe_prefilter_enabled() -> bool:
    """Deterministic prose tighten before LLM judge regen (SRFS only)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_SAFE_PREFILTER", "0").strip().lower()
    return RELEASE_SRFS_JUDGE_SAFE_REPAIR_ENABLED and raw in ("1", "true", "yes", "on")


# Re-run X1D after full X2 with authoritative gate snapshot (default on; no gate weakening).
RELEASE_POST_X2_JUDGE_REFRESH_ENABLED = True


def post_x2_judge_refresh_enabled() -> bool:
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_X1D_POST_X2_REFRESH", "1").strip().lower()
    return RELEASE_POST_X2_JUDGE_REFRESH_ENABLED and raw not in ("0", "false", "no", "off")


__all__ = [
    "JUDGE_REGEN_MAX_ATTEMPTS",
    "JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP",
    "POST_REGEN_JUDGE_RESCORE_FULL_PANEL",
    "POST_REGEN_JUDGE_RESCORE_SOFT_ONLY",
    "RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED",
    "RELEASE_JUDGE_REGENERATION_ENABLED",
    "RELEASE_POST_X2_JUDGE_REFRESH_ENABLED",
    "RELEASE_SRFS_DENSITY_MICRO_EXPANSION_ENABLED",
    "RELEASE_SRFS_EMERGENCY_FINALIZER_ENABLED",
    "RELEASE_SRFS_JUDGE_SAFE_REPAIR_ENABLED",
    "RELEASE_SRFS_LLM_REPAIR_ENABLED",
    "RELEASE_SYNTHESIS_REGENERATION_ENABLED",
    "SYNTHESIS_REGEN_MAX_ATTEMPTS",
    "SYNTHESIS_REGEN_MAX_ATTEMPTS_HARD_CAP",
    "judge_regen_max_attempts",
    "judge_regeneration_enabled",
    "judge_safe_prefilter_enabled",
    "post_regen_judge_rescore_mode",
    "post_x2_judge_refresh_enabled",
    "synthesis_regen_max_attempts",
    "synthesis_regeneration_enabled",
]
