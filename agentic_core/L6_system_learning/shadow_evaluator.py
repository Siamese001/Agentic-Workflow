"""Compatibility shim for the legacy L6 shadow-evaluator namespace."""

from __future__ import annotations

from agentic_core.L6_system_learning.validators.shadow_evaluator import (
    ShadowMetrics,
    ShadowRegression,
    ShadowThresholds,
    evaluate_shadow,
)

__all__ = [
    "ShadowMetrics",
    "ShadowRegression",
    "ShadowThresholds",
    "evaluate_shadow",
]
