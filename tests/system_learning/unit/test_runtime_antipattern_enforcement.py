"""Test RuntimeAntipatternEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeAntipatternEnforcement:
    """Test RuntimeAntipatternEnforcement functionality."""

    def test_runtime_antipattern_enforcement_imports(self):
        """Test runtime_antipattern_enforcement module imports."""
        from agentic_core import runtime_antipattern_enforcement

        assert runtime_antipattern_enforcement is not None

    def test_runtime_antipattern_enforcement_class(self):
        """Test RuntimeAntipatternEnforcement class exists."""
        from agentic_core import RuntimeAntipatternEnforcement

        assert RuntimeAntipatternEnforcement is not None

    def test_runtime_antipattern_enforcement_callable(self):
        """Test runtime_antipattern_enforcement functions are callable."""
        from agentic_core import validate_runtime_antipattern_enforcement

        assert callable(validate_runtime_antipattern_enforcement)
