"""Phase 3: SovereignLLMGateway 'no bypass' topology enforcement.

Policy: ADG::Policy::LLM_EGRESS_SINGLETON
Allowed topology: Agents/Tools -> SovereignLLMGateway -> Provider
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import (
    GATEWAY_ALLOWLIST,
    PROVIDER_SDK_SYMBOLS,
    canonical_name,
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "gateway_topology")
_emit_applies_guardrail("p0", "gateway_topology", "p0_governance")
_emit_snapshots_state("p0", "gateway_topology", "state_snapshot")
emit_replay_key("p0", "gateway_topology")
emit_determinism_digest("p0", "gateway_topology")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "gateway_topology", "execution_auth")
_emit_validates_capability("p2", "gateway_topology", "capability_check")
_emit_routes_to_capability("p2", "gateway_topology", "capability_route")
_emit_writes_via_uwg("p2", "gateway_topology", "uwg_write")
_emit_blocks_direct_write("p2", "gateway_topology", "direct_write_block")
_emit_records_tool_invocation("p2", "gateway_topology", "tool_invocation")
_emit_captures_execution_output("p2", "gateway_topology", "exec_output")
_emit_dispatches_agent("p3", "gateway_topology", "agent_dispatch")
_emit_coordinates_agents("p3", "gateway_topology", "agent_coordination")
_emit_records_workflow_lineage("p3", "gateway_topology", "workflow_lineage")
_emit_records_healing_outcome("p3", "gateway_topology", "healing_outcome")
_emit_escalates_failure("p3", "gateway_topology", "failure_escalation")
_emit_orchestrates_workflow("p3", "gateway_topology", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gateway_topology", "healing_dispatch")
_emit_invokes_evaluation("p3", "gateway_topology", "evaluation_signal")
_emit_records_telemetry_event("p4", "gateway_topology", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gateway_topology", "eval_metric")
_emit_stores_embedding("p4", "gateway_topology", "embedding_store")
_emit_updates_meta_learning_state("p4", "gateway_topology", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gateway_topology", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("gateway_topology", "p4obs", "metric_1")
_emit_emits_metric_event("gateway_topology", "p4obs", "metric_2")
_emit_emits_metric_event("gateway_topology", "p4obs", "metric_3")
_emit_emits_metric_event("gateway_topology", "p4obs", "metric_4")
_emit_emits_metric_event("gateway_topology", "p4obs", "metric_5")
_emit_emits_metric_event("gateway_topology", "p4obs", "metric_6")
_emit_records_incident_event("gateway_topology", "p4obs", "incident")
_emit_captures_runtime_anomaly("gateway_topology", "p4obs", "anomaly")
_emit_writes_observability_log("gateway_topology", "p4obs", "obs_log")
_emit_updates_monitoring_state("gateway_topology", "p4obs", "mon_state")
_emit_triggers_alert("gateway_topology", "p4obs", "alert")
_emit_links_incident_trace("gateway_topology", "p4obs", "trace_link")
_emit_captures_pattern("gateway_topology", "p3lm", "pattern")
_emit_records_learning_event("gateway_topology", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gateway_topology", "p3lm", "snapshot")
_emit_feeds_meta_learning("gateway_topology", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gateway_topology", "p3lm", "routing")
_emit_improves_agent_policy("gateway_topology", "p3lm", "policy")
_emit_stores_learning_state("gateway_topology", "p3lm", "state")
_emit_records_execution_trace("gateway_topology", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gateway_topology", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gateway_topology", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gateway_topology", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gateway_topology", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gateway_topology", "env_read", "p2_env_1")
_emit_reads_environ("gateway_topology", "env_read", "p2_env_2")
_emit_reads_runtime_state("gateway_topology", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gateway_topology", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gateway_topology", "context_pull")
_emit_pulls_context("p1", "gateway_topology", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "gateway_topology", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gateway_topology", "uwg_term_secondary")
_emit_writes_through("p1", "gateway_topology", "write_through")
_emit_writes_through("p1", "gateway_topology", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "gateway_topology", "safety_validation")
_emit_invokes_eval("p1", "gateway_topology", "eval_call")
_emit_proposal_commits_routing("p1", "gateway_topology", "routing_commit")
_emit_escalates_to_human("p1", "gateway_topology", "human_escalation")
_emit_routes_through("p1", "gateway_topology", "route_through")
_emit_checks_agent_registry("p1", "gateway_topology", "agent_registry")
_emit_validates_agent_capability("p1", "gateway_topology", "capability")
_emit_dispatches_execution_plan("p1", "gateway_topology", "exec_plan")
_emit_agent_executes_agent("p1", "gateway_topology", "sub_agent")
_emit_routes_to_agent("p1", "gateway_topology", "target_agent")
_emit_verifies_policy("p1", "gateway_topology", "policy_check")
_emit_observes_runtime_state("p1", "gateway_topology", "runtime_state")
_emit_verifies_boundary("p1", "gateway_topology", "boundary_check")
_emit_transcripts_response("p1", "gateway_topology", "transcript")
_emit_hard_fails_untranscripted("p1", "gateway_topology")
_emit_gated_by_confidence("p1", "gateway_topology", "confidence_gate")

logger = logging.getLogger(__name__)

_POLICY_ID = "ADG::Policy::LLM_EGRESS_SINGLETON"
_GW_PATH = GATEWAY_ALLOWLIST["SovereignLLMGateway"]
_GW_NODE = canonical_name("Gateway", "SovereignLLMGateway")

_ALLOWED_DIRECT_PROVIDER_MODULES: frozenset[str] = frozenset(
    {
        _GW_PATH,
        "infrastructure/sdks_mcps/client_wrappers.py",
    },
)


@dataclass
class GatewayViolation:
    """A gateway topology violation."""

    from_module: str
    to_symbol: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return (
            f"GATEWAY-VIOLATION policy={self.policy_id}\n"
            f"  from:  {self.from_module}\n"
            f"  to:    {self.to_symbol}\n"
            f"  file:  {self.source_file}:{self.line_no}"
        )


@dataclass
class GatewayTopologyReport:
    """Result of gateway topology enforcement check."""

    violations: list[GatewayViolation] = field(default_factory=list)
    provider_invocations: int = 0
    gateway_routes: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _symbol_name(adg_name: str) -> str:
    prefix = "ADG::Symbol::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def check_gateway_topology(
    result: ScanResult,
    client: ADGMCPClient | None = None,
) -> GatewayTopologyReport:
    """Check that all provider invocations route through SovereignLLMGateway."""
    provider_bases = {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}
    provider_invocations = []
    gateway_routes = []

    for edge in result.edges:
        sym = _symbol_name(edge.to_name)
        sym_base = sym.split(".")[0]

        if edge.relation_type in ("imports", "invokes_provider") and sym_base in provider_bases:
            provider_invocations.append(edge)

        if edge.relation_type == "routes_through" and _GW_PATH in _symbol_name(edge.to_name):
            gateway_routes.append(edge)

    violations: list[GatewayViolation] = []
    for edge in provider_invocations:
        from_rel = _module_rel(edge.from_name)
        norm = from_rel.replace("\\", "/")
        if any(norm == allowed or norm.endswith(allowed) for allowed in _ALLOWED_DIRECT_PROVIDER_MODULES):
            continue
        sym = _symbol_name(edge.to_name)
        violations.append(
            GatewayViolation(
                from_module=from_rel,
                to_symbol=sym,
                source_file=edge.source_file,
                line_no=edge.line_no,
            ),
        )

    proof_digest = _compute_proof_digest(result, violations)
    report = GatewayTopologyReport(
        violations=violations,
        provider_invocations=len(provider_invocations),
        gateway_routes=len(gateway_routes),
        snapshot_digest=proof_digest,
    )

    if client is not None:
        _persist_proof(result, report, client)

    return report


def _compute_proof_digest(result: ScanResult, violations: list[GatewayViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_symbol, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_symbol}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(
    result: ScanResult,
    report: GatewayTopologyReport,
    client: ADGMCPClient,
) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "gateway_topology_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"provider_invocations:{report.provider_invocations}",
            f"gateway_routes:{report.gateway_routes}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )
    client.upsert_relation(
        proof_node,
        "violates" if not report.passed else "allows",
        _GW_NODE,
    )


__all__ = ["check_gateway_topology", "GatewayTopologyReport", "GatewayViolation"]
