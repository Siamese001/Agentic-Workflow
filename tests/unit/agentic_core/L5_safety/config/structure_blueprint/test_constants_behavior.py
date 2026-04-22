"""Behavioral tests for ``agentic_core.L5_safety.config.structure_blueprint._constants``.

Covers the declarative-constants module: TypedDict aliases, layer overrides,
runtime config maps (HEALING, AGENT_RESILIENCE, MISSION), MCP capability table,
and the GRAVITY registry that downstream agents consume.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from agentic_core.L5_safety.config.structure_blueprint import _constants as mod
from agentic_core.L5_safety.config.structure_blueprint._constants import (
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    LAYER_OVERRIDES,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
    SubfolderDefinition,
    TerritoryDefinition,
)


# ---- TypedDict re-exports --------------------------------------------

class TestTypedDicts:
    def test_subfolder_definition_importable(self) -> None:
        assert SubfolderDefinition is not None

    def test_territory_definition_importable(self) -> None:
        assert TerritoryDefinition is not None


# ---- LAYER_OVERRIDES -------------------------------------------------

class TestLayerOverrides:
    def test_is_mapping(self) -> None:
        assert isinstance(LAYER_OVERRIDES, Mapping)

    @pytest.mark.parametrize("layer", [
        "L0_routing", "L1_cognition", "L2_execution",
        "L3_orchestration", "L4_state", "L5_safety", "L6_observability",
    ])
    def test_all_seven_layers_present(self, layer: str) -> None:
        assert layer in LAYER_OVERRIDES

    def test_every_entry_has_purpose(self) -> None:
        for layer, spec in LAYER_OVERRIDES.items():
            assert "purpose" in spec, f"{layer} missing purpose"
            assert isinstance(spec["purpose"], str)


# ---- HEALING_CONFIG --------------------------------------------------

class TestHealingConfig:
    @pytest.mark.parametrize("key", [
        "max_rounds", "max_per_file", "global_budget", "dust_threshold",
    ])
    def test_required_keys(self, key: str) -> None:
        assert key in HEALING_CONFIG

    def test_values_are_ints(self) -> None:
        for k, v in HEALING_CONFIG.items():
            assert isinstance(v, int), f"{k}={v!r} not int"

    def test_values_are_positive(self) -> None:
        for k, v in HEALING_CONFIG.items():
            assert v > 0, f"{k}={v} not positive"


# ---- AGENT_RESILIENCE_CONFIG ----------------------------------------

class TestAgentResilienceConfig:
    def test_retry_count_is_int(self) -> None:
        assert isinstance(AGENT_RESILIENCE_CONFIG["retry_count"], int)

    def test_backoff_base_is_float(self) -> None:
        assert isinstance(AGENT_RESILIENCE_CONFIG["backoff_base"], float)

    def test_values_non_negative(self) -> None:
        assert AGENT_RESILIENCE_CONFIG["retry_count"] >= 0
        assert AGENT_RESILIENCE_CONFIG["backoff_base"] >= 0


# ---- MISSION_CONFIG --------------------------------------------------

class TestMissionConfig:
    @pytest.mark.parametrize("key", [
        "GRAVITY_SURGERY_ENABLED", "hierarchy_healing_enabled",
        "span_surgery_enabled", "timeout_seconds",
    ])
    def test_required_keys(self, key: str) -> None:
        assert key in MISSION_CONFIG

    def test_timeout_is_positive_int(self) -> None:
        assert isinstance(MISSION_CONFIG["timeout_seconds"], int)
        assert MISSION_CONFIG["timeout_seconds"] > 0


# ---- MCP_CAPABILITIES -----------------------------------------------

class TestMcpCapabilities:
    def test_is_mapping(self) -> None:
        assert isinstance(MCP_CAPABILITIES, Mapping)

    def test_router_entry_shape(self) -> None:
        router = MCP_CAPABILITIES["router"]
        assert "enabled" in router
        assert "path" in router
        assert isinstance(router["enabled"], bool)

    def test_every_entry_has_enabled_and_path(self) -> None:
        for name, spec in MCP_CAPABILITIES.items():
            assert "enabled" in spec, f"{name} missing 'enabled'"
            assert "path" in spec, f"{name} missing 'path'"


# ---- GRAVITY registry -----------------------------------------------

class TestGravityRegistry:
    def test_gravity_config_shape(self) -> None:
        assert GRAVITY_CONFIG["enabled"] is True
        assert GRAVITY_CONFIG["UPSTREAM_SOVEREIGN_ROOTS"] == ["agentic_core"]
        assert "apps_*" in GRAVITY_CONFIG["downstream_domains"]

    def test_surgery_enabled_derives_from_config(self) -> None:
        assert GRAVITY_SURGERY_ENABLED is GRAVITY_CONFIG["enabled"]

    def test_upstream_sovereign_roots_is_frozenset(self) -> None:
        assert isinstance(UPSTREAM_SOVEREIGN_ROOTS, frozenset)
        assert "agentic_core" in UPSTREAM_SOVEREIGN_ROOTS

    def test_downstream_roots_is_frozenset(self) -> None:
        assert isinstance(DOWNSTREAM_ROOTS, frozenset)
        assert "apps_*" in DOWNSTREAM_ROOTS
        assert "tests" in DOWNSTREAM_ROOTS


# ---- Public surface -------------------------------------------------

class TestPublicSurface:
    @pytest.mark.parametrize("name", [
        "SubfolderDefinition", "TerritoryDefinition",
        "LAYER_OVERRIDES",
        "HEALING_CONFIG", "AGENT_RESILIENCE_CONFIG", "MISSION_CONFIG",
        "MCP_CAPABILITIES",
        "GRAVITY_CONFIG", "GRAVITY_SURGERY_ENABLED",
        "UPSTREAM_SOVEREIGN_ROOTS", "DOWNSTREAM_ROOTS",
    ])
    def test_symbol_present(self, name: str) -> None:
        assert hasattr(mod, name)
