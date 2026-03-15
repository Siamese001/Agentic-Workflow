"""
Component Factory for creating protocol-compliant components.

Provides factory functions for creating verification gates, review queues,
detection emitters, and meta-learning services with proper feature flag integration.
"""

import logging
from typing import Any

from agentic_core.utils.dependency_resolver import DynamicLoader
from agentic_core.utils.feature_flags import FeatureFlagManager

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.utils.detection_protocol_util import DetectionSignalProtocol
from agentic_core.utils.meta_learning_types_util import MetaLearningProtocol
from agentic_core.utils.review_protocol_util import HumanReviewProtocol
from agentic_core.utils.verification_types_util import VerificationGateProtocol

_emit_dispatches_healing_run("p1", "component_util", "L0")
_emit_routes_through("p1", "component_util", "L0")
_emit_escalates_to_human("p1", "component_util", "L0")
_emit_reads_policy_state("p1", "component_util", "L0")

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
                from agentic_core.L0_routing.seams.safety_reasoning_seam import load_verification_gate_adapter

                adapter_mod = load_verification_gate_adapter()
                instance = adapter_mod.VerificationGateAdapter()
                cls._instances[cache_key] = instance
                return instance
            except ImportError:
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
                from agentic_core.L0_routing.seams.safety_reasoning_seam import load_human_review_adapter

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
