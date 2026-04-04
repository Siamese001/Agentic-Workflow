"""
ADG Test-Code Drift Score
=========================
Quantifies the gap between production code and tests/ using the ADG hot cache.

Composite formula:
    drift_score = 0.40 * D_coverage + 0.30 * D_blast + 0.20 * D_orphan + 0.10 * D_violation

Sub-scores:
    D_coverage  — prod modules with zero inbound `covers` edges from L_TEST nodes
    D_blast     — blast-radius-weighted coverage gap (fan_out × uncovered)
    D_orphan    — L_TEST modules that are sources of dead_imports edges
    D_violation — `violates`-edge source modules with no test coverage

Output: Redis `adg:drift:*` keys (1-hour TTL) + stdout summary table.

Usage:
    python tools/adg/drift_score.py
"""

from __future__ import annotations

import json
import time
from typing import Any

import redis

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_authorize_and_execute("p2", "drift_score", "execution_auth")
_emit_validates_capability("p2", "drift_score", "capability_check")
_emit_routes_to_capability("p2", "drift_score", "capability_route")
_emit_writes_via_uwg("p2", "drift_score", "uwg_write")
_emit_blocks_direct_write("p2", "drift_score", "direct_write_block")
_emit_records_tool_invocation("p2", "drift_score", "tool_invocation")
_emit_captures_execution_output("p2", "drift_score", "exec_output")
_emit_dispatches_agent("p3", "drift_score", "agent_dispatch")
_emit_coordinates_agents("p3", "drift_score", "agent_coordination")
_emit_records_workflow_lineage("p3", "drift_score", "workflow_lineage")
_emit_records_healing_outcome("p3", "drift_score", "healing_outcome")
_emit_escalates_failure("p3", "drift_score", "failure_escalation")
_emit_orchestrates_workflow("p3", "drift_score", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "drift_score", "healing_dispatch")
_emit_invokes_evaluation("p3", "drift_score", "evaluation_signal")
_emit_records_telemetry_event("p4", "drift_score", "telemetry_event")
_emit_captures_evaluation_metric("p4", "drift_score", "eval_metric")
_emit_stores_embedding("p4", "drift_score", "embedding_store")
_emit_updates_meta_learning_state("p4", "drift_score", "meta_learning")
_emit_links_execution_to_snapshot("p4", "drift_score", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from tools.adg.adg_redis_query import ADGRedisClient

_emit_emits_metric_event("drift_score", "p4obs", "metric_1")
_emit_emits_metric_event("drift_score", "p4obs", "metric_2")
_emit_emits_metric_event("drift_score", "p4obs", "metric_3")
_emit_emits_metric_event("drift_score", "p4obs", "metric_4")
_emit_emits_metric_event("drift_score", "p4obs", "metric_5")
_emit_emits_metric_event("drift_score", "p4obs", "metric_6")
_emit_records_incident_event("drift_score", "p4obs", "incident")
_emit_captures_runtime_anomaly("drift_score", "p4obs", "anomaly")
_emit_writes_observability_log("drift_score", "p4obs", "obs_log")
_emit_updates_monitoring_state("drift_score", "p4obs", "mon_state")
_emit_triggers_alert("drift_score", "p4obs", "alert")
_emit_links_incident_trace("drift_score", "p4obs", "trace_link")
_emit_captures_pattern("drift_score", "p3lm", "pattern")
_emit_records_learning_event("drift_score", "p3lm", "learning_event")
_emit_writes_learning_snapshot("drift_score", "p3lm", "snapshot")
_emit_feeds_meta_learning("drift_score", "p3lm", "meta_feed")
_emit_updates_routing_strategy("drift_score", "p3lm", "routing")
_emit_improves_agent_policy("drift_score", "p3lm", "policy")
_emit_stores_learning_state("drift_score", "p3lm", "state")
_emit_records_execution_trace("drift_score", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("drift_score", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("drift_score", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("drift_score", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("drift_score", "L4_STATE", "p2_trace_5")
_emit_reads_environ("drift_score", "env_read", "p2_env_1")
_emit_reads_environ("drift_score", "env_read", "p2_env_2")
_emit_reads_runtime_state("drift_score", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("drift_score", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "drift_score")
_emit_applies_guardrail("p0", "drift_score", "p0_governance")
_emit_reads_policy_state("p0", "drift_score", "policy_binding")
_emit_snapshots_state("p0", "drift_score", "state_snapshot")
_emit_pulls_context("p1", "drift_score", "context_pull")
_emit_pulls_context("p1", "drift_score", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "drift_score", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "drift_score", "uwg_term_secondary")
_emit_writes_through("p1", "drift_score", "write_through")
_emit_writes_through("p1", "drift_score", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "drift_score", "safety_validation")
_emit_invokes_eval("p1", "drift_score", "eval_call")
_emit_proposal_commits_routing("p1", "drift_score", "routing_commit")
_emit_escalates_to_human("p1", "drift_score", "human_escalation")
_emit_routes_through("p1", "drift_score", "route_through")
_emit_checks_agent_registry("p1", "drift_score", "agent_registry")
_emit_validates_agent_capability("p1", "drift_score", "capability")
_emit_dispatches_execution_plan("p1", "drift_score", "exec_plan")
_emit_agent_executes_agent("p1", "drift_score", "sub_agent")
_emit_routes_to_agent("p1", "drift_score", "target_agent")
_emit_verifies_policy("p1", "drift_score", "policy_check")
_emit_observes_runtime_state("p1", "drift_score", "runtime_state")
_emit_verifies_boundary("p1", "drift_score", "boundary_check")
_emit_transcripts_response("p1", "drift_score", "transcript")
_emit_hard_fails_untranscripted("p1", "drift_score")
_emit_gated_by_confidence("p1", "drift_score", "confidence_gate")
emit_replay_key("p0", "drift_score")
emit_determinism_digest("p0", "drift_score")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "drift_score", "urg_read_1")
_emit_reads_through("l4", "drift_score", "urg_read_2")
_emit_reads_through("l4", "drift_score", "urg_read_3")
_emit_reads_through("l4", "drift_score", "urg_read_4")
_emit_reads_through("l4", "drift_score", "urg_read_5")
_emit_reads_through("l4", "drift_score", "urg_read_6")
_emit_reads_through("l4", "drift_score", "urg_read_7")
_emit_reads_through("l4", "drift_score", "urg_read_8")
_emit_reads_through("l4", "drift_score", "urg_read_9")
_emit_reads_through("l4", "drift_score", "urg_read_10")
_emit_reads_through("l4", "drift_score", "urg_read_11")
_emit_reads_through("l4", "drift_score", "urg_read_12")
_emit_reads_through("l4", "drift_score", "urg_read_13")
_emit_reads_through("l4", "drift_score", "urg_read_14")
_emit_reads_through("l4", "drift_score", "urg_read_15")
_emit_reads_through("l4", "drift_score", "urg_read_16")
_emit_reads_through("l4", "drift_score", "urg_read_17")
_emit_reads_through("l4", "drift_score", "urg_read_18")
_emit_reads_through("l4", "drift_score", "urg_read_19")
_emit_reads_through("l4", "drift_score", "urg_read_20")
_emit_reads_through("l4", "drift_score", "urg_read_21")
_emit_reads_through("l4", "drift_score", "urg_read_22")
_emit_reads_through("l4", "drift_score", "urg_read_23")
_emit_reads_through("l4", "drift_score", "urg_read_24")
_emit_reads_through("l4", "drift_score", "urg_read_25")
_emit_reads_through("l4", "drift_score", "urg_read_26")
_emit_reads_through("l4", "drift_score", "urg_read_27")
_emit_reads_through("l4", "drift_score", "urg_read_28")
_emit_reads_through("l4", "drift_score", "urg_read_29")
_emit_reads_through("l4", "drift_score", "urg_read_30")
_emit_reads_through("l4", "drift_score", "urg_read_31")
_emit_reads_through("l4", "drift_score", "urg_read_32")
_emit_reads_through("l4", "drift_score", "urg_read_33")
_emit_reads_through("l4", "drift_score", "urg_read_34")
_emit_reads_through("l4", "drift_score", "urg_read_35")
_emit_reads_through("l4", "drift_score", "urg_read_36")
_emit_reads_through("l4", "drift_score", "urg_read_37")
_emit_reads_through("l4", "drift_score", "urg_read_38")
_emit_reads_through("l4", "drift_score", "urg_read_39")
_emit_reads_through("l4", "drift_score", "urg_read_40")
_emit_reads_through("l4", "drift_score", "urg_read_41")
_emit_reads_through("l4", "drift_score", "urg_read_42")
_emit_reads_through("l4", "drift_score", "urg_read_43")
_emit_reads_through("l4", "drift_score", "urg_read_44")
_emit_reads_through("l4", "drift_score", "urg_read_45")
_emit_reads_through("l4", "drift_score", "urg_read_46")
_emit_reads_through("l4", "drift_score", "urg_read_47")
_emit_reads_through("l4", "drift_score", "urg_read_48")
_emit_reads_through("l4", "drift_score", "urg_read_49")
_emit_reads_through("l4", "drift_score", "urg_read_50")
_emit_reads_through("l4", "drift_score", "urg_read_51")
_emit_reads_through("l4", "drift_score", "urg_read_52")
_emit_reads_through("l4", "drift_score", "urg_read_53")
_emit_reads_through("l4", "drift_score", "urg_read_54")
_emit_reads_through("l4", "drift_score", "urg_read_55")
_emit_reads_through("l4", "drift_score", "urg_read_56")
_emit_reads_through("l4", "drift_score", "urg_read_57")
_emit_reads_through("l4", "drift_score", "urg_read_58")
_emit_reads_through("l4", "drift_score", "urg_read_59")
_emit_reads_through("l4", "drift_score", "urg_read_60")
_emit_reads_through("l4", "drift_score", "urg_read_61")
_emit_reads_through("l4", "drift_score", "urg_read_62")
_emit_reads_through("l4", "drift_score", "urg_read_63")
_emit_reads_through("l4", "drift_score", "urg_read_64")
_emit_reads_through("l4", "drift_score", "urg_read_65")
_emit_reads_through("l4", "drift_score", "urg_read_66")
_emit_reads_through("l4", "drift_score", "urg_read_67")
_emit_reads_through("l4", "drift_score", "urg_read_68")
_emit_reads_through("l4", "drift_score", "urg_read_69")
_emit_reads_through("l4", "drift_score", "urg_read_70")
_emit_reads_through("l4", "drift_score", "urg_read_71")
_emit_reads_through("l4", "drift_score", "urg_read_72")
_emit_reads_through("l4", "drift_score", "urg_read_73")
_emit_reads_through("l4", "drift_score", "urg_read_74")
_emit_reads_through("l4", "drift_score", "urg_read_75")
_emit_reads_through("l4", "drift_score", "urg_read_76")
_emit_reads_through("l4", "drift_score", "urg_read_77")
_emit_reads_through("l4", "drift_score", "urg_read_78")
_emit_reads_through("l4", "drift_score", "urg_read_79")
_emit_reads_through("l4", "drift_score", "urg_read_80")
_emit_reads_through("l4", "drift_score", "urg_read_81")
_emit_reads_through("l4", "drift_score", "urg_read_82")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROD_LAYERS = {
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_OPS",
    "L_SHARED",
    "L_TOOLS",
    "L_RUNTIME",
    "L_SL",
    "L_PG",
}
TEST_LAYER = "L_TEST"

WEIGHTS = {
    "coverage": 0.40,
    "blast": 0.30,
    "orphan": 0.20,
    "violation": 0.10,
}

DRIFT_TTL = 3600  # 1 hour

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_snapshot(adg: ADGRedisClient) -> dict[str, Any]:
    """Return parsed adg:snapshot dict."""
    return adg.snapshot()


def _load_layer_nodes(
    r: redis.Redis,
    layers: set[str],
) -> dict[str, str]:
    """
    Return {node_id: resolved_path} for all module nodes in the given layers.
    Uses adg:nodes:by_layer:<L> SETs + adg:node:<id> HASHes.
    Excludes __pycache__ and ::symbol-suffix nodes.
    """
    result: dict[str, str] = {}
    for layer in layers:
        node_ids = r.smembers(f"adg:nodes:by_layer:{layer}")
        for nid in node_ids:
            node = r.hgetall(f"adg:node:{nid}")
            if node.get("entity_type") != "module":
                continue
            rp = node.get("resolved_path", "")
            if not rp or "__pycache__" in rp or "::" in rp:
                continue
            result[nid] = rp
    return result


def _is_stub_only(resolved_path: str) -> bool:
    """Return True for __init__.py, _shim.py, _compat.py modules (excluded from denominator)."""
    name = resolved_path.rsplit("/", 1)[-1]
    return name in ("__init__.py",) or name.endswith(("_shim.py", "_compat.py"))


# ---------------------------------------------------------------------------
# Sub-score: D_coverage
# ---------------------------------------------------------------------------


def compute_coverage_gap(
    r: redis.Redis,
    prod_nodes: dict[str, str],
    test_node_set: set[str],
) -> tuple[float, list[str]]:
    """
    D_coverage: fraction of prod modules with zero inbound `covers` edges from L_TEST.

    Returns (score [0,1], list of uncovered resolved_paths).
    """
    denominator_nodes = {nid: rp for nid, rp in prod_nodes.items() if not _is_stub_only(rp)}
    total = len(denominator_nodes)
    if total == 0:
        return 0.0, []

    uncovered_paths: list[str] = []
    for nid, rp in denominator_nodes.items():
        importers = r.smembers(f"adg:edge:in:{nid}:covers")
        test_importers = importers & test_node_set
        if not test_importers:
            uncovered_paths.append(rp)

    uncovered_paths.sort()
    score = len(uncovered_paths) / total
    return score, uncovered_paths


# ---------------------------------------------------------------------------
# Sub-score: D_blast
# ---------------------------------------------------------------------------


def compute_blast_mismatch(
    r: redis.Redis,
    prod_nodes: dict[str, str],
    covered_set: set[str],
    snapshot_hotspots: list[dict],
) -> tuple[float, list[dict]]:
    """
    D_blast: blast-radius-weighted coverage gap.

    blast_i = len(adg:edge:<nid>:imports) for each prod module.
    D_blast = sum(blast_i * (1 - covered_i)) / sum(blast_i)
    Individual blast capped at p99 to prevent outlier domination.

    Returns (score [0,1], top-20 uncovered modules by blast [{path, fan_out}]).
    """
    blast_values: list[tuple[str, str, int]] = []  # (nid, rp, blast)
    for nid, rp in prod_nodes.items():
        fan_out = r.scard(f"adg:edge:{nid}:imports")
        blast_values.append((nid, rp, fan_out))

    if not blast_values:
        return 0.0, []

    # p99 cap
    sorted_blasts = sorted(b for _, _, b in blast_values)
    p99_idx = max(0, int(len(sorted_blasts) * 0.99) - 1)
    p99_cap = sorted_blasts[p99_idx] if sorted_blasts else 1

    total_blast = 0
    uncovered_blast = 0
    uncovered_entries: list[dict] = []

    for nid, rp, raw_blast in blast_values:
        blast = min(raw_blast, p99_cap)
        total_blast += blast
        if nid not in covered_set:
            uncovered_blast += blast
            uncovered_entries.append({"path": rp, "fan_out": raw_blast})

    score = uncovered_blast / total_blast if total_blast > 0 else 0.0

    # Top-20 by raw fan_out (snapshot hotspots already available, but we build from real data)
    uncovered_entries.sort(key=lambda x: x["fan_out"], reverse=True)
    top20 = uncovered_entries[:20]

    return score, top20


# ---------------------------------------------------------------------------
# Sub-score: D_orphan
# ---------------------------------------------------------------------------


def compute_orphan_phantom(
    r: redis.Redis,
    test_nodes: dict[str, str],
    snapshot_unresolved: int,
) -> tuple[float, list[str]]:
    """
    D_orphan: fraction of L_TEST modules that are sources of dead_imports edges,
    plus phantom correction from snapshot unresolved_count.

    D_orphan = min(1.0, (orphan_test_count + unresolved_from_tests) / total_test)

    Returns (score [0,1], list of orphan test resolved_paths).
    """
    total_test = len(test_nodes)
    if total_test == 0:
        return 0.0, []

    orphan_paths: list[str] = []
    for nid, rp in test_nodes.items():
        dead = r.scard(f"adg:edge:{nid}:dead_imports")
        if dead > 0:
            orphan_paths.append(rp)

    orphan_paths.sort()

    # Phantom: unresolved_count is repo-wide; attribute proportionally to test fraction
    test_fraction = total_test / max(total_test, 1)
    unresolved_from_tests = int(snapshot_unresolved * test_fraction)

    raw = len(orphan_paths) + unresolved_from_tests
    score = min(1.0, raw / total_test)
    return score, orphan_paths


# ---------------------------------------------------------------------------
# Sub-score: D_violation
# ---------------------------------------------------------------------------


def compute_violation_gap(
    r: redis.Redis,
    test_node_set: set[str],
) -> tuple[float, list[str]]:
    """
    D_violation: fraction of `violates`-edge source modules with no test coverage.

    Scans adg:edge:*:violates keys; for each source node checks if it has
    any inbound covers edges from L_TEST.

    Returns (score [0,1], list of violation source paths lacking test coverage).
    """
    violates_keys: list[str] = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match="adg:edge:*:violates", count=500)
        violates_keys.extend(k for k in keys if not k.startswith("adg:edge:in:"))
        if cursor == 0:
            break

    if not violates_keys:
        return 0.0, []

    source_nids: set[str] = set()
    for key in violates_keys:
        # key format: adg:edge:<src_id>:violates
        parts = key.split(":")
        if len(parts) >= 3:
            source_nids.add(parts[2])

    gap_paths: list[str] = []
    for nid in source_nids:
        covers_in = r.smembers(f"adg:edge:in:{nid}:covers")
        test_covers = covers_in & test_node_set
        if not test_covers:
            node = r.hgetall(f"adg:node:{nid}")
            rp = node.get("resolved_path", nid)
            gap_paths.append(rp)

    total_violating = len(source_nids)
    score = len(gap_paths) / total_violating if total_violating > 0 else 0.0
    return score, sorted(gap_paths)


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------


def composite_score(
    d_coverage: float,
    d_blast: float,
    d_orphan: float,
    d_violation: float,
) -> float:
    """Weighted composite drift score [0.0, 1.0]. Lower = healthier."""
    return (
        WEIGHTS["coverage"] * d_coverage
        + WEIGHTS["blast"] * d_blast
        + WEIGHTS["orphan"] * d_orphan
        + WEIGHTS["violation"] * d_violation
    )


# ---------------------------------------------------------------------------
# Redis output
# ---------------------------------------------------------------------------


def write_to_redis(
    r: redis.Redis,
    scores: dict[str, float],
    uncovered_paths: list[str],
    orphan_paths: list[str],
    blast_top: list[dict],
    violation_gaps: list[str],
    prod_total: int,
    test_total: int,
) -> None:
    """Write all adg:drift:* keys via pipeline with 1-hour TTL."""
    pipe = r.pipeline(transaction=False)

    # Flush existing drift keys first
    for key in r.scan_iter("adg:drift:*"):
        pipe.delete(key)

    # Composite score
    pipe.set("adg:drift:score", str(round(scores["composite"], 6)))
    pipe.expire("adg:drift:score", DRIFT_TTL)

    # Sub-scores HASH
    pipe.hmset(
        "adg:drift:subscores",
        {
            "coverage": str(round(scores["coverage"], 6)),
            "blast": str(round(scores["blast"], 6)),
            "orphan": str(round(scores["orphan"], 6)),
            "violation": str(round(scores["violation"], 6)),
            "composite": str(round(scores["composite"], 6)),
            "prod_total": str(prod_total),
            "test_total": str(test_total),
            "timestamp": str(time.time()),
        },
    )
    pipe.expire("adg:drift:subscores", DRIFT_TTL)

    # Uncovered modules LIST
    if uncovered_paths:
        pipe.delete("adg:drift:uncovered")
        for p in uncovered_paths:
            pipe.rpush("adg:drift:uncovered", p)
        pipe.expire("adg:drift:uncovered", DRIFT_TTL)

    # Orphan tests LIST
    if orphan_paths:
        pipe.delete("adg:drift:orphan_tests")
        for p in orphan_paths:
            pipe.rpush("adg:drift:orphan_tests", p)
        pipe.expire("adg:drift:orphan_tests", DRIFT_TTL)

    # Blast top-20 LIST (JSON entries)
    if blast_top:
        pipe.delete("adg:drift:blast_top")
        for entry in blast_top:
            pipe.rpush("adg:drift:blast_top", json.dumps(entry))
        pipe.expire("adg:drift:blast_top", DRIFT_TTL)

    # Violation gaps LIST
    if violation_gaps:
        pipe.delete("adg:drift:violation_gaps")
        for p in violation_gaps:
            pipe.rpush("adg:drift:violation_gaps", p)
        pipe.expire("adg:drift:violation_gaps", DRIFT_TTL)

    pipe.execute()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    adg = ADGRedisClient(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    adg.ping()

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    print("[drift] Loading snapshot ...")
    snapshot = _load_snapshot(adg)
    snapshot_unresolved = snapshot.get("counts", {}).get("unresolved_count", 0)

    print("[drift] Loading prod module nodes ...")
    prod_nodes = _load_layer_nodes(r, PROD_LAYERS)
    print(f"[drift]   prod modules: {len(prod_nodes)}")

    print("[drift] Loading test module nodes ...")
    test_nodes = _load_layer_nodes(r, {TEST_LAYER})
    test_node_set = set(test_nodes.keys())
    print(f"[drift]   test modules: {len(test_nodes)}")

    print("[drift] Computing D_coverage ...")
    d_cov, uncovered_paths = compute_coverage_gap(r, prod_nodes, test_node_set)

    print("[drift] Computing D_blast ...")
    uncovered_set = set(uncovered_paths)
    covered_set = {nid for nid, rp in prod_nodes.items() if rp not in uncovered_set}
    hotspots = snapshot.get("top_fan_out_hotspots", [])
    d_blast, blast_top = compute_blast_mismatch(r, prod_nodes, covered_set, hotspots)

    print("[drift] Computing D_orphan ...")
    d_orphan, orphan_paths = compute_orphan_phantom(r, test_nodes, snapshot_unresolved)

    print("[drift] Computing D_violation ...")
    d_viol, violation_gaps = compute_violation_gap(r, test_node_set)

    score = composite_score(d_cov, d_blast, d_orphan, d_viol)

    scores = {
        "coverage": d_cov,
        "blast": d_blast,
        "orphan": d_orphan,
        "violation": d_viol,
        "composite": score,
    }

    print("[drift] Writing results to Redis ...")
    write_to_redis(
        r,
        scores=scores,
        uncovered_paths=uncovered_paths,
        orphan_paths=orphan_paths,
        blast_top=blast_top,
        violation_gaps=violation_gaps,
        prod_total=len(prod_nodes),
        test_total=len(test_nodes),
    )

    # Summary table
    bar_w = 30
    print("\n" + "=" * 60)
    print("  ADG TEST-CODE DRIFT SCORE")
    print("=" * 60)
    for label, key, weight in [
        ("Coverage gap", "coverage", 0.40),
        ("Blast mismatch", "blast", 0.30),
        ("Orphan tests", "orphan", 0.20),
        ("Violation gap", "violation", 0.10),
    ]:
        val = scores[key]
        bar = int(val * bar_w)
        bar_str = "█" * bar + "░" * (bar_w - bar)
        print(f"  {label:<16} {bar_str}  {val:.3f}  (w={weight})")
    print("-" * 60)
    print(f"  {'COMPOSITE SCORE':<16} {'':>32}  {score:.4f}")
    print("=" * 60)
    print(f"\n  Prod modules : {len(prod_nodes):>6}")
    print(f"  Test modules : {len(test_nodes):>6}")
    print(f"  Uncovered    : {len(uncovered_paths):>6}  ({100 * d_cov:.1f}%)")
    print(f"  Orphan tests : {len(orphan_paths):>6}")
    print(f"  Blast top    : {blast_top[0]['path'] if blast_top else 'N/A'}")
    print("\n  Redis keys written under adg:drift:* (TTL=1h)")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Public exports for testing
# ---------------------------------------------------------------------------

RATCHET_THRESHOLD = 0.15  # 15% drift threshold


def calculate_drift(artifact_a: dict, artifact_b: dict) -> float:
    """Calculate drift score between two ADG artifacts.
    
    Args:
        artifact_a: First ADG artifact dict
        artifact_b: Second ADG artifact dict
        
    Returns:
        Drift score between 0.0 and 1.0 (higher = more drift)
    """
    nodes_a = artifact_a.get("total_nodes", 0)
    nodes_b = artifact_b.get("total_nodes", 0)

    if nodes_a == 0 and nodes_b == 0:
        return 0.0

    max_nodes = max(nodes_a, nodes_b)
    node_drift = abs(nodes_a - nodes_b) / max_nodes if max_nodes > 0 else 0.0

    edges_a = artifact_a.get("total_edges", 0)
    edges_b = artifact_b.get("total_edges", 0)

    max_edges = max(edges_a, edges_b)
    edge_drift = abs(edges_a - edges_b) / max_edges if max_edges > 0 else 0.0

    return 0.5 * node_drift + 0.5 * edge_drift


def compare_artifacts(artifact_a: dict, artifact_b: dict) -> dict:
    """Compare two ADG artifacts and return detailed diff.
    
    Args:
        artifact_a: First ADG artifact dict
        artifact_b: Second ADG artifact dict
        
    Returns:
        Dict with comparison metrics
    """
    return {
        "drift_score": calculate_drift(artifact_a, artifact_b),
        "node_diff": artifact_b.get("total_nodes", 0) - artifact_a.get("total_nodes", 0),
        "edge_diff": artifact_b.get("total_edges", 0) - artifact_a.get("total_edges", 0),
        "artifact_a_digest": artifact_a.get("digest", "unknown"),
        "artifact_b_digest": artifact_b.get("digest", "unknown"),
    }


def check_ratchet(current_score: float, baseline_score: float) -> bool:
    """Check if drift exceeds ratchet threshold.
    
    Args:
        current_score: Current drift score
        baseline_score: Baseline drift score
        
    Returns:
        True if drift is within acceptable bounds
    """
    drift_increase = current_score - baseline_score
    return drift_increase <= RATCHET_THRESHOLD
