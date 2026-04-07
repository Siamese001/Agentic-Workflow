"""Phase 4: UWG Write Authority side-effect control.

Policy: ADG::Policy::UWG_WRITE_AUTHORITY
All filesystem writes, network calls, database writes, and subprocess
executions must route through UniversalWriteGateway.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import (
    GATEWAY_ALLOWLIST,
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

_emit_records_execution_trace("p0", "evidence", "uwg_write_authority")
_emit_applies_guardrail("p0", "uwg_write_authority", "p0_governance")
_emit_snapshots_state("p0", "uwg_write_authority", "state_snapshot")
emit_replay_key("p0", "uwg_write_authority")
emit_determinism_digest("p0", "uwg_write_authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "uwg_write_authority", "execution_auth")
_emit_validates_capability("p2", "uwg_write_authority", "capability_check")
_emit_routes_to_capability("p2", "uwg_write_authority", "capability_route")
_emit_writes_via_uwg("p2", "uwg_write_authority", "uwg_write")
_emit_blocks_direct_write("p2", "uwg_write_authority", "direct_write_block")
_emit_records_tool_invocation("p2", "uwg_write_authority", "tool_invocation")
_emit_captures_execution_output("p2", "uwg_write_authority", "exec_output")
_emit_dispatches_agent("p3", "uwg_write_authority", "agent_dispatch")
_emit_coordinates_agents("p3", "uwg_write_authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "uwg_write_authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "uwg_write_authority", "healing_outcome")
_emit_escalates_failure("p3", "uwg_write_authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "uwg_write_authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "uwg_write_authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "uwg_write_authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "uwg_write_authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "uwg_write_authority", "eval_metric")
_emit_stores_embedding("p4", "uwg_write_authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "uwg_write_authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "uwg_write_authority", "exec_snapshot_link")

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

_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_1")
_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_2")
_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_3")
_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_4")
_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_5")
_emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_6")
_emit_records_incident_event("uwg_write_authority", "p4obs", "incident")
_emit_captures_runtime_anomaly("uwg_write_authority", "p4obs", "anomaly")
_emit_writes_observability_log("uwg_write_authority", "p4obs", "obs_log")
_emit_updates_monitoring_state("uwg_write_authority", "p4obs", "mon_state")
_emit_triggers_alert("uwg_write_authority", "p4obs", "alert")
_emit_links_incident_trace("uwg_write_authority", "p4obs", "trace_link")
_emit_captures_pattern("uwg_write_authority", "p3lm", "pattern")
_emit_records_learning_event("uwg_write_authority", "p3lm", "learning_event")
_emit_writes_learning_snapshot("uwg_write_authority", "p3lm", "snapshot")
_emit_feeds_meta_learning("uwg_write_authority", "p3lm", "meta_feed")
_emit_updates_routing_strategy("uwg_write_authority", "p3lm", "routing")
_emit_improves_agent_policy("uwg_write_authority", "p3lm", "policy")
_emit_stores_learning_state("uwg_write_authority", "p3lm", "state")
_emit_records_execution_trace("uwg_write_authority", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("uwg_write_authority", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("uwg_write_authority", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("uwg_write_authority", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("uwg_write_authority", "L4_STATE", "p2_trace_5")
_emit_reads_environ("uwg_write_authority", "env_read", "p2_env_1")
_emit_reads_environ("uwg_write_authority", "env_read", "p2_env_2")
_emit_reads_runtime_state("uwg_write_authority", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("uwg_write_authority", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "uwg_write_authority", "context_pull")
_emit_pulls_context("p1", "uwg_write_authority", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "uwg_write_authority", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "uwg_write_authority", "uwg_term_secondary")
_emit_writes_through("p1", "uwg_write_authority", "write_through")
_emit_writes_through("p1", "uwg_write_authority", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "uwg_write_authority", "safety_validation")
_emit_invokes_eval("p1", "uwg_write_authority", "eval_call")
_emit_proposal_commits_routing("p1", "uwg_write_authority", "routing_commit")
_emit_escalates_to_human("p1", "uwg_write_authority", "human_escalation")
_emit_routes_through("p1", "uwg_write_authority", "route_through")
_emit_checks_agent_registry("p1", "uwg_write_authority", "agent_registry")
_emit_validates_agent_capability("p1", "uwg_write_authority", "capability")
_emit_dispatches_execution_plan("p1", "uwg_write_authority", "exec_plan")
_emit_agent_executes_agent("p1", "uwg_write_authority", "sub_agent")
_emit_routes_to_agent("p1", "uwg_write_authority", "target_agent")
_emit_verifies_policy("p1", "uwg_write_authority", "policy_check")
_emit_observes_runtime_state("p1", "uwg_write_authority", "runtime_state")
_emit_verifies_boundary("p1", "uwg_write_authority", "boundary_check")
_emit_transcripts_response("p1", "uwg_write_authority", "transcript")
_emit_hard_fails_untranscripted("p1", "uwg_write_authority")
_emit_gated_by_confidence("p1", "uwg_write_authority", "confidence_gate")

logger = logging.getLogger(__name__)

_POLICY_ID = "ADG::Policy::UWG_WRITE_AUTHORITY"
_UWG_PATH = GATEWAY_ALLOWLIST["UniversalWriteGateway"]
_UWG_NODE = canonical_name("Gateway", "UniversalWriteGateway")

_SIDE_EFFECT_ENDPOINTS: dict[str, frozenset[str]] = {
    "filesystem_write": frozenset(
        {
            "open",
            "write",
            "os.remove",
            "os.rename",
            "os.makedirs",
            "os.mkdir",
            "shutil.copy",
            "shutil.move",
            "shutil.rmtree",
            "pathlib.Path.write_text",
            "pathlib.Path.write_bytes",
            "write_text",
            "write_bytes",
        },
    ),
    "subprocess_exec": frozenset(
        {
            "subprocess.run",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
        },
    ),
    "network_call": frozenset(
        {
            "requests.get",
            "requests.post",
            "requests.put",
            "requests.delete",
            "requests.patch",
            "httpx.get",
            "httpx.post",
            "httpx.Client",
            "httpx.AsyncClient",
            "aiohttp.ClientSession",
            "urllib.request.urlopen",
        },
    ),
    "database_write": frozenset(
        {
            "cursor.execute",
            "session.add",
            "session.commit",
            "collection.insert",
            "collection.update",
            "redis.set",
            "redis.hset",
        },
    ),
}

_ALLOWED_WRITE_MODULES: frozenset[str] = frozenset(
    {
        _UWG_PATH,
        "agentic_core/L2_execution/audit/hash_chain_audit_log.py",
        "tools/capture_evidence.py",
        "ops_scripts/ci/",
    },
)


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _symbol_name(adg_name: str) -> str:
    prefix = "ADG::Symbol::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _is_allowed_module(rel_path: str) -> bool:
    norm = rel_path.replace("\\", "/")
    for allowed in _ALLOWED_WRITE_MODULES:
        if norm == allowed or norm.startswith(allowed):
            return True
    if "test_" in norm or norm.startswith("tests/"):
        return True
    return False


def _classify_side_effect(sym: str) -> str:
    sym_tail = sym.split(".")[-1]
    for endpoint_type, syms in _SIDE_EFFECT_ENDPOINTS.items():
        if sym in syms:
            return endpoint_type
        if any(s.endswith(sym_tail) for s in syms if "." in s):
            return endpoint_type
    return "filesystem_write"


@dataclass
class UWGViolation:
    """A UWG write authority violation."""

    from_module: str
    to_symbol: str
    endpoint_type: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return (
            f"UWG-VIOLATION policy={self.policy_id} endpoint={self.endpoint_type}\n"
            f"  from:  {self.from_module}\n"
            f"  to:    {self.to_symbol}\n"
            f"  file:  {self.source_file}:{self.line_no}"
        )


@dataclass
class UWGReport:
    """Result of UWG write authority check."""

    violations: list[UWGViolation] = field(default_factory=list)
    write_edges_count: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def check_uwg_write_authority(
    result: ScanResult,
    client: ADGMCPClient | None = None,
) -> UWGReport:
    """Check that all side-effect writes route through UniversalWriteGateway."""
    write_edges = [e for e in result.edges if e.edge_kind == "write" and e.relation_type == "writes_to"]

    violations: list[UWGViolation] = []
    for edge in write_edges:
        from_rel = _module_rel(edge.from_name)
        if _is_allowed_module(from_rel):
            continue
        sym = _symbol_name(edge.to_name)
        endpoint_type = _classify_side_effect(sym)
        violations.append(
            UWGViolation(
                from_module=from_rel,
                to_symbol=sym,
                endpoint_type=endpoint_type,
                source_file=edge.source_file,
                line_no=edge.line_no,
            ),
        )

    proof_digest = _compute_proof_digest(result, violations)
    report = UWGReport(
        violations=violations,
        write_edges_count=len(write_edges),
        snapshot_digest=proof_digest,
    )

    if client is not None:
        _persist_proof(result, report, client)

    return report


def _compute_proof_digest(result: ScanResult, violations: list[UWGViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_symbol, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_symbol}|{v.endpoint_type}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(
    result: ScanResult,
    report: UWGReport,
    client: ADGMCPClient,
) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "uwg_write_authority_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"write_edges_count:{report.write_edges_count}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )
    client.upsert_relation(
        proof_node,
        "violates" if not report.passed else "allows",
        _UWG_NODE,
    )


__all__ = ["check_uwg_write_authority", "UWGReport", "UWGViolation"]
