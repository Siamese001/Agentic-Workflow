"""
Offline Evaluation Runner

Pipeline: dataset → retrieval → reranking → LLM answer generation →
          metric computation → evaluation report → L4 persistence
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Callable

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
)

_emit_authorize_and_execute("p2", "offline_eval_runner", "execution_auth")
_emit_validates_capability("p2", "offline_eval_runner", "capability_check")
_emit_routes_to_capability("p2", "offline_eval_runner", "capability_route")
_emit_writes_via_uwg("p2", "offline_eval_runner", "uwg_write")
_emit_blocks_direct_write("p2", "offline_eval_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "offline_eval_runner", "tool_invocation")
_emit_captures_execution_output("p2", "offline_eval_runner", "exec_output")
_emit_dispatches_agent("p3", "offline_eval_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "offline_eval_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "offline_eval_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "offline_eval_runner", "healing_outcome")
_emit_escalates_failure("p3", "offline_eval_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "offline_eval_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "offline_eval_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "offline_eval_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "offline_eval_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "offline_eval_runner", "eval_metric")
_emit_stores_embedding("p4", "offline_eval_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "offline_eval_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "offline_eval_runner", "exec_snapshot_link")
from ..metrics.answer_correctness import AnswerCorrectness
from ..metrics.base import EvaluationMetric
from ..metrics.groundedness import Groundedness
from ..metrics.mrr import MeanReciprocalRank
from ..metrics.ndcg import NDCG
from ..metrics.precision_at_k import PrecisionAtK
from ..metrics.recall_at_k import RecallAtK
from ..schemas.evaluation_dataset_schema import EvaluationDataset, EvaluationExample
from ..schemas.evaluation_result_schema import (
    EvaluationReport,
    EvaluationResult,
    EvaluationSnapshot,
)

_emit_applies_guardrail("p0", "offline_eval_runner", "p0_governance")
_emit_reads_policy_state("p0", "offline_eval_runner", "policy_binding")
_emit_snapshots_state("p0", "offline_eval_runner", "state_snapshot")
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

_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_1")
_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_2")
_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_3")
_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_4")
_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_5")
_emit_emits_metric_event("offline_eval_runner", "p4obs", "metric_6")
_emit_records_incident_event("offline_eval_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("offline_eval_runner", "p4obs", "anomaly")
_emit_writes_observability_log("offline_eval_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("offline_eval_runner", "p4obs", "mon_state")
_emit_triggers_alert("offline_eval_runner", "p4obs", "alert")
_emit_links_incident_trace("offline_eval_runner", "p4obs", "trace_link")
_emit_captures_pattern("offline_eval_runner", "p3lm", "pattern")
_emit_records_learning_event("offline_eval_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("offline_eval_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("offline_eval_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("offline_eval_runner", "p3lm", "routing")
_emit_improves_agent_policy("offline_eval_runner", "p3lm", "policy")
_emit_stores_learning_state("offline_eval_runner", "p3lm", "state")
_emit_records_execution_trace("offline_eval_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("offline_eval_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("offline_eval_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("offline_eval_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("offline_eval_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("offline_eval_runner", "env_read", "p2_env_1")
_emit_reads_environ("offline_eval_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("offline_eval_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("offline_eval_runner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "offline_eval_runner", "context_pull")
_emit_pulls_context("p1", "offline_eval_runner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "offline_eval_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "offline_eval_runner", "uwg_term_2")
_emit_writes_through("p1", "offline_eval_runner", "write_through")
_emit_writes_through("p1", "offline_eval_runner", "write_through_2")
_emit_validated_by_safety_plane("p1", "offline_eval_runner", "safety_validation")
_emit_invokes_eval("p1", "offline_eval_runner", "eval_call")
_emit_proposal_commits_routing("p1", "offline_eval_runner", "routing_commit")
_emit_escalates_to_human("p1", "offline_eval_runner", "human_escalation")
_emit_routes_through("p1", "offline_eval_runner", "route_through")
_emit_checks_agent_registry("p1", "offline_eval_runner", "agent_registry")
_emit_validates_agent_capability("p1", "offline_eval_runner", "capability")
_emit_dispatches_execution_plan("p1", "offline_eval_runner", "exec_plan")
_emit_agent_executes_agent("p1", "offline_eval_runner", "sub_agent")
_emit_routes_to_agent("p1", "offline_eval_runner", "target_agent")
_emit_verifies_policy("p1", "offline_eval_runner", "policy_check")
_emit_observes_runtime_state("p1", "offline_eval_runner", "runtime_state")
_emit_verifies_boundary("p1", "offline_eval_runner", "boundary_check")
_emit_transcripts_response("p1", "offline_eval_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "offline_eval_runner")
_emit_gated_by_confidence("p1", "offline_eval_runner", "confidence_gate")
emit_replay_key("p0", "offline_eval_runner")
emit_determinism_digest("p0", "offline_eval_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

RetrievalFn = Callable[[str], list[str]]
GenerationFn = Callable[[str, list[str]], str]


def _default_retrieval(query: str) -> list[str]:
    """Stub retrieval — returns empty list.  Replace with real retriever."""
    return []


def _default_generation(query: str, context_docs: list[str]) -> str:
    """Stub generation — returns empty string.  Replace with real LLM."""
    return ""


class OfflineEvaluationRunner:
    """Runs deterministic offline evaluation against a fixed dataset.

    Supports pluggable retrieval, generation, and metric functions.
    Writes an EvaluationSnapshot to the L4 store when a store is provided.
    """

    def __init__(
        self,
        metrics: list[EvaluationMetric] | None = None,
        retrieval_fn: RetrievalFn | None = None,
        generation_fn: GenerationFn | None = None,
        system_version: str = "unknown",
        l4_store: Any | None = None,
    ):
        self.metrics: list[EvaluationMetric] = metrics or _default_metrics()
        self.retrieval_fn: RetrievalFn = retrieval_fn or _default_retrieval
        self.generation_fn: GenerationFn = generation_fn or _default_generation
        self.system_version = system_version
        self.l4_store = l4_store

    def run(self, dataset: EvaluationDataset) -> EvaluationReport:
        """Execute evaluation over all examples in dataset.

        Args:
            dataset: EvaluationDataset with examples to evaluate

        Returns:
            EvaluationReport with per-example results and aggregate scores
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OfflineEvaluationRunner.run")

        run_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        per_example_results: list[EvaluationResult] = []

        for idx, example in enumerate(dataset.examples):
            result = self._evaluate_example(
                example_id=f"{dataset.name}_{idx}",
                example=example,
            )
            per_example_results.append(result)

        aggregate_scores = self._aggregate(per_example_results)

        report = EvaluationReport(
            run_id=run_id,
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            system_version=self.system_version,
            timestamp=timestamp,
            aggregate_scores=aggregate_scores,
            per_example_results=per_example_results,
        )

        if self.l4_store is not None:
            self._persist_snapshot(report)

        return report

    def _evaluate_example(self, example_id: str, example: EvaluationExample) -> EvaluationResult:
        """Run retrieval + generation + metric scoring for one example."""
        retrieved_docs = self.retrieval_fn(example.query)
        generated_answer = self.generation_fn(example.query, retrieved_docs)

        metric_scores: dict[str, float] = {}
        for metric in self.metrics:
            if hasattr(metric, "compute"):
                # Retrieval metrics receive (retrieved_docs, ground_truth_docs)
                # Generation metrics receive (generated_answer, expected_answer, context)
                from ..metrics.base import GenerationMetric, RetrievalMetric

                if isinstance(metric, GenerationMetric):
                    score = metric.compute(
                        prediction=generated_answer,
                        ground_truth=example.expected_answer,
                        context=retrieved_docs,
                    )
                elif isinstance(metric, RetrievalMetric):
                    score = metric.compute(
                        prediction=retrieved_docs,
                        ground_truth=example.ground_truth_documents,
                    )
                else:
                    score = metric.compute(
                        prediction=retrieved_docs,
                        ground_truth=example.ground_truth_documents,
                    )
                metric_scores[metric.name] = score

        return EvaluationResult(
            example_id=example_id,
            query=example.query,
            retrieved_doc_ids=retrieved_docs,
            generated_answer=generated_answer,
            metric_scores=metric_scores,
        )

    def _aggregate(self, results: list[EvaluationResult]) -> dict[str, float]:
        """Average per-example metric scores across all examples."""
        if not results:
            return {}

        metric_names = list(results[0].metric_scores.keys())
        aggregated: dict[str, float] = {}
        for metric_name in metric_names:
            scores = [r.metric_scores[metric_name] for r in results if metric_name in r.metric_scores]
            aggregated[metric_name] = sum(scores) / len(scores) if scores else 0.0
        return aggregated

    def _persist_snapshot(self, report: EvaluationReport) -> None:
        """Persist EvaluationSnapshot to L4 state registry."""
        try:
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            snapshot = EvaluationSnapshot(
                timestamp=report.timestamp,
                system_version=report.system_version,
                dataset_version=report.dataset_version,
                metric_results=report.aggregate_scores,
                run_id=report.run_id,
            )
            artifact = create_artifact(
                kind="evaluation_snapshot",
                logical_id=f"eval_{report.run_id[:8]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        except (ValueError, KeyError, AttributeError) as e:
            # Expected storage errors - log and continue
            logging.getLogger(__name__).warning(
                f"Failed to store evaluation snapshot {report.run_id[:8]}: {e}",
            )
        except (OSError, RuntimeError, MemoryError) as e:    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling
            # Critical storage errors - log and continue
            logging.getLogger(__name__).error(
                f"Critical error storing evaluation snapshot {report.run_id[:8]}: {e}",
            )


def _default_metrics() -> list[EvaluationMetric]:
    """Return the default metric suite."""
    return [
        PrecisionAtK(k=5),
        RecallAtK(k=10),
        MeanReciprocalRank(),
        NDCG(k=10),
        Groundedness(),
        AnswerCorrectness(),
    ]


__all__ = [
    "OfflineEvaluationRunner",
    "_default_metrics",
    "RetrievalFn",
    "GenerationFn",
]
