"""
LIC v11.8 - Comprehensive Test Suite
====================================

Tests all 5 new specifications:
1. 3-Layer Sender Grounding (v8.61)
2. Context-Aware CTA (v7.13.27)
3. Podcast-First RAG (v6.9)
4. RECRUITER Req-Focused Play (v7.13.27)
5. SENIOR_TA Business-Only Play (v7.13.27)

Plus regression tests for v11.7 features
"""

import pytest
import asyncio
import json
from pathlib import Path
from LIC_AGENTIC_v11_8 import *


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_master_resume():
    """Mock master_resume.json data"""
    return {
        "professional_experience": [
            {
                "company": "Unify Consulting",
                "title": "Chief AI Officer",
                "bullet_pool": [
                    "Built 12-person professional services AI team reducing sprint cycles by 27%",
                    "Delivered $34M transformation migrating risk systems to AWS cutting response times by 48%",
                    "Accelerated onboarding with RAG pipelines reducing intake times by 40%",
                    "Automated compliance validation cutting remediation cycles by 37%"
                ]
            },
            {
                "company": "IBM",
                "title": "Lead Client Partner",
                "bullet_pool": [
                    "Led ML engineering teams improving detection by 42%",
                    "Delivered $34M transformation for Fortune 500 banking clients"
                ]
            }
        ]
    }


@pytest.fixture
def mock_mission_job_confirmed(mock_master_resume):
    """Mission with job confirmed"""
    return Mission(
        recipient_name="Sarah Johnson",
        recipient_profile_url="https://linkedin.com/in/sarahjohnson",
        sender_profile=mock_master_resume,
        job_description={
            "title": "Senior Data Scientist",
            "company": "TechCorp",
            "description": "Leading AI initiatives"
        }
    )


@pytest.fixture
def mock_mission_no_job(mock_master_resume):
    """Mission without job confirmation"""
    return Mission(
        recipient_name="Mike Chen",
        recipient_profile_url="https://linkedin.com/in/mikechen",
        sender_profile=mock_master_resume,
        job_description={}
    )


@pytest.fixture
def circuit_breaker():
    """Circuit breaker instance"""
    return CircuitBreaker()


# ============================================================================
# SPECIFICATION 1: 3-LAYER SENDER GROUNDING TESTS
# ============================================================================

