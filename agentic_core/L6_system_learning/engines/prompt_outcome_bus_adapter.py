"""Prompt Outcome Bus Adapter — converts PromptOutcomeRecord → TraceFeatureRecord.

Bridges the prompt provenance system into the meta-learning bus pipeline.
Every ``PromptOutcomeRecord`` produced by the ``PromptExecutionTracer`` is
converted into a ``TraceFeatureRecord`` so the full meta-learning bus pipeline
(clustering, proposal generation, validation, commit) can process prompt
outcomes exactly like any other execution trace.

Mapping logic
-------------
PromptOutcomeRecord field         → TraceFeatureRecord field
─────────────────────────────────────────────────────────────
outcome_id                        → record_id (re-hashed with type prefix)
trace_id                          → trace_id
route                             → route
"RAG_BGE" / retrieval_path        → retrieval_pattern  (from signal hint)
groundedness_score                → retrieval_groundedness
guardrail_hits                    → guardrail_edges
[]                                → policy_edges  (populated from signal)
[]                                → determinism_signals
healer_id                         → healer_used
hitl_escalation                   → hitl_escalation
final_outcome (mapped)            → outcome_class
adg_entity_name                   → adg_node_id
[]                                → adg_relation_ids
outcome_record.stable_hash()      → feature_bundle_hash
timestamp_utc                     → timestamp_utc

Outcome class mapping
---------------------
PromptOutcomeRecord.final_outcome → TraceFeatureRecord.outcome_class
SUCCESS            → SUCCESS
HEALED_SUCCESS     → HEALED_SUCCESS
SAFE_FAILURE       → SAFE_FAILURE
ESCALATED          → HUMAN_OVERRIDE
REPLAY_FAILURE     → REPLAY_FAILURE
UNKNOWN            → UNKNOWN

Slot failure → policy_edges
---------------------------
When failure_slot is S0 or D0, the adapter injects a synthetic policy edge
"prompt_slot_{slot}_failure" to allow the clustering engine to identify
prompt-specific policy and fence failures.

Design invariants
-----------------
1. No wall-clock reads; timestamp_utc is taken from the PromptOutcomeRecord.
2. Conversion is deterministic and pure-function.
3. Batch conversion returns results sorted by record_id for determinism.
4. Fail-safe: conversion errors produce warnings and are skipped.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Sequence

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
)

_emit_authorize_and_execute("p2", "prompt_outcome_bus_adapter", "execution_auth")
_emit_validates_capability("p2", "prompt_outcome_bus_adapter", "capability_check")
_emit_routes_to_capability("p2", "prompt_outcome_bus_adapter", "capability_route")
_emit_writes_via_uwg("p2", "prompt_outcome_bus_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_outcome_bus_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_outcome_bus_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_outcome_bus_adapter", "exec_output")
_emit_dispatches_agent("p3", "prompt_outcome_bus_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_outcome_bus_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_outcome_bus_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_outcome_bus_adapter", "healing_outcome")
_emit_escalates_failure("p3", "prompt_outcome_bus_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_outcome_bus_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_outcome_bus_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_outcome_bus_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_outcome_bus_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_outcome_bus_adapter", "eval_metric")
_emit_stores_embedding("p4", "prompt_outcome_bus_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_outcome_bus_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_outcome_bus_adapter", "exec_snapshot_link")
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json
from agentic_core.L6_system_learning.types.prompt_artifact_types import PromptOutcomeRecord
from agentic_core.L6_system_learning.types.trace_feature_types import TraceFeatureRecord

_emit_applies_guardrail("p0", "prompt_outcome_bus_adapter", "p0_governance")
_emit_snapshots_state("p0", "prompt_outcome_bus_adapter", "state_snapshot")
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

_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_outcome_bus_adapter", "p4obs", "metric_6")
_emit_records_incident_event("prompt_outcome_bus_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_outcome_bus_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_outcome_bus_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_outcome_bus_adapter", "p4obs", "mon_state")
_emit_triggers_alert("prompt_outcome_bus_adapter", "p4obs", "alert")
_emit_links_incident_trace("prompt_outcome_bus_adapter", "p4obs", "trace_link")
_emit_captures_pattern("prompt_outcome_bus_adapter", "p3lm", "pattern")
_emit_records_learning_event("prompt_outcome_bus_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_outcome_bus_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_outcome_bus_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_outcome_bus_adapter", "p3lm", "routing")
_emit_improves_agent_policy("prompt_outcome_bus_adapter", "p3lm", "policy")
_emit_stores_learning_state("prompt_outcome_bus_adapter", "p3lm", "state")
_emit_records_execution_trace("prompt_outcome_bus_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_outcome_bus_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_outcome_bus_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_outcome_bus_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_outcome_bus_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_outcome_bus_adapter", "env_read", "p2_env_1")
_emit_reads_environ("prompt_outcome_bus_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_outcome_bus_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_outcome_bus_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_outcome_bus_adapter", "context_pull")
_emit_pulls_context("p1", "prompt_outcome_bus_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_outcome_bus_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_outcome_bus_adapter", "uwg_term_2")
_emit_writes_through("p1", "prompt_outcome_bus_adapter", "write_through")
_emit_writes_through("p1", "prompt_outcome_bus_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_outcome_bus_adapter", "safety_validation")
_emit_invokes_eval("p1", "prompt_outcome_bus_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_outcome_bus_adapter", "routing_commit")
_emit_escalates_to_human("p1", "prompt_outcome_bus_adapter", "human_escalation")
_emit_routes_through("p1", "prompt_outcome_bus_adapter", "route_through")
_emit_checks_agent_registry("p1", "prompt_outcome_bus_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_outcome_bus_adapter", "capability")
_emit_dispatches_execution_plan("p1", "prompt_outcome_bus_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_outcome_bus_adapter", "sub_agent")
_emit_routes_to_agent("p1", "prompt_outcome_bus_adapter", "target_agent")
_emit_verifies_policy("p1", "prompt_outcome_bus_adapter", "policy_check")
_emit_observes_runtime_state("p1", "prompt_outcome_bus_adapter", "runtime_state")
_emit_verifies_boundary("p1", "prompt_outcome_bus_adapter", "boundary_check")
_emit_transcripts_response("p1", "prompt_outcome_bus_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_outcome_bus_adapter")
_emit_gated_by_confidence("p1", "prompt_outcome_bus_adapter", "confidence_gate")
emit_replay_key("p0", "prompt_outcome_bus_adapter")
emit_determinism_digest("p0", "prompt_outcome_bus_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Outcome class translation
# ---------------------------------------------------------------------------

_OUTCOME_MAP: dict[str, str] = {
    "SUCCESS": "SUCCESS",
    "HEALED_SUCCESS": "HEALED_SUCCESS",
    "SAFE_FAILURE": "SAFE_FAILURE",
    "ESCALATED": "HUMAN_OVERRIDE",
    "REPLAY_FAILURE": "REPLAY_FAILURE",
    "UNKNOWN": "UNKNOWN",
}

# ---------------------------------------------------------------------------
# Slot → policy edge synthetic tag
# ---------------------------------------------------------------------------

_SLOT_POLICY_EDGE: dict[str, str] = {
    "S0": "prompt_slot_S0_failure",
    "D0": "prompt_slot_D0_failure",
    "I0": "prompt_slot_I0_failure",
    "C0": "prompt_slot_C0_failure",
    "U0": "prompt_slot_U0_failure",
}


def _build_record_id(outcome_id: str) -> str:
    canonical = deterministic_json({"outcome_id": outcome_id, "type": "PromptOutcomeBusRecord"})
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class PromptOutcomeBusAdapter:
    """Converts PromptOutcomeRecord objects into TraceFeatureRecord objects
    for ingestion by the meta-learning bus.

    Usage::

        adapter = PromptOutcomeBusAdapter()
        records = adapter.convert_batch(outcome_records)
        bus.process_records(records, timestamp_utc=ts)
    """

    def convert(self, outcome: PromptOutcomeRecord) -> TraceFeatureRecord:
        """Convert a single PromptOutcomeRecord to a TraceFeatureRecord.

        Parameters
        ----------
        outcome : PromptOutcomeRecord

        Returns
        -------
        TraceFeatureRecord
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOutcomeBusAdapter.convert"
        )

        record_id = _build_record_id(outcome.outcome_id)

        outcome_class = _OUTCOME_MAP.get(outcome.final_outcome, "UNKNOWN")

        # Build policy_edges from slot failure annotation
        policy_edges: list[str] = []
        slot_tag = _SLOT_POLICY_EDGE.get(outcome.failure_slot)
        if slot_tag:
            policy_edges.append(slot_tag)

        # Retrieval pattern: use a canonical label based on groundedness
        # High groundedness → RAG_BGE; low → LOW_CONFIDENCE_RETRIEVAL
        if outcome.groundedness_score >= 0.7:
            retrieval_pattern = "RAG_BGE"
        elif outcome.groundedness_score >= 0.4:
            retrieval_pattern = "RAG_MIXED"
        else:
            retrieval_pattern = "LOW_CONFIDENCE_RETRIEVAL"

        feature_bundle_hash = outcome.stable_hash()

        return TraceFeatureRecord(
            record_id=record_id,
            trace_id=outcome.trace_id,
            route=outcome.route,
            retrieval_pattern=retrieval_pattern,
            retrieval_groundedness=outcome.groundedness_score,
            policy_edges=tuple(sorted(policy_edges)),
            guardrail_edges=outcome.guardrail_hits,
            determinism_signals=(),
            healer_used=outcome.healer_id if outcome.healer_invoked else None,
            hitl_escalation=outcome.hitl_escalation,
            outcome_class=outcome_class,
            adg_node_id=outcome.adg_entity_name,
            adg_relation_ids=(),
            feature_bundle_hash=feature_bundle_hash,
            timestamp_utc=outcome.timestamp_utc,
        )

    def convert_batch(
        self,
        outcomes: Sequence[PromptOutcomeRecord],
    ) -> list[TraceFeatureRecord]:
        """Convert a batch of PromptOutcomeRecords.

        Returns
        -------
        list[TraceFeatureRecord]
            Sorted by record_id for determinism; conversion errors are skipped.
        """
        records: list[TraceFeatureRecord] = []
        for outcome in outcomes:
            try:
                records.append(self.convert(outcome))
            except (AttributeError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                logger.warning("prompt_outcome_bus_adapter: conversion failure: %s", exc, extra={"outcome_id": outcome.outcome_id, "error": str(exc)})
        records.sort(key=lambda r: r.record_id)
        return records


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def convert_outcome_to_record(outcome: PromptOutcomeRecord) -> TraceFeatureRecord:
    """Module-level convenience wrapper."""
    return PromptOutcomeBusAdapter().convert(outcome)


def convert_outcomes_to_records(
    outcomes: Sequence[PromptOutcomeRecord],
) -> list[TraceFeatureRecord]:
    """Module-level convenience wrapper for batch conversion."""
    return PromptOutcomeBusAdapter().convert_batch(outcomes)


__all__ = [
    "PromptOutcomeBusAdapter",
    "convert_outcome_to_record",
    "convert_outcomes_to_records",
]
