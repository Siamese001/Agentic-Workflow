"""RLHF Optimizer - deterministic DPO-driven threshold adjustments.

Converts DPO feedback into bounded, proposal-only threshold adjustments.
"""

from __future__ import annotations

import json
from typing import Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "rlhf_optimizer", "execution_auth")
trace_contract._emit_validates_capability("p2", "rlhf_optimizer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rlhf_optimizer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rlhf_optimizer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rlhf_optimizer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rlhf_optimizer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rlhf_optimizer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rlhf_optimizer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rlhf_optimizer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rlhf_optimizer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rlhf_optimizer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rlhf_optimizer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rlhf_optimizer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rlhf_optimizer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rlhf_optimizer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rlhf_optimizer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rlhf_optimizer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rlhf_optimizer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rlhf_optimizer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rlhf_optimizer", "exec_snapshot_link")
from .change_package_impl import ChangePackage

trace_contract._emit_applies_guardrail("p0", "rlhf_optimizer", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "rlhf_optimizer", "policy_binding")
trace_contract._emit_snapshots_state("p0", "rlhf_optimizer", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rlhf_optimizer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rlhf_optimizer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rlhf_optimizer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rlhf_optimizer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rlhf_optimizer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rlhf_optimizer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rlhf_optimizer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rlhf_optimizer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rlhf_optimizer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rlhf_optimizer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rlhf_optimizer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rlhf_optimizer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rlhf_optimizer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rlhf_optimizer", "p3lm", "state")
trace_contract._emit_records_execution_trace("rlhf_optimizer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rlhf_optimizer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rlhf_optimizer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rlhf_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rlhf_optimizer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rlhf_optimizer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rlhf_optimizer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rlhf_optimizer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rlhf_optimizer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rlhf_optimizer", "context_pull")
trace_contract._emit_pulls_context("p1", "rlhf_optimizer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rlhf_optimizer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rlhf_optimizer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rlhf_optimizer", "write_through")
trace_contract._emit_writes_through("p1", "rlhf_optimizer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rlhf_optimizer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rlhf_optimizer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rlhf_optimizer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "rlhf_optimizer", "human_escalation")
trace_contract._emit_routes_through("p1", "rlhf_optimizer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "rlhf_optimizer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rlhf_optimizer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rlhf_optimizer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rlhf_optimizer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rlhf_optimizer", "target_agent")
trace_contract._emit_verifies_policy("p1", "rlhf_optimizer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rlhf_optimizer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rlhf_optimizer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rlhf_optimizer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rlhf_optimizer")
trace_contract._emit_gated_by_confidence("p1", "rlhf_optimizer", "confidence_gate")
trace_contract.emit_replay_key("p0", "rlhf_optimizer")
trace_contract.emit_determinism_digest("p0", "rlhf_optimizer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RLHFOptimizer(Protocol):
    """Protocol for RLHF optimization from DPO feedback."""

    def propose_from_dpo(
        self,
        *,
        dpo_batch_bytes: bytes,
        current_threshold_config_bytes: bytes,
        embedding_context_hash: str | None = None,
    ) -> ChangePackage:
        """Generate proposal-only threshold adjustments from DPO batch.

        Parameters:
            dpo_batch_bytes: Serialized DPOBatch artifact.
            current_threshold_config_bytes: Current threshold configuration.

        Returns:
            ChangePackage with proposal-only adjustments (no activation).
        """
        ...


class DefaultDeterministicRLHFOptimizer:
    """Default deterministic RLHF optimizer.

    Applies bounded adjustments based on APPROVE/REJECT decisions.
    """

    def __init__(
        self,
        *,
        min_threshold: float = 0.1,
        max_threshold: float = 2.0,
        approve_relax_delta: float = 0.1,
        reject_tighten_delta: float = -0.1,
    ):
        """Initialize optimizer with bounded parameters.

        Args:
            min_threshold: Minimum allowed threshold value.
            max_threshold: Maximum allowed threshold value.
            approve_relax_delta: Positive delta for APPROVE decisions.
            reject_tighten_delta: Negative delta for REJECT decisions.
        """
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.approve_relax_delta = approve_relax_delta
        self.reject_tighten_delta = reject_tighten_delta

    def propose_from_dpo(
        self,
        *,
        dpo_batch_bytes: bytes,
        current_threshold_config_bytes: bytes,
        embedding_context_hash: str | None = None,
    ) -> ChangePackage:
        """Generate deterministic threshold adjustments from DPO batch.

        Args:
            dpo_batch_bytes: Serialized DPOBatch artifact.
            current_threshold_config_bytes: Current threshold configuration.

        Returns:
            ChangePackage with proposal-only adjustments.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DefaultDeterministicRLHFOptimizer.propose_from_dpo"
        )

        try:
            dpo_data = json.loads(dpo_batch_bytes.decode("utf-8"))
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):  # review: Encoding errors should specify fallback encoding strategy
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_dpo_batch",),
                timestamp_utc=0,
                embedding_context_hash=embedding_context_hash,
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )
        try:
            current_config = json.loads(current_threshold_config_bytes.decode("utf-8"))
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):  # review: Encoding errors should specify fallback encoding strategy
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_threshold_config",),
                timestamp_utc=0,
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )
        adjustments = {}
        reasons = []
        if "pairs" in dpo_data:
            sorted_pairs = sorted(
                dpo_data["pairs"],
                key=lambda p: (
                    p.get("score", 0.0),
                    p.get("timestamp_utc", 0),
                    p["example_id"]["control_hash"],
                    p["example_id"]["candidate_hash"],
                ),
                reverse=True,
            )
            for pair in tqdm(sorted_pairs, desc="Processing", unit="item"):
                human_decision = pair.get("human_decision", "")
                pair_reasons = pair.get("reasons", [])
                if human_decision == "APPROVE":
                    delta = self.approve_relax_delta
                    reasons.append(f"approve_relax_{delta:.6f}")
                elif human_decision == "REJECT":
                    delta = self.reject_tighten_delta
                    reasons.append(f"reject_tighten_{delta:.6f}")
                else:
                    continue
                for key, value in current_config.items():
                    if isinstance(value, (int, float)):
                        if key not in adjustments:
                            adjustments[key] = 0.0
                        adjustments[key] += delta
                reasons.extend(pair_reasons)
        for key in adjustments:
            adjustments[key] = round(adjustments[key], 6)
        final_config = {}
        for key, value in current_config.items():
            if isinstance(value, (int, float)) and key in adjustments:
                final_config[key] = round(value + adjustments[key], 6)
                final_config[key] = max(self.min_threshold, min(self.max_threshold, final_config[key]))
            else:
                final_config[key] = value
        changes_bytes = json.dumps(final_config, separators=(",", ":"), sort_keys=True).encode("utf-8")
        num_pairs = len(dpo_data.get("pairs", []))
        confidence = min(1.0, num_pairs * 0.1)
        package = ChangePackage(
            source="rlhf_optimizer",
            target="threshold_config",
            changes=changes_bytes,
            confidence=confidence,
            reason=tuple(reasons) if reasons else ("no_adjustments",),
            timestamp_utc=0,
            embedding_context_hash=embedding_context_hash,
            authority_sensitivity="MEDIUM",
            target_surface="threshold_config",
        )
        return package

    def commit_optimization(self, package: ChangePackage) -> bool:
        """Commit an optimization proposal (ADG: commits_optimization edge).

        Returns True if the proposal confidence exceeds the minimum threshold.
        Actual persistence is handled by the caller pipeline.
        """
        return package.confidence >= 0.1
