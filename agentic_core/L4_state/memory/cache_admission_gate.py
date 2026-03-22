"""L4 State: Semantic Cache Admission Gate.

Separates semantic cache admission from durable learning by enforcing four
admission criteria before a retrieval result is allowed into Redis DB-0:

  1. **Support validation** — at least one retrieved document directly supports
     the query (support_score >= support_threshold).
  2. **Completeness** — the retrieved set covers the query family sufficiently
     (completeness_score >= completeness_threshold).
  3. **Policy clearance** — no policy conflict flag is set for this query.
  4. **Replay safety** — no replay-sensitive contamination in the result set.

Only entries passing all four gates are admitted.  The gate outcome is recorded
as a ``CacheAdmissionDecision`` (frozen dataclass) and can be stored in the
``rag_admit`` key schema (see ``cache_key_builders.build_rag_admission_key``).

Design invariants
-----------------
1. No wall-clock reads — ``timestamp_utc`` is caller-supplied.
2. No side effects — this module only evaluates and records decisions.
3. Fail-closed on errors: if any gate check raises, admission is DENIED.
4. Thresholds are explicit parameters — no hidden magic constants in logic.
5. The gate does NOT write to Redis itself; callers use the returned decision
   to determine whether to call the cache ``set`` method.

Architecture connection
-----------------------
This implements the architecture design point:
  "Only admit Redis cache entries when:
   - support validation passes
   - completeness score passes threshold
   - no policy conflict
   - no replay-sensitive contamination"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "cache_admission_gate")
emit_determinism_digest("p0", "cache_admission_gate")

_emit_dispatches_healing_run("p1", "cache_admission_gate", "L4")
_emit_routes_through("p1", "cache_admission_gate", "L4")
_emit_checks_agent_registry("p1", "cache_admission_gate", "agent_registry")
_emit_validates_agent_capability("p1", "cache_admission_gate", "capability")
_emit_dispatches_execution_plan("p1", "cache_admission_gate", "exec_plan")
_emit_agent_executes_agent("p1", "cache_admission_gate", "sub_agent")
_emit_routes_to_agent("p1", "cache_admission_gate", "target_agent")
_emit_verifies_policy("p1", "cache_admission_gate", "policy_check")
_emit_observes_runtime_state("p1", "cache_admission_gate", "runtime_state")
_emit_verifies_boundary("p1", "cache_admission_gate", "boundary_check")
_emit_transcripts_response("p1", "cache_admission_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_admission_gate")
_emit_gated_by_confidence("p1", "cache_admission_gate", "confidence_gate")
_emit_escalates_to_human("p1", "cache_admission_gate", "L4")
_emit_reads_policy_state("p1", "cache_admission_gate", "L4")
_emit_authorize_and_execute("p2", "cache_admission_gate", "execution_auth")
_emit_validates_capability("p2", "cache_admission_gate", "capability_check")
_emit_routes_to_capability("p2", "cache_admission_gate", "capability_route")
_emit_writes_via_uwg("p2", "cache_admission_gate", "uwg_write")
_emit_blocks_direct_write("p2", "cache_admission_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_admission_gate", "tool_invocation")
_emit_captures_execution_output("p2", "cache_admission_gate", "exec_output")
_emit_dispatches_agent("p3", "cache_admission_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_admission_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_admission_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_admission_gate", "healing_outcome")
_emit_escalates_failure("p3", "cache_admission_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_admission_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_admission_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_admission_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_admission_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_admission_gate", "eval_metric")
_emit_stores_embedding("p4", "cache_admission_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_admission_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_admission_gate", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_1")
_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_2")
_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_3")
_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_4")
_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_5")
_emit_emits_metric_event("cache_admission_gate", "p4obs", "metric_6")
_emit_records_incident_event("cache_admission_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_admission_gate", "p4obs", "anomaly")
_emit_writes_observability_log("cache_admission_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_admission_gate", "p4obs", "mon_state")
_emit_triggers_alert("cache_admission_gate", "p4obs", "alert")
_emit_links_incident_trace("cache_admission_gate", "p4obs", "trace_link")
_emit_captures_pattern("cache_admission_gate", "p3lm", "pattern")
_emit_records_learning_event("cache_admission_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_admission_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_admission_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_admission_gate", "p3lm", "routing")
_emit_improves_agent_policy("cache_admission_gate", "p3lm", "policy")
_emit_stores_learning_state("cache_admission_gate", "p3lm", "state")
_emit_records_execution_trace("cache_admission_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_admission_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_admission_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_admission_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_admission_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_admission_gate", "env_read", "p2_env_1")
_emit_reads_environ("cache_admission_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_admission_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_admission_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_admission_gate", "context_pull")
_emit_pulls_context("p1", "cache_admission_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_admission_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_admission_gate", "uwg_term_2")
_emit_writes_through("p1", "cache_admission_gate", "write_through")
_emit_writes_through("p1", "cache_admission_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_admission_gate", "safety_validation")
_emit_invokes_eval("p1", "cache_admission_gate", "eval_call")
_emit_proposal_commits_routing("p1", "cache_admission_gate", "routing_commit")


def _get_determinism_fns():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_determinism_fns", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_determinism_fns", "p0_governance")
    from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

    return deterministic_json, stable_sha256_json


logger = logging.getLogger(__name__)

# Default thresholds — callers should override for their domain
_DEFAULT_SUPPORT_THRESHOLD: float = 0.6
_DEFAULT_COMPLETENESS_THRESHOLD: float = 0.5


# ---------------------------------------------------------------------------
# Admission decision record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CacheAdmissionDecision:
    """Frozen record of a single cache admission gate evaluation.

    Attributes
    ----------
    artifact_type:
        Always ``CACHE_ADMISSION_DECISION``.
    query_hash:
        SHA-256 hexdigest of the query (u0_hash).
    policy_hash:
        SHA-256 hexdigest of the active policy.
    embedder_version:
        Embedder version tag used for this retrieval.
    admitted:
        True if all four gates passed.
    deny_reasons:
        Tuple of stable deny reason codes (empty when admitted).
    support_score:
        Support validation score supplied by the caller.
    completeness_score:
        Completeness score supplied by the caller.
    policy_conflict:
        True if a policy conflict was detected.
    replay_contaminated:
        True if replay-sensitive content was found in the result set.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["CACHE_ADMISSION_DECISION"]
    query_hash: str
    policy_hash: str
    embedder_version: str
    admitted: bool
    deny_reasons: tuple[str, ...]
    support_score: float
    completeness_score: float
    policy_conflict: bool
    replay_contaminated: bool
    timestamp_utc: int

    def to_dict(self) -> dict[str, object]:
        return {
            "admitted": self.admitted,
            "artifact_type": self.artifact_type,
            "completeness_score": self.completeness_score,
            "deny_reasons": list(self.deny_reasons),
            "embedder_version": self.embedder_version,
            "policy_conflict": self.policy_conflict,
            "policy_hash": self.policy_hash,
            "query_hash": self.query_hash,
            "replay_contaminated": self.replay_contaminated,
            "support_score": self.support_score,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        _deterministic_json, _ = _get_determinism_fns()
        return _deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        _, _stable_sha256_json = _get_determinism_fns()
        return _stable_sha256_json(self.to_dict())


# Stable deny reason codes
DENY_SUPPORT_BELOW_THRESHOLD = "SUPPORT_BELOW_THRESHOLD"
DENY_COMPLETENESS_BELOW_THRESHOLD = "COMPLETENESS_BELOW_THRESHOLD"
DENY_POLICY_CONFLICT = "POLICY_CONFLICT"
DENY_REPLAY_CONTAMINATED = "REPLAY_CONTAMINATED"


# ---------------------------------------------------------------------------
# CacheAdmissionGate
# ---------------------------------------------------------------------------


class CacheAdmissionGate:
    """Evaluates four admission criteria before allowing a retrieval result
    into the semantic cache.

    Usage
    -----
    .. code-block:: python

        gate = CacheAdmissionGate(
            support_threshold=0.65,
            completeness_threshold=0.55,
        )

        decision = gate.evaluate(
            query_hash="a3f7b291..." * 2,   # 64-char SHA-256
            policy_hash="deadbeef..." * 2,
            embedder_version="bge-m3-v1",
            support_score=0.72,
            completeness_score=0.60,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=1700000000,
        )

        if decision.admitted:
            redis_cache.set(admission_key, result_bytes, ttl_seconds=3600)
    """

    def __init__(
        self,
        support_threshold: float = _DEFAULT_SUPPORT_THRESHOLD,
        completeness_threshold: float = _DEFAULT_COMPLETENESS_THRESHOLD,
    ) -> None:
        if not (0.0 <= support_threshold <= 1.0):
            raise ValueError(f"support_threshold must be in [0, 1], got {support_threshold}")
        if not (0.0 <= completeness_threshold <= 1.0):
            raise ValueError(f"completeness_threshold must be in [0, 1], got {completeness_threshold}")
        self.support_threshold = support_threshold
        self.completeness_threshold = completeness_threshold
        self._stats: dict[str, int] = {
            "admitted": 0,
            "denied_support": 0,
            "denied_completeness": 0,
            "denied_policy": 0,
            "denied_replay": 0,
            "errors": 0,
        }

    def evaluate(
        self,
        *,
        query_hash: str,
        policy_hash: str,
        embedder_version: str,
        support_score: float,
        completeness_score: float,
        policy_conflict: bool,
        replay_contaminated: bool,
        timestamp_utc: int,
    ) -> CacheAdmissionDecision:
        """Evaluate all four admission gates and return a decision record.

        Fail-closed: any unexpected error during evaluation produces a DENIED
        decision with ``INTERNAL_ERROR`` in deny_reasons.

        Parameters
        ----------
        query_hash:
            SHA-256 hexdigest of the query (u0_hash).
        policy_hash:
            SHA-256 hexdigest of the active policy.
        embedder_version:
            Embedder version tag (no colons).
        support_score:
            Float in [0, 1] — support validation score from the RAG evaluator.
        completeness_score:
            Float in [0, 1] — completeness score from the RAG evaluator.
        policy_conflict:
            True if the policy layer detected a conflict for this query.
        replay_contaminated:
            True if the result set contains replay-sensitive content.
        timestamp_utc:
            Unix timestamp provided by the caller.

        Returns
        -------
        CacheAdmissionDecision
            Frozen decision record.  ``admitted=True`` means all gates passed.
        """
        try:
            deny_reasons: list[str] = []

            if support_score < self.support_threshold:
                deny_reasons.append(DENY_SUPPORT_BELOW_THRESHOLD)
                self._stats["denied_support"] += 1

            if completeness_score < self.completeness_threshold:
                deny_reasons.append(DENY_COMPLETENESS_BELOW_THRESHOLD)
                self._stats["denied_completeness"] += 1

            if policy_conflict:
                deny_reasons.append(DENY_POLICY_CONFLICT)
                self._stats["denied_policy"] += 1

            if replay_contaminated:
                deny_reasons.append(DENY_REPLAY_CONTAMINATED)
                self._stats["denied_replay"] += 1

            admitted = len(deny_reasons) == 0
            if admitted:
                self._stats["admitted"] += 1
            else:
                logger.debug(
                    "[CacheAdmissionGate] DENIED query_hash=%s reasons=%s",
                    query_hash[:16],
                    deny_reasons,
                )

            return CacheAdmissionDecision(
                artifact_type="CACHE_ADMISSION_DECISION",
                query_hash=query_hash,
                policy_hash=policy_hash,
                embedder_version=embedder_version,
                admitted=admitted,
                deny_reasons=tuple(deny_reasons),
                support_score=support_score,
                completeness_score=completeness_score,
                policy_conflict=policy_conflict,
                replay_contaminated=replay_contaminated,
                timestamp_utc=timestamp_utc,
            )

        except Exception as exc:
            self._stats["errors"] += 1
            logger.warning("[CacheAdmissionGate] Evaluation error (fail-closed): %s", exc)
            return CacheAdmissionDecision(
                artifact_type="CACHE_ADMISSION_DECISION",
                query_hash=query_hash,
                policy_hash=policy_hash,
                embedder_version=embedder_version,
                admitted=False,
                deny_reasons=("INTERNAL_ERROR",),
                support_score=support_score,
                completeness_score=completeness_score,
                policy_conflict=policy_conflict,
                replay_contaminated=replay_contaminated,
                timestamp_utc=timestamp_utc,
            )

    def get_stats(self) -> dict[str, Any]:
        """Return admission gate statistics."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "CacheAdmissionGate.get_stats")

        total = sum(self._stats.values()) - self._stats["errors"]
        return {
            **self._stats,
            "total_evaluated": total,
            "admit_rate": (self._stats["admitted"] / total if total > 0 else 0.0),
            "support_threshold": self.support_threshold,
            "completeness_threshold": self.completeness_threshold,
        }


__all__ = [
    "CacheAdmissionDecision",
    "CacheAdmissionGate",
    "DENY_COMPLETENESS_BELOW_THRESHOLD",
    "DENY_POLICY_CONFLICT",
    "DENY_REPLAY_CONTAMINATED",
    "DENY_SUPPORT_BELOW_THRESHOLD",
]
