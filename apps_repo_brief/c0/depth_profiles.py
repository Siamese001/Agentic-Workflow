"""
P3.9 — C0 Depth Profile Thresholds (Python constants).

Mirrors apps_repo_brief/config/c0_depth_profiles.yaml as Python dicts
for use in RepoBriefC0Adapter.validate_fec() and board gate checks.

AG decision P3.1: Option A — Graduated thresholds.
Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.9
"""

from __future__ import annotations

from typing import Any

from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile

DEPTH_PROFILE_THRESHOLDS: dict[DepthProfile, dict[str, Any]] = {
    DepthProfile.REPO_BRIEF_LIGHT: {
        "min_sources": 5,
        "min_coverage_pct": 60.0,
        "min_citation_anchors": 3,
        "stale_source_policy": "caveat",
        "auth_governance_anchor_required": False,
        "board_gate_required": False,
        "semantic_cache_terminal_return": True,
    },
    DepthProfile.REPO_BRIEF_STANDARD: {
        "min_sources": 10,
        "min_coverage_pct": 75.0,
        "min_citation_anchors": 8,
        "stale_source_policy": "caveat",
        "auth_governance_anchor_required": False,
        "board_gate_required": False,
        "semantic_cache_terminal_return": True,
    },
    DepthProfile.REPO_BRIEF_DEEP: {
        "min_sources": 20,
        "min_coverage_pct": 85.0,
        "min_citation_anchors": 15,
        "stale_source_policy": "block",
        "auth_governance_anchor_required": False,
        "board_gate_required": False,
        "semantic_cache_terminal_return": True,
    },
    DepthProfile.REPO_BRIEF_BOARD_DOSSIER: {
        "min_sources": 30,
        "min_coverage_pct": 95.0,
        "min_citation_anchors": 25,
        "stale_source_policy": "block",
        "auth_governance_anchor_required": True,
        "board_gate_required": True,
        "semantic_cache_terminal_return": False,  # P3.13 strict compat — no terminal R1B for board
        "strict_compat_r1a": True,
        "critical_contradiction_policy": "escalate_hitl",
    },
}
