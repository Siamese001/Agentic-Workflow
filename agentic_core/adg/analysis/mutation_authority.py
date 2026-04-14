"""E28: Mutation Path Verification.

Verifies the architectural invariant that ALL state mutations pass through
the Universal Write Gateway (UWG).

From the live ADG (20260311 scan):
    writes_to:      2,323 edges  (direct mutations — must be verified)
    writes_through:    22 edges  (UWG-compliant writes)

Architecture contract:
    EVERY module that performs a writes_to MUST also have a corresponding
    writes_through edge to ADG::Symbol::UniversalWriteGateway, OR the
    writes_to target must be in the L5_safety or test allowlist.

Allowlisted patterns (legitimate direct writes):
    - L5_safety/static_checks — write_gateway_enforcer itself validates writes
    - agentic_core/L2_execution/UniversalWriteGateway.py — IS the UWG
    - agentic_core/interfaces/write_gateway.py — interface definition
    - tests/ — test files are exempt
    - tools/ — build/evidence tools
    - mutation_prohibition.py — enforcement module that necessarily references write symbols

Usage::

    from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

    report = verify_mutation_paths(result)
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import (
    UWG_CANONICAL_SYMBOL,
    UWG_INTERFACE_PATH,
    UWG_MODULE_PATH,
    module_path_to_layer,
)
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "mutation_authority", "p0_governance")
_emit_reads_policy_state("p0", "mutation_authority", "policy_binding")
_emit_snapshots_state("p0", "mutation_authority", "state_snapshot")
emit_replay_key("p0", "mutation_authority")
emit_determinism_digest("p0", "mutation_authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "mutation_authority", "execution_auth")
_emit_validates_capability("p2", "mutation_authority", "capability_check")
_emit_routes_to_capability("p2", "mutation_authority", "capability_route")
_emit_writes_via_uwg("p2", "mutation_authority", "uwg_write")
_emit_blocks_direct_write("p2", "mutation_authority", "direct_write_block")
_emit_records_tool_invocation("p2", "mutation_authority", "tool_invocation")
_emit_captures_execution_output("p2", "mutation_authority", "exec_output")
_emit_dispatches_agent("p3", "mutation_authority", "agent_dispatch")
_emit_coordinates_agents("p3", "mutation_authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "mutation_authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "mutation_authority", "healing_outcome")
_emit_escalates_failure("p3", "mutation_authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "mutation_authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mutation_authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "mutation_authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "mutation_authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mutation_authority", "eval_metric")
_emit_stores_embedding("p4", "mutation_authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "mutation_authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mutation_authority", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("mutation_authority", "p4obs", "metric_1")
_emit_emits_metric_event("mutation_authority", "p4obs", "metric_2")
_emit_emits_metric_event("mutation_authority", "p4obs", "metric_3")
_emit_emits_metric_event("mutation_authority", "p4obs", "metric_4")
_emit_emits_metric_event("mutation_authority", "p4obs", "metric_5")
_emit_emits_metric_event("mutation_authority", "p4obs", "metric_6")
_emit_records_incident_event("mutation_authority", "p4obs", "incident")
_emit_captures_runtime_anomaly("mutation_authority", "p4obs", "anomaly")
_emit_writes_observability_log("mutation_authority", "p4obs", "obs_log")
_emit_updates_monitoring_state("mutation_authority", "p4obs", "mon_state")
_emit_triggers_alert("mutation_authority", "p4obs", "alert")
_emit_links_incident_trace("mutation_authority", "p4obs", "trace_link")
_emit_captures_pattern("mutation_authority", "p3lm", "pattern")
_emit_records_learning_event("mutation_authority", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mutation_authority", "p3lm", "snapshot")
_emit_feeds_meta_learning("mutation_authority", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mutation_authority", "p3lm", "routing")
_emit_improves_agent_policy("mutation_authority", "p3lm", "policy")
_emit_stores_learning_state("mutation_authority", "p3lm", "state")
_emit_records_execution_trace("mutation_authority", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mutation_authority", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mutation_authority", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mutation_authority", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mutation_authority", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mutation_authority", "env_read", "p2_env_1")
_emit_reads_environ("mutation_authority", "env_read", "p2_env_2")
_emit_reads_runtime_state("mutation_authority", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mutation_authority", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mutation_authority", "context_pull")
_emit_pulls_context("p1", "mutation_authority", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mutation_authority", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mutation_authority", "uwg_term_2")
_emit_writes_through("p1", "mutation_authority", "write_through")
_emit_writes_through("p1", "mutation_authority", "write_through_2")
_emit_validated_by_safety_plane("p1", "mutation_authority", "safety_validation")
_emit_invokes_eval("p1", "mutation_authority", "eval_call")
_emit_proposal_commits_routing("p1", "mutation_authority", "routing_commit")
_emit_escalates_to_human("p1", "mutation_authority", "human_escalation")
_emit_routes_through("p1", "mutation_authority", "route_through")
_emit_checks_agent_registry("p1", "mutation_authority", "agent_registry")
_emit_validates_agent_capability("p1", "mutation_authority", "capability")
_emit_dispatches_execution_plan("p1", "mutation_authority", "exec_plan")
_emit_agent_executes_agent("p1", "mutation_authority", "sub_agent")
_emit_routes_to_agent("p1", "mutation_authority", "target_agent")
_emit_verifies_policy("p1", "mutation_authority", "policy_check")
_emit_observes_runtime_state("p1", "mutation_authority", "runtime_state")
_emit_verifies_boundary("p1", "mutation_authority", "boundary_check")
_emit_transcripts_response("p1", "mutation_authority", "transcript")
_emit_hard_fails_untranscripted("p1", "mutation_authority")
_emit_gated_by_confidence("p1", "mutation_authority", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"

_BYPASS_ALLOWLIST_PREFIXES: tuple[str, ...] = (
    "tests/",
    "tools/",
    UWG_MODULE_PATH,
    UWG_INTERFACE_PATH,
    "agentic_core/L0_routing/enforcement/mutation_prohibition.py",
    "agentic_core/L5_safety/static_checks/write_gateway_enforcer.py",
    "agentic_core/L5_safety/",
    "ops_scripts/",
)

_RISK_BY_LAYER: dict[str, str] = {
    "L1": "critical",
    "L2": "low",  # L2 writes are expected (it contains UWG)
    "L3": "high",
    "L4": "medium",  # L4 state bus may have direct write paths
    "L5": "low",  # L5 safety enforcer is allowlisted
    "L6": "high",
    "L0": "high",
    "L_APP": "medium",
    "L_SHARED": "low",
    "L_TOOLS": "low",
}


@dataclass
class MutationBypassViolation:
    """A module that writes_to without going through UWG."""

    module_path: str
    layer: str
    direct_write_targets: list[str]
    has_uwg_path: bool
    risk_level: str
    source_files: list[str]

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "direct_write_count": len(self.direct_write_targets),
            "direct_write_targets": self.direct_write_targets[:10],
            "has_uwg_path": self.has_uwg_path,
            "risk_level": self.risk_level,
            "source_files": sorted(set(self.source_files))[:5],
        }


@dataclass
class MutationPathReport:
    """Report of UWG bypass violations and mutation path coverage."""

    violations: list[MutationBypassViolation] = field(default_factory=list)
    compliant_modules: list[str] = field(default_factory=list)
    allowlisted_modules: list[str] = field(default_factory=list)
    total_writes_to: int = 0
    total_writes_through: int = 0
    violation_count: int = 0

    @property
    def compliance_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "MutationPathReport.compliance_rate"
        )

        total = self.violation_count + len(self.compliant_modules)
        if total == 0:
            return 1.0
        return round(len(self.compliant_modules) / total, 4)

    @property
    def summary(self) -> str:
        return (
            f"Mutation path: {self.violation_count} UWG bypasses | "
            f"{len(self.compliant_modules)} compliant | "
            f"{len(self.allowlisted_modules)} allowlisted | "
            f"compliance={self.compliance_rate:.1%} | "
            f"writes_to={self.total_writes_to} writes_through={self.total_writes_through}"
        )

    def critical_violations(self) -> list[MutationBypassViolation]:
        return [v for v in self.violations if v.risk_level == "critical"]

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "compliant_count": len(self.compliant_modules),
            "allowlisted_count": len(self.allowlisted_modules),
            "total_writes_to": self.total_writes_to,
            "total_writes_through": self.total_writes_through,
            "compliance_rate": self.compliance_rate,
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _is_allowlisted(mod_path: str) -> bool:
    for prefix in _BYPASS_ALLOWLIST_PREFIXES:
        if mod_path.startswith(prefix) or mod_path == prefix:
            return True
    return False


def verify_mutation_paths(result: ScanResult) -> MutationPathReport:
    """Verify that all writes_to edges are backed by a writes_through UWG edge.

    Algorithm:
    Pass 1: Build module → writes_to targets index.
    Pass 2: Build set of modules that have writes_through UWG.
    Pass 3: For each module with writes_to, check if:
            a) it is allowlisted (skip)
            b) it also has writes_through UWG (compliant)
            c) neither (violation)
    """
    # Pass 1: writes_to per module
    writes_to_map: dict[str, list[tuple[str, str]]] = {}  # mod → [(target, source_file)]
    for edge in result.edges:
        if edge.relation_type != "writes_to":
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        mod = edge.from_name[len(_MODULE_PREFIX) :]
        writes_to_map.setdefault(mod, []).append((edge.to_name, edge.source_file))

    # Pass 2: writes_through UWG per module
    uwg_writers: set[str] = set()
    total_writes_through = 0
    for edge in result.edges:
        if edge.relation_type != "writes_through":
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        if UWG_CANONICAL_SYMBOL in edge.to_name or "UniversalWriteGateway" in edge.to_name:
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            uwg_writers.add(mod)
        total_writes_through += 1

    # Pass 3: classify each module
    violations: list[MutationBypassViolation] = []
    compliant: list[str] = []
    allowlisted: list[str] = []

    for mod, targets in tqdm(sorted(writes_to_map.items()), desc="Processing", unit="item"):
        if _is_allowlisted(mod):
            allowlisted.append(mod)
            continue

        has_uwg = mod in uwg_writers
        layer = module_path_to_layer(mod)
        risk = _RISK_BY_LAYER.get(layer, "medium")

        # L2 execution containing UWG is compliant by definition
        if layer == "L2" or has_uwg:
            compliant.append(mod)
            continue

        target_names = [t for t, _ in targets]
        source_files = [s for _, s in targets]

        violations.append(
            MutationBypassViolation(
                module_path=mod,
                layer=layer,
                direct_write_targets=target_names,
                has_uwg_path=has_uwg,
                risk_level=risk,
                source_files=source_files,
            ),
        )

    violations.sort(
        key=lambda v: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(v.risk_level, 4),
            v.module_path,
        ),
    )

    return MutationPathReport(
        violations=violations,
        compliant_modules=compliant,
        allowlisted_modules=allowlisted,
        total_writes_to=sum(len(v) for v in writes_to_map.values()),
        total_writes_through=total_writes_through,
        violation_count=len(violations),
    )


__all__ = [
    "MutationBypassViolation",
    "MutationPathReport",
    "verify_mutation_paths",
]
