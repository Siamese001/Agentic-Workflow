"""
Pytest Advanced Test Suite for Modular Resume Workflow (v16.22+)

This suite provides "expansive" testing by focusing on:
1.  Parameterization: Testing multiple inputs for a single rule.
2.  Deeper Integration: Testing the internal logic of complex components
    like ArtistGenerator and the RAG (EnhancedJobDescriptionAnalyzer) pipeline.
3.  Negative E2E Scenarios: Ensuring the workflow halts correctly on bad data.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, Mock, call

# --- Import All Modules Under Test ---
from models import (
    ImmutableStagingBuffer,
    ResumeSection,
    GateDecision,
    ValidationSeverity,
    ValidationResult,
    BulletProvenance,
    ThematicAnalysis,
    CompetitiveIntelligence,
    HopStatus,
    RAGMission,
    HopExecutionError
)

from config import (
    AppConfig,
    ArtistConfig,
    ValidatorConfig,
    ContentConstraintsConfig,
    SignalControlConfig,
    RAGConfig,
    EnricherConfig
)

from workflow import (
    WorkflowOrchestrator,
    ArtistGenerator,
    ConstraintFailureClassifier
)

from validation import (
    PreFlightValidator,
    ValidationContext
)

from rag import (
    EnhancedJobDescriptionAnalyzer,
    GeminiWebSearchClient
)


# ============================================================================
#
# ADVANCED FIXTURES
#
# ============================================================================

@pytest.fixture(scope="module")
def mock_app_config() -> AppConfig:
    """Returns a real, fully-formed AppConfig object for testing."""
    return AppConfig(
        artist=ArtistConfig(
            bullet_word_count_ranges={
                'K2_UNIFY_BULLETS': (28, 38),
                'K3_IBM_BULLETS': (22, 34),
                'K9_COMPETENCIES': (28, 38),
            },
            provenance_split_targets={
                'K2_UNIFY_BULLETS': {'Verbatim': 1, 'Customized': 1, 'Synthetic': 1},
            }
        ),
        validator=ValidatorConfig(
            bullet_word_count_sections_to_check={'K2_UNIFY_BULLETS'},
            forbidden_verbs=["spearheaded", "leveraged"]
        ),
        content_constraints=ContentConstraintsConfig(
            TOTAL_WORD_COUNT_MIN=100,
            TOTAL_WORD_COUNT_MAX=2000,
            HEADLINE_COMPONENT_WORDS_MIN=2,
            HEADLINE_COMPONENT_WORDS_MAX=4
        ),
        signal_constraints=SignalControlConfig(),
        rag=RAGConfig(circuit_breaker_threshold=3),
        enricher=EnricherConfig()
    )

@pytest.fixture(scope="module")
def mock_master_resume() -> dict:
    """Provides a minimal, valid master_resume.json structure."""
    return {
        "owner": {
            "name": "Test User",
            "contact": { "phone": "555-1234", "email": "test@user.com", "linkedin": "linkedin.com/test" }
        },
        "professional_experience": [
            { "company": "Unify", "title": "Test Title", "bullet_pool": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4"] },
        ],
        "education": [],
        "certifications_and_credentials": [],
        "strategic_and_technical_competencies": []
    }

@pytest.fixture
def mock_validation_context(mock_master_resume, mock_app_config):
    """A fully-formed ValidationContext for testing specific rules."""
    mock_buffer = MagicMock(spec=ImmutableStagingBuffer)
    mock_ta = MagicMock(spec=ThematicAnalysis)
    return ValidationContext(
        staging_buffer=mock_buffer,
        thematic_analysis=mock_ta,
        job_description="test jd",
        master_resume=mock_master_resume,
        app_config=mock_app_config
    )

@pytest.fixture
def mock_orchestrator(mock_master_resume, mock_app_config):
    """A basic WorkflowOrchestrator in test mode."""
    return WorkflowOrchestrator(
        master_resume=mock_master_resume,
        config=mock_app_config,
        test_mode=True
    )

# ============================================================================
#
# TEST SUITE 01: ADVANCED VALIDATION (PARAMETERIZATION)
#
# ============================================================================

class Test01_AdvancedValidation:

    @pytest.fixture
    def validator(self, mock_master_resume, mock_app_config):
        """Returns a real PreFlightValidator with the correct config."""
        return PreFlightValidator(
            master_resume=mock_master_resume,
            app_config=mock_app_config
        )

    @pytest.mark.parametrize("headline, should_pass", [
        ("Good Title | Good Skill | Good Value", True),
        ("Manager of AI | Good Skill | Good Value", False), # Fails: Forbidden title
        ("Good Title | VP of Cloud | Good Value", False),   # Fails: Forbidden title
        ("Good Title | Good Skill | Senior Engineer", False), # Fails: Forbidden title
        ("Good Title, Bad Comma | Good Skill", False),    # Fails: Comma
        ("OneComponent", False),                           # Fails: Component count
        ("Too | Many | Components | For This", False),     # Fails: Component count
    ])
    def test_validate_headline_rules_parameterized(self, headline, should_pass, validator, mock_validation_context):
        # Set up the context with the parameterized headline
        mock_validation_context.staging_buffer.get.return_value = headline
        
        # Test the "no titles" rule
        is_valid_titles = validator._validate_headline_format_no_titles(mock_validation_context)
        
        # Test the "no commas" rule
        is_valid_commas = (',' not in mock_validation_context.headline_details.get('headline', ''))
        
        # Test component count (part of _validate_headline_format_component_wc)
        components = headline.split('|')
        is_valid_component_count = (len(components) == 3)

        assert (is_valid_titles and is_valid_commas and is_valid_component_count) == should_pass

    @pytest.mark.parametrize("text, should_pass, expected_snippet", [
        ("This is valid text.", True, None),
        ("This contains [Placeholder text]", False, "[Placeholder text]"),
        ("This has [MISSING_CONTEXT]", False, "[MISSING_CONTEXT]"),
        # NOTE: This test will FAIL until you update the regex in _validate_no_placeholders
        # to include "[Your Name]". This proves the test is finding new bugs!
        ("Please enter [Your Name] here", False, "[Your Name]"), 
    ])
    def test_validate_no_placeholders_parameterized(self, text, should_pass, expected_snippet, validator, mock_validation_context):
        # We need to mock .data to simulate a full buffer scan
        mock_validation_context.staging_buffer.data = {
            ResumeSection.K1_EXECUTIVE_SUMMARY.value: text
        }
        
        is_valid = validator._validate_no_placeholders(mock_validation_context)
        
        assert is_valid == should_pass
        if not should_pass:
            details = mock_validation_context.get_details_for_rule("H5_CONTENT_NO_PLACEHOLDERS")
            assert expected_snippet in details['placeholders']

    @pytest.mark.parametrize("text, should_pass, expected_verb", [
        ("I led a team of engineers", True, None),
        ("I spearheaded a new initiative", False, "spearheaded"),
        ("We leveraged cloud technology", False, "leveraged"),
    ])
    def test_validate_no_forbidden_verbs(self, text, should_pass, expected_verb, validator, mock_validation_context):
        mock_validation_context.staging_buffer.get.return_value = text # Mock K1
        
        is_valid = validator._validate_forbidden_verbs(mock_validation_context)
        
        assert is_valid == should_pass
        if not should_pass:
            details = mock_validation_context.get_details_for_rule("H3_CONTENT_NO_FORBIDDEN_VERBS")
            assert expected_verb in details['violations']


# ============================================================================
#
# TEST SUITE 02: DEEPER ARTIST LOGIC (INTEGRATION)
#
# ============================================================================

class Test02_ArtistGeneratorLogic:

    @pytest.fixture
    def artist(self, mock_master_resume, mock_app_config, sample_thematic_analysis):
        """Provides a real ArtistGenerator instance."""
        # We must load the real artist_specs.json for this to work
        try:
            specs = json.load(open("artist_specs.json"))
        except FileNotFoundError:
            pytest.skip("artist_specs.json not found, skipping deep artist test")
            
        return ArtistGenerator(
            master_resume=mock_master_resume,
            enriched_scaffold={},
            job_description="test jd",
            thematic_analysis=sample_thematic_analysis,
            artist_specs=specs,
            artist_config=mock_app_config.artist,
            content_constraints=mock_app_config.content_constraints
        )

    @patch('workflow.ArtistGenerator._call_gemini_api')
    def test_artist_generate_tailored_bullets_full_logic(self, mock_api_call, artist, mock_app_config):
        """
        Tests the entire _generate_tailored_bullets_for_experience logic,
        including selection, customization, synthesis, and reordering.
        This is a deep integration test of ArtistGenerator.
        """
        # --- Setup Mocks ---
        # We need to mock the API call 4 times with different return values
        mock_api_call.side_effect = [
            # 1. Verbatim Selection Call (Targets 1)
            ("Bullet 1", 1),
            
            # 2. Customization Call (Targets 1)
            ("• Customized Bullet 2", 1),
            
            # 3. Synthetic Call (Targets 1)
            ("* Synthetic Bullet 1", 1),
            
            # 4. Reordering Call
            ("Synthetic Bullet 1\nCustomized Bullet 2\nBullet 1", 1) 
        ]
        
        # --- Run the Method ---
        # We test K2_UNIFY_BULLETS, which has targets {'Verbatim': 1, 'Customized': 1, 'Synthetic': 1}
        section_enum = ResumeSection.K2_UNIFY_BULLETS
        final_bullets, total_calls = artist._generate_tailored_bullets_for_experience(
            company_name="Unify",
            provenance_targets=mock_app_config.artist.provenance_split_targets[section_enum.name],
            reasoning_config=ReasoningConfig.DEFAULT,
            section_enum=section_enum,
            temperature_override=1.0
        )
        
        # --- Assertions ---
        assert total_calls == 4
        assert len(final_bullets) == 3
        
        # Check that the final list is in the *reordered* order
        assert final_bullets[0]['text'] == "Synthetic Bullet 1"
        assert final_bullets[1]['text'] == "Customized Bullet 2"
        assert final_bullets[2]['text'] == "Bullet 1"
        
        # Check that provenances are correct
        assert final_bullets[0]['provenance'] == BulletProvenance.Synthetic.value
        assert final_bullets[1]['provenance'] == BulletProvenance.Customized.value
        assert final_bullets[2]['provenance'] == BulletProvenance.Verbatim.value


# ============================================================================
#
# TEST SUITE 03: DEEPER RAG LOGIC (INTEGRATION)
#
# ============================================================================

class Test03_RAG_PipelineLogic:

    @pytest.fixture
    def rag_analyzer(self, mock_master_resume, mock_app_config):
        """Provides a real EnhancedJobDescriptionAnalyzer with a mocked client."""
        
        # We patch the client *inside* the analyzer instance
        with patch('rag.GeminiWebSearchClient', spec=GeminiWebSearchClient) as MockClient:
            mock_client_instance = MockClient.return_value
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=mock_master_resume,
                app_config=mock_app_config
            )
            # Attach the mock client instance so we can control it
            analyzer.mock_client_instance = mock_client_instance
            return analyzer

    def test_rag_pipeline_full_success(self, rag_analyzer, sample_job_description):
        """
        Tests the 4-phase RAG pipeline's synthesis logic.
        """
        # --- Setup Mocks ---
        # Mock the RAG Mission (Hop -0.5)
        rag_analyzer.rag_mission = RAGMission(
            target_company_name="TestCo",
            precise_role_title="Test Role",
            key_technologies=["Python", "AWS"],
            core_responsibilities=["Develop", "Deploy"],
            signal_gap_keywords=[],
            signal_overlap_keywords=["Python", "AWS"]
        )
        
        # Mock the client's return values for each of the 4 phases
        mock_phase1_result = {"search_summary": {}, "thematic_analysis": {"primary_theme": {"name": "Phase 1 Theme"}}}
        mock_phase2_result = {"search_summary": {}, "authenticity_patterns": {"patterns": {"achievement_verb_patterns": ["Led"]}}}
        mock_phase3_result = {"search_summary": {}, "competitive_analysis": {"differentiator_keywords": [{"keyword": "Phase 3 Diff"}]}}
        mock_phase4_result = {"search_summary": {}, "problem_solution_narratives": {"common_problems": ["Phase 4 Problem"]}}
        
        # We mock the *executor's* return values
        rag_analyzer.web_rag.executor.execute_with_retry.side_effect = [
            (mock_phase1_result, 1), # Phase 1
            (mock_phase2_result, 1), # Phase 2
            (mock_phase3_result, 1), # Phase 3
            (mock_phase4_result, 1)  # Phase 4
        ]
        
        # --- Run the Method ---
        final_analysis, total_calls = rag_analyzer._analyze_with_resilient_web_search(sample_job_description)

        # --- Assertions ---
        assert total_calls == 4
        assert isinstance(final_analysis, ThematicAnalysis)
        
        # Check that data from all 4 phases was synthesized correctly
        assert final_analysis.primary_theme['name'] == "Phase 1 Theme"
        assert final_analysis.authenticity_patterns['patterns']['achievement_verb_patterns'] == ["Led"]
        assert "Phase 3 Diff" in [d['keyword'] for d in final_analysis.competitive_intelligence.differentiator_keywords_weighted]
        assert final_analysis.problem_solution_narratives['common_problems'] == ["Phase 4 Problem"]
        assert final_analysis.signal_quality_score > 0

    def test_rag_pipeline_partial_failure_halts(self, rag_analyzer, sample_job_description):
        """
        Tests that the RAG pipeline correctly halts if any phase fails.
        """
        # --- Setup Mocks ---
        rag_analyzer.rag_mission = RAGMission("TestCo", "Test Role", [], [], [], [])
        
        mock_phase1_result = {"search_summary": {}, "thematic_analysis": {"primary_theme": {"name": "Phase 1 Theme"}}}
        
        # Mock the executor to PASS Phase 1, but FAIL Phase 2
        rag_analyzer.web_rag.executor.execute_with_retry.side_effect = [
            (mock_phase1_result, 1), # Phase 1
            HopExecutionError("Phase 2 Failed!") # Phase 2
        ]
        
        # --- Run and Assert ---
        # The entire function should fail if any phase fails
        with pytest.raises(HopExecutionError, match="All RAG phases failed"):
            rag_analyzer._analyze_with_resilient_web_search(sample_job_description)

# ============================================================================
#
# TEST SUITE 04: E2E NEGATIVE SCENARIOS
#
# ============================================================================

class Test04_E2E_NegativeScenarios:

    @patch('rag.EnhancedJobDescriptionAnalyzer.analyze')
    def test_e2e_workflow_halts_on_rag_failure(self, mock_rag_analyze, mock_orchestrator, sample_job_description):
        """Tests that the entire workflow halts if Hop 0 (RAG) fails."""
        
        # --- Setup Mock ---
        # Mock Hop 0 to raise a critical exception
        mock_rag_analyze.side_effect = HopExecutionError("Simulated RAG API Failure")
        
        # --- Run and Assert ---
        result = mock_orchestrator.execute_workflow(
            job_description=sample_job_description,
            company_name="TestCo",
            job_title="TestRole",
            jd_url=""
        )
        
        assert result['status'] == 'HALTED'
        assert result['gate_decision'] == 'HALT'
        assert "Simulated RAG API Failure" in result['reason']
        assert result['hop_checkpoints'][0]['status'] == 'FAIL' # Hop 0 checkpoint
        assert len(result['hop_checkpoints']) == 1 # Workflow halted

    @patch('rag.EnhancedJobDescriptionAnalyzer.analyze')
    @patch('workflow.ArtistGenerator.generate')
    def test_e2e_workflow_halts_on_artist_failure(self, mock_artist_generate, mock_rag_analyze,
                                                    mock_orchestrator, sample_thematic_analysis,
                                                    sample_job_description):
        """Tests that the entire workflow halts if Hop 3 (Artist) fails."""

        # --- Setup Mocks ---
        # Mock Hop 0 (RAG) to succeed
        mock_rag_analyze.return_value = (sample_thematic_analysis, 1)
        # Mock Hop 3 (Artist) to raise a critical exception
        mock_artist_generate.side_effect = HopExecutionError("Simulated Artist Failure")
        
        # --- Run and Assert ---
        result = mock_orchestrator.execute_workflow(
            job_description=sample_job_description,
            company_name="TestCo",
            job_title="TestRole",
            jd_url=""
        )
        
        assert result['status'] == 'HALTED'
        assert result['gate_decision'] == 'HALT'
        assert "Simulated Artist Failure" in result['reason']
        assert result['hop_checkpoints'][2].status == 'PASS' # Hop 2 (Enrichment)
        assert result['hop_checkpoints'][3].status == 'FAIL' # Hop 3 (Artist)
        assert len(result['hop_checkpoints']) == 4 # Halted at Hop 3

    @patch('rag.EnhancedJobDescriptionAnalyzer.analyze')
    @patch('workflow.ArtistGenerator._call_gemini_api')
    def test_e2e_workflow_halts_on_validation_gate(self, mock_artist_api_call, mock_rag_analyze,
                                                     mock_orchestrator, sample_thematic_analysis,
                                                     sample_job_description):
        """
        Tests that the workflow completes generation but is HALTED at Hop 6
        due to a validation failure. This is the most important negative test.
        """
        # --- Setup Mocks ---
        # Mock Hop 0 (RAG) to succeed
        mock_rag_analyze.return_value = (sample_thematic_analysis, 1)
        
        # Mock Hop 3 (Artist) to return BAD data
        mock_artist_api_call.side_effect = (
            # Return a headline that will FAIL validation
            ("This headline is a Manager", 1), # <-- BAD DATA
            ("Valid summary " * 20, 1),
            ([{"text": "Valid bullet", "wc": 30}], 1), # K2 Bullets
            ("Valid overview", 1), # K2 Overview
            ([{"text": "Valid bullet", "wc": 30}], 1), # K3 Bullets
            ("Valid overview", 1), # K3 Overview
            ("Valid narrative", 1), # K4
            ("Valid narrative", 1), # K5
            ("Valid narrative", 1), # K6
            ([{"text": "Valid competency", "wc": 30}], 1), # K9
            ("* Skill 1\n* Skill 2\n* Skill 3\n* Skill 4\n* Skill 5\n* Skill 6\n* Skill 7\n* Skill 8\n* Skill 9\n* Skill 10\n* Skill 11\n* Skill 12", 1), # K10
            ("October 31, 2025\n\nHiring Manager\n[Company Name]\n\nDear Hiring Manager,\n\nPara 1\n\nPara 2\n\nPara 3\n\nSincerely,\n\nTest User  \ntest@user.com  \n555-1234  \nlinkedin.com/test", 1) # K11
        )
        
        # --- Run and Assert ---
        result = mock_orchestrator.execute_workflow(
            job_description=sample_job_description,
            company_name="TestCo",
            job_title="TestRole",
            jd_url=""
        )
        
        # The workflow should HALT, but *after* Hop 6
        assert result['status'] == 'HALTED'
        assert result['gate_decision'] == 'HALT'
        
        # Check the *reason* for the halt
        assert "HALT decision at HOP-6" in result['reason']
        assert "K.0 Headline contains forbidden titles" in result['reason']
        
        # Check the checkpoints
        assert result['hop_checkpoints'][0].status == HopStatus.PASS # Hop 0
        assert result['hop_checkpoints'][3].status == HopStatus.PASS # Hop 3 (Generation passed)
        assert result['hop_checkpoints'][5].status == HopStatus.FAIL # Hop 5 (Validation failed)
        assert result['hop_checkpoints'][6].status == HopStatus.FAIL # Hop 6 (Gate)
        assert len(result['hop_checkpoints']) == 7 # Halted at Hop 6