"""
Test Suite for LIC v11.5 - Archetype-Specific Configurations
============================================================

Tests all four priorities implemented from v10.22:
1. Archetype-Specific Reasoning Parameters
2. Global Constraints SSOT (ConfigRegistry)
3. Archetype-Specific Word Count Targets
4. Archetype-Specific Tone Mappings

Plus backward compatibility with v11.4 functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from LIC_AGENTIC_v11_5 import (
    ConfigRegistry,
    ARCHETYPE_REASONING_PARAMS,
    Route,
    Archetype,
    OutreachMission,
    ProfileAnalysis,
    ResearchContext,
    MessageScaffold,
    ImmutableStagingBuffer,
    ValidationResult,
    ValidationSeverity,
    ConstraintFailureType,
    ConstraintFailureClassifier,
    SimilarityCrossValidator,
    EventBus,
    EventType,
    ProfileAnalysisAgent,
    ResearchOrchestrator,
    RoutingAgent,
    ScaffoldAgent,
    ValidationAgent
)


# ============================================================================
# PRIORITY 2 TESTS: ConfigRegistry SSOT
# ============================================================================

class TestConfigRegistrySSO:
    """Test suite for ConfigRegistry SSOT functionality"""
    
    def test_get_target_word_count_c_level_inmail(self):
        """C_LEVEL INMAIL should return 240 words"""
        word_count = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.C_LEVEL)
        assert word_count == 240, f"Expected 240, got {word_count}"
    
    def test_get_target_word_count_c_level_followup(self):
        """C_LEVEL FOLLOW_UP should return 160 words"""
        word_count = ConfigRegistry.get_target_word_count(Route.FOLLOW_UP, Archetype.C_LEVEL)
        assert word_count == 160, f"Expected 160, got {word_count}"
    
    def test_get_target_word_count_executive_inmail(self):
        """EXECUTIVE INMAIL should return 225 words"""
        word_count = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.EXECUTIVE)
        assert word_count == 225, f"Expected 225, got {word_count}"
    
    def test_get_target_word_count_recruiter_inmail(self):
        """RECRUITER INMAIL should return 200 words"""
        word_count = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.RECRUITER)
        assert word_count == 200, f"Expected 200, got {word_count}"
    
    def test_get_target_word_count_variance(self):
        """Word count targets should show 40-word variance across archetypes"""
        c_level = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.C_LEVEL)
        recruiter = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.RECRUITER)
        
        variance = c_level - recruiter
        assert variance == 40, f"Expected 40-word variance, got {variance}"
    
    def test_get_rag_parameter_c_level_total_calls(self):
        """C_LEVEL should have 24 total RAG calls"""
        total_calls = ConfigRegistry.get_rag_parameter(Archetype.C_LEVEL, "total_calls")
        assert total_calls == 24, f"Expected 24, got {total_calls}"
    
    def test_get_rag_parameter_recruiter_total_calls(self):
        """RECRUITER should have 8 total RAG calls"""
        total_calls = ConfigRegistry.get_rag_parameter(Archetype.RECRUITER, "total_calls")
        assert total_calls == 8, f"Expected 8, got {total_calls}"
    
    def test_get_rag_parameter_variance(self):
        """RAG calls should have 3x variance between C_LEVEL and RECRUITER"""
        c_level_calls = ConfigRegistry.get_rag_parameter(Archetype.C_LEVEL, "total_calls")
        recruiter_calls = ConfigRegistry.get_rag_parameter(Archetype.RECRUITER, "total_calls")
        
        ratio = c_level_calls / recruiter_calls
        assert ratio == 3.0, f"Expected 3x ratio, got {ratio}"
    
    def test_get_tone_mapping_c_level_formality(self):
        """C_LEVEL should have 'very high' formality"""
        formality = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "formality")
        assert formality == "very high", f"Expected 'very high', got '{formality}'"
    
    def test_get_tone_mapping_recruiter_formality(self):
        """RECRUITER should have 'low-medium' formality"""
        formality = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "formality")
        assert formality == "low-medium", f"Expected 'low-medium', got '{formality}'"
    
    def test_get_tone_mapping_verb_preferences(self):
        """Different archetypes should have different verb preferences"""
        c_level_verbs = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "verb_preference")
        recruiter_verbs = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "verb_preference")
        
        assert "discuss" in c_level_verbs, "C_LEVEL should prefer 'discuss'"
        assert "chat" in recruiter_verbs, "RECRUITER should prefer 'chat'"
        assert "chat" not in c_level_verbs, "C_LEVEL should NOT prefer 'chat'"
    
    def test_get_route_constraint_char_limit(self):
        """Route constraints should return correct char limits"""
        inmail_limit = ConfigRegistry.get_route_constraint(Route.INMAIL, "char_limit")
        connection_limit = ConfigRegistry.get_route_constraint(Route.CONNECTION_REQ, "char_limit")
        
        assert inmail_limit == 1900, f"INMAIL limit should be 1900, got {inmail_limit}"
        assert connection_limit == 300, f"CONNECTION_REQ limit should be 300, got {connection_limit}"


# ============================================================================
# PRIORITY 1 TESTS: Archetype-Specific Reasoning Parameters
# ============================================================================

class TestArchetypeReasoningParameters:
    """Test suite for archetype-specific reasoning configurations"""
    
    def test_c_level_temperature(self):
        """C_LEVEL should have temp=0.45 for precision"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        assert params["temp"] == 0.45, f"Expected 0.45, got {params['temp']}"
    
    def test_recruiter_temperature(self):
        """RECRUITER should have temp=0.65 for warmth"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        assert params["temp"] == 0.65, f"Expected 0.65, got {params['temp']}"
    
    def test_c_level_self_consistency(self):
        """C_LEVEL should have 12 self-consistency runs"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        assert params["self_consistency"] == 12, f"Expected 12, got {params['self_consistency']}"
    
    def test_recruiter_self_consistency(self):
        """RECRUITER should have 3 self-consistency runs"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        assert params["self_consistency"] == 3, f"Expected 3, got {params['self_consistency']}"
    
    def test_c_level_tot_enabled(self):
        """C_LEVEL should have Tree-of-Thought enabled with 16 branches"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        assert params["hybrid_cot_tot"] is True, "C_LEVEL should enable ToT"
        assert params["tot_branches"] == 16, f"Expected 16 branches, got {params['tot_branches']}"
    
    def test_recruiter_tot_disabled(self):
        """RECRUITER should have Tree-of-Thought disabled"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        assert params["hybrid_cot_tot"] is False, "RECRUITER should disable ToT"
        assert params["tot_branches"] is None, "RECRUITER ToT branches should be None"
    
    def test_c_level_reflexion_enabled(self):
        """C_LEVEL should have reflexion enabled"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        assert params["reflexion"] is True, "C_LEVEL should enable reflexion"
    
    def test_recruiter_reflexion_disabled(self):
        """RECRUITER should have reflexion disabled"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        assert params["reflexion"] is False, "RECRUITER should disable reflexion"
    
    def test_c_level_max_hops(self):
        """C_LEVEL should have max_hops=6"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        assert params["max_hops"] == 6, f"Expected 6, got {params['max_hops']}"
    
    def test_recruiter_max_hops(self):
        """RECRUITER should have max_hops=2"""
        params = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        assert params["max_hops"] == 2, f"Expected 2, got {params['max_hops']}"
    
    def test_compute_investment_variance(self):
        """Verify 3x compute variance between C_LEVEL and RECRUITER"""
        c_level = ARCHETYPE_REASONING_PARAMS[Archetype.C_LEVEL]
        recruiter = ARCHETYPE_REASONING_PARAMS[Archetype.RECRUITER]
        
        # RAG calls: 24 vs 8 = 3x
        assert c_level["rag_total_calls"] / recruiter["rag_total_calls"] == 3.0
        
        # Self-consistency: 12 vs 3 = 4x
        assert c_level["self_consistency"] / recruiter["self_consistency"] == 4.0
        
        # Max hops: 6 vs 2 = 3x
        assert c_level["max_hops"] / recruiter["max_hops"] == 3.0


