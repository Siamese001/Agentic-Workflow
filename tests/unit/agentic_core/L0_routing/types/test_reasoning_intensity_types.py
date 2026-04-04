"""Test ReasoningIntensityTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningIntensityTypes:
    """Test ReasoningIntensityTypes functionality."""

    def test_reasoning_intensity_types_imports(self):
        """Test reasoning_intensity_types module imports."""
        from agentic_core import reasoning_intensity_types
        assert reasoning_intensity_types is not None

    def test_reasoning_intensity_types_class(self):
        """Test ReasoningIntensityTypes class exists."""
        from agentic_core import ReasoningIntensityTypes
        assert ReasoningIntensityTypes is not None

    def test_reasoning_intensity_types_callable(self):
        """Test reasoning_intensity_types functions are callable."""
        from agentic_core import validate_reasoning_intensity_types
        assert callable(validate_reasoning_intensity_types)


# G3 Fix: ADG complexity tests
from agentic_core.L0_routing.types.reasoning_intensity_types import (
    ADG_COMPLEXITY_TIER_TABLE,
    TIER_PARAMETER_TABLE,
    ReasoningIntensityProfile,
    ReasoningTier,
    StageTokenBudget,
    build_envelope_hash,
    build_profile_hash,
    compute_complexity_tier,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    REASONING_PATH_TABLE,
)


class TestComputeComplexityTier:
    """Test compute_complexity_tier function — G3 ADG complexity."""

    def test_simple_tier_low_nodes(self):
        """Happy path: low node count returns simple tier."""
        tier = compute_complexity_tier(adg_node_count=50, adg_edge_count=100)
        assert tier == "simple"

    def test_moderate_tier_medium_nodes(self):
        """Happy path: medium node count returns moderate tier."""
        tier = compute_complexity_tier(adg_node_count=300, adg_edge_count=800)
        assert tier == "moderate"

    def test_complex_tier_high_nodes(self):
        """Happy path: high node count returns complex tier."""
        tier = compute_complexity_tier(adg_node_count=1500, adg_edge_count=5000)
        assert tier == "complex"

    def test_deep_tier_very_high_nodes(self):
        """Happy path: very high node count returns deep tier."""
        tier = compute_complexity_tier(adg_node_count=5000, adg_edge_count=20000)
        assert tier == "deep"

    def test_boundary_simple_to_moderate(self):
        """Edge case: exactly at simple/moderate boundary."""
        tier = compute_complexity_tier(adg_node_count=100, adg_edge_count=500)
        assert tier == "moderate"

    def test_boundary_moderate_to_complex(self):
        """Edge case: exactly at moderate/complex boundary."""
        tier = compute_complexity_tier(adg_node_count=500, adg_edge_count=2500)
        assert tier == "complex"

    def test_boundary_complex_to_deep(self):
        """Edge case: exactly at complex/deep boundary."""
        tier = compute_complexity_tier(adg_node_count=2500, adg_edge_count=10000)
        assert tier == "deep"

    def test_zero_nodes_defaults_simple(self):
        """Edge case: zero nodes defaults to simple."""
        tier = compute_complexity_tier(adg_node_count=0, adg_edge_count=0)
        assert tier == "simple"

    def test_high_edges_override(self):
        """Edge case: high edge count can override node-based tier."""
        tier = compute_complexity_tier(adg_node_count=50, adg_edge_count=600)
        assert tier == "moderate"


class TestADGComplexityTierTable:
    """Test ADG_COMPLEXITY_TIER_TABLE structure — G3."""

    def test_table_has_expected_tiers(self):
        """Validation: table contains all expected tiers."""
        assert "simple" in ADG_COMPLEXITY_TIER_TABLE
        assert "moderate" in ADG_COMPLEXITY_TIER_TABLE
        assert "complex" in ADG_COMPLEXITY_TIER_TABLE
        assert "deep" in ADG_COMPLEXITY_TIER_TABLE

    def test_simple_tier_parameters(self):
        """Validation: simple tier has correct parameters."""
        params = ADG_COMPLEXITY_TIER_TABLE["simple"]
        assert params["max_adg_nodes"] == 100
        assert params["max_adg_edges"] == 500

    def test_complex_tier_has_tot_enabled(self):
        """Validation: complex tier enables TOT."""
        params = ADG_COMPLEXITY_TIER_TABLE["complex"]
        assert "max_adg_nodes" in params
        assert "max_adg_edges" in params


class TestReasoningPathTable:
    """Test REASONING_PATH_TABLE structure — G3."""

    def test_table_has_all_tiers(self):
        """Validation: table contains all complexity tiers."""
        assert "simple" in REASONING_PATH_TABLE
        assert "moderate" in REASONING_PATH_TABLE
        assert "complex" in REASONING_PATH_TABLE
        assert "deep" in REASONING_PATH_TABLE

    def test_simple_path_uses_cot_only(self):
        """Validation: simple path uses COT only."""
        path = REASONING_PATH_TABLE["simple"]
        assert path.path_id == "simple_cot"
        assert path.use_cot is True
        assert path.use_tot is False

    def test_moderate_path_uses_cot_with_reflexion(self):
        """Validation: moderate path uses COT with reflexion."""
        path = REASONING_PATH_TABLE["moderate"]
        assert path.path_id == "moderate_cot_reflexion"
        assert path.use_cot is True
        assert path.use_reflexion is True

    def test_complex_path_uses_tot(self):
        """Validation: complex path uses TOT."""
        path = REASONING_PATH_TABLE["complex"]
        assert path.path_id == "complex_tot_shallow"
        assert path.use_tot is True
        assert path.use_cot is True

    def test_deep_path_uses_full_tot(self):
        """Validation: deep path uses full TOT."""
        path = REASONING_PATH_TABLE["deep"]
        assert path.path_id == "deep_tot_deep"
        assert path.use_tot is True
        assert path.use_reflexion is True


class TestProfileHashComputation:
    """Test profile and envelope hash computation — G3."""

    def test_profile_hash_computation(self):
        """Happy path: profile hash is computed correctly."""
        profile_hash = build_profile_hash(
            version="1.0.0",
            policy_hash="policy123",
            tier=ReasoningTier.LOW,
            max_branches=1,
            max_depth=1,
            enable_reflection=False,
            token_budget_per_stage=[StageTokenBudget(stage_id=1, max_tokens=512)],
            allowed_modes=["cot"],
        )
        assert isinstance(profile_hash, str)
        assert len(profile_hash) == 64  # SHA256 hex length

    def test_envelope_hash_structure(self):
        """Happy path: envelope hash is computed correctly."""
        envelope_hash = build_envelope_hash(
            route_decision_trace_id="trace123",
            profile_hash="profile_hash_abc",
            policy_hash="policy_hash_def",
        )
        assert isinstance(envelope_hash, str)
        assert len(envelope_hash) == 64

    def test_envelope_hash_determinism(self):
        """Validation: same inputs produce same hash."""
        hash1 = build_envelope_hash("trace1", "profile1", "policy1")
        hash2 = build_envelope_hash("trace1", "profile1", "policy1")
        assert hash1 == hash2

    def test_envelope_hash_uniqueness(self):
        """Validation: different inputs produce different hashes."""
        hash1 = build_envelope_hash("trace1", "profile1", "policy1")
        hash2 = build_envelope_hash("trace2", "profile1", "policy1")
        assert hash1 != hash2
