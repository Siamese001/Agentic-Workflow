"""
Guardrails module - Re-exports from GuardrailsStrategy.py for backward compatibility.

This module provides the expected import path for MetaLearningGuardrails.
"""

from agentic_core.L1_cognition.meta_learning.GuardrailsStrategy import (
    CacheGuardrails,
    MetaLearningGuardrails,
    get_guardrails,
    reset_guardrails,
)

__all__ = [
    "CacheGuardrails",
    "MetaLearningGuardrails",
    "get_guardrails",
    "reset_guardrails",
]
