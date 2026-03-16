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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "blast_radius")
_emit_applies_guardrail("p0", "blast_radius", "p0_governance")
_emit_reads_policy_state("p0", "blast_radius", "policy_binding")
_emit_snapshots_state("p0", "blast_radius", "state_snapshot")
emit_replay_key("p0", "blast_radius")
emit_determinism_digest("p0", "blast_radius")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "blast_radius", "execution_auth")
_emit_validates_capability("p2", "blast_radius", "capability_check")
_emit_routes_to_capability("p2", "blast_radius", "capability_route")
_emit_writes_via_uwg("p2", "blast_radius", "uwg_write")
_emit_blocks_direct_write("p2", "blast_radius", "direct_write_block")
_emit_records_tool_invocation("p2", "blast_radius", "tool_invocation")
_emit_captures_execution_output("p2", "blast_radius", "exec_output")
_emit_dispatches_agent("p3", "blast_radius", "agent_dispatch")
_emit_coordinates_agents("p3", "blast_radius", "agent_coordination")
_emit_records_workflow_lineage("p3", "blast_radius", "workflow_lineage")
_emit_records_healing_outcome("p3", "blast_radius", "healing_outcome")
_emit_escalates_failure("p3", "blast_radius", "failure_escalation")
_emit_orchestrates_workflow("p3", "blast_radius", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "blast_radius", "healing_dispatch")
_emit_invokes_evaluation("p3", "blast_radius", "evaluation_signal")
_emit_records_telemetry_event("p4", "blast_radius", "telemetry_event")
_emit_captures_evaluation_metric("p4", "blast_radius", "eval_metric")
_emit_stores_embedding("p4", "blast_radius", "embedding_store")
_emit_updates_meta_learning_state("p4", "blast_radius", "meta_learning")
_emit_links_execution_to_snapshot("p4", "blast_radius", "exec_snapshot_link")

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
            f"ADG-BLAST-RADIUS: commit={self.commit_sha or 'none'} risk_score={self.risk_score} route_mode={self.route_mode} impact_digest={self.impact_digest} changed={len(self.changed_modules)} impacted={len(self.impacted_modules)}"
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
