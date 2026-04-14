"""Runtime-hardened tests for ``reasoning_intensity_types``."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


@pytest.fixture(scope="module")
def reasoning_symbols():
    module = pytest.importorskip("agentic_core.L0_routing.types.reasoning_intensity_types")
    return {
        "module": module,
        "ADG_COMPLEXITY_TIER_TABLE": module.ADG_COMPLEXITY_TIER_TABLE,
        "ReasoningTier": module.ReasoningTier,
        "StageTokenBudget": module.StageTokenBudget,
        "build_envelope_hash": module.build_envelope_hash,
        "build_profile_hash": module.build_profile_hash,
        "compute_complexity_tier": module.compute_complexity_tier,
    }


@pytest.fixture(scope="module")
def reasoning_path_table():
    module = pytest.importorskip("agentic_core.L2_execution.enforcement.SovereignLLMGateway")
    return module.REASONING_PATH_TABLE


class TestTopLevelExports:
    def test_reasoning_intensity_types_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "reasoning_intensity_types", None) is not None

    def test_reasoning_intensity_types_class_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "ReasoningIntensityTypes", None) is not None

    def test_validate_reasoning_intensity_types_is_callable(self, agentic_core_package):
        validator = getattr(agentic_core_package, "validate_reasoning_intensity_types", None)
        assert callable(validator)


class TestComputeComplexityTier:
    @pytest.mark.parametrize(
        ("node_count", "edge_count", "expected"),
        [
            (50, 100, "simple"),
            (300, 800, "moderate"),
            (1500, 5000, "complex"),
            (5000, 20000, "deep"),
            (100, 500, "simple"),
            (500, 2500, "moderate"),
            (2500, 10000, "deep"),
            (0, 0, "simple"),
            (50, 600, "moderate"),
        ],
    )
    def test_complexity_tier_resolution(self, reasoning_symbols, node_count, edge_count, expected):
        tier = reasoning_symbols["compute_complexity_tier"](
            adg_node_count=node_count,
            adg_edge_count=edge_count,
        )

        assert tier == expected


class TestADGComplexityTierTable:
    def test_table_has_expected_tiers(self, reasoning_symbols):
        table = reasoning_symbols["ADG_COMPLEXITY_TIER_TABLE"]

        assert set(table) >= {"simple", "moderate", "complex", "deep"}

    def test_simple_tier_parameters(self, reasoning_symbols):
        params = reasoning_symbols["ADG_COMPLEXITY_TIER_TABLE"]["simple"]

        assert params["max_adg_nodes"] == 100
        assert params["max_adg_edges"] == 500

    def test_complex_tier_has_limits(self, reasoning_symbols):
        params = reasoning_symbols["ADG_COMPLEXITY_TIER_TABLE"]["complex"]

        assert "max_adg_nodes" in params
        assert "max_adg_edges" in params


class TestReasoningPathTable:
    @pytest.mark.parametrize(
        ("tier", "path_id", "use_cot", "use_tot", "use_reflexion"),
        [
            ("simple", "simple_cot", True, False, False),
            ("moderate", "moderate_cot_hybrid", True, True, False),
            ("complex", "complex_tot_reflexion", True, True, False),
            ("deep", "deep_full_reasoning", None, True, True),
        ],
    )
    def test_path_table_expectations(
        self,
        reasoning_path_table,
        tier,
        path_id,
        use_cot,
        use_tot,
        use_reflexion,
    ):
        path = reasoning_path_table[tier]

        assert path.path_id == path_id
        if use_cot is not None:
            assert path.use_cot is use_cot
        assert path.use_tot is use_tot
        assert path.use_reflexion is use_reflexion


class TestProfileHashComputation:
    def test_profile_hash_computation(self, reasoning_symbols):
        profile_hash = reasoning_symbols["build_profile_hash"](
            version="1.0.0",
            policy_hash="policy123",
            tier=reasoning_symbols["ReasoningTier"].LOW,
            max_branches=1,
            max_depth=1,
            enable_reflection=False,
            token_budget_per_stage=[reasoning_symbols["StageTokenBudget"](stage_id=1, max_tokens=512)],
            allowed_modes=["cot"],
        )

        assert isinstance(profile_hash, str)
        assert len(profile_hash) == 64

    def test_envelope_hash_structure(self, reasoning_symbols):
        envelope_hash = reasoning_symbols["build_envelope_hash"](
            route_decision_trace_id="trace123",
            profile_hash="profile_hash_abc",
            policy_hash="policy_hash_def",
        )

        assert isinstance(envelope_hash, str)
        assert len(envelope_hash) == 64

    def test_envelope_hash_determinism(self, reasoning_symbols):
        hash1 = reasoning_symbols["build_envelope_hash"]("trace1", "profile1", "policy1")
        hash2 = reasoning_symbols["build_envelope_hash"]("trace1", "profile1", "policy1")

        assert hash1 == hash2

    def test_envelope_hash_uniqueness(self, reasoning_symbols):
        hash1 = reasoning_symbols["build_envelope_hash"]("trace1", "profile1", "policy1")
        hash2 = reasoning_symbols["build_envelope_hash"]("trace2", "profile1", "policy1")

        assert hash1 != hash2
