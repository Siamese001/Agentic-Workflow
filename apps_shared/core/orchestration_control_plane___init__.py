from __future__ import annotations

"""Facade for the safety control-plane orchestration layer.

This package re-exports the existing infra.control_plane primitives so
callers can depend on a stable ``orchestration.control_plane``
namespace without changing the underlying implementation.
"""

from archives.legacy_root_folders.infra.control_plane.models import SafetyContext, PolicyRule, PolicyDecision
from archives.legacy_root_folders.infra.control_plane.decisions import RulesEngineResult, RuleMatch
from archives.legacy_root_folders.infra.control_plane.rules_engine import evaluate_rules
from archives.legacy_root_folders.infra.control_plane.judge_engine import evaluate_with_guard_model
from archives.legacy_root_folders.infra.control_plane.control_plane import run_safety_pipeline

__all__ = [
    "SafetyContext",
    "PolicyRule",
    "PolicyDecision",
    "RulesEngineResult",
    "RuleMatch",
    "evaluate_rules",
    "evaluate_with_guard_model",
    "run_safety_pipeline",
]



