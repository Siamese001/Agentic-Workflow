"""
LEGACY MIGRATION COMPLETE: Phase 2B
All models centralized in sovereign SSOT: agentic_core/schemas/models/core_contracts.py
"""
from agentic_core.schemas.models.core_contracts import (
    GoldenStateTestCase,
    JudgeVerdict,
    EvalResult,
    GoldenCase,
    GoldenOutput
)

__all__ = [
    "GoldenStateTestCase", "JudgeVerdict", "EvalResult",
    "GoldenCase", "GoldenOutput"
]
