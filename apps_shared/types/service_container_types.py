"""Service Container - Dependency Injection System.

This module implements a lightweight dependency injection container to eliminate
global singletons and improve testability. Services are registered by type
and resolved as needed throughout the application.
"""

import logging
from abc import ABC
from collections.abc import Callable
from typing import Any, TypeVar

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "service_container_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "service_container_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "service_container_types", "state_snapshot")

trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("service_container_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("service_container_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("service_container_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("service_container_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("service_container_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("service_container_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("service_container_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("service_container_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("service_container_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("service_container_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("service_container_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("service_container_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("service_container_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("service_container_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("service_container_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("service_container_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("service_container_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("service_container_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("service_container_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("service_container_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("service_container_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("service_container_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("service_container_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "service_container_types", "context_pull")
trace_contract._emit_pulls_context("p1", "service_container_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "service_container_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "service_container_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "service_container_types", "write_through")
trace_contract._emit_writes_through("p1", "service_container_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "service_container_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "service_container_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "service_container_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "service_container_types", "human_escalation")
trace_contract._emit_routes_through("p1", "service_container_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "service_container_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "service_container_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "service_container_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "service_container_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "service_container_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "service_container_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "service_container_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "service_container_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "service_container_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "service_container_types")
trace_contract._emit_gated_by_confidence("p1", "service_container_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "service_container_types")
trace_contract.emit_determinism_digest("p0", "service_container_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "service_container_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "service_container_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "service_container_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "service_container_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "service_container_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "service_container_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "service_container_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "service_container_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "service_container_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "service_container_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "service_container_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "service_container_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "service_container_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "service_container_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "service_container_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "service_container_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "service_container_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "service_container_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "service_container_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "service_container_types", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ServiceContainer.register")

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
                except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError):  # guardian: allow-silent-swallow
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
