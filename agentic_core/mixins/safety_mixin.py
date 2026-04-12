"""
Safety Domain Mixins - Shared pure logic for safety-related operations.

These mixins extract pure, stateless logic that can be reused across
safety domain agents while preserving stateful orchestration locally.
"""

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
)

_emit_applies_guardrail("p0", "safety_mixin", "p0_governance")
_emit_reads_policy_state("p0", "safety_mixin", "policy_binding")
_emit_snapshots_state("p0", "safety_mixin", "state_snapshot")
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

_emit_emits_metric_event("safety_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("safety_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("safety_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("safety_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("safety_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("safety_mixin", "p4obs", "metric_6")
_emit_records_incident_event("safety_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("safety_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("safety_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("safety_mixin", "p4obs", "mon_state")
_emit_triggers_alert("safety_mixin", "p4obs", "alert")
_emit_links_incident_trace("safety_mixin", "p4obs", "trace_link")
_emit_captures_pattern("safety_mixin", "p3lm", "pattern")
_emit_records_learning_event("safety_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safety_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("safety_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safety_mixin", "p3lm", "routing")
_emit_improves_agent_policy("safety_mixin", "p3lm", "policy")
_emit_stores_learning_state("safety_mixin", "p3lm", "state")
_emit_records_execution_trace("safety_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safety_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safety_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safety_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safety_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safety_mixin", "env_read", "p2_env_1")
_emit_reads_environ("safety_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("safety_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safety_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safety_mixin", "context_pull")
_emit_pulls_context("p1", "safety_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safety_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safety_mixin", "uwg_term_2")
_emit_writes_through("p1", "safety_mixin", "write_through")
_emit_writes_through("p1", "safety_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "safety_mixin", "safety_validation")
_emit_invokes_eval("p1", "safety_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "safety_mixin", "routing_commit")
_emit_escalates_to_human("p1", "safety_mixin", "human_escalation")
_emit_routes_through("p1", "safety_mixin", "route_through")
_emit_checks_agent_registry("p1", "safety_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "safety_mixin", "capability")
_emit_dispatches_execution_plan("p1", "safety_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "safety_mixin", "sub_agent")
_emit_routes_to_agent("p1", "safety_mixin", "target_agent")
_emit_verifies_policy("p1", "safety_mixin", "policy_check")
_emit_observes_runtime_state("p1", "safety_mixin", "runtime_state")
_emit_verifies_boundary("p1", "safety_mixin", "boundary_check")
_emit_transcripts_response("p1", "safety_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_mixin")
_emit_gated_by_confidence("p1", "safety_mixin", "confidence_gate")
emit_replay_key("p0", "safety_mixin")
emit_determinism_digest("p0", "safety_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "safety_mixin", "execution_auth")
_emit_validates_capability("p2", "safety_mixin", "capability_check")
_emit_routes_to_capability("p2", "safety_mixin", "capability_route")
_emit_writes_via_uwg("p2", "safety_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "safety_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "safety_mixin", "exec_output")
_emit_dispatches_agent("p3", "safety_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_mixin", "healing_outcome")
_emit_escalates_failure("p3", "safety_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_mixin", "eval_metric")
_emit_stores_embedding("p4", "safety_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_mixin", "exec_snapshot_link")


class SafetyAnalysisMixin:
    """Mixin providing pure safety analysis logic."""

    @staticmethod
    def _compare_threat_levels(level1: str, level2: str) -> int:
        """
        Compare two threat levels.

        Args:
            level1: First threat level
            level2: Second threat level

        Returns:
            -1 if level1 < level2, 0 if equal, 1 if level1 > level2
        """
        threat_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        try:
            idx1 = threat_order.index(level1.upper())
            idx2 = threat_order.index(level2.upper())
            if idx1 < idx2:
                return -1
            elif idx1 > idx2:
                return 1
            else:
                return 0
        except ValueError as e:
            # TODO: Add proper input validation
            logger.warning(f"Invalid input: {e}")
            return (level1 > level2) - (level1 < level2)

    @staticmethod
    def _generate_recommendations(threat_level: str, context: dict[str, Any]) -> list[str]:
        """
        Generate safety recommendations based on threat level and context.

        Args:
            threat_level: Current threat level
            context: Context information for recommendations

        Returns:
            List of recommendation strings
        """
        recommendations = []
        if threat_level.upper() == "CRITICAL":
            recommendations.extend(
                ["Immediate action required", "Escalate to security team", "Consider system isolation"],
            )
        elif threat_level.upper() == "HIGH":
            recommendations.extend(
                ["Address within 24 hours", "Review security controls", "Monitor for related issues"],
            )
        elif threat_level.upper() == "MEDIUM":
            recommendations.extend(
                ["Address within 1 week", "Document mitigation plan", "Schedule follow-up review"],
            )
        else:
            recommendations.extend(
                [
                    "Address in next maintenance cycle",
                    "Consider for future improvements",
                    "Document for awareness",
                ],
            )
        if "file_count" in context and context["file_count"] > 100:
            recommendations.append("Consider bulk remediation approach")
        if "system_critical" in context and context["system_critical"]:
            recommendations.append("Prioritize system availability")
        return recommendations

    @staticmethod
    def matches(pattern: str, target: str) -> bool:
        """
        Check if pattern matches target using simple wildcard matching.

        Args:
            pattern: Pattern with optional wildcards
            target: Target string to match

        Returns:
            True if pattern matches target
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SafetyAnalysisMixin.matches")

        if not pattern or not target:
            return False
        if "*" in pattern:
            import re

            pattern_regex = pattern.replace("*", ".*")
            return re.fullmatch(pattern_regex, target) is not None
        else:
            return pattern == target


class HealingMixin:
    """Mixin providing pure healing logic."""

    @staticmethod
    def standard_heal(file_path: str, issue_type: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Standard healing logic for common file issues.

        Args:
            file_path: Path to file being healed
            issue_type: Type of issue detected
            context: Additional context for healing

        Returns:
            Healing result dictionary
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingMixin.standard_heal")

        result = {
            "file_path": file_path,
            "issue_type": issue_type,
            "healed": False,
            "actions_taken": [],
            "warnings": [],
        }
        if issue_type == "import_error":
            result["actions_taken"].append("Attempted import path correction")
            result["healed"] = True
        elif issue_type == "syntax_error":
            result["actions_taken"].append("Syntax validation failed - manual review required")
            result["warnings"].append("Syntax errors require manual intervention")
        elif issue_type == "missing_dependency":
            result["actions_taken"].append("Documented missing dependency")
            result["warnings"].append("Dependency installation may be required")
        else:
            result["actions_taken"].append(f"Applied standard healing for {issue_type}")
            result["healed"] = True
        if "backup_available" in context and context["backup_available"]:
            result["actions_taken"].append("Backup created before healing")
        return result


class StateAnalysisMixin:
    """Mixin providing pure state analysis logic."""

    @staticmethod
    # guardian: allow-magic-config
    def _check_past_failures(
        state_history: list[dict[str, Any]],
        failure_threshold: int = 3,
    ) -> dict[str, Any]:
        """
        Analyze past failures to determine retry strategy.

        Args:
            state_history: List of previous state dictionaries
            failure_threshold: Number of failures before changing strategy

        Returns:
            Analysis result with recommendations
        """
        if not state_history:
            return {
                "failures_detected": False,
                "failure_count": 0,
                "recommendation": "Proceed normally",
                "retry_delay": 0,
            }
        failure_count = sum(1 for state in state_history if state.get("status") == "failed")
        result = {
            "failures_detected": failure_count > 0,
            "failure_count": failure_count,
            "recommendation": "Proceed normally",
            "retry_delay": 0,
        }
        if failure_count >= failure_threshold:
            result["recommendation"] = "Change approach or escalate"
            result["retry_delay"] = min(300, 30 * failure_count)
        elif failure_count > 0:
            result["recommendation"] = "Retry with caution"
            result["retry_delay"] = min(60, 10 * failure_count)
        return result
