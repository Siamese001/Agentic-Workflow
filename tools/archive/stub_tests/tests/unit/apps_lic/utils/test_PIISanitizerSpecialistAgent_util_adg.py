"""Test PiisanitizerspecialistagentUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPiisanitizerspecialistagentUtilAdg:
    """Test PiisanitizerspecialistagentUtilAdg functionality."""

    def test_PIISanitizerSpecialistAgent_util_adg_imports(self):
        """Test PIISanitizerSpecialistAgent_util_adg module imports."""
        from agentic_core import PIISanitizerSpecialistAgent_util_adg

        assert PIISanitizerSpecialistAgent_util_adg is not None

    def test_PIISanitizerSpecialistAgent_util_adg_class(self):
        """Test PiisanitizerspecialistagentUtilAdg class exists."""
        from agentic_core import PiisanitizerspecialistagentUtilAdg

        assert PiisanitizerspecialistagentUtilAdg is not None

    def test_PIISanitizerSpecialistAgent_util_adg_callable(self):
        """Test PIISanitizerSpecialistAgent_util_adg functions are callable."""
        from agentic_core import validate_PIISanitizerSpecialistAgent_util_adg

        assert callable(validate_PIISanitizerSpecialistAgent_util_adg)
