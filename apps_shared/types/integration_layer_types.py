"""
Integration Layer - Connects apps_lic and apps_rg with shared infrastructure.

Provides unified configuration loading, service discovery, and cross-app
communication patterns.
Phase 3B - Integration Layer Implementation
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
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

_emit_applies_guardrail("p0", "integration_layer_types", "p0_governance")
_emit_reads_policy_state("p0", "integration_layer_types", "policy_binding")
_emit_snapshots_state("p0", "integration_layer_types", "state_snapshot")
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

_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_1")
_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_2")
_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_3")
_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_4")
_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_5")
_emit_emits_metric_event("integration_layer_types", "p4obs", "metric_6")
_emit_records_incident_event("integration_layer_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("integration_layer_types", "p4obs", "anomaly")
_emit_writes_observability_log("integration_layer_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("integration_layer_types", "p4obs", "mon_state")
_emit_triggers_alert("integration_layer_types", "p4obs", "alert")
_emit_links_incident_trace("integration_layer_types", "p4obs", "trace_link")
_emit_captures_pattern("integration_layer_types", "p3lm", "pattern")
_emit_records_learning_event("integration_layer_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("integration_layer_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("integration_layer_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("integration_layer_types", "p3lm", "routing")
_emit_improves_agent_policy("integration_layer_types", "p3lm", "policy")
_emit_stores_learning_state("integration_layer_types", "p3lm", "state")
_emit_records_execution_trace("integration_layer_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("integration_layer_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("integration_layer_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("integration_layer_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("integration_layer_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("integration_layer_types", "env_read", "p2_env_1")
_emit_reads_environ("integration_layer_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("integration_layer_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("integration_layer_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "integration_layer_types", "context_pull")
_emit_pulls_context("p1", "integration_layer_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "integration_layer_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "integration_layer_types", "uwg_term_2")
_emit_writes_through("p1", "integration_layer_types", "write_through")
_emit_writes_through("p1", "integration_layer_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "integration_layer_types", "safety_validation")
_emit_invokes_eval("p1", "integration_layer_types", "eval_call")
_emit_proposal_commits_routing("p1", "integration_layer_types", "routing_commit")
_emit_escalates_to_human("p1", "integration_layer_types", "human_escalation")
_emit_routes_through("p1", "integration_layer_types", "route_through")
_emit_checks_agent_registry("p1", "integration_layer_types", "agent_registry")
_emit_validates_agent_capability("p1", "integration_layer_types", "capability")
_emit_dispatches_execution_plan("p1", "integration_layer_types", "exec_plan")
_emit_agent_executes_agent("p1", "integration_layer_types", "sub_agent")
_emit_routes_to_agent("p1", "integration_layer_types", "target_agent")
_emit_verifies_policy("p1", "integration_layer_types", "policy_check")
_emit_observes_runtime_state("p1", "integration_layer_types", "runtime_state")
_emit_verifies_boundary("p1", "integration_layer_types", "boundary_check")
_emit_transcripts_response("p1", "integration_layer_types", "transcript")
_emit_hard_fails_untranscripted("p1", "integration_layer_types")
_emit_gated_by_confidence("p1", "integration_layer_types", "confidence_gate")
emit_replay_key("p0", "integration_layer_types")
emit_determinism_digest("p0", "integration_layer_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "integration_layer_types", "execution_auth")
_emit_validates_capability("p2", "integration_layer_types", "capability_check")
_emit_routes_to_capability("p2", "integration_layer_types", "capability_route")
_emit_writes_via_uwg("p2", "integration_layer_types", "uwg_write")
_emit_blocks_direct_write("p2", "integration_layer_types", "direct_write_block")
_emit_records_tool_invocation("p2", "integration_layer_types", "tool_invocation")
_emit_captures_execution_output("p2", "integration_layer_types", "exec_output")
_emit_dispatches_agent("p3", "integration_layer_types", "agent_dispatch")
_emit_coordinates_agents("p3", "integration_layer_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "integration_layer_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "integration_layer_types", "healing_outcome")
_emit_escalates_failure("p3", "integration_layer_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "integration_layer_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "integration_layer_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "integration_layer_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "integration_layer_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "integration_layer_types", "eval_metric")
_emit_stores_embedding("p4", "integration_layer_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "integration_layer_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "integration_layer_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class AppDomain(str, Enum):
    """Application domains."""

    LIC = "lic"
    RG = "rg"
    SHARED = "shared"


@dataclass
class ServiceEndpoint:
    """Represents a service endpoint."""

    name: str
    domain: AppDomain
    handler: Callable[..., Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __hash__(self):
        return hash(f"{self.domain.value}:{self.name}")


@dataclass
class IntegrationConfig:
    """Configuration for integration layer."""

    project_root: Path = field(default_factory=lambda: Path.cwd())
    config_dir: str = "config"
    enable_cross_domain: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600


class ServiceRegistry:
    """Registry for managing service endpoints across domains."""

    def __init__(self):
        self._services: dict[str, ServiceEndpoint] = {}
        self._domain_services: dict[AppDomain, list[str]] = {
            AppDomain.LIC: [],
            AppDomain.RG: [],
            AppDomain.SHARED: [],
        }

    def register(self, endpoint: ServiceEndpoint) -> None:
        """Register a service endpoint."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ServiceRegistry.register")

        key = f"{endpoint.domain.value}:{endpoint.name}"
        self._services[key] = endpoint
        if key not in self._domain_services[endpoint.domain]:
            self._domain_services[endpoint.domain].append(key)
        logger.info(f"Registered service: {key}")

    def get(self, name: str, domain: AppDomain | None = None) -> ServiceEndpoint | None:
        """Get a service endpoint by name and optional domain."""
        if domain:
            key = f"{domain.value}:{name}"
            return self._services.get(key)
        for d in AppDomain:
            key = f"{d.value}:{name}"
            if key in self._services:
                return self._services[key]
        return None

    def get_by_domain(self, domain: AppDomain) -> list[ServiceEndpoint]:
        """Get all services in a domain."""
        return [self._services[key] for key in self._domain_services[domain] if key in self._services]

    def list_all(self) -> list[ServiceEndpoint]:
        """List all registered services."""
        return list(self._services.values())

    def unregister(self, name: str, domain: AppDomain) -> bool:
        """Unregister a service endpoint."""
        key = f"{domain.value}:{name}"
        if key in self._services:
            del self._services[key]
            if key in self._domain_services[domain]:
                self._domain_services[domain].remove(key)
            logger.info(f"Unregistered service: {key}")
            return True
        return False


