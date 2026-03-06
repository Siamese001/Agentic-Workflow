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

from .schemas import DPOBatch, DPOPair, FeedbackExample


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

    def __init__(
        self,
        min_score_delta: float = 0.1,
        l4_store: Any | None = None,
    ):
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
                                dict.fromkeys(
                                    pos.context_documents + neg.context_documents
                                )
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
                kind="dpo_batch",
                logical_id=f"dpo_batch_{batch.batch_id[:8]}",
                payload=batch.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:
            pass


__all__ = ["DPOBatchBuilder"]
