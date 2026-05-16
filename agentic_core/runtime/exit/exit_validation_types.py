"""AG-5 Exit normalization validation types — generic core only."""

from __future__ import annotations

from enum import Enum
from typing import Final


class TerminalPathClass(str, Enum):
    """Routing posture for evidence/prompt requirements."""

    GROUNDED = "grounded"
    MODEL = "model"
    NEUTRAL = "neutral"


class AG5NormalizationError(ValueError):
    """Raised when terminal input cannot be normalized into ExitReviewPacket."""


# Canonical AG-5 terminal source strings → mapped to v6 SourceType in normalizer.
AG5_SOURCE_STRINGS: Final[frozenset[str]] = frozenset({
    "RET_EXACT_CACHE",
    "RET_SEMANTIC_CACHE",
    "RET_FALLBACK",
    "SEALED_L2_ARTIFACT",
    "SEALED_WORKFLOW_PACKAGE",
    "RECLEARED_HITL_PACKET",
    "APP_BINDING_COMPATIBILITY_PACKAGE",
})


__all__ = [
    "AG5NormalizationError",
    "AG5_SOURCE_STRINGS",
    "TerminalPathClass",
]
