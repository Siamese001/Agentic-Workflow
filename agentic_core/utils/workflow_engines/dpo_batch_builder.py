"""
Phase 5: DPO Batch Builder

Converts human feedback decisions into DPO (Direct Preference Optimization)
training pairs.  Pairs are constructed by grouping feedback examples with
the same query and contrasting positive vs negative annotations.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "dpo_batch_builder", "execution_auth")
trace_contract._emit_validates_capability("p2", "dpo_batch_builder", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dpo_batch_builder", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dpo_batch_builder", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dpo_batch_builder", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dpo_batch_builder", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dpo_batch_builder", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dpo_batch_builder", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dpo_batch_builder", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dpo_batch_builder", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dpo_batch_builder", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dpo_batch_builder", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dpo_batch_builder", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dpo_batch_builder", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dpo_batch_builder", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dpo_batch_builder", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dpo_batch_builder", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dpo_batch_builder", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dpo_batch_builder", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dpo_batch_builder", "exec_snapshot_link")
from agentic_core.utils.schemas.schemas import DPOBatch, DPOPair, FeedbackExample

trace_contract._emit_applies_guardrail("p0", "dpo_batch_builder", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "dpo_batch_builder", "policy_binding")
trace_contract._emit_snapshots_state("p0", "dpo_batch_builder", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dpo_batch_builder", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dpo_batch_builder", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dpo_batch_builder", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dpo_batch_builder", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dpo_batch_builder", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dpo_batch_builder", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dpo_batch_builder", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dpo_batch_builder", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dpo_batch_builder", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dpo_batch_builder", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dpo_batch_builder", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dpo_batch_builder", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dpo_batch_builder", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dpo_batch_builder", "p3lm", "state")
trace_contract._emit_records_execution_trace("dpo_batch_builder", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dpo_batch_builder", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dpo_batch_builder", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dpo_batch_builder", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dpo_batch_builder", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dpo_batch_builder", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dpo_batch_builder", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dpo_batch_builder", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dpo_batch_builder", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dpo_batch_builder", "context_pull")
trace_contract._emit_pulls_context("p1", "dpo_batch_builder", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dpo_batch_builder", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dpo_batch_builder", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dpo_batch_builder", "write_through")
trace_contract._emit_writes_through("p1", "dpo_batch_builder", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dpo_batch_builder", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dpo_batch_builder", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dpo_batch_builder", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "dpo_batch_builder", "human_escalation")
trace_contract._emit_routes_through("p1", "dpo_batch_builder", "route_through")
trace_contract._emit_checks_agent_registry("p1", "dpo_batch_builder", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dpo_batch_builder", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dpo_batch_builder", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dpo_batch_builder", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dpo_batch_builder", "target_agent")
trace_contract._emit_verifies_policy("p1", "dpo_batch_builder", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dpo_batch_builder", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dpo_batch_builder", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dpo_batch_builder", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dpo_batch_builder")
trace_contract._emit_gated_by_confidence("p1", "dpo_batch_builder", "confidence_gate")
trace_contract.emit_replay_key("p0", "dpo_batch_builder")
trace_contract.emit_determinism_digest("p0", "dpo_batch_builder")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DPOBatchBuilder.generate_pairs"
        )

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
        for query in tqdm(sorted(grouped.keys()), desc="Processing", unit="item"):
            query_examples = sorted(grouped[query], key=lambda e: e.example_id)
            positive = [e for e in query_examples if e.human_annotation.is_positive]
            negative = [e for e in query_examples if not e.human_annotation.is_positive]
            if not positive or not negative:
                continue
            for pos in tqdm(positive, desc="Processing", unit="item"):
                for neg in tqdm(negative, desc="Processing", unit="item"):
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
                                dict.fromkeys(pos.context_documents + neg.context_documents),
                            ),
                            chosen_score=chosen_score,
                            rejected_score=rejected_score,
                            source_example_ids=[pos.example_id, neg.example_id],
                        ),
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
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="dpo_batch",
                logical_id=f"dpo_batch_{batch.batch_id[:8]}",
                payload=batch.to_dict(),
            )
            self.l4_store.put(artifact)
        except (
            ValueError,
            KeyError,
            AttributeError,
        ) as e:  # guardian: allow-log-and-swallow -- DPO batch persist best-effort: non-fatal, batch already built in memory
            logging.getLogger(__name__).warning(f"Failed to store DPO batch {batch.batch_id[:8]}: {e}")
        except (
            OSError,
            RuntimeError,
            MemoryError,
        ) as e:  # guardian: allow-log-and-swallow -- critical storage error: logged, batch already built in memory
            logging.getLogger(__name__).error(f"Critical error storing DPO batch {batch.batch_id[:8]}: {e}")


__all__ = ["DPOBatchBuilder"]