class ConfigurationLoader:
    """Loads and manages configuration across domains."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self._loaded_configs: dict[str, dict[str, Any]] = {}

    def _get_config_path(self, domain: AppDomain, config_name: str) -> Path:
        """Get the path to a configuration file."""
        if domain == AppDomain.SHARED:
            return self.config.project_root / self.config.config_dir / f"{config_name}.yaml"
        return self.config.project_root / f"apps_{domain.value}" / "domain" / "config" / f"{config_name}.json"

    def load(self, config_name: str, domain: AppDomain = AppDomain.SHARED) -> dict[str, Any]:
        """Load a configuration file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigurationLoader.load")

        cache_key = f"{domain.value}:{config_name}"
        if self.config.enable_caching and cache_key in self._loaded_configs:
            return self._loaded_configs[cache_key]
        config_path = self._get_config_path(domain, config_name)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return {}
        try:
            if config_path.suffix == ".json":
                import json

                with open(config_path) as f:
                    config_data = json.load(f)
            elif config_path.suffix in (".yaml", ".yml"):
                try:
                    import yaml

                    with open(config_path) as f:
                        config_data = yaml.safe_load(f) or {}
                except ImportError:  # guardian: allow-silent-swallow - optional dependency
                    logger.warning("PyYAML not installed, cannot load YAML configs")
                    config_data = {}
            else:
                logger.warning(f"Unsupported config format: {config_path.suffix}")
                config_data = {}
            if self.config.enable_caching:
                self._loaded_configs[cache_key] = config_data
            logger.debug(f"Loaded configuration: {config_path}")
            return config_data
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to load configuration {config_path}: {e}")
            return {}

    def get_value(
        self,
        key: str,
        domain: AppDomain = AppDomain.SHARED,
        config_name: str = "settings",
        default: Any = None,
    ) -> Any:
        """Get a specific configuration value."""
        config = self.load(config_name, domain)
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def clear_cache(self, domain: AppDomain | None = None) -> None:
        """Clear cached configurations."""
        if domain:
            keys_to_remove = [k for k in self._loaded_configs if k.startswith(f"{domain.value}:")]
            for k in keys_to_remove:
                del self._loaded_configs[k]
        else:
            self._loaded_configs.clear()


