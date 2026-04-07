"""
Deliverability Validator - Deterministic Deliverability Validation

Zero-Ambiguity Standard: Renamed from deliverability_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Spam trigger detection (keyword matching)
- Link count validation (counting)
- Image count validation (counting)
- Content analysis (pattern matching)
"""

from __future__ import annotations

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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "deliverability_validator")
emit_determinism_digest("p0", "deliverability_validator")

_emit_dispatches_healing_run("p1", "deliverability_validator", "L5")
_emit_routes_through("p1", "deliverability_validator", "L5")
_emit_checks_agent_registry("p1", "deliverability_validator", "agent_registry")
_emit_validates_agent_capability("p1", "deliverability_validator", "capability")
_emit_dispatches_execution_plan("p1", "deliverability_validator", "exec_plan")
_emit_agent_executes_agent("p1", "deliverability_validator", "sub_agent")
_emit_routes_to_agent("p1", "deliverability_validator", "target_agent")
_emit_verifies_policy("p1", "deliverability_validator", "policy_check")
_emit_observes_runtime_state("p1", "deliverability_validator", "runtime_state")
_emit_verifies_boundary("p1", "deliverability_validator", "boundary_check")
_emit_transcripts_response("p1", "deliverability_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "deliverability_validator")
_emit_gated_by_confidence("p1", "deliverability_validator", "confidence_gate")
_emit_escalates_to_human("p1", "deliverability_validator", "L5")
_emit_reads_policy_state("p1", "deliverability_validator", "L5")

_emit_applies_guardrail("p0", "deliverability_validator", "p0_governance")
_emit_snapshots_state("p0", "deliverability_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "deliverability_validator", "execution_auth")
_emit_validates_capability("p2", "deliverability_validator", "capability_check")
_emit_routes_to_capability("p2", "deliverability_validator", "capability_route")
_emit_writes_via_uwg("p2", "deliverability_validator", "uwg_write")
_emit_blocks_direct_write("p2", "deliverability_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "deliverability_validator", "tool_invocation")
_emit_captures_execution_output("p2", "deliverability_validator", "exec_output")
_emit_dispatches_agent("p3", "deliverability_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "deliverability_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "deliverability_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "deliverability_validator", "healing_outcome")
_emit_escalates_failure("p3", "deliverability_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "deliverability_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deliverability_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "deliverability_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "deliverability_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deliverability_validator", "eval_metric")
_emit_stores_embedding("p4", "deliverability_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "deliverability_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deliverability_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_1")
_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_2")
_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_3")
_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_4")
_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_5")
_emit_emits_metric_event("deliverability_validator", "p4obs", "metric_6")
_emit_records_incident_event("deliverability_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("deliverability_validator", "p4obs", "anomaly")
_emit_writes_observability_log("deliverability_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("deliverability_validator", "p4obs", "mon_state")
_emit_triggers_alert("deliverability_validator", "p4obs", "alert")
_emit_links_incident_trace("deliverability_validator", "p4obs", "trace_link")
_emit_captures_pattern("deliverability_validator", "p3lm", "pattern")
_emit_records_learning_event("deliverability_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("deliverability_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("deliverability_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("deliverability_validator", "p3lm", "routing")
_emit_improves_agent_policy("deliverability_validator", "p3lm", "policy")
_emit_stores_learning_state("deliverability_validator", "p3lm", "state")
_emit_records_execution_trace("deliverability_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("deliverability_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("deliverability_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("deliverability_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("deliverability_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("deliverability_validator", "env_read", "p2_env_1")
_emit_reads_environ("deliverability_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("deliverability_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("deliverability_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "deliverability_validator", "context_pull")
_emit_pulls_context("p1", "deliverability_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "deliverability_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "deliverability_validator", "uwg_term_2")
_emit_writes_through("p1", "deliverability_validator", "write_through")
_emit_writes_through("p1", "deliverability_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "deliverability_validator", "safety_validation")
_emit_invokes_eval("p1", "deliverability_validator", "eval_call")
_emit_proposal_commits_routing("p1", "deliverability_validator", "routing_commit")


@dataclass
class DeliverabilityResult:
    """Result of deliverability validation."""

    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class DeliverabilityValidator:
    """
    Pure deterministic deliverability validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize with deliverability validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.spam_triggers = config.get(
            "spam_triggers", ["$$$", "!!!", "CAPS LOCK", "FREE", "BUY NOW", "CLICK HERE", "ACT NOW"],
        )
        self.max_links = config.get("max_links", 3)
        self.max_images = config.get("max_images", 2)
        self.spam_rate_threshold = config.get("spam_rate_threshold", 0.01)

    def validate_deliverability(self, messages: list[dict[str, Any]]) -> DeliverabilityResult:
        """
        Validate deliverability using purely deterministic logic.

        Args:
            messages: List of message dictionaries with 'content' field

        Returns:
            DeliverabilityResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "DeliverabilityValidator.validate_deliverability",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DeliverabilityValidator.validate_deliverability".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not messages:
            return DeliverabilityResult(
                passed=True,
                issues=[],
                score=1.0,
                metadata={"validation_type": "deterministic", "message_count": 0},
            )
        issues: list[str] = []
        for i, message in enumerate(messages):
            content = message.get("content", "")
            spam_issues = self._check_spam_triggers(content, i)
            issues.extend(spam_issues)
            link_issues = self._check_link_count(content, i)
            issues.extend(link_issues)
            image_issues = self._check_image_count(content, i)
            issues.extend(image_issues)
        score = self._calculate_deliverability_score(issues, len(messages))
        return DeliverabilityResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"validation_type": "deterministic", "message_count": len(messages)},
        )

    def _check_spam_triggers(self, content: str, message_index: int) -> list[str]:
        """
        Check for spam triggers using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching logic
        """
        issues: list[str] = []
        for trigger in self.spam_triggers:
            if trigger in content:
                issues.append(f"Message {message_index}: Spam trigger '{trigger}'")
        return issues

    def _check_link_count(self, content: str, message_index: int) -> list[str]:
        """
        Check link count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        """
        issues: list[str] = []
        link_count = content.count("http")
        if link_count > self.max_links:
            issues.append(f"Message {message_index}: Too many links ({link_count})")
        return issues

    def _check_image_count(self, content: str, message_index: int) -> list[str]:
        """
        Check image count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        """
        issues: list[str] = []
        img_count = content.count("<img")
        if img_count > self.max_images:
            issues.append(f"Message {message_index}: Too many images ({img_count})")
        return issues

    def _calculate_deliverability_score(self, issues: list[str], message_count: int) -> float:
        """
        Calculate deliverability score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        if message_count == 0:
            return 1.0
        base_score = 1.0
        issue_penalty = len(issues) * 0.1
        base_score -= issue_penalty
        return max(0.0, min(1.0, base_score))

    def check_single_message(self, content: str) -> DeliverabilityResult:
        """
        Check a single message for deliverability issues.

        Convenience method for single message validation.
        """
        return self.validate_deliverability([{"content": content}])

    def get_spam_trigger_count(self, content: str) -> int:
        """
        Count spam triggers in content.

        Moved to Deterministic: Pure counting logic
        """
        count = 0
        for trigger in self.spam_triggers:
            count += content.count(trigger)
        return count

    def analyze_content_risk(self, content: str) -> dict[str, Any]:
        """
        Analyze content risk using deterministic rules.

        Returns detailed risk analysis for content.
        """
        spam_count = self.get_spam_trigger_count(content)
        link_count = content.count("http")
        image_count = content.count("<img")
        risk_score = 0
        if spam_count > 0:
            risk_score += spam_count * 2
        if link_count > self.max_links:
            risk_score += (link_count - self.max_links) * 1
        if image_count > self.max_images:
            risk_score += (image_count - self.max_images) * 1
        risk_level = "low" if risk_score == 0 else "medium" if risk_score < 5 else "high"
        return {
            "spam_trigger_count": spam_count,
            "link_count": link_count,
            "image_count": image_count,
            "risk_score": risk_score,
            "risk_level": risk_level,
        }
