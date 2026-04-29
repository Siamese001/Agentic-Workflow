"""Hardening tests for agent registry phase files."""

from __future__ import annotations

from types import MappingProxyType

import pytest


@pytest.mark.unit
class TestAgentExecutionProfileTypes:
    """Tests for agent_execution_profile_types.py hardening."""

    def test_profile_construction_happy_path(self):
        from agentic_core.agents.types.agent_execution_profile_types import (
            AgentExecutionProfile,
            ExecutionMode,
            ReasoningIntensity,
        )

        p = AgentExecutionProfile(
            agent_id="  test_agent  ",
            reasoning_intensity=ReasoningIntensity.HIGH,
            execution_mode=ExecutionMode.DETERMINISTIC,
            allowed_models=(),
        )
        assert p.agent_id == "test_agent"
        assert p.reasoning_intensity == ReasoningIntensity.HIGH
        assert not p.is_llm_allowed()

    def test_deterministic_with_models_raises(self):
        from agentic_core.agents.types.agent_execution_profile_types import (
            AgentExecutionProfile,
            ExecutionMode,
            ReasoningIntensity,
        )

        with pytest.raises(ValueError, match="cannot have allowed_models"):
            AgentExecutionProfile(
                agent_id="x",
                reasoning_intensity=ReasoningIntensity.LOW,
                execution_mode=ExecutionMode.DETERMINISTIC,
                allowed_models=("gpt-4",),
            )

    def test_llm_api_without_models_raises(self):
        from agentic_core.agents.types.agent_execution_profile_types import (
            AgentExecutionProfile,
            ExecutionMode,
            ReasoningIntensity,
        )

        with pytest.raises(ValueError, match="must have allowed_models"):
            AgentExecutionProfile(
                agent_id="y",
                reasoning_intensity=ReasoningIntensity.HIGH,
                execution_mode=ExecutionMode.LLM_API,
                allowed_models=(),
            )

    def test_from_dict_missing_keys_raises(self):
        from agentic_core.agents.types.agent_execution_profile_types import AgentExecutionProfile

        with pytest.raises(KeyError, match="Missing required profile keys"):
            AgentExecutionProfile.from_dict({"agent_id": "x"})

    def test_allowed_models_deduplication_and_strip(self):
        from agentic_core.agents.types.agent_execution_profile_types import (
            AgentExecutionProfile,
            ExecutionMode,
            ReasoningIntensity,
        )

        p = AgentExecutionProfile(
            agent_id="llm_agent",
            reasoning_intensity=ReasoningIntensity.HIGH,
            execution_mode=ExecutionMode.LLM_API,
            allowed_models=("gpt-4", "gpt-4", "  gpt-4  "),
        )
        assert p.allowed_models == ("gpt-4",)

    def test_compute_registry_digest_is_deterministic_and_sha256(self):
        from agentic_core.agents.types.agent_execution_profile_types import (
            AgentExecutionProfile,
            ExecutionMode,
            ReasoningIntensity,
            compute_registry_digest,
        )

        p = AgentExecutionProfile(
            agent_id="z",
            reasoning_intensity=ReasoningIntensity.LOW,
            execution_mode=ExecutionMode.DETERMINISTIC,
            allowed_models=(),
        )
        d1 = compute_registry_digest({"z": p})
        d2 = compute_registry_digest({"z": p})
        assert d1 == d2
        assert len(d1) == 64


@pytest.mark.unit
class TestAgentRegistry:
    """Tests for agent_registry.py hardening."""

    def test_get_profile_returns_correct_profile(self):
        from agentic_core.agents.types.agent_registry import AGENT_REGISTRY, get_profile

        agent_id = next(iter(AGENT_REGISTRY))
        profile = get_profile(agent_id)
        assert profile.agent_id == agent_id

    def test_get_profile_unknown_agent_raises_key_error(self):
        from agentic_core.agents.types.agent_registry import get_profile

        with pytest.raises(KeyError, match="not found in registry"):
            get_profile("__nonexistent_agent_xyz__")

    def test_agent_registry_is_read_only_mapping_proxy(self):
        from agentic_core.agents.types.agent_registry import AGENT_REGISTRY

        assert isinstance(AGENT_REGISTRY, MappingProxyType)
        with pytest.raises(TypeError):
            AGENT_REGISTRY["__injected__"] = None  # type: ignore[index]

    def test_has_profile_empty_and_whitespace_returns_false(self):
        from agentic_core.agents.types.agent_registry import has_profile

        assert has_profile("") is False
        assert has_profile("   ") is False

    def test_list_agent_ids_is_sorted_tuple(self):
        from agentic_core.agents.types.agent_registry import list_agent_ids

        ids = list_agent_ids()
        assert isinstance(ids, tuple)
        assert len(ids) > 0
        assert list(ids) == sorted(ids)

    def test_registry_digest_is_deterministic_with_colon_separator(self):
        from agentic_core.agents.types.agent_registry import registry_digest

        d1 = registry_digest()
        d2 = registry_digest()
        assert d1 == d2
        assert all(":" in v for v in d1.values())

    def test_normalize_agent_id_rejects_whitespace_and_non_string(self):
        from agentic_core.agents.types.agent_registry import _normalize_agent_id

        with pytest.raises(ValueError):
            _normalize_agent_id("   ")
        with pytest.raises(TypeError):
            _normalize_agent_id(123)  # type: ignore[arg-type]


