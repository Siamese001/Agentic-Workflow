"""
Comprehensive Test Suite for LIC v11.7
Tests all 5 new implementations from QA review
"""

import pytest
import asyncio
from LIC_AGENTIC_v11_7 import *


# ============================================================================
# TEST v11.7 NEW FEATURE: S5_Implement_SelfConsistency (FEATURE 2.3)
# ============================================================================

class TestSelfConsistencySynthesizer:
    """Test N-candidate synthesis for C_LEVEL archetype"""
    
    @pytest.mark.asyncio
    async def test_c_level_uses_synthesis(self):
        """C_LEVEL archetype triggers N-candidate synthesis"""
        synthesizer = SelfConsistencySynthesizer()
        
        scaffold = MessageScaffold(
            route=Route.INMAIL,
            archetype=Archetype.C_LEVEL,
            sections={},
            constraints={}
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[],
            recipient_insights=[],
            company_context=["TestCorp"],
            sender_context=[]
        )
        
        profile = ProfileAnalysis(
            archetype=Archetype.C_LEVEL,
            confidence=0.95,
            reasoning="Test",
            needs_manual_override=False,
            critique_history=[]
        )
        
        result = await synthesizer.synthesize_c_level_message(
            scaffold, context, profile, 0.7
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "strategic" in result.lower() or "vision" in result.lower()
    
    @pytest.mark.asyncio
    async def test_non_c_level_raises_error(self):
        """Non-C_LEVEL archetype raises ValueError"""
        synthesizer = SelfConsistencySynthesizer()
        
        scaffold = MessageScaffold(
            route=Route.INMAIL,
            archetype=Archetype.RECRUITER,
            sections={},
            constraints={}
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        profile = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            confidence=0.90,
            reasoning="Test",
            needs_manual_override=False,
            critique_history=[]
        )
        
        with pytest.raises(ValueError, match="Self-consistency synthesis only for C_LEVEL"):
            await synthesizer.synthesize_c_level_message(scaffold, context, profile, 0.7)
    
    @pytest.mark.asyncio
    async def test_synthesis_generates_n_candidates(self):
        """Synthesizer generates N=3 candidates and synthesizes"""
        synthesizer = SelfConsistencySynthesizer()
        assert synthesizer.n_candidates == 3


# ============================================================================
# TEST v11.7 NEW FEATURE: S6_ValidateMetricContext (GAP 1.4 / LIC-QA-043)
# ============================================================================

class TestMetricContextValidation:
    """Test metric validation requires keyword context from RAG"""
    
    def test_metric_without_rag_context_fails(self):
        """Metric without supporting RAG keywords fails validation"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="We achieved 40% growth in revenue last quarter.",
            word_count=8,
            char_count=50,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[
                RAGResult(
                    source="test",
                    source_type="GENERIC",
                    text="Company information",
                    extracted_keywords=["company", "information"],  # No "growth" or "revenue"
                    source_weight=1.0,
                    age_days=10,
                    recipient_specific=False
                )
            ],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have metric context failure
        metric_failures = [r for r in results if r.rule_id == "LIC-QA-043"]
        assert len(metric_failures) > 0
        assert "40%" in metric_failures[0].message
    
    def test_metric_with_rag_context_passes(self):
        """Metric with supporting RAG keywords passes validation"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="We achieved 40% growth in revenue last quarter.",
            word_count=8,
            char_count=50,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[
                RAGResult(
                    source="test",
                    source_type="COMPANY_BLOG",
                    text="Company showed significant growth in revenue",
                    extracted_keywords=["growth", "revenue", "significant"],  # Matches context!
                    source_weight=1.5,
                    age_days=10,
                    recipient_specific=False
                )
            ],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT have metric context failure
        metric_failures = [r for r in results if r.rule_id == "LIC-QA-043"]
        assert len(metric_failures) == 0
    
    def test_multiple_metrics_all_validated(self):
        """All metrics in message are validated for RAG context"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="We achieved 40% growth and 3x market expansion with 5 million users.",
            word_count=12,
            char_count=75,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[
                RAGResult(
                    source="test",
                    source_type="COMPANY_BLOG",
                    text="Company information",
                    extracted_keywords=["growth"],  # Only 1/3 metrics supported
                    source_weight=1.0,
                    age_days=10,
                    recipient_specific=False
                )
            ],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have failures for unsupported metrics
        metric_failures = [r for r in results if r.rule_id == "LIC-QA-043"]
        assert len(metric_failures) >= 2  # 3x and 5 million lack support


# ============================================================================
# TEST v11.7 NEW FEATURE: S6_ValidateSenderClaims (GAP 1.8 / LIC-QA-105)
# ============================================================================

class TestSenderClaimsValidation:
    """Test sender claims validation against team whitelist"""
    
    def test_team_claim_without_whitelist_fails(self):
        """'My team' claim without sender whitelist fails critically"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="My team built a revolutionary AI platform that increased efficiency.",
            word_count=10,
            char_count=70,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},  # No sender_teams whitelist
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have critical sender claims failure
        claims_failures = [r for r in results if r.rule_id == "LIC-QA-105"]
        assert len(claims_failures) == 1
        assert claims_failures[0].severity == ValidationSeverity.CRITICAL
        assert "team claims" in claims_failures[0].message.lower()
    
    def test_team_claim_with_whitelist_passes(self):
        """'My team' claim with sender whitelist passes"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="My team built a revolutionary AI platform.",
            word_count=7,
            char_count=45,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"sender_teams": ["AI Platform Team", "ML Research"]},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT have sender claims failure
        claims_failures = [r for r in results if r.rule_id == "LIC-QA-105"]
        assert len(claims_failures) == 0
    
    def test_no_team_claim_passes(self):
        """Message without team claims passes regardless of whitelist"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I have experience in AI and ML development.",
            word_count=8,
            char_count=45,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT have sender claims failure
        claims_failures = [r for r in results if r.rule_id == "LIC-QA-105"]
        assert len(claims_failures) == 0
    
    def test_various_team_keywords_detected(self):
        """Various team claim keywords trigger validation"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        test_phrases = [
            "our team developed",
            "we built this system",
            "our work on ML",
            "my team created"
        ]
        
        for phrase in test_phrases:
            message = GeneratedMessage(
                content=f"I wanted to share that {phrase} amazing results.",
                word_count=10,
                char_count=50,
                route=Route.INMAIL,
                archetype=Archetype.EXECUTIVE,
                generation_temperature=0.7,
                generation_attempts=1,
                locked_sections=[],
                checksum="test123"
            )
            
            context = ResearchContext(
                mission_context={},
                rag_results=[],
                recipient_insights=[],
                company_context=[],
                sender_context=[]
            )
            
            results = validator.validate_message(message, context)
            claims_failures = [r for r in results if r.rule_id == "LIC-QA-105"]
            assert len(claims_failures) > 0, f"Failed to detect team claim: {phrase}"


# ============================================================================
# TEST v11.7 NEW FEATURE: S6_ValidateJobTitlePlacement (GAP 1.6 / LIC-QA-075)
# ============================================================================

class TestJobTitlePlacement:
    """Test job title must appear in first 50 words for INMAIL"""
    
    def test_job_title_in_first_50_words_passes(self):
        """Job title in first 50 words passes"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I am writing about the Senior AI Engineer position at your company.",
            word_count=12,
            char_count=70,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"job_title": "Senior AI Engineer"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT have job title placement failure
        title_failures = [r for r in results if r.rule_id == "LIC-QA-075"]
        assert len(title_failures) == 0
    
    def test_job_title_after_50_words_fails(self):
        """Job title after first 50 words fails"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        # 60-word message with job title at end
        long_intro = " ".join(["word"] * 55)
        message = GeneratedMessage(
            content=f"{long_intro} I am interested in the Senior AI Engineer role.",
            word_count=65,
            char_count=300,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"job_title": "Senior AI Engineer"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have job title placement failure
        title_failures = [r for r in results if r.rule_id == "LIC-QA-075"]
        assert len(title_failures) == 1
        assert title_failures[0].severity == ValidationSeverity.HIGH
    
    def test_job_title_validation_only_for_inmail(self):
        """Job title placement only validated for INMAIL route"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        # CONNECTION_REQ without job title in first 50 - should pass
        long_message = " ".join(["word"] * 55) + " Senior AI Engineer"
        
        message = GeneratedMessage(
            content=long_message,
            word_count=56,
            char_count=250,
            route=Route.CONNECTION_REQ,  # Not INMAIL
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"job_title": "Senior AI Engineer"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT validate job title for non-INMAIL
        title_failures = [r for r in results if r.rule_id == "LIC-QA-075"]
        assert len(title_failures) == 0


# ============================================================================
# TEST v11.7 NEW FEATURE: S6_ValidateCompanySpelling (GAP 1.7 / LIC-QA-049)
# ============================================================================

class TestCompanySpelling:
    """Test company name spelling validation with fuzzy matching"""
    
    def test_exact_company_name_passes(self):
        """Exact company name match passes"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I am interested in opportunities at TechCorp.",
            word_count=7,
            char_count=50,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"company": "TechCorp"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should NOT have company spelling failure
        company_failures = [r for r in results if r.rule_id == "LIC-QA-049"]
        assert len(company_failures) == 0
    
    def test_misspelled_company_fails(self):
        """Misspelled company name fails validation"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I am interested in opportunities at TechKorp.",  # Wrong spelling
            word_count=7,
            char_count=50,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"company": "TechCorp"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have company spelling failure
        company_failures = [r for r in results if r.rule_id == "LIC-QA-049"]
        assert len(company_failures) == 1
        assert company_failures[0].severity == ValidationSeverity.HIGH
    
    def test_fuzzy_match_within_2_chars_passes(self):
        """Fuzzy match within 2 char Levenshtein distance passes"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        # Test helper method
        assert validator._levenshtein_distance("TechCorp", "TechCorp") == 0
        assert validator._levenshtein_distance("TechCorp", "TechCorps") == 1
        assert validator._levenshtein_distance("TechCorp", "TechCrp") == 1
    
    def test_missing_company_name_fails(self):
        """Message without company name fails"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I am interested in opportunities at your organization.",
            word_count=8,
            char_count=55,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={"company": "TechCorp"},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        
        # Should have company spelling failure
        company_failures = [r for r in results if r.rule_id == "LIC-QA-049"]
        assert len(company_failures) == 1


# ============================================================================
# REGRESSION TESTS: Ensure v11.6.1 features still work
# ============================================================================

class TestRegressionV11_6_1:
    """Ensure all v11.6.1 tests still pass"""
    
    def test_archetype_enum_has_4_values(self):
        """4-archetype standard maintained"""
        assert len(Archetype) == 4
        assert Archetype.C_LEVEL in Archetype
        assert Archetype.EXECUTIVE in Archetype
        assert Archetype.SENIOR_TA in Archetype
        assert Archetype.RECRUITER in Archetype
    
    def test_hardened_routing_5_nodes(self):
        """5-node routing tree functional"""
        circuit_breaker = CircuitBreaker()
        router = RoutingAgent(circuit_breaker)
        
        # Node 1: Override
        mission = OutreachMission(
            mission_id="test",
            recipient_name="Test",
            recipient_profile={},
            sender_profile={},
            job_description={},
            connection_status="not_connected",
            prior_message_count=0,
            route_override=Route.FOLLOW_UP
        )
        route, _ = router.determine_route(mission, ProfileAnalysis(Archetype.EXECUTIVE, 0.9, "", False, []))
        assert route == Route.FOLLOW_UP
    
    def test_placeholder_detection_still_works(self):
        """Critical placeholder validation functional"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="Hi [NAME], this is a test.",
            word_count=6,
            char_count=27,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.7,
            generation_attempts=1,
            locked_sections=[],
            checksum="test123"
        )
        
        context = ResearchContext(
            mission_context={},
            rag_results=[],
            recipient_insights=[],
            company_context=[],
            sender_context=[]
        )
        
        results = validator.validate_message(message, context)
        placeholder_failures = [r for r in results if r.rule_id == "LIC-QA-067"]
        assert len(placeholder_failures) > 0


# ============================================================================
# E2E INTEGRATION TEST
# ============================================================================

class TestE2EWorkflow:
    """End-to-end workflow test with v11.7 features"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_c_level_with_all_validations(self):
        """Full workflow for C_LEVEL with all v11.7 validations"""
        orchestrator = WorkflowOrchestrator()
        
        mission = OutreachMission(
            mission_id="e2e_test",
            recipient_name="Jane Smith",
            recipient_profile={"title": "Chief Technology Officer"},
            sender_profile={},
            job_description={"title": "Senior AI Engineer", "company": "TechCorp"},
            connection_status="not_connected",
            prior_message_count=0,
            route_override=None
        )
        
        # Should complete without errors
        result = await orchestrator.execute_workflow(mission)
        
        assert result["status"] == "COMPLETED"
        assert "message" in result
        assert "qa_report" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
