"""
Unified L5 Safety/Validation Agents

Phase 2 Consolidation: 18 validators → 3 unified agents

This module provides consolidated validation agents that merge functionality
from multiple legacy validators while maintaining backward compatibility.

Unified Agents:
- UnifiedCodeValidatorAgent: Single-pass AST validation (syntax, canon, async, print)
- UnifiedStructureValidatorAgent: Gravity, hygiene, registry, contract validation
"""
from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
    UnifiedCodeValidatorAgent,
    RuleSet,
    ValidationReport,
    Violation,
    ViolationType,
    create_legacy_syntax_validator,
    create_legacy_canon_validator,
    create_legacy_async_validator,
    create_legacy_print_validator,
)
from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
    UnifiedStructureValidatorAgent,
    StructureViolation,
    StructureViolationType,
    create_legacy_gravity_validator,
    create_legacy_hygiene_validator,
    create_legacy_registry_validator,
)

__all__ = [
    "UnifiedCodeValidatorAgent",
    "UnifiedStructureValidatorAgent",
    "RuleSet",
    "ValidationReport",
    "Violation",
    "ViolationType",
    "StructureViolation",
    "StructureViolationType",
    "create_legacy_syntax_validator",
    "create_legacy_canon_validator",
    "create_legacy_async_validator",
    "create_legacy_print_validator",
    "create_legacy_gravity_validator",
    "create_legacy_hygiene_validator",
    "create_legacy_registry_validator",
]
