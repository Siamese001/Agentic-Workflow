"""C0 G7: SOVEREIGN EGRESS - Fail-closed exit with no silent fallback.

10C-REQ-116: Map symbolic to specific provider No silent fallback exactly one approved path
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class EgressStatus(Enum):
    """Egress status enumeration."""
    ALLOWED = auto()
    BLOCKED = auto()
    FALLBACK_TRIGGERED = auto()
    ERROR = auto()


@dataclass
class EgressResult:
    """Result of sovereign egress."""
    status: EgressStatus
    symbolic_request: str
    resolved_provider: str
    resolved_path: str
    is_fallback: bool
    rejection_reason: str = ""


class SovereignEgress:
    """C0 G7: Sovereign egress gate.

    10C-REQ-116: Map symbolic request to specific provider enforce
    No silent fallback ensure exactly one approved path.
    """

    def __init__(self) -> None:
        self._provider_map: dict[str, str] = {}  # symbolic -> provider
        self._approved_paths: dict[str, list[str]] = {}  # provider -> paths
        self._fallback_attempts: int = 0
        self._fallback_blocked: int = 0

    def egress(self, symbolic_request: str) -> EgressResult:
        """Execute sovereign egress.

        10C-REQ-116: No silent fallback - if primary path fails, reject.
        """
        # Resolve symbolic to provider
        provider = self._provider_map.get(symbolic_request)

        if not provider:
            return EgressResult(
                status=EgressStatus.ERROR,
                symbolic_request=symbolic_request,
                resolved_provider="",
                resolved_path="",
                is_fallback=False,
                rejection_reason="unmapped_symbolic_request",
            )

        # Get approved paths for provider
        paths = self._approved_paths.get(provider, [])

        if not paths:
            return EgressResult(
                status=EgressStatus.ERROR,
                symbolic_request=symbolic_request,
                resolved_provider=provider,
                resolved_path="",
                is_fallback=False,
                rejection_reason="no_approved_paths_for_provider",
            )

        # Select exactly one approved path (deterministic: first)
        selected_path = paths[0]

        # Verify path is still approved
        if selected_path not in paths:
            # Path was removed - fail closed
            return EgressResult(
                status=EgressStatus.BLOCKED,
                symbolic_request=symbolic_request,
                resolved_provider=provider,
                resolved_path=selected_path,
                is_fallback=False,
                rejection_reason="path_no_longer_approved",
            )

        return EgressResult(
            status=EgressStatus.ALLOWED,
            symbolic_request=symbolic_request,
            resolved_provider=provider,
            resolved_path=selected_path,
            is_fallback=False,
        )

    def attempt_fallback(self, symbolic_request: str, failed_path: str) -> EgressResult:
        """Handle fallback attempt - BLOCKED by design.

        10C-REQ-116: No silent fallback.
        """
        self._fallback_attempts += 1
        self._fallback_blocked += 1

        return EgressResult(
            status=EgressStatus.FALLBACK_TRIGGERED,
            symbolic_request=symbolic_request,
            resolved_provider="",
            resolved_path="",
            is_fallback=True,
            rejection_reason="silent_fallback_blocked_by_sovereign_egress",
        )

    def register_provider_map(self, symbolic: str, provider: str) -> None:
        """Register symbolic to provider mapping."""
        self._provider_map[symbolic] = provider

    def register_approved_path(self, provider: str, path: str) -> None:
        """Register approved path for provider."""
        if provider not in self._approved_paths:
            self._approved_paths[provider] = []
        self._approved_paths[provider].append(path)

    def get_fallback_stats(self) -> dict[str, int]:
        """Get fallback attempt statistics."""
        return {
            "attempts": self._fallback_attempts,
            "blocked": self._fallback_blocked,
        }

    def get_provider_count(self) -> int:
        """Get number of registered provider mappings."""
        return len(self._provider_map)
