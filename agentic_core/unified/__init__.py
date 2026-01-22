from __future__ import annotations
"""
Public API for Unified Agents - Facade over L5_safety implementations.

This module provides clean import paths for unified agents, decoupling
consumers from the internal folder structure.

SSOT Consolidation (Jan 20, 2026):
Instead of:
    from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import UnifiedCodeValidatorAgent

Use:
    from agentic_core.unified import UnifiedCodeValidatorAgent
"""


from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import UnifiedCodeEnforcerAgent
from agentic_core.L5_safety.unified.UnifiedCodeHealerAgent import UnifiedCodeHealerAgent

# Re-export key agents from their deep locations
# Note: Using absolute imports to avoid circular dependency issues
from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
    RuleSet,
    UnifiedCodeValidatorAgent,
    ValidationReport,
    Violation,
    ViolationType,
)
from agentic_core.L5_safety.unified.UnifiedResourceManagerAgent import UnifiedResourceManagerAgent
from agentic_core.L5_safety.unified.UnifiedStructureEnforcerAgent import (
    UnifiedStructureEnforcerAgent,
)
from agentic_core.L5_safety.unified.UnifiedStructureHealerAgent import UnifiedStructureHealerAgent
from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
    StructureViolation,
    StructureViolationType,
    UnifiedStructureValidatorAgent,
)

__all__ = [
    # Code Validation
    "UnifiedCodeValidatorAgent",
    "RuleSet",
    "ValidationReport",
    "Violation",
    "ViolationType",
    # Structure Validation
    "UnifiedStructureValidatorAgent",
    "StructureViolation",
    "StructureViolationType",
    # Enforcers
    "UnifiedCodeEnforcerAgent",
    "UnifiedStructureEnforcerAgent",
    # Healers
    "UnifiedCodeHealerAgent",
    "UnifiedStructureHealerAgent",
    # Resource Management
    "UnifiedResourceManagerAgent",
]
