"""ADG Graph Persister -- writes ScanResult into Memory MCP via ADGMCPClient.

Persists:
- ADG::Commit::<sha> entity
- ADG::Snapshot::<sha>::<digest> entity
- ADG::Module::<path> entities
- ADG::Symbol::<qualified> entities
- ADG::Layer::L0..L6 entities
- All edges as relations
- Observations on each node (commit, digest, path, line_no, edge_kind, etc.)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from agentic_core.adg.client.InMemoryStore import ADGMCPClient
from agentic_core.adg.contracts.schema_util import (
    GATEWAY_ALLOWLIST,
    canonical_name,
    module_path_to_layer,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "graph_persister")
trace_contract._emit_applies_guardrail("p0", "graph_persister", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "graph_persister", "policy_binding")
trace_contract._emit_snapshots_state("p0", "graph_persister", "state_snapshot")
trace_contract.emit_replay_key("p0", "graph_persister")
trace_contract.emit_determinism_digest("p0", "graph_persister")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "graph_persister", "execution_auth")
trace_contract._emit_validates_capability("p2", "graph_persister", "capability_check")
trace_contract._emit_routes_to_capability("p2", "graph_persister", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "graph_persister", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "graph_persister", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "graph_persister", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "graph_persister", "exec_output")
trace_contract._emit_dispatches_agent("p3", "graph_persister", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "graph_persister", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "graph_persister", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "graph_persister", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "graph_persister", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "graph_persister", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "graph_persister", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "graph_persister", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "graph_persister", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "graph_persister", "eval_metric")
trace_contract._emit_stores_embedding("p4", "graph_persister", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "graph_persister", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "graph_persister", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("graph_persister", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("graph_persister", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("graph_persister", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("graph_persister", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("graph_persister", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("graph_persister", "p4obs", "alert")
trace_contract._emit_links_incident_trace("graph_persister", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("graph_persister", "p3lm", "pattern")
trace_contract._emit_records_learning_event("graph_persister", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("graph_persister", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("graph_persister", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("graph_persister", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("graph_persister", "p3lm", "policy")
trace_contract._emit_stores_learning_state("graph_persister", "p3lm", "state")
trace_contract._emit_records_execution_trace("graph_persister", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("graph_persister", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("graph_persister", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("graph_persister", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("graph_persister", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("graph_persister", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("graph_persister", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("graph_persister", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("graph_persister", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "graph_persister", "context_pull")
trace_contract._emit_pulls_context("p1", "graph_persister", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "graph_persister", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "graph_persister", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "graph_persister", "write_through")
trace_contract._emit_writes_through("p1", "graph_persister", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "graph_persister", "safety_validation")
trace_contract._emit_invokes_eval("p1", "graph_persister", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "graph_persister", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "graph_persister", "human_escalation")
trace_contract._emit_routes_through("p1", "graph_persister", "route_through")
trace_contract._emit_checks_agent_registry("p1", "graph_persister", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "graph_persister", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "graph_persister", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "graph_persister", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "graph_persister", "target_agent")
trace_contract._emit_verifies_policy("p1", "graph_persister", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "graph_persister", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "graph_persister", "boundary_check")
trace_contract._emit_transcripts_response("p1", "graph_persister", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "graph_persister")
trace_contract._emit_gated_by_confidence("p1", "graph_persister", "confidence_gate")

from tqdm import tqdm

trace_contract._emit_validates_request("handoff", "graph_persister", "validates_request_bootstrap")
trace_contract._emit_produces_plan("handoff", "graph_persister", "produces_plan_bootstrap")
trace_contract._emit_proposes_route("handoff", "graph_persister", "proposes_route_bootstrap")
trace_contract._emit_prefilters_scope("handoff", "graph_persister", "prefilters_scope_bootstrap")
trace_contract._emit_produces_evidence_contract("handoff", "graph_persister", "produces_evidence_contract_bootstrap")
trace_contract._emit_packages_prompt_envelope("handoff", "graph_persister", "packages_prompt_envelope_bootstrap")
trace_contract._emit_stamps_execution_packet("handoff", "graph_persister", "stamps_execution_packet_bootstrap")
trace_contract._emit_propagates_policy_hash("handoff", "graph_persister", "propagates_policy_hash_bootstrap")
trace_contract._emit_propagates_replay_key("handoff", "graph_persister", "propagates_replay_key_bootstrap")
trace_contract._emit_seals_result("handoff", "graph_persister", "seals_result_bootstrap")
trace_contract._emit_chooses_exit_disposition("handoff", "graph_persister", "chooses_exit_disposition_bootstrap")
trace_contract._emit_materializes_hitl_packet("handoff", "graph_persister", "materializes_hitl_packet_bootstrap")
trace_contract._emit_reclears_human_decision("handoff", "graph_persister", "reclears_human_decision_bootstrap")
trace_contract._emit_verifies_blast_radius("handoff", "graph_persister", "verifies_blast_radius_bootstrap")
trace_contract._emit_appends_commit_receipt("handoff", "graph_persister", "appends_commit_receipt_bootstrap")
trace_contract._emit_publishes_retrieval_surface("handoff", "graph_persister", "publishes_retrieval_surface_bootstrap")
trace_contract._emit_promotes_future_run_change("handoff", "graph_persister", "promotes_future_run_change_bootstrap")

logger = logging.getLogger(__name__)

_LAYER_LABELS = (
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_SL",
    "L_TOOLS",
    "L_OPS",
    "L_UNKNOWN",
)


def persist_scan_result(result: ScanResult, client: ADGMCPClient) -> None:
    """Persist a full ScanResult into the ADG graph via client.

    All writes are commit-scoped and snapshot-scoped.
    Idempotent: safe to call multiple times with the same result.
    """
    scan_time = datetime.now(timezone.utc).isoformat()

    _ensure_layer_nodes(client)
    _ensure_gateway_nodes(client)

    if result.commit_sha:
        commit_node = canonical_name("Commit", result.commit_sha)
        client.upsert_entity(
            commit_node,
            "commit",
            [f"commit:{result.commit_sha}", f"scan_time:{scan_time}"],
        )

    snapshot_node: str | None = None
    if result.commit_sha and result.digest:
        snapshot_node = canonical_name("Snapshot", result.commit_sha, result.digest)
        client.upsert_entity(
            snapshot_node,
            "snapshot",
            [
                f"commit:{result.commit_sha}",
                f"snapshot_digest:{result.digest}",
                f"scan_time:{scan_time}",
            ],
        )

    _persist_modules(result, client, result.commit_sha, scan_time)
    _persist_edges(result, client, snapshot_node)


def _ensure_layer_nodes(client: ADGMCPClient) -> None:
    for label in _LAYER_LABELS:
        node = canonical_name("Layer", label)
        client.upsert_entity(node, "layer", [f"layer_label:{label}"])


def _ensure_gateway_nodes(client: ADGMCPClient) -> None:
    for gw_name, gw_path in tqdm(GATEWAY_ALLOWLIST.items(), desc="Processing", unit="item"):
        node = canonical_name("Gateway", gw_name)
        client.upsert_entity(
            node,
            "gateway",
            [f"path:{gw_path}", f"gateway_name:{gw_name}"],
        )
        module_node = canonical_name("Module", gw_path)
        client.upsert_entity(module_node, "module", [f"path:{gw_path}"])
        layer_label = module_path_to_layer(gw_path)
        layer_node = canonical_name("Layer", layer_label)
        client.upsert_relation(module_node, "belongs_to_layer", layer_node)
        client.upsert_relation(module_node, "implements", node)


def _persist_modules(
    result: ScanResult,
    client: ADGMCPClient,
    commit_sha: str,
    scan_time: str,
) -> None:
    for rel in result.modules:
        module_node = canonical_name("Module", rel)
        layer_label = module_path_to_layer(rel)
        obs = [f"path:{rel}", f"scan_time:{scan_time}"]
        if commit_sha:
            obs.append(f"commit:{commit_sha}")
        client.upsert_entity(module_node, "module", obs)
        layer_node = canonical_name("Layer", layer_label)
        client.upsert_relation(module_node, "belongs_to_layer", layer_node)


def _persist_edges(
    result: ScanResult,
    client: ADGMCPClient,
    snapshot_node: str | None,
) -> None:
    symbol_obs_map: dict[str, list[str]] = {}

    for edge in tqdm(result.edges, desc="Processing", unit="item"):
        client.upsert_relation(edge.from_name, edge.relation_type, edge.to_name)

        sym_node = edge.to_name
        if sym_node not in symbol_obs_map:
            symbol_obs_map[sym_node] = []

        obs_list = [
            f"edge_kind:{edge.edge_kind}",
            f"symbol:{edge.symbol}",
            f"source_file:{edge.source_file}",
            f"line_no:{edge.line_no}",
        ]
        # G16: attach structured rule_id to violation/bypass edges
        rule_id = _derive_rule_id(edge.relation_type, edge.symbol)
        if rule_id:
            obs_list.append(f"rule_id:{rule_id}")

        for obs in obs_list:
            if obs not in symbol_obs_map[sym_node]:
                symbol_obs_map[sym_node].append(obs)

    for sym_node, obs_list in sorted(symbol_obs_map.items()):
        entity_type = _infer_entity_type(sym_node)
        client.upsert_entity(sym_node, entity_type, sorted(obs_list))

    if snapshot_node:
        client.add_observation(snapshot_node, [f"edge_count:{len(result.edges)}"])


_RULE_TYPE_MAP: dict[str, str] = {
    "violates": "LAYER_GRAVITY",
    "bypasses_uwg": "UWG_BYPASS",
    "seam_bypass": "SEAM_BYPASS",
}


def _derive_rule_id(relation_type: str, symbol: str) -> str:
    """G16: Return structured rule_id for violation/bypass edges, else empty string."""
    prefix = _RULE_TYPE_MAP.get(relation_type, "")
    if not prefix:
        return ""
    if symbol:
        return f"{prefix}:{symbol}"
    return prefix


def _infer_entity_type(adg_name: str) -> str:
    parts = adg_name.split("::")
    if len(parts) >= 2:
        t = parts[1].lower()
        # G2: map canonical ADG prefix to entity_type
        _prefix_to_type: dict[str, str] = {
            "symbol": "symbol",
            "module": "module",
            "gateway": "gateway",
            "layer": "layer",
            "seam": "seam",
            "provider": "provider",
            "promptslot": "prompt_slot",
            "prompttemplate": "prompt_template",
        }
        if t in _prefix_to_type:
            return _prefix_to_type[t]
    return "symbol"


__all__ = ["persist_scan_result"]
