"""ADG Identity Normalizer - Normalizes ADG node identities."""
from __future__ import annotations

from typing import Any


class IdentityNormalizer:
    """Normalizes identities for ADG nodes."""

    def __init__(self) -> None:
        """Initialize the identity normalizer."""
        self.cache: dict[str, str] = {}

    def normalize(self, identity: str) -> str:
        """Normalize an identity string.

        Args:
            identity: Raw identity string

        Returns:
            Normalized identity
        """
        return identity.strip().lower()


def normalize_identity(identity: str) -> str:
    """Normalize an identity.

    Args:
        identity: Identity to normalize

    Returns:
        Normalized identity string
    """
    normalizer = IdentityNormalizer()
    return normalizer.normalize(identity)


__all__ = [
    "IdentityNormalizer",
    "normalize_identity",
]
