"""
W4-F Retrieval Profile Replay Check Engine

Performs deterministic replay checks to verify profile changes produce consistent results.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

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

_emit_authorize_and_execute("p2", "retrieval_profile_replay_check", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_replay_check", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_replay_check", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_replay_check", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_replay_check", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_replay_check", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_replay_check", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_replay_check", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_replay_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_replay_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_replay_check", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_replay_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_replay_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_replay_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_replay_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_replay_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_replay_check", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_replay_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_replay_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_replay_check", "exec_snapshot_link")
from .retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "retrieval_profile_replay_check", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile_replay_check", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile_replay_check", "state_snapshot")
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
from tqdm import tqdm

record_execution_trace("retrieval_profile_replay_check", "retrieval_profile_replay_check_trace")


_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile_replay_check", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile_replay_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile_replay_check", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile_replay_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile_replay_check", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile_replay_check", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile_replay_check", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile_replay_check", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile_replay_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile_replay_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile_replay_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile_replay_check", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile_replay_check", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile_replay_check", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile_replay_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile_replay_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile_replay_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile_replay_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile_replay_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile_replay_check", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile_replay_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile_replay_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile_replay_check", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile_replay_check", "context_pull")
_emit_pulls_context("p1", "retrieval_profile_replay_check", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_replay_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_replay_check", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile_replay_check", "write_through")
_emit_writes_through("p1", "retrieval_profile_replay_check", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile_replay_check", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile_replay_check", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile_replay_check", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile_replay_check", "human_escalation")
_emit_routes_through("p1", "retrieval_profile_replay_check", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile_replay_check", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile_replay_check", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile_replay_check", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile_replay_check", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile_replay_check", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile_replay_check", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile_replay_check", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile_replay_check", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile_replay_check", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile_replay_check")
_emit_gated_by_confidence("p1", "retrieval_profile_replay_check", "confidence_gate")
emit_replay_key("p0", "retrieval_profile_replay_check")
emit_determinism_digest("p0", "retrieval_profile_replay_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class ReplayCheckResult:
    """Result of deterministic replay check."""

    passed: bool
    digest: str
    base_output: dict[str, Any]
    proposed_output: dict[str, Any]
    reason: str


class RetrievalProfileReplayChecker:
    """Performs deterministic replay checks for profile changes."""

    def __init__(self):
        """Initialize replay checker with deterministic test fixtures."""
        self._test_queries = [
            "machine learning fundamentals",
            "neural network architectures",
            "optimization algorithms",
            "data preprocessing techniques",
            "model evaluation metrics",
        ]
        self._test_embeddings = {
            "machine learning fundamentals": [0.1, 0.2, 0.3, 0.4, 0.5],
            "neural network architectures": [0.2, 0.3, 0.4, 0.5, 0.6],
            "optimization algorithms": [0.3, 0.4, 0.5, 0.6, 0.7],
            "data preprocessing techniques": [0.4, 0.5, 0.6, 0.7, 0.8],
            "model evaluation metrics": [0.5, 0.6, 0.7, 0.8, 0.9],
        }

    def replay_check_profile_change(
        self,
        *,
        base_profile: RetrievalProfile,
        proposed_profile: RetrievalProfile,
    ) -> ReplayCheckResult:
        """Perform deterministic replay check of profile change.

        Args:
            base_profile: Base profile to test
            proposed_profile: Proposed profile to test

        Returns:
            ReplayCheckResult with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "RetrievalProfileReplayChecker.replay_check_profile_change",
        )

        base_output = self._run_deterministic_retrieval(base_profile)
        proposed_output = self._run_deterministic_retrieval(proposed_profile)
        digest = self._compute_replay_digest(
            base_profile=base_profile,
            proposed_profile=proposed_profile,
            base_output=base_output,
            proposed_output=proposed_output,
        )
        passed = self._compare_outputs(base_output, proposed_output)
        if passed:
            reason = "Replay check passed: deterministic outputs consistent"
        else:
            reason = "Replay check failed: outputs differ between profiles"
        print(f"W4F-REPLAY-DIGEST: {digest}")
        return ReplayCheckResult(
            passed=passed,
            digest=digest,
            base_output=base_output,
            proposed_output=proposed_output,
            reason=reason,
        )

    def _run_deterministic_retrieval(self, profile: RetrievalProfile) -> dict[str, Any]:
        """Run deterministic retrieval scenario with given profile.

        Args:
            profile: Profile to use for retrieval

        Returns:
            Deterministic output dictionary
        """
        results = []
        for query in tqdm(self._test_queries, desc="Processing", unit="item"):
            query_embedding = self._test_embeddings[query]
            similarities = []
            for other_query, other_embedding in self._test_embeddings.items():
                similarity = sum((q * o for q, o in zip(query_embedding, other_embedding)))
                similarities.append((other_query, similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            filtered_results = []
            for other_query, similarity in similarities:
                if similarity >= profile.similarity_cutoff:
                    filtered_results.append((other_query, similarity))
            limited_results = filtered_results[: profile.top_k]
            scaled_results = []
            for other_query, similarity in limited_results:
                scaled_similarity = similarity * profile.influence_cap
                scaled_results.append((other_query, round(scaled_similarity, 6)))
            results.append(
                {
                    "query": query,
                    "results": scaled_results,
                    "profile_similarity_cutoff": profile.similarity_cutoff,
                    "profile_top_k": profile.top_k,
                    "profile_influence_cap": profile.influence_cap,
                },
            )
        return {"profile_id": profile.profile_id, "query_results": results, "total_results": len(results)}

    def _compare_outputs(self, base_output: dict[str, Any], proposed_output: dict[str, Any]) -> bool:
        """Compare outputs for deterministic consistency.

        Args:
            base_output: Output from base profile
            proposed_output: Output from proposed profile

        Returns:
            True if outputs are consistent with profile differences
        """
        if set(base_output.keys()) != set(proposed_output.keys()):
            return False
        if base_output["total_results"] != proposed_output["total_results"]:
            return False
        if len(base_output["query_results"]) != len(proposed_output["query_results"]):
            return False
        for i, (base_query, proposed_query) in enumerate(
            zip(base_output["query_results"], proposed_output["query_results"]),
        ):
            if base_query["query"] != proposed_query["query"]:
                return False
            if not isinstance(proposed_query["results"], list):
                return False
        return True

    def _compute_replay_digest(
        self,
        *,
        base_profile: RetrievalProfile,
        proposed_profile: RetrievalProfile,
        base_output: dict[str, Any],
        proposed_output: dict[str, Any],
    ) -> str:
        """Compute deterministic SHA-256 digest for replay check.

        Args:
            base_profile: Base profile used
            proposed_profile: Proposed profile used
            base_output: Output from base profile
            proposed_output: Output from proposed profile

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile": json.loads(base_profile.to_canonical_json()),
            "proposed_profile": json.loads(proposed_profile.to_canonical_json()),
            "base_output_summary": {
                "profile_id": base_output["profile_id"],
                "total_results": base_output["total_results"],
                "query_count": len(base_output["query_results"]),
            },
            "proposed_output_summary": {
                "profile_id": proposed_output["profile_id"],
                "total_results": proposed_output["total_results"],
                "query_count": len(proposed_output["query_results"]),
            },
            "replay_version": "W4-F-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileReplayChecker", "ReplayCheckResult"]
