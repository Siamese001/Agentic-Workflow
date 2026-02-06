"""
Unit Tests for ATSCompatibilityAgent Facade - Phase 2

Tests the facade conversion of ATSCompatibilityAgent including:
- Legacy signature compatibility
- Delegation to ATSValidatorStrategy
- Signal handling preservation
- Return type consistency
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.agents.UnifiedAgent import ValidationResult


class TestATSValidatorStrategy:
    """Tests for ATSValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "standard_headers": {
                "experience": ["work experience", "employment history"],
                "education": ["academic background"],
                "skills": ["technical skills", "competencies"],
            },
            "ats_unfriendly_patterns": [r"table", r"graphic", r"image"],
            "allowed_non_standard_sections": ["projects", "certifications"],
            "keyword_optimization": {
                "min_score_threshold": 0.3,
                "stop_words": ["the", "and", "for"],
            },
        }

    @pytest.fixture
    def strategy(self, config):
        """Create ATSValidatorStrategy instance."""
        from apps_rg.engines.ATSCompatibilityAgent import ATSValidatorStrategy

        return ATSValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.STANDARD_HEADERS == config["standard_headers"]
        assert strategy.ATS_UNFRIENDLY_PATTERNS == config["ats_unfriendly_patterns"]
        assert strategy.min_score_threshold == 0.3

    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test execute with valid resume."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "5 years of Python development",
            "education": "BS Computer Science",
            "skills": "Python, JavaScript, React",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_execute_no_resume(self, strategy):
        """Test execute with no resume."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert "No resume to check" in result.issues

    @pytest.mark.asyncio
    async def test_execute_ats_unfriendly_pattern(self, strategy):
        """Test execute detects ATS-unfriendly patterns."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "Created table layouts and graphic designs",
            "skills": "Python",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert any("ATS-unfriendly" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_execute_non_standard_header(self, strategy):
        """Test execute detects non-standard headers."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "5 years",
            "random_section": "Some content",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert any("Non-standard section" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_execute_allowed_non_standard(self, strategy):
        """Test execute allows configured non-standard sections."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "5 years",
            "projects": "Open source contributions",
            "certifications": "AWS Certified",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_execute_keyword_score(self, strategy):
        """Test execute calculates keyword score."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {"experience": "Python developer with React experience"}
        job_desc = "Looking for Python and React developer"

        result = await strategy.execute(mock_agent, resume=resume, job_desc=job_desc)

        assert isinstance(result, ValidationResult)
        assert result.score is not None
        assert 0.0 <= result.score <= 1.0

    def test_calculate_keyword_score(self, strategy):
        """Test keyword score calculation."""
        resume = {"skills": "python javascript react"}
        job_desc = "Python developer with React experience"

        score = strategy._calculate_keyword_score(resume, job_desc)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some matches


class TestATSCompatibilityAgentFacade:
    """Tests for ATSCompatibilityAgent facade."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "standard_headers": {"experience": ["work"]},
            "ats_unfriendly_patterns": [],
            "allowed_non_standard_sections": [],
            "keyword_optimization": {"min_score_threshold": 0.3, "stop_words": []},
        }

    @pytest.fixture
    def agent(self, mock_config):
        """Create ATSCompatibilityAgent instance."""
        with patch("apps_rg.engines.ATSCompatibilityAgent.load_agent_config") as mock_load:
            mock_load.return_value = mock_config

            # Mock the parent class initialization
            with patch("apps_rg.shared.core.RGAgentBaseAgent.RGAgentBase.__post_init__"):
                from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

                agent = ATSCompatibilityAgent()
                agent.log = Mock()
                agent.record_pass = Mock()
                agent.record_fail = Mock()
                agent.add_signal = Mock()
                agent.remove_signal = Mock()
                return agent

    def test_legacy_attributes_preserved(self, agent):
        """Test legacy attributes are preserved."""
        assert hasattr(agent, "STANDARD_HEADERS")
        assert hasattr(agent, "ATS_UNFRIENDLY_PATTERNS")
        assert hasattr(agent, "allowed_non_standard_sections")
        assert hasattr(agent, "keyword_config")
        assert hasattr(agent, "min_score_threshold")
        assert hasattr(agent, "stop_words")

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        from apps_rg.engines.ATSCompatibilityAgent import ATSValidatorStrategy

        assert isinstance(agent._unified_strategy, ATSValidatorStrategy)

    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """Test execute with valid resume."""
        agent.ctx = Mock()
        agent.ctx.current_resume = {"experience": "5 years Python"}
        agent.ctx.JobDescription = None

        await agent.execute()

        agent.record_pass.assert_called_once()
        agent.remove_signal.assert_called_with("ATS_FAILURE")

    @pytest.mark.asyncio
    async def test_execute_failure(self, agent):
        """Test execute with no resume."""
        agent.ctx = Mock()
        agent.ctx.current_resume = None
        agent.ctx.JobDescription = None

        await agent.execute()

        agent.record_fail.assert_called_once()
        agent.add_signal.assert_called_with("ATS_FAILURE")

    def test_calculate_keyword_score_delegation(self, agent):
        """Test _calculate_keyword_score delegates to strategy."""
        resume = {"skills": "python"}
        job_desc = "Python developer"

        score = agent._calculate_keyword_score(resume, job_desc)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_heal_method(self, agent):
        """Test heal method returns proper structure."""
        violation = {"type": "test", "id": "123"}

        result = agent.heal(violation)

        assert "status" in result
        assert result["status"] == "skipped"
        assert "details" in result
        assert "artifacts" in result
        assert "errors" in result


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

        assert ATSCompatibilityAgent is not None

    def test_class_is_dataclass(self):
        """Test class is still a dataclass."""
        from dataclasses import is_dataclass

        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

        assert is_dataclass(ATSCompatibilityAgent)

    def test_inherits_from_rg_base(self):
        """Test class still inherits from RGAgentBase."""
        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        assert issubclass(ATSCompatibilityAgent, RGAgentBase)

    def test_execute_is_async(self):
        """Test execute method is still async."""
        import asyncio

        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

        assert asyncio.iscoroutinefunction(ATSCompatibilityAgent.execute)

    def test_heal_repository_signature(self):
        """Test heal_repository has correct signature."""
        import inspect

        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

        sig = inspect.signature(ATSCompatibilityAgent.heal_repository)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "dry_run" in params
        assert "execute" in params

    def test_heal_signature(self):
        """Test heal has correct signature."""
        import inspect

        from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent

        sig = inspect.signature(ATSCompatibilityAgent.heal)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "violation" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
