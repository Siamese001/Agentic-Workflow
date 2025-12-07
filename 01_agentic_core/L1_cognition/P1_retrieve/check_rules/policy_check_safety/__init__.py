"""
01_agentic_core/L1_cognition/P1_retrieve/check_rules/policy_check_safety/__init__.py
Policy Check Safety - Safety-Specific Policy Enforcement.

This module contains safety policy checking implementations:
- check_registry_policy: Registry policy validation
- enforce_boundaries: Boundary enforcement
- enforce_core_boundaries: Core boundary enforcement
- validate_constraints: Constraint validation
- validate_core_constraints: Core constraint validation

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""

from __future__ import annotations

__version__ = "7.0.0"

# Re-export from submodules
from .check_registry_policy import (
    CheckScriptsPolicyPlanType,
    CheckScriptsPolicyPlanConstraints,
    CheckScriptsPolicyPlanResult,
    CheckScriptsPolicyPlanProcessor,
    CheckScriptsPolicyPlanImpl,
    CheckScriptsPolicyPlanInterface,
    CheckScriptsPolicyPlanFactory,
    SecurityError,
    check_scripts_policy,
)

__all__ = [
    "__version__",
    "CheckScriptsPolicyPlanType",
    "CheckScriptsPolicyPlanConstraints",
    "CheckScriptsPolicyPlanResult",
    "CheckScriptsPolicyPlanProcessor",
    "CheckScriptsPolicyPlanImpl",
    "CheckScriptsPolicyPlanInterface",
    "CheckScriptsPolicyPlanFactory",
    "SecurityError",
    "check_scripts_policy",
]
