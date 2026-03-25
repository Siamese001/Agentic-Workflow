"""
Unit tests for Integration Layer.

Tests Phase 3B - Integration Layer Implementation.
"""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_authorize_and_execute("p2", "test_integration_layer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_integration_layer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_integration_layer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_integration_layer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_integration_layer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_integration_layer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_integration_layer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_integration_layer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_integration_layer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_integration_layer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_integration_layer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_integration_layer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_integration_layer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_integration_layer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_integration_layer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_integration_layer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_integration_layer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_integration_layer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_integration_layer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_integration_layer", "exec_snapshot_link")
from apps_shared.types.integration_layer_types import (
    AppDomain,
    ConfigurationLoader,
    IntegrationBridge,
    IntegrationConfig,
    ServiceEndpoint,
    ServiceRegistry,
    get_integration_bridge,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_integration_layer")
# REMOVED: _emit_applies_guardrail("p0", "test_integration_layer", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_integration_layer", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_integration_layer", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_integration_layer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_integration_layer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_integration_layer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_integration_layer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_integration_layer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_integration_layer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_integration_layer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_integration_layer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_integration_layer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_integration_layer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_integration_layer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_integration_layer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_integration_layer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_integration_layer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_integration_layer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_integration_layer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_integration_layer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_integration_layer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_integration_layer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_integration_layer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_integration_layer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_integration_layer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_integration_layer", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_integration_layer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_integration_layer", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_integration_layer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_integration_layer", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_integration_layer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_integration_layer", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_integration_layer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_integration_layer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_integration_layer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_integration_layer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_integration_layer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_integration_layer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_integration_layer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_integration_layer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_integration_layer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_integration_layer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_integration_layer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_integration_layer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_integration_layer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_integration_layer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_integration_layer")
# REMOVED: _emit_gated_by_confidence("p1", "test_integration_layer", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_integration_layer")
# REMOVED: emit_determinism_digest("p0", "test_integration_layer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestAppDomain:
    """Test AppDomain enum."""

    def test_domain_values(self):
        """Test domain enum values."""
        assert AppDomain.LIC.value == "lic"
        assert AppDomain.RG.value == "rg"
        assert AppDomain.SHARED.value == "shared"


class TestServiceEndpoint:
    """Test ServiceEndpoint dataclass."""

    def test_endpoint_creation(self):
        """Test creating a service endpoint."""
        endpoint = ServiceEndpoint(
            name="test-service",
            domain=AppDomain.LIC,
            metadata={"key": "value"},
        )
        assert endpoint.name == "test-service"
        assert endpoint.domain == AppDomain.LIC
        assert endpoint.enabled is True
        assert endpoint.handler is None

    def test_endpoint_hash(self):
        """Test endpoint hashing for use in sets/dicts."""
        endpoint1 = ServiceEndpoint(name="svc", domain=AppDomain.LIC)
        endpoint2 = ServiceEndpoint(name="svc", domain=AppDomain.LIC)
        endpoint3 = ServiceEndpoint(name="svc", domain=AppDomain.RG)

        assert hash(endpoint1) == hash(endpoint2)
        assert hash(endpoint1) != hash(endpoint3)


class TestIntegrationConfig:
    """Test IntegrationConfig dataclass."""

    def test_config_defaults(self):
        """Test IntegrationConfig default values."""
        config = IntegrationConfig()
        assert config.config_dir == "config"
        assert config.enable_cross_domain is True
        assert config.enable_caching is True
        assert config.cache_ttl == 3600


class TestServiceRegistry:
    """Test ServiceRegistry functionality."""

    def test_register_and_get(self):
        """Test registering and getting a service."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.LIC)
        registry.register(endpoint)

        retrieved = registry.get("test", AppDomain.LIC)
        assert retrieved is endpoint

    def test_get_without_domain(self):
        """Test getting service without specifying domain."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.RG)
        registry.register(endpoint)

        retrieved = registry.get("test")
        assert retrieved is endpoint

    def test_get_nonexistent(self):
        """Test getting a nonexistent service."""
        registry = ServiceRegistry()
        result = registry.get("nonexistent", AppDomain.LIC)
        assert result is None

    def test_get_by_domain(self):
        """Test getting all services in a domain."""
        registry = ServiceRegistry()
        registry.register(ServiceEndpoint(name="svc1", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc2", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc3", domain=AppDomain.RG))

        lic_services = registry.get_by_domain(AppDomain.LIC)
        assert len(lic_services) == 2

        rg_services = registry.get_by_domain(AppDomain.RG)
        assert len(rg_services) == 1

    def test_list_all(self):
        """Test listing all services."""
        registry = ServiceRegistry()
        registry.register(ServiceEndpoint(name="svc1", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc2", domain=AppDomain.RG))

        all_services = registry.list_all()
        assert len(all_services) == 2

    def test_unregister(self):
        """Test unregistering a service."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.LIC)
        registry.register(endpoint)

        result = registry.unregister("test", AppDomain.LIC)
        assert result is True

        retrieved = registry.get("test", AppDomain.LIC)
        assert retrieved is None

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent service."""
        registry = ServiceRegistry()
        result = registry.unregister("nonexistent", AppDomain.LIC)
        assert result is False


class TestConfigurationLoader:
    """Test ConfigurationLoader functionality."""

    def test_get_config_path_shared(self):
        """Test config path generation for shared domain."""
        config = IntegrationConfig(project_root=Path("/project"))
        loader = ConfigurationLoader(config)

        path = loader._get_config_path(AppDomain.SHARED, "settings")
        # Use Path comparison for cross-platform compatibility
        expected = Path("/project") / "config" / "settings.yaml"
        assert path == expected

    def test_get_config_path_lic(self):
        """Test config path generation for LIC domain."""
        config = IntegrationConfig(project_root=Path("/project"))
        loader = ConfigurationLoader(config)

        path = loader._get_config_path(AppDomain.LIC, "agent_specs")
        expected = Path("/project") / APPS_LIC_DIR / "domain" / "config" / "agent_specs.json"
        assert path == expected

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent config file."""
        config = IntegrationConfig(project_root=Path("/nonexistent"))
        loader = ConfigurationLoader(config)

        result = loader.load("settings", AppDomain.SHARED)
        assert result == {}

    def test_caching(self):
        """Test configuration caching."""
        config = IntegrationConfig(enable_caching=True)
        loader = ConfigurationLoader(config)

        # Manually add to cache
        loader._loaded_configs["shared:test"] = {"cached": True}

        result = loader.load("test", AppDomain.SHARED)
        assert result == {"cached": True}

    def test_clear_cache_all(self):
        """Test clearing all cached configurations."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:test1"] = {}
        loader._loaded_configs["lic:test2"] = {}

        loader.clear_cache()
        assert len(loader._loaded_configs) == 0

    def test_clear_cache_by_domain(self):
        """Test clearing cached configurations by domain."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:test1"] = {}
        loader._loaded_configs["lic:test2"] = {}

        loader.clear_cache(AppDomain.LIC)

        assert "shared:test1" in loader._loaded_configs
        assert "lic:test2" not in loader._loaded_configs

    def test_get_value_nested(self):
        """Test getting nested configuration value."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:settings"] = {"database": {"host": "localhost", "port": 5432}}

        value = loader.get_value("database.host", AppDomain.SHARED, "settings")
        assert value == "localhost"

    def test_get_value_with_default(self):
        """Test getting value with default."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:settings"] = {}

        value = loader.get_value(
            "nonexistent.key",
            AppDomain.SHARED,
            "settings",
            default="default_value",
        )
        assert value == "default_value"


class TestIntegrationBridge:
    """Test IntegrationBridge functionality."""

    def test_initialization(self):
        """Test bridge initialization."""
        bridge = IntegrationBridge()
        assert bridge._initialized is False

        bridge.initialize()
        assert bridge._initialized is True

    def test_default_services_registered(self):
        """Test that default services are registered on init."""
        bridge = IntegrationBridge()
        bridge.initialize()

        services = bridge.list_services(AppDomain.SHARED)
        service_names = [s["name"] for s in services]

        assert "config" in service_names
        assert "logging" in service_names
        assert "metrics" in service_names

    def test_get_service(self):
        """Test getting a service."""
        bridge = IntegrationBridge()
        bridge.initialize()

        service = bridge.get_service("config", AppDomain.SHARED)
        assert service is not None
        assert service.name == "config"

    def test_call_service_with_handler(self):
        """Test calling a service with a handler."""
        bridge = IntegrationBridge()

        def test_handler(x, y):
            return x + y

        endpoint = ServiceEndpoint(
            name="adder",
            domain=AppDomain.LIC,
            handler=test_handler,
        )
        bridge.service_registry.register(endpoint)

        result = bridge.call_service("adder", AppDomain.LIC, 1, 2)
        assert result == 3

    def test_call_service_not_found(self):
        """Test calling a nonexistent service."""
        bridge = IntegrationBridge()

        with pytest.raises(ValueError, match="Service not found"):
            bridge.call_service("nonexistent")

    def test_call_service_disabled(self):
        """Test calling a disabled service."""
        bridge = IntegrationBridge()

        endpoint = ServiceEndpoint(
            name="disabled",
            domain=AppDomain.LIC,
            handler=lambda: None,
            enabled=False,
        )
        bridge.service_registry.register(endpoint)

        with pytest.raises(ValueError, match="Service disabled"):
            bridge.call_service("disabled", AppDomain.LIC)

    def test_call_service_no_handler(self):
        """Test calling a service without a handler."""
        bridge = IntegrationBridge()
        bridge.initialize()

        with pytest.raises(ValueError, match="has no handler"):
            bridge.call_service("config", AppDomain.SHARED)

    def test_list_services_all(self):
        """Test listing all services."""
        bridge = IntegrationBridge()
        bridge.initialize()

        services = bridge.list_services()
        assert len(services) >= 3  # At least the default services

    def test_list_services_by_domain(self):
        """Test listing services by domain."""
        bridge = IntegrationBridge()
        bridge.service_registry.register(ServiceEndpoint(name="lic-svc", domain=AppDomain.LIC))

        services = bridge.list_services(AppDomain.LIC)
        assert len(services) == 1
        assert services[0]["name"] == "lic-svc"


class TestGetIntegrationBridge:
    """Test get_integration_bridge singleton."""

    def test_singleton_instance(self):
        """Test that get_integration_bridge returns singleton."""
        import apps_shared.types.integration_layer_types as il_module

        il_module._integration_bridge = None

        bridge1 = get_integration_bridge()
        bridge2 = get_integration_bridge()

        assert bridge1 is bridge2

        il_module._integration_bridge = None
