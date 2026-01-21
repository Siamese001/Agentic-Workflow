"""
Unified L5 Safety/Validation Agents

[SOVEREIGN UPGRADE 2026-01-21]: Semantic Realignment in progress.
Phase 2 Consolidation: 18 validators → 3 unified agents

This module provides consolidated validation agents that merge functionality
from multiple legacy validators while maintaining backward compatibility.

Agents:
- UnifiedCodeValidatorAgent: Single-pass AST validation (syntax, canon, async, print)
- StructuralValidatorAgent: Gravity, hygiene, registry, contract validation
  (Renamed from UnifiedStructureValidatorAgent - alias maintained for backward compat)
"""

from agentic_core.L5_safety.unified.StructuralValidatorAgent import (
    StructuralValidatorAgent,
    StructureConfig,
    StructureReport,
    StructureViolation,
    StructureViolationType,
    UnifiedStructureValidatorAgent,  # Backward compat alias
    create_legacy_gravity_validator,
    create_legacy_hygiene_validator,
    create_legacy_registry_validator,
)
from agentic_core.L5_safety.unified.UnifiedCodeDetectorAgent import UnifiedCodeDetectorAgent
from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import UnifiedCodeEnforcerAgent
from agentic_core.L5_safety.unified.UnifiedCodeHealerAgent import UnifiedCodeHealerAgent
from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
    RuleSet,
    UnifiedCodeValidatorAgent,
    ValidationReport,
    Violation,
    ViolationType,
    create_legacy_async_validator,
    create_legacy_canon_validator,
    create_legacy_print_validator,
    create_legacy_syntax_validator,
)
from agentic_core.L5_safety.unified.UnifiedResourceManagerAgent import UnifiedResourceManagerAgent
from agentic_core.L5_safety.unified.UnifiedSafetyDetectorAgent import UnifiedSafetyDetectorAgent
from agentic_core.L5_safety.unified.UnifiedSafetyExecutorAgent import UnifiedSafetyExecutorAgent
from agentic_core.L5_safety.unified.UnifiedSecurityManagerAgent import UnifiedSecurityManagerAgent
from agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent import (
    UnifiedStructureEnforcerAgent,
)
from agentic_core.L5_safety.unified.UnifiedStructureHealerAgent import UnifiedStructureHealerAgent

__all__ = [
    # New canonical names
    "StructuralValidatorAgent",
    # Legacy aliases (backward compat)
    "UnifiedCodeValidatorAgent",
    "UnifiedStructureValidatorAgent",
    "UnifiedCodeDetectorAgent",
    "UnifiedCodeEnforcerAgent",
    "UnifiedCodeHealerAgent",
    "UnifiedResourceManagerAgent",
    "UnifiedSafetyDetectorAgent",
    "UnifiedSafetyExecutorAgent",
    "UnifiedSecurityManagerAgent",
    "UnifiedStructureEnforcerAgent",
    "UnifiedStructureHealerAgent",
    # Data classes
    "RuleSet",
    "ValidationReport",
    "Violation",
    "ViolationType",
    "StructureConfig",
    "StructureReport",
    "StructureViolation",
    "StructureViolationType",
    # Factory methods
    "create_legacy_syntax_validator",
    "create_legacy_canon_validator",
    "create_legacy_async_validator",
    "create_legacy_print_validator",
    "create_legacy_gravity_validator",
    "create_legacy_hygiene_validator",
    "create_legacy_registry_validator",
]
