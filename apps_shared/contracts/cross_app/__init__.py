"""Cross-app producer -> consumer envelopes.

Plan: apps-cross-app-precursors-c94c71 (Wave 2).

The 4 envelopes model the real cross-app HOP precursors identified in the
2026-05-01 orchestration inventory:

    ExperienceLibraryEnvelope  apps_shared  -> apps_qna
    ResearchBriefEnvelope      apps_research -> apps_qna
    ExecutiveBriefEnvelope     apps_exec    -> apps_qna
    ResumeBankEnvelope         apps_rg      -> apps_qna

Each envelope is a frozen pydantic model with producer/consumer helpers and a
seal/hash/freshness invariant enforced at load time.
"""

from __future__ import annotations

from apps_shared.contracts.cross_app.base import (
    CrossAppEnvelope,
    EnvelopeExpiredError,
    EnvelopeHashMismatchError,
    EnvelopeLoadError,
    EnvelopeSchemaError,
    compute_sha256,
)
from apps_shared.contracts.cross_app.executive_brief import ExecutiveBriefEnvelope
from apps_shared.contracts.cross_app.experience_library import (
    ExperienceLibraryEnvelope,
)
from apps_shared.contracts.cross_app.research_brief import ResearchBriefEnvelope
from apps_shared.contracts.cross_app.resume_bank import ResumeBankEnvelope

__all__ = [
    "CrossAppEnvelope",
    "EnvelopeExpiredError",
    "EnvelopeHashMismatchError",
    "EnvelopeLoadError",
    "EnvelopeSchemaError",
    "ExecutiveBriefEnvelope",
    "ExperienceLibraryEnvelope",
    "ResearchBriefEnvelope",
    "ResumeBankEnvelope",
    "compute_sha256",
]
