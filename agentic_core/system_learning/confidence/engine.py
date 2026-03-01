"""
agentic_core/system_learning/confidence/engine.py

Shim — canonical implementation lives in system_learning.engines.confidence.
"""

from system_learning.engines.confidence.engine import (  # noqa: F401
    HealingConfidenceScorer,
)

__all__ = ["HealingConfidenceScorer"]