# ============================================================================
# PRIORITY 3 TESTS: Archetype-Specific Word Count Targets
# ============================================================================

class TestArchetypeWordCountTargets:
    """Test suite for archetype-specific word count targeting"""
    
    def test_word_count_ordering_inmail(self):
        """INMAIL word counts should be ordered: C_LEVEL > EXECUTIVE > HIRING_MANAGER > RECRUITER"""
        c_level = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.C_LEVEL)
        executive = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.EXECUTIVE)
        hiring_mgr = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.HIRING_MANAGER)
        recruiter = ConfigRegistry.get_target_word_count(Route.INMAIL, Archetype.RECRUITER)
        
        assert c_level > executive > hiring_mgr > recruiter, \
            f"Word counts not properly ordered: C={c_level}, E={executive}, H={hiring_mgr}, R={recruiter}"
    
    def test_word_count_ordering_followup(self):
        """FOLLOW_UP word counts should follow same ordering"""
        c_level = ConfigRegistry.get_target_word_count(Route.FOLLOW_UP, Archetype.C_LEVEL)
        executive = ConfigRegistry.get_target_word_count(Route.FOLLOW_UP, Archetype.EXECUTIVE)
        hiring_mgr = ConfigRegistry.get_target_word_count(Route.FOLLOW_UP, Archetype.HIRING_MANAGER)
        recruiter = ConfigRegistry.get_target_word_count(Route.FOLLOW_UP, Archetype.RECRUITER)
        
        assert c_level > executive > hiring_mgr > recruiter, \
            f"Word counts not properly ordered: C={c_level}, E={executive}, H={hiring_mgr}, R={recruiter}"
    
    def test_connection_req_no_word_count(self):
        """CONNECTION_REQ should use base constraint (no archetype override)"""
        c_level = ConfigRegistry.get_target_word_count(Route.CONNECTION_REQ, Archetype.C_LEVEL)
        recruiter = ConfigRegistry.get_target_word_count(Route.CONNECTION_REQ, Archetype.RECRUITER)
        
        # Should fall back to base constraint midpoint
        assert c_level == recruiter, "CONNECTION_REQ should not vary by archetype"


