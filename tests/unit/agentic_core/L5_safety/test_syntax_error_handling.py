"""Test SyntaxErrorHandling functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSyntaxErrorHandling:
    """Test SyntaxErrorHandling functionality."""

    def test_syntax_error_handling_imports(self):
        """Test syntax_error_handling module imports."""
        from agentic_core import syntax_error_handling
        assert syntax_error_handling is not None

    def test_syntax_error_handling_class(self):
        """Test SyntaxErrorHandling class exists."""
        from agentic_core import SyntaxErrorHandling
        assert SyntaxErrorHandling is not None

    def test_syntax_error_handling_callable(self):
        """Test syntax_error_handling functions are callable."""
        from agentic_core import validate_syntax_error_handling
        assert callable(validate_syntax_error_handling)
