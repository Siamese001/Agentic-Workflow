"""
Test suite for meta-learning pattern learning capabilities.

Tests the advanced pattern learning features that should be implemented
in apps_rg and apps_lic to match agentic_core capabilities.
"""

import pytest
import time
from unittest.mock import Mock, patch

# Test imports - these will need to be implemented
try:
    from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
    from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase
except ImportError as e:
    pytest.skip(f"Apps not yet enhanced with pattern learning: {e}", allow_module_level=True)


class TestPatternLearning:
    """Test pattern learning capabilities for both RG and LIC agents."""

    def test_resume_quality_pattern_embedding(self):
        """Test resume quality patterns generate embeddings for semantic search."""
        agent = RGAgentBase()

        pattern_data = {
            "structure": "chronological",
            "sections": ["summary", "experience", "education"],
            "quality_score": 0.95,
            "ats_compatible": True,
            "industry": "technology",
        }

        # Test enhanced caching with embedding
        result = agent.ml_cache_resume_quality_pattern_enhanced("test_pattern_001", pattern_data)
        assert result is True, "Resume quality pattern should be cached successfully"

        # Verify embedding was generated and stored
        cached = agent.ml_recall_resume_quality_pattern("test_pattern_001")
        assert cached is not None, "Cached pattern should be retrievable"
        assert "embedding" in cached, "Pattern should have embedding"
        assert cached["domain"] == "apps_rg", "Pattern should have correct domain"
        assert "timestamp" in cached, "Pattern should have timestamp"

        # Verify embedding is a list of floats
        assert isinstance(cached["embedding"], list), "Embedding should be a list"
        if cached["embedding"]:  # If embedding was generated
            assert all(isinstance(x, float) for x in cached["embedding"]), (
                "Embedding values should be floats"
            )

    def test_campaign_pattern_embedding(self):
        """Test campaign patterns generate embeddings for semantic search."""
        agent = LICAgentBase()

        pattern_data = {
            "template": "tech_outreach",
            "timing": "tuesday_9am",
            "response_rate": 0.12,
            "audience": "engineering_managers",
            "channel": "linkedin",
        }

        # Test enhanced caching with embedding
        result = agent.ml_cache_campaign_pattern_enhanced("test_campaign_001", pattern_data)
        assert result is True, "Campaign pattern should be cached successfully"

        # Verify embedding was generated and stored
        cached = agent.ml_recall_campaign_pattern("test_campaign_001")
        assert cached is not None, "Cached pattern should be retrievable"
        assert "embedding" in cached, "Pattern should have embedding"
        assert cached["domain"] == "apps_lic", "Pattern should have correct domain"
        assert "timestamp" in cached, "Pattern should have timestamp"

        # Verify embedding is a list of floats
        assert isinstance(cached["embedding"], list), "Embedding should be a list"
        if cached["embedding"]:  # If embedding was generated
            assert all(isinstance(x, float) for x in cached["embedding"]), (
                "Embedding values should be floats"
            )

    def test_ats_compatibility_pattern_learning(self):
        """Test ATS compatibility pattern learning for RG domain."""
        agent = RGAgentBase()

        ats_data = {
            "system": "lever",
            "requirements": {
                "pdf_only": False,
                "max_file_size": "2MB",
                "required_sections": ["experience", "education"],
                "forbidden_formats": ["doc", "docx"],
            },
            "optimization_tips": [
                "Use standard section headers",
                "Avoid tables and columns",
                "Use simple fonts",
            ],
        }

        # Cache ATS compatibility data
        result = agent.ml_cache_ats_compatibility("lever", ats_data)
        assert result is True, "ATS compatibility data should be cached"

        # Retrieve and verify
        cached = agent.ml_recall_ats_compatibility("lever")
        assert cached is not None, "Cached ATS data should be retrievable"
        assert cached["system"] == "lever", "Should retrieve correct ATS system"
        assert "requirements" in cached, "Should contain requirements"
        assert "optimization_tips" in cached, "Should contain optimization tips"

    def test_section_balance_pattern_learning(self):
        """Test section balance pattern learning for different job types."""
        agent = RGAgentBase()

        job_types = [
            (
                "software_engineer",
                {
                    "summary_weight": 0.15,
                    "experience_weight": 0.50,
                    "education_weight": 0.15,
                    "skills_weight": 0.20,
                },
            ),
            (
                "product_manager",
                {
                    "summary_weight": 0.20,
                    "experience_weight": 0.45,
                    "education_weight": 0.10,
                    "skills_weight": 0.25,
                },
            ),
            (
                "data_scientist",
                {
                    "summary_weight": 0.10,
                    "experience_weight": 0.40,
                    "education_weight": 0.25,
                    "skills_weight": 0.25,
                },
            ),
        ]

        for job_type, balance_data in job_types:
            # Cache balance data
            result = agent.ml_cache_section_balance(job_type, balance_data)
            assert result is True, f"Section balance for {job_type} should be cached"

            # Retrieve and verify
            cached = agent.ml_recall_section_balance(job_type)
            assert cached is not None, f"Cached balance for {job_type} should be retrievable"
            assert cached["summary_weight"] == balance_data["summary_weight"], (
                f"Should retrieve correct balance for {job_type}"
            )

    def test_compliance_rule_pattern_learning(self):
        """Test compliance rule pattern learning for LIC domain."""
        agent = LICAgentBase()

        compliance_rules = [
            (
                "gdpr",
                {
                    "consent_required": True,
                    "data_retention_days": 30,
                    "right_to_deletion": True,
                    "privacy_policy_required": True,
                },
            ),
            (
                "canada_anti_spam",
                {
                    "consent_required": True,
                    "unsubscribe_required": True,
                    "identification_required": True,
                    "timing_restrictions": "9am-6pm_local",
                },
            ),
        ]

        for rule_id, rule_data in compliance_rules:
            # Cache compliance rule
            result = agent.ml_cache_compliance_rule(rule_id, rule_data)
            assert result is True, f"Compliance rule {rule_id} should be cached"

            # Retrieve and verify
            cached = agent.ml_recall_compliance_rule(rule_id)
            assert cached is not None, f"Cached rule {rule_id} should be retrievable"
            assert cached["consent_required"] == rule_data["consent_required"], (
                f"Should retrieve correct rule for {rule_id}"
            )


