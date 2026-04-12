"""Test FusionAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFusionAdg:
    """Test FusionAdg functionality."""

    def test_fusion_adg_imports(self):
        """Test fusion_adg module imports."""
        from agentic_core import fusion_adg

        assert fusion_adg is not None

    def test_fusion_adg_class(self):
        """Test FusionAdg class exists."""
        from agentic_core import FusionAdg

        assert FusionAdg is not None

    def test_fusion_adg_callable(self):
        """Test fusion_adg functions are callable."""
        from agentic_core import validate_fusion_adg

        assert callable(validate_fusion_adg)
