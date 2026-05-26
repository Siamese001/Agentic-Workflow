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


# Post-X1D same-authority regen when X2 passed and any judge is below floor.
# Default 3 Qwen cycles (hard cap 3); post-regen rescores soft-failed judges only.
JUDGE_REGEN_MAX_ATTEMPTS = 3
JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP = 3
REGEN_MAX_DELTA_TOKENS_DEFAULT = 512
REGEN_MAX_DELTA_TOKENS_HARD_CAP = 768
POST_REGEN_JUDGE_RESCORE_SOFT_ONLY = "soft_failed_only"
POST_REGEN_JUDGE_RESCORE_FULL_PANEL = "full_panel"
# Opt-in via APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1 after X2 pass (bounded, same-authority).
RELEASE_JUDGE_REGENERATION_ENABLED = True


def _truthy_env(raw: str) -> bool:
    return str(raw or "").strip().lower() in ("1", "true", "yes", "on")


def judge_regen_max_delta_tokens() -> int:
    """Apps env for core ``IncrementalRepairContract.max_delta_tokens`` (W4.1)."""
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS",
        str(REGEN_MAX_DELTA_TOKENS_DEFAULT),
    ).strip()
    try:
        n = int(raw)
    except ValueError:
        n = REGEN_MAX_DELTA_TOKENS_DEFAULT
    return max(1, min(n, REGEN_MAX_DELTA_TOKENS_HARD_CAP))


def judge_pass_floor_0_to_5() -> float | None:
    """Operator override for holistic pass floor on 0..5 scale (``APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR``)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR", "").strip()
    if not raw:
        return None
    try:
        floor = float(raw)
    except ValueError:
        return None
    if floor < 0.0 or floor > 5.0:
        return None
    return floor


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


def judge_regen_prescriptive_delta_enabled() -> bool:
    """Surgical regen addendum: lock compiled prompt; anchor prior draft; delta-only judge lines."""
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_PRESCRIPTIVE_DELTA",
        "1",
    ).strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    return True


def judge_regen_core_runner_enabled() -> bool:
    """Delegate prescriptive regen to agentic_core SameAuthorityRegenRunner (ADR-085)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def judge_regen_legacy_remediation_block_enabled() -> bool:
    """Re-teach synthesis/composition/X2 guards in regen user turn (drift-prone; debug only)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_LEGACY_BLOCK", "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def exploratory_full_paragraph_regen_enabled() -> bool:
    """Opt-in full S2–S6 rewrite (default off — W4 GAP-3)."""
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_EXPLORATORY_FULL_PARAGRAPH_REGEN", "0").strip().lower()
    return _truthy_env(raw)


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
    "exploratory_full_paragraph_regen_enabled",
    "judge_regen_core_runner_enabled",
    "judge_pass_floor_0_to_5",
    "judge_regen_max_attempts",
    "judge_regen_max_delta_tokens",
    "REGEN_MAX_DELTA_TOKENS_DEFAULT",
    "REGEN_MAX_DELTA_TOKENS_HARD_CAP",
    "judge_regeneration_enabled",
    "judge_safe_prefilter_enabled",
    "post_regen_judge_rescore_mode",
    "post_x2_judge_refresh_enabled",
    "synthesis_regen_max_attempts",
    "synthesis_regeneration_enabled",
]
