"""Compatibility exports for runtime ADG span contracts.

The canonical implementation lives in
``agentic_core.L6_system_learning.runtime_adg.span_contracts``.  Runtime-cert
tooling still imports this older top-level path, including two internal
contract-table symbols used for read-only normalization.
"""

from __future__ import annotations

__layer__ = "L6"

from agentic_core.L6_system_learning.runtime_adg.span_contracts import (  # noqa: F401
    APPS_RG_SPINE_SPAN_CHECKLIST,
    SIGNAL_THRESHOLD,
    AppsRgSpineSpanRow,
    CorpusTier1Report,
    CorpusTier2Report,
    Tier1Coverage,
    Tier2Coverage,
    _CategoryContract,
    _TIER1_CONTRACTS,
    apps_rg_spine_span_checklist_report,
    tier2_stage_count,
    tier2_stage_names,
    validate_apps_rg_spine_spans_against_snapshot,
    validate_tier1_corpus_coverage,
    validate_tier1_coverage,
    validate_tier2_corpus_coverage,
    validate_tier2_coverage,
)

__all__ = [
    "APPS_RG_SPINE_SPAN_CHECKLIST",
    "SIGNAL_THRESHOLD",
    "AppsRgSpineSpanRow",
    "CorpusTier1Report",
    "CorpusTier2Report",
    "Tier1Coverage",
    "Tier2Coverage",
    "_CategoryContract",
    "_TIER1_CONTRACTS",
    "apps_rg_spine_span_checklist_report",
    "tier2_stage_count",
    "tier2_stage_names",
    "validate_apps_rg_spine_spans_against_snapshot",
    "validate_tier1_corpus_coverage",
    "validate_tier1_coverage",
    "validate_tier2_corpus_coverage",
    "validate_tier2_coverage",
]
