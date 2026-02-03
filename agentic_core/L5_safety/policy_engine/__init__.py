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

from agentic_core.L5_safety.policy_engine.code_detector_agent_types import CodeDetectorAgent
from agentic_core.L5_safety.policy_engine.code_enforcer_agent_types import CodeEnforcerAgent
from agentic_core.L5_safety.policy_engine.code_healer_agent import CodeHealerAgent
from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
    CodeValidatorAgent,
    RuleSet,
    ValidationReport,
    Violation,
    ViolationType,
    create_legacy_async_validator,
    create_legacy_canon_validator,
    create_legacy_print_validator,
    create_legacy_syntax_validator,
)
from agentic_core.L5_safety.policy_engine.resource_manager_agent_types import ResourceManagerAgent
from agentic_core.L5_safety.policy_engine.safety_detector_agent_types import SafetyDetectorAgent

# from agentic_core.L5_safety.policy_engine.SafetyExecutorAgent import SafetyExecutorAgent  # Module not found
from agentic_core.L5_safety.policy_engine.security_manager_agent_types import SecurityManagerAgent
from agentic_core.L5_safety.policy_engine.structure_enforcer_agent_types import (
    StructureEnforcerAgent,
)
from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import StructureHealerAgent

__all__ = [
    # Sovereign agents (canonical namespace)
    "CodeValidatorAgent",
    "CodeDetectorAgent",
    "CodeEnforcerAgent",
    "CodeHealerAgent",
    "ResourceManagerAgent",
    "SafetyDetectorAgent",
    # "SafetyExecutorAgent",  # Module not found
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
