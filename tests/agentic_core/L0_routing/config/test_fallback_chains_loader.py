"""Tests for fallback_chains_loader.py module."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from agentic_core.L0_routing._archive.v12.config.fallback_chains_loader import (
    get_fallback_chain,
    get_slo_default,
    reset_cache,
    _MAX_CHAIN_DEPTH,
    _HARDCODED_CHAINS,
    _HARDCODED_SLO,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    FallbackEntry,
    RouteId,
    CostTier,
    RouteSLO,
    V12RouteContractError,
)


class TestGetFallbackChain:
    """Tests for get_fallback_chain function."""

    def test_get_fallback_chain_from_yaml(self):
        """Test loading fallback chain from YAML file."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": [
                    {"route_id": "R1A", "cost_tier": "TIER_S"},
                    {"route_id": "R5_FALLBACK", "cost_tier": "TIER_S"},
                ]
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            chain = get_fallback_chain("R3_GROUNDED")

            assert len(chain) == 2
            assert chain[0].route_id == RouteId.R1A
            assert chain[0].cost_tier == CostTier.TIER_S
            assert chain[1].route_id == RouteId.R5_FALLBACK
            assert chain[1].cost_tier == CostTier.TIER_S

    def test_get_fallback_chain_hardcoded_fallback(self):
        """Test hardcoded fallback when YAML is unavailable."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            chain = get_fallback_chain("R3_GROUNDED")

            # Should return hardcoded fallback
            assert isinstance(chain, tuple)
            assert all(isinstance(entry, FallbackEntry) for entry in chain)

    def test_get_fallback_chain_exceeds_max_depth(self):
        """Test that chains exceeding max depth raise error."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": [
                    {"route_id": "R1A", "cost_tier": "TIER_S"}
                    for _ in range(_MAX_CHAIN_DEPTH + 1)
                ]
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            with pytest.raises(V12RouteContractError):
                get_fallback_chain("R3_GROUNDED")

    def test_get_fallback_chain_invalid_route_id(self):
        """Test handling of invalid route_id in YAML."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": [
                    {"route_id": "INVALID_ROUTE", "cost_tier": "TIER_S"},
                ]
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            with pytest.raises(V12RouteContractError):
                get_fallback_chain("R3_GROUNDED")

    def test_get_fallback_chain_empty_chain(self):
        """Test handling of empty fallback chain."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": []
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            chain = get_fallback_chain("R3_GROUNDED")
            assert chain == ()

    def test_get_fallback_chain_route_id_as_string(self):
        """Test that route_id can be passed as string."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            chain = get_fallback_chain("R3_GROUNDED")
            assert isinstance(chain, tuple)

    def test_get_fallback_chain_route_id_as_enum(self):
        """Test that route_id can be passed as RouteId enum."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            chain = get_fallback_chain(RouteId.R3_GROUNDED)
            assert isinstance(chain, tuple)

    def test_get_fallback_chain_terminal_routes(self):
        """Test that terminal routes return empty chain."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            assert get_fallback_chain("R1A") == ()
            assert get_fallback_chain("R5_FALLBACK") == ()

    def test_get_fallback_chain_duplicate_entries(self):
        """Test that duplicate entries raise error."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": [
                    {"route_id": "R1A", "cost_tier": "TIER_S"},
                    {"route_id": "R1A", "cost_tier": "TIER_S"},
                ]
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            with pytest.raises(V12RouteContractError, match="duplicate"):
                get_fallback_chain("R3_GROUNDED")

    def test_get_fallback_chain_self_reference(self):
        """Test that self-referencing chains raise error."""
        yaml_data = {
            "chains": {
                "R3_GROUNDED": [
                    {"route_id": "R3_GROUNDED", "cost_tier": "TIER_M"},
                ]
            }
        }

        with patch(
            "agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml",
            return_value=yaml_data,
        ):
            reset_cache()
            with pytest.raises(V12RouteContractError, match="cycle"):
                get_fallback_chain("R3_GROUNDED")


