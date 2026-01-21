from __future__ import annotations
"""Backoff strategies for retry logic.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class BackoffStrategy(ABC):
    """Abstract base for backoff strategies."""

    @abstractmethod
    def calculate(self, attempt: int) -> int:
        """Calculate backoff delay in milliseconds.

        Args:
            attempt: Current attempt number (1-indexed)

        Returns:
            Backoff delay in milliseconds
        """
        pass


@dataclass
class ExponentialBackoff(BackoffStrategy):
    """Exponential backoff with optional jitter.

    Attributes:
        base_ms: Base delay in milliseconds
        max_ms: Maximum delay cap
        jitter_ms: Random jitter range
        multiplier: Exponential multiplier (default 2)
    """

    base_ms: int = 200
    max_ms: int = 30000
    jitter_ms: int = 100
    multiplier: float = 2.0

    def calculate(self, attempt: int) -> int:
        """Calculate exponential backoff with jitter."""
        base = min(
            self.base_ms * (self.multiplier ** (attempt - 1)),
            self.max_ms,
        )

        if self.jitter_ms <= 0:
            return int(base)

        jitter = random.randint(-self.jitter_ms, self.jitter_ms)
        return max(0, int(base + jitter))


@dataclass
class LinearBackoff(BackoffStrategy):
    """Linear backoff with optional jitter.

    Attributes:
        base_ms: Base delay in milliseconds
        increment_ms: Delay increment per attempt
        max_ms: Maximum delay cap
        jitter_ms: Random jitter range
    """

    base_ms: int = 200
    increment_ms: int = 200
    max_ms: int = 10000
    jitter_ms: int = 100

    def calculate(self, attempt: int) -> int:
        """Calculate linear backoff with jitter."""
        base = min(
            self.base_ms + (self.increment_ms * (attempt - 1)),
            self.max_ms,
        )

        if self.jitter_ms <= 0:
            return int(base)

        jitter = random.randint(-self.jitter_ms, self.jitter_ms)
        return max(0, int(base + jitter))


def calculate_backoff_ms(
    base_backoff_ms: int,
    attempt: int,
    jitter_ms: int = 100,
    strategy: str = "exponential",
) -> int:
    """Convenience function for calculating backoff.

    Args:
        base_backoff_ms: Base delay in milliseconds
        attempt: Current attempt number (1-indexed)
        jitter_ms: Random jitter range
        strategy: "exponential" or "linear"

    Returns:
        Backoff delay in milliseconds
    """
    if strategy == "exponential":
        backoff = ExponentialBackoff(
            base_ms=base_backoff_ms,
            jitter_ms=jitter_ms,
        )
    elif strategy == "linear":
        backoff = LinearBackoff(
            base_ms=base_backoff_ms,
            jitter_ms=jitter_ms,
        )
    else:
        raise ValueError(f"Unknown backoff strategy: {strategy}")

    return backoff.calculate(attempt)
