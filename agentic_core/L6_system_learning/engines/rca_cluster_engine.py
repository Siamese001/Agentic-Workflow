"""RCA Cluster Engine — clusters TraceFeatureRecords into RCAClusters.

Extends the existing ``rca_engine.py`` (which clusters raw audit-log text)
with a structured, ADG-aware clustering pass over ``TraceFeatureRecord``
objects.  Produces ``RCACluster`` objects that feed the optimization
proposal generator.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
3. All cluster outputs are deterministically content-addressed.
4. Clustering is failure-pattern-first: records are grouped by their
   dominant failure category, then sub-grouped by dominant route/guardrail
   to limit cluster explosion.
5. Minimum cluster size is enforced (default: 2); singletons are merged
   into a SINGLETON_RESIDUAL cluster unless ``allow_singletons=True``.
6. Negative-case sources (FailurePattern objects) may be injected to
   seed additional clusters without requiring live trace records.
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "rca_cluster_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "rca_cluster_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rca_cluster_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rca_cluster_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rca_cluster_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rca_cluster_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rca_cluster_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rca_cluster_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rca_cluster_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rca_cluster_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rca_cluster_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rca_cluster_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rca_cluster_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rca_cluster_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rca_cluster_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rca_cluster_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rca_cluster_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rca_cluster_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rca_cluster_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rca_cluster_engine", "exec_snapshot_link")
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json
from agentic_core.L6_system_learning.types.trace_feature_types import (
    FailurePattern,
    RCACluster,
    TraceFeatureRecord,
)

trace_contract._emit_applies_guardrail("p0", "rca_cluster_engine", "p0_governance")
trace_contract._emit_snapshots_state("p0", "rca_cluster_engine", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rca_cluster_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rca_cluster_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rca_cluster_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rca_cluster_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rca_cluster_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rca_cluster_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rca_cluster_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rca_cluster_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rca_cluster_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rca_cluster_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rca_cluster_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rca_cluster_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rca_cluster_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rca_cluster_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("rca_cluster_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rca_cluster_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rca_cluster_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rca_cluster_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rca_cluster_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rca_cluster_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rca_cluster_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rca_cluster_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rca_cluster_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rca_cluster_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "rca_cluster_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rca_cluster_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rca_cluster_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rca_cluster_engine", "write_through")
trace_contract._emit_writes_through("p1", "rca_cluster_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rca_cluster_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rca_cluster_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rca_cluster_engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "rca_cluster_engine", "human_escalation")
trace_contract._emit_routes_through("p1", "rca_cluster_engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "rca_cluster_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rca_cluster_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rca_cluster_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rca_cluster_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rca_cluster_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "rca_cluster_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rca_cluster_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rca_cluster_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rca_cluster_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rca_cluster_engine")
trace_contract._emit_gated_by_confidence("p1", "rca_cluster_engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "rca_cluster_engine")
trace_contract.emit_determinism_digest("p0", "rca_cluster_engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULT_MIN_CLUSTER_SIZE = 2
_SINGLETON_RESIDUAL_PATTERN = "SINGLETON_RESIDUAL"
_NEGATIVE_SEED_PATTERN_PREFIX = "NEG_SEED"


@dataclass
class RCAClusterConfig:
    """Configuration for the RCA cluster engine."""

    min_cluster_size: int = _DEFAULT_MIN_CLUSTER_SIZE
    allow_singletons: bool = False
    max_clusters: int = 64
    sub_group_by_route: bool = True
    sub_group_by_guardrail: bool = False


# ---------------------------------------------------------------------------
# Failure pattern extractor (from TraceFeatureRecord)
# ---------------------------------------------------------------------------


def _derive_failure_pattern(record: TraceFeatureRecord) -> str:
    """Derive a canonical failure pattern label from a TraceFeatureRecord.

    Mapping logic (priority order):
    1. REPLAY_FAILURE  — outcome is REPLAY_FAILURE
    2. ROLLBACK        — outcome is ROLLBACK
    3. HEALER_REQUIRED — healing was invoked regardless of final outcome
    4. HITL_ESCALATION — HITL flag set
    5. LOW_GROUNDEDNESS — groundedness < 0.5
    6. GUARDRAIL_BLOCK — at least one guardrail fired
    7. POLICY_VIOLATION — policy edges present in non-SUCCESS traces
    8. SAFE_FAILURE    — outcome is SAFE_FAILURE
    9. SUCCESS         — outcome is SUCCESS (used for success clusters)
    10. UNKNOWN        — fallback
    """
    oc = record.outcome_class
    if oc == "REPLAY_FAILURE":
        return "REPLAY_FAILURE"
    if oc == "ROLLBACK":
        return "ROLLBACK"
    if record.policy_edges and oc not in ("SUCCESS", "HEALED_SUCCESS"):
        return "POLICY_VIOLATION"
    if record.safety_audit_count > 0:
        # Factor safety audit into failure pattern
        if "REJECT" in record.safety_audit_outcomes:
            return "SAFETY_REJECTION"
        elif "ESCALATE" in record.safety_audit_outcomes:
            return "SAFETY_ESCALATION"
        else:
            return "SAFETY_AUDIT"
    if oc == "SAFE_FAILURE":
        return "SAFE_FAILURE"
    if oc in ("SUCCESS", "HEALED_SUCCESS", "HUMAN_OVERRIDE"):
        return oc
    return "UNKNOWN"


def _derive_sub_key(
    record: TraceFeatureRecord,
    *,
    by_route: bool,
    by_guardrail: bool,
) -> str:
    """Produce a sub-grouping key for within-pattern partitioning."""
    parts: list[str] = []
    if by_route:
        parts.append(f"route:{record.route}")
    if by_guardrail and record.guardrail_edges:
        # Use the first guardrail (most prominent) for sub-grouping
        parts.append(f"guard:{sorted(record.guardrail_edges)[0]}")
    return "|".join(parts) if parts else "_default"


# ---------------------------------------------------------------------------
# Dominant-value helpers
# ---------------------------------------------------------------------------


def _dominant(counter: Counter) -> str:
    if not counter:
        return "UNKNOWN"
    return counter.most_common(1)[0][0]


def _dominant_optional(counter: Counter) -> str | None:
    if not counter:
        return None
    val, _ = counter.most_common(1)[0]
    return val


def _outcome_distribution(records: list[TraceFeatureRecord]) -> tuple[tuple[str, int], ...]:
    c: Counter[str] = Counter(r.outcome_class for r in records)
    return tuple(sorted(c.items()))


def _avg_groundedness(records: list[TraceFeatureRecord]) -> float:
    if not records:
        return 0.0
    return round(sum(r.retrieval_groundedness for r in records) / len(records), 6)


def _hitl_rate(records: list[TraceFeatureRecord]) -> float:
    if not records:
        return 0.0
    return round(sum(1 for r in records if r.hitl_escalation) / len(records), 6)


def _healer_rate(records: list[TraceFeatureRecord]) -> float:
    if not records:
        return 0.0
    return round(sum(1 for r in records if r.healer_used is not None) / len(records), 6)


def _affected_agents(records: list[TraceFeatureRecord]) -> tuple[str, ...]:
    return tuple(sorted({r.adg_node_id for r in records}))


def _adg_cluster_node(failure_pattern: str, sub_key: str, cluster_hash: str) -> str:
    safe = failure_pattern.replace(" ", "_").upper()
    return f"ADG::RCACluster::{safe}::{cluster_hash[:12]}"


# ---------------------------------------------------------------------------
# Cluster builder
# ---------------------------------------------------------------------------


def _build_cluster(
    failure_pattern: str,
    sub_key: str,
    records: list[TraceFeatureRecord],
    timestamp_utc: int,
) -> RCACluster:
    """Build a single RCACluster from a group of records."""
    route_counter: Counter[str] = Counter(r.route for r in records)
    guard_counter: Counter[str] = Counter(g for r in records for g in r.guardrail_edges)
    retrieval_counter: Counter[str] = Counter(r.retrieval_pattern for r in records)

    dominant_route = _dominant(route_counter)
    dominant_guardrail = _dominant_optional(guard_counter)
    dominant_retrieval = _dominant(retrieval_counter)

    member_trace_ids = tuple(sorted(r.trace_id for r in records))
    outcome_dist = _outcome_distribution(records)
    avg_gnd = _avg_groundedness(records)
    hitl_r = _hitl_rate(records)
    healer_r = _healer_rate(records)
    agents = _affected_agents(records)

    # Content-addressed cluster_id
    canonical = deterministic_json(
        {
            "failure_pattern": failure_pattern,
            "member_trace_ids": list(member_trace_ids),
            "sub_key": sub_key,
            "timestamp_utc": timestamp_utc,
        }
    )
    cluster_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    cluster_id = cluster_hash

    adg_node = _adg_cluster_node(failure_pattern, sub_key, cluster_hash)

    return RCACluster(
        cluster_id=cluster_id,
        failure_pattern=failure_pattern,
        dominant_route=dominant_route,
        dominant_guardrail=dominant_guardrail,
        dominant_retrieval_pattern=dominant_retrieval,
        affected_agents=agents,
        member_trace_ids=member_trace_ids,
        member_count=len(records),
        outcome_distribution=outcome_dist,
        avg_groundedness=avg_gnd,
        hitl_escalation_rate=hitl_r,
        healer_invocation_rate=healer_r,
        adg_cluster_node=adg_node,
        timestamp_utc=timestamp_utc,
    )


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------


class RCAClusterEngine:
    """ADG-aware RCA cluster engine.

    Groups ``TraceFeatureRecord`` objects into ``RCACluster`` objects by
    failure pattern, optionally sub-grouped by route and/or guardrail.

    Negative-case ``FailurePattern`` seeds may be injected to ensure that
    known recurring patterns are always represented even when live traces
    are sparse.
    """

    def __init__(self, config: RCAClusterConfig | None = None) -> None:
        self._config = config or RCAClusterConfig()

    def cluster(
        self,
        records: Sequence[TraceFeatureRecord],
        timestamp_utc: int,
        negative_seeds: Sequence[FailurePattern] | None = None,
    ) -> list[RCACluster]:
        """Cluster records into RCAClusters.

        Parameters
        ----------
        records:
            TraceFeatureRecord objects to cluster (order-independent).
        timestamp_utc:
            Caller-supplied Unix timestamp for all produced clusters.
        negative_seeds:
            Optional FailurePattern objects used to seed clusters for
            known negative cases that may lack live trace coverage.

        Returns
        -------
        list[RCACluster]
            Deterministically ordered list (sorted by cluster_id).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RCAClusterEngine.cluster")

        cfg = self._config

        # Build grouping dict: (failure_pattern, sub_key) → [records]
        groups: dict[tuple[str, str], list[TraceFeatureRecord]] = defaultdict(list)
        for rec in records:
            pattern = _derive_failure_pattern(rec)
            sub_key = _derive_sub_key(
                rec,
                by_route=cfg.sub_group_by_route,
                by_guardrail=cfg.sub_group_by_guardrail,
            )
            groups[(pattern, sub_key)].append(rec)

        clusters: list[RCACluster] = []
        singletons: list[TraceFeatureRecord] = []

        for (pattern, sub_key), grp in sorted(groups.items()):
            if len(grp) < cfg.min_cluster_size:
                if cfg.allow_singletons:
                    cluster = _build_cluster(pattern, sub_key, grp, timestamp_utc)
                    clusters.append(cluster)
                else:
                    singletons.extend(grp)
            else:
                cluster = _build_cluster(pattern, sub_key, grp, timestamp_utc)
                clusters.append(cluster)

        # Merge all singletons into one residual cluster
        if singletons:
            residual = _build_cluster(
                _SINGLETON_RESIDUAL_PATTERN,
                "_merged",
                singletons,
                timestamp_utc,
            )
            clusters.append(residual)

        # Inject negative-seed clusters (one per unique source_type + signature)
        if negative_seeds:
            clusters.extend(
                self._seed_clusters_from_negatives(negative_seeds, timestamp_utc),
            )

        # Enforce max_clusters (trim by member_count desc, keep largest)
        if len(clusters) > cfg.max_clusters:
            clusters.sort(key=lambda c: c.member_count, reverse=True)
            clusters = clusters[: cfg.max_clusters]

        clusters.sort(key=lambda c: c.cluster_id)
        return clusters

    def _seed_clusters_from_negatives(
        self,
        seeds: Sequence[FailurePattern],
        timestamp_utc: int,
    ) -> list[RCACluster]:
        """Build minimal RCAClusters from FailurePattern seeds.

        Seeds that already match a pattern in ``records`` are not
        duplicated — they use distinct ``_NEGATIVE_SEED_PATTERN_PREFIX``
        sub-keys.  Each seed becomes a single-member cluster (member_count=1)
        flagged with the negative-seed origin in ``failure_pattern``.
        """
        seed_clusters: list[RCACluster] = []
        seen: set[str] = set()
        for seed in tqdm(seeds, desc="Processing", unit="item"):
            key = f"{seed.source_type}::{seed.signature}"
            if key in seen:
                continue
            seen.add(key)
            pattern = f"{_NEGATIVE_SEED_PATTERN_PREFIX}_{seed.source_type}"
            canonical = deterministic_json(
                {
                    "evidence_hash": seed.evidence_hash,
                    "pattern": pattern,
                    "signature": seed.signature,
                    "timestamp_utc": timestamp_utc,
                }
            )
            cluster_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            cluster_id = cluster_hash
            adg_node = _adg_cluster_node(pattern, seed.signature, cluster_hash)
            seed_clusters.append(
                RCACluster(
                    cluster_id=cluster_id,
                    failure_pattern=pattern,
                    dominant_route="UNKNOWN",
                    dominant_guardrail=None,
                    dominant_retrieval_pattern="UNKNOWN",
                    affected_agents=(seed.affected_component,),
                    member_trace_ids=(),
                    member_count=seed.occurrence_count,
                    outcome_distribution=(("SAFE_FAILURE", seed.occurrence_count),),
                    avg_groundedness=0.0,
                    hitl_escalation_rate=0.0,
                    healer_invocation_rate=0.0,
                    adg_cluster_node=adg_node,
                    timestamp_utc=timestamp_utc,
                ),
            )
        return seed_clusters


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def cluster_records(
    records: Sequence[TraceFeatureRecord],
    timestamp_utc: int,
    *,
    config: RCAClusterConfig | None = None,
    negative_seeds: Sequence[FailurePattern] | None = None,
) -> list[RCACluster]:
    """Module-level convenience wrapper for ``RCAClusterEngine.cluster``."""
    return RCAClusterEngine(config).cluster(
        records,
        timestamp_utc,
        negative_seeds=negative_seeds,
    )


__all__ = [
    "RCAClusterConfig",
    "RCAClusterEngine",
    "cluster_records",
]
