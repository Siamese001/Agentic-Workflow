"""Test L6observabilitybaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL6observabilitybaseAdg:
    """Test L6observabilitybaseAdg functionality."""

    def test_L6ObservabilityBase_adg_imports(self):
        """Test L6ObservabilityBase_adg module imports."""
        from agentic_core import L6ObservabilityBase_adg

        assert L6ObservabilityBase_adg is not None

    def test_L6ObservabilityBase_adg_class(self):
        """Test L6observabilitybaseAdg class exists."""
        from agentic_core import L6observabilitybaseAdg

        assert L6observabilitybaseAdg is not None

    def test_L6ObservabilityBase_adg_callable(self):
        """Test L6ObservabilityBase_adg functions are callable."""
        from agentic_core import validate_L6ObservabilityBase_adg

        assert callable(validate_L6ObservabilityBase_adg)