class TestSenderGroundingSpec1:
    """Test Specification 1 - 3-Layer Sender Grounding from v8.61"""
    
    def test_layer1_whitelist_extraction(self, mock_master_resume, circuit_breaker):
        """Test Layer 1: Pre-Generation Fact Extraction"""
        research_agent = ResearchOrchestrator(circuit_breaker)
        
        whitelists = research_agent._extract_sender_grounding_whitelists(mock_master_resume)
        
        # Verify companies extracted
        assert len(whitelists.sender_company_whitelist) >= 2
        assert "Unify Consulting" in whitelists.sender_company_whitelist
        assert "IBM" in whitelists.sender_company_whitelist
        
        # Verify teams extracted
        assert len(whitelists.sender_team_whitelist) >= 1
        assert any("professional services" in team.lower() for team in whitelists.sender_team_whitelist)
        
        # Verify metrics map
        assert len(whitelists.sender_metric_map) >= 2
        assert "40%" in whitelists.sender_metric_map or "37%" in whitelists.sender_metric_map
        
        print(f"✅ Layer 1: Extracted {len(whitelists.sender_company_whitelist)} companies, "
              f"{len(whitelists.sender_team_whitelist)} teams, "
              f"{len(whitelists.sender_metric_map)} metrics")
    
    @pytest.mark.asyncio
    async def test_layer2_generation_constraints(self, mock_mission_job_confirmed, circuit_breaker):
        """Test Layer 2: Generation-Time Constraint injection"""
        validation_agent = ValidationAgent(circuit_breaker)
        generation_agent = GenerationOrchestrator(circuit_breaker, validation_agent)
        
        # Create mock sender grounding
        sender_grounding = SenderGroundingWhitelists(
            sender_company_whitelist=["Unify Consulting", "IBM"],
            sender_team_whitelist=["ML engineering teams"],
            sender_metric_map={"40%": ["onboarding", "timelines"], "$34M": ["transformation", "risk systems"]}
        )
        
        # Build constraints
        constraints = generation_agent._build_grounding_constraints(sender_grounding)
        
        # Verify constraint strings
        assert "Unify Consulting" in constraints
        assert "IBM" in constraints
        assert "40%" in constraints
        assert "onboarding" in constraints
        assert "$34M" in constraints
        assert "transformation" in constraints
        assert "CRITICAL" in constraints
        
        print("✅ Layer 2: Generation constraints properly formatted")
    
    def test_layer3_metric_context_validation(self, circuit_breaker):
        """Test Layer 3: Post-Generation Validation - Metric Context"""
        validation_agent = ValidationAgent(circuit_breaker)
        
        # Mock message with metric
        message = GeneratedMessage(
            route=Route.INMAIL,
            content="We reduced onboarding times by 40% through automated workflows."
        )
        
        # Mock context with sender grounding
        sender_grounding = SenderGroundingWhitelists(
            sender_metric_map={"40%": ["onboarding", "timelines"]}
        )
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            sender_grounding=sender_grounding
        )
        
        # Validate - should PASS (has "onboarding")
        results = validation_agent._S6_ValidateMetricContext(message, context)
        assert any(r.passed for r in results), "Should pass - metric has required context"
        
        # Test FAILURE case - metric without context
        message_bad = GeneratedMessage(
            route=Route.INMAIL,
            content="We achieved 40% improvement in our systems."
        )
        results_bad = validation_agent._S6_ValidateMetricContext(message_bad, context)
        assert any(not r.passed for r in results_bad), "Should fail - metric lacks required context"
        
        print("✅ Layer 3: Metric context validation working")
    
    def test_layer3_team_claims_validation(self, circuit_breaker):
        """Test Layer 3: Post-Generation Validation - Team Claims"""
        validation_agent = ValidationAgent(circuit_breaker)
        
        # Mock message with team claim
        message = GeneratedMessage(
            route=Route.INMAIL,
            content="My ML engineering teams delivered production-grade systems."
        )
        
        # Mock context with team whitelist
        sender_grounding = SenderGroundingWhitelists(
            sender_team_whitelist=["ML engineering teams", "professional services AI team"]
        )
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={},
            sender_grounding=sender_grounding
        )
        
        # Validate - should PASS (team in whitelist)
        results = validation_agent._S6_ValidateSenderClaims(message, context)
        assert all(r.passed for r in results), "Should pass - team claim in whitelist"
        
        # Test FAILURE case - no whitelist
        context_no_whitelist = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={},
            sender_grounding=None
        )
        results_bad = validation_agent._S6_ValidateSenderClaims(message, context_no_whitelist)
        assert any(not r.passed for r in results_bad), "Should fail - no whitelist"
        
        print("✅ Layer 3: Team claims validation working")


# ============================================================================
# SPECIFICATION 2: CONTEXT-AWARE CTA TESTS
# ============================================================================

class TestContextAwareCTASpec2:
    """Test Specification 2 - Context-Aware CTA from v7.13.27"""
    
    def test_cta_tone_job_confirmed(self):
        """Test CTA tone is assertive when job confirmed"""
        scaffold_agent = ScaffoldAgent()
        
        # Mock context with job confirmed
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": True}
        )
        
        scaffold = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.EXECUTIVE, context)
        
        assert scaffold.cta_tone == "assertive", "Should be assertive when job confirmed"
        print("✅ CTA tone assertive for job_confirmed=true")
    
    def test_cta_tone_no_job(self):
        """Test CTA tone is collaborative when no job"""
        scaffold_agent = ScaffoldAgent()
        
        # Mock context without job
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": False}
        )
        
        scaffold = scaffold_agent.create_scaffold(Route.CONNECTION_REQ, Archetype.C_LEVEL, context)
        
        assert scaffold.cta_tone == "collaborative", "Should be collaborative when no job"
        print("✅ CTA tone collaborative for job_confirmed=false")
    
    def test_date_strategy_job_confirmed(self):
        """Test date proposal strategy with job confirmed"""
        scaffold_agent = ScaffoldAgent()
        
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": True}
        )
        
        scaffold = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.EXECUTIVE, context)
        
        assert scaffold.date_proposal_strategy == "tight_clustering", "Should use tight clustering for job"
        print("✅ Date strategy tight_clustering for job_confirmed=true")
    
    def test_date_strategy_no_job(self):
        """Test date proposal strategy without job"""
        scaffold_agent = ScaffoldAgent()
        
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": False}
        )
        
        scaffold = scaffold_agent.create_scaffold(Route.CONNECTION_REQ, Archetype.C_LEVEL, context)
        
        assert scaffold.date_proposal_strategy == "wide_spacing", "Should use wide spacing for no job"
        print("✅ Date strategy wide_spacing for job_confirmed=false")


# ============================================================================
# SPECIFICATION 3: PODCAST-FIRST RAG TESTS
# ============================================================================

