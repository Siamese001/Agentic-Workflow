from __future__ import annotations

"""Facade for the safety control-plane orchestration layer.

This package re-exports the existing infra.control_plane primitives so
callers can depend on a stable ``orchestration.control_plane``
namespace without changing the underlying implementation.
"""

from infra.control_plane.models import SafetyContext, PolicyRule, JudgeVerdict, PolicyDecision  # noqa: F401
from infra.control_plane.rules_engine import evaluate_rules, evaluate_tool_rules  # noqa: F401
from infra.control_plane.judge_engine import evaluate_with_guard_model  # noqa: F401
from infra.control_plane.decisions import choose_safety_decision  # noqa: F401
from infra.control_plane.control_plane import run_safety_pipeline  # noqa: F401

__all__ = [
    "SafetyContext",
    "PolicyRule",
    "JudgeVerdict",
    "PolicyDecision",
    "evaluate_rules",
    "evaluate_tool_rules",
    "evaluate_with_guard_model",
    "choose_safety_decision",
    "run_safety_pipeline",
]
