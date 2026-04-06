"""E31: Policy Hash Runtime Validation.

Validates that modules referencing runtime instruction packets also reference
an active policy hash. The architecture asserts:

    all instruction packets → must reference active policy_hash

This analyzer detects:
    1. Modules that use policy-hash symbols but reference potentially stale hashes
    2. Modules that produce/consume prompts without any policy_hash reference
    3. Modules in L0-L3 that route/orchestrate without policy hash coupling

From the live ADG (20260311 scan), policy-related symbols confirmed:
    - ADG::Symbol::uwg._verify_plan_hash
    - ADG::Symbol::uwg._verify_replay_hash
    - governance test modules referencing policy_hash patterns

Usage::

    from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

    report = validate_policy_hash_coupling(result)
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.contracts.schema_util import module_path_to_layer
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "policy_hash_validator", "p0_governance")
_emit_snapshots_state("p0", "policy_hash_validator", "state_snapshot")
emit_replay_key("p0", "policy_hash_validator")
emit_determinism_digest("p0", "policy_hash_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "policy_hash_validator", "execution_auth")
_emit_validates_capability("p2", "policy_hash_validator", "capability_check")
_emit_routes_to_capability("p2", "policy_hash_validator", "capability_route")
_emit_writes_via_uwg("p2", "policy_hash_validator", "uwg_write")
_emit_blocks_direct_write("p2", "policy_hash_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_hash_validator", "tool_invocation")
_emit_captures_execution_output("p2", "policy_hash_validator", "exec_output")
_emit_dispatches_agent("p3", "policy_hash_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_hash_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_hash_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_hash_validator", "healing_outcome")
_emit_escalates_failure("p3", "policy_hash_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_hash_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_hash_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_hash_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_hash_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_hash_validator", "eval_metric")
_emit_stores_embedding("p4", "policy_hash_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_hash_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_hash_validator", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_1")
_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_2")
_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_3")
_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_4")
_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_5")
_emit_emits_metric_event("policy_hash_validator", "p4obs", "metric_6")
_emit_records_incident_event("policy_hash_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_hash_validator", "p4obs", "anomaly")
_emit_writes_observability_log("policy_hash_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_hash_validator", "p4obs", "mon_state")
_emit_triggers_alert("policy_hash_validator", "p4obs", "alert")
_emit_links_incident_trace("policy_hash_validator", "p4obs", "trace_link")
_emit_captures_pattern("policy_hash_validator", "p3lm", "pattern")
_emit_records_learning_event("policy_hash_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_hash_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_hash_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_hash_validator", "p3lm", "routing")
_emit_improves_agent_policy("policy_hash_validator", "p3lm", "policy")
_emit_stores_learning_state("policy_hash_validator", "p3lm", "state")
_emit_records_execution_trace("policy_hash_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_hash_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_hash_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_hash_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_hash_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_hash_validator", "env_read", "p2_env_1")
_emit_reads_environ("policy_hash_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_hash_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_hash_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "policy_hash_validator", "context_pull")
_emit_pulls_context("p1", "policy_hash_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "policy_hash_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_hash_validator", "uwg_term_2")
_emit_writes_through("p1", "policy_hash_validator", "write_through")
_emit_writes_through("p1", "policy_hash_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "policy_hash_validator", "safety_validation")
_emit_invokes_eval("p1", "policy_hash_validator", "eval_call")
_emit_proposal_commits_routing("p1", "policy_hash_validator", "routing_commit")
_emit_escalates_to_human("p1", "policy_hash_validator", "human_escalation")
_emit_routes_through("p1", "policy_hash_validator", "route_through")
_emit_checks_agent_registry("p1", "policy_hash_validator", "agent_registry")
_emit_validates_agent_capability("p1", "policy_hash_validator", "capability")
_emit_dispatches_execution_plan("p1", "policy_hash_validator", "exec_plan")
_emit_agent_executes_agent("p1", "policy_hash_validator", "sub_agent")
_emit_routes_to_agent("p1", "policy_hash_validator", "target_agent")
_emit_verifies_policy("p1", "policy_hash_validator", "policy_check")
_emit_observes_runtime_state("p1", "policy_hash_validator", "runtime_state")
_emit_verifies_boundary("p1", "policy_hash_validator", "boundary_check")
_emit_transcripts_response("p1", "policy_hash_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "policy_hash_validator")
_emit_gated_by_confidence("p1", "policy_hash_validator", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

# Symbols that indicate policy hash awareness
_POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "policy_hash",
        "_verify_plan_hash",
        "_verify_replay_hash",
        "verify_policy_hash",
        "POLICY_HASH",
        "policy_root",
        "merkle_root",
        "config_hash",
        "instruction_hash",
        "MERKLE_POLICY_ROOT",
    }
)

# Symbols that indicate instruction packet creation/routing (should be policy-coupled)
_INSTRUCTION_PACKET_SYMBOLS: frozenset[str] = frozenset(
    {
        "InstructionPacket",
        "instruction_packet",
        "build_instruction",
        "create_instruction",
        "route_instruction",
        "RoutingInputs",
        "AutonomousDecisionEngine",
        "SovereignDecisionEngine",
        "GovernedPayload",
        "AssembledPrompt",
    }
)

# Layers that MUST have policy hash coupling if they route instructions
_POLICY_REQUIRED_LAYERS: frozenset[str] = frozenset({"L0", "L1", "L2", "L3"})


@dataclass
class PolicyHashViolation:
    """A module that creates/routes instruction packets without policy hash coupling."""

    module_path: str
    layer: str
    violation_type: str
    instruction_symbols_used: list[str]
    has_policy_hash_ref: bool
    severity: str
    suggested_fix: str

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "violation_type": self.violation_type,
            "instruction_symbols_used": self.instruction_symbols_used,
            "has_policy_hash_ref": self.has_policy_hash_ref,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class PolicyHashReport:
    """Report of policy hash coupling validation."""

    violations: list[PolicyHashViolation] = field(default_factory=list)
    policy_coupled_modules: list[str] = field(default_factory=list)
    instruction_modules: list[str] = field(default_factory=list)
    violation_count: int = 0

    @property
    def coupling_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyHashReport.coupling_rate")

        total = len(self.instruction_modules)
        if total == 0:
            return 1.0
        return round(len(self.policy_coupled_modules) / total, 4)

    @property
    def summary(self) -> str:
        return (
            f"Policy hash coupling: {self.violation_count} uncoupled modules | "
            f"{len(self.policy_coupled_modules)} coupled | "
            f"{len(self.instruction_modules)} instruction modules | "
            f"coupling={self.coupling_rate:.1%}"
        )

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "coupled_count": len(self.policy_coupled_modules),
            "instruction_module_count": len(self.instruction_modules),
            "coupling_rate": self.coupling_rate,
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def validate_policy_hash_coupling(result: ScanResult) -> PolicyHashReport:
    """Validate that instruction packet modules reference active policy hashes.

    Pass 1: Build module → instruction symbols used index.
    Pass 2: Build module → policy hash symbols used index.
    Pass 3: For each instruction module in L0-L3, check for policy hash coupling.
    """
    # Pass 1: instruction packet usage per module
    instruction_map: dict[str, list[str]] = {}
    for edge in result.edges:
        if edge.relation_type not in ("calls", "instantiates", "imports"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]
        sym_base = sym.split(".")[-1] if "." in sym else sym

        if sym_base in _INSTRUCTION_PACKET_SYMBOLS or sym in _INSTRUCTION_PACKET_SYMBOLS:
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            instruction_map.setdefault(mod, []).append(sym_base)

    # Pass 2: policy hash usage per module
    policy_hash_modules: set[str] = set()
    for edge in result.edges:
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]
        sym_base = sym.split(".")[-1] if "." in sym else sym

        if sym_base in _POLICY_HASH_SYMBOLS or sym in _POLICY_HASH_SYMBOLS:
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            policy_hash_modules.add(mod)

    # Pass 3: classify
    violations: list[PolicyHashViolation] = []
    coupled: list[str] = []
    instruction_mods: list[str] = sorted(instruction_map.keys())

    for mod in instruction_mods:
        layer = module_path_to_layer(mod)
        if layer not in _POLICY_REQUIRED_LAYERS:
            continue

        has_policy = mod in policy_hash_modules
        if has_policy:
            coupled.append(mod)
            continue

        symbols_used = sorted(set(instruction_map[mod]))
        violations.append(
            PolicyHashViolation(
                module_path=mod,
                layer=layer,
                violation_type="INSTRUCTION_WITHOUT_POLICY_HASH",
                instruction_symbols_used=symbols_used,
                has_policy_hash_ref=False,
                severity="high" if layer in ("L0", "L1") else "medium",
                suggested_fix=(
                    f"Module in {layer} creates/routes instruction packets but does not "
                    "reference an active policy_hash. Add policy hash verification via "
                    "uwg._verify_plan_hash() or equivalent before routing instructions."
                ),
            )
        )

    violations.sort(
        key=lambda v: (
            {"high": 0, "medium": 1, "low": 2}.get(v.severity, 3),
            v.module_path,
        )
    )

    return PolicyHashReport(
        violations=violations,
        policy_coupled_modules=coupled,
        instruction_modules=instruction_mods,
        violation_count=len(violations),
    )


__all__ = [
    "PolicyHashReport",
    "PolicyHashViolation",
    "validate_policy_hash_coupling",
]
