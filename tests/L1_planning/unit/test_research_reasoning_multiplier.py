"""
Tests for research planner unified reasoning-intensity multiplier logic.

Verifies that research planner uses cot_depth * tot_branches consistently
and that query expansion scales with reasoning intensity.
"""

from l1.outreach_dataclasses import (
    ArchetypeType,
    EXECUTIVE_REASONING_PROFILES,
    compute_reasoning_multiplier
)
from l1.research_planning import ResearchRefinementPlanner
from l1.outreach_archetype_planning import OutreachArchetypePlanner


class TestResearchReasoningMultiplier:
    """Test research planner unified reasoning multiplier functionality."""
    
    def test_unified_multiplier_logic_consistency(self):
        """Test that research planner uses unified cot_depth * tot_branches logic."""
        planner = ResearchRefinementPlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Test all archetypes
        for archetype in [ArchetypeType.RECRUITER, ArchetypeType.SENIOR_TA, 
                         ArchetypeType.EXECUTIVE, ArchetypeType.C_LEVEL]:
            
            # Create archetype context
            context = archetype_planner.build_archetype_context(
                target_title="Test Title",
                target_company="TestCorp",
                recipient_description="Test description"
            )
            context.archetype = archetype  # Override for testing
            context.executive_reasoning_profile = EXECUTIVE_REASONING_PROFILES[archetype]
            
            # Test query expansion uses unified multiplier
            cognitive_axes_queries = {
                "strategic": ["strategic query"],
                "financial": ["financial query"],
                "technical": ["technical query"]
            }
            
            expanded_queries = planner._expand_queries_with_reasoning_depth(
                cognitive_axes_queries, 
                context.executive_reasoning_profile
            )
            
            expected_multiplier = compute_reasoning_multiplier(context.executive_reasoning_profile)
            expected_total = len(cognitive_axes_queries) * expected_multiplier
            
            assert len(expanded_queries) == expected_total
            
            # Verify each query is expanded by multiplier
            for axis, queries in cognitive_axes_queries.items():
                for query in queries:
                    # Count variations of this query
                    variations = [q for q in expanded_queries if q.startswith(query)]
                    assert len(variations) == expected_multiplier
    
    def test_c_level_query_expansion_count(self):
        """Test C_LEVEL gets maximum query expansion."""
        planner = ResearchRefinementPlanner()
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        
        cognitive_axes_queries = {
            "strategic": ["strategic query"],
            "financial": ["financial query"],
            "technical": ["technical query"],
            "competitive": ["competitive query"]
        }
        
        expanded_queries = planner._expand_queries_with_reasoning_depth(
            cognitive_axes_queries, 
            c_level_profile
        )
        
        # C_LEVEL: 12 * 10 = 120 multiplier per query
        # 4 axes * 120 = 480 total queries
        assert len(expanded_queries) == 480
        
        # Verify depth variations
        strategic_variations = [q for q in expanded_queries if q.startswith("strategic query")]
        assert len(strategic_variations) == 120
        assert strategic_variations[0] == "strategic query (depth 1)"
        assert strategic_variations[-1] == "strategic query (depth 120)"
    
    def test_executive_query_expansion_count(self):
        """Test EXECUTIVE gets high query expansion."""
        planner = ResearchRefinementPlanner()
        executive_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        
        cognitive_axes_queries = {
            "strategic": ["strategic query"],
            "financial": ["financial query"]
        }
        
        expanded_queries = planner._expand_queries_with_reasoning_depth(
            cognitive_axes_queries, 
            executive_profile
        )
        
        # EXECUTIVE: 8 * 6 = 48 multiplier per query
        # 2 axes * 48 = 96 total queries
        assert len(expanded_queries) == 96
        
        # Verify depth variations
        strategic_variations = [q for q in expanded_queries if q.startswith("strategic query")]
        assert len(strategic_variations) == 48
    
    def test_senior_ta_query_expansion_count(self):
        """Test SENIOR_TA gets medium query expansion."""
        planner = ResearchRefinementPlanner()
        senior_ta_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA]
        
        cognitive_axes_queries = {
            "technical": ["technical query"]
        }
        
        expanded_queries = planner._expand_queries_with_reasoning_depth(
            cognitive_axes_queries, 
            senior_ta_profile
        )
        
        # SENIOR_TA: 4 * 3 = 12 multiplier per query
        # 1 axis * 12 = 12 total queries
        assert len(expanded_queries) == 12
    
    def test_recruiter_query_expansion_count(self):
        """Test RECRUITER gets low query expansion."""
        planner = ResearchRefinementPlanner()
        recruiter_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        
        cognitive_axes_queries = {
            "basic": ["basic query"]
        }
        
        expanded_queries = planner._expand_queries_with_reasoning_depth(
            cognitive_axes_queries, 
            recruiter_profile
        )
        
        # RECRUITER: 2 * 2 = 4 multiplier per query
        # 1 axis * 4 = 4 total queries
        assert len(expanded_queries) == 4
    
    def test_multi_axis_reasoning_plan_integration(self):
        """Test MultiAxisReasoningPlan uses unified multiplier."""
        planner = ResearchRefinementPlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Create C_LEVEL context
        context = archetype_planner.build_archetype_context(
            target_title="CEO",
            target_company="TechCorp",
            recipient_description="Chief Executive Officer"
        )
        
        # Generate multi-axis plan
        plan = planner.plan_multi_axis_research(
            target_person="John Doe",
            target_company="TechCorp",
            archetype_context=context
        )
        
        # Verify plan includes reasoning multiplier
        assert plan.reasoning_multiplier == 120  # C_LEVEL: 12 * 10
        assert plan.reasoning_intensity == "extreme"
        assert len(plan.cognitive_axes) == 8
        
        # Verify expanded queries count matches multiplier
        total_expected_queries = len(plan.cognitive_axes) * plan.reasoning_multiplier
        assert len(plan.expanded_queries) == total_expected_queries
    
    def test_reflexion_plan_scales_with_intensity(self):
        """Test ReflexionPlan scales with reasoning intensity."""
        planner = ResearchRefinementPlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Test C_LEVEL gets maximum reflexion passes
        c_level_context = archetype_planner.build_archetype_context(
            target_title="CEO",
            target_company="TechCorp",
            recipient_description="Chief Executive Officer"
        )
        
        reflexion_plan = planner.plan_reflexion_cycles(
            current_research=None,  # Mock for testing
            archetype_context=c_level_context,
            iteration=1
        )
        
        assert reflexion_plan.reflexion_passes == 3  # C_LEVEL
        assert reflexion_plan.reasoning_intensity == "extreme"
        assert len(reflexion_plan.critique_questions) > 0
        assert len(reflexion_plan.refinement_strategies) > 0
        
        # Test RECRUITER gets minimum reflexion passes
        recruiter_context = archetype_planner.build_archetype_context(
            target_title="Recruiter",
            target_company="TechCorp",
            recipient_description="Technical Recruiter"
        )
        
        reflexion_plan = planner.plan_reflexion_cycles(
            current_research=None,  # Mock for testing
            archetype_context=recruiter_context,
            iteration=1
        )
        
        assert reflexion_plan.reflexion_passes == 0  # RECRUITER
        assert reflexion_plan.reasoning_intensity == "low"