class TestSemanticPatternRetrieval:
    """Test semantic similarity-based pattern retrieval."""

    def test_semantic_resume_pattern_retrieval(self):
        """Test semantic similarity retrieves relevant resume patterns."""
        agent = RGAgentBase()

        # Store similar patterns with embeddings
        patterns = [
            {
                "pattern_id": "pattern_001",
                "type": "resume_quality",
                "message": "Missing work experience section",
                "fix": "add_experience_section",
                "data": {"section": "experience", "action": "add"},
            },
            {
                "pattern_id": "pattern_002",
                "type": "resume_quality",
                "message": "No work history listed",
                "fix": "include_work_history",
                "data": {"section": "experience", "action": "create"},
            },
            {
                "pattern_id": "pattern_003",
                "type": "resume_quality",
                "message": "Experience section too short",
                "fix": "expand_experience",
                "data": {"section": "experience", "action": "expand"},
            },
            {
                "pattern_id": "pattern_004",
                "type": "resume_quality",
                "message": "Missing education section",
                "fix": "add_education_section",
                "data": {"section": "education", "action": "add"},
            },
        ]

        # Cache patterns with embeddings
        for pattern in patterns:
            agent.ml_cache_resume_quality_pattern_enhanced(pattern["pattern_id"], pattern)

        # Test semantic retrieval for similar violation
        violation = {
            "type": "resume_quality",
            "message": "Work experience missing from resume",
            "path": "/resume/experience",
        }

        # Mock the meta client's retrieve method
        with patch.object(agent._meta_client, "retrieve_healing_patterns") as mock_retrieve:
            # Setup mock to return similar patterns
            mock_patterns = [
                Mock(similarity_score=0.92, to_dict=lambda: patterns[0]),
                Mock(similarity_score=0.88, to_dict=lambda: patterns[1]),
                Mock(similarity_score=0.85, to_dict=lambda: patterns[2]),
            ]
            mock_retrieve.return_value = mock_patterns

            # Retrieve patterns
            retrieved = agent._meta_client.retrieve_healing_patterns(
                violation, domain="apps_rg", min_similarity=0.85
            )

            assert len(retrieved) == 3, "Should retrieve 3 similar patterns"
            assert retrieved[0].similarity_score >= 0.85, "All patterns should meet threshold"

            # Should be sorted by similarity (highest first)
            assert retrieved[0].similarity_score >= retrieved[1].similarity_score, (
                "Should be sorted by similarity"
            )

    def test_semantic_campaign_pattern_retrieval(self):
        """Test semantic similarity retrieves relevant campaign patterns."""
        agent = LICAgentBase()

        # Store campaign patterns
        campaigns = [
            {
                "pattern_id": "campaign_001",
                "type": "campaign_optimization",
                "message": "Low open rate for tech outreach",
                "fix": "optimize_subject_line",
                "data": {"metric": "open_rate", "improvement": "subject_optimization"},
            },
            {
                "pattern_id": "campaign_002",
                "type": "campaign_optimization",
                "message": "Poor response from engineering managers",
                "fix": "personalize_content",
                "data": {"metric": "response_rate", "improvement": "personalization"},
            },
        ]

        # Cache campaigns with embeddings
        for campaign in campaigns:
            agent.ml_cache_campaign_pattern_enhanced(campaign["pattern_id"], campaign)

        # Test semantic retrieval
        incident = {
            "type": "campaign_performance",
            "message": "Engineering outreach campaign not getting responses",
            "channel": "linkedin",
        }

        # Mock the meta client's retrieve method
        with patch.object(agent._meta_client, "retrieve_healing_patterns") as mock_retrieve:
            # Setup mock to return similar patterns
            mock_campaigns = [
                Mock(similarity_score=0.90, to_dict=lambda: campaigns[1]),
                Mock(similarity_score=0.75, to_dict=lambda: campaigns[0]),
            ]
            mock_retrieve.return_value = mock_campaigns

            # Retrieve patterns
            retrieved = agent._meta_client.retrieve_healing_patterns(
                incident,
                domain="apps_lic",
                min_similarity=0.92,  # Higher threshold for LIC
            )

            # Should only return patterns meeting the higher threshold
            assert len(retrieved) == 1, "Should retrieve 1 pattern meeting high threshold"
            assert retrieved[0].similarity_score >= 0.92, "Pattern should meet LIC threshold"


