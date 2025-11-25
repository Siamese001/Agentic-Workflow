"""
Test Workflow Planning

Tests comprehensive workflow planning functionality for résumé optimization,
including profile inference, complexity classification, and workflow bundle creation.
"""

import pytest
from unittest.mock import Mock, patch

# Import actual workflow planning components
try:
    from l1.workflow_planning import (
        build_workflow_plan_bundle,
        _normalize_text,
        _map_meta_profile_to_routing_hint,
        _infer_seniority,
        _infer_domains,
        _infer_skill_clusters,
        _classify_complexity,
        _choose_reasoning_mode,
        _to_execution_profile,
    )
    from core.models.models import (
        JobInput,
        ResumeInput,
        WorkflowConfig,
        ComplexityLevel,
        ReasoningMode,
        SeniorityClassifierResult,
        DomainClassifierResult,
        SkillClusterResult,
        ProfileInferenceResult,
        WorkflowPlanBundle,
        ExecutionProfile,
        RetrievalConfig,
    )
    from config.config_profiles_v10_10 import ExecutionProfileSpec, get_profile
    from config.meta_profile import MetaProfileSnapshot
except ImportError:
    pytest.skip("Workflow planning components not available", allow_module_level=True)

# Mark as L1 planning tests
pytestmark = [pytest.mark.l1, pytest.mark.planning, pytest.mark.workflow]


