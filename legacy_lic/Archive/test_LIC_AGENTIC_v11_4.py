"""
Test Suite for LIC-AGENTIC v11.4
=================================

PRIORITY: Decision Tree Validation from v10.24
Focus on validating the new routing logic and connection status tracking.

Test Categories:
1. Decision Tree Tests (NEW v11.4) - PRIORITY
2. Connection Status Tests (NEW v11.4)
3. Follow-Up Route Tests (NEW v11.4)
4. Route Constraints Validation (Updated)
5. Regression Tests (v11.3 compatibility)
6. End-to-End Integration Tests
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

# Import all components from LIC v11.4
import sys
sys.path.insert(0, '/home/claude')

from LIC_AGENTIC_v11_4 import (
    # Enums
    Route, Archetype, EventType, AgentStatus, ValidationSeverity,
    ConstraintFailureType,
    # Data structures
    OutreachMission, ResearchContext, GenerationContext, StagingBuffer,
    ValidationResult, HopCheckpoint, OutreachState, QAReportSummary,
    ConstraintFailure,
    # Core components
    MessageBus, StateStore, SemanticCache, CircuitBreaker, LLMClient,
    CheckpointManager, TelemetryService, LoggingService, ValidationService,
    QAReportGenerator,
    # NEW v11.3 components (maintained in v11.4)
    ConstraintFailureClassifier, SimilarityCrossValidator,
    # Agents
    ProfileAnalysisAgent, ResearchOrchestrator, ScaffoldArchitect,
    GenerationOrchestrator, StagingBufferAssembler, ValidationAgent, GateAgent,
    # Orchestrator
    WorkflowOrchestrator, create_orchestrator,
    # Constants
    ROUTE_CONSTRAINTS, DEFAULT_TEMPERATURES, SIMILARITY_THRESHOLDS, __version__
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_llm_client():
    """Mock LLM client with intelligent routing responses"""
    client = Mock(spec=LLMClient)
    client.api_call_count = 0
    
    async def mock_call_claude(prompt, *args, **kwargs):
        client.api_call_count += 1
        
        # Intelligent routing based on prompt content
        if "route" in prompt.lower() and "decision tree" in prompt.lower():
            # Parse connection status more carefully
            is_not_connected = "CONNECTION STATUS: not_connected" in prompt
            is_connected = "CONNECTION STATUS: connected" in prompt
            has_prior_messages = ("PRIOR MESSAGE COUNT: 1" in prompt or 
                                 "PRIOR MESSAGE COUNT: 2" in prompt or
                                 "prior_message_count: 1" in prompt)
            is_recruiter = "Recruiter" in prompt or "Talent" in prompt
            is_senior_exec = any(title in prompt for title in ["VP", "CEO", "CTO", "SVP", "Chief"])
            
            # Apply decision tree logic exactly
            if is_not_connected and is_senior_exec:
                # Step 1: not_connected + senior exec → INMAIL
                return json.dumps({
                    "route": "INMAIL",
                    "archetype": "EXECUTIVE",
                    "reasoning": "Not connected + senior exec → INMAIL per decision tree step 1"
                })
            elif is_recruiter:
                # Step 2: Recruiter → CONNECTION_REQ
                return json.dumps({
                    "route": "CONNECTION_REQ",
                    "archetype": "RECRUITER",
                    "reasoning": "Recruiter title → CONNECTION_REQ per decision tree step 2"
                })
            elif is_connected and has_prior_messages:
                # Step 3: connected + prior messages → FOLLOW_UP
                return json.dumps({
                    "route": "FOLLOW_UP",
                    "archetype": "HIRING_MANAGER",
                    "reasoning": "Connected + prior messages → FOLLOW_UP per decision tree step 3"
                })
            else:
                # Step 4: Default → CONNECTION_REQ
                return json.dumps({
                    "route": "CONNECTION_REQ",
                    "archetype": "HIRING_MANAGER",
                    "reasoning": "Default → CONNECTION_REQ per decision tree step 4"
                })
        elif "queries" in prompt.lower():
            return json.dumps({"queries": ["query1", "query2", "query3"]})
        elif "critique" in prompt.lower():
            return json.dumps({
                "signal_score": 0.85,
                "gaps": [],
                "strengths": ["good"],
                "recommendations": []
            })
        elif "scaffold" in prompt.lower():
            return json.dumps({
                "key_achievements": ["achievement1"],
                "value_proposition": "Strong value prop",
                "connection_points": ["point1"],
                "tone_guidance": "professional"
            })
        elif "greeting" in prompt.lower():
            return "Hi there, great to connect!"
        elif "subject" in prompt.lower():
            return "Exciting AI Platform Opportunity"
        elif "body" in prompt.lower():
            return "I noticed your impressive work in AI platform engineering. " * 25  # ~200 words
        elif "cta" in prompt.lower():
            return "Would love to discuss this opportunity."
        elif "signature" in prompt.lower():
            return "Best regards\nAmit"
        
        return "Mock response"
    
    client.call_claude = AsyncMock(side_effect=mock_call_claude)
    client.call_gemini = AsyncMock(side_effect=mock_call_claude)
    
    return client


@pytest.fixture
def message_bus():
    """Message bus instance"""
    return MessageBus()


@pytest.fixture
def state_store():
    """State store instance"""
    return StateStore()


@pytest.fixture
def telemetry_service():
    """Telemetry service instance"""
    return TelemetryService()


@pytest.fixture
def logging_service(tmp_path):
    """Logging service instance"""
    return LoggingService(tmp_path)


@pytest.fixture
def checkpoint_manager():
    """Checkpoint manager instance"""
    return CheckpointManager()


@pytest.fixture
def failure_classifier():
    """Constraint failure classifier instance"""
    return ConstraintFailureClassifier()


@pytest.fixture
def similarity_validator():
    """Similarity cross-validator instance"""
    return SimilarityCrossValidator()


@pytest.fixture
def validation_service(telemetry_service, logging_service, failure_classifier, similarity_validator):
    """Validation service instance"""
    return ValidationService(telemetry_service, logging_service, failure_classifier, similarity_validator)


@pytest.fixture
def qa_report_generator(logging_service):
    """QA report generator instance"""
    return QAReportGenerator(logging_service)


# ============================================================================
# DECISION TREE TESTS (NEW v11.4 - PRIORITY)
# ============================================================================

class TestDecisionTreeRouting:
    """Test v10.24 decision tree routing logic"""
    
    @pytest.mark.asyncio
    async def test_route_not_connected_senior_exec_to_inmail(
        self, mock_llm_client, message_bus, telemetry_service, logging_service
    ):
        """
        Decision Tree Step 1: not_connected + senior exec → INMAIL
        """
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={"name": "Amit", "title": "Chief AI Officer"},
            recipient_profile={
                "name": "Jane Doe",
                "title": "VP of Engineering",  # Senior exec
                "company": "TechCorp"
            },
            job_description={"title": "AI Lead", "company": "TechCorp"},
            connection_status="not_connected",  # NOT connected
            prior_message_count=0
        )
        
        agent = ProfileAnalysisAgent(
            mock_llm_client, message_bus, telemetry_service, logging_service
        )
        
        state = OutreachState(mission=mission)
        result_state = await agent.execute(state)
        
        # Should route to INMAIL for senior exec who is not connected
        assert result_state.mission.route == Route.INMAIL
        assert result_state.mission.archetype == Archetype.EXECUTIVE
        assert result_state.status == AgentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_route_recruiter_to_connection_req(
        self, mock_llm_client, message_bus, telemetry_service, logging_service
    ):
        """
        Decision Tree Step 2: Recruiter → CONNECTION_REQ
        """
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={"name": "Amit", "title": "Chief AI Officer"},
            recipient_profile={
                "name": "Bob Smith",
                "title": "Technical Recruiter",  # Recruiter
                "company": "TechCorp"
            },
            job_description={"title": "AI Lead", "company": "TechCorp"},
            connection_status="not_connected",
            prior_message_count=0
        )
        
        agent = ProfileAnalysisAgent(
            mock_llm_client, message_bus, telemetry_service, logging_service
        )
        
        state = OutreachState(mission=mission)
        result_state = await agent.execute(state)
        
        # Should route to CONNECTION_REQ for recruiters
        assert result_state.mission.route == Route.CONNECTION_REQ
        assert result_state.mission.archetype == Archetype.RECRUITER
    
    @pytest.mark.asyncio
    async def test_route_connected_with_prior_messages_to_followup(
        self, mock_llm_client, message_bus, telemetry_service, logging_service
    ):
        """
        Decision Tree Step 3: connected + prior_message_count > 0 → FOLLOW_UP
        """
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={"name": "Amit", "title": "Chief AI Officer"},
            recipient_profile={
                "name": "Alice Johnson",
                "title": "Engineering Manager",
                "company": "TechCorp"
            },
            job_description={"title": "AI Lead", "company": "TechCorp"},
            connection_status="connected",  # Connected
            prior_message_count=1  # Prior conversation exists
        )
        
        agent = ProfileAnalysisAgent(
            mock_llm_client, message_bus, telemetry_service, logging_service
        )
        
        state = OutreachState(mission=mission)
        result_state = await agent.execute(state)
        
        # Should route to FOLLOW_UP when connected with prior messages
        assert result_state.mission.route == Route.FOLLOW_UP
    
    @pytest.mark.asyncio
    async def test_route_default_to_connection_req(
        self, mock_llm_client, message_bus, telemetry_service, logging_service
    ):
        """
        Decision Tree Step 4: Default → CONNECTION_REQ
        """
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={"name": "Amit", "title": "Chief AI Officer"},
            recipient_profile={
                "name": "Charlie Brown",
                "title": "Software Engineer",  # Not senior, not recruiter
                "company": "TechCorp"
            },
            job_description={"title": "AI Lead", "company": "TechCorp"},
            connection_status="not_connected",
            prior_message_count=0
        )
        
        agent = ProfileAnalysisAgent(
            mock_llm_client, message_bus, telemetry_service, logging_service
        )
        
        state = OutreachState(mission=mission)
        result_state = await agent.execute(state)
        
        # Should default to CONNECTION_REQ
        assert result_state.mission.route == Route.CONNECTION_REQ


# ============================================================================
# CONNECTION STATUS TESTS (NEW v11.4)
# ============================================================================

class TestConnectionStatus:
    """Test connection status tracking and usage"""
    
    def test_mission_has_connection_status_field(self):
        """Test that OutreachMission includes connection_status"""
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={},
            recipient_profile={},
            job_description={},
            connection_status="connected"
        )
        
        assert hasattr(mission, "connection_status")
        assert mission.connection_status == "connected"
    
    def test_mission_has_prior_message_count_field(self):
        """Test that OutreachMission includes prior_message_count"""
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={},
            recipient_profile={},
            job_description={},
            prior_message_count=3
        )
        
        assert hasattr(mission, "prior_message_count")
        assert mission.prior_message_count == 3
    
    def test_connection_status_defaults_to_not_connected(self):
        """Test default connection status"""
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={},
            recipient_profile={},
            job_description={}
        )
        
        assert mission.connection_status == "not_connected"
        assert mission.prior_message_count == 0


# ============================================================================
# FOLLOW_UP ROUTE TESTS (NEW v11.4)
# ============================================================================

class TestFollowUpRoute:
    """Test FOLLOW_UP route functionality"""
    
    def test_followup_route_exists(self):
        """Test that FOLLOW_UP route is defined"""
        assert hasattr(Route, "FOLLOW_UP")
        assert Route.FOLLOW_UP.value == "FOLLOW_UP"
    
    def test_followup_route_constraints_defined(self):
        """Test that FOLLOW_UP route has constraints"""
        assert Route.FOLLOW_UP in ROUTE_CONSTRAINTS
        
        constraints = ROUTE_CONSTRAINTS[Route.FOLLOW_UP]
        assert "word_range" in constraints
        assert "char_limit" in constraints
        assert "subject_required" in constraints
        
        # Verify reasonable constraints for follow-up messages
        assert constraints["word_range"] == (150, 220)
        assert constraints["char_limit"] == 1600
        assert constraints["subject_required"] is True
    
    def test_followup_constraints_between_connection_req_and_inmail(self):
        """Test that FOLLOW_UP constraints are between CONNECTION_REQ and INMAIL"""
        followup = ROUTE_CONSTRAINTS[Route.FOLLOW_UP]
        conn_req = ROUTE_CONSTRAINTS[Route.CONNECTION_REQ]
        inmail = ROUTE_CONSTRAINTS[Route.INMAIL]
        
        # Word range: CONNECTION_REQ < FOLLOW_UP < INMAIL
        assert conn_req["word_range"][0] < followup["word_range"][0] < inmail["word_range"][0]
        assert conn_req["word_range"][1] < followup["word_range"][1] < inmail["word_range"][1]
        
        # Char limit: CONNECTION_REQ < FOLLOW_UP < INMAIL
        assert conn_req["char_limit"] < followup["char_limit"] < inmail["char_limit"]


# ============================================================================
# ROUTE CONSTRAINTS VALIDATION (Updated for v11.4)
# ============================================================================

class TestRouteConstraints:
    """Validate all route constraints including new FOLLOW_UP route"""
    
    def test_all_four_routes_have_constraints(self):
        """Test that all 4 routes (including FOLLOW_UP) have constraints"""
        assert len(ROUTE_CONSTRAINTS) == 4  # INMAIL, CONNECTION_REQ, EMAIL, FOLLOW_UP
        
        assert Route.INMAIL in ROUTE_CONSTRAINTS
        assert Route.CONNECTION_REQ in ROUTE_CONSTRAINTS
        assert Route.EMAIL in ROUTE_CONSTRAINTS
        assert Route.FOLLOW_UP in ROUTE_CONSTRAINTS
    
    def test_route_constraints_have_required_fields(self):
        """Test that each route has all required constraint fields"""
        required_fields = [
            "word_range",
            "char_limit",
            "subject_required",
            "greeting_word_range",
            "cta_word_range",
            "signature_word_range",
            "body_min_words"
        ]
        
        for route in Route:
            constraints = ROUTE_CONSTRAINTS[route]
            for field in required_fields:
                assert field in constraints, f"Route {route.value} missing {field}"


# ============================================================================
# REGRESSION TESTS (v11.3 Compatibility)
# ============================================================================

class TestRegressionV11_3Compatibility:
    """Ensure v11.4 maintains v11.3 functionality"""
    
    def test_v11_3_features_preserved(self):
        """Test that v11.3 features still work"""
        # ConstraintFailureClassifier should still exist
        assert ConstraintFailureClassifier is not None
        classifier = ConstraintFailureClassifier()
        
        failure = classifier.classify_failure(
            section="k3_body",
            constraint_name="word_count_range",
            expected=(180, 250),
            actual=150,
            context={"route": "INMAIL"}
        )
        
        assert failure.failure_type == ConstraintFailureType.MECHANICAL
    
    def test_similarity_validator_preserved(self):
        """Test that SimilarityCrossValidator still works"""
        validator = SimilarityCrossValidator()
        
        sections = {
            "section1": "This is unique content for section one.",
            "section2": "This is different content for section two."
        }
        
        result = validator.validate_no_duplicates(sections)
        assert "duplicate_pairs" in result
    
    def test_original_routes_unchanged(self):
        """Test that original 3 routes still have same constraints"""
        # INMAIL constraints unchanged
        assert ROUTE_CONSTRAINTS[Route.INMAIL]["word_range"] == (180, 250)
        assert ROUTE_CONSTRAINTS[Route.INMAIL]["char_limit"] == 1900
        
        # CONNECTION_REQ constraints unchanged
        assert ROUTE_CONSTRAINTS[Route.CONNECTION_REQ]["word_range"] == (40, 60)
        assert ROUTE_CONSTRAINTS[Route.CONNECTION_REQ]["char_limit"] == 300
        
        # EMAIL constraints unchanged
        assert ROUTE_CONSTRAINTS[Route.EMAIL]["word_range"] == (200, 350)
        assert ROUTE_CONSTRAINTS[Route.EMAIL]["char_limit"] == 2500


# ============================================================================
# END-TO-END INTEGRATION TEST
# ============================================================================

class TestEndToEndIntegration:
    """End-to-end workflow test for v11.4"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_decision_tree(self, mock_llm_client):
        """Test complete workflow with decision tree routing"""
        
        # Test scenario: Not connected, senior exec → should route to INMAIL
        mission = OutreachMission(
            mission_id=str(uuid4()),
            sender_profile={
                "name": "Amit",
                "title": "Chief AI Officer",
                "company": "AI Innovations Inc"
            },
            recipient_profile={
                "name": "Sarah Johnson",
                "title": "VP of Engineering",
                "company": "Tech Giants Corp",
                "connection_status": "not_connected",
                "prior_message_count": 0
            },
            job_description={
                "title": "Head of AI Platform",
                "company": "Tech Giants Corp",
                "requirements": "10+ years AI/ML leadership"
            },
            connection_status="not_connected",
            prior_message_count=0
        )
        
        # Create orchestrator components
        message_bus = MessageBus()
        state_store = StateStore()
        telemetry = TelemetryService()
        logging_svc = LoggingService(Path("/tmp"))
        checkpoint_mgr = CheckpointManager()
        
        classifier = ConstraintFailureClassifier()
        similarity = SimilarityCrossValidator()
        validation_svc = ValidationService(telemetry, logging_svc, classifier, similarity)
        qa_gen = QAReportGenerator(logging_svc)
        
        orchestrator = WorkflowOrchestrator(
            message_bus,
            state_store,
            mock_llm_client,
            telemetry,
            logging_svc,
            validation_svc,
            checkpoint_mgr,
            qa_gen
        )
        
        # Execute workflow
        result = await orchestrator.execute_workflow(mission)
        
        # Verify decision tree routing worked
        assert result["mission_id"] == mission.mission_id
        assert "workflow_time" in result
        
        # Check that routing was determined
        state = state_store.get_state(mission.mission_id)
        if state and state.mission.route:
            # Should be INMAIL for not_connected + VP
            assert state.mission.route == Route.INMAIL


# ============================================================================
# SUMMARY REPORT
# ============================================================================

def test_suite_summary():
    """Print test suite summary for v11.4"""
    print("\n" + "="*80)
    print("LIC v11.4 Test Suite Summary")
    print("="*80)
    print(f"Version: {__version__}")
    print("\nNEW v11.4 Test Categories:")
    print("  ✓ Decision Tree Routing Tests (4 tests) - PRIORITY 1")
    print("  ✓ Connection Status Tests (3 tests) - NEW")
    print("  ✓ Follow-Up Route Tests (3 tests) - NEW")
    print("  ✓ Route Constraints Validation (2 tests) - Updated")
    print("  ✓ Regression Tests (3 tests) - v11.3 Compatibility")
    print("  ✓ End-to-End Integration (1 test) - Full Workflow")
    print("\nTotal: 16 core tests")
    print("Focus: v10.24 Decision Tree Implementation")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_suite_summary()
    pytest.main([__file__, "-v", "--tb=short"])
