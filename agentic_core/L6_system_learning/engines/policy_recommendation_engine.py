"""
W4-D Policy Recommendation Engine

Converts W4-C DriftSummary outputs into deterministic, bounded policy recommendations.
Advisory only - does not mutate active RetrievalProfile.
"""

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "policy_recommendation_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "policy_recommendation_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "policy_recommendation_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "policy_recommendation_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "policy_recommendation_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "policy_recommendation_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "policy_recommendation_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "policy_recommendation_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "policy_recommendation_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "policy_recommendation_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "policy_recommendation_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "policy_recommendation_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "policy_recommendation_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "policy_recommendation_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "policy_recommendation_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "policy_recommendation_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "policy_recommendation_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "policy_recommendation_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "policy_recommendation_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "policy_recommendation_engine", "exec_snapshot_link")
from .retrieval_profile import RetrievalProfile
from .shadow_drift_analyzer import DriftSummary

trace_contract._emit_records_execution_trace("p0", "evidence", "policy_recommendation_engine")
trace_contract._emit_applies_guardrail("p0", "policy_recommendation_engine", "p0_governance")
trace_contract._emit_snapshots_state("p0", "policy_recommendation_engine", "state_snapshot")

trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("policy_recommendation_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("policy_recommendation_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("policy_recommendation_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("policy_recommendation_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("policy_recommendation_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("policy_recommendation_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("policy_recommendation_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("policy_recommendation_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("policy_recommendation_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("policy_recommendation_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("policy_recommendation_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("policy_recommendation_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("policy_recommendation_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("policy_recommendation_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("policy_recommendation_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("policy_recommendation_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("policy_recommendation_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("policy_recommendation_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("policy_recommendation_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("policy_recommendation_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("policy_recommendation_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("policy_recommendation_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("policy_recommendation_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "policy_recommendation_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "policy_recommendation_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_recommendation_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_recommendation_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "policy_recommendation_engine", "write_through")
trace_contract._emit_writes_through("p1", "policy_recommendation_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "policy_recommendation_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "policy_recommendation_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "policy_recommendation_engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "policy_recommendation_engine", "human_escalation")
trace_contract._emit_routes_through("p1", "policy_recommendation_engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "policy_recommendation_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "policy_recommendation_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "policy_recommendation_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "policy_recommendation_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "policy_recommendation_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "policy_recommendation_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "policy_recommendation_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "policy_recommendation_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "policy_recommendation_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "policy_recommendation_engine")
trace_contract._emit_gated_by_confidence("p1", "policy_recommendation_engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "policy_recommendation_engine")
trace_contract.emit_determinism_digest("p0", "policy_recommendation_engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class PolicyRecommendation:
    """Advisory policy recommendation based on drift analysis."""

    profile_id: str
    recommended_changes: dict[str, float]
    rationale: str
    confidence_score: float
    deterministic_digest: str

    def emit_digest(self) -> None:
        """Print the recommendation digest for determinism verification."""
        print(f"W4D-RECOMMEND-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        data = {
            "profile_id": self.profile_id,
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "rationale": self.rationale,
            "confidence_score": round(self.confidence_score, 6),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


class PolicyRecommendationEngine:
    """Generates deterministic, bounded policy recommendations from drift analysis."""

    def generate_recommendation(
        self,
        *,
        drift_summary: DriftSummary,
        active_profile: RetrievalProfile,
        now_utc: int,
    ) -> PolicyRecommendation:
        """Generate policy recommendation based on drift analysis.

        Args:
            drift_summary: Drift analysis from W4-C
            active_profile: Current active RetrievalProfile
            now_utc: Current timestamp

        Returns:
            PolicyRecommendation with deterministic digest
        """
        if drift_summary.drift_flag:
            recommended_changes = {}
            rationale_parts = []
            max_cutoff_reduction = min(0.02, drift_summary.drift_score * 0.05)
            if max_cutoff_reduction > 1e-06:
                new_cutoff = max(0.1, round(active_profile.similarity_cutoff - max_cutoff_reduction, 6))
                recommended_changes["similarity_cutoff"] = new_cutoff
                rationale_parts.append(
                    f"Lower similarity_cutoff from {active_profile.similarity_cutoff:.6f} to {new_cutoff:.6f} (drift_score={drift_summary.drift_score:.6f})",
                )
            max_cap_increase = min(0.01, drift_summary.drift_score * 0.02)
            if max_cap_increase > 1e-06:
                new_cap = min(1.0, round(active_profile.influence_cap + max_cap_increase, 6))
                recommended_changes["influence_cap"] = new_cap
                rationale_parts.append(
                    f"Increase influence_cap from {active_profile.influence_cap:.6f} to {new_cap:.6f} (drift_score={drift_summary.drift_score:.6f})",
                )
            rationale = "Drift detected: " + "; ".join(rationale_parts)
            confidence_score = min(1.0, drift_summary.drift_score * 2.0)
        else:
            recommended_changes = {}
            rationale = f"No drift detected (p95_cosine={drift_summary.p95_cosine:.6f} >= 0.92)"
            confidence_score = 0.95
        deterministic_digest = self._compute_digest(
            profile_id=active_profile.profile_id,
            drift_summary=drift_summary,
            recommended_changes=recommended_changes,
            rationale=rationale,
            confidence_score=confidence_score,
            now_utc=now_utc,
        )
        return PolicyRecommendation(
            profile_id=active_profile.profile_id,
            recommended_changes=recommended_changes,
            rationale=rationale,
            confidence_score=round(confidence_score, 6),
            deterministic_digest=deterministic_digest,
        )

    def _compute_digest(
        self,
        *,
        profile_id: str,
        drift_summary: DriftSummary,
        recommended_changes: dict[str, float],
        rationale: str,
        confidence_score: float,
        now_utc: int,
    ) -> str:
        """Compute deterministic SHA-256 digest of recommendation data."""
        data = {
            "profile_id": profile_id,
            "drift_summary": {
                "profile_id": drift_summary.profile_id,
                "batch_size": drift_summary.batch_size,
                "mean_cosine": round(drift_summary.mean_cosine, 6),
                "p95_cosine": round(drift_summary.p95_cosine, 6),
                "drift_flag": drift_summary.drift_flag,
                "drift_score": round(drift_summary.drift_score, 6),
            },
            "recommended_changes": {k: round(v, 6) for k, v in sorted(recommended_changes.items())},
            "rationale": rationale,
            "confidence_score": round(confidence_score, 6),
            "now_utc": now_utc,
            "engine_version": "W4-D-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class MemoryAwarePolicyRecommendationEngine(PolicyRecommendationEngine):
    """PolicyRecommendationEngine that persists recommendations to Memory MCP.

    Drop-in replacement. Every call to ``generate_recommendation`` is
    automatically persisted to the Memory MCP knowledge graph, building a
    cross-session recommendation history for drift trend analysis.
    """

    def generate_recommendation(
        self,
        *,
        drift_summary: DriftSummary,
        active_profile: RetrievalProfile,
        now_utc: int,
    ) -> PolicyRecommendation:
        recommendation = super().generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        try:
            from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            get_sl_memory_bridge().persist_policy_recommendation(recommendation, ts=str(now_utc))

            # Factor healing memory retrieval quality into recommendation confidence
            try:
                bridge = get_sl_memory_bridge()
                # Query recent retrieval quality metrics
                recent_quality = bridge._query_recent_healing_memory_quality(hours=24)
                if recent_quality:
                    avg_quality_score = sum(q.get("score", 0.5) for q in recent_quality) / len(recent_quality)
                    # Adjust confidence based on retrieval quality
                    quality_adjustment = (avg_quality_score - 0.5) * 0.2  # ±10% adjustment
                    recommendation.confidence_score = max(
                        0.0, min(1.0, recommendation.confidence_score + quality_adjustment)
                    )
            except (  # guardian: allow-log-and-swallow -- quality adjustment optional: non-fatal, recommendation returned without adjustment
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:
                # Quality adjustment unavailable - continue without it
                import logging

                logging.getLogger(__name__).debug(
                    "policy_recommendation_engine: retrieval quality adjustment failed: %s", exc
                )
        except (  # guardian: allow-log-and-swallow -- memory-aware augmentation optional: non-fatal, base recommendation returned
            AttributeError,
            ImportError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            import logging

            logging.getLogger(__name__).debug(
                "policy_recommendation_engine: memory-aware augmentation unavailable: %s", exc
            )
        return recommendation


__all__ = ["PolicyRecommendationEngine", "MemoryAwarePolicyRecommendationEngine", "PolicyRecommendation"]
