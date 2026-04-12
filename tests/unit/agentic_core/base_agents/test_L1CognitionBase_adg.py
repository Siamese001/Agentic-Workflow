"""Test L1cognitionbaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL1cognitionbaseAdg:
    """Test L1cognitionbaseAdg functionality."""

    def test_L1CognitionBase_adg_imports(self):
        """Test L1CognitionBase_adg module imports."""
        from agentic_core import L1CognitionBase_adg

        assert L1CognitionBase_adg is not None

    def test_L1CognitionBase_adg_class(self):
        """Test L1cognitionbaseAdg class exists."""
        from agentic_core import L1cognitionbaseAdg

        assert L1cognitionbaseAdg is not None

    def test_L1CognitionBase_adg_callable(self):
        """Test L1CognitionBase_adg functions are callable."""
        from agentic_core import validate_L1CognitionBase_adg

        assert callable(validate_L1CognitionBase_adg)
