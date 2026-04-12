"""C7 G1: WHAT KIND OF POWER? - Classify access type.

10C-REQ-155: Classify access type read tool model network memory write
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class AccessType(Enum):
    """Types of access requests."""

    READ = auto()  # Read operations
    TOOL = auto()  # Tool invocation
    MODEL = auto()  # Model/LLM access
    NETWORK = auto()  # Network/external API
    MEMORY = auto()  # Memory/storage access
    WRITE = auto()  # Write operations (UWG path)


@dataclass
class ClassificationResult:
    """Result of access classification."""

    access_type: AccessType
    confidence: float
    reason: str
    requires_ticket: bool


class AccessClassifier:
    """C7 G1: Access classifier.

    10C-REQ-155: Classify access type read tool model network memory write.
    """

    def __init__(self) -> None:
        self._type_keywords: dict[AccessType, list[str]] = {
            AccessType.READ: ["read", "get", "fetch", "load", "retrieve"],
            AccessType.TOOL: ["tool", "execute", "run", "invoke", "call"],
            AccessType.MODEL: ["model", "llm", "completion", "generate", "chat"],
            AccessType.NETWORK: ["http", "api", "url", "fetch", "request", "external"],
            AccessType.MEMORY: ["memory", "store", "cache", "vector", "index"],
            AccessType.WRITE: ["write", "commit", "save", "persist", "mutate"],
        }

    def classify(self, request: dict[str, Any]) -> ClassificationResult:
        """Classify request to access type."""
        operation = request.get("operation", "").lower()
        intent = request.get("intent", "").lower()
        target = request.get("target", "").lower()

        # Score each access type
        scores: dict[AccessType, int] = {t: 0 for t in AccessType}

        for access_type, keywords in self._type_keywords.items():
            for keyword in keywords:
                if keyword in operation:
                    scores[access_type] += 2
                if keyword in intent:
                    scores[access_type] += 2
                if keyword in target:
                    scores[access_type] += 1

        # Select highest scoring type
        if not scores or max(scores.values()) == 0:
            # Default based on target hints
            if "llm" in target or "model" in target:
                return ClassificationResult(
                    access_type=AccessType.MODEL,
                    confidence=0.6,
                    reason="target_hint_model",
                    requires_ticket=True,
                )
            return ClassificationResult(
                access_type=AccessType.READ,
                confidence=0.5,
                reason="default_low_confidence",
                requires_ticket=False,
            )

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Calculate confidence
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.5

        # Determine if ticket required
        requires_ticket = best_type in (
            AccessType.TOOL,
            AccessType.MODEL,
            AccessType.NETWORK,
            AccessType.WRITE,
        )

        return ClassificationResult(
            access_type=best_type,
            confidence=confidence,
            reason=f"keyword_match:{best_score}",
            requires_ticket=requires_ticket,
        )

    def add_keywords(self, access_type: AccessType, keywords: list[str]) -> None:
        """Add classification keywords for an access type."""
        self._type_keywords[access_type].extend(keywords)
