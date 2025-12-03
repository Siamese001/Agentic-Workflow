"""Tests for LIC Research Planner - L1 pure planning layer."""

import pytest
from unittest.mock import MagicMock

from l1.lic_research_planner import (
    LICResearchPlanner,
    LICResearchPlan,
    LICResearchHop,
)


@pytest.fixture
def mock_telemetry_bus():
    """Mock telemetry bus."""
    bus = MagicMock()
    bus.record_event = MagicMock()
    return bus


@pytest.fixture
def default_planner():
    """Default LIC research planner."""
    return LICResearchPlanner()


@pytest.fixture
def planner_with_telemetry(mock_telemetry_bus):
    """LIC research planner with telemetry."""
    return LICResearchPlanner(telemetry_bus=mock_telemetry_bus)


@pytest.fixture
def sample_outreach_context():
    """Sample outreach context for testing."""
    return {
        "recipient_profile": {
            "name": "John Doe",
            "role_title": "Senior Software Engineer",
        },
        "company_data": {
            "name": "TechCorp",
            "industry": "Technology",
        },
        "mission": "Test mission",
    }


class TestLICResearchPlanner:
    """Test suite for LIC research planner."""
    
    def test_creates_default_seed_queries(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that default seed queries are created correctly."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        expected_seed_queries = [
            "Senior Software Engineer responsibilities at TechCorp",
            "TechCorp strategy Senior Software Engineer",
            "TechCorp product roadmap",
        ]
        
        assert plan.seed_queries == expected_seed_queries
        assert len(plan.seed_queries) == 3
    
    def test_generates_correct_number_of_hops(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that the correct number of hops is generated."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        assert len(plan.hops) == 3  # Default max_hops
        assert plan.max_hops == 3
        
        # Check hop indices
        for i, hop in enumerate(plan.hops, start=1):
            assert hop.hop_index == i
    
    def test_semantic_first_hop_strategy(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that first hop uses semantic expansion strategy."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        first_hop = plan.hops[0]
        assert first_hop.expansion_strategy == "semantic"
        assert first_hop.requires_freshness is False
        assert "technical requirements" in first_hop.query_text
        assert first_hop.query_seed == plan.seed_queries[0]
    
    def test_temporal_second_hop_strategy(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that second hop uses temporal expansion strategy."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        second_hop = plan.hops[1]
        assert second_hop.expansion_strategy == "temporal"
        assert second_hop.requires_freshness is True
        assert "developments changes" in second_hop.query_text
        assert second_hop.query_seed == plan.seed_queries[1]
    
    def test_hybrid_later_hops(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that later hops use role_synonym or hybrid strategy."""
        plan = default_planner.plan(
            role_title="Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        third_hop = plan.hops[2]
        # Should be role_synonym since "engineer" is in role_title
        assert third_hop.expansion_strategy == "role_synonym"
        assert third_hop.requires_freshness is False
        assert "career growth" in third_hop.query_text
        assert third_hop.query_seed == plan.seed_queries[2]
    
    def test_expected_evidence_contains_funding_strategy_product(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that expected evidence contains required signal targets."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        for hop in plan.hops:
            assert "funding" in hop.expected_evidence
            assert "strategy" in hop.expected_evidence
            assert "product" in hop.expected_evidence
            assert "leadership moves" in hop.expected_evidence
            assert "hiring signals" in hop.expected_evidence
            assert "technology stack" in hop.expected_evidence
    
    def test_stop_condition_cache_when_enabled(
        self,
        planner_with_telemetry,
        sample_outreach_context,
    ):
        """Test that stop condition is cache_good_enough when cache critique enabled."""
        plan = planner_with_telemetry.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        assert plan.stop_condition == "cache_good_enough"
        assert plan.metadata["cache_critique_enabled"] is True
    
    def test_stop_condition_max_hops_when_disabled(
        self,
        sample_outreach_context,
    ):
        """Test that stop condition is max_hops when cache critique disabled."""
        planner = LICResearchPlanner(enable_cache_critique=False)
        
        plan = planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        assert plan.stop_condition == "max_hops"
        assert plan.metadata["cache_critique_enabled"] is False
    
    def test_metadata_contains_signal_targets(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that metadata contains required signal targets."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        assert "signal_targets" in plan.metadata
        signal_targets = plan.metadata["signal_targets"]
        expected_targets = ["funding", "product", "strategy", "personnel", "market"]
        assert signal_targets == expected_targets
        
        # Check other metadata fields
        assert plan.metadata["cache_critique_enabled"] is True
        assert plan.metadata["temporal_signal_enabled"] is True
        assert plan.metadata["synonym_expansion_enabled"] is True
    
    def test_plan_is_pure_and_has_no_execution(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that plan is pure with no external execution calls."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Verify plan structure
        assert isinstance(plan, LICResearchPlan)
        assert plan.role_title == "Senior Software Engineer"
        assert plan.company_name == "TechCorp"
        assert len(plan.seed_queries) == 3
        assert len(plan.hops) == 3
        
        # Verify all hops are pure data
        for hop in plan.hops:
            assert isinstance(hop, LICResearchHop)
            assert isinstance(hop.query_text, str)
            assert isinstance(hop.query_seed, str)
            assert isinstance(hop.expansion_strategy, str)
            assert isinstance(hop.requires_freshness, bool)
            assert isinstance(hop.expected_evidence, list)
            assert isinstance(hop.metadata, dict)
    
    def test_custom_max_hops_configuration(
        self,
        sample_outreach_context,
    ):
        """Test custom max_hops configuration."""
        planner = LICResearchPlanner(max_hops=5)
        
        plan = planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        assert len(plan.hops) == 5
        assert plan.max_hops == 5
        
        # Verify hop indices
        for i, hop in enumerate(plan.hops, start=1):
            assert hop.hop_index == i
    
    def test_temporal_signal_disabled_configuration(
        self,
        sample_outreach_context,
    ):
        """Test configuration with temporal signal disabled."""
        planner = LICResearchPlanner(enable_temporal_signal=False)
        
        plan = planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Second hop should not be temporal when disabled
        second_hop = plan.hops[1]
        assert second_hop.expansion_strategy != "temporal"
        assert second_hop.requires_freshness is False
        assert plan.metadata["temporal_signal_enabled"] is False
    
    def test_synonym_expansion_disabled_configuration(
        self,
        sample_outreach_context,
    ):
        """Test configuration with synonym expansion disabled."""
        planner = LICResearchPlanner(enable_synonym_expansion=False)
        
        plan = planner.plan(
            role_title="Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Third hop should be hybrid when synonym disabled
        third_hop = plan.hops[2]
        assert third_hop.expansion_strategy == "hybrid"
        assert plan.metadata["synonym_expansion_enabled"] is False
    
    def test_telemetry_recording(
        self,
        planner_with_telemetry,
        sample_outreach_context,
        mock_telemetry_bus,
    ):
        """Test that telemetry is recorded correctly."""
        plan = planner_with_telemetry.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Verify telemetry was recorded
        mock_telemetry_bus.record_event.assert_called_once_with(
            "lic_research_plan_created",
            layer="L1",
            payload={
                "role_title": "Senior Software Engineer",
                "company_name": "TechCorp",
                "max_hops": 3,
                "stop_condition": "cache_good_enough",
                "hop_count": 3,
                "cache_critique_enabled": True,
            },
        )
    
    def test_telemetry_error_handling(
        self,
        planner_with_telemetry,
        sample_outreach_context,
    ):
        """Test that telemetry errors don't break planning."""
        # Make telemetry bus raise exceptions
        planner_with_telemetry.telemetry_bus.record_event.side_effect = Exception("Telemetry failed")
        
        # Planning should still work despite telemetry failure
        plan = planner_with_telemetry.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Should still produce valid plan
        assert isinstance(plan, LICResearchPlan)
        assert len(plan.hops) == 3
        assert plan.role_title == "Senior Software Engineer"
    
    def test_query_expansion_strategies_deterministic(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that query expansion is deterministic."""
        plan1 = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        plan2 = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        # Plans should be identical (deterministic)
        assert plan1.seed_queries == plan2.seed_queries
        assert len(plan1.hops) == len(plan2.hops)
        
        for hop1, hop2 in zip(plan1.hops, plan2.hops):
            assert hop1.query_text == hop2.query_text
            assert hop1.expansion_strategy == hop2.expansion_strategy
            assert hop1.requires_freshness == hop2.requires_freshness
    
    def test_hop_metadata_structure(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test that hop metadata contains required fields."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            outreach_context=sample_outreach_context,
        )
        
        for hop in plan.hops:
            assert "expansion_applied" in hop.metadata
            assert "role_aware" in hop.metadata
            assert "vector_first" in hop.metadata
            assert hop.metadata["expansion_applied"] is True
            assert hop.metadata["role_aware"] is True
            assert hop.metadata["vector_first"] is True
    
    def test_different_role_titles_and_companies(
        self,
        default_planner,
        sample_outreach_context,
    ):
        """Test planner with different role titles and companies."""
        test_cases = [
            ("Product Manager", "StartupCo"),
            ("Data Scientist", "DataCorp"),
            ("DevOps Engineer", "CloudTech"),
        ]
        
        for role_title, company_name in test_cases:
            plan = default_planner.plan(
                role_title=role_title,
                company_name=company_name,
                outreach_context=sample_outreach_context,
            )
            
            assert plan.role_title == role_title
            assert plan.company_name == company_name
            assert len(plan.hops) == 3
            
            # Check seed queries are properly formatted
            assert role_title in plan.seed_queries[0]
            assert company_name in plan.seed_queries[0]
            assert company_name in plan.seed_queries[1]
            assert company_name in plan.seed_queries[2]


if __name__ == "__main__":
    pytest.main([__file__])