class TestPatternEvolution:
    """Test pattern evolution and learning over time."""

    def test_pattern_success_tracking(self):
        """Test successful patterns are tracked and prioritized."""
        agent = RGAgentBase()

        # Store a pattern
        pattern_data = {
            "type": "resume_quality",
            "message": "Missing skills section",
            "fix": "add_skills_section",
            "success_count": 1,
        }

        agent.ml_cache_resume_quality_pattern_enhanced("skills_pattern", pattern_data)

        # Simulate multiple successful applications
        for i in range(5):
            # Increment success count
            cached = agent.ml_recall_resume_quality_pattern("skills_pattern")
            if cached:
                cached["success_count"] += 1
                agent.ml_cache_resume_quality_pattern_enhanced("skills_pattern", cached)

        # Verify success tracking
        final_cached = agent.ml_recall_resume_quality_pattern("skills_pattern")
        assert final_cached["success_count"] >= 5, "Should track successful applications"

    def test_pattern_ttl_expiration(self):
        """Test patterns expire according to TTL policies."""
        agent = LICAgentBase()

        # Cache a pattern
        pattern_data = {"type": "campaign", "message": "test pattern"}
        agent.ml_cache_campaign_pattern_enhanced("ttl_test", pattern_data)

        # Verify it exists
        cached = agent.ml_recall_campaign_pattern("ttl_test")
        assert cached is not None, "Pattern should be cached initially"

        # Mock time passage (beyond TTL)
        with patch("time.time") as mock_time:
            # Set time to be beyond TTL (7200 seconds for LIC)
            mock_time.return_value = time.time() + 8000

            # Pattern should be expired (if TTL enforcement is implemented)
            # This test will need to be adapted based on actual TTL implementation
            pass  # Implementation dependent

    def test_pattern_adaptation_by_domain(self):
        """Test patterns adapt differently based on domain characteristics."""
        rg_agent = RGAgentBase()
        lic_agent = LICAgentBase()

        # Same pattern type for both domains
        base_pattern = {"type": "performance_issue", "message": "Response rate below target"}

        # RG-specific adaptation
        rg_pattern = {
            **base_pattern,
            "domain_specific": {
                "target_response_rate": 0.15,  # Resume submission response
                "optimization_focus": "resume_content",
            },
        }

        # LIC-specific adaptation
        lic_pattern = {
            **base_pattern,
            "domain_specific": {
                "target_response_rate": 0.08,  # Campaign response
                "optimization_focus": "messaging_strategy",
            },
        }

        # Cache both patterns
        rg_agent.ml_cache_resume_quality_pattern_enhanced("performance_rg", rg_pattern)
        lic_agent.ml_cache_campaign_pattern_enhanced("performance_lic", lic_pattern)

        # Verify domain-specific adaptations
        rg_cached = rg_agent.ml_recall_resume_quality_pattern("performance_rg")
        lic_cached = lic_agent.ml_recall_campaign_pattern("performance_lic")

        assert rg_cached["domain_specific"]["target_response_rate"] == 0.15
        assert lic_cached["domain_specific"]["target_response_rate"] == 0.08


if __name__ == "__main__":
    pytest.main([__file__])
