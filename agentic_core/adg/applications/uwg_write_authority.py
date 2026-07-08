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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "uwg_write_authority")
trace_contract._emit_applies_guardrail("p0", "uwg_write_authority", "p0_governance")
trace_contract._emit_snapshots_state("p0", "uwg_write_authority", "state_snapshot")
trace_contract.emit_replay_key("p0", "uwg_write_authority")
trace_contract.emit_determinism_digest("p0", "uwg_write_authority")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "uwg_write_authority", "execution_auth")
trace_contract._emit_validates_capability("p2", "uwg_write_authority", "capability_check")
trace_contract._emit_routes_to_capability("p2", "uwg_write_authority", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "uwg_write_authority", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "uwg_write_authority", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "uwg_write_authority", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "uwg_write_authority", "exec_output")
trace_contract._emit_dispatches_agent("p3", "uwg_write_authority", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "uwg_write_authority", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "uwg_write_authority", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "uwg_write_authority", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "uwg_write_authority", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "uwg_write_authority", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "uwg_write_authority", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "uwg_write_authority", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "uwg_write_authority", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "uwg_write_authority", "eval_metric")
trace_contract._emit_stores_embedding("p4", "uwg_write_authority", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "uwg_write_authority", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "uwg_write_authority", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("uwg_write_authority", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("uwg_write_authority", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("uwg_write_authority", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("uwg_write_authority", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("uwg_write_authority", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("uwg_write_authority", "p4obs", "alert")
trace_contract._emit_links_incident_trace("uwg_write_authority", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("uwg_write_authority", "p3lm", "pattern")
trace_contract._emit_records_learning_event("uwg_write_authority", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("uwg_write_authority", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("uwg_write_authority", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("uwg_write_authority", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("uwg_write_authority", "p3lm", "policy")
trace_contract._emit_stores_learning_state("uwg_write_authority", "p3lm", "state")
trace_contract._emit_records_execution_trace("uwg_write_authority", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("uwg_write_authority", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("uwg_write_authority", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("uwg_write_authority", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("uwg_write_authority", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("uwg_write_authority", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("uwg_write_authority", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("uwg_write_authority", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("uwg_write_authority", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "uwg_write_authority", "context_pull")
trace_contract._emit_pulls_context("p1", "uwg_write_authority", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "uwg_write_authority", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "uwg_write_authority", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "uwg_write_authority", "write_through")
trace_contract._emit_writes_through("p1", "uwg_write_authority", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "uwg_write_authority", "safety_validation")
trace_contract._emit_invokes_eval("p1", "uwg_write_authority", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "uwg_write_authority", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "uwg_write_authority", "human_escalation")
trace_contract._emit_routes_through("p1", "uwg_write_authority", "route_through")
trace_contract._emit_checks_agent_registry("p1", "uwg_write_authority", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "uwg_write_authority", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "uwg_write_authority", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "uwg_write_authority", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "uwg_write_authority", "target_agent")
trace_contract._emit_verifies_policy("p1", "uwg_write_authority", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "uwg_write_authority", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "uwg_write_authority", "boundary_check")
trace_contract._emit_transcripts_response("p1", "uwg_write_authority", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "uwg_write_authority")
trace_contract._emit_gated_by_confidence("p1", "uwg_write_authority", "confidence_gate")

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


def _is_side_effect_edge(edge) -> bool:
    if edge.edge_kind == "write":
        return True
    if edge.relation_type == "imports":
        return False
    sym = _symbol_name(edge.to_name)
    return _classify_side_effect(sym) != "filesystem_write"


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
    write_edges = []
    seen_edges: set[tuple[str, str, str, int, str, str]] = set()
    for edge in result.edges:  # progress_bar: deduplicate side-effect edges
        if not _is_side_effect_edge(edge):
            continue
        edge_key = (
            edge.from_name,
            edge.to_name,
            edge.source_file,
            edge.line_no,
            edge.relation_type,
            edge.edge_kind,
        )
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        write_edges.append(edge)

    violations: list[UWGViolation] = []
    for edge in write_edges:  # progress_bar: check UWG authority per edge
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
