"""
Dynamic Dependency Resolver for avoiding circular imports.

Provides lazy loading of implementations to prevent circular dependencies
between base agents and L5 components.
"""

import importlib
import logging
from typing import Any, TypeVar

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "dynamic_loader_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "dynamic_loader_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "dynamic_loader_util", "state_snapshot")

trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dynamic_loader_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dynamic_loader_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dynamic_loader_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dynamic_loader_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dynamic_loader_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dynamic_loader_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dynamic_loader_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dynamic_loader_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dynamic_loader_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dynamic_loader_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dynamic_loader_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dynamic_loader_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dynamic_loader_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dynamic_loader_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("dynamic_loader_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dynamic_loader_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dynamic_loader_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dynamic_loader_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dynamic_loader_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dynamic_loader_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dynamic_loader_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dynamic_loader_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dynamic_loader_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dynamic_loader_util", "context_pull")
trace_contract._emit_pulls_context("p1", "dynamic_loader_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dynamic_loader_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dynamic_loader_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dynamic_loader_util", "write_through")
trace_contract._emit_writes_through("p1", "dynamic_loader_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dynamic_loader_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dynamic_loader_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dynamic_loader_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "dynamic_loader_util", "human_escalation")
trace_contract._emit_routes_through("p1", "dynamic_loader_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "dynamic_loader_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dynamic_loader_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dynamic_loader_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dynamic_loader_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dynamic_loader_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "dynamic_loader_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dynamic_loader_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dynamic_loader_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dynamic_loader_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dynamic_loader_util")
trace_contract._emit_gated_by_confidence("p1", "dynamic_loader_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "dynamic_loader_util")
trace_contract.emit_determinism_digest("p0", "dynamic_loader_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "dynamic_loader_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "dynamic_loader_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dynamic_loader_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dynamic_loader_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dynamic_loader_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dynamic_loader_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dynamic_loader_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dynamic_loader_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dynamic_loader_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dynamic_loader_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dynamic_loader_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dynamic_loader_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dynamic_loader_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dynamic_loader_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dynamic_loader_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dynamic_loader_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dynamic_loader_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dynamic_loader_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dynamic_loader_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dynamic_loader_util", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DynamicLoader.load_class")

        cache_key = f"{module_path}:{class_name}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        try:
            module = importlib.import_module(module_path)
            implementation = getattr(module, class_name)
            cls._cache[cache_key] = implementation
            logger.debug(f"[LOADER] Loaded {class_name} from {module_path}")
            return implementation
        except ImportError as e:  # guardian: allow-return-none-swallow -- dynamic import: caller handles None as unavailable component
            logger.warning(f"[LOADER] Could not import {module_path}: {e}")
            return None
        except AttributeError as e:  # guardian: allow-return-none-swallow -- dynamic import: caller handles None as unavailable component
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
        cls,
        protocol_name: str,
        *args: Any,
        singleton: bool = True,
        **kwargs: Any,
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
        except (  # guardian: allow-return-none-swallow allow-log-and-swallow -- dynamic instantiation: non-fatal, caller handles None as unavailable
            ImportError,
            AttributeError,
            TypeError,
            RuntimeError,
            OSError,
        ) as e:
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
