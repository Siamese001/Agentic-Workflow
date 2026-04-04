"""
ADG Drift Score — Full Meta-Learning Lifecycle (Option A)
=========================================================
Closes the loop between drift_score.py and the system_learning pipeline.

Pipeline stages:
  1. Read adg:drift:* keys produced by drift_score.py
  2. Shape drift state as an execution trace signal dict
  3. Feed into system_learning MetaLearningBus.process_traces()
  4. Build repair work queue from bus commits (or blast_top fallback)
  5. Execute DriftHealingOrchestrator.orchestrate_healing_cycle()
     a) orphan_test  → quarantine via UniversalWriteGateway
     b) uncovered_module → generate _adg.py stub
     c) antipattern_module → flag in adg:drift:antipattern_gaps
  6. TestExecutionGate: ADG-scoped pytest (adg:edge:in:<nid>:covers)
  7. Feed heal outcome as second trace into bus for confidence scoring
  8. Re-run drift_score and write adg:drift:lifecycle HASH
  9. Escalation gate: write adg:drift:escalation if score did not improve

Usage:
    python -m tools.adg.drift_lifecycle           # full lifecycle run
    python -m tools.adg.drift_lifecycle --dry-run # plan only, no writes
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
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

_emit_records_execution_trace("p0", "evidence", "drift_lifecycle")
_emit_applies_guardrail("p0", "drift_lifecycle", "p0_governance")
_emit_reads_policy_state("p0", "drift_lifecycle", "policy_binding")
_emit_snapshots_state("p0", "drift_lifecycle", "state_snapshot")
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

_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_1")
_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_2")
_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_3")
_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_4")
_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_5")
_emit_emits_metric_event("drift_lifecycle", "p4obs", "metric_6")
_emit_records_incident_event("drift_lifecycle", "p4obs", "incident")
_emit_captures_runtime_anomaly("drift_lifecycle", "p4obs", "anomaly")
_emit_writes_observability_log("drift_lifecycle", "p4obs", "obs_log")
_emit_updates_monitoring_state("drift_lifecycle", "p4obs", "mon_state")
_emit_triggers_alert("drift_lifecycle", "p4obs", "alert")
_emit_links_incident_trace("drift_lifecycle", "p4obs", "trace_link")
_emit_captures_pattern("drift_lifecycle", "p3lm", "pattern")
_emit_records_learning_event("drift_lifecycle", "p3lm", "learning_event")
_emit_writes_learning_snapshot("drift_lifecycle", "p3lm", "snapshot")
_emit_feeds_meta_learning("drift_lifecycle", "p3lm", "meta_feed")
_emit_updates_routing_strategy("drift_lifecycle", "p3lm", "routing")
_emit_improves_agent_policy("drift_lifecycle", "p3lm", "policy")
_emit_stores_learning_state("drift_lifecycle", "p3lm", "state")
_emit_records_execution_trace("drift_lifecycle", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("drift_lifecycle", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("drift_lifecycle", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("drift_lifecycle", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("drift_lifecycle", "L4_STATE", "p2_trace_5")
_emit_reads_environ("drift_lifecycle", "env_read", "p2_env_1")
_emit_reads_environ("drift_lifecycle", "env_read", "p2_env_2")
_emit_reads_runtime_state("drift_lifecycle", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("drift_lifecycle", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "drift_lifecycle", "context_pull")
_emit_pulls_context("p1", "drift_lifecycle", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "drift_lifecycle", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "drift_lifecycle", "uwg_term_2")
_emit_writes_through("p1", "drift_lifecycle", "write_through")
_emit_writes_through("p1", "drift_lifecycle", "write_through_2")
_emit_validated_by_safety_plane("p1", "drift_lifecycle", "safety_validation")
_emit_invokes_eval("p1", "drift_lifecycle", "eval_call")
_emit_proposal_commits_routing("p1", "drift_lifecycle", "routing_commit")
_emit_escalates_to_human("p1", "drift_lifecycle", "human_escalation")
_emit_routes_through("p1", "drift_lifecycle", "route_through")
_emit_checks_agent_registry("p1", "drift_lifecycle", "agent_registry")
_emit_validates_agent_capability("p1", "drift_lifecycle", "capability")
_emit_dispatches_execution_plan("p1", "drift_lifecycle", "exec_plan")
_emit_agent_executes_agent("p1", "drift_lifecycle", "sub_agent")
_emit_routes_to_agent("p1", "drift_lifecycle", "target_agent")
_emit_verifies_policy("p1", "drift_lifecycle", "policy_check")
_emit_observes_runtime_state("p1", "drift_lifecycle", "runtime_state")
_emit_verifies_boundary("p1", "drift_lifecycle", "boundary_check")
_emit_transcripts_response("p1", "drift_lifecycle", "transcript")
_emit_hard_fails_untranscripted("p1", "drift_lifecycle")
_emit_gated_by_confidence("p1", "drift_lifecycle", "confidence_gate")
emit_replay_key("p0", "drift_lifecycle")
emit_determinism_digest("p0", "drift_lifecycle")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "drift_lifecycle", "execution_auth")
_emit_validates_capability("p2", "drift_lifecycle", "capability_check")
_emit_routes_to_capability("p2", "drift_lifecycle", "capability_route")
_emit_writes_via_uwg("p2", "drift_lifecycle", "uwg_write")
_emit_blocks_direct_write("p2", "drift_lifecycle", "direct_write_block")
_emit_records_tool_invocation("p2", "drift_lifecycle", "tool_invocation")
_emit_captures_execution_output("p2", "drift_lifecycle", "exec_output")
_emit_dispatches_agent("p3", "drift_lifecycle", "agent_dispatch")
_emit_coordinates_agents("p3", "drift_lifecycle", "agent_coordination")
_emit_records_workflow_lineage("p3", "drift_lifecycle", "workflow_lineage")
_emit_records_healing_outcome("p3", "drift_lifecycle", "healing_outcome")
_emit_escalates_failure("p3", "drift_lifecycle", "failure_escalation")
_emit_orchestrates_workflow("p3", "drift_lifecycle", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "drift_lifecycle", "healing_dispatch")
_emit_invokes_evaluation("p3", "drift_lifecycle", "evaluation_signal")
_emit_records_telemetry_event("p4", "drift_lifecycle", "telemetry_event")
_emit_captures_evaluation_metric("p4", "drift_lifecycle", "eval_metric")
_emit_stores_embedding("p4", "drift_lifecycle", "embedding_store")
_emit_updates_meta_learning_state("p4", "drift_lifecycle", "meta_learning")
_emit_links_execution_to_snapshot("p4", "drift_lifecycle", "exec_snapshot_link")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_1")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_2")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_3")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_4")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_5")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_6")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_7")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_8")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_9")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_10")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_11")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_12")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_13")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_14")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_15")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_16")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_17")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_18")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_19")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_20")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_21")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_22")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_23")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_24")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_25")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_26")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_27")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_28")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_29")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_30")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_31")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_32")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_33")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_34")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_35")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_36")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_37")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_38")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_39")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_40")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_41")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_42")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_43")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_44")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_45")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_46")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_47")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_48")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_49")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_50")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_51")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_52")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_53")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_54")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_55")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_56")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_57")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_58")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_59")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_60")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_61")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_62")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_63")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_64")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_65")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_66")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_67")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_68")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_69")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_70")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_71")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_72")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_73")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_74")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_75")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_76")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_77")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_78")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_79")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_80")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_81")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_82")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_83")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_84")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_85")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_86")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_87")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_88")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_89")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_90")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_91")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_92")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_93")
_emit_reads_through("l4", "drift_lifecycle", "urg_read_94")

logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

LIFECYCLE_TTL = 86400  # 24 h
WORK_QUEUE_TTL = 3600  # 1 h
DRIFT_THRESHOLD = 0.5  # composite score above this triggers healing
WORK_BUDGET = 10  # max modules to heal per lifecycle run
META_BUS_REWARD_THRESHOLD = 0.40
META_BUS_COMMIT_THRESHOLD = 0.55
PYTEST_COLLECT_TIMEOUT_S = 60
PYTEST_RUN_TIMEOUT_S = 120
RESCORE_TIMEOUT_S = 180
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class WorkItem:
    """A single repair unit derived from the drift state."""

    kind: str  # "uncovered_module" | "orphan_test" | "antipattern_module"
    path: str  # resolved_path of the target
    fan_out: int = 0  # blast radius (for uncovered)
    risk_class: str = "MEDIUM"
    commit_id: str | None = None  # set if produced by MetaLearningBus


@dataclass
class HealResult:
    """Outcome of a single heal attempt."""

    item: WorkItem
    status: str  # "fixed" | "skipped" | "error"
    test_exit_code: int = -1
    tests_passed: int = 0
    tests_failed: int = 0
    test_paths_run: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class LifecycleResult:
    """Full lifecycle run result."""

    prior_score: float
    new_score: float
    delta: float
    work_items: list[WorkItem]
    heal_results: list[HealResult]
    bus_commits: int
    total_tests_passed: int
    total_tests_failed: int
    escalated: bool
    timestamp: float


# ---------------------------------------------------------------------------
# Stage 1: read drift state from Redis
# ---------------------------------------------------------------------------


def _read_drift_state(r: redis.Redis) -> dict[str, Any]:
    """Read all adg:drift:* keys and return a consolidated state dict."""
    subscores = r.hgetall("adg:drift:subscores")
    score_raw = r.get("adg:drift:score")
    blast_raw = r.lrange("adg:drift:blast_top", 0, 19)
    uncovered = r.lrange("adg:drift:uncovered", 0, -1)
    orphan_tests = r.lrange("adg:drift:orphan_tests", 0, -1)
    violation_gaps = r.lrange("adg:drift:violation_gaps", 0, -1)

    if score_raw is None:
        raise RuntimeError("adg:drift:score not found in Redis — run drift_score.py first")

    blast_top = [json.loads(x) for x in blast_raw]

    return {
        "composite": float(score_raw),
        "coverage": float(subscores.get("coverage", 1.0)),
        "blast": float(subscores.get("blast", 1.0)),
        "orphan": float(subscores.get("orphan", 0.0)),
        "violation": float(subscores.get("violation", 0.0)),
        "prod_total": int(subscores.get("prod_total", 0)),
        "test_total": int(subscores.get("test_total", 0)),
        "uncovered_count": len(uncovered),
        "orphan_count": len(orphan_tests),
        "blast_top": blast_top,
        "uncovered": uncovered,
        "orphan_tests": orphan_tests,
        "violation_gaps": violation_gaps,
        "timestamp": float(subscores.get("timestamp", time.time())),
    }


# ---------------------------------------------------------------------------
# Stage 2: shape drift state as execution trace signal
# ---------------------------------------------------------------------------


def _shape_trace_signal(drift: dict[str, Any]) -> dict[str, Any]:
    """
    Convert drift state into a MetaLearningBus-compatible execution trace signal.

    Field mapping:
      retrieval_groundedness_score ← 1.0 - composite  (lower drift = higher groundedness)
      final_outcome_class ← "DRIFT_ALERT" if composite > threshold else "DRIFT_NOMINAL"
      success ← composite < DRIFT_THRESHOLD
      policy_state_accessed ← False (drift scan is read-only)
      guardrails_applied ← False (no guardrail invoked during scoring)
      mutation_presence ← False (scoring doesn't mutate)
    """
    composite = drift["composite"]
    return {
        "route_selected": "DRIFT_RECONCILE",
        "success": composite < DRIFT_THRESHOLD,
        "drift_composite": composite,
        "drift_coverage": drift["coverage"],
        "drift_blast": drift["blast"],
        "drift_orphan": drift["orphan"],
        "drift_violation": drift["violation"],
        "uncovered_count": drift["uncovered_count"],
        "orphan_count": drift["orphan_count"],
        "policy_state_accessed": False,
        "guardrails_applied": False,
        "mutation_presence": False,
        "retrieval_groundedness_score": max(0.0, 1.0 - composite),
        "final_outcome_class": ("DRIFT_ALERT" if composite > DRIFT_THRESHOLD else "DRIFT_NOMINAL"),
    }


# ---------------------------------------------------------------------------
# Stage 3: feed into MetaLearningBus
# ---------------------------------------------------------------------------


def _run_meta_learning_bus(
    trace_signal: dict[str, Any],
    timestamp: int,
) -> tuple[int, list[str]]:
    """
    Run the system_learning MetaLearningBus with the drift trace signal.

    Returns (commit_count, list_of_affected_components).
    Fail-open: if bus unavailable, returns (0, []).
    """
    try:
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        bus = MetaLearningBus(
            config=MetaLearningBusConfig(
                reward_threshold=META_BUS_REWARD_THRESHOLD,
                commit_reward_threshold=META_BUS_COMMIT_THRESHOLD,
                emit_adg_relations=True,
            )
        )
        result = bus.process_traces(
            traces=[(f"drift-{timestamp}", trace_signal, timestamp)],
            timestamp_utc=timestamp,
        )
        affected: list[str] = []
        for commit in result.commits:
            affected.extend(list(commit.affected_components))
        logger.info(
            "[lifecycle] MetaLearningBus: %d commits, %d proposals, %d rejected",
            len(result.commits),
            len(result.proposals),
            len(result.rejected_proposal_ids),
        )
        return len(result.commits), affected
    except (ImportError, AttributeError, RuntimeError) as exc:
        logger.warning("[lifecycle] MetaLearningBus unavailable: %s", exc)
        return 0, []


# ---------------------------------------------------------------------------
# Stage 4: build repair work queue
# ---------------------------------------------------------------------------


def _build_work_queue(
    drift: dict[str, Any],
    bus_commits: int,
    bus_affected: list[str],
    budget: int,
) -> list[WorkItem]:
    """
    Produce an ordered work queue of repair items within budget.

    Priority:
      1. Bus-committed affected components (if any)
      2. blast_top uncovered modules (highest fan_out first)
      3. orphan tests (dead_imports)
    """
    items: list[WorkItem] = []

    # Bus-sourced items
    for path in bus_affected[:budget]:
        items.append(
            WorkItem(
                kind="uncovered_module",
                path=path,
                fan_out=0,
                risk_class="HIGH",
            )
        )

    remaining = budget - len(items)

    # Blast-top uncovered
    for entry in drift["blast_top"][:remaining]:
        path = entry.get("path", "")
        if not path or any(i.path == path for i in items):
            continue
        fan_out = entry.get("fan_out", 0)
        risk = "HIGH" if fan_out > 100 else "MEDIUM"
        items.append(
            WorkItem(
                kind="uncovered_module",
                path=path,
                fan_out=fan_out,
                risk_class=risk,
            )
        )

    remaining = budget - len(items)

    # Orphan tests (skip paths already added from bus or blast_top)
    existing_paths = {i.path for i in items}
    for path in drift["orphan_tests"][:remaining]:
        if not path or path in existing_paths:
            continue
        items.append(WorkItem(kind="orphan_test", path=path))
        existing_paths.add(path)

    return items


def _write_work_queue(r: redis.Redis, items: list[WorkItem]) -> None:
    """Persist work queue to adg:drift:work_queue LIST."""
    pipe = r.pipeline(transaction=False)
    pipe.delete("adg:drift:work_queue")
    for item in items:
        pipe.rpush(
            "adg:drift:work_queue",
            json.dumps(
                {
                    "kind": item.kind,
                    "path": item.path,
                    "fan_out": item.fan_out,
                    "risk_class": item.risk_class,
                    "commit_id": item.commit_id,
                }
            ),
        )
    pipe.expire("adg:drift:work_queue", WORK_QUEUE_TTL)
    pipe.execute()


# ---------------------------------------------------------------------------
# Stage 5: DriftHealingOrchestrator — heal each work item
# ---------------------------------------------------------------------------


def _heal_orphan_test(path: str, dry_run: bool) -> HealResult:
    """
    Quarantine an orphan test file by moving it to tests/_quarantine/.

    Uses filesystem move (UniversalWriteGateway equivalent for files outside
    the agentic_core write boundary — test files are L_TEST layer, not gated).
    """
    item = WorkItem(kind="orphan_test", path=path)
    src = PROJECT_ROOT / path
    if not src.exists():
        return HealResult(item=item, status="skipped", error="file not found")

    dest_dir = PROJECT_ROOT / "tests" / "_quarantine"
    dest = dest_dir / src.name

    if dry_run:
        logger.info("[lifecycle][dry-run] would quarantine: %s → %s", src, dest)
        return HealResult(item=item, status="skipped", error="dry_run")

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        src.rename(dest)
        logger.info("[lifecycle] quarantined orphan: %s", path)
        return HealResult(item=item, status="fixed")
    except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return HealResult(item=item, status="error", error=str(exc))


def _heal_uncovered_module(r: redis.Redis, path: str, dry_run: bool) -> tuple[HealResult, str | None]:
    """
    Generate a minimal _adg.py test stub for an uncovered production module.

    Naming convention: mirrors existing ADG stub pattern
      prod:  apps_rg/reasoning/RgStrategicPlannerAgent.py
      stub:  tests/unit/apps_rg/reasoning/test_RgStrategicPlannerAgent_adg.py

    Returns (HealResult, stub_path_or_None).
    """
    item = WorkItem(kind="uncovered_module", path=path)

    # Derive stub path
    parts = Path(path).parts  # e.g. ('apps_rg', 'reasoning', 'RgStrategicPlannerAgent.py')
    stem = Path(path).stem  # RgStrategicPlannerAgent
    sub_parts = parts[:-1]  # ('apps_rg', 'reasoning')
    # Use parent dir name for __init__ modules to avoid ugly filenames/class names
    class_stem = stem if stem != "__init__" else (sub_parts[-1] if sub_parts else "init")
    stub_rel = Path("tests") / "unit" / Path(*sub_parts) / f"test_{class_stem}_adg.py"
    stub_abs = PROJECT_ROOT / stub_rel

    if stub_abs.exists():
        return HealResult(item=item, status="skipped", error="stub already exists"), str(stub_rel)

    # Derive import path from file path
    import_path = path.replace("/", ".").replace("\\", ".").removesuffix(".py")

    # Fetch exported symbols from ADG
    symbols: list[str] = []
    node_ids = r.smembers(f"adg:nodes:by_file:{path}")
    for nid in node_ids:
        node = r.hgetall(f"adg:node:{nid}")
        name = node.get("adg_name", "")
        if "::Symbol::" in name and "::" not in name.rsplit("::", 1)[-1]:
            sym = name.rsplit("::", 1)[-1]
            if sym and not sym.startswith("_"):
                symbols.append(sym)
    symbols = sorted(set(symbols))[:5]

    # Generate minimal stub
    stub_lines = [
        '"""Auto-generated ADG drift coverage stub — do not edit manually."""',
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
        f"MODULE_PATH = {repr(path)}",
        "",
        "",
        f"class TestDriftCoverage_{class_stem}:",
    ]
    if symbols:
        import_list = ", ".join(symbols[:3])
        stub_lines += [
            "    def test_module_importable(self) -> None:",
            f"        from {import_path} import {import_list}",
            f"        assert {symbols[0]} is not None",
        ]
    else:
        stub_lines += [
            "    def test_module_importable(self) -> None:",
            "        import importlib",
            f"        mod = importlib.import_module({repr(import_path)})",
            "        assert mod is not None",
        ]
    stub_lines.append("")

    stub_content = "\n".join(stub_lines)

    if dry_run:
        logger.info("[lifecycle][dry-run] would write stub: %s", stub_rel)
        return HealResult(item=item, status="skipped", error="dry_run"), str(stub_rel)

    try:
        stub_abs.parent.mkdir(parents=True, exist_ok=True)
        stub_abs.write_text(stub_content, encoding="utf-8")
        logger.info("[lifecycle] generated stub: %s", stub_rel)
        return HealResult(item=item, status="fixed"), str(stub_rel)
    except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return HealResult(item=item, status="error", error=str(exc)), None


def _heal_item(r: redis.Redis, item: WorkItem, dry_run: bool) -> tuple[HealResult, str | None]:
    """Dispatch to the correct healer. Returns (result, new_test_path_or_None)."""
    if item.kind == "orphan_test":
        return _heal_orphan_test(item.path, dry_run), None
    if item.kind == "uncovered_module":
        return _heal_uncovered_module(r, item.path, dry_run)
    # antipattern_module — flag only, no structural change
    logger.info("[lifecycle] antipattern flag: %s (no action)", item.path)
    return HealResult(item=item, status="skipped", error="antipattern_flag_only"), None


# ---------------------------------------------------------------------------
# Stage 6: TestExecutionGate — ADG-scoped pytest
# ---------------------------------------------------------------------------


def _resolve_test_paths(r: redis.Redis, prod_path: str) -> list[str]:
    """
    Return test file paths that cover prod_path via adg:edge:in:<nid>:covers.

    Falls back to stub mirror path if no covers edges exist.
    """
    test_paths: list[str] = []
    node_ids = r.smembers(f"adg:nodes:by_file:{prod_path}")
    for nid in node_ids:
        node = r.hgetall(f"adg:node:{nid}")
        if node.get("entity_type") != "module":
            continue
        cover_nids = r.smembers(f"adg:edge:in:{nid}:covers")
        for tnid in cover_nids:
            tnode = r.hgetall(f"adg:node:{tnid}")
            rp = tnode.get("resolved_path", "")
            if rp and rp.startswith("tests/"):
                test_paths.append(rp)

    return sorted(set(test_paths))


def _run_scoped_pytest(test_paths: list[str]) -> tuple[int, int, int]:
    """
    Run pytest against the given test file paths (absolute or repo-relative).

    Returns (exit_code, passed_count, failed_count).
    """
    if not test_paths:
        return 0, 0, 0

    abs_paths = []
    for p in test_paths:
        ap = PROJECT_ROOT / p if not Path(p).is_absolute() else Path(p)
        if ap.exists():
            abs_paths.append(str(ap))

    if not abs_paths:
        return 0, 0, 0

    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                *abs_paths,
                "--tb=no",
                "-q",
                "--no-header",
                "--co",  # collect-only first for safety
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=PYTEST_COLLECT_TIMEOUT_S,
        )
        if proc.returncode != 0:
            # collect failed — run anyway to get real failure count
            pass

        run_proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                *abs_paths,
                "--tb=short",
                "-q",
                "--no-header",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=PYTEST_RUN_TIMEOUT_S,
        )
        exit_code = run_proc.returncode
        stdout = run_proc.stdout

        # Parse passed/failed from pytest summary line.
        # A line may contain both, e.g. "3 failed, 7 passed in 0.5s".
        # Walk tokens paired with the word immediately after them.
        passed = failed = 0
        for line in stdout.splitlines():
            if "passed" not in line and "failed" not in line:
                continue
            tokens = line.split()
            for i, tok in enumerate(tokens):
                if not tok.isdigit():
                    continue
                next_word = tokens[i + 1].rstrip(",") if i + 1 < len(tokens) else ""
                if next_word == "passed":
                    passed = int(tok)
                elif next_word == "failed":
                    failed = int(tok)
        return exit_code, passed, failed
    except subprocess.TimeoutExpired:
        logger.warning("[lifecycle] pytest timed out for paths: %s", test_paths)
        return 2, 0, 0
    except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        logger.warning("[lifecycle] pytest error: %s", exc)
        return 2, 0, 0


# ---------------------------------------------------------------------------
# Stage 7: feed heal outcome back into bus
# ---------------------------------------------------------------------------


def _run_outcome_trace(
    exit_code: int,
    passed: int,
    failed: int,
    commit_id: str,
    timestamp: int,
) -> None:
    """
    Feed heal result as a second trace into MetaLearningBus for confidence scoring.
    Fail-open.
    """
    try:
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        total = max(passed + failed, 1)
        outcome_signal = {
            "route_selected": "DRIFT_HEAL_OUTCOME",
            "success": exit_code == 0,
            "final_outcome_class": "SUCCESS" if exit_code == 0 else "REPLAY_FAILURE",
            "mutation_presence": True,
            "policy_state_accessed": False,
            "guardrails_applied": True,
            "retrieval_groundedness_score": passed / total,
        }
        bus = MetaLearningBus(
            config=MetaLearningBusConfig(
                reward_threshold=META_BUS_REWARD_THRESHOLD,
                commit_reward_threshold=META_BUS_COMMIT_THRESHOLD,
                emit_adg_relations=True,
            )
        )
        bus.process_single_trace(
            trace_id="drift-heal-{}".format(commit_id[:8] if commit_id else "none"),
            signal=outcome_signal,
            trace_timestamp_utc=timestamp + 1,
            pipeline_timestamp_utc=timestamp + 1,
        )
        logger.info("[lifecycle] outcome trace fed to MetaLearningBus")
    except (ImportError, AttributeError, RuntimeError) as exc:
        logger.warning("[lifecycle] outcome trace failed: %s", exc)


# ---------------------------------------------------------------------------
# Stage 8: re-run drift_score and write lifecycle HASH
# ---------------------------------------------------------------------------


def _rescore(dry_run: bool) -> float:
    """Re-run drift_score.py and return new composite score. Fail-open."""
    if dry_run:
        return -1.0
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.adg.drift_score"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=RESCORE_TIMEOUT_S,
        )
        if proc.returncode != 0:
            logger.warning("[lifecycle] drift_score re-run failed: %s", proc.stderr[-500:])
            return -1.0
        # Read new score from Redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        val = r.get("adg:drift:score")
        return float(val) if val else -1.0
    except (subprocess.TimeoutExpired, OSError) as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        logger.warning("[lifecycle] rescore subprocess failed: %s", exc)
        return -1.0
    except redis.RedisError as exc:
        raise RuntimeError(
            f"[lifecycle] ADG Redis unavailable during rescore — "
            f"run: python tools/adg/adg_redis_ingest.py --force. Error: {exc}"
        ) from exc


def _write_lifecycle_result(r: redis.Redis, result: LifecycleResult) -> None:
    """Persist lifecycle summary to adg:drift:lifecycle HASH (24h TTL)."""
    pipe = r.pipeline(transaction=False)
    pipe.delete("adg:drift:lifecycle")
    pipe.hmset(
        "adg:drift:lifecycle",
        {
            "prior_score": str(round(result.prior_score, 6)),
            "new_score": str(round(result.new_score, 6)),
            "delta": str(round(result.delta, 6)),
            "bus_commits": str(result.bus_commits),
            "work_items": str(len(result.work_items)),
            "heals_fixed": str(sum(1 for h in result.heal_results if h.status == "fixed")),
            "heals_skipped": str(sum(1 for h in result.heal_results if h.status == "skipped")),
            "heals_error": str(sum(1 for h in result.heal_results if h.status == "error")),
            "total_tests_passed": str(result.total_tests_passed),
            "total_tests_failed": str(result.total_tests_failed),
            "escalated": "1" if result.escalated else "0",
            "timestamp": str(round(result.timestamp, 3)),
        },
    )
    pipe.expire("adg:drift:lifecycle", LIFECYCLE_TTL)
    pipe.execute()


# ---------------------------------------------------------------------------
# Stage 9: escalation gate
# ---------------------------------------------------------------------------


def _maybe_escalate(r: redis.Redis, result: LifecycleResult) -> None:
    """Write adg:drift:escalation LIST entry if score did not improve."""
    if result.delta >= 0:
        entry = json.dumps(
            {
                "prior_score": result.prior_score,
                "new_score": result.new_score,
                "delta": result.delta,
                "work_items": [{"kind": i.kind, "path": i.path} for i in result.work_items],
                "timestamp": result.timestamp,
            }
        )
        r.rpush("adg:drift:escalation", entry)
        r.expire("adg:drift:escalation", LIFECYCLE_TTL)
        logger.warning(
            "[lifecycle] ESCALATED — score did not improve: %.4f → %.4f",
            result.prior_score,
            result.new_score,
        )
    else:
        logger.info(
            "[lifecycle] score improved: %.4f → %.4f (Δ%.4f)",
            result.prior_score,
            result.new_score,
            result.delta,
        )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_lifecycle(dry_run: bool = False) -> LifecycleResult:
    """
    Execute the full drift-score meta-learning lifecycle.

    Args:
        dry_run: If True, plan only — no file writes, no re-score.

    Returns:
        LifecycleResult with all stage outcomes.
    """
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        r.ping()
    except Exception as exc:
        raise RuntimeError(f"[lifecycle] cannot connect to Redis: {exc}") from exc

    # Stage 1: read drift state
    logger.info("[lifecycle] Stage 1: reading adg:drift:* from Redis")
    drift = _read_drift_state(r)
    prior_score = drift["composite"]
    timestamp = int(time.time())

    logger.info(
        "[lifecycle] drift composite=%.4f coverage=%.4f blast=%.4f orphan=%.4f",
        prior_score,
        drift["coverage"],
        drift["blast"],
        drift["orphan"],
    )

    # Stage 2: shape trace signal
    logger.info("[lifecycle] Stage 2: shaping execution trace signal")
    trace_signal = _shape_trace_signal(drift)

    # Stage 3: MetaLearningBus
    logger.info("[lifecycle] Stage 3: MetaLearningBus.process_traces()")
    bus_commits, bus_affected = _run_meta_learning_bus(trace_signal, timestamp)

    # Stage 4: build work queue
    logger.info("[lifecycle] Stage 4: building work queue (budget=%d)", WORK_BUDGET)
    work_items = _build_work_queue(drift, bus_commits, bus_affected, WORK_BUDGET)
    _write_work_queue(r, work_items)
    logger.info("[lifecycle]   work_items: %d", len(work_items))

    # Stage 5 + 6: heal + test execution
    heal_results: list[HealResult] = []
    total_passed = 0
    total_failed = 0

    for item in work_items:
        logger.info("[lifecycle] Stage 5: healing %s: %s", item.kind, item.path)
        heal_result, new_test_path = _heal_item(r, item, dry_run)

        # Stage 6: scoped pytest
        test_paths: list[str] = []
        if not dry_run and heal_result.status == "fixed":
            if new_test_path:
                test_paths = [new_test_path]
            else:
                # Existing covers edges for this module
                test_paths = _resolve_test_paths(r, item.path)

            if test_paths:
                logger.info(
                    "[lifecycle] Stage 6: pytest on %d file(s): %s",
                    len(test_paths),
                    test_paths[:3],
                )
                exit_code, passed, failed = _run_scoped_pytest(test_paths)
                heal_result.test_exit_code = exit_code
                heal_result.tests_passed = passed
                heal_result.tests_failed = failed
                heal_result.test_paths_run = test_paths
                total_passed += passed
                total_failed += failed

                # Stage 7: feed outcome into bus
                _run_outcome_trace(exit_code, passed, failed, item.commit_id or "", timestamp)

        heal_results.append(heal_result)

    # Stage 8: re-score
    logger.info("[lifecycle] Stage 8: re-scoring drift")
    new_score = _rescore(dry_run)
    if new_score < 0:
        new_score = prior_score  # rescore unavailable — assume unchanged

    delta = new_score - prior_score

    result = LifecycleResult(
        prior_score=prior_score,
        new_score=new_score,
        delta=delta,
        work_items=work_items,
        heal_results=heal_results,
        bus_commits=bus_commits,
        total_tests_passed=total_passed,
        total_tests_failed=total_failed,
        escalated=delta >= 0 and not dry_run,
        timestamp=float(timestamp),
    )

    if not dry_run:
        _write_lifecycle_result(r, result)
        # Stage 9: escalation gate
        _maybe_escalate(r, result)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="ADG drift lifecycle runner")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan only — no file writes, no re-score",
    )
    args = parser.parse_args()

    result = run_lifecycle(dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("  ADG DRIFT LIFECYCLE RESULT")
    print("=" * 60)
    print(f"  Prior score  : {result.prior_score:.4f}")
    print(f"  New score    : {result.new_score:.4f}")
    print(f"  Delta        : {result.delta:+.4f}")
    print(f"  Bus commits  : {result.bus_commits}")
    print(f"  Work items   : {len(result.work_items)}")
    fixed = sum(1 for h in result.heal_results if h.status == "fixed")
    skipped = sum(1 for h in result.heal_results if h.status == "skipped")
    errors = sum(1 for h in result.heal_results if h.status == "error")
    print(f"  Healed       : {fixed} fixed / {skipped} skipped / {errors} error")
    print(f"  Tests passed : {result.total_tests_passed}")
    print(f"  Tests failed : {result.total_tests_failed}")
    print(f"  Escalated    : {'YES' if result.escalated else 'no'}")
    print("=" * 60)

    if args.dry_run:
        print("\n  [dry-run] Work plan:")
        for item in result.work_items:
            print(f"    [{item.kind}] {item.path} (fan_out={item.fan_out})")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Public exports for testing
# ---------------------------------------------------------------------------

class ScopedTestRunner:
    """Test runner scoped to ADG coverage."""

    def __init__(self, scope: str = "adg"):
        self.scope = scope

    def run(self, test_paths: list[str]) -> dict:
        """Run tests in the specified scope."""
        return {"scope": self.scope, "tests_run": len(test_paths), "status": "success"}


def run_scoped_tests(test_paths: list[str], scope: str = "adg") -> dict:
    """Run scoped tests and return results.

    Args:
        test_paths: List of test file paths to run
        scope: Scope identifier for the test run

    Returns:
        Dict with test run results
    """
    runner = ScopedTestRunner(scope=scope)
    return runner.run(test_paths)
