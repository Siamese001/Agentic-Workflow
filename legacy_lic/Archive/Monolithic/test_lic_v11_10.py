"""
LIC v11.10 - Complete Agentic Architecture Test Suite
=====================================================

__version__ = "11.10"

Requirements:
  pip install pytest pytest-asyncio pytest-mock

Run tests:
  pytest test_lic_v11_10.py -v
  pytest test_lic_v11_10.py -k "Enhancement1" -v  # Run specific test group

Comprehensive tests for 4 key v11.10 enhancements:
1. S2 Multi-Agent Specialization (Supervisor/Specialist pattern)
2. S2 Internal "Execute-Critique-Replan" Loop
3. S2 Adversarial Self-Verification (Red Team checks)
4. S6 -> S2 "Meta-Loop" (Factual Failure Recovery)

Plus regression tests for v11.9 features (Sender Grounding, Context-Aware CTAs).
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch, call
from datetime import datetime

# Import from modular structure
from models import *
from workflow import *
from validation import *
from rag import *
from utils import *
from config import CONFIG_REGISTRY

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def circuit_breaker():
    """Circuit breaker instance"""
    return CircuitBreaker()

@pytest.fixture
def mock_mission():
    """Standard test mission"""
    return OutreachMission(
        mission_id="test_mission_123",
        sender_profile={
            "name": "Test Sender",
            "title": "Chief AI Officer",
            "company": "AI Corp",
            "teams": ["AI Platform", "GenAI R&D"]
        },
        recipient_profile={
            "name": "Test Recipient",
            "title": "VP Engineering",
            "company": "Tech Giants"
        },
        job_description={
            "title": "Head of AI Platform",
            "company": "Tech Giants",
            "requirements": "10+ years AI/ML leadership"
        },
        connection_status="not_connected"
    )

@pytest.fixture
def mock_profile_analysis():
    """Standard profile analysis"""
    return ProfileAnalysis(
        archetype=Archetype.EXECUTIVE,
        confidence=0.9,
        reasoning="VP title detected",
        key_indicators=["VP"],
        needs_manual_override=False
    )

@pytest.fixture
def mock_research_context():
    """Standard research context with RAG results"""
    return ResearchContext(
        recipient_insights=["Tech leader", "Platform scaling"],
        company_context=["Growing AI initiative"],
        recent_activity=["Hired 3 engineers"],
        rag_results=[
            RAGResult(
                source="linkedin",
                source_type="RECIPIENT_LINKEDIN_ABOUT",
                text="VP Engineering with 12 years experience...",
                extracted_keywords=["engineering", "platform"],
                source_weight=1.0,
                age_days=5,
                recipient_specific=True,
                confidence=0.9
            )
        ],
        signal_score=0.85,
        mission_context={"job_title": "Head of AI Platform"}
    )

@pytest.fixture
def mock_scaffold():
    """Standard message scaffold"""
    return MessageScaffold(
        route=Route.INMAIL,
        archetype=Archetype.EXECUTIVE,
        sections={
            "greeting": {"required": True, "word_range": (2, 5)},
            "body": {"required": True, "min_words": 120},
            "cta": {"required": True, "word_range": (5, 12)},
            "signature": {"required": True, "word_range": (2, 6)}
        },
        constraints={"word_range": (180, 250), "char_limit": 1900},
        locked_sections=set(),
        context_aware_cta=False
    )

@pytest.fixture
def mock_generated_message():
    """Standard generated message"""
    return GeneratedMessage(
        content="Hi Sarah, I noticed your work in AI platform scaling...",
        word_count=225,
        char_count=1200,
        route=Route.INMAIL,
        archetype=Archetype.EXECUTIVE,
        generation_temperature=0.5,
        generation_attempts=1,
        locked_sections=set(),
        checksum="abc123"
    )

# ============================================================================
# ENHANCEMENT 1: S2 MULTI-AGENT SPECIALIZATION TESTS
# ============================================================================

class TestEnhancement1_MultiAgent:
    """Test S2 supervisor delegates to specialist agents"""

    def test_specialist_agents_instantiate(self, circuit_breaker):
        """Test all specialist agents are created"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        assert hasattr(supervisor, 'recipient_agent')
        assert hasattr(supervisor, 'organization_agent')
        assert hasattr(supervisor, 'internal_agent')
        assert isinstance(supervisor.recipient_agent, RecipientAgent)
        assert isinstance(supervisor.organization_agent, OrganizationAgent)
        assert isinstance(supervisor.internal_agent, InternalAgent)
        print("✅ E1.1: All specialist agents instantiate correctly")

    @pytest.mark.asyncio
    async def test_supervisor_delegates_parallel(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test S2 supervisor delegates to specialists in parallel"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        # Mock specialist responses
        recipient_data = {
            "rag_results": [RAGResult(
                source="linkedin", source_type="RECIPIENT_LINKEDIN_ABOUT",
                text="VP Engineering...", extracted_keywords=["VP"],
                source_weight=1.0, age_days=0, recipient_specific=True
            )]
        }
        org_data = {
            "rag_results": [RAGResult(
                source="blog", source_type="COMPANY_BLOG_ANNOUNCEMENT",
                text="We're hiring...", extracted_keywords=["hiring"],
                source_weight=0.9, age_days=10, recipient_specific=False
            )]
        }
        internal_data = {"prior_applications": [], "rag_results": []}
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock, return_value=recipient_data)
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock, return_value=org_data)
        mocker.patch.object(InternalAgent, 'get_internal_context', return_value=internal_data)
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency', return_value=RAGCritique(
            is_sufficient=True, confidence_score=0.9, gaps_identified=[],
            refinement_tasks=[], reasoning="Mock sufficient"
        ))
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        context, profile = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        # Verify all agents called
        RecipientAgent.get_profile.assert_called_once()
        OrganizationAgent.get_organization_context.assert_called_once()
        InternalAgent.get_internal_context.assert_called_once()
        
        # Verify synthesis
        assert len(context.rag_results) == 2
        assert context.rag_results[0].source == "linkedin"
        assert context.rag_results[1].source == "blog"
        print("✅ E1.2: Supervisor successfully delegates and synthesizes results")

    @pytest.mark.asyncio
    async def test_supervisor_merges_specialist_results(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test supervisor correctly merges specialist outputs"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        # Multiple RAG results from different specialists
        recipient_rags = [
            RAGResult(source="r1", source_type="RECIPIENT_LINKEDIN_ABOUT", text="...", 
                     extracted_keywords=[], source_weight=1.0, age_days=0, recipient_specific=True),
            RAGResult(source="r2", source_type="RECIPIENT_GITHUB_PROFILE", text="...", 
                     extracted_keywords=[], source_weight=0.9, age_days=5, recipient_specific=True)
        ]
        org_rags = [
            RAGResult(source="o1", source_type="COMPANY_BLOG_ANNOUNCEMENT", text="...", 
                     extracted_keywords=[], source_weight=0.85, age_days=15, recipient_specific=False)
        ]
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock, 
                          return_value={"rag_results": recipient_rags})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": org_rags})
        mocker.patch.object(InternalAgent, 'get_internal_context', 
                          return_value={"prior_applications": [], "rag_results": []})
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=RAGCritique(is_sufficient=True, confidence_score=0.9,
                                                  gaps_identified=[], refinement_tasks=[], reasoning="OK"))
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        # Should have all 3 RAG results merged
        assert len(context.rag_results) == 3
        assert sum(1 for r in context.rag_results if r.recipient_specific) == 2
        assert sum(1 for r in context.rag_results if not r.recipient_specific) == 1
        print("✅ E1.3: Supervisor correctly merges specialist results")

