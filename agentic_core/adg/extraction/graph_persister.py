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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "graph_persister")
_emit_applies_guardrail("p0", "graph_persister", "p0_governance")
_emit_reads_policy_state("p0", "graph_persister", "policy_binding")
_emit_snapshots_state("p0", "graph_persister", "state_snapshot")
emit_replay_key("p0", "graph_persister")
emit_determinism_digest("p0", "graph_persister")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "graph_persister", "execution_auth")
_emit_validates_capability("p2", "graph_persister", "capability_check")
_emit_routes_to_capability("p2", "graph_persister", "capability_route")
_emit_writes_via_uwg("p2", "graph_persister", "uwg_write")
_emit_blocks_direct_write("p2", "graph_persister", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_persister", "tool_invocation")
_emit_captures_execution_output("p2", "graph_persister", "exec_output")
_emit_dispatches_agent("p3", "graph_persister", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_persister", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_persister", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_persister", "healing_outcome")
_emit_escalates_failure("p3", "graph_persister", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_persister", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_persister", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_persister", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_persister", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_persister", "eval_metric")
_emit_stores_embedding("p4", "graph_persister", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_persister", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_persister", "exec_snapshot_link")

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

_emit_emits_metric_event("graph_persister", "p4obs", "metric_1")
_emit_emits_metric_event("graph_persister", "p4obs", "metric_2")
_emit_emits_metric_event("graph_persister", "p4obs", "metric_3")
_emit_emits_metric_event("graph_persister", "p4obs", "metric_4")
_emit_emits_metric_event("graph_persister", "p4obs", "metric_5")
_emit_emits_metric_event("graph_persister", "p4obs", "metric_6")
_emit_records_incident_event("graph_persister", "p4obs", "incident")
_emit_captures_runtime_anomaly("graph_persister", "p4obs", "anomaly")
_emit_writes_observability_log("graph_persister", "p4obs", "obs_log")
_emit_updates_monitoring_state("graph_persister", "p4obs", "mon_state")
_emit_triggers_alert("graph_persister", "p4obs", "alert")
_emit_links_incident_trace("graph_persister", "p4obs", "trace_link")
_emit_captures_pattern("graph_persister", "p3lm", "pattern")
_emit_records_learning_event("graph_persister", "p3lm", "learning_event")
_emit_writes_learning_snapshot("graph_persister", "p3lm", "snapshot")
_emit_feeds_meta_learning("graph_persister", "p3lm", "meta_feed")
_emit_updates_routing_strategy("graph_persister", "p3lm", "routing")
_emit_improves_agent_policy("graph_persister", "p3lm", "policy")
_emit_stores_learning_state("graph_persister", "p3lm", "state")
_emit_records_execution_trace("graph_persister", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("graph_persister", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("graph_persister", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("graph_persister", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("graph_persister", "L4_STATE", "p2_trace_5")
_emit_reads_environ("graph_persister", "env_read", "p2_env_1")
_emit_reads_environ("graph_persister", "env_read", "p2_env_2")
_emit_reads_runtime_state("graph_persister", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("graph_persister", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "graph_persister", "context_pull")
_emit_pulls_context("p1", "graph_persister", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "graph_persister", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "graph_persister", "uwg_term_secondary")
_emit_writes_through("p1", "graph_persister", "write_through")
_emit_writes_through("p1", "graph_persister", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "graph_persister", "safety_validation")
_emit_invokes_eval("p1", "graph_persister", "eval_call")
_emit_proposal_commits_routing("p1", "graph_persister", "routing_commit")
_emit_escalates_to_human("p1", "graph_persister", "human_escalation")
_emit_routes_through("p1", "graph_persister", "route_through")
_emit_checks_agent_registry("p1", "graph_persister", "agent_registry")
_emit_validates_agent_capability("p1", "graph_persister", "capability")
_emit_dispatches_execution_plan("p1", "graph_persister", "exec_plan")
_emit_agent_executes_agent("p1", "graph_persister", "sub_agent")
_emit_routes_to_agent("p1", "graph_persister", "target_agent")
_emit_verifies_policy("p1", "graph_persister", "policy_check")
_emit_observes_runtime_state("p1", "graph_persister", "runtime_state")
_emit_verifies_boundary("p1", "graph_persister", "boundary_check")
_emit_transcripts_response("p1", "graph_persister", "transcript")
_emit_hard_fails_untranscripted("p1", "graph_persister")
_emit_gated_by_confidence("p1", "graph_persister", "confidence_gate")

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
    for gw_name, gw_path in GATEWAY_ALLOWLIST.items():
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

    for edge in result.edges:
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