class TestWorkflowPlanning:
    """Test workflow planning functionality."""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        dirty_text = "  Hello   World!  \n\n  This   has   extra   spaces.  "
        normalized = _normalize_text(dirty_text)
        
        # _normalize_text only strips whitespace, doesn't collapse spaces
        assert normalized == "Hello   World!  \n\n  This   has   extra   spaces."
        assert not normalized.startswith(" ")
        assert not normalized.endswith(" ")
    
    def test_normalize_text_none_handling(self):
        """Test text normalization with None and empty inputs."""
        assert _normalize_text(None) == ""
        assert _normalize_text("") == ""
        assert _normalize_text("   ") == ""
    
    def test_infer_seniority_executive(self):
        """Test seniority inference for executive roles."""
        job_text = "Chief Technology Officer role reporting to CEO"
        resume_text = "SVP of Engineering with executive leadership"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "executive"
    
    def test_infer_seniority_director(self):
        """Test seniority inference for director roles."""
        job_text = "Director of Software Engineering"
        resume_text = "Head of Development team"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "director"
    
    def test_infer_seniority_manager(self):
        """Test seniority inference for manager roles."""
        job_text = "Engineering Manager position"
        resume_text = "Team Lead with management experience"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "manager"
    
    def test_infer_seniority_senior_ic(self):
        """Test seniority inference for senior individual contributor."""
        job_text = "Senior Software Developer role"
        resume_text = "Staff Engineer with technical expertise"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "senior_ic"
    
    def test_infer_seniority_junior(self):
        """Test seniority inference for junior roles."""
        job_text = "Junior Developer position"
        resume_text = "Entry-level software engineer"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "junior"
    
    def test_infer_seniority_default(self):
        """Test seniority inference defaults to mid-level."""
        job_text = "Software Developer position"
        resume_text = "Computer science graduate"
        
        seniority = _infer_seniority(job_text, resume_text)
        
        assert seniority == "mid"
    
    def test_infer_domains_insurance(self):
        """Test domain inference for insurance industry."""
        job_text = "Actuarial analyst position"
        resume_text = "Insurance risk management experience"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "insurance" in domains
    
    def test_infer_domains_financial_services(self):
        """Test domain inference for financial services."""
        job_text = "Investment banking role"
        resume_text = "Credit analysis and trading experience"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "financial_services" in domains
    
    def test_infer_domains_foundation_models(self):
        """Test domain inference for foundation models."""
        job_text = "LLM research position"
        resume_text = "Large language model development"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "foundation_models" in domains
    
    def test_infer_domains_machine_learning(self):
        """Test domain inference for machine learning."""
        job_text = "ML Engineer position"
        resume_text = "Machine learning and deep learning expertise"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "machine_learning" in domains
    
    def test_infer_domains_cloud(self):
        """Test domain inference for cloud computing."""
        job_text = "Cloud Architect role"
        resume_text = "AWS and Azure experience"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "cloud" in domains
    
    def test_infer_domains_data_platform(self):
        """Test domain inference for data platforms."""
        job_text = "Data Platform Engineer"
        resume_text = "Databricks and Snowflake experience"
        
        domains = _infer_domains(job_text, resume_text)
        
        assert "data_platform" in domains
    
    def test_infer_skill_clusters_python_data(self):
        """Test skill cluster inference for Python data stack."""
        job_text = "Data Scientist position"
        resume_text = "Python, pandas, numpy expertise"
        
        clusters = _infer_skill_clusters(job_text, resume_text)
        
        assert "python_data" in clusters
    
    def test_infer_skill_clusters_deep_learning(self):
        """Test skill cluster inference for deep learning."""
        job_text = "AI Research position"
        resume_text = "PyTorch, TensorFlow, Keras experience"
        
        clusters = _infer_skill_clusters(job_text, resume_text)
        
        assert "deep_learning" in clusters
    
    def test_infer_skill_clusters_cloud_infra(self):
        """Test skill cluster inference for cloud infrastructure."""
        job_text = "DevOps Engineer"
        resume_text = "AWS, Azure, GCP deployment experience"
        
        clusters = _infer_skill_clusters(job_text, resume_text)
        
        assert "cloud_infra" in clusters
    
    def test_classify_complexity_low(self):
        """Test complexity classification for low content."""
        job_text = "Short job description"
        resume_text = "Brief resume"
        
        profile_spec = Mock()
        profile_spec.min_complexity = None
        
        complexity = _classify_complexity(job_text, resume_text, profile_spec, None)
        
        assert complexity == ComplexityLevel.LOW
    
    def test_classify_complexity_medium(self):
        """Test complexity classification for medium content."""
        job_text = " ".join(["word"] * 500)  # ~500 words
        resume_text = " ".join(["word"] * 500)  # ~500 words
        
        profile_spec = Mock()
        profile_spec.min_complexity = None
        
        complexity = _classify_complexity(job_text, resume_text, profile_spec, None)
        
        assert complexity == ComplexityLevel.MEDIUM
    
    def test_classify_complexity_high(self):
        """Test complexity classification for high content."""
        job_text = " ".join(["word"] * 1500)  # ~1500 words
        resume_text = " ".join(["word"] * 1500)  # ~1500 words
        
        profile_spec = Mock()
        profile_spec.min_complexity = None
        
        complexity = _classify_complexity(job_text, resume_text, profile_spec, None)
        
        assert complexity == ComplexityLevel.HIGH
    
    def test_classify_complexity_with_meta_profile_elevation(self):
        """Test complexity elevation with meta profile."""
        job_text = "Short job description"
        resume_text = "Brief resume"
        
        profile_spec = Mock()
        profile_spec.min_complexity = None
        
        meta_profile = Mock()
        meta_profile.elevated_caution = True
        meta_profile.correction_rate_last_10 = 0.4
        
        complexity = _classify_complexity(job_text, resume_text, profile_spec, meta_profile)
        
        assert complexity == ComplexityLevel.MEDIUM  # Elevated from LOW
    
    def test_choose_reasoning_mode_default(self):
        """Test reasoning mode selection with defaults."""
        profile_spec = Mock()
        profile_spec.reasoning_mode = ReasoningMode.CHAIN_OF_THOUGHT
        
        mode = _choose_reasoning_mode(profile_spec, None)
        
        assert mode == ReasoningMode.CHAIN_OF_THOUGHT
    
    def test_choose_reasoning_mode_with_meta_hint(self):
        """Test reasoning mode selection with meta profile hints."""
        profile_spec = Mock()
        profile_spec.reasoning_mode = ReasoningMode.CHAIN_OF_THOUGHT
        
        meta_profile = Mock()
        meta_profile.reasoning_mode_hint = "tot"
        
        mode = _choose_reasoning_mode(profile_spec, meta_profile)
        
        assert mode == ReasoningMode.TOT
    
    def test_to_execution_profile(self):
        """Test conversion to execution profile."""
        profile_spec = Mock()
        profile_spec.id = "test_profile"
        profile_spec.description = "Test profile"
        profile_spec.retrieval = RetrievalConfig(strategy="hybrid", max_hits=16)
        profile_spec.safety_tier.value = "standard"
        profile_spec.model_tier.value = "balanced"
        profile_spec.max_cost_usd = 1.0
        profile_spec.max_latency_ms = 5000
        profile_spec.qa_council_size = 3
        profile_spec.enable_correction_loop = True
        profile_spec.max_corrections = 2
        profile_spec.rag_allow_hyde = False
        profile_spec.hyde_model_tier = "balanced"
        profile_spec.routing_telemetry_mode = "basic"
        
        profile = _to_execution_profile(profile_spec)
        
        assert isinstance(profile, ExecutionProfile)
        assert profile.name == "test_profile"
        assert profile.description == "Test profile"
        assert profile.metadata["safety_tier"] == "standard"
        assert profile.metadata["model_tier"] == "balanced"
    
    def test_map_meta_profile_to_routing_hint(self):
        """Test meta profile to routing hint mapping."""
        meta_profile = Mock()
        meta_profile.active_profile_id = "test_profile"
        meta_profile.prefers_anthropic = True
        meta_profile.prefers_openai = False
        meta_profile.prefers_fast_models = False
        meta_profile.reasoning_mode_hint = "cot"
        meta_profile.qa_failure_rate_last_10 = 0.1
        meta_profile.correction_rate_last_10 = 0.2
        meta_profile.extra_qa_passes = 1
        meta_profile.reinforce_strictness = False
        meta_profile.elevated_caution = False
        meta_profile.hil_preferred = False
        meta_profile.seniority_label = "senior_ic"
        meta_profile.domain_label = "software"
        meta_profile.skill_cluster_labels = {"python_data"}
        
        routing_hint = _map_meta_profile_to_routing_hint(meta_profile)
        
        assert routing_hint["active_profile_id"] == "test_profile"
        assert routing_hint["prefers_anthropic"] is True
        assert routing_hint["reasoning_mode_hint"] == "cot"
        assert routing_hint["seniority_label"] == "senior_ic"
        assert "python_data" in routing_hint["skill_cluster_labels"]
    
    def test_map_meta_profile_to_routing_hint_none(self):
        """Test routing hint mapping with None meta profile."""
        routing_hint = _map_meta_profile_to_routing_hint(None)
        
        assert routing_hint == {}
    
    @patch('l1.workflow_planning.get_profile')
    def test_build_workflow_plan_bundle_basic(self, mock_get_profile):
        """Test basic workflow plan bundle creation."""
        # Mock dependencies
        profile_spec = Mock()
        profile_spec.id = "test_profile"  # Actual string, not Mock
        profile_spec.description = "Test profile"  # Actual string, not Mock
        profile_spec.qa_depth = 2  # Actual integer, not Mock
        profile_spec.min_complexity = None
        profile_spec.reasoning_mode = ReasoningMode.CHAIN_OF_THOUGHT
        profile_spec.retrieval = RetrievalConfig(strategy="hybrid", max_hits=16)
        profile_spec.safety_tier.value = "standard"
        profile_spec.model_tier.value = "balanced"
        profile_spec.max_cost_usd = 1.0
        profile_spec.max_latency_ms = 5000
        profile_spec.qa_council_size = 3
        profile_spec.enable_correction_loop = True
        profile_spec.max_corrections = 2
        profile_spec.rag_allow_hyde = False
        profile_spec.hyde_model_tier = "balanced"
        profile_spec.routing_telemetry_mode = "basic"
        
        mock_get_profile.return_value = profile_spec
        
        # Create inputs
        job = JobInput(
            title="Software Engineer",
            requirements=["Python", "AWS experience"]  # Must be List[str]
        )
        
        resume = ResumeInput(
            summary="Python developer with AWS experience",
            experience_sections=[],  # Required field
            skills=["Python", "AWS"],  # Required field
            projects=[]  # Required field
        )
        
        config = WorkflowConfig(
            profile_id="default",
            enable_rag=True,
            enable_qa=True
        )
        
        # Build workflow plan
        bundle = build_workflow_plan_bundle(job, resume, config)
        
        # Validate bundle structure
        assert isinstance(bundle, WorkflowPlanBundle)
        assert hasattr(bundle, 'strategy')
        assert hasattr(bundle, 'prompt_meta')
    
    @patch('l1.workflow_planning.get_profile')
    def test_build_workflow_plan_bundle_with_meta_profile(self, mock_get_profile):
        """Test workflow plan bundle with meta profile."""
        # Mock dependencies
        profile_spec = Mock()
        profile_spec.id = "test_profile"  # Actual string, not Mock
        profile_spec.description = "Test profile"  # Actual string, not Mock
        profile_spec.qa_depth = 2  # Actual integer, not Mock
        profile_spec.min_complexity = None
        profile_spec.reasoning_mode = ReasoningMode.CHAIN_OF_THOUGHT
        profile_spec.retrieval = RetrievalConfig(strategy="hybrid", max_hits=16)
        profile_spec.safety_tier.value = "standard"
        profile_spec.model_tier.value = "balanced"
        profile_spec.max_cost_usd = 1.0
        profile_spec.max_latency_ms = 5000
        profile_spec.qa_council_size = 3
        profile_spec.enable_correction_loop = True
        profile_spec.max_corrections = 2
        profile_spec.rag_allow_hyde = False
        profile_spec.hyde_model_tier = "balanced"
        profile_spec.routing_telemetry_mode = "basic"
        
        mock_get_profile.return_value = profile_spec
        
        # Create meta profile
        meta_profile = Mock()
        meta_profile.active_profile_id = "test_profile"
        meta_profile.prefers_anthropic = True
        meta_profile.prefers_openai = False
        meta_profile.prefers_fast_models = False
        meta_profile.reasoning_mode_hint = "tot"
        meta_profile.qa_failure_rate_last_10 = 0.1
        meta_profile.correction_rate_last_10 = 0.4
        meta_profile.extra_qa_passes = 1
        meta_profile.reinforce_strictness = False
        meta_profile.elevated_caution = True
        meta_profile.hil_preferred = False
        meta_profile.seniority_label = "senior_ic"
        meta_profile.domain_label = "software"
        meta_profile.skill_cluster_labels = {"python_data"}
        
        # Create inputs
        job = JobInput(
            title="Senior Engineer",
            requirements=["5+ years Python", "AWS"]  # Must be List[str]
        )
        
        resume = ResumeInput(
            summary="Senior Python developer with AWS and team leadership",
            experience_sections=[],
            skills=["Python", "AWS", "Leadership"],
            projects=[]
        )
        
        config = WorkflowConfig(
            profile_id="senior",
            enable_rag=True,
            enable_qa=True
        )
        
        # Build workflow plan
        bundle = build_workflow_plan_bundle(job, resume, config, meta_profile=meta_profile)
        
        # Validate bundle incorporates meta profile
        assert isinstance(bundle, WorkflowPlanBundle)
        # Meta profile should influence complexity and reasoning mode
        assert hasattr(bundle, 'strategy')
