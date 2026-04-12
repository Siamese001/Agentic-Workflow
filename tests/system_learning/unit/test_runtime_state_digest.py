"""Test RuntimeStateDigest functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeStateDigest:
    """Test RuntimeStateDigest functionality."""

    def test_runtime_state_digest_imports(self):
        """Test runtime_state_digest module imports."""
        from agentic_core import runtime_state_digest

        assert runtime_state_digest is not None

    def test_runtime_state_digest_class(self):
        """Test RuntimeStateDigest class exists."""
        from agentic_core import RuntimeStateDigest

        assert RuntimeStateDigest is not None

    def test_runtime_state_digest_callable(self):
        """Test runtime_state_digest functions are callable."""
        from agentic_core import validate_runtime_state_digest

        assert callable(validate_runtime_state_digest)