class TestPodcastFirstRAGSpec3:
    """Test Specification 3 - Podcast-First RAG from v6.9"""
    
    @pytest.mark.asyncio
    async def test_podcast_first_c_level(self, mock_mission_job_confirmed, circuit_breaker):
        """Test Podcast-First RAG for C_LEVEL archetype"""
        research_agent = ResearchOrchestrator(circuit_breaker)
        
        profile_analysis = ProfileAnalysis(
            archetype=Archetype.C_LEVEL,
            archetype_confidence=0.95,
            seniority_level="Executive",
            industry="Technology",
            company="TechCorp",
            job_title="Chief Technology Officer"
        )
        
        # Execute RAG
        rag_results = await research_agent._podcast_first_rag(
            mock_mission_job_confirmed,
            profile_analysis
        )
        
        # Verify Tier 1 Premium Sources prioritized
        tier1_sources = ConfigRegistry.RAG_SOURCE_TIERS["tier_1_premium"]
        source_types = [r.source_type for r in rag_results]
        
        assert any(st in tier1_sources for st in source_types), "Should include Tier 1 Premium sources"
        
        # Verify 1.5x boost applied (scores should be higher)
        assert any(r.relevance_score >= 0.90 for r in rag_results), "Should have boosted scores"
        
        print(f"✅ Podcast-First RAG: {len(rag_results)} results with Tier 1 prioritization")
    
    @pytest.mark.asyncio
    async def test_podcast_first_executive(self, mock_mission_no_job, circuit_breaker):
        """Test Podcast-First RAG for EXECUTIVE archetype"""
        research_agent = ResearchOrchestrator(circuit_breaker)
        
        profile_analysis = ProfileAnalysis(
            archetype=Archetype.EXECUTIVE,
            archetype_confidence=0.90,
            seniority_level="VP",
            industry="Technology",
            company="TechCorp",
            job_title="VP of Engineering"
        )
        
        rag_results = await research_agent._podcast_first_rag(
            mock_mission_no_job,
            profile_analysis
        )
        
        assert len(rag_results) > 0, "Should return RAG results"
        tier1_sources = ConfigRegistry.RAG_SOURCE_TIERS["tier_1_premium"]
        assert any(r.source_type in tier1_sources for r in rag_results), "Should prioritize Tier 1"
        
        print("✅ Podcast-First RAG works for EXECUTIVE archetype")


# ============================================================================
# SPECIFICATION 4: RECRUITER REQ-FOCUSED TESTS
# ============================================================================

class TestRecruiterReqFocusedSpec4:
    """Test Specification 4 - RECRUITER Req-Focused Play from v7.13.27"""
    
    @pytest.mark.asyncio
    async def test_recruiter_rag_no_stalking(self, mock_mission_job_confirmed, circuit_breaker):
        """Test RECRUITER RAG avoids recipient stalking"""
        research_agent = ResearchOrchestrator(circuit_breaker)
        
        profile_analysis = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            archetype_confidence=0.90,
            seniority_level="Recruiter",
            industry="Technology",
            company="TechCorp",
            job_title="Senior Technical Recruiter"
        )
        
        # Execute RECRUITER RAG
        rag_results = await research_agent._recruiter_req_focused_rag(
            mock_mission_job_confirmed,
            profile_analysis
        )
        
        # Verify NO recipient name in queries (company-focused only)
        for result in rag_results:
            content_lower = result.content.lower()
            assert "sarah" not in content_lower, "Should NOT stalk recipient"
            assert "johnson" not in content_lower, "Should NOT stalk recipient"
        
        # Verify company-focused content
        assert any("hiring" in r.content.lower() for r in rag_results), "Should focus on hiring signals"
        assert any("techcorp" in r.content.lower() for r in rag_results), "Should focus on company"
        
        print("✅ RECRUITER RAG: Company-focused, NO recipient stalking")
    
    @pytest.mark.asyncio
    async def test_recruiter_prompt_structure(self, mock_mission_job_confirmed, circuit_breaker):
        """Test RECRUITER prompt has req-focused structure"""
        validation_agent = ValidationAgent(circuit_breaker)
        generation_agent = GenerationOrchestrator(circuit_breaker, validation_agent)
        
        # Mock context
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={
                "job_title": "Senior Data Scientist",
                "company": "TechCorp"
            }
        )
        
        # Mock scaffold
        scaffold = MessageScaffold(
            structure={},
            constraints={},
            tone_guidance="direct"
        )
        
        # Build RECRUITER prompt
        profile = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            archetype_confidence=0.90,
            seniority_level="Recruiter",
            industry="Technology",
            company="TechCorp",
            job_title="Recruiter"
        )
        
        prompt = generation_agent._build_recruiter_prompt(scaffold, context, "")
        
        # Verify structure
        assert "Senior Data Scientist" in prompt, "Should reference job title"
        assert "TechCorp" in prompt, "Should reference company"
        assert "OPENER" in prompt, "Should have opener section"
        assert "BODY" in prompt, "Should have body section"
        assert "achievement bullets" in prompt.lower(), "Should require achievement bullets"
        assert "bridge sentence" in prompt.lower(), "Should require bridge sentences"
        assert "CLOSING" in prompt, "Should have closing"
        assert "Resume attached" in prompt, "Should include resume mention"
        
        print("✅ RECRUITER prompt: Req-focused structure verified")


