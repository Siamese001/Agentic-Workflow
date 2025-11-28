"""
Pytest Test Suite for Resume Workflow Engine v16.30 (Resumable Architecture)

This suite tests:
1. State serialization/deserialization (StateSerializer)
2. Manifest management (ManifestManager)
3. Resumable workflow execution
4. Cache hit/miss behavior
5. Idempotent hop execution
6. Force rerun functionality
7. Legacy validation and RAG logic (regression)

Updated for modular architecture with:
- models_RES.py
- config_RES.py
- workflow_RES.py
- validation_RES.py
- rag_RES.py
- state_manager_RES.py
- utils_RES.py
"""

import pytest
import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from pathlib import Path

# --- Import All Modules Under Test ---
from models_RES import (
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
    HopExecutionError,
    HopCheckpoint
)

from config_RES import (
    AppConfig,
    ArtistConfig,
    ValidatorConfig,
    ContentConstraintsConfig,
    SignalControlConfig,
    RAGConfig,
    EnricherConfig,
    CONFIG
)

from workflow_RES import (
    WorkflowOrchestrator,
    __version__
)

from validation_RES import (
    PreFlightValidator
)

from rag_RES import (
    EnhancedJobDescriptionAnalyzer
)

from state_manager_RES import (
    StateSerializer,
    ManifestManager
)


# ============================================================================
# FIXTURES
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
            "contact": {
                "phone": "555-1234",
                "email": "test@user.com",
                "linkedin": "linkedin.com/test"
            }
        },
        "professional_experience": [
            {
                "company": "Unify Consulting",
                "title": "Test Title",
                "bullet_pool": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4"]
            },
        ],
        "education": [],
        "certifications_and_credentials": [],
        "strategic_and_technical_competencies": []
    }


