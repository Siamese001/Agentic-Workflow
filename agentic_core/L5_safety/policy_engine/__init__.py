"""
Sovereign L5 Safety/Validation Agents - Policy Engine

[PHASE 6 SOVEREIGN NAMESPACE MIGRATION]: Reclaimed canonical namespace.
Former "Unified" agents now occupy sovereign positions.

This module provides consolidated validation agents that merge functionality
from multiple legacy validators while maintaining backward compatibility.

Agents:
- CodeValidatorAgent: Single-pass AST validation (syntax, canon, async, print)
- CodeDetectorAgent: Dead code, deadlock, memory leak detection
- CodeEnforcerAgent: Standards, patterns, type hints enforcement
- CodeHealerAgent: Import healing, canon compliance, structural fixes
- ResourceManagerAgent: Budget management, allocation strategies
- SafetyDetectorAgent: Bias, hallucination, prompt injection detection
- SafetyExecutorAgent: Pre-execution safety checks
- SecurityManagerAgent: Permissions, vault, checkpoints
- StructureEnforcerAgent: Gravity, naming, documentation enforcement
- StructureHealerAgent: Gravity healing, naming fixes, territory healing
"""

from agentic_core.L5_safety.policy_engine.CodeDetectorAgent import CodeDetectorAgent
from agentic_core.L5_safety.policy_engine.CodeEnforcerAgent import CodeEnforcerAgent
from agentic_core.L5_safety.policy_engine.CodeHealerAgent import CodeHealerAgent
from agentic_core.L5_safety.policy_engine.CodeValidatorAgent import (
    RuleSet,
    CodeValidatorAgent,
    ValidationReport,
    Violation,
    ViolationType,
    create_legacy_async_validator,
    create_legacy_canon_validator,
    create_legacy_print_validator,
    create_legacy_syntax_validator,
)
from agentic_core.L5_safety.policy_engine.ResourceManagerAgent import ResourceManagerAgent
from agentic_core.L5_safety.policy_engine.SafetyDetectorAgent import SafetyDetectorAgent
from agentic_core.L5_safety.policy_engine.SafetyExecutorAgent import SafetyExecutorAgent
from agentic_core.L5_safety.policy_engine.SecurityManagerAgent import SecurityManagerAgent
from agentic_core.L5_safety.policy_engine.StructureEnforcerAgent import (
    StructureEnforcerAgent,
)
from agentic_core.L5_safety.policy_engine.StructureHealerAgent import StructureHealerAgent

__all__ = [
    # Sovereign agents (canonical namespace)
    "CodeValidatorAgent",
    "CodeDetectorAgent",
    "CodeEnforcerAgent",
    "CodeHealerAgent",
    "ResourceManagerAgent",
    "SafetyDetectorAgent",
    "SafetyExecutorAgent",
    "SecurityManagerAgent",
    "StructureEnforcerAgent",
    "StructureHealerAgent",
    # Data classes
    "RuleSet",
    "ValidationReport",
    "Violation",
    "ViolationType",
    # Factory methods
    "create_legacy_syntax_validator",
    "create_legacy_canon_validator",
    "create_legacy_async_validator",
    "create_legacy_print_validator",
]
