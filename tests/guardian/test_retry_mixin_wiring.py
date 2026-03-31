"""Test RetryMixinWiring functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRetryMixinWiring:
    """Test RetryMixinWiring functionality."""

    def test_retry_mixin_wiring_imports(self):
        """Test retry_mixin_wiring module imports."""
        from agentic_core import retry_mixin_wiring
        assert retry_mixin_wiring is not None

    def test_retry_mixin_wiring_class(self):
        """Test RetryMixinWiring class exists."""
        from agentic_core import RetryMixinWiring
        assert RetryMixinWiring is not None

    def test_retry_mixin_wiring_callable(self):
        """Test retry_mixin_wiring functions are callable."""
        from agentic_core import validate_retry_mixin_wiring
        assert callable(validate_retry_mixin_wiring)
