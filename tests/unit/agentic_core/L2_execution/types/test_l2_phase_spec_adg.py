"""Test L2PhaseSpecAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL2PhaseSpecAdg:
    """Test L2PhaseSpecAdg functionality."""

    def test_l2_phase_spec_adg_imports(self):
        """Test l2_phase_spec_adg module imports."""
        from agentic_core import l2_phase_spec_adg

        assert l2_phase_spec_adg is not None

    def test_l2_phase_spec_adg_class(self):
        """Test L2PhaseSpecAdg class exists."""
        from agentic_core import L2PhaseSpecAdg

        assert L2PhaseSpecAdg is not None

    def test_l2_phase_spec_adg_callable(self):
        """Test l2_phase_spec_adg functions are callable."""
        from agentic_core import validate_l2_phase_spec_adg

        assert callable(validate_l2_phase_spec_adg)
