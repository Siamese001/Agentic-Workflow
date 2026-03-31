"""Test EnforcementModeTransitionMatrix functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEnforcementModeTransitionMatrix:
    """Test EnforcementModeTransitionMatrix functionality."""

    def test_enforcement_mode_transition_matrix_imports(self):
        """Test enforcement_mode_transition_matrix module imports."""
        from agentic_core import enforcement_mode_transition_matrix
        assert enforcement_mode_transition_matrix is not None

    def test_enforcement_mode_transition_matrix_class(self):
        """Test EnforcementModeTransitionMatrix class exists."""
        from agentic_core import EnforcementModeTransitionMatrix
        assert EnforcementModeTransitionMatrix is not None

    def test_enforcement_mode_transition_matrix_callable(self):
        """Test enforcement_mode_transition_matrix functions are callable."""
        from agentic_core import validate_enforcement_mode_transition_matrix
        assert callable(validate_enforcement_mode_transition_matrix)
