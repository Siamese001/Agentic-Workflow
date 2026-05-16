"""Provider exhaustion error + hardened router scaffolding for RG types."""

from __future__ import annotations

from typing import Any


class AllProvidersDownError(Exception):
    """Raised when every upstream model lane rejects or is unavailable."""

    def __init__(self, message: str = "all providers exhausted", **_: Any) -> None:
        super().__init__(message)


class HardenedRouter:
    """Lightweight façade matching historical RG circuit-reset contracts."""

    def reset_all_circuit_breakers(self) -> None:
        """Reset pooled provider breakers."""

    def get_provider_health(self) -> dict[str, Any]:
        return {}


__all__ = ["AllProvidersDownError", "HardenedRouter"]
