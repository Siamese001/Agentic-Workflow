"""Exceptions for same-authority regen prefix and bundle guards."""

from __future__ import annotations


class SameAuthorityRegenError(Exception):
    """Base for same-authority regen guard failures."""


class FrozenPrefixMutationError(SameAuthorityRegenError):
    """Raised when system/developer/slot prefix would change after freeze."""


class SameAuthorityBundleDriftError(SameAuthorityRegenError):
    """Raised when authority hashes or lanes drift across regen."""


class EmptyDeltaTurnError(SameAuthorityRegenError):
    """Raised when REGEN_DELTA user content is empty."""
