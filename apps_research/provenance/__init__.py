"""apps_research per-claim provenance ledger (W4 follow-up skeleton).

Public API:
    ClaimWithProvenance — a single research claim with source citations
    ConfidenceBand      — discrete bucketing (HIGH / MEDIUM / LOW / SPECULATIVE)
    ProvenanceLedger    — builder + validator
    ProvenanceMode      — NONE / SECTION / PER_CLAIM (declares the run's level)
    ProvenanceValidationResult — verdict + violations from validate()

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P3 NEXT_STEP)
"""
from __future__ import annotations

from apps_research.provenance.ledger import (
    ClaimWithProvenance,
    ConfidenceBand,
    ProvenanceLedger,
    ProvenanceMode,
    ProvenanceValidationResult,
    build_ledger_from_sections,
)

__all__ = [
    "ClaimWithProvenance",
    "ConfidenceBand",
    "ProvenanceLedger",
    "ProvenanceMode",
    "ProvenanceValidationResult",
    "build_ledger_from_sections",
]
