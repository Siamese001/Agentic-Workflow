"""Test D0InjectionEngine functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestD0InjectionEngine:
    """Test D0InjectionEngine functionality."""

    def test_d0_injection_engine_imports(self):
        """Test d0_injection_engine module imports."""
        from agentic_core import d0_injection_engine
        assert d0_injection_engine is not None

    def test_d0_injection_engine_class(self):
        """Test D0InjectionEngine class exists."""
        from agentic_core import D0InjectionEngine
        assert D0InjectionEngine is not None

    def test_d0_injection_engine_callable(self):
        """Test d0_injection_engine functions are callable."""
        from agentic_core import validate_d0_injection_engine
        assert callable(validate_d0_injection_engine)