@pytest.fixture
def temp_workflow_dir():
    """Creates a temporary directory for workflow outputs."""
    temp_dir = tempfile.mkdtemp(prefix="test_workflow_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_job_input():
    """Sample job input for testing."""
    return {
        "company_name": "TestCorp",
        "job_title": "Senior AI Engineer",
        "job_description": "We are looking for a Senior AI Engineer with strong Python skills and experience in machine learning.",
        "jd_url": "https://example.com/job/123"
    }


@pytest.fixture
def sample_thematic_analysis():
    """Sample ThematicAnalysis for testing."""
    return ThematicAnalysis(
        primary_theme={"name": "AI Engineering", "confidence": 0.9},
        secondary_themes=[{"name": "Python Development", "confidence": 0.8}],
        role_classification={"level": "senior", "type": "technical"},
        positioning_directives={},
        authenticity_patterns={},
        competitive_intelligence=CompetitiveIntelligence(),
        problem_solution_narratives=None,
        signal_quality_score=0.85,
        retrieval_method="WEB_SEARCH",
        retrieval_sources=[],
        weighting_formula=None,
        evidence_log=[]
    )


# ============================================================================
# TEST SUITE 01: STATE SERIALIZATION (StateSerializer)
# ============================================================================

class TestStateSerializer:
    """Tests for StateSerializer class."""
    
    def test_initialization(self, temp_workflow_dir):
        """Test StateSerializer initialization."""
        run_id = "test_run_001"
        run_path = os.path.join(temp_workflow_dir, run_id)
        os.makedirs(run_path, exist_ok=True)
        
        serializer = StateSerializer(run_path, run_id)
        
        assert serializer.run_path == run_path
        assert serializer.run_id == run_id
        assert len(serializer.HOP_CONFIG) == 8  # 8 hops with file outputs
    
    def test_get_path_for_hop(self, temp_workflow_dir):
        """Test path generation for hops."""
        run_id = "test_run_002"
        run_path = os.path.join(temp_workflow_dir, run_id)
        os.makedirs(run_path, exist_ok=True)
        
        serializer = StateSerializer(run_path, run_id)
        
        # Test valid hop
        path_0 = serializer.get_path_for_hop(0)
        assert path_0.endswith("_HOP-0_ThematicAnalysis.json")
        assert run_id in path_0
        
        # Test invalid hop
        with pytest.raises(ValueError, match="No file path config found"):
            serializer.get_path_for_hop(99)
    
    def test_save_and_load_thematic_analysis(self, temp_workflow_dir, sample_thematic_analysis):
        """Test saving and loading ThematicAnalysis."""
        run_id = "test_run_003"
        run_path = os.path.join(temp_workflow_dir, run_id)
        os.makedirs(run_path, exist_ok=True)
        
        serializer = StateSerializer(run_path, run_id)
        
        # Save
        serializer.save(0, sample_thematic_analysis)
        
        # Verify file exists
        assert serializer.exists(0)
        
        # Load
        loaded_ta = serializer.load(0)
        
        # Verify data integrity
        assert isinstance(loaded_ta, ThematicAnalysis)
        assert loaded_ta.primary_theme["name"] == "AI Engineering"
        assert loaded_ta.signal_quality_score == 0.85
        assert loaded_ta.retrieval_method == "WEB_SEARCH"
    
    def test_save_and_load_validation_results(self, temp_workflow_dir):
        """Test saving and loading ValidationResult list."""
        run_id = "test_run_004"
        run_path = os.path.join(temp_workflow_dir, run_id)
        os.makedirs(run_path, exist_ok=True)
        
        serializer = StateSerializer(run_path, run_id)
        
        # Create sample validation results
        vr_list = [
            ValidationResult(
                rule_id="TEST_RULE_1",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Test passed"
            ),
            ValidationResult(
                rule_id="TEST_RULE_2",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Test failed"
            )
        ]
        
        # Save
        serializer.save(5, vr_list)
        
        # Verify file exists
        assert serializer.exists(5)
        
        # Load
        loaded_vr_list = serializer.load(5)
        
        # Verify data integrity
        assert isinstance(loaded_vr_list, list)
        assert len(loaded_vr_list) == 2
        assert loaded_vr_list[0].rule_id == "TEST_RULE_1"
        assert loaded_vr_list[0].severity == ValidationSeverity.INFO
        assert loaded_vr_list[1].passed == False
    
    def test_delete_hop_file(self, temp_workflow_dir):
        """Test deleting hop files."""
        run_id = "test_run_005"
        run_path = os.path.join(temp_workflow_dir, run_id)
        os.makedirs(run_path, exist_ok=True)
        
        serializer = StateSerializer(run_path, run_id)
        
        # Save a file
        serializer.save(1, {"test": "data"})
        assert serializer.exists(1)
        
        # Delete it
        result = serializer.delete_hop_file(1)
        assert result == True
        assert not serializer.exists(1)
        
        # Try deleting again (should return False)
        result = serializer.delete_hop_file(1)
        assert result == False


# ============================================================================
# TEST SUITE 02: MANIFEST MANAGEMENT (ManifestManager)
# ============================================================================

class TestManifestManager:
    """Tests for ManifestManager class."""
    
    def test_create_and_load_manifest(self, temp_workflow_dir, sample_job_input):
        """Test creating and loading a manifest."""
        run_path = os.path.join(temp_workflow_dir, "test_run_006")
        os.makedirs(run_path, exist_ok=True)
        
        manager = ManifestManager(run_path)
        
        # Create manifest
        run_id = "test_run_006"
        manifest = manager.create_manifest(
            run_id=run_id,
            engine_version="16.30",
            job_input=sample_job_input,
            master_resume_hash="abc123hash"
        )
        
        # Verify creation
        assert manifest["run_id"] == run_id
        assert manifest["engine_version"] == "16.30"
        assert manifest["job_input"] == sample_job_input
        
        # Load manifest
        loaded_manifest = manager.load_manifest()
        assert loaded_manifest["run_id"] == run_id
        assert loaded_manifest["master_resume_hash"] == "abc123hash"
    
    def test_add_checkpoint(self, temp_workflow_dir, sample_job_input):
        """Test adding checkpoints to manifest."""
        run_path = os.path.join(temp_workflow_dir, "test_run_007")
        os.makedirs(run_path, exist_ok=True)
        
        manager = ManifestManager(run_path)
        
        # Create manifest
        manager.create_manifest(
            run_id="test_run_007",
            engine_version="16.30",
            job_input=sample_job_input,
            master_resume_hash="abc123"
        )
        
        # Add checkpoint
        checkpoint = HopCheckpoint(
            hop_id="HOP-0",
            hop_name="JD Analysis",
            status=HopStatus.PASS,
            timestamp_start="2025-01-01T00:00:00Z",
            timestamp_end="2025-01-01T00:00:05Z",
            validation_results=[]
        )
        
        manager.add_checkpoint(checkpoint)
        
        # Load and verify
        checkpoints = manager.get_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0].hop_id == "HOP-0"
        assert checkpoints[0].status == HopStatus.PASS


# ============================================================================
# TEST SUITE 03: RESUMABLE WORKFLOW EXECUTION
# ============================================================================

