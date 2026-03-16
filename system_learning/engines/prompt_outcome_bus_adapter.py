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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_artifact_types import PromptOutcomeRecord
from system_learning.types.trace_feature_types import TraceFeatureRecord

_emit_applies_guardrail("p0", "prompt_outcome_bus_adapter", "p0_governance")
_emit_snapshots_state("p0", "prompt_outcome_bus_adapter", "state_snapshot")
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOutcomeBusAdapter.convert")

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
            except Exception as exc:
                logger.warning(
                    "prompt_outcome_bus_adapter: conversion failed",
                    extra={"outcome_id": outcome.outcome_id, "error": str(exc)},
                )
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
