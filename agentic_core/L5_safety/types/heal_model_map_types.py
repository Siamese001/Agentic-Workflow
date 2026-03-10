"""
Tier-to-model ID mapping for heal policy escalation.

Pure mapping function (stdlib-only, no environment access).
Phase 6 Wave 6.2.
"""

from __future__ import annotations

from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Model identifiers for LOW and HIGH reasoning tiers
LOW_MODEL_ID = "local_low"
HIGH_MODEL_ID = "local_high"


def map_tier_to_model_id(tier: ReasoningTier) -> str:
    """Map a reasoning tier to a model identifier.

    Args:
        tier: The reasoning tier (LOW or HIGH)

    Returns:
        Model identifier string ("local_low" or "local_high")
    """
    return LOW_MODEL_ID if tier == ReasoningTier.LOW else HIGH_MODEL_ID
