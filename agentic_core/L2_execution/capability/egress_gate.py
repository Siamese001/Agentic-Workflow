"""C7 G6: SOVEREIGN EGRESS GATE - No silent fallback.

10C-REQ-160: Map symbolic to specific provider No silent fallback exactly one approved path
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class EgressStatus(Enum):
    """Egress gate status."""
    ALLOWED = auto()
    BLOCKED = auto()
    FALLBACK_BLOCKED = auto()
    NO_PATH = auto()


@dataclass
class EgressResult:
    """Result of egress gate."""
    status: EgressStatus
    symbolic: str
    provider: str
    path: str
    is_fallback: bool
    rejection_reason: str = ""


class EgressGate:
    """C7 G6: Sovereign egress gate.

    10C-REQ-160: Map symbolic request to specific provider enforce
    No silent fallback ensure exactly one approved path.
    """

    def __init__(self) -> None:
        self._mappings: dict[str, str] = {}  # symbolic -> provider
        self._approved_paths: dict[str, list[str]] = {}  # provider -> [paths]
        self._fallback_blocked_count: int = 0

    def egress(self, symbolic: str) -> EgressResult:
        """Process egress request.

        10C-REQ-160: No silent fallback - if primary path unavailable, BLOCK.
        """
        provider = self._mappings.get(symbolic)

        if not provider:
            return EgressResult(
                status=EgressStatus.NO_PATH,
                symbolic=symbolic,
                provider="",
                path="",
                is_fallback=False,
                rejection_reason="no_provider_mapping",
            )

        paths = self._approved_paths.get(provider, [])

        if not paths:
            return EgressResult(
                status=EgressStatus.NO_PATH,
                symbolic=symbolic,
                provider=provider,
                path="",
                is_fallback=False,
                rejection_reason="no_approved_paths",
            )

        # Exactly one approved path - deterministic selection
        selected_path = paths[0]

        return EgressResult(
            status=EgressStatus.ALLOWED,
            symbolic=symbolic,
            provider=provider,
            path=selected_path,
            is_fallback=False,
        )

    def attempt_fallback(self, symbolic: str, failed_path: str) -> EgressResult:
        """Block fallback attempt.

        10C-REQ-160: No silent fallback - always block.
        """
        self._fallback_blocked_count += 1

        return EgressResult(
            status=EgressStatus.FALLBACK_BLOCKED,
            symbolic=symbolic,
            provider="",
            path="",
            is_fallback=True,
            rejection_reason="silent_fallback_blocked_by_policy",
        )

    def register_mapping(self, symbolic: str, provider: str) -> None:
        """Register symbolic to provider mapping."""
        self._mappings[symbolic] = provider

    def register_approved_path(self, provider: str, path: str) -> None:
        """Register approved path for provider."""
        if provider not in self._approved_paths:
            self._approved_paths[provider] = []
        if path not in self._approved_paths[provider]:
            self._approved_paths[provider].append(path)

    def get_fallback_stats(self) -> dict[str, int]:
        """Get fallback blocking statistics."""
        return {
            "fallback_blocked": self._fallback_blocked_count,
        }
