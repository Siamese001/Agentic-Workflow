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
from l1.research_planning import ResearchRefinementPlanner, ResearchResult
from l1.outreach_archetype_planning import OutreachArchetypePlanner, RecipientProfile, OutreachMission


class TestResearchReasoningMultiplier:
    """Test research planner unified reasoning multiplier functionality."""
    
    def test_unified_multiplier_logic_consistency(self):
        """Test that research planner uses unified cot_depth * tot_branches logic."""
        planner = ResearchRefinementPlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Test all archetypes
        for archetype in [ArchetypeType.RECRUITER, ArchetypeType.SENIOR_TA, 
                         ArchetypeType.EXECUTIVE, ArchetypeType.C_LEVEL]:
            
            # Create archetype context using RecipientProfile and OutreachMission
            recipient = RecipientProfile(
                name="Test Person", title="Test Title", company="TestCorp", industry="Technology",
                seniority="Mid-level", department="Engineering", skills=["testing"],
                recent_activity=[], metadata={}
            )
            
            mission = OutreachMission(
                objective="Testing", target_role="Test Title",
                value_proposition="Test value", urgency="medium",
                personalization_points=[], constraints=["basic"], metadata={}
            )
            
            context = archetype_planner.build_archetype_context(recipient, mission)
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
        
        # Create C_LEVEL context using RecipientProfile and OutreachMission
        recipient = RecipientProfile(
            name="John Doe", title="CEO", company="TechCorp", industry="Technology",
            seniority="Executive", department="Executive", skills=["leadership"],
            recent_activity=[], metadata={}
        )
        
        mission = OutreachMission(
            objective="Strategic partnership", target_role="CEO",
            value_proposition="Strategic leadership", urgency="high",
            personalization_points=[], constraints=["formal"], metadata={}
        )
        
        context = archetype_planner.build_archetype_context(recipient, mission)
        
        # Generate multi-axis plan
        plan = planner.plan_multi_axis_research(
            base_query="John Doe",
            archetype_context=context,
            target_company="TechCorp"
        )
        
        # Verify plan includes reasoning multiplier
        assert plan.cot_depth_multiplier == 12  # C_LEVEL: 12
        assert plan.tot_recursion_multiplier == 4  # C_LEVEL: actual value
        assert plan.reasoning_intensity == "extreme"
        assert len(plan.cognitive_axes) == 8
        
        # Verify expanded queries count matches multiplier
        # 8 axes × 3 base queries per axis = 24 base queries
        # Each base query expands by reasoning multiplier (12 × 10 = 120)
        # Total: 24 × 120 = 2880 expanded queries
        total_expected_queries = 2880
        assert len(plan.expanded_subqueries) == total_expected_queries
    
    def test_reflexion_plan_scales_with_intensity(self):
        """Test ReflexionPlan scales with reasoning intensity."""
        planner = ResearchRefinementPlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Test C_LEVEL gets maximum reflexion passes using RecipientProfile and OutreachMission
        c_level_recipient = RecipientProfile(
            name="John Doe", title="CEO", company="TechCorp", industry="Technology",
            seniority="Executive", department="Executive", skills=["leadership"],
            recent_activity=[], metadata={}
        )
        
        c_level_mission = OutreachMission(
            objective="Strategic partnership", target_role="CEO",
            value_proposition="Strategic leadership", urgency="high",
            personalization_points=[], constraints=["formal"], metadata={}
        )
        
        c_level_context = archetype_planner.build_archetype_context(c_level_recipient, c_level_mission)
        
        reflexion_plan = planner.plan_reflexion_cycles(
            current_results=ResearchResult(
                query="test",
                results=[],
                confidence_scores=[],
                metadata={},
                timestamp="2023-01-01"
            ),  # Mock for testing
            archetype_context=c_level_context,
            iteration=1
        )
        
        assert reflexion_plan.reflexion_passes == 3  # C_LEVEL
        assert reflexion_plan.reasoning_intensity == "extreme"
        assert len(reflexion_plan.critique_questions) > 0
        assert len(reflexion_plan.refinement_strategies) > 0
        
        # Test RECRUITER gets minimum reflexion passes using RecipientProfile and OutreachMission
        recruiter_recipient = RecipientProfile(
            name="Recruiter", title="Technical Recruiter", company="TestCorp", industry="Technology",
            seniority="Mid-level", department="HR", skills=["recruiting"],
            recent_activity=[], metadata={}
        )
        
        recruiter_mission = OutreachMission(
            objective="Hiring", target_role="Technical Recruiter",
            value_proposition="Candidate placement", urgency="medium",
            personalization_points=[], constraints=["basic"], metadata={}
        )
        
        recruiter_context = archetype_planner.build_archetype_context(recruiter_recipient, recruiter_mission)
        
        reflexion_plan = planner.plan_reflexion_cycles(
            current_results=ResearchResult(
                query="test",
                results=[],
                confidence_scores=[],
                metadata={},
                timestamp="2023-01-01"
            ),  # Mock for testing
            archetype_context=recruiter_context,
            iteration=1
        )
        
        assert reflexion_plan.reflexion_passes == 0  # RECRUITER
        assert reflexion_plan.reasoning_intensity == "low"
