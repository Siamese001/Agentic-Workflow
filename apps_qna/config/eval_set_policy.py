"""Holdout vs dev eval-set separation policy — D3.2.

Provides deterministic, hash-based assignment of interview slugs to one of
three eval partitions:

    dev      — used during active development and continuous evaluation
    holdout  — reserved; must NOT be used for rubric tuning or judge
               calibration (prevents data leakage)
    test     — final acceptance gate (run-once at release)

The assignment is a pure function of the slug string. No randomness,
no external state. The same slug always maps to the same partition.

Default split ratios:
    dev      — 70 %
    holdout  — 20 %
    test     — 10 %

Ratios are configurable via EvalSetPolicy. The policy must sum to 1.0
(checked at construction).

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D3.2
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class EvalPartition(str, Enum):
    """Eval partition a slug belongs to."""

    DEV = "dev"
    HOLDOUT = "holdout"
    TEST = "test"


@dataclass(frozen=True)
class EvalSetPolicy:
    """Deterministic slug → partition assignment policy.

    Attributes:
        dev_ratio: Fraction assigned to dev partition.
        holdout_ratio: Fraction assigned to holdout partition.
        test_ratio: Fraction assigned to test partition.
        salt: Optional salt mixed into the hash to allow policy versioning
              without changing slug assignments globally.

    Ratios must sum to 1.0 (within float tolerance 1e-6).
    """

    dev_ratio: float = 0.70
    holdout_ratio: float = 0.20
    test_ratio: float = 0.10
    salt: str = "apps_qna::eval_set::v1"

    def __post_init__(self) -> None:
        total = self.dev_ratio + self.holdout_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"EvalSetPolicy ratios must sum to 1.0, got {total:.6f}"
            )
        if any(r < 0 for r in (self.dev_ratio, self.holdout_ratio, self.test_ratio)):
            raise ValueError("EvalSetPolicy ratios must be non-negative")

    def assign(self, slug: str) -> EvalPartition:
        """Assign a slug to a partition deterministically.

        The assignment is a pure function of (salt + slug). Changing the
        salt produces a new independent assignment without altering the
        slug input.

        Args:
            slug: Interview slug or any identifier string.

        Returns:
            EvalPartition for this slug.
        """
        key = f"{self.salt}::{slug}"
        digest = hashlib.sha256(key.encode()).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        if bucket < self.dev_ratio:
            return EvalPartition.DEV
        if bucket < self.dev_ratio + self.holdout_ratio:
            return EvalPartition.HOLDOUT
        return EvalPartition.TEST

    def filter_partition(
        self,
        slugs: Sequence[str],
        partition: EvalPartition,
    ) -> list[str]:
        """Return only slugs assigned to the given partition.

        Args:
            slugs: Collection of slug strings to filter.
            partition: Target partition.

        Returns:
            Sorted list of slugs in the target partition.
        """
        return sorted(s for s in slugs if self.assign(s) is partition)

    def partition_counts(self, slugs: Sequence[str]) -> dict[str, int]:
        """Count slugs per partition.

        Args:
            slugs: Collection of slug strings.

        Returns:
            Dict mapping partition name → count.
        """
        counts: dict[str, int] = {p.value: 0 for p in EvalPartition}
        for slug in slugs:
            counts[self.assign(slug).value] += 1
        return counts


# Default singleton policy — callers may override via EvalSetPolicy(...)
DEFAULT_EVAL_SET_POLICY: EvalSetPolicy = EvalSetPolicy()


def assign_partition(slug: str, *, policy: EvalSetPolicy | None = None) -> EvalPartition:
    """Convenience function — assign slug using the default or provided policy.

    Args:
        slug: Interview slug.
        policy: Optional custom policy; uses DEFAULT_EVAL_SET_POLICY if None.

    Returns:
        EvalPartition for this slug.
    """
    return (policy or DEFAULT_EVAL_SET_POLICY).assign(slug)


def is_holdout(slug: str, *, policy: EvalSetPolicy | None = None) -> bool:
    """Return True if the slug is in the holdout partition.

    Guard: callers should call this before using a slug in rubric tuning
    or judge calibration to prevent data leakage.

    Args:
        slug: Interview slug.
        policy: Optional custom policy.

    Returns:
        True when slug belongs to the holdout partition.
    """
    return assign_partition(slug, policy=policy) is EvalPartition.HOLDOUT


__all__ = [
    "DEFAULT_EVAL_SET_POLICY",
    "EvalPartition",
    "EvalSetPolicy",
    "assign_partition",
    "is_holdout",
]
