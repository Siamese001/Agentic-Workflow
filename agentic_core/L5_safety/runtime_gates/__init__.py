"""Runtime Gate Mesh.

Implementation of the 29 runtime gates G01–G29 specified in
``docs/reference/05_Exit_Evaluation_&_Control/Evaluation_Runtime_Gates.md``.

Greenfield module — production wiring into L0/L1/L2/L3/L5 dispatch is tracked
as a NEXT_STEP follow-up to plan ``runtime-gates-impl-9c2e8a.md``.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import (
    GATE_REGISTRY,
    RuntimeGate,
    allow,
    deny,
    escalate,
    register_gate,
)
from agentic_core.L5_safety.runtime_gates.contracts import (
    SCHEMA_VERSION,
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    GraderType,
    RegressionSignal,
    Result,
    Severity,
)


def all_gates() -> list[str]:
    """Return the registered gate IDs in canonical G01..G29 order."""
    return sorted(GATE_REGISTRY.keys())


def get_gate(gate_id: str) -> RuntimeGate:
    """Return the registered gate for ``gate_id`` or raise KeyError."""
    if gate_id not in GATE_REGISTRY:
        raise KeyError(f"runtime gate {gate_id!r} not registered (registered: {all_gates()})")
    return GATE_REGISTRY[gate_id]


def evaluate(gate_id: str, ctx: GateContext) -> GateDecision:
    """Convenience: look up a gate and run its ``evaluate``."""
    return get_gate(gate_id).evaluate(ctx)


# Eagerly import every gate module so registration side effects fire when
# callers do `from agentic_core.L5_safety.runtime_gates import ...`.
# The list mirrors the 29 gates from the spec; missing files are tolerated
# during the staged W1..W5 implementation rollout.
_GATE_MODULES = [
    "g01_request_ingress",
    "g02_identity_session",
    "g03_intent_ambiguity",
    "g04_safety_policy",
    "g05_risk_tier",
    "g06_hitl_approval",
    "g07_route_selection",
    "g08_retrieval_grounding",
    "g09_evidence_quality",
    "g10_prompt_assembly",
    "g11_tool_model_registry",
    "g12_tool_argument",
    "g13_tool_output_trust",
    "g14_external_egress",
    "g15_filesystem_shell",
    "g16_memory_access",
    "g17_privacy_cross_context",
    "g18_workflow_trajectory",
    "g19_loop_retry_thrash",
    "g20_cost_latency_budget",
    "g21_output_schema",
    "g22_output_quality",
    "g23_security_leakage",
    "g24_determinism_replay",
    "g25_runtime_anomaly",
    "g26_exit_disposition",
    "g27_durable_write_sovereignty",
    "g28_audit_trace_completeness",
    "g29_learning_firewall",
]
for _mod in _GATE_MODULES:
    try:
        __import__(f"agentic_core.L5_safety.runtime_gates.{_mod}")
    except ImportError:  # guardian: allow-silent-swallow -- gate module not yet implemented: tolerated during rollout; other gates unaffected
        # Module not yet implemented — tolerated during rollout.
        pass


__all__ = [
    "Disposition",
    "DecisionAlias",
    "RegressionSignal",
    "GateContext",
    "GateDecision",
    "GraderType",
    "Result",
    "Severity",
    "SCHEMA_VERSION",
    "RuntimeGate",
    "GATE_REGISTRY",
    "register_gate",
    "allow",
    "deny",
    "escalate",
    "all_gates",
    "get_gate",
    "evaluate",
]