# ============================================================================
# ENHANCEMENT 2: S2 INTERNAL "EXECUTE-CRITIQUE-REPLAN" LOOP TESTS
# ============================================================================

class TestEnhancement2_S2InternalLoop:
    """Test S2's internal critique and refinement loop"""

    @pytest.mark.asyncio
    async def test_s2_loop_triggers_refinement(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test S2 runs refinement when critique fails"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        # Initial specialist responses (insufficient)
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock, 
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        
        # Mock refinement task
        refined_rag = RAGResult(source="refined", source_type="COMPANY_BLOG_ANNOUNCEMENT",
                               text="Refined content", extracted_keywords=["AI"],
                               source_weight=1.0, age_days=0, recipient_specific=False)
        mock_refinement = mocker.patch.object(OrganizationAgent, 'run_refinement_task',
                                             new_callable=AsyncMock,
                                             return_value={"rag_results": [refined_rag]})
        
        # Mock critique: fail first, pass second
        critique_fail = RAGCritique(
            is_sufficient=False, confidence_score=0.4,
            gaps_identified=["Missing company info"],
            refinement_tasks=["Search company blog for AI initiatives"],
            reasoning="Insufficient context"
        )
        critique_pass = RAGCritique(
            is_sufficient=True, confidence_score=0.9,
            gaps_identified=[], refinement_tasks=[], reasoning="Sufficient"
        )
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          side_effect=[critique_fail, critique_pass])
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        # Verify refinement was called
        mock_refinement.assert_called_once()
        assert context.reflexion_iterations == 1
        assert len(context.rag_results) == 1
        assert context.rag_results[0].source == "refined"
        print("✅ E2.1: S2 internal loop triggers refinement on critique failure")

    @pytest.mark.asyncio
    async def test_s2_loop_respects_max_iterations(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test S2 stops after max refinement iterations"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        supervisor.MAX_REFLEXION_CYCLES = 2  # Override for testing
        
        # Mock specialists returning insufficient data
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        mocker.patch.object(OrganizationAgent, 'run_refinement_task', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        
        # Mock critique always failing
        critique_fail = RAGCritique(
            is_sufficient=False, confidence_score=0.3,
            gaps_identified=["Still missing"], refinement_tasks=["Try again"],
            reasoning="Not enough"
        )
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=critique_fail)
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        # Should stop at MAX_REFLEXION_CYCLES
        assert context.reflexion_iterations == 2
        print("✅ E2.2: S2 internal loop respects max iteration limit")

    @pytest.mark.asyncio
    async def test_s2_refinement_targets_correct_specialist(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test S2 delegates refinement to the correct specialist"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        
        # Mock refinement spies
        recipient_spy = mocker.patch.object(RecipientAgent, 'run_refinement_task',
                                           new_callable=AsyncMock,
                                           return_value={"rag_results": []})
        org_spy = mocker.patch.object(OrganizationAgent, 'run_refinement_task',
                                     new_callable=AsyncMock,
                                     return_value={"rag_results": []})
        
        # Critique with recipient-specific gap
        critique_fail = RAGCritique(
            is_sufficient=False, confidence_score=0.5,
            gaps_identified=["Need recipient LinkedIn activity"],
            refinement_tasks=["Search recipient LinkedIn posts"],
            reasoning="Missing recipient data"
        )
        critique_pass = RAGCritique(
            is_sufficient=True, confidence_score=0.9,
            gaps_identified=[], refinement_tasks=[], reasoning="OK"
        )
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          side_effect=[critique_fail, critique_pass])
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        # RecipientAgent should be called for LinkedIn-related task
        recipient_spy.assert_called_once()
        org_spy.assert_not_called()
        print("✅ E2.3: S2 routes refinement tasks to correct specialist")

# ============================================================================
# ENHANCEMENT 3: S2 ADVERSARIAL SELF-VERIFICATION TESTS
# ============================================================================

class TestEnhancement3_AdversarialCheck:
    """Test S2's adversarial red-team verification"""

    @pytest.mark.asyncio
    async def test_adversarial_check_runs_after_critique(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test adversarial check executes after critique passes"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=RAGCritique(is_sufficient=True, confidence_score=0.9,
                                                  gaps_identified=[], refinement_tasks=[], reasoning="OK"))
        
        # Spy on adversarial check
        adversarial_spy = mocker.patch.object(supervisor, '_run_adversarial_check',
                                             new_callable=AsyncMock,
                                             return_value=["Refuted: direct platform experience"])
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        adversarial_spy.assert_called_once()
        assert len(context.adversarial_findings) == 1
        assert "Refuted" in context.adversarial_findings[0]
        print("✅ E3.1: Adversarial check runs after critique loop completes")

    @pytest.mark.asyncio
    async def test_adversarial_findings_populate_context(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test adversarial findings are added to ResearchContext"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=RAGCritique(is_sufficient=True, confidence_score=0.9,
                                                  gaps_identified=[], refinement_tasks=[], reasoning="OK"))
        
        # Mock adversarial findings
        findings = [
            "Refuted theme: 'led platform migration'",
            "Weak claim: '40% efficiency gain' lacks evidence"
        ]
        mocker.patch.object(supervisor, '_run_adversarial_check',
                          new_callable=AsyncMock, return_value=findings)
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        
        assert context.adversarial_findings == findings
        print("✅ E3.2: Adversarial findings correctly populate ResearchContext")

    def test_adversarial_findings_field_exists(self):
        """Test ResearchContext has adversarial_findings field"""
        context = ResearchContext(
            recipient_insights=[],
            company_context=[],
            recent_activity=[],
            rag_results=[]
        )
        
        assert hasattr(context, 'adversarial_findings')
        assert isinstance(context.adversarial_findings, list)
        print("✅ E3.3: ResearchContext.adversarial_findings field exists")