# ============================================================================
# PRIORITY 4 TESTS: Archetype-Specific Tone Mappings
# ============================================================================

class TestArchetypeToneMappings:
    """Test suite for archetype-specific tone configurations"""
    
    def test_message_tone_differentiation(self):
        """Different archetypes should have distinct message tones"""
        c_level_tone = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "message_tone")
        recruiter_tone = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "message_tone")
        
        assert "strategic" in c_level_tone, "C_LEVEL should be 'strategic'"
        assert "warm" in recruiter_tone, "RECRUITER should be 'warm'"
        assert c_level_tone != recruiter_tone, "Tones should differ"
    
    def test_jargon_level_differentiation(self):
        """Jargon levels should vary by archetype"""
        c_level_jargon = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "jargon_level")
        recruiter_jargon = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "jargon_level")
        
        assert c_level_jargon == "strategic", "C_LEVEL should use 'strategic' jargon"
        assert recruiter_jargon == "layman_with_metrics", "RECRUITER should use 'layman_with_metrics'"
    
    def test_language_adaptation_strategies(self):
        """Language adaptation should differ by archetype"""
        c_level_adapt = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "language_adaptation")
        executive_adapt = ConfigRegistry.get_tone_mapping(Archetype.EXECUTIVE, "language_adaptation")
        recruiter_adapt = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "language_adaptation")
        
        assert c_level_adapt == "ANALYST_LEVEL_PITCH"
        assert executive_adapt == "OPERATIONAL_PITCH"
        assert recruiter_adapt == "SKILL_TO_ROLE_MAPPING"
    
    def test_cta_tone_variance(self):
        """CTA tones should vary appropriately"""
        c_level_cta = ConfigRegistry.get_tone_mapping(Archetype.C_LEVEL, "cta_tone")
        executive_cta = ConfigRegistry.get_tone_mapping(Archetype.EXECUTIVE, "cta_tone")
        recruiter_cta = ConfigRegistry.get_tone_mapping(Archetype.RECRUITER, "cta_tone")
        
        assert "formal" in c_level_cta, "C_LEVEL CTA should be formal"
        assert "collaborative" in executive_cta, "EXECUTIVE CTA should be collaborative"
        assert "professional_neutral" in recruiter_cta, "RECRUITER CTA should be professional_neutral"