class TestGetSloDefault:
    """Tests for get_slo_default function."""

    def test_get_slo_default_from_yaml_with_tier(self):
        """Test loading SLO default with tier from YAML file."""
        yaml_data = {
            "slo_defaults": {
                "R3_GROUNDED__TIER_S": {
                    "latency_budget_ms": 2000,
                    "token_budget_in": 4000,
                    "token_budget_out": 800,
                    "cost_cap_usd": 0.01,
                }
            }
        }

        with patch("builtins.open", mock_open()):
            with patch("yaml.safe_load", return_value=yaml_data):
                slo = get_slo_default("R3_GROUNDED", "TIER_S")

                assert slo.latency_budget_ms == 2000
                assert slo.token_budget_in == 4000
                assert slo.token_budget_out == 800
                assert slo.cost_cap_usd == 0.01

    def test_get_slo_default_from_yaml_route_only(self):
        """Test loading SLO default without tier from YAML file."""
        yaml_data = {
            "slo_defaults": {
                "R1A": {
                    "latency_budget_ms": 50,
                    "token_budget_in": 0,
                    "token_budget_out": 0,
                    "cost_cap_usd": 0.00,
                }
            }
        }

        with patch("builtins.open", mock_open()):
            with patch("yaml.safe_load", return_value=yaml_data):
                slo = get_slo_default("R1A", None)

                assert slo.latency_budget_ms == 50
                assert slo.token_budget_in == 0

    def test_get_slo_default_hardcoded_fallback(self):
        """Test hardcoded SLO defaults when YAML is unavailable."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            slo = get_slo_default("R1A", None)

            # Should return hardcoded defaults
            assert isinstance(slo, RouteSLO)
            assert slo.latency_budget_ms == 50

    def test_get_slo_default_missing_route(self):
        """Test that missing route raises error."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            with pytest.raises(V12RouteContractError, match="no SLO default"):
                get_slo_default("INVALID_ROUTE", None)

    def test_get_slo_default_route_id_as_string(self):
        """Test that route_id can be passed as string."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            slo = get_slo_default("R1A", None)
            assert isinstance(slo, RouteSLO)

    def test_get_slo_default_route_id_as_enum(self):
        """Test that route_id can be passed as RouteId enum."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            slo = get_slo_default(RouteId.R1A, None)
            assert isinstance(slo, RouteSLO)

    def test_get_slo_default_cost_tier_as_string(self):
        """Test that cost_tier can be passed as string."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            slo = get_slo_default("R3_GROUNDED", "TIER_S")
            assert isinstance(slo, RouteSLO)

    def test_get_slo_default_cost_tier_as_enum(self):
        """Test that cost_tier can be passed as CostTier enum."""
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            slo = get_slo_default("R3_GROUNDED", CostTier.TIER_S)
            assert isinstance(slo, RouteSLO)


class TestHardcodedFallbacks:
    """Tests for hardcoded fallback data structures."""

    def test_hardcoded_chains_structure(self):
        """Test that hardcoded fallback chains have correct structure."""
        assert isinstance(_HARDCODED_CHAINS, dict)
        for route_id, chain in _HARDCODED_CHAINS.items():
            assert isinstance(route_id, str)
            assert isinstance(chain, list)
            for entry in chain:
                assert isinstance(entry, dict)
                assert "route_id" in entry
                assert "cost_tier" in entry

    def test_hardcoded_slo_structure(self):
        """Test that hardcoded SLO defaults have correct structure."""
        assert isinstance(_HARDCODED_SLO, dict)
        for route_id, slo in _HARDCODED_SLO.items():
            assert isinstance(route_id, str)
            assert isinstance(slo, dict)

    def test_max_chain_depth_constant(self):
        """Test that _MAX_CHAIN_DEPTH is a positive integer."""
        assert isinstance(_MAX_CHAIN_DEPTH, int)
        assert _MAX_CHAIN_DEPTH > 0


class TestResetCache:
    """Tests for cache reset functionality."""

    def test_reset_cache(self):
        """Test that reset_cache clears the YAML cache."""
        # Load once to populate cache
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            get_fallback_chain("R3_GROUNDED")

        # Reset cache
        reset_cache()

        # Should work without error
        with patch("agentic_core.L0_routing._archive.v12.config.fallback_chains_loader._load_yaml", return_value={}):
            get_fallback_chain("R3_GROUNDED")


class TestFallbackEntryValidation:
    """Tests for FallbackEntry creation and validation."""

    def test_fallback_entry_creation(self):
        """Test creating FallbackEntry with valid data."""
        entry = FallbackEntry(
            route_id=RouteId.R1A,
            cost_tier=CostTier.TIER_S
        )
        assert entry.route_id == RouteId.R1A
        assert entry.cost_tier == CostTier.TIER_S

    def test_fallback_entry_with_provider(self):
        """Test creating FallbackEntry with optional provider."""
        entry = FallbackEntry(
            route_id=RouteId.R1A,
            cost_tier=CostTier.TIER_S,
            provider="openai"
        )
        assert entry.route_id == RouteId.R1A
        assert entry.provider == "openai"

    def test_fallback_entry_invalid_cost_tier(self):
        """Test handling of invalid cost tier."""
        with pytest.raises((ValueError, V12RouteContractError)):
            FallbackEntry(
                route_id=RouteId.R1A,
                cost_tier="INVALID_TIER"  # type: ignore
            )