@pytest.mark.unit
class TestADGBackedRegistry:
    """Tests for adg_backed_registry.py hardening."""

    def _make_stub_engine(self, composition_index=None):
        class _StubEngine:
            def find_agents_by_base_class(self, base_class):
                return []

            def find_agents_by_capability(self, capability):
                return []

            def stats(self):
                return {"indexed_nodes": 10}

        stub = _StubEngine()
        if composition_index is not None:
            stub.composition_index = composition_index
        return stub

    def test_construction_with_valid_engine(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        engine = self._make_stub_engine({"MyCapability": ["agent_a"]})
        registry = ADGBackedAgentRegistry(engine)
        assert registry.query_engine is engine
        assert "MyCapability" in registry._capability_index

    def test_none_engine_raises_value_error(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        with pytest.raises(ValueError, match="query_engine is required"):
            ADGBackedAgentRegistry(None)  # type: ignore[arg-type]

    def test_engine_missing_method_raises_type_error(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        class _IncompleteEngine:
            def find_agents_by_base_class(self, b):
                return []

            def find_agents_by_capability(self, c):
                return []

        with pytest.raises(TypeError, match="must provide callable 'stats'"):
            ADGBackedAgentRegistry(_IncompleteEngine())  # type: ignore[arg-type]

    def test_capability_index_string_value_raises_type_error(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        engine = self._make_stub_engine({"bad_cap": "this_is_a_string_not_a_list"})
        with pytest.raises(TypeError, match="iterable collections"):
            ADGBackedAgentRegistry(engine)

    def test_stats_filters_non_integer_engine_values(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        class _BadStatsEngine:
            def find_agents_by_base_class(self, b):
                return []

            def find_agents_by_capability(self, c):
                return []

            def stats(self):
                return {"good_int": 5, "bad_float": 3.14, "bad_str": "text"}

        registry = ADGBackedAgentRegistry(_BadStatsEngine())
        result = registry.stats()
        assert result["good_int"] == 5
        assert "bad_float" not in result
        assert "bad_str" not in result

    def test_find_by_capability_returns_cached_entry(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        sentinel = object()
        engine = self._make_stub_engine({"CachedCap": [sentinel]})
        registry = ADGBackedAgentRegistry(engine)
        result = registry.find_by_capability("CachedCap")
        assert sentinel in result

    def test_find_by_base_class_empty_string_raises(self):
        from agentic_core.agents.types.adg_backed_registry import ADGBackedAgentRegistry

        registry = ADGBackedAgentRegistry(self._make_stub_engine())
        with pytest.raises(ValueError):
            registry.find_by_base_class("")


@pytest.mark.unit
class TestCompatShim:
    """Tests for _compat/agent_registry.py — shim must re-export canonical objects."""

    def test_compat_agent_registry_is_same_object_as_canonical(self):
        from agentic_core.agents._compat import agent_registry as compat
        from agentic_core.agents.types import agent_registry as canonical

        assert compat.AGENT_REGISTRY is canonical.AGENT_REGISTRY

    def test_compat_get_profile_is_same_callable_as_canonical(self):
        from agentic_core.agents._compat import agent_registry as compat
        from agentic_core.agents.types import agent_registry as canonical

        assert compat.get_profile is canonical.get_profile

    def test_compat_all_contains_required_exports(self):
        from agentic_core.agents._compat import agent_registry as compat

        required = {"AGENT_REGISTRY", "get_profile", "has_profile", "list_agent_ids", "registry_digest"}
        assert required.issubset(set(compat.__all__))
