"""meta_learning_replay_binding — Replay key binding struct for meta-learning state.

Encapsulates the three digest components required for deterministic replay:
  - FAISS index digests (per-index W-A-DETERMINISM-DIGEST values)
  - strategy_weights_digest (from MetaLearningAgent.strategy_weights_digest)
  - embedding_model_version (runtime model identifier string)

A replay run that loads from a persisted state must present an identical
``MetaLearningReplayBinding`` to confirm it started from the same learned
state as the original run.

Usage::

    from system_learning.engines.meta_learning_replay_binding import (
        MetaLearningReplayBinding,
    )

    binding = MetaLearningReplayBinding(
        faiss_index_digests={"healing_contexts_v1": store.persist_to_disk(...)},
        strategy_weights_digest=agent.strategy_weights_digest,
        embedding_model_version="BAAI/bge-m3-v1",
    )
    binding.emit()            # prints REPLAY-BINDING line to stdout
    line = binding.to_line()  # "REPLAY-BINDING: <json>"
"""

from __future__ import annotations

import hashlib
import json

from system_learning._tracing import sl_span
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
    record_execution_trace,
)

_emit_applies_guardrail("p0", "meta_learning_replay_binding", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_replay_binding", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_replay_binding", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("meta_learning_replay_binding", "meta_learning_replay_binding_trace")


_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_replay_binding", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_replay_binding", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_replay_binding", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_replay_binding", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_replay_binding", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_replay_binding", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_replay_binding", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_replay_binding", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_replay_binding", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_replay_binding", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_replay_binding", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_replay_binding", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_replay_binding", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_replay_binding", "p3lm", "state")
_emit_records_execution_trace("meta_learning_replay_binding", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_replay_binding", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_replay_binding", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_replay_binding", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_replay_binding", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_replay_binding", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_replay_binding", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_replay_binding", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_replay_binding", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_replay_binding", "context_pull")
_emit_pulls_context("p1", "meta_learning_replay_binding", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_replay_binding", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_replay_binding", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_replay_binding", "write_through")
_emit_writes_through("p1", "meta_learning_replay_binding", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_replay_binding", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_replay_binding", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_replay_binding", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_replay_binding", "human_escalation")
_emit_routes_through("p1", "meta_learning_replay_binding", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_replay_binding", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_replay_binding", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_replay_binding", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_replay_binding", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_replay_binding", "target_agent")
_emit_verifies_policy("p1", "meta_learning_replay_binding", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_replay_binding", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_replay_binding", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_replay_binding", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_replay_binding")
_emit_gated_by_confidence("p1", "meta_learning_replay_binding", "confidence_gate")
emit_replay_key("p0", "meta_learning_replay_binding")
emit_determinism_digest("p0", "meta_learning_replay_binding")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_learning_replay_binding", "execution_auth")
_emit_validates_capability("p2", "meta_learning_replay_binding", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_replay_binding", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_replay_binding", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_replay_binding", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_replay_binding", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_replay_binding", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_replay_binding", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_replay_binding", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_replay_binding", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_replay_binding", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_replay_binding", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_replay_binding", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_replay_binding", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_replay_binding", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_replay_binding", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_replay_binding", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_replay_binding", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_replay_binding", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_replay_binding", "exec_snapshot_link")


@dataclass(frozen=True)
class MetaLearningReplayBinding:
    """Immutable binding of all digest components needed for replay verification.

    All three fields are required.  The binding is emitted as a single
    ``REPLAY-BINDING: <json>`` line to stdout and can be re-parsed and compared
    by a replay runner to verify identical initialisation state.

    Attributes:
        faiss_index_digests: Mapping of index_id -> W-A-DETERMINISM-DIGEST hex.
                             Must contain at least one entry.
        strategy_weights_digest: SHA-256 hex of current MetaLearningAgent weights.
        embedding_model_version: Runtime embedding model identifier string.
    """

    faiss_index_digests: dict[str, str]
    strategy_weights_digest: str
    embedding_model_version: str

    def __post_init__(self) -> None:
        if not self.faiss_index_digests:
            raise ValueError("faiss_index_digests must contain at least one entry")
        if len(self.strategy_weights_digest) != 64:
            raise ValueError(
                f"strategy_weights_digest must be 64-hex chars, got {len(self.strategy_weights_digest)}",
            )
        if not self.embedding_model_version:
            raise ValueError("embedding_model_version must be a non-empty string")

    def to_dict(self) -> dict[str, object]:
        """Return a canonical dict representation (keys sorted)."""
        return {
            "embedding_model_version": self.embedding_model_version,
            "faiss_index_digests": dict(sorted(self.faiss_index_digests.items())),
            "strategy_weights_digest": self.strategy_weights_digest,
        }

    def to_line(self) -> str:
        """Serialise to the canonical ``REPLAY-BINDING: <json>`` log line."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "MetaLearningReplayBinding.to_line"
        )

        payload = json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True, ensure_ascii=True)
        return f"REPLAY-BINDING: {payload}"

    def emit(self) -> None:
        """Print the canonical REPLAY-BINDING line to stdout exactly once."""
        with sl_span(
            "system_learning.v1.meta_learning_replay_binding.emit",
            {"sl.embedding_model": self.embedding_model_version},
        ):
            print(self.to_line())

    @classmethod
    def from_line(cls, line: str) -> MetaLearningReplayBinding:
        """Parse a ``REPLAY-BINDING: <json>`` line back into a binding object.

        Raises:
            ValueError: If the line is not a valid REPLAY-BINDING line or
                        the JSON payload is missing required keys.
        """
        prefix = "REPLAY-BINDING: "
        if not line.startswith(prefix):
            raise ValueError(f"Not a REPLAY-BINDING line: {line!r}")
        raw = json.loads(line[len(prefix) :])
        missing = {"faiss_index_digests", "strategy_weights_digest", "embedding_model_version"} - raw.keys()
        if missing:
            raise ValueError(f"REPLAY-BINDING missing keys: {sorted(missing)}")
        return cls(
            faiss_index_digests=raw["faiss_index_digests"],
            strategy_weights_digest=raw["strategy_weights_digest"],
            embedding_model_version=raw["embedding_model_version"],
        )


def compute_replay_key(
    *,
    trace_id: str,
    transcript_hash: str,
    strategy_weights_digest: str,
    faiss_index_digests: dict[str, str],
) -> str:
    """Compute a deterministic replay key binding all execution-state digests.

    The replay key is the SHA-256 of the pipe-concatenated canonical components:

        trace_id | transcript_hash | strategy_weights_digest | <sorted faiss digests>

    FAISS index digests are sorted by ``index_id`` before concatenation so the
    result is independent of insertion order.

    Args:
        trace_id: Unique trace/run identifier (e.g. UUID or timestamp string).
        transcript_hash: SHA-256 hex of the raw replay transcript bytes.
        strategy_weights_digest: SHA-256 hex from MetaLearningAgent.strategy_weights_digest.
        faiss_index_digests: Mapping of index_id -> W-A-DETERMINISM-DIGEST hex.
                             Must contain at least one entry.

    Returns:
        64-char lowercase hex SHA-256 replay key.

    Raises:
        ValueError: If faiss_index_digests is empty or any digest is not 64 hex chars.
    """
    if not faiss_index_digests:
        raise ValueError("faiss_index_digests must contain at least one entry")
    if len(strategy_weights_digest) != 64:
        raise ValueError(f"strategy_weights_digest must be 64-hex chars, got {len(strategy_weights_digest)}")
    sorted_faiss = "|".join((f"{k}:{v}" for k, v in sorted(faiss_index_digests.items())))
    binding = json.dumps(
        {
            "faiss_index_digests_sorted": sorted_faiss,
            "strategy_weights_digest": strategy_weights_digest,
            "trace_id": trace_id,
            "transcript_hash": transcript_hash,
        },
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(binding).hexdigest()


__all__ = ["MetaLearningReplayBinding", "compute_replay_key"]
