"""
Unit Tests for BrandComplianceAgent Facade - Phase 2

Tests the facade conversion of BrandComplianceAgent including:
- Legacy signature compatibility
- Delegation to BrandValidatorStrategy
- Signal handling preservation
- Return type consistency
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import ValidationResult


class TestBrandValidatorStrategy:
    """Tests for BrandValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "forbidden_phrases": ["synergy", "leverage", "paradigm"],
            "power_verbs": ["achieved", "led", "developed", "implemented"],
            "compliance_rules": {
                "require_power_verbs_in_experience": True,
                "check_forbidden_phrases_all_sections": True,
                "case_sensitive_checking": False,
            },
        }

    @pytest.fixture
    def strategy(self, config):
        """Create BrandValidatorStrategy instance."""
        from apps_rg.reasoning.BrandComplianceAgent import BrandValidatorStrategy

        return BrandValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.FORBIDDEN_PHRASES == config["forbidden_phrases"]
        assert strategy.POWER_VERBS == config["power_verbs"]
        assert strategy.require_power_verbs is True
        assert strategy.case_sensitive is False

    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test execute with valid resume."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "Led team of 5 developers and achieved 20% improvement",
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
    async def test_execute_forbidden_phrase(self, strategy):
        """Test execute detects forbidden phrases."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "Created synergy between teams to leverage resources",
            "skills": "Python",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert any("Forbidden phrase" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_execute_missing_power_verbs(self, strategy):
        """Test execute suggests power verbs when missing."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "Worked on projects and did stuff",
            "skills": "Python",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        # Should pass but have suggestions
        assert any("action verbs" in s for s in result.suggestions)

    @pytest.mark.asyncio
    async def test_execute_with_power_verbs(self, strategy):
        """Test execute passes with power verbs."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        resume = {
            "experience": "Led team and achieved goals",
            "skills": "Python",
        }

        result = await strategy.execute(mock_agent, resume=resume)

        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert not any("action verbs" in s for s in result.suggestions)

    def test_to_string_str(self, strategy):
        """Test _to_string with string input."""
        result = strategy._to_string("test string")
        assert result == "test string"

    def test_to_string_list(self, strategy):
        """Test _to_string with list input."""
        result = strategy._to_string(["item1", "item2"])
        assert result == "item1 item2"

    def test_to_string_dict(self, strategy):
        """Test _to_string with dict input."""
        result = strategy._to_string({"key": "value"})
        assert "key" in result
        assert "value" in result


class TestBrandComplianceAgentFacade:
    """Tests for BrandComplianceAgent facade."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "forbidden_phrases": ["synergy"],
            "power_verbs": ["achieved"],
            "compliance_rules": {
                "require_power_verbs_in_experience": True,
                "check_forbidden_phrases_all_sections": True,
                "case_sensitive_checking": False,
            },
        }

    @pytest.fixture
    def agent(self, mock_config):
        """Create BrandComplianceAgent instance."""
        with patch("apps_rg.engines.BrandComplianceAgent.load_agent_config") as mock_load:
            mock_load.return_value = mock_config

            # Mock the parent class initialization
            with patch("apps_rg.utils.RGAgentBaseAgent.RGAgentBase.__post_init__"):
                from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

                agent = BrandComplianceAgent()
                agent.log = Mock()
                agent.record_pass = Mock()
                agent.record_fail = Mock()
                agent.add_signal = Mock()
                agent.remove_signal = Mock()
                return agent

    def test_legacy_attributes_preserved(self, agent):
        """Test legacy attributes are preserved."""
        assert hasattr(agent, "FORBIDDEN_PHRASES")
        assert hasattr(agent, "POWER_VERBS")
        assert hasattr(agent, "compliance_rules")
        assert hasattr(agent, "require_power_verbs")
        assert hasattr(agent, "check_forbidden_all_sections")
        assert hasattr(agent, "case_sensitive")

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        from apps_rg.reasoning.BrandComplianceAgent import BrandValidatorStrategy

        assert isinstance(agent._unified_strategy, BrandValidatorStrategy)

    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """Test execute with valid resume."""
        agent.ctx = Mock()
        agent.ctx.current_resume = {"experience": "Achieved great results"}

        await agent.execute()

        agent.record_pass.assert_called_once()
        agent.remove_signal.assert_called_with("BRAND_VIOLATION")

    @pytest.mark.asyncio
    async def test_execute_failure(self, agent):
        """Test execute with no resume."""
        agent.ctx = Mock()
        agent.ctx.current_resume = None

        await agent.execute()

        agent.record_fail.assert_called_once()
        agent.add_signal.assert_called_with("BRAND_VIOLATION")

    @pytest.mark.asyncio
    async def test_execute_forbidden_phrase_signal(self, agent):
        """Test execute adds signal on forbidden phrase."""
        agent.ctx = Mock()
        agent.ctx.current_resume = {"summary": "Creating synergy"}

        await agent.execute()

        agent.record_fail.assert_called_once()
        agent.add_signal.assert_called_with("BRAND_VIOLATION")

    def test_to_string_delegation(self, agent):
        """Test _to_string delegates to strategy."""
        result = agent._to_string("test")
        assert result == "test"

        result = agent._to_string(["a", "b"])
        assert result == "a b"

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
        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        assert BrandComplianceAgent is not None

    def test_class_is_dataclass(self):
        """Test class is still a dataclass."""
        from dataclasses import is_dataclass

        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        assert is_dataclass(BrandComplianceAgent)

    def test_inherits_from_rg_base(self):
        """Test class still inherits from RGAgentBase."""
        from apps_rg.utils.RGAgentBaseAgent import RGAgentBase

        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        assert issubclass(BrandComplianceAgent, RGAgentBase)

    def test_execute_is_async(self):
        """Test execute method is still async."""
        import asyncio

        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        assert asyncio.iscoroutinefunction(BrandComplianceAgent.execute)

    def test_heal_repository_signature(self):
        """Test heal_repository has correct signature."""
        import inspect

        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        sig = inspect.signature(BrandComplianceAgent.heal_repository)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "dry_run" in params
        assert "execute" in params

    def test_heal_signature(self):
        """Test heal has correct signature."""
        import inspect

        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        sig = inspect.signature(BrandComplianceAgent.heal)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "violation" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