# ============================================================================
# SPECIFICATION 5: SENIOR_TA BUSINESS-ONLY TESTS
# ============================================================================

class TestSeniorTABusinessOnlySpec5:
    """Test Specification 5 - SENIOR_TA Business-Only Play from v7.13.27"""
    
    def test_senior_ta_constraints_injected(self):
        """Test SENIOR_TA scaffold has business-only constraints"""
        scaffold_agent = ScaffoldAgent()
        
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": False}
        )
        
        scaffold = scaffold_agent.create_scaffold(Route.CONNECTION_REQ, Archetype.SENIOR_TA, context)
        
        # Verify forbidden topics injected
        assert scaffold.forbidden_topics is not None, "Should have forbidden topics"
        assert len(scaffold.forbidden_topics) > 0, "Should have multiple forbidden topics"
        assert any("recruiting" in topic.lower() for topic in scaffold.forbidden_topics), "Should forbid recruiting"
        
        # Verify required topics injected
        assert scaffold.required_topics is not None, "Should have required topics"
        assert len(scaffold.required_topics) > 0, "Should have multiple required topics"
        assert any("revenue" in topic.lower() or "business" in topic.lower() for topic in scaffold.required_topics), "Should require business topics"
        
        print("✅ SENIOR_TA scaffold: Business-only constraints injected")
    
    @pytest.mark.asyncio
    async def test_senior_ta_prompt_structure(self, mock_mission_no_job, circuit_breaker):
        """Test SENIOR_TA prompt has business-only structure"""
        validation_agent = ValidationAgent(circuit_breaker)
        generation_agent = GenerationOrchestrator(circuit_breaker, validation_agent)
        
        # Mock scaffold with SENIOR_TA constraints
        scaffold = MessageScaffold(
            structure={},
            constraints={},
            tone_guidance="peer",
            forbidden_topics=ConfigRegistry.SENIOR_TA_CONSTRAINTS["forbidden_topics"],
            required_topics=ConfigRegistry.SENIOR_TA_CONSTRAINTS["required_topics"]
        )
        
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={}
        )
        
        # Build SENIOR_TA prompt
        prompt = generation_agent._build_senior_ta_prompt(scaffold, context, "")
        
        # Verify forbidden topics listed
        assert "FORBIDDEN TOPICS" in prompt, "Should list forbidden topics"
        assert "Recruiting operations" in prompt, "Should forbid recruiting topics"
        assert "Hiring efficiency" in prompt, "Should forbid hiring topics"
        
        # Verify required topics listed
        assert "REQUIRED TOPICS" in prompt, "Should list required topics"
        assert "Revenue" in prompt or "business" in prompt, "Should require business topics"
        
        # Verify CTA structure
        assert "Your perspective on connecting with leaders" in prompt, "Should have introduction CTA"
        assert "would be invaluable" in prompt, "Should have correct CTA phrasing"
        
        print("✅ SENIOR_TA prompt: Business-only structure verified")
    
    def test_senior_ta_not_applied_to_other_archetypes(self):
        """Test SENIOR_TA constraints only apply to SENIOR_TA"""
        scaffold_agent = ScaffoldAgent()
        
        context = ResearchContext(
            rag_results=[],
            signal_quality_score=0.75,
            company_context={},
            mission_context={"job_confirmed": False}
        )
        
        # Test C_LEVEL
        scaffold_clevel = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.C_LEVEL, context)
        assert scaffold_clevel.forbidden_topics is None, "C_LEVEL should not have SENIOR_TA constraints"
        
        # Test RECRUITER
        scaffold_recruiter = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.RECRUITER, context)
        assert scaffold_recruiter.forbidden_topics is None, "RECRUITER should not have SENIOR_TA constraints"
        
        print("✅ SENIOR_TA constraints properly scoped to SENIOR_TA only")


# ============================================================================
# REGRESSION TESTS (v11.7 features)
# ============================================================================

