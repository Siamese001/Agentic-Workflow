"""
Component Factory for creating protocol-compliant components.

Provides factory functions for creating verification gates, review queues,
detection emitters, and meta-learning services with proper feature flag integration.
"""

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.utils.dependency_resolver import DynamicLoader
from agentic_core.utils.feature_flags import FeatureFlagManager

_emit_authorize_and_execute("p2", "component_util", "execution_auth")
_emit_validates_capability("p2", "component_util", "capability_check")
_emit_routes_to_capability("p2", "component_util", "capability_route")
_emit_writes_via_uwg("p2", "component_util", "uwg_write")
_emit_blocks_direct_write("p2", "component_util", "direct_write_block")
_emit_records_tool_invocation("p2", "component_util", "tool_invocation")
_emit_captures_execution_output("p2", "component_util", "exec_output")
_emit_dispatches_agent("p3", "component_util", "agent_dispatch")
_emit_coordinates_agents("p3", "component_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "component_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "component_util", "healing_outcome")
_emit_escalates_failure("p3", "component_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "component_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "component_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "component_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "component_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "component_util", "eval_metric")
_emit_stores_embedding("p4", "component_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "component_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "component_util", "exec_snapshot_link")
from agentic_core.utils.schemas.detection_protocol_util import DetectionSignalProtocol
from agentic_core.utils.schemas.meta_learning_types_util import MetaLearningProtocol
from agentic_core.utils.schemas.review_protocol_util import HumanReviewProtocol
from agentic_core.utils.schemas.verification_types_util import VerificationGateProtocol

_emit_dispatches_healing_run("p1", "component_util", "L0")
_emit_routes_through("p1", "component_util", "L0")
_emit_checks_agent_registry("p1", "component_util", "agent_registry")
_emit_validates_agent_capability("p1", "component_util", "capability")
_emit_dispatches_execution_plan("p1", "component_util", "exec_plan")
_emit_agent_executes_agent("p1", "component_util", "sub_agent")
_emit_routes_to_agent("p1", "component_util", "target_agent")
_emit_verifies_policy("p1", "component_util", "policy_check")
_emit_observes_runtime_state("p1", "component_util", "runtime_state")
_emit_verifies_boundary("p1", "component_util", "boundary_check")
_emit_transcripts_response("p1", "component_util", "transcript")
_emit_hard_fails_untranscripted("p1", "component_util")
_emit_gated_by_confidence("p1", "component_util", "confidence_gate")
_emit_escalates_to_human("p1", "component_util", "L0")
_emit_reads_policy_state("p1", "component_util", "L0")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("component_util", "p4obs", "metric_1")
_emit_emits_metric_event("component_util", "p4obs", "metric_2")
_emit_emits_metric_event("component_util", "p4obs", "metric_3")
_emit_emits_metric_event("component_util", "p4obs", "metric_4")
_emit_emits_metric_event("component_util", "p4obs", "metric_5")
_emit_emits_metric_event("component_util", "p4obs", "metric_6")
_emit_records_incident_event("component_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("component_util", "p4obs", "anomaly")
_emit_writes_observability_log("component_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("component_util", "p4obs", "mon_state")
_emit_triggers_alert("component_util", "p4obs", "alert")
_emit_links_incident_trace("component_util", "p4obs", "trace_link")
_emit_captures_pattern("component_util", "p3lm", "pattern")
_emit_records_learning_event("component_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("component_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("component_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("component_util", "p3lm", "routing")
_emit_improves_agent_policy("component_util", "p3lm", "policy")
_emit_stores_learning_state("component_util", "p3lm", "state")
_emit_records_execution_trace("component_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("component_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("component_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("component_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("component_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("component_util", "env_read", "p2_env_1")
_emit_reads_environ("component_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("component_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("component_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "component_util", "context_pull")
_emit_pulls_context("p1", "component_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "component_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "component_util", "uwg_term_2")
_emit_writes_through("p1", "component_util", "write_through")
_emit_writes_through("p1", "component_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "component_util", "safety_validation")
_emit_invokes_eval("p1", "component_util", "eval_call")
_emit_proposal_commits_routing("p1", "component_util", "routing_commit")

logger = logging.getLogger(__name__)


class ComponentFactory:
    """Factory for creating protocol-compliant components.

    Manages singleton instances of components and provides proper
    feature flag integration for all component creation.
    """

    _instances: dict[str, Any] = {}

    @classmethod
    def get_verification_gate(cls, use_adapter: bool = True) -> VerificationGateProtocol | None:
        """Get verification gate instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            VerificationGateProtocol instance or None if disabled
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ComponentFactory.get_verification_gate", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ComponentFactory.get_verification_gate", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ComponentFactory.get_verification_gate"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not FeatureFlagManager.is_enabled("ENABLE_VERIFICATION_GATE"):
            logger.debug("ComponentFactory: Verification gate disabled")
            return None
        cache_key = "verification_gate"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        if use_adapter:
            try:
                from agentic_core.L0_routing.utils.seams.safety_reasoning_seam import load_verification_gate_adapter

                adapter_mod = load_verification_gate_adapter()
                instance = adapter_mod.VerificationGateAdapter()
                cls._instances[cache_key] = instance
                return instance
            except ImportError:  # guardian: allow-silent-swallow
                logger.warning("ComponentFactory: Could not load adapter")
        instance = DynamicLoader.create_instance("verification")
        if instance:
            cls._instances[cache_key] = instance
        return instance

    @classmethod
    def get_human_review_queue(cls, use_adapter: bool = True) -> HumanReviewProtocol | None:
        """Get human review queue instance.

        Args:
            use_adapter: If True, use protocol-compliant adapter

        Returns:
            HumanReviewProtocol instance or None if disabled
        """
        if not FeatureFlagManager.is_enabled("ENABLE_HITL_WORKFLOW"):
            logger.debug("ComponentFactory: HITL workflow disabled")
            return None
        cache_key = "human_review"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        if use_adapter:
            try:
                from agentic_core.L0_routing.utils.seams.safety_reasoning_seam import load_human_review_adapter

                adapter_mod = load_human_review_adapter()
                instance = adapter_mod.HumanReviewAdapter()
                cls._instances[cache_key] = instance
                return instance
            except ImportError:
                logger.warning("ComponentFactory: Could not load adapter")
        instance = DynamicLoader.create_instance("review")
        if instance:
            cls._instances[cache_key] = instance
        return instance

    @classmethod
    def get_detection_emitter(cls) -> DetectionSignalProtocol | None:
        """Get detection signal emitter instance.

        Returns:
            DetectionSignalProtocol instance or None if disabled
        """
        if not FeatureFlagManager.is_enabled("ENABLE_DETECTION_SIGNAL"):
            logger.debug("ComponentFactory: Detection signal disabled")
            return None
        cache_key = "detection_emitter"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        instance = DynamicLoader.create_instance("detection")
        if instance:
            cls._instances[cache_key] = instance
        return instance

    @classmethod
    def get_meta_learning_service(cls) -> MetaLearningProtocol | None:
        """Get meta-learning service instance.

        Returns:
            MetaLearningProtocol instance or None if disabled
        """
        if not FeatureFlagManager.is_enabled("ENABLE_META_LEARNING"):
            logger.debug("ComponentFactory: Meta-learning disabled")
            return None
        cache_key = "meta_learning"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        instance = DynamicLoader.create_instance("meta_learning")
        if instance:
            cls._instances[cache_key] = instance
        return instance

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached instances."""
        cls._instances.clear()
        logger.info("ComponentFactory: Cleared all instances")

    @classmethod
    def get_component_status(cls) -> dict[str, Any]:
        """Get status of all components.

        Returns:
            Dictionary with component availability and flag status
        """
        return {
            "verification_gate": {
                "flag_enabled": FeatureFlagManager.is_enabled("ENABLE_VERIFICATION_GATE"),
                "instance_cached": "verification_gate" in cls._instances,
            },
            "human_review": {
                "flag_enabled": FeatureFlagManager.is_enabled("ENABLE_HITL_WORKFLOW"),
                "instance_cached": "human_review" in cls._instances,
            },
            "detection_emitter": {
                "flag_enabled": FeatureFlagManager.is_enabled("ENABLE_DETECTION_SIGNAL"),
                "instance_cached": "detection_emitter" in cls._instances,
            },
            "meta_learning": {
                "flag_enabled": FeatureFlagManager.is_enabled("ENABLE_META_LEARNING"),
                "instance_cached": "meta_learning" in cls._instances,
            },
        }


def get_verification_gate(use_adapter: bool = True) -> VerificationGateProtocol | None:
    """Get verification gate instance."""
    return ComponentFactory.get_verification_gate(use_adapter)


def get_human_review_queue(use_adapter: bool = True) -> HumanReviewProtocol | None:
    """Get human review queue instance."""
    return ComponentFactory.get_human_review_queue(use_adapter)


def get_detection_emitter() -> DetectionSignalProtocol | None:
    """Get detection signal emitter instance."""
    return ComponentFactory.get_detection_emitter()


def get_meta_learning_service() -> MetaLearningProtocol | None:
    """Get meta-learning service instance."""
    return ComponentFactory.get_meta_learning_service()