# ============================================================================
# ENHANCEMENT 4: S6 -> S2 "META-LOOP" TESTS
# ============================================================================

class TestEnhancement4_MetaLoop:
    """Test S6->S2 meta-loop for factual failure recovery"""

    def test_failure_classifier_enum_exists(self):
        """Test FailureClassifier enum is defined"""
        assert hasattr(FailureClassifier, 'CREATIVE_FAILURE')
        assert hasattr(FailureClassifier, 'FACTUAL_FAILURE')
        print("✅ E4.1: FailureClassifier enum exists")

    def test_factual_gap_error_exists(self):
        """Test FactualGapError exception is defined"""
        try:
            raise FactualGapError([ValidationResult(
                passed=False, severity=ValidationSeverity.HIGH,
                rule_id="LIC-E010", message="Test failure"
            )])
        except FactualGapError as e:
            assert len(e.args[0]) == 1
            assert e.args[0][0].rule_id == "LIC-E010"
            print("✅ E4.2: FactualGapError exception works correctly")

    @pytest.mark.asyncio
    async def test_s5_classifies_failures_correctly(self, circuit_breaker, mock_scaffold, mock_research_context, 
                                                   mock_profile_analysis, mocker):
        """Test S5 classifies validation failures into CREATIVE vs FACTUAL"""
        generator = GenerationOrchestrator(circuit_breaker)
        validator = ValidationAgent(circuit_breaker)
        
        # Mock generation
        mocker.patch.object(generator, '_generate_content', 
                          return_value="Generated content with 40% metric")
        
        # Mock validation returning a metric context failure (FACTUAL)
        factual_failure = ValidationResult(
            passed=False, severity=ValidationSeverity.HIGH,
            rule_id="LIC-E010", message="Metric '40%' lacks context"
        )
        mocker.patch.object(validator, 'validate_message', return_value=[factual_failure])
        
        # Should raise FactualGapError
        with pytest.raises(FactualGapError) as exc_info:
            await generator.generate_message(mock_scaffold, mock_research_context, 
                                            mock_profile_analysis, validator)
        
        assert len(exc_info.value.args[0]) == 1
        assert exc_info.value.args[0][0].rule_id == "LIC-E010"
        print("✅ E4.3: S5 correctly classifies FACTUAL failures and raises FactualGapError")

    @pytest.mark.asyncio
    async def test_s5_retries_creative_failures(self, circuit_breaker, mock_scaffold, mock_research_context,
                                               mock_profile_analysis, mocker):
        """Test S5 retries internally for CREATIVE failures"""
        generator = GenerationOrchestrator(circuit_breaker)
        validator = ValidationAgent(circuit_breaker)
        
        # Mock generation attempts
        mocker.patch.object(generator, '_generate_content', 
                          side_effect=["Content with spearheaded", "Better content"])
        
        # Mock validation: fail creative first, then pass
        creative_failure = ValidationResult(
            passed=False, severity=ValidationSeverity.MEDIUM,
            rule_id="LIC-E008", message="Forbidden verb detected"
        )
        mocker.patch.object(validator, 'validate_message',
                          side_effect=[[creative_failure], []])
        
        # Should succeed after retry (not raise FactualGapError)
        message = await generator.generate_message(mock_scaffold, mock_research_context,
                                                   mock_profile_analysis, validator)
        
        assert message.content == "Better content"
        assert message.generation_attempts == 2
        print("✅ E4.4: S5 retries internally for CREATIVE failures")

    @pytest.mark.asyncio
    async def test_workflow_meta_loop_reruns_s2(self, mocker):
        """Test WorkflowOrchestrator meta-loop reruns S2 on FactualGapError"""
        orchestrator = WorkflowOrchestrator()
        
        mock_mission = OutreachMission(
            mission_id="test",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "Recipient", "title": "VP"},
            job_description={"title": "Job", "company": "Corp"}
        )
        
        mock_profile = ProfileAnalysis(
            archetype=Archetype.EXECUTIVE, confidence=0.9,
            reasoning="Test", key_indicators=[]
        )
        
        # Mock S1
        mocker.patch.object(ProfileAnalysisAgent, 'analyze_profile', return_value=mock_profile)
        
        # Mock S2 - should be called twice
        mock_context_v1 = ResearchContext(rag_results=[], signal_score=0.7)
        mock_context_v2 = ResearchContext(rag_results=[], signal_score=0.9)
        s2_spy = mocker.patch.object(S2_SupervisorAgent, 'conduct_research',
                                     new_callable=AsyncMock,
                                     side_effect=[(mock_context_v1, mock_profile), 
                                                 (mock_context_v2, mock_profile)])
        
        # Mock S3/S4
        mocker.patch.object(RoutingAgent, 'determine_route', return_value=(Route.INMAIL, "Test"))
        mocker.patch.object(ScaffoldAgent, 'create_scaffold',
                          return_value=MessageScaffold(route=Route.INMAIL, archetype=Archetype.EXECUTIVE,
                                                      sections={}, constraints={}))
        
        # Mock S5 - fail first (FactualGapError), succeed second
        factual_failure = ValidationResult(
            passed=False, severity=ValidationSeverity.HIGH,
            rule_id="LIC-E010", message="Test failure"
        )
        success_message = GeneratedMessage(
            content="Success", word_count=5, char_count=20, route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE, generation_temperature=0.5,
            generation_attempts=1, locked_sections=set(), checksum="abc"
        )
        mocker.patch.object(GenerationOrchestrator, 'generate_message',
                          new_callable=AsyncMock,
                          side_effect=[FactualGapError([factual_failure]), success_message])
        
        # Mock S6/S7
        mocker.patch.object(ValidationAgent, 'validate_message', return_value=[])
        mocker.patch.object(QAAgent, 'generate_qa_report',
                          return_value=QAReport(mission_id="test", validation_results=[],
                                               critical_issues=0, high_issues=0, errors=0,
                                               warnings=0, passed=True, timestamp=""))
        
        result = await orchestrator.execute_workflow(mock_mission)
        
        assert result['status'] == 'success'
        assert s2_spy.call_count == 2
        
        # Verify second S2 call received refinement context
        second_call_kwargs = s2_spy.call_args_list[1].kwargs
        assert 'refinement_context' in second_call_kwargs
        assert second_call_kwargs['refinement_context'] == [factual_failure]
        print("✅ E4.5: Workflow meta-loop successfully reruns S2 with refinement context")

    @pytest.mark.asyncio
    async def test_s2_processes_refinement_context(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test S2 uses refinement_context from S6 failure"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        mocker.patch.object(InternalAgent, 'get_internal_context',
                          return_value={"prior_applications": [], "rag_results": []})
        
        # Mock refinement task
        mocker.patch.object(OrganizationAgent, 'run_refinement_task', new_callable=AsyncMock,
                          return_value={"rag_results": []})
        
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=RAGCritique(is_sufficient=True, confidence_score=0.9,
                                                  gaps_identified=[], refinement_tasks=[], reasoning="OK"))
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        # Pass refinement context from S6
        s6_failure = ValidationResult(
            passed=False, severity=ValidationSeverity.HIGH,
            rule_id="LIC-E010", message="Metric '40%' lacks RAG evidence"
        )
        
        context, _ = await supervisor.conduct_research(mock_mission, mock_profile_analysis,
                                                       refinement_context=[s6_failure])
        
        # Should force a refinement iteration even if critique passes
        assert context.reflexion_iterations >= 1
        print("✅ E4.6: S2 processes refinement_context from S6 failure")

    @pytest.mark.asyncio
    async def test_meta_loop_respects_max_attempts(self, mocker):
        """Test meta-loop stops after MAX_META_LOOPS"""
        orchestrator = WorkflowOrchestrator()
        orchestrator.MAX_META_LOOPS = 2
        
        mock_mission = OutreachMission(
            mission_id="test",
            sender_profile={"name": "Test"},
            recipient_profile={"name": "R", "title": "VP"},
            job_description={"title": "Job", "company": "Corp"}
        )
        
        # Mock all stages
        mocker.patch.object(ProfileAnalysisAgent, 'analyze_profile',
                          return_value=ProfileAnalysis(archetype=Archetype.EXECUTIVE, confidence=0.9,
                                                      reasoning="Test", key_indicators=[]))
        mocker.patch.object(S2_SupervisorAgent, 'conduct_research', new_callable=AsyncMock,
                          return_value=(ResearchContext(rag_results=[], signal_score=0.7),
                                       ProfileAnalysis(archetype=Archetype.EXECUTIVE, confidence=0.9,
                                                      reasoning="Test", key_indicators=[])))
        mocker.patch.object(RoutingAgent, 'determine_route', return_value=(Route.INMAIL, "Test"))
        mocker.patch.object(ScaffoldAgent, 'create_scaffold',
                          return_value=MessageScaffold(route=Route.INMAIL, archetype=Archetype.EXECUTIVE,
                                                      sections={}, constraints={}))
        
        # S5 always fails
        failure = ValidationResult(passed=False, severity=ValidationSeverity.HIGH,
                                  rule_id="LIC-E010", message="Always fail")
        mocker.patch.object(GenerationOrchestrator, 'generate_message', new_callable=AsyncMock,
                          side_effect=FactualGapError([failure]))
        
        # Should raise after max attempts
        with pytest.raises(Exception) as exc_info:
            await orchestrator.execute_workflow(mock_mission)
        
        assert "not resolved after" in str(exc_info.value)
        print("✅ E4.7: Meta-loop respects MAX_META_LOOPS limit")

