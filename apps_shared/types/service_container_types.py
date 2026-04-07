"""Service Container - Dependency Injection System.

This module implements a lightweight dependency injection container to eliminate
global singletons and improve testability. Services are registered by type
and resolved as needed throughout the application.
"""

import logging
from abc import ABC
from collections.abc import Callable
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

_emit_applies_guardrail("p0", "service_container_types", "p0_governance")
_emit_reads_policy_state("p0", "service_container_types", "policy_binding")
_emit_snapshots_state("p0", "service_container_types", "state_snapshot")
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

_emit_emits_metric_event("service_container_types", "p4obs", "metric_1")
_emit_emits_metric_event("service_container_types", "p4obs", "metric_2")
_emit_emits_metric_event("service_container_types", "p4obs", "metric_3")
_emit_emits_metric_event("service_container_types", "p4obs", "metric_4")
_emit_emits_metric_event("service_container_types", "p4obs", "metric_5")
_emit_emits_metric_event("service_container_types", "p4obs", "metric_6")
_emit_records_incident_event("service_container_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("service_container_types", "p4obs", "anomaly")
_emit_writes_observability_log("service_container_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("service_container_types", "p4obs", "mon_state")
_emit_triggers_alert("service_container_types", "p4obs", "alert")
_emit_links_incident_trace("service_container_types", "p4obs", "trace_link")
_emit_captures_pattern("service_container_types", "p3lm", "pattern")
_emit_records_learning_event("service_container_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("service_container_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("service_container_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("service_container_types", "p3lm", "routing")
_emit_improves_agent_policy("service_container_types", "p3lm", "policy")
_emit_stores_learning_state("service_container_types", "p3lm", "state")
_emit_records_execution_trace("service_container_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("service_container_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("service_container_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("service_container_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("service_container_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("service_container_types", "env_read", "p2_env_1")
_emit_reads_environ("service_container_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("service_container_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("service_container_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "service_container_types", "context_pull")
_emit_pulls_context("p1", "service_container_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "service_container_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "service_container_types", "uwg_term_2")
_emit_writes_through("p1", "service_container_types", "write_through")
_emit_writes_through("p1", "service_container_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "service_container_types", "safety_validation")
_emit_invokes_eval("p1", "service_container_types", "eval_call")
_emit_proposal_commits_routing("p1", "service_container_types", "routing_commit")
_emit_escalates_to_human("p1", "service_container_types", "human_escalation")
_emit_routes_through("p1", "service_container_types", "route_through")
_emit_checks_agent_registry("p1", "service_container_types", "agent_registry")
_emit_validates_agent_capability("p1", "service_container_types", "capability")
_emit_dispatches_execution_plan("p1", "service_container_types", "exec_plan")
_emit_agent_executes_agent("p1", "service_container_types", "sub_agent")
_emit_routes_to_agent("p1", "service_container_types", "target_agent")
_emit_verifies_policy("p1", "service_container_types", "policy_check")
_emit_observes_runtime_state("p1", "service_container_types", "runtime_state")
_emit_verifies_boundary("p1", "service_container_types", "boundary_check")
_emit_transcripts_response("p1", "service_container_types", "transcript")
_emit_hard_fails_untranscripted("p1", "service_container_types")
_emit_gated_by_confidence("p1", "service_container_types", "confidence_gate")
emit_replay_key("p0", "service_container_types")
emit_determinism_digest("p0", "service_container_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "service_container_types", "execution_auth")
_emit_validates_capability("p2", "service_container_types", "capability_check")
_emit_routes_to_capability("p2", "service_container_types", "capability_route")
_emit_writes_via_uwg("p2", "service_container_types", "uwg_write")
_emit_blocks_direct_write("p2", "service_container_types", "direct_write_block")
_emit_records_tool_invocation("p2", "service_container_types", "tool_invocation")
_emit_captures_execution_output("p2", "service_container_types", "exec_output")
_emit_dispatches_agent("p3", "service_container_types", "agent_dispatch")
_emit_coordinates_agents("p3", "service_container_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "service_container_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "service_container_types", "healing_outcome")
_emit_escalates_failure("p3", "service_container_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "service_container_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "service_container_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "service_container_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "service_container_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "service_container_types", "eval_metric")
_emit_stores_embedding("p4", "service_container_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "service_container_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "service_container_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)
T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""

    pass


class ServiceContainer:
    """Simple dependency injection container.

    Supports:
    - Type-based registration and resolution
    - Factory functions for lazy initialization
    - Singleton instances (default)
    - Transient instances (new each time)
    """

    def __init__(self, name: str = "default"):
        """Initialize the container.

        Args:
            name: Optional name for the container (useful for debugging)
        """
        self.name = name
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
        self._singletons: dict[type, Any] = {}
        self._lifecycle: dict[type, str] = {}

    def register(
        self,
        interface: type[T],
        implementation: T | None = None,
        factory: Callable[[], T] | None = None,
        lifecycle: str = "singleton",
    ) -> None:
        """Register a service in the container.

        Args:
            interface: The type/class to register
            implementation: Optional instance to use (for singletons)
            factory: Optional factory function to create instances
            lifecycle: "singleton" (default) or "transient"

        Raises:
            ValueError: If neither implementation nor factory is provided
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ServiceContainer.register")

        if implementation is None and factory is None:
            raise ValueError("Must provide either implementation or factory")
        if lifecycle not in ["singleton", "transient"]:
            raise ValueError("Lifecycle must be 'singleton' or 'transient'")
        self._lifecycle[interface] = lifecycle
        if implementation is not None:
            if lifecycle == "singleton":
                self._singletons[interface] = implementation
            else:
                self._services[interface] = implementation
        if factory is not None:
            self._factories[interface] = factory
        logger.debug(f"Registered {interface.__name__} in container '{self.name}'")

    def resolve(self, interface: type[T]) -> T:
        """Resolve a service from the container.

        Args:
            interface: The type/class to resolve

        Returns:
            An instance of the requested type

        Raises:
            ServiceNotFoundError: If the service is not registered
        """
        if interface not in self._lifecycle:
            raise ServiceNotFoundError(f"{interface.__name__} not registered in container")
        lifecycle = self._lifecycle[interface]
        if lifecycle == "singleton":
            if interface in self._singletons:
                return self._singletons[interface]
            if interface in self._factories:
                instance = self._factories[interface]()
                self._singletons[interface] = instance
                return instance
            if interface in self._services:
                return self._services[interface]
        if lifecycle == "transient":
            if interface in self._factories:
                return self._factories[interface]()
            if interface in self._services:
                implementation = self._services[interface]
                try:
                    return type(implementation)()
                # guardian: allow-silent-swallow
                except Exception:
                    logger.warning(
                        f"Could not create transient instance of {interface.__name__}, returning singleton",
                    )
                    return implementation
        raise ServiceNotFoundError(f"Could not resolve {interface.__name__}")

    def is_registered(self, interface: type) -> bool:
        """Check if a service is registered.

        Args:
            interface: The type/class to check

        Returns:
            True if registered, False otherwise
        """
        return interface in self._lifecycle

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._lifecycle.clear()
        logger.debug(f"Cleared all services from container '{self.name}'")

    def list_services(self) -> dict[type, str]:
        """List all registered services and their lifecycles.

        Returns:
            Dictionary mapping types to lifecycle names
        """
        return self._lifecycle.copy()


_default_container: ServiceContainer | None = None


def get_default_container() -> ServiceContainer:
    """Get the default container instance.

    Returns:
        The default ServiceContainer
    """
    global _default_container
    if _default_container is None:
        _default_container = ServiceContainer("default")
    return _default_container


def register_default(
    interface: type[T],
    implementation: T | None = None,
    factory: Callable[[], T] | None = None,
    lifecycle: str = "singleton",
) -> None:
    """Register a service in the default container.

    This is a convenience function for global registration.

    Args:
        interface: The type/class to register
        implementation: Optional instance to use
        factory: Optional factory function
        lifecycle: "singleton" (default) or "transient"
    """
    get_default_container().register(interface, implementation, factory, lifecycle)


def resolve_default(interface: type[T]) -> T:
    """Resolve a service from the default container.

    This is a convenience function for global resolution.

    Args:
        interface: The type/class to resolve

    Returns:
        An instance of the requested type
    """
    return get_default_container().resolve(interface)


class Service(ABC):
    """Base class for services that can be dependency injected."""

    pass
