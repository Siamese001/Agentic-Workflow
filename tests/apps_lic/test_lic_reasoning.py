"""Tests for apps_lic reasoning components."""

from apps_lic.reasoning.LICValidationExecutor import (
    LICValidationExecutor,
)
from apps_lic.reasoning.MessageComplianceAgent import (
    MessageComplianceAgent,
)


class TestLICValidationExecutor:
    """Test LICValidationExecutor."""

    def test_executor_import(self):
        """Test that LICValidationExecutor can be imported."""
        assert LICValidationExecutor is not None

    def test_executor_class_exists(self):
        """Test that LICValidationExecutor class exists."""
        assert callable(LICValidationExecutor)


class TestMessageComplianceAgent:
    """Test MessageComplianceAgent."""

    def test_agent_import(self):
        """Test that MessageComplianceAgent can be imported."""
        assert MessageComplianceAgent is not None

    def test_agent_aliases_executor(self):
        """Test that MessageComplianceAgent remains the executor alias."""
        assert MessageComplianceAgent is LICValidationExecutor