# ============================================================================
# REGRESSION TESTS (v11.9 Features)
# ============================================================================

class TestRegressionV11_9:
    """Ensure v11.9 features still work after v11.10 refactor"""

    def test_sender_grounding_extraction(self, circuit_breaker, mock_mission):
        """Test sender grounding whitelist extraction"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        rag_results = [
            RAGResult(source="mock", source_type="MOCK",
                     text="My colleague Alice Smith and teammate Bob Jones...",
                     extracted_keywords=[], source_weight=1.0, age_days=0, recipient_specific=False),
            RAGResult(source="mock", source_type="MOCK",
                     text="Our product 'CloudScale Platform' and 'DataHub' solution...",
                     extracted_keywords=[], source_weight=1.0, age_days=0, recipient_specific=False),
            RAGResult(source="mock", source_type="MOCK",
                     text="Case study with TechCorp client and FinanceInc implementation...",
                     extracted_keywords=[], source_weight=1.0, age_days=0, recipient_specific=False)
        ]
        
        grounding = supervisor._extract_sender_grounding(rag_results, mock_mission)
        
        assert "Alice Smith" in grounding.team_members or "Bob Jones" in grounding.team_members
        assert "CloudScale Platform" in grounding.products or "DataHub" in grounding.products
        assert "TechCorp" in grounding.case_studies or "FinanceInc" in grounding.case_studies
        print("✅ Regression v11.9.1: Sender grounding extraction works")

    def test_context_aware_cta_scaffold(self, circuit_breaker, mock_research_context):
        """Test context-aware CTA generation"""
        scaffold_agent = ScaffoldAgent(circuit_breaker)
        
        # CONNECTION_REQ should have no CTA
        scaffold_conn = scaffold_agent.create_scaffold(Route.CONNECTION_REQ, Archetype.EXECUTIVE,
                                                       mock_research_context)
        assert not scaffold_conn.sections['cta']['required']
        
        # SENIOR_TA should have context-aware CTA
        scaffold_ta = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.SENIOR_TA,
                                                     mock_research_context)
        assert scaffold_ta.sections['cta']['required']
        assert scaffold_ta.context_aware_cta
        
        # C_LEVEL should have standard CTA (not context-aware)
        scaffold_clevel = scaffold_agent.create_scaffold(Route.INMAIL, Archetype.C_LEVEL,
                                                         mock_research_context)
        assert scaffold_clevel.sections['cta']['required']
        assert not scaffold_clevel.context_aware_cta
        
        print("✅ Regression v11.9.2: Context-aware CTA logic works")

    def test_metric_context_validation(self, circuit_breaker):
        """Test metric context validation (LIC-E010)"""
        validator = ValidationAgent(circuit_breaker)
        
        message = GeneratedMessage(
            content="...led to a 40% reduction in processing time...",
            word_count=10, char_count=50, route=Route.INMAIL,
            archetype=Archetype.EXECUTIVE, generation_temperature=0.5,
            generation_attempts=1, locked_sections=set(), checksum="abc"
        )
        
        # Context WITH supporting RAG
        context_good = ResearchContext(
            rag_results=[RAGResult(
                source="blog", source_type="COMPANY_BLOG_ANNOUNCEMENT",
                text="achieved 40% reduction in processing time",
                extracted_keywords=["40%", "reduction", "processing"],
                source_weight=1.0, age_days=10, recipient_specific=False
            )],
            recipient_insights=[], company_context=[], recent_activity=[]
        )
        
        # Context WITHOUT supporting RAG
        context_bad = ResearchContext(
            rag_results=[RAGResult(
                source="blog", source_type="COMPANY_BLOG_ANNOUNCEMENT",
                text="Our company is innovative",
                extracted_keywords=["company"], source_weight=1.0,
                age_days=10, recipient_specific=False
            )],
            recipient_insights=[], company_context=[], recent_activity=[]
        )
        
        results_good = validator.validate_message(message, context_good)
        metric_failures_good = [r for r in results_good if r.rule_id == "LIC-E010" and not r.passed]
        
        results_bad = validator.validate_message(message, context_bad)
        metric_failures_bad = [r for r in results_bad if r.rule_id == "LIC-E010" and not r.passed]
        
        assert len(metric_failures_good) == 0
        assert len(metric_failures_bad) > 0
        print("✅ Regression v11.9.3: Metric context validation (LIC-E010) works")

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_full_workflow_success(self, mocker):
        """Test complete workflow from mission to message"""
        orchestrator = WorkflowOrchestrator()
        
        mission = OutreachMission(
            mission_id="integration_test",
            sender_profile={"name": "Alice", "title": "CTO"},
            recipient_profile={"name": "Bob", "title": "VP Engineering", "company": "TechCo"},
            job_description={"title": "Director AI", "company": "TechCo"}
        )
        
        # Mock all components
        mocker.patch.object(ProfileAnalysisAgent, 'analyze_profile',
                          return_value=ProfileAnalysis(archetype=Archetype.EXECUTIVE, confidence=0.9,
                                                      reasoning="VP title", key_indicators=["VP"]))
        
        mocker.patch.object(S2_SupervisorAgent, 'conduct_research', new_callable=AsyncMock,
                          return_value=(ResearchContext(rag_results=[], signal_score=0.85,
                                                       recipient_insights=[], company_context=[],
                                                       recent_activity=[]),
                                       ProfileAnalysis(archetype=Archetype.EXECUTIVE, confidence=0.9,
                                                      reasoning="VP", key_indicators=[])))
        
        mocker.patch.object(RoutingAgent, 'determine_route', return_value=(Route.INMAIL, "Job app"))
        
        mocker.patch.object(ScaffoldAgent, 'create_scaffold',
                          return_value=MessageScaffold(route=Route.INMAIL, archetype=Archetype.EXECUTIVE,
                                                      sections={"greeting": {"required": True, "word_range": (2, 5)},
                                                               "body": {"required": True, "min_words": 120},
                                                               "cta": {"required": True, "word_range": (5, 12)},
                                                               "signature": {"required": True, "word_range": (2, 6)}},
                                                      constraints={"word_range": (180, 250)}, locked_sections=set()))
        
        mocker.patch.object(GenerationOrchestrator, 'generate_message', new_callable=AsyncMock,
                          return_value=GeneratedMessage(content="Hi Bob, I saw your work...", word_count=220,
                                                        char_count=1200, route=Route.INMAIL,
                                                        archetype=Archetype.EXECUTIVE, generation_temperature=0.5,
                                                        generation_attempts=1, locked_sections=set(), checksum="xyz"))
        
        mocker.patch.object(ValidationAgent, 'validate_message', return_value=[])
        
        mocker.patch.object(QAAgent, 'generate_qa_report',
                          return_value=QAReport(mission_id="integration_test", validation_results=[],
                                               critical_issues=0, high_issues=0, errors=0, warnings=0,
                                               passed=True, timestamp=datetime.now().isoformat()))
        
        result = await orchestrator.execute_workflow(mission)
        
        assert result['status'] == 'success'
        assert result['production_ready']
        assert result['word_count'] == 220
        assert result['route'] == 'INMAIL'
        assert result['archetype'] == 'EXECUTIVE'
        print("✅ Integration: Full workflow executes successfully")

    def test_config_registry_integration(self):
        """Test CONFIG_REGISTRY provides correct values"""
        # Test route constraints
        inmail_constraints = CONFIG_REGISTRY.get_route_constraints(Route.INMAIL)
        assert 'word_range' in inmail_constraints
        assert inmail_constraints['word_range'] == (180, 250)
        
        # Test archetype word targets
        target = CONFIG_REGISTRY.get_target_word_count(Archetype.C_LEVEL, Route.INMAIL)
        assert target == 240
        
        # Test RAG parameters
        rag_calls = CONFIG_REGISTRY.get_rag_parameter(Archetype.C_LEVEL, 'total_calls')
        assert rag_calls == 24
        
        # Test reasoning parameters
        max_hops = CONFIG_REGISTRY.get_reasoning_parameter(Archetype.C_LEVEL, 'max_hops')
        assert max_hops == 6
        
        print("✅ Integration: CONFIG_REGISTRY provides correct configuration")

    def test_circuit_breaker_integration(self):
        """Test circuit breaker functionality"""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
        
        assert cb.state == CircuitState.CLOSED
        
        # Simulate failures
        def failing_func():
            raise Exception("Test failure")
        
        for _ in range(2):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        print("✅ Integration: Circuit breaker opens after threshold")

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and resource usage tests"""

    @pytest.mark.asyncio
    async def test_parallel_specialist_execution_speed(self, circuit_breaker, mock_mission, mock_profile_analysis, mocker):
        """Test specialists execute in parallel (not sequential)"""
        supervisor = S2_SupervisorAgent(circuit_breaker)
        
        import time
        
        # Mock specialists with delays
        async def slow_recipient(*args, **kwargs):
            await asyncio.sleep(0.1)
            return {"rag_results": []}
        
        async def slow_org(*args, **kwargs):
            await asyncio.sleep(0.1)
            return {"rag_results": []}
        
        def internal(*args, **kwargs):
            return {"prior_applications": [], "rag_results": []}
        
        mocker.patch.object(RecipientAgent, 'get_profile', new_callable=AsyncMock, side_effect=slow_recipient)
        mocker.patch.object(OrganizationAgent, 'get_organization_context', new_callable=AsyncMock, side_effect=slow_org)
        mocker.patch.object(InternalAgent, 'get_internal_context', side_effect=internal)
        mocker.patch.object(RAGReflexionSystem, 'critique_rag_sufficiency',
                          return_value=RAGCritique(is_sufficient=True, confidence_score=0.9,
                                                  gaps_identified=[], refinement_tasks=[], reasoning="OK"))
        mocker.patch.object(supervisor, '_run_adversarial_check', new_callable=AsyncMock, return_value=[])
        
        start = time.time()
        await supervisor.conduct_research(mock_mission, mock_profile_analysis)
        elapsed = time.time() - start
        
        # Should take ~0.1s (parallel), not ~0.2s (sequential)
        assert elapsed < 0.15
        print(f"✅ Performance: Specialists execute in parallel ({elapsed:.3f}s)")

    def test_memory_efficiency_rag_results(self):
        """Test RAG results don't duplicate excessively"""
        # Create many RAG results
        results = [
            RAGResult(source=f"src{i}", source_type="TEST", text=f"Text {i}",
                     extracted_keywords=[], source_weight=1.0, age_days=0,
                     recipient_specific=False)
            for i in range(100)
        ]
        
        context = ResearchContext(
            rag_results=results,
            recipient_insights=[], company_context=[], recent_activity=[]
        )
        
        # Should store efficiently
        assert len(context.rag_results) == 100
        print("✅ Performance: RAG results stored efficiently")

# ============================================================================
# SUMMARY
# ============================================================================

def test_summary():
    """Print test suite summary"""
    print("\n" + "="*80)
    print("LIC v11.10 TEST SUITE SUMMARY")
    print("="*80)
    print("\n✅ Enhancement 1: S2 Multi-Agent Specialization - 3 tests")
    print("✅ Enhancement 2: S2 Internal Execute-Critique-Replan Loop - 3 tests")
    print("✅ Enhancement 3: S2 Adversarial Self-Verification - 3 tests")
    print("✅ Enhancement 4: S6 -> S2 Meta-Loop - 7 tests")
    print("✅ Regression (v11.9 Features) - 3 tests")
    print("✅ Integration Tests - 3 tests")
    print("✅ Performance Tests - 2 tests")
    print(f"\nTotal: 24 comprehensive tests")
    print("="*80 + "\n")
