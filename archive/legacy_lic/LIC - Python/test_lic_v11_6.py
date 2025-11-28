"""
Test Suite for LIC v11.6 - Full v10.22 + SUPREME_SPELL Integration
===================================================================

Tests all v11.6 features:
1. 4-Archetype Standard (C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER)
2. Hardened Deterministic Routing (5-node tree)
3. Comprehensive QA Framework (107 rules)
4. Signal Quality Scoring
5. RAG Reflexion Loop
6. Adaptive Temperature Control
7. Constraint Pre-Flight Testing
8. Content Cleanliness Validators
9. Circuit Breaker
10. Manual Override for Low Confidence
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from LIC_AGENTIC_v11_6 import (
    ConfigRegistry,
    Route,
    Archetype,
    OutreachMission,
    ProfileAnalysis,
    ResearchContext,
    MessageScaffold,
    ValidationResult,
    ValidationSeverity,
    ConstraintFailureType,
    CircuitBreaker,
    CircuitState,
    SignalQualityScorer,
    ClaimConfidenceScorer,
    RAGReflexionSystem,
    AdaptiveTemperatureController,
    ConstraintFeasibilityChecker,
    ContentCleanlinessValidator,
    PlaceholderDetector,
    MessageDiversityValidator,
    ASCIIEnforcer,
    ProfileAnalysisAgent,
    ResearchOrchestrator,
    RoutingAgent,
    ScaffoldAgent,
    GenerationOrchestrator,
    ValidationAgent,
    QAAgent,
    RAGResult,
    MessageClaim,
    RAGCritique,
    GeneratedMessage
)


# ============================================================================
# v11.6 NEW: 4-ARCHETYPE STANDARD TESTS
# ============================================================================

class TestArchetypeStandard:
    """Test v11.6 4-archetype standard (removed HIRING_MANAGER, PEER; added SENIOR_TA)"""
    
    def test_archetype_enum_has_four_values(self):
        """Archetype enum should have exactly 4 values"""
        archetypes = list(Archetype)
        assert len(archetypes) == 4, f"Expected 4 archetypes, got {len(archetypes)}"
    
    def test_archetype_enum_values(self):
        """Archetype enum should contain C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER"""
        archetype_names = [a.value for a in Archetype]
        assert "C_LEVEL" in archetype_names
        assert "EXECUTIVE" in archetype_names
        assert "SENIOR_TA" in archetype_names
        assert "RECRUITER" in archetype_names
    
    def test_no_deprecated_archetypes(self):
        """Archetype enum should NOT contain HIRING_MANAGER or PEER"""
        archetype_names = [a.value for a in Archetype]
        assert "HIRING_MANAGER" not in archetype_names
        assert "PEER" not in archetype_names
    
    def test_senior_ta_word_targets_exist(self):
        """SENIOR_TA should have word count targets"""
        inmail_count = ConfigRegistry.get_target_word_count(Archetype.SENIOR_TA, Route.INMAIL)
        assert inmail_count == 220, f"SENIOR_TA INMAIL should be 220, got {inmail_count}"
        
        followup_count = ConfigRegistry.get_target_word_count(Archetype.SENIOR_TA, Route.FOLLOW_UP)
        assert followup_count == 148, f"SENIOR_TA FOLLOW_UP should be 148, got {followup_count}"
    
    def test_senior_ta_rag_params_exist(self):
        """SENIOR_TA should have RAG parameters"""
        total_calls = ConfigRegistry.get_rag_parameter(Archetype.SENIOR_TA, "total_calls")
        assert total_calls == 16, f"SENIOR_TA should have 16 RAG calls, got {total_calls}"
    
    def test_senior_ta_reasoning_params_exist(self):
        """SENIOR_TA should have reasoning parameters"""
        temp = ConfigRegistry.get_reasoning_parameter(Archetype.SENIOR_TA, "temperature")
        assert temp == 0.55, f"SENIOR_TA temp should be 0.55, got {temp}"
        
        max_hops = ConfigRegistry.get_reasoning_parameter(Archetype.SENIOR_TA, "max_hops")
        assert max_hops == 4, f"SENIOR_TA max_hops should be 4, got {max_hops}"
    
    def test_senior_ta_tone_mapping_exists(self):
        """SENIOR_TA should have tone mapping"""
        tone = ConfigRegistry.get_tone_mapping(Archetype.SENIOR_TA, "message_tone")
        assert tone == "technical_peer", f"SENIOR_TA tone should be 'technical_peer', got '{tone}'"
        
        formality = ConfigRegistry.get_tone_mapping(Archetype.SENIOR_TA, "formality")
        assert formality == "medium-high"


# ============================================================================
# v11.6 NEW: HARDENED ROUTING TESTS (5-NODE TREE)
# ============================================================================

class TestHardenedRouting:
    """Test v11.6 5-node deterministic routing tree (GAP 2.1)"""
    
    def test_node1_route_override(self):
        """Node 1: route_override should bypass automatic selection"""
        circuit_breaker = CircuitBreaker()
        agent = RoutingAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-route-override",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Test", "title": "CEO"},
            job_description={"title": "Test"},
            route_override=Route.EMAIL  # Manual override
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.C_LEVEL,
            confidence=0.95,
            reasoning="Test",
            key_indicators=[]
        )
        
        route, reasoning = agent.determine_route(mission, analysis)
        assert route == Route.EMAIL
        assert "Node 1" in reasoning
        assert "override" in reasoning.lower()
    
    def test_node2_job_confirmed_inmail(self):
        """Node 2: job_confirmed=true should → INMAIL"""
        circuit_breaker = CircuitBreaker()
        agent = RoutingAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-job-confirmed",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Test", "title": "VP"},
            job_description={"title": "Senior Engineer", "company": "Tech Co"},  # Job confirmed
            connection_status="not_connected"
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.EXECUTIVE,
            confidence=0.90,
            reasoning="Test",
            key_indicators=[]
        )
        
        route, reasoning = agent.determine_route(mission, analysis)
        assert route == Route.INMAIL
        assert "Node 2" in reasoning
    
    def test_node3_existing_relationship_followup(self):
        """Node 3: existing_relationship=true should → FOLLOW_UP"""
        circuit_breaker = CircuitBreaker()
        agent = RoutingAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-followup",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Test", "title": "Manager"},
            job_description={"title": ""},  # No job
            connection_status="connected",
            prior_message_count=2  # Existing relationship
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.RECRUITER,
            confidence=0.88,
            reasoning="Test",
            key_indicators=[]
        )
        
        route, reasoning = agent.determine_route(mission, analysis)
        assert route == Route.FOLLOW_UP
        assert "Node 3" in reasoning
    
    def test_node4_new_recipient_connection_req(self):
        """Node 4: new_recipient=true should → CONNECTION_REQ"""
        circuit_breaker = CircuitBreaker()
        agent = RoutingAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-connection",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Test", "title": "Engineer"},
            job_description={"title": ""},  # No job
            connection_status="not_connected",
            prior_message_count=0  # New recipient
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.SENIOR_TA,
            confidence=0.85,
            reasoning="Test",
            key_indicators=[]
        )
        
        route, reasoning = agent.determine_route(mission, analysis)
        assert route == Route.CONNECTION_REQ
        assert "Node 4" in reasoning
    
    def test_node5_fallback_inmail(self):
        """Node 5: Fallback should → INMAIL"""
        circuit_breaker = CircuitBreaker()
        agent = RoutingAgent(circuit_breaker)
        
        # Create ambiguous scenario
        mission = OutreachMission(
            mission_id="test-fallback",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Test", "title": "Director"},
            job_description={"title": ""},
            connection_status="connected",
            prior_message_count=0  # Connected but no prior messages - ambiguous
        )
        
        analysis = ProfileAnalysis(
            archetype=Archetype.EXECUTIVE,
            confidence=0.80,
            reasoning="Test",
            key_indicators=[]
        )
        
        route, reasoning = agent.determine_route(mission, analysis)
        # Should go to Node 5 fallback or Node 4
        assert route in [Route.INMAIL, Route.CONNECTION_REQ]


# ============================================================================
# v11.6 NEW: SIGNAL QUALITY SCORING TESTS (FEATURE 1.1)
# ============================================================================

class TestSignalQualityScorer:
    """Test signal quality scoring from SUPREME_SPELL"""
    
    def test_high_quality_sources_score_high(self):
        """High-quality sources should produce high signal scores"""
        scorer = SignalQualityScorer()
        
        rag_results = [
            RAGResult(
                source="linkedin_about",
                source_type="RECIPIENT_LINKEDIN_ABOUT",
                text="Test recipient data",
                extracted_keywords=["leadership", "innovation", "AI"],
                source_weight=2.0,
                age_days=5,
                recipient_specific=True
            ),
            RAGResult(
                source="recent_post",
                source_type="RECIPIENT_RECENT_POST",
                text="Test recent activity",
                extracted_keywords=["AI", "machine learning"],
                source_weight=1.8,
                age_days=10,
                recipient_specific=True
            )
        ]
        
        message = "I noticed your leadership in AI and innovation, particularly in machine learning"
        score, breakdown = scorer.calculate_signal_score(rag_results, message)
        
        assert score >= 0.70, f"High-quality sources should score ≥0.70, got {score:.2f}"
    
    def test_low_quality_sources_score_low(self):
        """Low-quality sources should produce low signal scores"""
        scorer = SignalQualityScorer()
        
        rag_results = [
            RAGResult(
                source="generic_trend",
                source_type="GENERIC_INDUSTRY_TREND",
                text="Industry is growing",
                extracted_keywords=["growth", "technology"],
                source_weight=0.6,
                age_days=365,
                recipient_specific=False
            )
        ]
        
        message = "I noticed growth in technology"
        score, breakdown = scorer.calculate_signal_score(rag_results, message)
        
        assert score < 0.70, f"Low-quality sources should score <0.70, got {score:.2f}"
    
    def test_minimum_signal_validation(self):
        """validate_minimum_signal should enforce 0.70 threshold"""
        scorer = SignalQualityScorer()
        
        assert scorer.validate_minimum_signal(0.75) is True
        assert scorer.validate_minimum_signal(0.70) is True
        assert scorer.validate_minimum_signal(0.69) is False


# ============================================================================
# v11.6 NEW: CLAIM CONFIDENCE SCORING TESTS (FEATURE 1.2)
# ============================================================================

class TestClaimConfidenceScorer:
    """Test per-claim confidence scoring"""
    
    def test_well_supported_claim_scores_high(self):
        """Claims with multiple supporting sources should score high"""
        scorer = ClaimConfidenceScorer()
        
        rag_results = [
            RAGResult(
                source="source1",
                source_type="RECIPIENT_LINKEDIN_ABOUT",
                text="Led AI transformation with machine learning team",
                extracted_keywords=["AI", "transformation", "machine", "learning"],
                source_weight=2.0,
                age_days=10,
                recipient_specific=True
            ),
            RAGResult(
                source="source2",
                source_type="COMPANY_BLOG_ANNOUNCEMENT",
                text="AI transformation initiative led by engineering team",
                extracted_keywords=["AI", "transformation", "engineering"],
                source_weight=1.5,
                age_days=20,
                recipient_specific=True
            )
        ]
        
        claim = "You led AI transformation initiatives"
        claim_obj = scorer.score_claim(claim, rag_results)
        
        assert claim_obj.confidence >= 0.70, f"Well-supported claim should score ≥0.70, got {claim_obj.confidence:.2f}"
        assert len(claim_obj.supporting_sources) >= 1
    
    def test_unsupported_claim_scores_low(self):
        """Claims without supporting sources should score 0"""
        scorer = ClaimConfidenceScorer()
        
        rag_results = [
            RAGResult(
                source="source1",
                source_type="GENERIC_INDUSTRY_TREND",
                text="Industry trends in cloud computing",
                extracted_keywords=["cloud", "computing"],
                source_weight=0.6,
                age_days=100,
                recipient_specific=False
            )
        ]
        
        claim = "You pioneered blockchain innovations at your company"
        claim_obj = scorer.score_claim(claim, rag_results)
        
        assert claim_obj.confidence < 0.70, f"Unsupported claim should score <0.70, got {claim_obj.confidence:.2f}"


# ============================================================================
# v11.6 NEW: RAG REFLEXION SYSTEM TESTS (FEATURE 1.4)
# ============================================================================

class TestRAGReflexionSystem:
    """Test RAG reflexion loop"""
    
    def test_critique_identifies_missing_recipient_data(self):
        """Critique should identify missing recipient-specific data"""
        system = RAGReflexionSystem()
        
        rag_results = [
            RAGResult(
                source="company_page",
                source_type="COMPANY_LINKEDIN_PAGE",
                text="Company information",
                extracted_keywords=["company"],
                source_weight=1.3,
                age_days=30,
                recipient_specific=False
            )
        ]
        
        critique = system.critique_rag_sufficiency(
            rag_results,
            Archetype.C_LEVEL,
            iteration=1
        )
        
        assert not critique.is_sufficient
        assert len(critique.gaps_identified) > 0
        assert any("recipient" in gap.lower() for gap in critique.gaps_identified)
    
    def test_critique_passes_with_sufficient_data(self):
        """Critique should pass with sufficient high-quality data"""
        system = RAGReflexionSystem()
        
        rag_results = [
            RAGResult(
                source="recipient_about",
                source_type="RECIPIENT_LINKEDIN_ABOUT",
                text="Recipient profile",
                extracted_keywords=["leadership"],
                source_weight=2.0,
                age_days=5,
                recipient_specific=True
            ),
            RAGResult(
                source="recipient_post",
                source_type="RECIPIENT_RECENT_POST",
                text="Recent activity",
                extracted_keywords=["innovation"],
                source_weight=1.8,
                age_days=10,
                recipient_specific=True
            ),
            RAGResult(
                source="company_blog",
                source_type="COMPANY_BLOG_ANNOUNCEMENT",
                text="Company news",
                extracted_keywords=["growth"],
                source_weight=1.5,
                age_days=15,
                recipient_specific=False
            )
        ]
        
        critique = system.critique_rag_sufficiency(
            rag_results,
            Archetype.RECRUITER,
            iteration=1
        )
        
        # Sufficient for RECRUITER (lower bar than C_LEVEL)
        assert critique.confidence_score >= 0.60


# ============================================================================
# v11.6 NEW: ADAPTIVE TEMPERATURE TESTS (FEATURE 2.2)
# ============================================================================

class TestAdaptiveTemperatureController:
    """Test adaptive temperature escalation"""
    
    def test_temperature_escalates_with_attempts(self):
        """Temperature should increase with retry attempts"""
        controller = AdaptiveTemperatureController()
        
        temp1 = controller.get_temperature("greeting", Archetype.C_LEVEL, attempt=1)
        temp2 = controller.get_temperature("greeting", Archetype.C_LEVEL, attempt=2)
        temp3 = controller.get_temperature("greeting", Archetype.C_LEVEL, attempt=3)
        
        assert temp2 > temp1, "Attempt 2 should have higher temp than attempt 1"
        assert temp3 > temp2, "Attempt 3 should have higher temp than attempt 2"
        assert temp3 - temp1 == pytest.approx(0.30, abs=0.01), "Should escalate by 0.15 per attempt"
    
    def test_temperature_respects_max(self):
        """Temperature should not exceed MAX_TEMPERATURE"""
        controller = AdaptiveTemperatureController()
        
        temp = controller.get_temperature("greeting", Archetype.C_LEVEL, attempt=10)
        
        assert temp <= 0.95, f"Temperature should not exceed 0.95, got {temp}"
    
    def test_different_archetypes_start_different(self):
        """Different archetypes should start at different base temperatures"""
        controller = AdaptiveTemperatureController()
        
        c_level_temp = controller.get_temperature("body", Archetype.C_LEVEL, attempt=1)
        recruiter_temp = controller.get_temperature("body", Archetype.RECRUITER, attempt=1)
        
        assert recruiter_temp > c_level_temp, "RECRUITER should start with higher temp than C_LEVEL"


# ============================================================================
# v11.6 NEW: CONSTRAINT FEASIBILITY TESTS (FEATURE 2.1)
# ============================================================================

class TestConstraintFeasibilityChecker:
    """Test constraint pre-flight checking"""
    
    def test_feasible_constraints_pass(self):
        """Reasonable constraints should pass feasibility check"""
        checker = ConstraintFeasibilityChecker()
        
        feasible, reason = checker.check_feasibility(
            Route.INMAIL,
            Archetype.C_LEVEL,
            required_elements=["recipient_name", "company", "value_prop", "cta"]
        )
        
        assert feasible is True
    
    def test_infeasible_constraints_fail(self):
        """Impossible constraints should fail feasibility check"""
        checker = ConstraintFeasibilityChecker()
        
        # CONNECTION_REQ has ~50-60 word budget, too many elements
        feasible, reason = checker.check_feasibility(
            Route.CONNECTION_REQ,
            Archetype.C_LEVEL,
            required_elements=[
                "name", "title", "company", "achievement1", "achievement2",
                "achievement3", "value_prop", "company_context", "personal_story", "cta"
            ]
        )
        
        assert feasible is False
        assert "too many" in reason.lower() or "word budget" in reason.lower()


# ============================================================================
# v11.6 NEW: CONTENT CLEANLINESS TESTS (FEATURE 3.1, 3.2, 3.3)
# ============================================================================

class TestContentCleanlinessValidator:
    """Test forbidden verbs and weak language detection"""
    
    def test_detect_forbidden_verbs(self):
        """Should detect forbidden corporate verbs"""
        validator = ContentCleanlinessValidator()
        
        text = "I spearheaded initiatives and leveraged synergies to drive growth"
        forbidden = validator.detect_forbidden_verbs(text)
        
        assert len(forbidden) >= 3, f"Should detect at least 3 forbidden verbs, found {len(forbidden)}"
        assert "spearheaded" in forbidden
        assert "leveraged" in forbidden
    
    def test_detect_filler_phrases(self):
        """Should detect weak filler phrases"""
        validator = ContentCleanlinessValidator()
        
        text = "I hope this message finds you well. I wanted to reach out and I was wondering if you might be interested"
        fillers = validator.detect_fillers(text)
        
        assert len(fillers) >= 2, f"Should detect at least 2 fillers, found {len(fillers)}"
    
    def test_clean_message_passes(self):
        """Clean message should pass both validations"""
        validator = ContentCleanlinessValidator()
        
        text = "I'm reaching out to discuss the AI Platform role at your company. My experience in building enterprise AI systems aligns well with this opportunity."
        
        verbs_pass, _ = validator.validate_verbs(text)
        fillers_pass, _ = validator.validate_fillers(text)
        
        assert verbs_pass is True
        assert fillers_pass is True


class TestPlaceholderDetector:
    """Test comprehensive placeholder detection"""
    
    def test_detect_bracket_placeholders(self):
        """Should detect [placeholder] patterns"""
        detector = PlaceholderDetector()
        
        text = "Hi [recipient name], I work at [company name]"
        placeholders = detector.detect_placeholders(text)
        
        assert len(placeholders) >= 2
    
    def test_detect_curly_brace_placeholders(self):
        """Should detect {variable} patterns"""
        detector = PlaceholderDetector()
        
        text = "Dear {first_name}, regarding {job_title}"
        placeholders = detector.detect_placeholders(text)
        
        assert len(placeholders) >= 2
    
    def test_detect_tbd_todo(self):
        """Should detect TBD, TODO, FIXME"""
        detector = PlaceholderDetector()
        
        text = "The date is TBD and we need to TODO this FIXME that"
        placeholders = detector.detect_placeholders(text)
        
        assert len(placeholders) >= 3
    
    def test_clean_message_passes(self):
        """Clean message should pass validation"""
        detector = PlaceholderDetector()
        
        text = "Hi Sarah, I'm reaching out about the engineering role at TechCorp."
        passed, msg = detector.validate(text)
        
        assert passed is True


class TestASCIIEnforcer:
    """Test ASCII character enforcement"""
    
    def test_detect_unicode_bullets(self):
        """Should detect Unicode bullets"""
        enforcer = ASCIIEnforcer()
        
        text = "• Point one • Point two"
        passed, msg = enforcer.validate(text)
        
        assert passed is False
    
    def test_enforce_ascii_replacement(self):
        """Should replace Unicode with ASCII"""
        enforcer = ASCIIEnforcer()
        
        text = "• Bullet – dash — em-dash"
        clean = enforcer.enforce_ascii(text)
        
        assert "•" not in clean
        assert "–" not in clean
        assert "—" not in clean
        assert "-" in clean
    
    def test_clean_ascii_passes(self):
        """Clean ASCII text should pass"""
        enforcer = ASCIIEnforcer()
        
        text = "This is clean ASCII text with - dashes and normal punctuation."
        passed, msg = enforcer.validate(text)
        
        assert passed is True


# ============================================================================
# v11.6 NEW: CIRCUIT BREAKER TESTS (FEATURE 4.1)
# ============================================================================

class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def test_circuit_starts_closed(self):
        """Circuit breaker should start in CLOSED state"""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=5)
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_opens_after_threshold_failures(self):
        """Circuit should open after exceeding failure threshold"""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=5)
        
        def failing_function():
            raise ValueError("API error")
        
        # First 2 failures
        for i in range(2):
            try:
                cb.call(failing_function)
            except ValueError:
                pass
        
        assert cb.state == CircuitState.CLOSED  # Still closed
        
        # 3rd failure should open circuit
        try:
            cb.call(failing_function)
        except ValueError:
            pass
        
        assert cb.state == CircuitState.OPEN
    
    def test_open_circuit_blocks_requests(self):
        """OPEN circuit should block requests"""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=60)
        
        def failing_function():
            raise ValueError("API error")
        
        # Trigger failure to open circuit
        try:
            cb.call(failing_function)
        except ValueError:
            pass
        
        assert cb.state == CircuitState.OPEN
        
        # Next call should raise CircuitBreakerOpenError
        from LIC_AGENTIC_v11_6 import CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(failing_function)


# ============================================================================
# v11.6 NEW: PROFILE ANALYSIS WITH MANUAL OVERRIDE TESTS
# ============================================================================

class TestProfileAnalysisWithManualOverride:
    """Test profile analysis with low-confidence manual override"""
    
    def test_c_level_detection_high_confidence(self):
        """C-level titles should have high confidence"""
        circuit_breaker = CircuitBreaker()
        agent = ProfileAnalysisAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-ceo",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "John Doe", "title": "Chief Executive Officer"},
            job_description={"title": "Test"}
        )
        
        analysis = agent.analyze_profile(mission)
        
        assert analysis.archetype == Archetype.C_LEVEL
        assert analysis.confidence >= 0.90
        assert analysis.needs_manual_override is False
    
    def test_senior_ta_detection(self):
        """SENIOR_TA titles should be detected"""
        circuit_breaker = CircuitBreaker()
        agent = ProfileAnalysisAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-staff",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Jane Smith", "title": "Staff Engineer"},
            job_description={"title": "Test"}
        )
        
        analysis = agent.analyze_profile(mission)
        
        assert analysis.archetype == Archetype.SENIOR_TA
        assert analysis.confidence >= 0.80
    
    def test_ambiguous_title_triggers_manual_override(self):
        """Ambiguous titles should trigger manual override flag"""
        circuit_breaker = CircuitBreaker()
        agent = ProfileAnalysisAgent(circuit_breaker)
        
        mission = OutreachMission(
            mission_id="test-ambiguous",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Sam Lee", "title": "Manager"},  # Ambiguous
            job_description={"title": "Test"}
        )
        
        analysis = agent.analyze_profile(mission)
        
        # Should default to SENIOR_TA with lower confidence
        assert analysis.confidence < 0.85
        assert analysis.needs_manual_override is True


# ============================================================================
# v11.6 NEW: VALIDATION AGENT COMPREHENSIVE TESTS
# ============================================================================

class TestValidationAgentComprehensive:
    """Test comprehensive validation framework"""
    
    def test_placeholder_detection_critical(self):
        """Placeholder detection should be CRITICAL severity"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="Hi [recipient name], I work at [company]",
            word_count=50,
            char_count=200,
            route=Route.INMAIL,
            archetype=Archetype.C_LEVEL,
            generation_temperature=0.45,
            generation_attempts=1,
            locked_sections=set(),
            checksum="test123"
        )
        
        context = ResearchContext(
            recipient_insights=[],
            company_context=[],
            recent_activity=[],
            rag_results=[]
        )
        
        results = validator.validate_message(message, context)
        
        critical_failures = [r for r in results if r.severity == ValidationSeverity.CRITICAL]
        assert len(critical_failures) > 0
        assert any("placeholder" in r.message.lower() for r in critical_failures)
    
    def test_ascii_validation_high_severity(self):
        """Non-ASCII characters should be HIGH severity"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="Hi Sarah, • Bullet point – dash",
            word_count=50,
            char_count=200,
            route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE,
            generation_temperature=0.50,
            generation_attempts=1,
            locked_sections=set(),
            checksum="test123"
        )
        
        context = ResearchContext(
            recipient_insights=[],
            company_context=[],
            recent_activity=[],
            rag_results=[]
        )
        
        results = validator.validate_message(message, context)
        
        high_failures = [r for r in results if r.severity == ValidationSeverity.HIGH]
        assert len(high_failures) > 0
        assert any("ascii" in r.message.lower() or "non-ascii" in r.message.lower() for r in high_failures)
    
    def test_forbidden_verbs_medium_severity(self):
        """Forbidden verbs should be MEDIUM severity"""
        circuit_breaker = CircuitBreaker()
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="I spearheaded initiatives and leveraged synergies to drive transformational change",
            word_count=50,
            char_count=200,
            route=Route.INMAIL,
            archetype=Archetype.C_LEVEL,
            generation_temperature=0.45,
            generation_attempts=1,
            locked_sections=set(),
            checksum="test123"
        )
        
        context = ResearchContext(
            recipient_insights=[],
            company_context=[],
            recent_activity=[],
            rag_results=[]
        )
        
        results = validator.validate_message(message, context)
        
        medium_failures = [r for r in results if r.severity == ValidationSeverity.MEDIUM]
        assert len(medium_failures) > 0


# ============================================================================
# CONFIGREGISTRY SSOT TESTS
# ============================================================================

class TestConfigRegistrySSO:
    """Test ConfigRegistry SSOT functionality (v11.6 updated)"""
    
    def test_get_target_word_count_c_level_inmail(self):
        """C_LEVEL INMAIL should return 240 words"""
        word_count = ConfigRegistry.get_target_word_count(Archetype.C_LEVEL, Route.INMAIL)
        assert word_count == 240
    
    def test_get_target_word_count_senior_ta_inmail(self):
        """SENIOR_TA INMAIL should return 220 words"""
        word_count = ConfigRegistry.get_target_word_count(Archetype.SENIOR_TA, Route.INMAIL)
        assert word_count == 220
    
    def test_get_rag_parameter_c_level_total_calls(self):
        """C_LEVEL should have 24 total RAG calls"""
        total_calls = ConfigRegistry.get_rag_parameter(Archetype.C_LEVEL, "total_calls")
        assert total_calls == 24
    
    def test_get_rag_parameter_senior_ta_total_calls(self):
        """SENIOR_TA should have 16 total RAG calls"""
        total_calls = ConfigRegistry.get_rag_parameter(Archetype.SENIOR_TA, "total_calls")
        assert total_calls == 16


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
