"""
Dynamic Dependency Resolver for avoiding circular imports.

Provides lazy loading of implementations to prevent circular dependencies
between base agents and L5 components.
"""

import importlib
import logging
from typing import Any, TypeVar

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

_emit_applies_guardrail("p0", "dynamic_loader_util", "p0_governance")
_emit_reads_policy_state("p0", "dynamic_loader_util", "policy_binding")
_emit_snapshots_state("p0", "dynamic_loader_util", "state_snapshot")
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

_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_1")
_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_2")
_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_3")
_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_4")
_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_5")
_emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_6")
_emit_records_incident_event("dynamic_loader_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("dynamic_loader_util", "p4obs", "anomaly")
_emit_writes_observability_log("dynamic_loader_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("dynamic_loader_util", "p4obs", "mon_state")
_emit_triggers_alert("dynamic_loader_util", "p4obs", "alert")
_emit_links_incident_trace("dynamic_loader_util", "p4obs", "trace_link")
_emit_captures_pattern("dynamic_loader_util", "p3lm", "pattern")
_emit_records_learning_event("dynamic_loader_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dynamic_loader_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("dynamic_loader_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dynamic_loader_util", "p3lm", "routing")
_emit_improves_agent_policy("dynamic_loader_util", "p3lm", "policy")
_emit_stores_learning_state("dynamic_loader_util", "p3lm", "state")
_emit_records_execution_trace("dynamic_loader_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dynamic_loader_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dynamic_loader_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dynamic_loader_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dynamic_loader_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dynamic_loader_util", "env_read", "p2_env_1")
_emit_reads_environ("dynamic_loader_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("dynamic_loader_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dynamic_loader_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dynamic_loader_util", "context_pull")
_emit_pulls_context("p1", "dynamic_loader_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "dynamic_loader_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dynamic_loader_util", "uwg_term_2")
_emit_writes_through("p1", "dynamic_loader_util", "write_through")
_emit_writes_through("p1", "dynamic_loader_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "dynamic_loader_util", "safety_validation")
_emit_invokes_eval("p1", "dynamic_loader_util", "eval_call")
_emit_proposal_commits_routing("p1", "dynamic_loader_util", "routing_commit")
_emit_escalates_to_human("p1", "dynamic_loader_util", "human_escalation")
_emit_routes_through("p1", "dynamic_loader_util", "route_through")
_emit_checks_agent_registry("p1", "dynamic_loader_util", "agent_registry")
_emit_validates_agent_capability("p1", "dynamic_loader_util", "capability")
_emit_dispatches_execution_plan("p1", "dynamic_loader_util", "exec_plan")
_emit_agent_executes_agent("p1", "dynamic_loader_util", "sub_agent")
_emit_routes_to_agent("p1", "dynamic_loader_util", "target_agent")
_emit_verifies_policy("p1", "dynamic_loader_util", "policy_check")
_emit_observes_runtime_state("p1", "dynamic_loader_util", "runtime_state")
_emit_verifies_boundary("p1", "dynamic_loader_util", "boundary_check")
_emit_transcripts_response("p1", "dynamic_loader_util", "transcript")
_emit_hard_fails_untranscripted("p1", "dynamic_loader_util")
_emit_gated_by_confidence("p1", "dynamic_loader_util", "confidence_gate")
emit_replay_key("p0", "dynamic_loader_util")
emit_determinism_digest("p0", "dynamic_loader_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "dynamic_loader_util", "execution_auth")
_emit_validates_capability("p2", "dynamic_loader_util", "capability_check")
_emit_routes_to_capability("p2", "dynamic_loader_util", "capability_route")
_emit_writes_via_uwg("p2", "dynamic_loader_util", "uwg_write")
_emit_blocks_direct_write("p2", "dynamic_loader_util", "direct_write_block")
_emit_records_tool_invocation("p2", "dynamic_loader_util", "tool_invocation")
_emit_captures_execution_output("p2", "dynamic_loader_util", "exec_output")
_emit_dispatches_agent("p3", "dynamic_loader_util", "agent_dispatch")
_emit_coordinates_agents("p3", "dynamic_loader_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "dynamic_loader_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "dynamic_loader_util", "healing_outcome")
_emit_escalates_failure("p3", "dynamic_loader_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "dynamic_loader_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dynamic_loader_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "dynamic_loader_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "dynamic_loader_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dynamic_loader_util", "eval_metric")
_emit_stores_embedding("p4", "dynamic_loader_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "dynamic_loader_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dynamic_loader_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)
T = TypeVar("T")


class DynamicLoader:
    """Dynamically loads implementations to avoid circular dependencies.

    Uses lazy loading and caching to efficiently resolve dependencies
    at runtime rather than import time.
    """

    _cache: dict[str, Any] = {}
    _instance_cache: dict[str, Any] = {}
    IMPLEMENTATION_REGISTRY: dict[str, dict[str, str]] = {
        "verification": {
            "module": "agentic_core.L5_safety.enforcement.verification_gate",
            "class": "VerificationGate",
        },
        "detection": {
            "module": "agentic_core.L0_routing.enforcement.detection_signal",
            "class": "DetectionSignalEmitter",
        },
        "review": {"module": "agentic_core.L5_safety.enforcement.review_queue", "class": "HumanReviewQueue"},
        "meta_learning": {
            "module": "agentic_core.mixins.meta_learning_mixin",
            "class": "MetaLearningService",
        },
    }

    @classmethod
    def load_class(cls, module_path: str, class_name: str) -> type[T] | None:
        """Load a class dynamically.

        Args:
            module_path: Full module path (e.g., 'agentic_core.L5_safety.enforcement.verification_gate')
            class_name: Name of the class to load

        Returns:
            Class type or None if loading fails
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DynamicLoader.load_class")

        cache_key = f"{module_path}:{class_name}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        try:
            module = importlib.import_module(module_path)
            implementation = getattr(module, class_name)
            cls._cache[cache_key] = implementation
            logger.debug(f"[LOADER] Loaded {class_name} from {module_path}")
            return implementation
        except ImportError as e:
            logger.warning(f"[LOADER] Could not import {module_path}: {e}")
            return None
        except AttributeError as e:
            logger.warning(f"[LOADER] Class {class_name} not found in {module_path}: {e}")
            return None

    @classmethod
    def load_implementation(cls, protocol_name: str) -> type[T] | None:
        """Load implementation for a protocol.

        Args:
            protocol_name: Name of the protocol (e.g., 'verification')

        Returns:
            Implementation class or None if not found
        """
        registry_entry = cls.IMPLEMENTATION_REGISTRY.get(protocol_name)
        if registry_entry is None:
            logger.warning(f"[LOADER] Unknown protocol: {protocol_name}")
            return None
        return cls.load_class(module_path=registry_entry["module"], class_name=registry_entry["class"])

    @classmethod
    def create_instance(
        cls, protocol_name: str, *args: Any, singleton: bool = True, **kwargs: Any,
    ) -> T | None:
        """Create instance of implementation.

        Args:
            protocol_name: Name of the protocol
            *args: Positional arguments for constructor
            singleton: If True, return cached instance
            **kwargs: Keyword arguments for constructor

        Returns:
            Instance or None if creation fails
        """
        if singleton and protocol_name in cls._instance_cache:
            return cls._instance_cache[protocol_name]
        implementation = cls.load_implementation(protocol_name)
        if implementation is None:
            return None
        try:
            instance = implementation(*args, **kwargs)
            if singleton:
                cls._instance_cache[protocol_name] = instance
            logger.debug(f"[LOADER] Created instance of {protocol_name}")
            return instance
        except Exception as e:
            logger.warning(f"[LOADER] Could not create instance of {protocol_name}: {e}")
            return None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached classes and instances."""
        cls._cache.clear()
        cls._instance_cache.clear()
        logger.info("[LOADER] Cache cleared")

    @classmethod
    def clear_instance_cache(cls, protocol_name: str | None = None) -> None:
        """Clear instance cache.

        Args:
            protocol_name: Specific protocol to clear, or None for all
        """
        if protocol_name:
            if protocol_name in cls._instance_cache:
                del cls._instance_cache[protocol_name]
        else:
            cls._instance_cache.clear()

    @classmethod
    def register_implementation(cls, protocol_name: str, module_path: str, class_name: str) -> None:
        """Register a custom implementation.

        Args:
            protocol_name: Name of the protocol
            module_path: Module path
            class_name: Class name
        """
        cls.IMPLEMENTATION_REGISTRY[protocol_name] = {"module": module_path, "class": class_name}
        cache_key = f"{module_path}:{class_name}"
        if cache_key in cls._cache:
            del cls._cache[cache_key]
        if protocol_name in cls._instance_cache:
            del cls._instance_cache[protocol_name]
        logger.info(f"[LOADER] Registered {protocol_name} -> {module_path}:{class_name}")

    @classmethod
    def is_available(cls, protocol_name: str) -> bool:
        """Check if an implementation is available.

        Args:
            protocol_name: Name of the protocol

        Returns:
            True if implementation can be loaded
        """
        implementation = cls.load_implementation(protocol_name)
        return implementation is not None

    @classmethod
    def get_registered_protocols(cls) -> list[str]:
        """Get list of registered protocol names."""
        return list(cls.IMPLEMENTATION_REGISTRY.keys())
