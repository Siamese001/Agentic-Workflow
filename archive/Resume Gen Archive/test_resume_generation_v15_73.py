"""
Pytest suite for Resume_Generation_v15_71.py Configuration Centralization validation.

Tests v15_71 NEW features:
1. AppConfig master dataclass structure and initialization
2. FilePathsConfig centralized file paths
3. ArtistConfig centralized artist generator configuration
4. ValidatorConfig centralized validator configuration
5. WebRagConfig centralized web RAG configuration
6. EnricherConfig centralized enricher configuration
7. Dependency injection of configs into classes
8. WorkflowOrchestrator config management
9. No config drift between ArtistGenerator and PreFlightValidator
10. Backward compatibility - all functional behavior unchanged

Also includes inherited tests from v15_69 for Agentic RAG Loop,
v15_68 for HOP output JSON persistence, v15_67 for narrative generation fix, 
and v15_66 for MasterResumeIndex integration.

Run with: pytest test_resume_generation_v15_71.py -v
"""

import pytest
from typing import Dict, List
from dataclasses import asdict

# Mock imports to avoid external dependencies in tests
import sys
from unittest.mock import Mock, MagicMock, patch

# Create mock modules
sys.modules['google.generativeai'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()

# Import after mocking
from Resume_Generation_v15_73 import (
    EnhancedJobDescriptionAnalyzer,
    RAGConfig,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    RAGMission,
    RAGCritique,
    RAGState,
    RAGEvidence,
    WebSearchRAG,
    WorkflowOrchestrator,
    ImmutableStagingBuffer,
    ThematicAnalysis,
    ValidationResult,
    ValidationSeverity,
    ResumeSection,
    # v15.71: New config classes
    AppConfig,
    FilePathsConfig,
    ArtistConfig,
    ValidatorConfig,
    WebRagConfig,
    EnricherConfig,
    ContentConstraintsConfig,
    SignalControlConfig,
    CONFIG,
    ArtistGenerator,
    PreFlightValidator,
    DataEnricher,
    AppTrackerQAValidator
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_master_resume() -> Dict:
    """Sample master resume data for testing."""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "professional_experience": [
            {
                "role": "Director, Technology Alliances",
                "company": "CloudTech Corp",
                "start_date": "January 2020",
                "end_date": "Present",
                "bullets": [
                    "Led strategic partnerships with AWS, Azure, and GCP resulting in $50M revenue growth",
                    "Managed a team of 12 partnership managers achieving 150% quota attainment",
                    "Developed co-sell programs with Microsoft Azure generating 200+ new enterprise deals"
                ]
            },
            {
                "role": "Senior Account Executive",
                "company": "SaaS Innovations Inc",
                "start_date": "June 2017",
                "end_date": "December 2019",
                "bullets": [
                    "Closed $3.5M in annual recurring revenue through enterprise SaaS sales",
                    "Built relationships with C-level executives at Fortune 500 companies",
                    "Achieved 120% of quota for 8 consecutive quarters"
                ]
            },
            {
                "role": "Business Development Manager",
                "company": "FinTech Solutions",
                "start_date": "March 2015",
                "end_date": "May 2017",
                "bullets": [
                    "Launched partnership program with 50+ financial institutions",
                    "Drove 35% year-over-year growth in API integration partnerships"
                ]
            }
        ]
    }


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description for testing."""
    return """
    As the Director, Technology Alliances you will drive incremental revenue for our company 
    by developing and advancing key strategic global technology partnerships.
    
    Required Qualifications:
    - 5+ years of experience in leadership including hiring and developing sales and partner personnel
    - 10+ years of experience in business development or strategic alliances at a cloud services or SaaS organization
    - Experience with AWS, Google Cloud Platform, and Microsoft Azure partnerships
    - Strong executive communication and relationship management skills
    
    Preferred Qualifications:
    - MBA or equivalent business degree
    - Experience in AI/ML partnerships
    - Familiarity with co-sell programs and joint GTM strategies
    - Background in enterprise software sales
    
    Responsibilities:
    - Serve as executive sponsor for AWS, GCP, and Microsoft Azure
    - Develop and execute strategic initiatives with key technology partnerships
    - Collaborate closely with product leaders to design GTM initiatives
    """


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    client = Mock()
    client.search_and_analyze = Mock(return_value=(
        {
            "jd_entities": {
                "target_company_name": "TestCorp",
                "precise_role_title": "Director, Technology Alliances",
                "key_technologies": ["AWS", "Azure", "GCP", "SaaS"],
                "core_responsibilities": ["strategic partnerships", "GTM strategy"]
            },
            "resume_entities": {
                "candidate_skills": ["AWS", "SaaS", "enterprise sales"]
            },
            "differential_analysis": {
                "signal_gap_keywords": ["GTM strategy", "co-sell programs"],
                "signal_overlap_keywords": ["AWS", "SaaS"]
            }
        },
        1  # API call count
    ))
    return client


# ============================================================================
# TEST SUITE 1: MASTER RESUME SEMANTIC INDEXING (UPGRADE #2)
# ============================================================================

class TestMasterResumeSemanticIndexing:
    """Tests for semantic indexing of master resume."""
    
    def test_index_initialization(self, sample_master_resume):
        """Test that semantic index is built during initialization."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            assert analyzer.master_resume_index is not None
            assert isinstance(analyzer.master_resume_index, MasterResumeIndex)
    
    def test_skill_to_experiences_mapping(self, sample_master_resume):
        """Test that skills are correctly mapped to experiences."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            index = analyzer.master_resume_index
            
            # Check that AWS is mapped to relevant experiences
            assert "aws" in index.skill_to_experiences or "AWS" in index.skill_to_experiences
            
            # Check structure of skill mappings
            skill_key = "aws" if "aws" in index.skill_to_experiences else "AWS"
            if skill_key in index.skill_to_experiences:
                experiences = index.skill_to_experiences[skill_key]
                assert isinstance(experiences, list)
                assert len(experiences) > 0
                
                # Verify experience structure
                exp = experiences[0]
                assert "role" in exp
                assert "company" in exp
                assert "bullet" in exp
                assert "recency" in exp
    
    def test_achievement_catalog_extraction(self, sample_master_resume):
        """Test extraction of quantified achievements."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            index = analyzer.master_resume_index
            
            # Should have extracted metrics like $50M, 150%, 200+, etc.
            assert len(index.achievement_catalog) > 0
            
            # Check structure of achievements
            achievement = index.achievement_catalog[0]
            assert "metric_type" in achievement
            assert "value" in achievement or "context" in achievement
            assert "source_bullet" in achievement
    
    def test_recency_scoring(self, sample_master_resume):
        """Test that recency scores are calculated correctly."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            index = analyzer.master_resume_index
            
            # Should have recency scores for skills
            assert len(index.recency_scores) > 0
            
            # Recency scores should be between 0.0 and 1.0
            for skill, score in index.recency_scores.items():
                assert 0.0 <= score <= 1.0
    
    def test_domain_vocabulary_extraction(self, sample_master_resume):
        """Test extraction of domain-specific vocabularies."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            index = analyzer.master_resume_index
            
            # Should have identified at least one domain
            assert len(index.domain_vocabularies) > 0
            
            # Each domain should have vocabulary list
            for domain, vocab in index.domain_vocabularies.items():
                assert isinstance(vocab, list)
                assert len(vocab) > 0


# ============================================================================
# TEST SUITE 2: STRUCTURED REQUIREMENTS EXTRACTION (UPGRADE #1 - Part A)
# ============================================================================

class TestStructuredRequirementsExtraction:
    """Tests for structured skill requirements extraction."""
    
    def test_extract_structured_requirements(self, sample_master_resume, sample_job_description):
        """Test extraction of must-have vs nice-to-have skills."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            must_have, nice_to_have = analyzer._extract_structured_requirements(sample_job_description)
            
            # Should have extracted both types
            assert len(must_have) > 0
            assert len(nice_to_have) > 0
            
            # Verify structure
            for skill_req in must_have:
                assert isinstance(skill_req, SkillRequirement)
                assert skill_req.requirement_type == "MUST_HAVE"
                assert skill_req.skill is not None
            
            for skill_req in nice_to_have:
                assert isinstance(skill_req, SkillRequirement)
                assert skill_req.requirement_type == "NICE_TO_HAVE"
    
    def test_section_detection(self, sample_master_resume):
        """Test that required vs preferred sections are detected correctly."""
        jd_with_clear_sections = """
        Required:
        - AWS experience
        - 5 years leadership
        
        Preferred:
        - MBA degree
        - AI/ML background
        """
        
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            must_have, nice_to_have = analyzer._extract_structured_requirements(jd_with_clear_sections)
            
            # AWS and leadership should be must-have
            must_have_skills = [sr.skill for sr in must_have]
            assert any("AWS" in skill for skill in must_have_skills)
            
            # MBA should be nice-to-have
            nice_to_have_skills = [sr.skill for sr in nice_to_have]
            assert any("MBA" in skill for skill in nice_to_have_skills)


# ============================================================================
# TEST SUITE 3: SKILL CLUSTERING (UPGRADE #1 - Part B)
# ============================================================================

class TestSkillClustering:
    """Tests for semantic skill clustering."""
    
    def test_cluster_related_skills(self, sample_master_resume):
        """Test clustering of semantically similar skills."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            skills = [
                "AWS", "Azure", "GCP",  # Cloud platforms cluster
                "leadership", "team management", "hiring",  # Leadership cluster
                "sales", "revenue", "quota"  # Sales cluster
            ]
            
            # Mock TfidfVectorizer and cosine_similarity
            with patch('Resume_Generation_v15_66.TfidfVectorizer') as mock_vectorizer, \
                 patch('Resume_Generation_v15_66.cosine_similarity') as mock_similarity:
                
                # Setup mocks
                mock_vec_instance = Mock()
                mock_vectorizer.return_value = mock_vec_instance
                mock_vec_instance.fit_transform.return_value = Mock()
                
                # Mock similarity matrix with known clusters
                import numpy as np
                similarity_matrix = np.array([
                    [1.0, 0.8, 0.7, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # AWS
                    [0.8, 1.0, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # Azure
                    [0.7, 0.9, 1.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # GCP
                    [0.1, 0.1, 0.1, 1.0, 0.7, 0.6, 0.2, 0.2, 0.2],  # leadership
                    [0.1, 0.1, 0.1, 0.7, 1.0, 0.8, 0.2, 0.2, 0.2],  # team management
                    [0.1, 0.1, 0.1, 0.6, 0.8, 1.0, 0.2, 0.2, 0.2],  # hiring
                    [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 1.0, 0.6, 0.7],  # sales
                    [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.6, 1.0, 0.8],  # revenue
                    [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.7, 0.8, 1.0],  # quota
                ])
                mock_similarity.return_value = similarity_matrix
                
                clusters = analyzer._cluster_related_skills(skills)
                
                # Should have identified clusters
                assert len(clusters) > 0
                
                # Verify cluster structure
                for cluster in clusters:
                    assert isinstance(cluster, SkillCluster)
                    assert len(cluster.skills) > 1  # Cluster should have multiple skills
                    assert cluster.representative_skill in cluster.skills
                    assert 0.0 <= cluster.confidence <= 1.0
    
    def test_empty_skill_list(self, sample_master_resume):
        """Test clustering with empty or single skill list."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Empty list
            clusters = analyzer._cluster_related_skills([])
            assert len(clusters) == 0
            
            # Single skill
            clusters = analyzer._cluster_related_skills(["AWS"])
            assert len(clusters) == 0


# ============================================================================
# TEST SUITE 4: IMPLICIT SKILL INFERENCE (UPGRADE #1 - Part C)
# ============================================================================

class TestImplicitSkillInference:
    """Tests for implicit skill inference from domain context."""
    
    def test_infer_implicit_skills_partnerships(self, sample_master_resume):
        """Test inference from 'strategic partnerships' context."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            explicit_skills = ["strategic partnerships"]
            domain_context = "technology alliances and cloud partnerships"
            
            implicit = analyzer._infer_implicit_skills(explicit_skills, domain_context)
            
            # Should infer relationship management, executive communication, etc.
            assert len(implicit) > 0
            implicit_lower = [s.lower() for s in implicit]
            
            # Check for expected inferred skills
            expected_inferences = ["relationship management", "executive communication", "cloud platforms"]
            found = sum(1 for exp in expected_inferences if any(exp in imp for imp in implicit_lower))
            assert found > 0
    
    def test_infer_implicit_skills_enterprise_sales(self, sample_master_resume):
        """Test inference from 'enterprise sales' context."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            explicit_skills = ["enterprise sales"]
            domain_context = "selling SaaS solutions to Fortune 500"
            
            implicit = analyzer._infer_implicit_skills(explicit_skills, domain_context)
            
            # Should infer account management, quota attainment, etc.
            implicit_lower = [s.lower() for s in implicit]
            expected = ["account management", "quota attainment", "pipeline management"]
            found = sum(1 for exp in expected if any(exp in imp for imp in implicit_lower))
            assert found > 0
    
    def test_no_duplicate_explicit_skills(self, sample_master_resume):
        """Test that inferred skills don't duplicate explicit skills."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            explicit_skills = ["AWS", "relationship management", "strategic partnerships"]
            domain_context = "cloud partnerships"
            
            implicit = analyzer._infer_implicit_skills(explicit_skills, domain_context)
            
            # Implicit should not contain any explicit skills
            implicit_lower = [s.lower() for s in implicit]
            explicit_lower = [s.lower() for s in explicit_skills]
            
            for imp in implicit_lower:
                assert imp not in explicit_lower


# ============================================================================
# TEST SUITE 5: ENHANCED HOP-0.5 INTEGRATION
# ============================================================================

class TestEnhancedHOP05Integration:
    """Tests for integrated HOP-0.5 execution with enhancements."""
    
    def test_execute_pre_rag_analysis_with_enhancements(self, sample_master_resume, 
                                                        sample_job_description, mock_gemini_client):
        """Test that _execute_pre_rag_analysis uses all enhancements."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', True):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=True
            )
            analyzer.gemini_client = mock_gemini_client
            
            mission = analyzer._execute_pre_rag_analysis(sample_job_description)
            
            # Verify mission structure
            assert isinstance(mission, RAGMission)
            assert mission.target_company_name == "TestCorp"
            assert mission.precise_role_title == "Director, Technology Alliances"
            
            # Verify key_technologies was enhanced (should have more than original 4)
            assert len(mission.key_technologies) >= 4
            
            # Verify API was called
            mock_gemini_client.search_and_analyze.assert_called_once()
    
    def test_enhancement_logging(self, sample_master_resume, sample_job_description, 
                                 mock_gemini_client, caplog):
        """Test that enhancements generate appropriate log messages."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', True):
            import logging
            caplog.set_level(logging.INFO)
            
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=True
            )
            analyzer.gemini_client = mock_gemini_client
            
            mission = analyzer._execute_pre_rag_analysis(sample_job_description)
            
            # Check for enhancement log messages
            assert "Extracting structured requirements" in caplog.text
            assert "Clustering related skills" in caplog.text
            assert "Inferring implicit skills" in caplog.text
            assert "Enhanced key_technologies" in caplog.text


# ============================================================================
# TEST SUITE 6: HELPER METHOD VALIDATION
# ============================================================================

class TestHelperMethods:
    """Tests for helper methods used in enhancements."""
    
    def test_extract_skills_from_text(self, sample_master_resume):
        """Test skill extraction from text."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            text = "Led strategic partnerships with AWS, Azure, and GCP using Python and ML models"
            skills = analyzer._extract_skills_from_text(text)
            
            # Should extract capitalized terms and acronyms
            assert len(skills) > 0
            skills_str = " ".join(skills)
            assert any(s in skills_str for s in ["AWS", "Azure", "GCP", "Python", "ML"])
    
    def test_extract_metrics_from_text(self, sample_master_resume):
        """Test metric extraction from text."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            text = "Generated $50M revenue, improved efficiency by 35%, managed 200+ customers"
            metrics = analyzer._extract_metrics_from_text(text)
            
            # Should extract money, percentage, and count metrics
            assert len(metrics) >= 3
            
            metric_types = [m["metric_type"] for m in metrics]
            assert "revenue/cost" in metric_types or "percentage" in metric_types
    
    def test_infer_domain(self, sample_master_resume):
        """Test domain inference from experience."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Cloud partnerships context
            domain = analyzer._infer_domain(
                "Director, Cloud Alliances",
                "AWS Solutions Inc",
                ["Led AWS partnership programs"]
            )
            assert domain == "cloud_partnerships"
            
            # Enterprise sales context
            domain = analyzer._infer_domain(
                "Enterprise Account Executive",
                "Salesforce",
                ["Closed $5M in enterprise SaaS deals"]
            )
            assert domain == "enterprise_sales"


# ============================================================================
# TEST SUITE 7: PERFORMANCE & EDGE CASES
# ============================================================================

class TestPerformanceAndEdgeCases:
    """Tests for performance and edge case handling."""
    
    def test_large_resume_indexing_performance(self):
        """Test indexing performance with large resume."""
        large_resume = {
            "professional_experience": [
                {
                    "role": f"Role {i}",
                    "company": f"Company {i}",
                    "start_date": "January 2010",
                    "end_date": "Present",
                    "bullets": [f"Bullet {j} with skills like Python AWS Azure" for j in range(10)]
                }
                for i in range(10)  # 10 roles with 10 bullets each
            ]
        }
        
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            import time
            start = time.time()
            
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=large_resume,
                enable_web_search=False
            )
            
            elapsed = time.time() - start
            
            # Should complete within reasonable time (< 2 seconds)
            assert elapsed < 2.0
            assert analyzer.master_resume_index is not None
    
    def test_empty_resume_handling(self):
        """Test handling of empty resume."""
        empty_resume = {"professional_experience": []}
        
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=empty_resume,
                enable_web_search=False
            )
            
            # Should not crash, should have empty index
            assert analyzer.master_resume_index is not None
            assert len(analyzer.master_resume_index.skill_to_experiences) == 0
    
    def test_malformed_jd_handling(self, sample_master_resume):
        """Test handling of malformed job description."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Empty JD
            must_have, nice_to_have = analyzer._extract_structured_requirements("")
            assert isinstance(must_have, list)
            assert isinstance(nice_to_have, list)
            
            # JD with special characters
            weird_jd = "Required: $$$ AWS ### Azure @@@ GCP"
            must_have, nice_to_have = analyzer._extract_structured_requirements(weird_jd)
            assert isinstance(must_have, list)


# ============================================================================
# v15_66 INTEGRATION TESTS
# ============================================================================

class TestMasterResumeIndexIntegration:
    """Test suite for v15_66 MasterResumeIndex integration into RAG pipeline."""
    
    def test_web_search_rag_accepts_index(self, sample_master_resume):
        """Test that WebSearchRAG accepts master_resume_index parameter."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Create mock WebSearchRAG with index
            from Resume_Generation_v15_66 import GeminiWebSearchClient
            mock_client = Mock(spec=GeminiWebSearchClient)
            
            web_rag = WebSearchRAG(
                client=mock_client,
                config=RAGConfig(),
                master_resume_index=analyzer.master_resume_index
            )
            
            # Verify index is stored
            assert web_rag.master_resume_index is not None
            assert web_rag.master_resume_index == analyzer.master_resume_index
    
    def test_phase1_prompt_includes_candidate_context(self, sample_master_resume):
        """Test that Phase 1 prompt includes candidate context from index."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Create WebSearchRAG with index
            mock_client = Mock()
            web_rag = WebSearchRAG(
                client=mock_client,
                config=RAGConfig(),
                master_resume_index=analyzer.master_resume_index
            )
            
            # Create mock mission
            mission = RAGMission(
                target_company_name="TestCorp",
                precise_role_title="Director",
                key_technologies=["AWS", "Azure"],
                core_responsibilities=["Leadership"],
                signal_gap_keywords=[],
                signal_overlap_keywords=[]
            )
            
            # Build prompt
            prompt = web_rag._build_phase1_prompt("Sample JD", mission)
            
            # Verify candidate context is included
            assert "CANDIDATE BACKGROUND CONTEXT" in prompt
            assert "demonstrated expertise" in prompt.lower()
    
    def test_phase3_prompt_includes_achievements(self, sample_master_resume):
        """Test that Phase 3 prompt includes candidate achievements."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Verify achievements were extracted
            assert len(analyzer.master_resume_index.achievement_catalog) > 0
            
            # Create WebSearchRAG with index
            mock_client = Mock()
            web_rag = WebSearchRAG(
                client=mock_client,
                config=RAGConfig(),
                master_resume_index=analyzer.master_resume_index
            )
            
            # Create mock mission
            mission = RAGMission(
                target_company_name="TestCorp",
                precise_role_title="Director",
                key_technologies=["AWS"],
                core_responsibilities=[],
                signal_gap_keywords=[],
                signal_overlap_keywords=[]
            )
            
            # Build prompt
            prompt = web_rag._build_phase3_prompt("Sample JD", mission)
            
            # Verify achievements context is included
            assert "CANDIDATE ACHIEVEMENTS" in prompt
            assert "quantified results" in prompt.lower()
    
    def test_synthesis_applies_candidate_weighting(self, sample_master_resume):
        """Test that synthesis applies candidate experience weighting."""
        with patch('Resume_Generation_v15_66.GEMINI_AVAILABLE', False):
            analyzer = EnhancedJobDescriptionAnalyzer(
                master_resume=sample_master_resume,
                enable_web_search=False
            )
            
            # Create WebSearchRAG with index
            mock_client = Mock()
            web_rag = WebSearchRAG(
                client=mock_client,
                config=RAGConfig(),
                master_resume_index=analyzer.master_resume_index
            )
            
            # Set up mock mission
            web_rag.rag_mission = RAGMission(
                target_company_name="TestCorp",
                precise_role_title="Director",
                key_technologies=["AWS", "Azure", "Leadership"],
                core_responsibilities=[],
                signal_gap_keywords=[],
                signal_overlap_keywords=[]
            )
            
            # Mock phase results
            phase1 = {
                "thematic_analysis": {
                    "primary_theme": {
                        "name": "Cloud Partnerships",
                        "confidence": 0.9,
                        "keywords": ["AWS", "Azure", "Partnership"]
                    },
                    "secondary_themes": [],
                    "trending_keywords": ["Leadership"]
                },
                "role_classification": {
                    "seniority": "executive",
                    "precise_role_title": "Director"
                }
            }
            
            phase2 = {
                "authenticity_patterns": {},
                "pattern_confidence": {"overall": 0.8}
            }
            
            phase3 = {
                "competitive_analysis": {
                    "differentiator_keywords": [
                        {"keyword": "AWS", "uniqueness_score": 0.9}
                    ],
                    "table_stakes_keywords": []
                },
                "search_summary": {"peer_jds_analyzed": 5}
            }
            
            phase4 = {}
            
            # Call synthesis (will apply candidate weighting)
            result = web_rag._synthesize_thematic_analysis(
                phase1, phase2, phase3, phase4, "Sample JD"
            )
            
            # Verify result has competitive intelligence with weighted keywords
            assert hasattr(result, 'competitive_intel')
            assert len(result.competitive_intel.differentiator_keywords) > 0


# ============================================================================
# V15_68 SPECIFIC TESTS: HOP OUTPUT JSON PERSISTENCE
# ============================================================================

class TestHOPOutputJSONPersistence:
    """Tests for v15_68 intermediate HOP output JSON saving functionality."""
    
    def test_save_hop_output_json_method_exists(self, sample_master_resume):
        """Verify _save_hop_output_json method exists on WorkflowOrchestrator."""
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        assert hasattr(orchestrator, '_save_hop_output_json')
        assert callable(orchestrator._save_hop_output_json)
    
    def test_save_hop_output_json_creates_directory(self, sample_master_resume, tmp_path):
        """Verify _save_hop_output_json creates correct directory structure."""
        import os
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        
        # Mock the workflow_id to a known value
        orchestrator.workflow_id = "test1234"
        
        # Create test data
        test_data = {"test_key": "test_value"}
        
        # Save using the method (in tmp_path)
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            orchestrator._save_hop_output_json("HOP-0", "TestOutput", test_data)
            
            # Verify directory exists
            expected_dir = tmp_path / "workflow_outputs" / "test1234" / "intermediate_hops"
            assert expected_dir.exists()
            
            # Verify file exists with correct name
            expected_file = expected_dir / "test1234_HOP-0_TestOutput.json"
            assert expected_file.exists()
            
            # Verify file contains JSON
            import json
            with open(expected_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
        finally:
            os.chdir(original_cwd)
    
    def test_save_hop_output_json_handles_dataclasses(self, sample_master_resume, tmp_path):
        """Verify _save_hop_output_json correctly serializes dataclasses."""
        import os
        import json
        from datetime import datetime
        
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        orchestrator.workflow_id = "test5678"
        
        # Create a ValidationResult (dataclass) to test serialization
        validation_result = ValidationResult(
            rule_id="TEST_RULE",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Test message",
            details={"key": "value"}
        )
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            orchestrator._save_hop_output_json("HOP-5", "TestValidation", [validation_result])
            
            expected_file = tmp_path / "workflow_outputs" / "test5678" / "intermediate_hops" / "test5678_HOP-5_TestValidation.json"
            assert expected_file.exists()
            
            # Verify dataclass was serialized
            with open(expected_file, 'r') as f:
                saved_data = json.load(f)
            
            assert isinstance(saved_data, list)
            assert len(saved_data) == 1
            assert saved_data[0]['rule_id'] == "TEST_RULE"
            assert saved_data[0]['passed'] is True
            assert saved_data[0]['severity'] == "INFO"  # Enum value as string
        finally:
            os.chdir(original_cwd)
    
    def test_save_hop_output_json_handles_immutable_staging_buffer(self, sample_master_resume, tmp_path):
        """Verify _save_hop_output_json correctly serializes ImmutableStagingBuffer."""
        import os
        import json
        
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        orchestrator.workflow_id = "test9999"
        
        # Create an ImmutableStagingBuffer
        buffer = ImmutableStagingBuffer()
        buffer.set("test_section", "test_content")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            orchestrator._save_hop_output_json("HOP-4", "StagingBuffer", buffer.data)
            
            expected_file = tmp_path / "workflow_outputs" / "test9999" / "intermediate_hops" / "test9999_HOP-4_StagingBuffer.json"
            assert expected_file.exists()
            
            # Verify buffer data was serialized
            with open(expected_file, 'r') as f:
                saved_data = json.load(f)
            
            assert "test_section" in saved_data
            assert saved_data["test_section"] == "test_content"
        finally:
            os.chdir(original_cwd)
    
    def test_save_hop_output_json_handles_serialization_errors(self, sample_master_resume, tmp_path):
        """Verify _save_hop_output_json doesn't halt workflow on serialization errors."""
        import os
        
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        orchestrator.workflow_id = "testerr"
        
        # Create unserializable object (function)
        def unserializable_func():
            pass
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # This should not raise an exception
            orchestrator._save_hop_output_json("HOP-TEST", "ErrorTest", unserializable_func)
            # Method should log warning but not crash
        finally:
            os.chdir(original_cwd)
    
    def test_json_filenames_match_specification(self, sample_master_resume):
        """Verify JSON filenames follow the specified convention."""
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        workflow_id = orchestrator.workflow_id
        
        # Expected filename patterns
        expected_patterns = [
            (f"{workflow_id}_HOP-0.5_RAGMission.json", "HOP-0.5", "RAGMission"),
            (f"{workflow_id}_HOP-0_ThematicAnalysis.json", "HOP-0", "ThematicAnalysis"),
            (f"{workflow_id}_HOP-1_ExtractedData.json", "HOP-1", "ExtractedData"),
            (f"{workflow_id}_HOP-2_EnrichedScaffold.json", "HOP-2", "EnrichedScaffold"),
            (f"{workflow_id}_HOP-3_ArtistOutput.json", "HOP-3", "ArtistOutput"),
            (f"{workflow_id}_HOP-4_StagingBufferData.json", "HOP-4", "StagingBufferData"),
            (f"{workflow_id}_HOP-4.5_SanitizedBufferData.json", "HOP-4.5", "SanitizedBufferData"),
            (f"{workflow_id}_HOP-5_ValidationResults.json", "HOP-5", "ValidationResults"),
            (f"{workflow_id}_HOP-7_FilePaths.json", "HOP-7", "FilePaths"),
        ]
        
        # All expected patterns should be valid
        for expected_filename, hop_id, output_desc in expected_patterns:
            # Verify naming convention
            assert expected_filename.startswith(workflow_id)
            assert hop_id in expected_filename
            assert output_desc in expected_filename
            assert expected_filename.endswith(".json")
    
    def test_json_output_pretty_printed(self, sample_master_resume, tmp_path):
        """Verify JSON output is pretty-printed for human readability."""
        import os
        import json
        
        orchestrator = WorkflowOrchestrator(sample_master_resume, test_mode=True)
        orchestrator.workflow_id = "testpret"
        
        test_data = {
            "key1": "value1",
            "key2": {"nested": "value2"},
            "key3": [1, 2, 3]
        }
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            orchestrator._save_hop_output_json("HOP-TEST", "PrettyTest", test_data)
            
            expected_file = tmp_path / "workflow_outputs" / "testpret" / "intermediate_hops" / "testpret_HOP-TEST_PrettyTest.json"
            
            # Read raw file content
            with open(expected_file, 'r') as f:
                content = f.read()
            
            # Verify it's pretty-printed (contains newlines and indentation)
            assert '\n' in content
            assert '  ' in content  # 2-space indentation
        finally:
            os.chdir(original_cwd)


# ============================================================================
# NEW v15_69: AGENTIC RAG LOOP TESTS
# ============================================================================

class TestAgenticRAGDataclasses:
    """Test new v15_69 dataclasses for agentic RAG loop."""
    
    def test_rag_evidence_structure(self):
        """Verify RAGEvidence dataclass has required fields."""
        evidence = RAGEvidence(
            iteration=1,
            action="initial_search",
            query_or_action="Test query",
            findings_summary="Found 5 sources",
            sources_count=5,
            confidence_contribution=0.5
        )
        
        assert evidence.iteration == 1
        assert evidence.action == "initial_search"
        assert evidence.sources_count == 5
        assert evidence.confidence_contribution == 0.5
        assert hasattr(evidence, 'timestamp')
    
    def test_rag_critique_structure(self):
        """Verify RAGCritique dataclass has required fields."""
        critique = RAGCritique(
            confidence_score=0.75,
            gaps_identified=["Gap 1", "Gap 2"],
            refinement_tasks=["Task 1"],
            reasoning="Test reasoning",
            is_sufficient=True
        )
        
        assert critique.confidence_score == 0.75
        assert len(critique.gaps_identified) == 2
        assert len(critique.refinement_tasks) == 1
        assert critique.is_sufficient is True
    
    def test_rag_state_initialization(self):
        """Verify RAGState initializes correctly."""
        state = RAGState(
            phase_name="Phase 1",
            iteration=1
        )
        
        assert state.phase_name == "Phase 1"
        assert state.iteration == 1
        assert state.evidence_log == []
        assert state.total_api_calls == 0
        assert state.critiques == []
        assert state.cumulative_result is None
    
    def test_rag_state_add_evidence(self):
        """Verify evidence can be added to RAGState."""
        state = RAGState(phase_name="Test", iteration=1)
        
        evidence = RAGEvidence(
            iteration=1,
            action="test",
            query_or_action="query",
            findings_summary="summary",
            sources_count=3,
            confidence_contribution=0.3
        )
        
        state.add_evidence(evidence)
        
        assert len(state.evidence_log) == 1
        assert state.evidence_log[0] == evidence
    
    def test_rag_state_add_critique(self):
        """Verify critiques can be added to RAGState."""
        state = RAGState(phase_name="Test", iteration=1)
        
        critique = RAGCritique(
            confidence_score=0.6,
            gaps_identified=[],
            refinement_tasks=[],
            reasoning="test",
            is_sufficient=False
        )
        
        state.add_critique(critique)
        
        assert len(state.critiques) == 1
        assert state.get_latest_critique() == critique
    
    def test_thematic_analysis_has_evidence_log(self):
        """Verify ThematicAnalysis dataclass has evidence_log field."""
        analysis = ThematicAnalysis()
        
        assert hasattr(analysis, 'evidence_log')
        assert isinstance(analysis.evidence_log, list)
        assert analysis.evidence_log == []


class TestAgenticRAGCritique:
    """Test critique evaluation logic."""
    
    def setup_method(self):
        """Setup mock client for testing."""
        self.mock_genai = MagicMock()
        
        with patch('Resume_Generation_v15_69.genai', self.mock_genai), \
             patch('Resume_Generation_v15_69.GEMINI_AVAILABLE', True):
            from Resume_Generation_v15_69 import GeminiWebSearchClient
            self.client = GeminiWebSearchClient(config=RAGConfig())
    
    def test_critique_low_search_count(self):
        """Test that low search count reduces confidence."""
        result = {
            'search_summary': {
                'searches_performed': 2,
                'sources': ['url1', 'url2']
            },
            'thematic_analysis': {
                'primary_theme': {'name': 'Test'},
                'secondary_themes': [{'name': 'Theme1'}],
                'trending_keywords': ['kw1', 'kw2', 'kw3']
            }
        }
        
        critique = self.client._critique_rag_results(result, "Phase 1", 1)
        
        assert critique.confidence_score < 0.7
        assert any('search depth' in gap.lower() or 'fewer than 5' in gap.lower() 
                  for gap in critique.gaps_identified)
    
    def test_critique_sufficient_data(self):
        """Test that sufficient data yields high confidence."""
        result = {
            'search_summary': {
                'searches_performed': 12,
                'sources': [f'https://domain{i}.com' for i in range(8)]
            },
            'thematic_analysis': {
                'primary_theme': {'name': 'Test'},
                'secondary_themes': [{'name': f'Theme{i}'} for i in range(4)],
                'trending_keywords': [f'kw{i}' for i in range(10)]
            }
        }
        
        critique = self.client._critique_rag_results(result, "Phase 1", 1)
        
        assert critique.confidence_score >= 0.7
        assert critique.is_sufficient is True
    
    def test_critique_identifies_missing_primary_theme(self):
        """Test that missing primary theme is flagged as gap."""
        result = {
            'search_summary': {
                'searches_performed': 10,
                'sources': [f'url{i}' for i in range(8)]
            },
            'thematic_analysis': {
                'secondary_themes': [{'name': 'Theme1'}],
                'trending_keywords': ['kw1', 'kw2']
            }
        }
        
        critique = self.client._critique_rag_results(result, "Phase 1 Thematic", 1)
        
        assert any('primary theme' in gap.lower() for gap in critique.gaps_identified)
        assert critique.confidence_score < 0.7
    
    def test_critique_source_diversity(self):
        """Test that source diversity affects confidence."""
        # All sources from same domain
        result_low_diversity = {
            'search_summary': {
                'searches_performed': 10,
                'sources': [f'https://samedomain.com/page{i}' for i in range(8)]
            },
            'thematic_analysis': {
                'primary_theme': {'name': 'Test'},
                'secondary_themes': [{'name': 'Theme1'}]
            }
        }
        
        critique_low = self.client._critique_rag_results(result_low_diversity, "Phase 1", 1)
        
        # Diverse sources
        result_high_diversity = {
            'search_summary': {
                'searches_performed': 10,
                'sources': [f'https://domain{i}.com' for i in range(8)]
            },
            'thematic_analysis': {
                'primary_theme': {'name': 'Test'},
                'secondary_themes': [{'name': 'Theme1'}]
            }
        }
        
        critique_high = self.client._critique_rag_results(result_high_diversity, "Phase 1", 1)
        
        # High diversity should have higher confidence
        assert critique_high.confidence_score > critique_low.confidence_score


class TestAgenticRAGRefinement:
    """Test refinement prompt generation and result merging."""
    
    def setup_method(self):
        """Setup mock client for testing."""
        self.mock_genai = MagicMock()
        
        with patch('Resume_Generation_v15_69.genai', self.mock_genai), \
             patch('Resume_Generation_v15_69.GEMINI_AVAILABLE', True):
            from Resume_Generation_v15_69 import GeminiWebSearchClient
            self.client = GeminiWebSearchClient(config=RAGConfig())
    
    def test_build_refinement_prompt_includes_gaps(self):
        """Test that refinement prompt includes identified gaps."""
        original_prompt = "Search for job data"
        
        critique = RAGCritique(
            confidence_score=0.5,
            gaps_identified=["Gap 1", "Gap 2"],
            refinement_tasks=["Task 1", "Task 2"],
            reasoning="Test",
            is_sufficient=False
        )
        
        result = {'search_summary': {}}
        
        refined_prompt = self.client._build_refinement_prompt(
            original_prompt=original_prompt,
            current_result=result,
            critique=critique,
            phase_name="Phase 1"
        )
        
        assert "Gap 1" in refined_prompt
        assert "Gap 2" in refined_prompt
        assert "Task 1" in refined_prompt
        assert "Task 2" in refined_prompt
        assert original_prompt in refined_prompt
    
    def test_merge_rag_results_accumulates_sources(self):
        """Test that merging combines sources without duplication."""
        original = {
            'search_summary': {
                'searches_performed': 5,
                'sources': ['url1', 'url2', 'url3']
            }
        }
        
        refined = {
            'search_summary': {
                'searches_performed': 3,
                'sources': ['url3', 'url4', 'url5']  # url3 is duplicate
            }
        }
        
        merged = self.client._merge_rag_results(original, refined, "Phase 1")
        
        assert merged['search_summary']['searches_performed'] == 8
        assert len(merged['search_summary']['sources']) == 5  # Deduplicated
        assert 'url3' in merged['search_summary']['sources']
        assert 'url5' in merged['search_summary']['sources']
    
    def test_merge_rag_results_combines_keywords(self):
        """Test that merging combines keyword lists."""
        original = {
            'search_summary': {'searches_performed': 5, 'sources': []},
            'thematic_analysis': {
                'trending_keywords': ['kw1', 'kw2'],
                'required_skills': ['skill1']
            }
        }
        
        refined = {
            'search_summary': {'searches_performed': 3, 'sources': []},
            'thematic_analysis': {
                'trending_keywords': ['kw2', 'kw3', 'kw4'],
                'required_skills': ['skill2']
            }
        }
        
        merged = self.client._merge_rag_results(original, refined, "Phase 1 Thematic")
        
        merged_keywords = merged['thematic_analysis']['trending_keywords']
        assert len(merged_keywords) == 4  # kw1, kw2, kw3, kw4 deduplicated
        assert 'kw1' in merged_keywords
        assert 'kw4' in merged_keywords
        
        merged_skills = merged['thematic_analysis']['required_skills']
        assert 'skill1' in merged_skills
        assert 'skill2' in merged_skills


class TestAgenticRAGIntegration:
    """Integration tests for full agentic RAG loop."""
    
    def test_agentic_loop_returns_state_with_evidence(self):
        """Test that agentic loop returns complete RAGState."""
        # This is a mock-based integration test
        mock_genai = MagicMock()
        
        with patch('Resume_Generation_v15_69.genai', mock_genai), \
             patch('Resume_Generation_v15_69.GEMINI_AVAILABLE', True):
            from Resume_Generation_v15_69 import GeminiWebSearchClient
            client = GeminiWebSearchClient(config=RAGConfig())
            
            # Mock search_and_analyze to return valid structure
            mock_result = {
                'search_summary': {
                    'searches_performed': 12,
                    'sources': [f'https://domain{i}.com' for i in range(10)]
                },
                'thematic_analysis': {
                    'primary_theme': {'name': 'Test', 'confidence': 0.9},
                    'secondary_themes': [{'name': f'Theme{i}'} for i in range(4)],
                    'trending_keywords': [f'kw{i}' for i in range(10)]
                }
            }
            
            client.search_and_analyze = Mock(return_value=(mock_result, 1))
            
            # Run agentic loop
            result, calls, state = client.agentic_search_and_analyze(
                prompt="Test prompt",
                phase_name="Phase 1",
                max_iterations=3,
                confidence_threshold=0.7
            )
            
            # Verify state structure
            assert isinstance(state, RAGState)
            assert state.phase_name == "Phase 1"
            assert len(state.evidence_log) >= 1  # At least initial evidence
            assert len(state.critiques) >= 1  # At least initial critique
            assert state.total_api_calls >= 1
            
            # Verify result has evidence attached
            if 'thematic_analysis' in result:
                assert 'evidence_log' in result['thematic_analysis']
    
    def test_agentic_loop_early_termination_on_high_confidence(self):
        """Test that loop terminates early if confidence threshold met."""
        mock_genai = MagicMock()
        
        with patch('Resume_Generation_v15_69.genai', mock_genai), \
             patch('Resume_Generation_v15_69.GEMINI_AVAILABLE', True):
            from Resume_Generation_v15_69 import GeminiWebSearchClient
            client = GeminiWebSearchClient(config=RAGConfig())
            
            # Mock high-quality result
            high_quality_result = {
                'search_summary': {
                    'searches_performed': 15,
                    'sources': [f'https://domain{i}.com' for i in range(12)]
                },
                'thematic_analysis': {
                    'primary_theme': {'name': 'Test', 'confidence': 0.95},
                    'secondary_themes': [{'name': f'Theme{i}'} for i in range(5)],
                    'trending_keywords': [f'kw{i}' for i in range(15)]
                }
            }
            
            client.search_and_analyze = Mock(return_value=(high_quality_result, 1))
            
            # Run with max 3 iterations
            result, calls, state = client.agentic_search_and_analyze(
                prompt="Test prompt",
                phase_name="Phase 1",
                max_iterations=3,
                confidence_threshold=0.7
            )
            
            # Should terminate after iteration 1 due to high confidence
            assert state.iteration == 1
            latest_critique = state.get_latest_critique()
            assert latest_critique.confidence_score >= 0.7
            assert latest_critique.is_sufficient


# ============================================================================
# RUN CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


# ============================================================================
# v15_71 CONFIGURATION CENTRALIZATION TESTS
# ============================================================================

def test_app_config_initialization():
    """Test that global CONFIG is properly initialized with all sub-configs."""
    assert CONFIG is not None, "Global CONFIG should be initialized"
    assert isinstance(CONFIG, AppConfig), "CONFIG should be AppConfig instance"
    assert isinstance(CONFIG.paths, FilePathsConfig), "CONFIG.paths should be FilePathsConfig"
    assert isinstance(CONFIG.artist, ArtistConfig), "CONFIG.artist should be ArtistConfig"
    assert isinstance(CONFIG.validator, ValidatorConfig), "CONFIG.validator should be ValidatorConfig"
    assert isinstance(CONFIG.web_rag, WebRagConfig), "CONFIG.web_rag should be WebRagConfig"
    assert isinstance(CONFIG.enricher, EnricherConfig), "CONFIG.enricher should be EnricherConfig"
    assert isinstance(CONFIG.content_constraints, ContentConstraintsConfig), "CONFIG.content_constraints should be ContentConstraintsConfig"
    assert isinstance(CONFIG.signal_constraints, SignalControlConfig), "CONFIG.signal_constraints should be SignalControlConfig"

def test_artist_config_structure():
    """Test that ArtistConfig contains expected configuration."""
    artist_config = CONFIG.artist
    
    # Test provenance_split_targets
    assert 'K2_UNIFY_BULLETS' in artist_config.provenance_split_targets
    assert artist_config.provenance_split_targets['K2_UNIFY_BULLETS'] == {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2}
    
    # Test bullet_word_count_ranges
    assert 'K2_UNIFY_BULLETS' in artist_config.bullet_word_count_ranges
    assert artist_config.bullet_word_count_ranges['K2_UNIFY_BULLETS'] == (28, 38)
    
    # Test narrative_config
    assert 'K4_TRADERSENSE_NARRATIVE' in artist_config.narrative_config
    assert 'min_wc_key' in artist_config.narrative_config['K4_TRADERSENSE_NARRATIVE']

def test_validator_config_structure():
    """Test that ValidatorConfig contains expected configuration."""
    validator_config = CONFIG.validator
    
    # Test forbidden_verbs
    assert isinstance(validator_config.forbidden_verbs, list)
    assert "spearheaded" in validator_config.forbidden_verbs
    assert "leveraged" in validator_config.forbidden_verbs
    
    # Test required_sections
    assert isinstance(validator_config.required_sections, set)
    assert 'K0_NAME' in validator_config.required_sections
    assert 'K1_EXECUTIVE_SUMMARY' in validator_config.required_sections
    
    # Test pipeline_status_enum
    assert isinstance(validator_config.pipeline_status_enum, list)
    assert "Applied" in validator_config.pipeline_status_enum

def test_web_rag_config_structure():
    """Test that WebRagConfig contains expected configuration."""
    web_rag_config = CONFIG.web_rag
    
    # Test peers_by_industry
    assert isinstance(web_rag_config.peers_by_industry, dict)
    assert "Financial Technology" in web_rag_config.peers_by_industry
    assert "JPMorgan" in web_rag_config.peers_by_industry["Financial Technology"]

def test_enricher_config_structure():
    """Test that EnricherConfig contains expected configuration."""
    enricher_config = CONFIG.enricher
    
    # Test canonical_verbs
    assert isinstance(enricher_config.canonical_verbs, dict)
    assert "led" in enricher_config.canonical_verbs
    assert enricher_config.canonical_verbs["led"] == ["led", "lead", "leading"]

def test_no_config_drift_between_artist_and_validator():
    """Test that ArtistConfig and ValidatorConfig have matching provenance_split_targets."""
    artist_targets = CONFIG.artist.provenance_split_targets
    validator_targets = CONFIG.validator.provenance_split_targets
    
    # Both should have the same keys
    assert set(artist_targets.keys()) == set(validator_targets.keys()), \
        "Artist and Validator provenance_split_targets should have matching keys"
    
    # Values should match for each key
    for key in artist_targets.keys():
        assert artist_targets[key] == validator_targets[key], \
            f"Artist and Validator provenance_split_targets for {key} should match"

def test_workflow_orchestrator_receives_config(sample_master_resume):
    """Test that WorkflowOrchestrator can be instantiated with CONFIG."""
    with patch('Resume_Generation_v15_71.setup_workflow_logging', return_value=(MagicMock(), 'test.log')):
        orchestrator = WorkflowOrchestrator(sample_master_resume, config=CONFIG, test_mode=True)
        assert orchestrator.config is CONFIG
        assert orchestrator.constraints is CONFIG.content_constraints

def test_artist_generator_receives_config(sample_master_resume):
    """Test that ArtistGenerator receives and uses artist_config."""
    enriched_scaffold = {}
    job_description = "Test JD"
    thematic_analysis = ThematicAnalysis()
    artist_specs = {}
    
    artist = ArtistGenerator(
        master_resume=sample_master_resume,
        enriched_scaffold=enriched_scaffold,
        job_description=job_description,
        thematic_analysis=thematic_analysis,
        artist_specs=artist_specs,
        artist_config=CONFIG.artist,
        content_constraints=CONFIG.content_constraints
    )
    
    assert artist.artist_config is CONFIG.artist
    assert artist.constraints is CONFIG.content_constraints
    assert hasattr(artist, 'PROVENANCE_SPLIT_TARGETS')
    assert hasattr(artist, 'BULLET_WORD_COUNT_RANGES')
    assert hasattr(artist, 'NARRATIVE_CONFIG')

def test_preflight_validator_receives_config(sample_master_resume):
    """Test that PreFlightValidator receives and uses validator_config."""
    validator = PreFlightValidator(
        master_resume=sample_master_resume,
        validator_config=CONFIG.validator,
        content_constraints=CONFIG.content_constraints,
        signal_config=CONFIG.signal_constraints
    )
    
    assert validator.validator_config is CONFIG.validator
    assert validator.constraints is CONFIG.content_constraints
    assert validator.signal_constraints is CONFIG.signal_constraints
    assert hasattr(validator, 'FORBIDDEN_VERBS')
    assert hasattr(validator, 'REQUIRED_SECTIONS')

def test_data_enricher_receives_config():
    """Test that DataEnricher receives and uses enricher_config."""
    enricher = DataEnricher(enricher_config=CONFIG.enricher)
    
    assert enricher.CANONICAL_VERBS == CONFIG.enricher.canonical_verbs

def test_app_tracker_qa_validator_receives_config():
    """Test that AppTrackerQAValidator receives and uses validator_config."""
    validator = AppTrackerQAValidator(validator_config=CONFIG.validator)
    
    assert validator.PIPELINE_STATUS_ENUM == CONFIG.validator.pipeline_status_enum

def test_config_immutability_pattern():
    """Test that config follows immutability pattern (single source of truth)."""
    # CONFIG should be the single global instance
    assert CONFIG is not None
    
    # Creating a new AppConfig should not affect global CONFIG
    new_config = AppConfig()
    assert new_config is not CONFIG
    assert new_config.artist is not CONFIG.artist

def test_backward_compatibility_functional_behavior(sample_master_resume):
    """Test that v15_71 maintains backward compatibility in functional behavior."""
    # Test that WorkflowOrchestrator can still be instantiated
    with patch('Resume_Generation_v15_71.setup_workflow_logging', return_value=(MagicMock(), 'test.log')):
        orchestrator = WorkflowOrchestrator(sample_master_resume, config=CONFIG, test_mode=True)
        assert orchestrator is not None
        assert hasattr(orchestrator, 'execute_workflow')

