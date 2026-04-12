"""Test RuntimeStateDigestAdvanced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeStateDigestAdvanced:
    """Test RuntimeStateDigestAdvanced functionality."""

    def test_runtime_state_digest_advanced_imports(self):
        """Test runtime_state_digest_advanced module imports."""
        from agentic_core import runtime_state_digest_advanced

        assert runtime_state_digest_advanced is not None

    def test_runtime_state_digest_advanced_class(self):
        """Test RuntimeStateDigestAdvanced class exists."""
        from agentic_core import RuntimeStateDigestAdvanced

        assert RuntimeStateDigestAdvanced is not None

    def test_runtime_state_digest_advanced_callable(self):
        """Test runtime_state_digest_advanced functions are callable."""
        from agentic_core import validate_runtime_state_digest_advanced

        assert callable(validate_runtime_state_digest_advanced)