# ============================================================================
# BACKWARD COMPATIBILITY TESTS (v11.4 Functionality)
# ============================================================================

class TestBackwardCompatibility:
    """Ensure v11.4 functionality still works correctly"""
    
    def test_immutable_staging_buffer_integrity(self):
        """Ground truth validation should still work"""
        buffer = ImmutableStagingBuffer(
            mission_id="test-123",
            content={
                "subject": "Test Subject",
                "body": "This is a test body with multiple words.",
                "cta": "Please respond."
            },
            ground_truth_metrics={},  # Will be recalculated
            checksum=""  # Will be recalculated
        )
        
        assert buffer.verify_integrity(), "Buffer integrity check should pass"
        assert buffer.ground_truth_metrics["total_word_count"] == 12  # "Test Subject" (2) + body (8) + "Please respond." (2)
        assert buffer.ground_truth_metrics["body_word_count"] == 8
    
    def test_constraint_failure_classifier(self):
        """Failure classification should still work"""
        validation_results = [
            ValidationResult(
                passed=False,
                severity=ValidationSeverity.ERROR,
                rule_id="WORD_COUNT_001",
                message="Word count too low",
                section="body"
            )
        ]
        
        failure_type, strategy = ConstraintFailureClassifier.classify_failure(
            validation_results, "body"
        )
        
        assert failure_type == ConstraintFailureType.MECHANICAL
        assert "temp_adjustment" in strategy
    
    def test_similarity_cross_validator(self):
        """Similarity checking should still work"""
        validator = SimilarityCrossValidator()
        
        buffer1 = ImmutableStagingBuffer(
            mission_id="test-1",
            content={"body": "This is the first unique message"},
            ground_truth_metrics={},
            checksum=""
        )
        
        buffer2 = ImmutableStagingBuffer(
            mission_id="test-2",
            content={"body": "This is a completely different message with other words"},
            ground_truth_metrics={},
            checksum=""
        )
        
        report = validator.check_contamination(buffer2, [buffer1])
        
        assert "contaminated" in report
        assert "max_similarity" in report
        assert report["max_similarity"] < 0.95  # Should not be exact duplicate


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for complete workflow"""
    
    async def test_profile_analysis_archetype_detection(self):
        """Profile analysis should correctly detect archetypes"""
        event_bus = EventBus()
        agent = ProfileAnalysisAgent(event_bus)
        
        # Test C_LEVEL detection
        mission = OutreachMission(
            mission_id="test-1",
            sender_profile={"name": "Test Sender"},
            recipient_profile={"name": "John Doe", "title": "CEO"},
            job_description={"title": "Test Job", "company": "Test Co"}
        )
        
        analysis = await agent.analyze_profile(mission)
        assert analysis.archetype == Archetype.C_LEVEL
    
    async def test_research_orchestrator_uses_archetype_params(self):
        """Research should use archetype-specific RAG budgets"""
        event_bus = EventBus()
        orchestrator = ResearchOrchestrator(event_bus)
        
        mission = OutreachMission(
            mission_id="test-2",
            sender_profile={"name": "Test Sender"},
            recipient_profile={"name": "Jane Smith", "title": "Recruiter"},
            job_description={"title": "Test Job", "company": "Test Co"}
        )
        
        profile_analysis = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            seniority_level="MANAGER",
            primary_domain="RECRUITING",
            reasoning="Test",
            confidence_score=0.9
        )
        
        # This should use RECRUITER params (8 calls, 2 hops max)
        context = await orchestrator.conduct_research(mission, profile_analysis)
        
        # In demo mode, uses fewer calls, but should respect max
        assert context.research_hops <= 2, "RECRUITER should have max 2 hops"
    
    async def test_routing_decision_tree_v11_4(self):
        """Routing should follow v11.4 decision tree"""
        event_bus = EventBus()
        agent = RoutingAgent(event_bus)
        
        # Test: not_connected + C_LEVEL → INMAIL
        mission1 = OutreachMission(
            mission_id="test-3",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "CEO", "title": "Chief Executive"},
            job_description={"title": "Job"},
            connection_status="not_connected",
            prior_message_count=0
        )
        
        analysis1 = ProfileAnalysis(
            archetype=Archetype.C_LEVEL,
            seniority_level="C_LEVEL",
            primary_domain="EXECUTIVE",
            reasoning="Test",
            confidence_score=0.95
        )
        
        route1 = await agent.determine_route(mission1, analysis1)
        assert route1 == Route.INMAIL, "not_connected + C_LEVEL should → INMAIL"
        
        # Test: RECRUITER → CONNECTION_REQ
        mission2 = OutreachMission(
            mission_id="test-4",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Recruiter", "title": "Senior Recruiter"},
            job_description={"title": "Job"},
            connection_status="not_connected",
            prior_message_count=0
        )
        
        analysis2 = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            seniority_level="MANAGER",
            primary_domain="RECRUITING",
            reasoning="Test",
            confidence_score=0.9
        )
        
        route2 = await agent.determine_route(mission2, analysis2)
        assert route2 == Route.CONNECTION_REQ, "RECRUITER should → CONNECTION_REQ"
    
    async def test_scaffold_uses_archetype_constraints(self):
        """Scaffold should apply archetype-specific word counts and tones"""
        event_bus = EventBus()
        agent = ScaffoldAgent(event_bus)
        
        mission = OutreachMission(
            mission_id="test-5",
            sender_profile={"name": "Test Sender", "title": "Engineer"},
            recipient_profile={"name": "Test Recipient", "title": "VP Engineering"},
            job_description={"title": "Senior Engineer", "company": "Tech Co"}
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.EXECUTIVE,
            seniority_level="VP_LEVEL",
            primary_domain="TECHNICAL",
            reasoning="Test",
            confidence_score=0.9
        )
        
        research_context = ResearchContext(
            mission_id="test-5",
            research_queries=["test"],
            findings={"test": "data"},
            sources_used=["source1"],
            total_rag_calls=5,
            research_hops=2
        )
        
        scaffold = await agent.create_scaffold(
            mission, analysis, research_context, Route.INMAIL
        )
        
        # EXECUTIVE + INMAIL should target 225 words
        assert scaffold.target_word_count == 225
        
        # Tone should be EXECUTIVE-specific
        assert scaffold.tone_guidance["message_tone"] == "direct, collaborative"
        assert scaffold.tone_guidance["formality"] == "high"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_missing_archetype_fallback(self):
        """ConfigRegistry should handle missing archetypes gracefully"""
        # This should not crash
        result = ConfigRegistry.get_rag_parameter(Archetype.PEER, "nonexistent_param")
        assert result == 0, "Missing parameter should return 0"
    
    def test_connection_req_uses_base_constraints(self):
        """CONNECTION_REQ should not vary word count by archetype"""
        # All archetypes should get same CONNECTION_REQ constraint
        routes_counts = [
            ConfigRegistry.get_target_word_count(Route.CONNECTION_REQ, arch)
            for arch in [Archetype.C_LEVEL, Archetype.EXECUTIVE, Archetype.RECRUITER]
        ]
        
        # All should be equal (falling back to base)
        assert len(set(routes_counts)) == 1, "CONNECTION_REQ should not vary by archetype"
    
    def test_all_archetypes_have_reasoning_params(self):
        """All archetypes should have complete reasoning configurations"""
        required_params = [
            "temp", "top_p", "rag_total_calls", "min_hops", "max_hops",
            "self_consistency", "hybrid_cot_tot", "reflexion"
        ]
        
        for archetype in [Archetype.C_LEVEL, Archetype.EXECUTIVE, 
                         Archetype.HIRING_MANAGER, Archetype.RECRUITER, Archetype.PEER]:
            params = ARCHETYPE_REASONING_PARAMS.get(archetype)
            assert params is not None, f"{archetype} missing reasoning params"
            
            for param in required_params:
                assert param in params, f"{archetype} missing parameter: {param}"


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
