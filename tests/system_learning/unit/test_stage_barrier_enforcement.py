"""Test StageBarrierEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStageBarrierEnforcement:
    """Test StageBarrierEnforcement functionality."""

    def test_stage_barrier_enforcement_imports(self):
        """Test stage_barrier_enforcement module imports."""
        from agentic_core import stage_barrier_enforcement

        assert stage_barrier_enforcement is not None

    def test_stage_barrier_enforcement_class(self):
        """Test StageBarrierEnforcement class exists."""
        from agentic_core import StageBarrierEnforcement

        assert StageBarrierEnforcement is not None

    def test_stage_barrier_enforcement_callable(self):
        """Test stage_barrier_enforcement functions are callable."""
        from agentic_core import validate_stage_barrier_enforcement

        assert callable(validate_stage_barrier_enforcement)
