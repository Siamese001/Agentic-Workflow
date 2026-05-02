"""apps_underwriting_ai — AI Underwriting Decision Pipeline.

5-stage HOP pipeline: initialize_evidence → reconcile_documents →
derive_features → collect_evidence → assemble_decision.

Public surface:
    - UnderwritingRequest, UnderwritingResult, DecisionPacket (types)
    - UnderwritingEngine (imperative entrypoint)
    - UnderwritingHopOrchestrator (shared-substrate entrypoint)

See README.md for usage and SLO.md / RUNBOOK.md for operational discipline.
"""

from __future__ import annotations

from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    EvidenceRegister,
    RiskFeatures,
    UnderwritingRequest,
    UnderwritingResult,
)

__all__ = [
    "DecisionPacket",
    "EvidenceRegister",
    "RiskFeatures",
    "UnderwritingRequest",
    "UnderwritingResult",
]

__version__ = "0.1.0"
