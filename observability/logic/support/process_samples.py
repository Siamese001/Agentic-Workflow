"""
sampling_processor.py - Sampling Module

Domain: support
Generated: 2025-12-07T12:07:59.852534
"""

import logging
import random
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SamplingDecision:
    """Sampling decision."""

    def __init__(self, sampled: bool, reason: str):
        """  Init   implementation."""
        self.sampled = sampled
        self.reason = reason

class SamplingProcessor:
    """Sampler for support domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        """  Init   implementation."""
        self.config = config or {}
        self.rate = self.config.get("rate", 1.0)
        self.always_sample = self.config.get("always_sample", [])
        logger.info(f"Initialized {self.__class__.__name__} with rate={self.rate}")

    def should_sample(self, context: Optional[Dict] = None) -> SamplingDecision:
        """Determine if should sample."""
        ctx = context or {}

        # Check always sample conditions
        for condition in self.always_sample:
            if self._matches_condition(ctx, condition):
                return SamplingDecision(True, "always_sample_match")

        # Rate-based sampling
        if random.random() < self.rate:
            return SamplingDecision(True, "rate_sampled")

        return SamplingDecision(False, "rate_rejected")

    def _matches_condition(self, context: Dict[str, object], condition: Dict[str, object]) -> bool:
        """Check if context matches condition."""
        for key, value in condition.items():
            if context.get(key) != value:
                return False
        return True

def should_sample(context: Optional[Dict] = None, config: Optional[Dict] = None) -> bool:
    """Check if should sample."""
    return SamplingProcessor(config).should_sample(context).sampled