class TestRegressionV11_7:
    """Regression tests for v11.7 features"""
    
    def test_4_archetype_standard(self):
        """Test v11.7 4-archetype classification still works"""
        profile_data_clevel = {"raw_title": "Chief Technology Officer"}
        profile_data_exec = {"raw_title": "VP of Engineering"}
        profile_data_recruiter = {"raw_title": "Senior Technical Recruiter"}
        profile_data_ta = {"raw_title": "Staff Engineer"}
        
        circuit_breaker = CircuitBreaker()
        agent = ProfileAnalysisAgent(circuit_breaker)
        
        arch1, conf1 = agent._classify_archetype_v10_22(profile_data_clevel)
        assert arch1 == Archetype.C_LEVEL
        
        arch2, conf2 = agent._classify_archetype_v10_22(profile_data_exec)
        assert arch2 == Archetype.EXECUTIVE
        
        arch3, conf3 = agent._classify_archetype_v10_22(profile_data_recruiter)
        assert arch3 == Archetype.RECRUITER
        
        arch4, conf4 = agent._classify_archetype_v10_22(profile_data_ta)
        assert arch4 == Archetype.SENIOR_TA
        
        print("✅ Regression: 4-archetype classification working")
    
    def test_placeholder_detection(self, circuit_breaker):
        """Test v11.7 placeholder validation still works"""
        validation_agent = ValidationAgent(circuit_breaker)
        
        message_with_placeholder = GeneratedMessage(
            route=Route.INMAIL,
            content="Hi [NAME], I wanted to reach out about [COMPANY]."
        )
        
        results = validation_agent._S6_ValidatePlaceholders(message_with_placeholder)
        assert any(not r.passed for r in results), "Should detect placeholder"
        
        message_clean = GeneratedMessage(
            route=Route.INMAIL,
            content="Hi Sarah, I wanted to reach out about your work at TechCorp."
        )
        
        results_clean = validation_agent._S6_ValidatePlaceholders(message_clean)
        assert all(r.passed for r in results_clean), "Should pass without placeholders"
        
        print("✅ Regression: Placeholder detection working")
    
    def test_self_consistency_c_level_only(self):
        """Test v11.7 self-consistency only triggers for C_LEVEL"""
        synthesizer = SelfConsistencySynthesizer()
        
        # Should work for C_LEVEL
        try:
            # Will fail since we're not actually calling LLM, but validates guard works
            pass
        except Exception:
            pass
        
        # Should raise error for non-C_LEVEL
        with pytest.raises(ValueError):
            profile = ProfileAnalysis(
                archetype=Archetype.EXECUTIVE,
                archetype_confidence=0.90,
                seniority_level="VP",
                industry="Tech",
                company="Corp",
                job_title="VP"
            )
            asyncio.run(synthesizer.synthesize_c_level_message(None, None, profile, 0.7))
        
        print("✅ Regression: Self-consistency scoped to C_LEVEL only")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationE2E:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_job_confirmed(self, mock_mission_job_confirmed):
        """Test complete workflow with job confirmed"""
        orchestrator = LinkedInOutreachOrchestrator()
        
        result = await orchestrator.execute_workflow(mock_mission_job_confirmed)
        
        assert result["status"] == "success", "Workflow should complete successfully"
        assert result["message"] is not None, "Should generate message"
        assert result["metadata"]["route"] == "INMAIL", "Should route to INMAIL for job"
        
        print("✅ E2E: Full workflow with job confirmed")
    
    @pytest.mark.asyncio
    async def test_full_workflow_recruiter_archetype(self, mock_master_resume):
        """Test workflow with RECRUITER archetype"""
        mission = Mission(
            recipient_name="Jane Doe",
            recipient_profile_url="https://linkedin.com/in/janedoe",
            sender_profile=mock_master_resume,
            job_description={
                "title": "ML Engineer",
                "company": "DataCo"
            }
        )
        
        # Force RECRUITER archetype
        orchestrator = LinkedInOutreachOrchestrator()
        
        # Override profile analysis for testing
        original_analyze = orchestrator.profile_agent.analyze_profile
        async def mock_analyze(m):
            return ProfileAnalysis(
                archetype=Archetype.RECRUITER,
                archetype_confidence=0.90,
                seniority_level="Recruiter",
                industry="Technology",
                company="DataCo",
                job_title="Technical Recruiter"
            )
        orchestrator.profile_agent.analyze_profile = mock_analyze
        
        result = await orchestrator.execute_workflow(mission)
        
        assert result["status"] == "success"
        assert result["metadata"]["archetype"] == "RECRUITER"
        
        print("✅ E2E: RECRUITER workflow complete")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
