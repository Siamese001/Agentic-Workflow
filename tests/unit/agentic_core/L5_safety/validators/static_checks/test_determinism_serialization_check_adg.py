"""Test DeterminismSerializationCheckAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismSerializationCheckAdg:
    """Test DeterminismSerializationCheckAdg functionality."""

    def test_determinism_serialization_check_adg_imports(self):
        """Test determinism_serialization_check_adg module imports."""
        from agentic_core import determinism_serialization_check_adg

        assert determinism_serialization_check_adg is not None

    def test_determinism_serialization_check_adg_class(self):
        """Test DeterminismSerializationCheckAdg class exists."""
        from agentic_core import DeterminismSerializationCheckAdg

        assert DeterminismSerializationCheckAdg is not None

    def test_determinism_serialization_check_adg_callable(self):
        """Test determinism_serialization_check_adg functions are callable."""
        from agentic_core import validate_determinism_serialization_check_adg

        assert callable(validate_determinism_serialization_check_adg)
