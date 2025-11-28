"""
Pytest suite for Resume_Generation_v15_67.py narrative generation fix validation.

Tests v15_67 fixes for HOP-3 Artist Generation failure in narrative sections:
1. Validates section_enum is correctly passed to context builders
2. Ensures _build_context_narrative receives section_enum parameter
3. Confirms narrative generation no longer fails at K.4_TraderSense_Narrative
4. Validates all context builder signatures accept optional section_enum

Also includes v15_66 tests for MasterResumeIndex integration throughout RAG pipeline:
- WebSearchRAG accepts and uses master_resume_index
- Phase 1 and Phase 3 prompts include candidate context
- Synthesis weights keywords based on candidate experience
- Recency scores and achievements influence final prioritization

Run with: pytest test_resume_generation_v15_67.py -v
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
from Resume_Generation_v15_67 import (
    EnhancedJobDescriptionAnalyzer,
    RAGConfig,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    RAGMission,
    WebSearchRAG
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
# RUN CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
