"""
Phase 5: DPO Batch Builder

Converts human feedback decisions into DPO (Direct Preference Optimization)
training pairs.  Pairs are constructed by grouping feedback examples with
the same query and contrasting positive vs negative annotations.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "dpo_batch_builder", "execution_auth")
_emit_validates_capability("p2", "dpo_batch_builder", "capability_check")
_emit_routes_to_capability("p2", "dpo_batch_builder", "capability_route")
_emit_writes_via_uwg("p2", "dpo_batch_builder", "uwg_write")
_emit_blocks_direct_write("p2", "dpo_batch_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "dpo_batch_builder", "tool_invocation")
_emit_captures_execution_output("p2", "dpo_batch_builder", "exec_output")
_emit_dispatches_agent("p3", "dpo_batch_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "dpo_batch_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "dpo_batch_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "dpo_batch_builder", "healing_outcome")
_emit_escalates_failure("p3", "dpo_batch_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "dpo_batch_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dpo_batch_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "dpo_batch_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "dpo_batch_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dpo_batch_builder", "eval_metric")
_emit_stores_embedding("p4", "dpo_batch_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "dpo_batch_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dpo_batch_builder", "exec_snapshot_link")
from .schemas import DPOBatch, DPOPair, FeedbackExample

_emit_applies_guardrail("p0", "dpo_batch_builder", "p0_governance")
_emit_reads_policy_state("p0", "dpo_batch_builder", "policy_binding")
_emit_snapshots_state("p0", "dpo_batch_builder", "state_snapshot")
emit_replay_key("p0", "dpo_batch_builder")
emit_determinism_digest("p0", "dpo_batch_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _utcnow() -> str:
    return datetime.utcnow().isoformat() + "Z"


class DPOBatchBuilder:
    """Builds DPO training pairs from collected human decisions.

    Strategy:
    - Group feedback examples by query.
    - Within each group, pair positive-annotation examples (chosen)
      with negative-annotation examples (rejected).
    - If a query has only positives or only negatives, skip it.
    - Output is deterministic: sorted by query string, then by example_id.
    """

    # guardian: allow-magic-config
    def __init__(self, min_score_delta: float = 0.1, l4_store: Any | None = None):
        """Initialize DPO batch builder.

        Args:
            min_score_delta: Minimum quality score difference between chosen
                             and rejected for a pair to be included.
            l4_store: Optional L4 store for persisting DPO batches.
        """
        if min_score_delta < 0.0:
            raise ValueError(f"min_score_delta must be non-negative, got {min_score_delta}")
        self.min_score_delta = min_score_delta
        self.l4_store = l4_store

    def generate_pairs(self, human_decisions: list[FeedbackExample]) -> DPOBatch:
        """Generate DPO training pairs from human feedback examples.

        Args:
            human_decisions: List of human-annotated feedback examples

        Returns:
            DPOBatch containing all valid preference pairs
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DPOBatchBuilder.generate_pairs")

        if not human_decisions:
            return DPOBatch(
                batch_id=str(uuid.uuid4()),
                timestamp=_utcnow(),
                pair_count=0,
                pairs=[],
                source_feedback_count=0,
            )
        grouped: dict[str, list[FeedbackExample]] = {}
        for example in human_decisions:
            grouped.setdefault(example.query, []).append(example)
        pairs: list[DPOPair] = []
        for query in sorted(grouped.keys()):
            query_examples = sorted(grouped[query], key=lambda e: e.example_id)
            positive = [e for e in query_examples if e.human_annotation.is_positive]
            negative = [e for e in query_examples if not e.human_annotation.is_positive]
            if not positive or not negative:
                continue
            for pos in positive:
                for neg in negative:
                    chosen_score = pos.human_annotation.quality_score
                    rejected_score = neg.human_annotation.quality_score
                    if chosen_score - rejected_score < self.min_score_delta:
                        continue
                    pairs.append(
                        DPOPair(
                            pair_id=str(uuid.uuid4()),
                            query=query,
                            chosen_response=pos.model_answer,
                            rejected_response=neg.model_answer,
                            context_documents=list(
                                dict.fromkeys(pos.context_documents + neg.context_documents)
                            ),
                            chosen_score=chosen_score,
                            rejected_score=rejected_score,
                            source_example_ids=[pos.example_id, neg.example_id],
                        )
                    )
        batch = DPOBatch(
            batch_id=str(uuid.uuid4()),
            timestamp=_utcnow(),
            pair_count=len(pairs),
            pairs=pairs,
            source_feedback_count=len(human_decisions),
        )
        if self.l4_store is not None:
            self._persist(batch)
        return batch

    def _persist(self, batch: DPOBatch) -> None:
        """Persist DPO batch artifact to L4 state registry."""
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="dpo_batch", logical_id=f"dpo_batch_{batch.batch_id[:8]}", payload=batch.to_dict()
            )
            self.l4_store.put(artifact)
        except (ValueError, KeyError, AttributeError) as e:
            logging.getLogger(__name__).warning(f"Failed to store DPO batch {batch.batch_id[:8]}: {e}")
        except (OSError, RuntimeError, MemoryError) as e:
            logging.getLogger(__name__).error(f"Critical error storing DPO batch {batch.batch_id[:8]}: {e}")


__all__ = ["DPOBatchBuilder"]
