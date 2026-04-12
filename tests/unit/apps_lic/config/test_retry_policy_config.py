"""Test RetryPolicyConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRetryPolicyConfig:
    """Test RetryPolicyConfig functionality."""

    def test_retry_policy_config_imports(self):
        """Test retry_policy_config module imports."""
        from agentic_core import retry_policy_config

        assert retry_policy_config is not None

    def test_retry_policy_config_class(self):
        """Test RetryPolicyConfig class exists."""
        from agentic_core import RetryPolicyConfig

        assert RetryPolicyConfig is not None

    def test_retry_policy_config_callable(self):
        """Test retry_policy_config functions are callable."""
        from agentic_core import validate_retry_policy_config

        assert callable(validate_retry_policy_config)