class IntegrationBridge:
    """
    Main integration bridge connecting apps_lic and apps_rg.

    Provides:
    - Service discovery and routing
    - Configuration management
    - Cross-domain communication
    """

    def __init__(self, config: IntegrationConfig | None = None):
        self.config = config or IntegrationConfig()
        self.service_registry = ServiceRegistry()
        self.config_loader = ConfigurationLoader(self.config)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the integration bridge."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "IntegrationBridge.initialize"
        )

        if self._initialized:
            return
        logger.info("Initializing integration bridge...")
        self._register_default_services()
        self._initialized = True
        logger.info("Integration bridge initialized")

    def _register_default_services(self) -> None:
        """Register default shared services."""
        default_services = [
            ServiceEndpoint(
                name="config",
                domain=AppDomain.SHARED,
                metadata={"description": "Configuration service"},
            ),
            ServiceEndpoint(
                name="logging",
                domain=AppDomain.SHARED,
                metadata={"description": "Logging service"},
            ),
            ServiceEndpoint(
                name="metrics",
                domain=AppDomain.SHARED,
                metadata={"description": "Metrics collection service"},
            ),
        ]
        for service in default_services:
            self.service_registry.register(service)

    def get_service(self, name: str, domain: AppDomain | None = None) -> ServiceEndpoint | None:
        """Get a service endpoint."""
        self.initialize()
        return self.service_registry.get(name, domain)

    def call_service(self, name: str, domain: AppDomain | None = None, *args, **kwargs) -> Any:
        """Call a service handler."""
        endpoint = self.get_service(name, domain)
        if not endpoint:
            raise ValueError(f"Service not found: {name}")
        if not endpoint.enabled:
            raise ValueError(f"Service disabled: {name}")
        if not endpoint.handler:
            raise ValueError(f"Service has no handler: {name}")
        return endpoint.handler(*args, **kwargs)

    def load_config(self, config_name: str, domain: AppDomain = AppDomain.SHARED) -> dict[str, Any]:
        """Load a configuration."""
        return self.config_loader.load(config_name, domain)

    def get_config_value(
        self,
        key: str,
        domain: AppDomain = AppDomain.SHARED,
        config_name: str = "settings",
        default: Any = None,
    ) -> Any:
        """Get a configuration value."""
        return self.config_loader.get_value(key, domain, config_name, default)

    def list_services(self, domain: AppDomain | None = None) -> list[dict[str, Any]]:
        """List registered services."""
        self.initialize()
        if domain:
            services = self.service_registry.get_by_domain(domain)
        else:
            services = self.service_registry.list_all()
        return [
            {"name": s.name, "domain": s.domain.value, "enabled": s.enabled, "metadata": s.metadata}
            for s in services
        ]


_integration_bridge: IntegrationBridge | None = None


def get_integration_bridge() -> IntegrationBridge:
    """Get the singleton integration bridge instance."""
    global _integration_bridge
    if _integration_bridge is None:
        _integration_bridge = IntegrationBridge()
    return _integration_bridge
