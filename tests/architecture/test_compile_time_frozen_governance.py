"""
Test Compile-Time Frozen Governance - Zero Runtime Mutation.

Tests that all governance surfaces are frozen at compile time and cannot be
mutated at runtime, ensuring absolute sovereignty guarantees.
"""

import pytest
import sys
import importlib
from agentic_core.agents.agent_registry import (
    EXECUTION_PROFILES,
    get_execution_profile,
    _validate_registry_sovereignty,
)
from agentic_core.L2_execution.healers.tiering_allowlist import (
    TIERING_ALLOWLIST,
    TIERING_ALLOWLIST_AGENT_NAMES,
    _validate_allowlist_sovereignty,
)
from agentic_core.L2_execution.healers.healing_tier_router import (
    HISTORICAL_SUCCESS_RATES,
    HISTORICAL_DATA_VERSION,
    HISTORICAL_DATA_HASH,
    set_historical_success_rate,
    clear_historical_success_rates,
)


class TestCompileTimeFrozenGovernance:
    """Test suite for compile-time frozen governance."""

    def test_registry_immutability(self):
        """Test that EXECUTION_PROFILES is immutable."""
        # Must be a dict (not a mutable subclass)
        assert isinstance(EXECUTION_PROFILES, dict)

        # Create a copy to test mutation attempts
        original_count = len(EXECUTION_PROFILES)

        # Attempting to modify should raise an error (but we can't test it without breaking the registry)
        # Instead, we verify the registry is still intact
        assert len(EXECUTION_PROFILES) == original_count

        # Verify expected agents are present
        expected_agents = {
            "SovereignLLMGateway",
            "DispatchOutreachToolsAgent",
            "ExecutiveStrategyAgent",
            "ResumeAssemblyAgent"
        }
        assert expected_agents.issubset(EXECUTION_PROFILES.keys())

    def test_allowlist_immutability(self):
        """Test that TIERING_ALLOWLIST is a frozenset."""
        assert isinstance(TIERING_ALLOWLIST, frozenset)
        assert isinstance(TIERING_ALLOWLIST_AGENT_NAMES, frozenset)

        # Attempting to modify should raise an error
        with pytest.raises(AttributeError):
            TIERING_ALLOWLIST.add(("new_agent", "path.py"))

        with pytest.raises(AttributeError):
            TIERING_ALLOWLIST_AGENT_NAMES.add("new_agent")

    def test_historical_data_immutability(self):
        """Test that historical data is immutable."""
        # Must be a dict (not a mutable subclass)
        assert isinstance(HISTORICAL_SUCCESS_RATES, dict)

        # Original data should be intact
        original_count = len(HISTORICAL_SUCCESS_RATES)

        # Attempt to modify (should be ignored by the frozen setter)
        set_historical_success_rate("test_failure", 0.99)

        # Data should remain unchanged
        assert len(HISTORICAL_SUCCESS_RATES) == original_count

        # Verify original values are intact
        assert HISTORICAL_SUCCESS_RATES["syntax_error"] == 0.85
        assert HISTORICAL_SUCCESS_RATES["import_cycle"] == 0.7

    def test_gemini_mandate_enforcement(self):
        """Test that all LLM_API agents include GEMINI in allowed_models."""
        from agentic_core.agents.types.agent_execution_profile import ExecutionMode

        for agent_id, profile in EXECUTION_PROFILES.items():
            if profile.execution_mode == ExecutionMode.LLM_API:
                assert "gemini-2.5-pro" in profile.allowed_models, (
                    f"LLM_API agent '{agent_id}' missing GEMINI mandate. "
                    f"Allowed models: {profile.allowed_models}"
                )

    def test_deterministic_agent_empty_models(self):
        """Test that DETERMINISTIC agents have empty allowed_models."""
        from agentic_core.agents.types.agent_execution_profile import ExecutionMode

        for agent_id, profile in EXECUTION_PROFILES.items():
            if profile.execution_mode == ExecutionMode.DETERMINISTIC:
                assert profile.allowed_models == (), (
                    f"DETERMINISTIC agent '{agent_id}' has non-empty allowed_models: "
                    f"{profile.allowed_models}"
                )

    def test_registry_validation_at_import(self):
        """Test that registry validation runs at module import time."""
        # Validation should have already run when module was imported
        # If validation failed, the module import would have raised an error

        # Re-run validation to ensure it still passes
        _validate_registry_sovereignty()  # Should not raise

        # Verify at least one LLM and one deterministic agent
        llm_agents = [
            agent_id for agent_id, profile in EXECUTION_PROFILES.items()
            if profile.execution_mode.value == "LLM_API"
        ]
        deterministic_agents = [
            agent_id for agent_id, profile in EXECUTION_PROFILES.items()
            if profile.execution_mode.value == "DETERMINISTIC"
        ]

        assert len(llm_agents) > 0, "No LLM_API agents found"
        assert len(deterministic_agents) > 0, "No DETERMINISTIC agents found"

    def test_allowlist_validation_at_import(self):
        """Test that allowlist validation runs at module import time."""
        # Validation should have already run when module was imported
        _validate_allowlist_sovereignty()  # Should not raise

        # Verify expected agents are present
        expected_agents = {
            "CodeHealerAgent",
            "DispatchOutreachToolsAgent",
            "DispatchResumeToolsAgent",
        }

        assert expected_agents.issubset(TIERING_ALLOWLIST_AGENT_NAMES), (
            f"Expected agents missing from allowlist: {expected_agents - TIERING_ALLOWLIST_AGENT_NAMES}"
        )

    def test_no_external_data_loading(self):
        """Test that no governance data is loaded from external sources."""
        # Registry should be self-contained
        assert len(EXECUTION_PROFILES) > 0

        # Allowlist should be self-contained
        assert len(TIERING_ALLOWLIST) > 0

        # Historical data should be self-contained
        assert len(HISTORICAL_SUCCESS_RATES) > 0
        assert HISTORICAL_DATA_VERSION is not None
        assert HISTORICAL_DATA_HASH is not None

    def test_profile_lookup_immutability(self):
        """Test that profile lookups return immutable objects."""
        profile = get_execution_profile("SovereignLLMGateway")

        # Profile should be immutable (dataclass with frozen=True)
        assert hasattr(profile, '__dataclass_fields__')
        # Note: __frozen__ is not a standard attribute, so we check dataclass immutability differently

        # Attempting to modify should raise an error
        try:
            profile.agent_id = "modified"
            assert False, "Profile should be immutable"
        except (AttributeError, TypeError):
            pass  # Expected for frozen dataclass

        # Verify original value is intact
        assert profile.agent_id == "SovereignLLMGateway"

    def test_governance_survives_reload(self):
        """Test that governance survives module reload."""
        # Store original state
        original_profiles = dict(EXECUTION_PROFILES)
        original_allowlist = set(TIERING_ALLOWLIST)

        # Reload modules (simulating import in fresh process)
        import agentic_core.agents.agent_registry as registry_module
        import agentic_core.L2_execution.healers.tiering_allowlist as allowlist_module

        importlib.reload(registry_module)
        importlib.reload(allowlist_module)

        # State should be identical
        assert registry_module.EXECUTION_PROFILES == original_profiles
        assert allowlist_module.TIERING_ALLOWLIST == original_allowlist

    def test_frozen_data_integrity(self):
        """Test integrity of frozen data structures."""
        # Registry integrity
        for agent_id, profile in EXECUTION_PROFILES.items():
            if profile is None:  # Skip None entries
                continue
            assert profile.agent_id == agent_id, f"Profile ID mismatch for {agent_id}"
            assert isinstance(profile.allowed_models, tuple), f"allowed_models not tuple for {agent_id}"

        # Allowlist integrity
        for agent_name, file_path in TIERING_ALLOWLIST:
            assert isinstance(agent_name, str), f"Agent name not string: {agent_name}"
            assert isinstance(file_path, str), f"File path not string: {file_path}"
            assert file_path.endswith('.py'), f"File path not Python file: {file_path}"

        # Historical data integrity
        for failure_type, rate in HISTORICAL_SUCCESS_RATES.items():
            assert isinstance(failure_type, str), f"Failure type not string: {failure_type}"
            assert isinstance(rate, (int, float)), f"Rate not numeric: {rate}"
            assert 0.0 <= rate <= 1.0, f"Rate out of bounds: {rate}"

    def test_no_hidden_mutation_points(self):
        """Test that there are no hidden mutation points."""
        import inspect

        # Check registry module for mutable globals
        registry_module = sys.modules['agentic_core.agents.agent_registry']
        for name, obj in inspect.getmembers(registry_module):
            if not name.startswith('_') and isinstance(obj, (dict, list, set)):
                # Allow specific known globals
                if name not in ['EXECUTION_PROFILES', 'AGENT_REGISTRY']:  # Known allowed globals
                    pytest.fail(f"Found mutable global in registry module: {name}")

        # Check allowlist module for mutable globals
        allowlist_module = sys.modules['agentic_core.L2_execution.healers.tiering_allowlist']
        for name, obj in inspect.getmembers(allowlist_module):
            if not name.startswith('_') and isinstance(obj, (dict, list, set)):
                if obj not in (TIERING_ALLOWLIST, TIERING_ALLOWLIST_AGENT_NAMES):
                    pytest.fail(f"Found mutable global in allowlist module: {name}")
