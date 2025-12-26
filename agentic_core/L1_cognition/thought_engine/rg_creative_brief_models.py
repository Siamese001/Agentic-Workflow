"""
DEPRECATED – Phase 5 Comprehensive Enforcement Sweep (Dec 26, 2025)
All models have been migrated to the Sovereign SSOT:
agentic_core/schemas/models/core_contracts.py

This file now serves as a backward-compatible import proxy.
New code MUST import directly from core_contracts.py

NOTE: ExecutiveSummaryBrief has external dependency on VoiceType enum - not migrated.
Requires enum migration first before full file migration.
"""
from agentic_core.schemas.models.core_contracts import (
    WordCountConstraint,
    CharCountConstraint,
    StructureConstraint,
    HeadlineBrief,
)

__all__ = [
    "WordCountConstraint",
    "CharCountConstraint",
    "StructureConstraint",
    "HeadlineBrief",
]
