"""Programmatic Tool Calling (PTC) Module

Implements the PTC v2 specification for inference batching and context isolation.

Architecture:
    [PTC Script] → [Orchestrator] → [Safety Gates] → [HITL (if needed)] → [Sandbox Execute] → [Summary]

Key Components:
- PTCOrchestrator: Manages script parsing and batch execution
- PTCSafetyGateManager: Coordinates all safety gates
- PTCHITLIntegration: Human review workflows
- PTCSandboxExecutor: Isolated execution environment

Usage:
    from agentic_core.L3_orchestration.reasoning.ptc import (
        PTCOrchestrator,
        PTCSafetyGateManager,
        PTCHITLIntegration,
        parse_ptc_script,
        execute_ptc_batch,
    )

    # Parse and execute
    plan = parse_ptc_script("script-001", code)
    result = execute_ptc_batch(plan)
"""

from __future__ import annotations

from agentic_core.L2_execution.types.ptc_tool_contracts_types import (
    ToolCall as L2ToolCall,
)
from agentic_core.L2_execution.types.ptc_tool_contracts_types import (
    ToolContractViolation,
    ToolResult,
)

# L2 Execution Contracts
from agentic_core.L2_execution.utils.ptc_contract import (
    PTC_STDOUT_BYTE_CAP,
    PTCBytesCapExceeded,
    PTCContractEnforcer,
    PTCContractViolation,
    PTCUnsignedEnvelopeError,
    redact_output,
)

# Built-in Tools
from agentic_core.L3_orchestration.reasoning.ptc.builtin_tools import (
    expr_eval_handler,
    register_builtin_tools,
    repo_rg_handler,
)

# PTC HITL Integration (New)
from agentic_core.L3_orchestration.reasoning.ptc.ptc_hitl_integration import (
    PTCHITLIntegration,
    PTCHumanDecision,
    PTCHumanReviewRecord,
    PTCSafetyAssessment,
    PTCSafetyGateResult,
    PTCScriptRiskLevel,
    assess_ptc_script_safety,
    generate_ptc_dpo_pair,
    get_ptc_hitl_integration,
    perform_ptc_l5_reclear,
    request_ptc_human_review,
    reset_ptc_hitl_integration,
)

# PTC Orchestrator (New)
from agentic_core.L3_orchestration.reasoning.ptc.ptc_orchestrator import (
    PTCExecutionResult,
    PTCOrchestrator,
    PTCSandboxContext,
    PTCSandboxExecutor,
    PTCScriptPlan,
    execute_in_ptc_sandbox,
    execute_ptc_batch,
    get_ptc_orchestrator,
    get_ptc_sandbox,
    parse_ptc_script,
    reset_ptc_orchestrator,
    reset_ptc_sandbox,
)

# PTC Registry
from agentic_core.L3_orchestration.reasoning.ptc.ptc_registry import (
    ToolRegistry,
    get_global_registry,
    get_tool,
    list_tools,
    register_tool,
)

# PTC Safety Gates (New)
from agentic_core.L3_orchestration.reasoning.ptc.ptc_safety_gates import (
    PTCConfidenceGate,
    PTCExecutionGate,
    PTCRoutingGate,
    PTCSafetyGateManager,
    PTCSafetyGateResult,
    PTCSafetyGateStatus,
    PTCSafetyGateType,
    PTCSafetyGateViolation,
    PTCValidationGate,
    check_ptc_safety_passed,
    evaluate_ptc_safety_gates,
    get_ptc_safety_gate_manager,
    reset_ptc_safety_gate_manager,
)

# Tool Call Store
from agentic_core.L3_orchestration.reasoning.ptc.tool_call_store import (
    ToolCallStore,
    get_tool_call_store,
    list_tool_calls,
    record_tool_call,
)

# Core PTC types
from agentic_core.L3_orchestration.reasoning.ptc.tool_contract import (
    ToolArg,
    ToolCall,
    ToolCallResult,
    ToolSpec,
    canonical_json,
    generate_call_id,
    hash_result_data,
    sha256_hex,
    tool_call_result_to_json,
    tool_call_to_json,
    tool_spec_to_json,
)

# Tool Invoker
from agentic_core.L3_orchestration.reasoning.ptc.tool_invoker import (
    ToolInvoker,
)

__version__ = "2.0.0"

__all__ = [
    # Version
    "__version__",

    # Core Types
    "ToolArg",
    "ToolCall",
    "ToolCallResult",
    "ToolSpec",
    "canonical_json",
    "generate_call_id",
    "hash_result_data",
    "sha256_hex",
    "tool_call_result_to_json",
    "tool_call_to_json",
    "tool_spec_to_json",

    # Registry
    "ToolRegistry",
    "get_global_registry",
    "get_tool",
    "list_tools",
    "register_tool",

    # Invoker
    "ToolInvoker",

    # Store
    "ToolCallStore",
    "get_tool_call_store",
    "list_tool_calls",
    "record_tool_call",

    # Built-in Tools
    "expr_eval_handler",
    "register_builtin_tools",
    "repo_rg_handler",

    # Orchestrator
    "PTCExecutionResult",
    "PTCOrchestrator",
    "PTCScriptPlan",
    "PTCSandboxContext",
    "PTCSandboxExecutor",
    "execute_in_ptc_sandbox",
    "execute_ptc_batch",
    "get_ptc_orchestrator",
    "get_ptc_sandbox",
    "parse_ptc_script",
    "reset_ptc_orchestrator",
    "reset_ptc_sandbox",

    # HITL Integration
    "PTCHITLIntegration",
    "PTCHumanDecision",
    "PTCHumanReviewRecord",
    "PTCSafetyAssessment",
    "PTCSafetyGateResult",
    "PTCScriptRiskLevel",
    "assess_ptc_script_safety",
    "generate_ptc_dpo_pair",
    "get_ptc_hitl_integration",
    "perform_ptc_l5_reclear",
    "request_ptc_human_review",
    "reset_ptc_hitl_integration",

    # Safety Gates
    "PTCConfidenceGate",
    "PTCExecutionGate",
    "PTCRoutingGate",
    "PTCSafetyGateManager",
    "PTCSafetyGateResult",
    "PTCSafetyGateStatus",
    "PTCSafetyGateType",
    "PTCSafetyGateViolation",
    "PTCValidationGate",
    "check_ptc_safety_passed",
    "evaluate_ptc_safety_gates",
    "get_ptc_safety_gate_manager",
    "reset_ptc_safety_gate_manager",

    # L2 Contracts
    "PTCBytesCapExceeded",
    "PTCContractEnforcer",
    "PTCContractViolation",
    "PTCUnsignedEnvelopeError",
    "PTC_STDOUT_BYTE_CAP",
    "redact_output",
    "L2ToolCall",
    "ToolResult",
    "ToolContractViolation",
]

# Auto-register built-in tools on import
register_builtin_tools()
