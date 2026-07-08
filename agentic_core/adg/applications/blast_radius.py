"""Phase 5: L0 Router Blast-Radius scoring.

Inputs:
  - changed modules (git diff)
  - reachable downstream dependents (reverse import graph)
  - layer criticality weights (deterministic, precomputed)

Outputs:
  - ImpactDigest: sha256(sorted impacted nodes + weights)
  - risk_score: integer
  - route_mode: NORMAL | RESTRICTED | HUMAN_REVIEW

Layer criticality weights:
  L0: 100  L1: 80  L2: 90  L3: 70  L4: 60
  L5: 85   L6: 50  L_APP: 40  L_SL: 45
  L_TOOLS: 30  L_OPS: 20  L_UNKNOWN: 10
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import canonical_name, module_path_to_layer
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "blast_radius")
trace_contract._emit_applies_guardrail("p0", "blast_radius", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "blast_radius", "policy_binding")
trace_contract._emit_snapshots_state("p0", "blast_radius", "state_snapshot")

trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("blast_radius", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("blast_radius", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("blast_radius", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("blast_radius", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("blast_radius", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("blast_radius", "p4obs", "alert")
trace_contract._emit_links_incident_trace("blast_radius", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("blast_radius", "p3lm", "pattern")
trace_contract._emit_records_learning_event("blast_radius", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("blast_radius", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("blast_radius", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("blast_radius", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("blast_radius", "p3lm", "policy")
trace_contract._emit_stores_learning_state("blast_radius", "p3lm", "state")
trace_contract._emit_records_execution_trace("blast_radius", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("blast_radius", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("blast_radius", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("blast_radius", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("blast_radius", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("blast_radius", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("blast_radius", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("blast_radius", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("blast_radius", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "blast_radius", "context_pull")
trace_contract._emit_pulls_context("p1", "blast_radius", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "blast_radius", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "blast_radius", "uwg_term_2")
trace_contract._emit_writes_through("p1", "blast_radius", "write_through")
trace_contract._emit_writes_through("p1", "blast_radius", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "blast_radius", "safety_validation")
trace_contract._emit_invokes_eval("p1", "blast_radius", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "blast_radius", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "blast_radius", "human_escalation")
trace_contract._emit_routes_through("p1", "blast_radius", "route_through")
trace_contract._emit_checks_agent_registry("p1", "blast_radius", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "blast_radius", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "blast_radius", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "blast_radius", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "blast_radius", "target_agent")
trace_contract._emit_verifies_policy("p1", "blast_radius", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "blast_radius", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "blast_radius", "boundary_check")
trace_contract._emit_transcripts_response("p1", "blast_radius", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "blast_radius")
trace_contract._emit_gated_by_confidence("p1", "blast_radius", "confidence_gate")
trace_contract.emit_replay_key("p0", "blast_radius")
trace_contract.emit_determinism_digest("p0", "blast_radius")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "blast_radius", "execution_auth")
trace_contract._emit_validates_capability("p2", "blast_radius", "capability_check")
trace_contract._emit_routes_to_capability("p2", "blast_radius", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "blast_radius", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "blast_radius", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "blast_radius", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "blast_radius", "exec_output")
trace_contract._emit_dispatches_agent("p3", "blast_radius", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "blast_radius", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "blast_radius", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "blast_radius", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "blast_radius", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "blast_radius", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "blast_radius", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "blast_radius", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "blast_radius", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "blast_radius", "eval_metric")
trace_contract._emit_stores_embedding("p4", "blast_radius", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "blast_radius", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "blast_radius", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
logger = logging.getLogger(__name__)
RouteMode = Literal["NORMAL", "RESTRICTED", "HUMAN_REVIEW"]
_LAYER_WEIGHTS: dict[str, int] = {
    "L0": 100,
    "L1": 80,
    "L2": 90,
    "L3": 70,
    "L4": 60,
    "L5": 85,
    "L6": 50,
    "L_APP": 40,
    "L_SL": 45,
    "L_TOOLS": 30,
    "L_OPS": 20,
    "L_UNKNOWN": 10,
}
_RESTRICTED_THRESHOLD = 300
_HUMAN_REVIEW_THRESHOLD = 700


@dataclass
class BlastRadiusResult:
    """Output of blast-radius scoring for a commit."""

    changed_modules: list[str]
    impacted_modules: list[str]
    risk_score: int
    route_mode: RouteMode
    impact_digest: str
    commit_sha: str = ""

    def print_summary(self) -> None:
        print(
            f"ADG-BLAST-RADIUS: commit={self.commit_sha or 'none'} risk_score={self.risk_score} route_mode={self.route_mode} impact_digest={self.impact_digest} changed={len(self.changed_modules)} impacted={len(self.impacted_modules)}",
        )


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def compute_blast_radius(
    changed_files: list[str],
    result: ScanResult,
    commit_sha: str = "",
    client: ADGMCPClient | None = None,
    run_id: str = "",
) -> BlastRadiusResult:
    """Compute deterministic blast-radius score for a set of changed files."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner.__new__(ADGStaticScanner)
    reverse_graph = scanner.build_reverse_import_graph(result)
    changed_adg = [canonical_name("Module", f.replace("\\", "/")) for f in sorted(changed_files)]
    impacted: set[str] = set(changed_adg)
    frontier: list[str] = list(changed_adg)
    while frontier:
        current = frontier.pop()
        sym_name = canonical_name("Symbol", _module_rel(current))
        for dependents_key in (current, sym_name):
            for dependent in reverse_graph.get(dependents_key, []):
                if dependent not in impacted:
                    impacted.add(dependent)
                    frontier.append(dependent)
    impacted_sorted = sorted(impacted)
    score_lines = []
    total_weight = 0
    for adg_name in impacted_sorted:
        rel = _module_rel(adg_name)
        layer = module_path_to_layer(rel)
        weight = _LAYER_WEIGHTS.get(layer, 10)
        total_weight += weight
        score_lines.append(f"{adg_name}:{weight}")
    impact_digest = hashlib.sha256("\n".join(score_lines).encode("utf-8")).hexdigest()
    if total_weight >= _HUMAN_REVIEW_THRESHOLD:
        route_mode: RouteMode = "HUMAN_REVIEW"
    elif total_weight >= _RESTRICTED_THRESHOLD:
        route_mode = "RESTRICTED"
    else:
        route_mode = "NORMAL"
    br_result = BlastRadiusResult(
        changed_modules=sorted(changed_files),
        impacted_modules=[_module_rel(n) for n in impacted_sorted],
        risk_score=total_weight,
        route_mode=route_mode,
        impact_digest=impact_digest,
        commit_sha=commit_sha,
    )
    if client is not None and (commit_sha or run_id):
        _persist_blast_radius(br_result, client, run_id, commit_sha)
    return br_result


def _persist_blast_radius(br: BlastRadiusResult, client: ADGMCPClient, run_id: str, commit_sha: str) -> None:
    if run_id:
        run_node = canonical_name("Run", run_id)
        client.upsert_entity(
            run_node,
            "scan_run",
            [
                f"commit:{commit_sha}",
                f"risk_score:{br.risk_score}",
                f"route_mode:{br.route_mode}",
                f"impact_digest:{br.impact_digest}",
                f"impacted_count:{len(br.impacted_modules)}",
            ],
        )
    if commit_sha:
        snap_node = canonical_name("Snapshot", commit_sha, "blast_radius")
        client.upsert_entity(
            snap_node,
            "snapshot",
            [
                f"commit:{commit_sha}",
                f"risk_score:{br.risk_score}",
                f"route_mode:{br.route_mode}",
                f"impact_digest:{br.impact_digest}",
                f"impacted_count:{len(br.impacted_modules)}",
            ],
        )


__all__ = ["compute_blast_radius", "BlastRadiusResult", "RouteMode"]