class TestResumableExecution:
    """Tests for resumable workflow execution."""
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_new_run_initialization(self, mock_master_resume, mock_app_config, sample_job_input):
        """Test creating a new workflow run."""
        orchestrator = WorkflowOrchestrator(
            config=mock_app_config,
            master_resume=mock_master_resume,
            job_input=sample_job_input
        )
        
        # Verify initialization
        assert orchestrator.run_id is not None
        assert len(orchestrator.run_id) == 8  # UUID[:8]
        assert os.path.exists(orchestrator.run_path)
        assert orchestrator.job_input == sample_job_input
        
        # Verify manifest was created
        manifest_path = os.path.join(orchestrator.run_path, "run_manifest.json")
        assert os.path.exists(manifest_path)
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_idempotent_hop_execution(self, mock_master_resume,
                                      mock_app_config, sample_job_input,
                                      sample_thematic_analysis):
        """Test that hops skip execution when cache exists."""
        orchestrator = WorkflowOrchestrator(
            config=mock_app_config,
            master_resume=mock_master_resume,
            job_input=sample_job_input
        )
        
        # Manually save HOP-0 output to simulate cache
        orchestrator.state_serializer.save(0, sample_thematic_analysis)
        
        # Create a mock jd_analyzer if it's None (when genai not installed)
        if orchestrator.jd_analyzer is None:
            orchestrator.jd_analyzer = MagicMock()
        
        # Mock the actual analysis method
        with patch.object(orchestrator.jd_analyzer, 'analyze') as mock_analyze:
            # Execute HOP-0
            orchestrator._execute_hop_0_jd_analysis()
            
            # Verify analyze was NOT called (cache hit)
            mock_analyze.assert_not_called()
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_cache_miss_executes_hop(self, mock_master_resume,
                                     mock_app_config, sample_job_input,
                                     sample_thematic_analysis):
        """Test that hops execute when cache doesn't exist."""
        orchestrator = WorkflowOrchestrator(
            config=mock_app_config,
            master_resume=mock_master_resume,
            job_input=sample_job_input
        )
        
        # Ensure no cache exists
        assert not orchestrator.state_serializer.exists(0)
        
        # Create a mock jd_analyzer if it's None (when genai not installed)
        if orchestrator.jd_analyzer is None:
            orchestrator.jd_analyzer = MagicMock()
        
        # Mock the analysis method
        with patch.object(orchestrator.jd_analyzer, 'analyze',
                        return_value=(sample_thematic_analysis, 1)) as mock_analyze:
            # Execute HOP-0
            orchestrator._execute_hop_0_jd_analysis()
            
            # Verify analyze WAS called (cache miss)
            mock_analyze.assert_called_once()
            
            # Verify output was saved
            assert orchestrator.state_serializer.exists(0)


# ============================================================================
# TEST SUITE 04: FORCE RERUN FUNCTIONALITY
# ============================================================================

class TestForceRerun:
    """Tests for force rerun and cache invalidation."""
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_force_rerun_deletes_downstream_cache(self, mock_master_resume, mock_app_config,
                                                   sample_job_input, sample_thematic_analysis):
        """Test that force_rerun_from_hop deletes downstream cache files."""
        orchestrator = WorkflowOrchestrator(
            config=mock_app_config,
            master_resume=mock_master_resume,
            job_input=sample_job_input
        )
        
        # Create fake cache files for hops 0-5 using correct types
        # HOP-0 needs ThematicAnalysis
        orchestrator.state_serializer.save(0, sample_thematic_analysis)
        # HOP-1, 2, 3, 4 use dict type
        for hop in [1, 2, 3, 4]:
            if hop in orchestrator.state_serializer.HOP_CONFIG:
                orchestrator.state_serializer.save(hop, {"fake": f"data_{hop}"})
        # HOP-5 needs ValidationResult list
        orchestrator.state_serializer.save(5, [])
        
        # Verify all exist
        for hop in range(6):
            if hop in orchestrator.state_serializer.HOP_CONFIG:
                assert orchestrator.state_serializer.exists(hop)
        
        # Mock the execution methods
        with patch.object(orchestrator, '_execute_hop_3_artist_generation') as mock_hop3, \
             patch.object(orchestrator, '_execute_hop_4_staging_and_sanitization') as mock_hop4, \
             patch.object(orchestrator, '_execute_hop_5_validation') as mock_hop5:
            
            # Force rerun using the actual method
            orchestrator._delete_downstream_hop_files(3)
            
            # Verify hops 3, 4, 5 were deleted
            assert not orchestrator.state_serializer.exists(3)
            assert not orchestrator.state_serializer.exists(4)
            assert not orchestrator.state_serializer.exists(5)
            
            # Verify hops 0-2 still exist
            assert orchestrator.state_serializer.exists(0)
            assert orchestrator.state_serializer.exists(1)
            assert orchestrator.state_serializer.exists(2)


# ============================================================================
# TEST SUITE 05: REGRESSION TESTS (Legacy Functionality)
# ============================================================================

