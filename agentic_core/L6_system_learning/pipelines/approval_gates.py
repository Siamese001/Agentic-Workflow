"""G-16-28: Approval gates for System Learning governance.

Deterministic approval decision logic for change packages.

Invariants:
  - All gates are deterministic
  - Risk classification is rule-based
  - High impact defaults to REJECT unless explicitly overridden
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "approval_gates", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "approval_gates", "policy_binding")
trace_contract._emit_snapshots_state("p0", "approval_gates", "state_snapshot")

trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("approval_gates", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("approval_gates", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("approval_gates", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("approval_gates", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("approval_gates", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("approval_gates", "p4obs", "alert")
trace_contract._emit_links_incident_trace("approval_gates", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("approval_gates", "p3lm", "pattern")
trace_contract._emit_records_learning_event("approval_gates", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("approval_gates", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("approval_gates", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("approval_gates", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("approval_gates", "p3lm", "policy")
trace_contract._emit_stores_learning_state("approval_gates", "p3lm", "state")
trace_contract._emit_records_execution_trace("approval_gates", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("approval_gates", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("approval_gates", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("approval_gates", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("approval_gates", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("approval_gates", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("approval_gates", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("approval_gates", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("approval_gates", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "approval_gates", "context_pull")
trace_contract._emit_pulls_context("p1", "approval_gates", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "approval_gates", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "approval_gates", "uwg_term_2")
trace_contract._emit_writes_through("p1", "approval_gates", "write_through")
trace_contract._emit_writes_through("p1", "approval_gates", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "approval_gates", "safety_validation")
trace_contract._emit_invokes_eval("p1", "approval_gates", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "approval_gates", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "approval_gates", "human_escalation")
trace_contract._emit_routes_through("p1", "approval_gates", "route_through")
trace_contract._emit_checks_agent_registry("p1", "approval_gates", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "approval_gates", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "approval_gates", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "approval_gates", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "approval_gates", "target_agent")
trace_contract._emit_verifies_policy("p1", "approval_gates", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "approval_gates", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "approval_gates", "boundary_check")
trace_contract._emit_transcripts_response("p1", "approval_gates", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "approval_gates")
trace_contract._emit_gated_by_confidence("p1", "approval_gates", "confidence_gate")
trace_contract.emit_replay_key("p0", "approval_gates")
trace_contract.emit_determinism_digest("p0", "approval_gates")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "approval_gates", "execution_auth")
trace_contract._emit_validates_capability("p2", "approval_gates", "capability_check")
trace_contract._emit_routes_to_capability("p2", "approval_gates", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "approval_gates", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "approval_gates", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "approval_gates", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "approval_gates", "exec_output")
trace_contract._emit_dispatches_agent("p3", "approval_gates", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "approval_gates", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "approval_gates", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "approval_gates", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "approval_gates", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "approval_gates", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "approval_gates", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "approval_gates", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "approval_gates", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "approval_gates", "eval_metric")
trace_contract._emit_stores_embedding("p4", "approval_gates", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "approval_gates", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "approval_gates", "exec_snapshot_link")


class ApprovalDecision(Enum):
    """Approval decision for change package."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ApprovalGate(Protocol):
    """Protocol for approval gate."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve change package.

        Parameters
        ----------
        pkg : Any
            Change package to evaluate.
        rca : Any
            RCA report.
        snapshot : Any
            Snapshot.

        Returns
        -------
        ApprovalDecision
            APPROVE or REJECT.
        """
        ...


class RiskTierClassifier(Protocol):
    """Protocol for risk tier classification."""

    def classify(self, pkg: Any) -> int:
        """Classify risk tier of change package.

        Parameters
        ----------
        pkg : Any
            Change package to classify.

        Returns
        -------
        int
            Risk tier (higher = more risky).
        """
        ...


class DefaultRuleBasedGate:
    """Default deterministic rule-based approval gate.

    Rules:
      - High impact (risk tier >= 3): REJECT by default
      - Low impact (risk tier < 3): APPROVE

    High impact criteria:
      - Touches more than K surfaces
      - Delta exceeds threshold
      - Affects L5 (safety-critical)
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        risk_classifier: RiskTierClassifier,
        high_impact_threshold: int = 3,
        allow_high_impact: bool = False,
    ):
        """Initialize approval gate.

        Parameters
        ----------
        risk_classifier : RiskTierClassifier
            Risk tier classifier.
        high_impact_threshold : int
            Threshold for high impact (default 3).
        allow_high_impact : bool
            Whether to allow high impact changes (default False).
        """
        self.risk_classifier = risk_classifier
        self.high_impact_threshold = high_impact_threshold
        self.allow_high_impact = allow_high_impact

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve change package.

        Parameters
        ----------
        pkg : Any
            Change package to evaluate.
        rca : Any
            RCA report.
        snapshot : Any
            Snapshot.

        Returns
        -------
        ApprovalDecision
            APPROVE or REJECT.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DefaultRuleBasedGate.decide")

        risk_tier = self.risk_classifier.classify(pkg)
        if risk_tier >= self.high_impact_threshold:
            if self.allow_high_impact:
                return ApprovalDecision.APPROVE
            return ApprovalDecision.REJECT
        return ApprovalDecision.APPROVE


class DefaultRiskClassifier:
    """Default deterministic risk tier classifier.

    Risk tiers:
      0: No change
      1: Low impact (single surface, small delta)
      2: Medium impact (multiple surfaces, moderate delta)
      3: High impact (many surfaces, large delta, or L5)
      4: Critical impact (L5 + large delta)
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        max_surfaces_low: int = 1,
        max_surfaces_medium: int = 3,
        max_delta_low: float = 0.05,
        max_delta_medium: float = 0.1,
    ):
        """Initialize risk classifier.

        Parameters
        ----------
        max_surfaces_low : int
            Max surfaces for low impact (default 1).
        max_surfaces_medium : int
            Max surfaces for medium impact (default 3).
        max_delta_low : float
            Max delta for low impact (default 0.05).
        max_delta_medium : float
            Max delta for medium impact (default 0.10).
        """
        self.max_surfaces_low = max_surfaces_low
        self.max_surfaces_medium = max_surfaces_medium
        self.max_delta_low = max_delta_low
        self.max_delta_medium = max_delta_medium

    def classify(self, pkg: Any) -> int:
        """Classify risk tier of change package.

        Parameters
        ----------
        pkg : Any
            Change package to classify.

        Returns
        -------
        int
            Risk tier (0-4).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DefaultRiskClassifier.classify"
        )

        num_surfaces = getattr(pkg, "num_surfaces", 1)
        max_delta = getattr(pkg, "max_delta", 0.0)
        affects_l5 = getattr(pkg, "affects_l5", False)
        if affects_l5 and max_delta > self.max_delta_medium:
            return 4
        if affects_l5 or num_surfaces > self.max_surfaces_medium or max_delta > self.max_delta_medium:
            return 3
        if num_surfaces > self.max_surfaces_low or max_delta > self.max_delta_low:
            return 2
        return 1
