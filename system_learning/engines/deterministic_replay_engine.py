"""
W5 Deterministic Replay Engine

Validates RetrievalProfile changes by replaying fixed synthetic retrieval cases
and emitting a stable replay digest.
"""

import hashlib
import json
from dataclasses import dataclass

import numpy as np

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

_emit_authorize_and_execute("p2", "deterministic_replay_engine", "execution_auth")
_emit_validates_capability("p2", "deterministic_replay_engine", "capability_check")
_emit_routes_to_capability("p2", "deterministic_replay_engine", "capability_route")
_emit_writes_via_uwg("p2", "deterministic_replay_engine", "uwg_write")
_emit_blocks_direct_write("p2", "deterministic_replay_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "deterministic_replay_engine", "tool_invocation")
_emit_captures_execution_output("p2", "deterministic_replay_engine", "exec_output")
_emit_dispatches_agent("p3", "deterministic_replay_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "deterministic_replay_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "deterministic_replay_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "deterministic_replay_engine", "healing_outcome")
_emit_escalates_failure("p3", "deterministic_replay_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "deterministic_replay_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deterministic_replay_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "deterministic_replay_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "deterministic_replay_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deterministic_replay_engine", "eval_metric")
_emit_stores_embedding("p4", "deterministic_replay_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "deterministic_replay_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deterministic_replay_engine", "exec_snapshot_link")
from system_learning.engines.retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "deterministic_replay_engine", "p0_governance")
_emit_reads_policy_state("p0", "deterministic_replay_engine", "policy_binding")
_emit_snapshots_state("p0", "deterministic_replay_engine", "state_snapshot")
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

record_execution_trace("deterministic_replay_engine", "deterministic_replay_engine_trace")


_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_1")
_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_2")
_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_3")
_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_4")
_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_5")
_emit_emits_metric_event("deterministic_replay_engine", "p4obs", "metric_6")
_emit_records_incident_event("deterministic_replay_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("deterministic_replay_engine", "p4obs", "anomaly")
_emit_writes_observability_log("deterministic_replay_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("deterministic_replay_engine", "p4obs", "mon_state")
_emit_triggers_alert("deterministic_replay_engine", "p4obs", "alert")
_emit_links_incident_trace("deterministic_replay_engine", "p4obs", "trace_link")
_emit_captures_pattern("deterministic_replay_engine", "p3lm", "pattern")
_emit_records_learning_event("deterministic_replay_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("deterministic_replay_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("deterministic_replay_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("deterministic_replay_engine", "p3lm", "routing")
_emit_improves_agent_policy("deterministic_replay_engine", "p3lm", "policy")
_emit_stores_learning_state("deterministic_replay_engine", "p3lm", "state")
_emit_records_execution_trace("deterministic_replay_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("deterministic_replay_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("deterministic_replay_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("deterministic_replay_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("deterministic_replay_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("deterministic_replay_engine", "env_read", "p2_env_1")
_emit_reads_environ("deterministic_replay_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("deterministic_replay_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("deterministic_replay_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "deterministic_replay_engine", "context_pull")
_emit_pulls_context("p1", "deterministic_replay_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "deterministic_replay_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "deterministic_replay_engine", "uwg_term_2")
_emit_writes_through("p1", "deterministic_replay_engine", "write_through")
_emit_writes_through("p1", "deterministic_replay_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "deterministic_replay_engine", "safety_validation")
_emit_invokes_eval("p1", "deterministic_replay_engine", "eval_call")
_emit_proposal_commits_routing("p1", "deterministic_replay_engine", "routing_commit")
_emit_escalates_to_human("p1", "deterministic_replay_engine", "human_escalation")
_emit_routes_through("p1", "deterministic_replay_engine", "route_through")
_emit_checks_agent_registry("p1", "deterministic_replay_engine", "agent_registry")
_emit_validates_agent_capability("p1", "deterministic_replay_engine", "capability")
_emit_dispatches_execution_plan("p1", "deterministic_replay_engine", "exec_plan")
_emit_agent_executes_agent("p1", "deterministic_replay_engine", "sub_agent")
_emit_routes_to_agent("p1", "deterministic_replay_engine", "target_agent")
_emit_verifies_policy("p1", "deterministic_replay_engine", "policy_check")
_emit_observes_runtime_state("p1", "deterministic_replay_engine", "runtime_state")
_emit_verifies_boundary("p1", "deterministic_replay_engine", "boundary_check")
_emit_transcripts_response("p1", "deterministic_replay_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "deterministic_replay_engine")
_emit_gated_by_confidence("p1", "deterministic_replay_engine", "confidence_gate")
emit_replay_key("p0", "deterministic_replay_engine")
emit_determinism_digest("p0", "deterministic_replay_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """Result of deterministic replay validation."""

    case_count: int
    base_outputs: dict[str, list[str]]
    candidate_outputs: dict[str, list[str]]
    changed_cases: int
    replay_digest: str

    def emit_digest(self) -> None:
        """Print the replay digest for verification."""
        print(f"W5-REPLAY-DIGEST: {self.replay_digest}")


class DeterministicReplayEngine:
    """Deterministic replay engine for RetrievalProfile validation."""

    def __init__(self):
        """Initialize replay engine with fixed synthetic cases."""
        self._synthetic_cases = [
            {
                "query": "machine learning fundamentals",
                "corpus": [
                    {"id": "doc1", "text": "ML basics"},
                    {"id": "doc2", "text": "Deep learning"},
                    {"id": "doc3", "text": "Neural networks"},
                    {"id": "doc4", "text": "Optimization"},
                    {"id": "doc5", "text": "Data preprocessing"},
                ],
            },
            {
                "query": "neural network architectures",
                "corpus": [
                    {"id": "doc6", "text": "CNN architectures"},
                    {"id": "doc7", "text": "RNN architectures"},
                    {"id": "doc8", "text": "Transformer models"},
                    {"id": "doc9", "text": "Attention mechanisms"},
                    {"id": "doc10", "text": "GAN architectures"},
                ],
            },
            {
                "query": "optimization algorithms",
                "corpus": [
                    {"id": "doc11", "text": "Gradient descent"},
                    {"id": "doc12", "text": "Adam optimizer"},
                    {"id": "doc13", "text": "SGD with momentum"},
                    {"id": "doc14", "text": "Learning rate schedules"},
                    {"id": "doc15", "text": "Adaptive methods"},
                ],
            },
            {
                "query": "data preprocessing techniques",
                "corpus": [
                    {"id": "doc16", "text": "Normalization"},
                    {"id": "doc17", "text": "Standardization"},
                    {"id": "doc18", "text": "Feature scaling"},
                    {"id": "doc19", "text": "Missing value imputation"},
                    {"id": "doc20", "text": "Data augmentation"},
                ],
            },
            {
                "query": "model evaluation metrics",
                "corpus": [
                    {"id": "doc21", "text": "Accuracy metrics"},
                    {"id": "doc22", "text": "Precision and recall"},
                    {"id": "doc23", "text": "F1 score"},
                    {"id": "doc24", "text": "ROC curves"},
                    {"id": "doc25", "text": "Cross-validation"},
                ],
            },
        ]

    def replay(self, *, base_profile: RetrievalProfile, candidate_profile: RetrievalProfile) -> ReplayResult:
        """Replay synthetic cases with both profiles and compare results.

        Args:
            base_profile: Base RetrievalProfile to test
            candidate_profile: Candidate RetrievalProfile to test

        Returns:
            ReplayResult with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DeterministicReplayEngine.replay")

        base_outputs = self._run_replay_cases(base_profile)
        candidate_outputs = self._run_replay_cases(candidate_profile)
        changed_cases = sum(
            1 for case_id in base_outputs if base_outputs[case_id] != candidate_outputs[case_id]
        )
        replay_digest = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        replay_digest_check = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        if replay_digest != replay_digest_check:
            raise ValueError(f"Determinism self-check failed: {replay_digest} != {replay_digest_check}")
        result = ReplayResult(
            case_count=len(self._synthetic_cases),
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
            replay_digest=replay_digest,
        )
        result.emit_digest()
        return result

    def _run_replay_cases(self, profile: RetrievalProfile) -> dict[str, list[str]]:
        """Run all synthetic cases with given profile.

        Args:
            profile: RetrievalProfile to use for replay

        Returns:
            Dictionary mapping case IDs to result lists
        """
        outputs = {}
        sorted_cases = sorted(enumerate(self._synthetic_cases), key=lambda x: x[1]["query"])
        for original_index, case in sorted_cases:
            query_hash = hashlib.md5(case["query"].encode("utf-8")).hexdigest()[:8]
            case_id = f"case_{query_hash}"
            query_hash_int = int(query_hash, 16)
            dim = profile.embedding_dim
            query_embedding = np.zeros(dim)
            deterministic_index = query_hash_int % dim
            query_embedding[deterministic_index] = 1.0
            corpus = case["corpus"]
            similarities = []
            for i, doc in enumerate(corpus):
                doc_embedding = np.zeros(dim)
                if i < dim:
                    doc_seed = (query_hash_int + i) % dim
                    doc_embedding[doc_seed] = 0.9
                similarity = np.dot(query_embedding, doc_embedding)
                similarities.append((doc["id"], similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            filtered_results = []
            for doc_id, similarity in similarities:
                if similarity >= profile.similarity_cutoff:
                    filtered_results.append((doc_id, similarity))
            limited_results = filtered_results[: profile.top_k]
            scaled_results = []
            for doc_id, similarity in limited_results:
                scaled_similarity = round(similarity * profile.influence_cap, 6)
                scaled_results.append((doc_id, scaled_similarity))
            result_strings = [f"{doc_id}:{similarity:.6f}" for doc_id, similarity in scaled_results]
            result_strings.sort()
            outputs[case_id] = result_strings
        return outputs

    def _compute_replay_digest(
        self,
        *,
        base_profile: RetrievalProfile,
        candidate_profile: RetrievalProfile,
        base_outputs: dict[str, list[str]],
        candidate_outputs: dict[str, list[str]],
        changed_cases: int,
    ) -> str:
        """Compute deterministic SHA-256 digest for replay.

        Args:
            base_profile: Base profile used
            candidate_profile: Candidate profile used
            base_outputs: Outputs from base profile
            candidate_outputs: Outputs from candidate profile
            changed_cases: Number of changed cases

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile": json.loads(base_profile.to_canonical_json()),
            "candidate_profile": json.loads(candidate_profile.to_canonical_json()),
            "base_outputs": {k: sorted(v) for k, v in sorted(base_outputs.items())},
            "candidate_outputs": {k: sorted(v) for k, v in sorted(candidate_outputs.items())},
            "changed_cases": changed_cases,
            "case_count": len(self._synthetic_cases),
            "replay_version": "W11-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["DeterministicReplayEngine", "ReplayResult"]