class TestRegressionValidation:
    """Regression tests for validation logic."""
    
    @pytest.fixture
    def validator(self, mock_master_resume, mock_app_config):
        """Returns a real PreFlightValidator."""
        return PreFlightValidator(
            master_resume=mock_master_resume,
            app_config=mock_app_config
        )
    
    @pytest.mark.parametrize("headline, should_pass", [
        ("Good Title | Good Skill | Good Value", True),
        ("Manager of AI | Good Skill | Good Value", False),
        ("Good Title | VP of Cloud | Good Value", False),
        ("Good Title, Bad Comma | Good Skill", False),
        ("OneComponent", False),
    ])
    def test_headline_validation_regression(self, headline, should_pass, validator):
        """Regression test for headline validation rules."""
        # Create a proper mock context
        mock_buffer = MagicMock()
        mock_buffer.get.return_value = headline
        mock_buffer.data = {ResumeSection.K0_HEADLINE.value: headline}
        
        mock_context = MagicMock()
        mock_context.staging_buffer = mock_buffer
        mock_context.headline_details = {"headline": headline}
        
        # Test forbidden titles
        is_valid = validator._validate_headline_format_no_titles(mock_context)
        has_comma = ',' in headline
        components = headline.split('|')
        is_valid_count = len(components) == 3
        
        result = is_valid and not has_comma and is_valid_count
        assert result == should_pass


class TestRegressionRAG:
    """Regression tests for RAG functionality."""
    
    def test_dict_to_thematic_analysis_static_method(self):
        """Test that _dict_to_thematic_analysis is a proper static method."""
        test_dict = {
            "primary_theme": {"name": "Test"},
            "secondary_themes": [],
            "role_classification": {},
            "positioning_directives": {},
            "authenticity_patterns": {},
            "competitive_intelligence": None,
            "problem_solution_narratives": None,
            "signal_quality_score": 0.5,
            "retrieval_method": "TEST",
            "retrieval_sources": [],
            "weighting_formula": None,
            "evidence_log": []
        }
        
        # Call as static method
        result = EnhancedJobDescriptionAnalyzer._dict_to_thematic_analysis(test_dict)
        
        # Verify reconstruction
        assert isinstance(result, ThematicAnalysis)
        assert result.primary_theme["name"] == "Test"
        assert result.signal_quality_score == 0.5


# ============================================================================
# TEST SUITE 06: END-TO-END INTEGRATION TESTS
# ============================================================================

class TestE2EIntegration:
    """End-to-end integration tests."""
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    @patch('rag_RES.EnhancedJobDescriptionAnalyzer.analyze')
    def test_e2e_new_run_with_mocked_rag(self, mock_rag_analyze,
                                         mock_master_resume, mock_app_config,
                                         sample_job_input, sample_thematic_analysis):
        """Test complete new run with mocked RAG."""
        
        # Mock RAG to return quickly
        mock_rag_analyze.return_value = (sample_thematic_analysis, 1)
        
        orchestrator = WorkflowOrchestrator(
            config=mock_app_config,
            master_resume=mock_master_resume,
            job_input=sample_job_input
        )
        
        # Execute just HOP-0 to verify pipeline
        orchestrator._execute_hop_0_jd_analysis()
        
        # Verify state was saved
        assert orchestrator.state_serializer.exists(0)
        
        # Verify checkpoint was created
        checkpoints = orchestrator.manifest_manager.get_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0].hop_id == "HOP-0"
        assert checkpoints[0].status == HopStatus.PASS


# ============================================================================
# TEST SUITE 07: DATA MODEL TESTS
# ============================================================================

class TestDataModels:
    """Tests for data models in models_RES.py"""
    
    def test_immutable_staging_buffer_lock(self):
        """Test ImmutableStagingBuffer lock mechanism."""
        buffer = ImmutableStagingBuffer()
        
        # Should allow writes before lock
        buffer.set("key1", "value1")
        assert buffer.get("key1") == "value1"
        
        # Lock the buffer
        buffer.lock()
        assert buffer.is_locked()
        
        # Should raise error on write after lock
        from models_RES import StagingBufferError
        with pytest.raises(StagingBufferError):
            buffer.set("key2", "value2")
    
    def test_validation_result_creation(self):
        """Test ValidationResult dataclass creation."""
        result = ValidationResult(
            rule_id="TEST_RULE",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Test message",
            details={"extra": "info"}
        )
        
        assert result.rule_id == "TEST_RULE"
        assert result.passed == True
        assert result.severity == ValidationSeverity.INFO
        assert result.details["extra"] == "info"
    
    def test_hop_checkpoint_creation(self):
        """Test HopCheckpoint dataclass creation."""
        checkpoint = HopCheckpoint(
            hop_id="HOP-0",
            hop_name="Test Hop",
            status=HopStatus.PASS,
            timestamp_start="2025-01-01T00:00:00Z",
            timestamp_end="2025-01-01T00:00:05Z",
            output_hash="abc123",
            validation_results=[],
            metadata={"test": "data"}
        )
        
        assert checkpoint.hop_id == "HOP-0"
        assert checkpoint.status == HopStatus.PASS
        assert checkpoint.metadata["test"] == "data"


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
