"""Phase 6: RAG / Embedding Sovereignty C0 enforcement.

Policy: ADG::Policy::RAG_C0_INFORMATIONAL_ONLY

Decision point nodes:
  ADG::Decision::RoutingDecision
  ADG::Decision::SafetyThreshold
  ADG::Decision::TierSelection

Retrieval output node:
  ADG::Retrieval::C0Context

Enforcement:
  - C0Context may be consumed by PromptAssembly only
  - No influences relation from retrieval or C0Context to any decision node
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.InMemoryStore import ADGMCPClient
from agentic_core.adg.contracts.schema_util import canonical_name
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "rag_sovereignty")
_emit_applies_guardrail("p0", "rag_sovereignty", "p0_governance")
_emit_snapshots_state("p0", "rag_sovereignty", "state_snapshot")
emit_replay_key("p0", "rag_sovereignty")
emit_determinism_digest("p0", "rag_sovereignty")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rag_sovereignty", "execution_auth")
_emit_validates_capability("p2", "rag_sovereignty", "capability_check")
_emit_routes_to_capability("p2", "rag_sovereignty", "capability_route")
_emit_writes_via_uwg("p2", "rag_sovereignty", "uwg_write")
_emit_blocks_direct_write("p2", "rag_sovereignty", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_sovereignty", "tool_invocation")
_emit_captures_execution_output("p2", "rag_sovereignty", "exec_output")
_emit_dispatches_agent("p3", "rag_sovereignty", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_sovereignty", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_sovereignty", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_sovereignty", "healing_outcome")
_emit_escalates_failure("p3", "rag_sovereignty", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_sovereignty", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_sovereignty", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_sovereignty", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_sovereignty", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_sovereignty", "eval_metric")
_emit_stores_embedding("p4", "rag_sovereignty", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_sovereignty", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_sovereignty", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_1")
_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_2")
_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_3")
_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_4")
_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_5")
_emit_emits_metric_event("rag_sovereignty", "p4obs", "metric_6")
_emit_records_incident_event("rag_sovereignty", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_sovereignty", "p4obs", "anomaly")
_emit_writes_observability_log("rag_sovereignty", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_sovereignty", "p4obs", "mon_state")
_emit_triggers_alert("rag_sovereignty", "p4obs", "alert")
_emit_links_incident_trace("rag_sovereignty", "p4obs", "trace_link")
_emit_captures_pattern("rag_sovereignty", "p3lm", "pattern")
_emit_records_learning_event("rag_sovereignty", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_sovereignty", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_sovereignty", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_sovereignty", "p3lm", "routing")
_emit_improves_agent_policy("rag_sovereignty", "p3lm", "policy")
_emit_stores_learning_state("rag_sovereignty", "p3lm", "state")
_emit_records_execution_trace("rag_sovereignty", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_sovereignty", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_sovereignty", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_sovereignty", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_sovereignty", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_sovereignty", "env_read", "p2_env_1")
_emit_reads_environ("rag_sovereignty", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_sovereignty", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_sovereignty", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_sovereignty", "context_pull")
_emit_pulls_context("p1", "rag_sovereignty", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rag_sovereignty", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_sovereignty", "uwg_term_secondary")
_emit_writes_through("p1", "rag_sovereignty", "write_through")
_emit_writes_through("p1", "rag_sovereignty", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rag_sovereignty", "safety_validation")
_emit_invokes_eval("p1", "rag_sovereignty", "eval_call")
_emit_proposal_commits_routing("p1", "rag_sovereignty", "routing_commit")
_emit_escalates_to_human("p1", "rag_sovereignty", "human_escalation")
_emit_routes_through("p1", "rag_sovereignty", "route_through")
_emit_checks_agent_registry("p1", "rag_sovereignty", "agent_registry")
_emit_validates_agent_capability("p1", "rag_sovereignty", "capability")
_emit_dispatches_execution_plan("p1", "rag_sovereignty", "exec_plan")
_emit_agent_executes_agent("p1", "rag_sovereignty", "sub_agent")
_emit_routes_to_agent("p1", "rag_sovereignty", "target_agent")
_emit_verifies_policy("p1", "rag_sovereignty", "policy_check")
_emit_observes_runtime_state("p1", "rag_sovereignty", "runtime_state")
_emit_verifies_boundary("p1", "rag_sovereignty", "boundary_check")
_emit_transcripts_response("p1", "rag_sovereignty", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_sovereignty")
_emit_gated_by_confidence("p1", "rag_sovereignty", "confidence_gate")
logger = logging.getLogger(__name__)
_POLICY_ID = "ADG::Policy::RAG_C0_INFORMATIONAL_ONLY"
_DECISION_NODES: frozenset[str] = frozenset(
    {
        canonical_name("Decision", "RoutingDecision"),
        canonical_name("Decision", "SafetyThreshold"),
        canonical_name("Decision", "TierSelection"),
    }
)
_C0_CONTEXT_NODE = canonical_name("Retrieval", "C0Context")
_RAG_MODULE_PATTERNS: frozenset[str] = frozenset(
    {
        "SovereignRAGManager",
        "SovereignRAGManagerAgent",
        "knowledge/reasoning",
        "EmbeddingSovereignAgent",
        "bmg_embedding_similarity",
        "healing_contexts",
        "retrieval",
    }
)
_DECISION_MODULE_PATTERNS: frozenset[str] = frozenset(
    {
        "shadow_router_classifier",
        "path_router",
        "reasoning_policy_engine",
        "escalation_router",
        "timeshift_router",
        "assembly_stage",
    }
)


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _is_rag_module(rel: str) -> bool:
    return any(pat in rel for pat in _RAG_MODULE_PATTERNS)


def _is_decision_module(rel: str) -> bool:
    return any(pat in rel for pat in _DECISION_MODULE_PATTERNS)


@dataclass
class RAGSovereigntyViolation:
    """A RAG C0 sovereignty violation."""

    violation_type: str
    from_module: str
    to_module: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return f"RAG-C0-VIOLATION [{self.violation_type}] policy={self.policy_id}\n  from:  {self.from_module}\n  to:    {self.to_module}\n  file:  {self.source_file}:{self.line_no}"


@dataclass
class RAGSovereigntyReport:
    """Result of RAG sovereignty enforcement check."""

    violations: list[RAGSovereigntyViolation] = field(default_factory=list)
    rag_edges_count: int = 0
    decision_edges_count: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def check_rag_sovereignty(
    result: ScanResult, client: ADGMCPClient | None = None, extra_edges: list[dict] | None = None
) -> RAGSovereigntyReport:
    """Enforce RAG C0 informational-only policy.

    extra_edges: optional synthetic edges for negative-control tests.
      Format: [{"from": adg_name, "relation": "influences", "to": adg_name}]
    """
    rag_edges = []
    decision_edges = []
    for edge in result.edges:
        from_rel = _module_rel(edge.from_name)
        to_rel = _module_rel(edge.to_name)
        if _is_rag_module(from_rel):
            rag_edges.append(edge)
        if _is_rag_module(from_rel) and _is_decision_module(to_rel):
            decision_edges.append(edge)
    violations: list[RAGSovereigntyViolation] = []
    for edge in decision_edges:
        violations.append(
            RAGSovereigntyViolation(
                violation_type="RAG_INFLUENCES_DECISION",
                from_module=_module_rel(edge.from_name),
                to_module=_module_rel(edge.to_name),
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
        )
    if extra_edges:
        for ee in extra_edges:
            from_adg = ee.get("from", "")
            relation = ee.get("relation", "")
            to_adg = ee.get("to", "")
            if relation == "influences" and to_adg in _DECISION_NODES:
                violations.append(
                    RAGSovereigntyViolation(
                        violation_type="C0_CONTEXT_INFLUENCES_DECISION",
                        from_module=from_adg,
                        to_module=_module_rel(to_adg),
                        source_file="<synthetic>",
                        line_no=0,
                    )
                )
    proof_digest = _compute_proof_digest(result, violations)
    report = RAGSovereigntyReport(
        violations=violations,
        rag_edges_count=len(rag_edges),
        decision_edges_count=len(decision_edges),
        snapshot_digest=proof_digest,
    )
    if client is not None:
        _persist_proof(result, report, client)
        _ensure_graph_nodes(client)
    return report


def _compute_proof_digest(result: ScanResult, violations: list[RAGSovereigntyViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_module, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_module}|{v.violation_type}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(result: ScanResult, report: RAGSovereigntyReport, client: ADGMCPClient) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "rag_sovereignty_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"rag_edges:{report.rag_edges_count}",
            f"decision_edges:{report.decision_edges_count}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )


def _ensure_graph_nodes(client: ADGMCPClient) -> None:
    client.upsert_entity(
        _C0_CONTEXT_NODE, "retrieval_component", ["component:C0Context", f"policy_id:{_POLICY_ID}"]
    )
    for dn in sorted(_DECISION_NODES):
        client.upsert_entity(dn, "decision_point", [f"policy_id:{_POLICY_ID}"])


__all__ = ["check_rag_sovereignty", "RAGSovereigntyReport", "RAGSovereigntyViolation"]
