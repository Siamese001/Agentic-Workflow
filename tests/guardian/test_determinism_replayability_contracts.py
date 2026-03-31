"""Test DeterminismReplayabilityContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismReplayabilityContracts:
    """Test DeterminismReplayabilityContracts functionality."""

    def test_determinism_replayability_contracts_imports(self):
        """Test determinism_replayability_contracts module imports."""
        from agentic_core import determinism_replayability_contracts
        assert determinism_replayability_contracts is not None

    def test_determinism_replayability_contracts_class(self):
        """Test DeterminismReplayabilityContracts class exists."""
        from agentic_core import DeterminismReplayabilityContracts
        assert DeterminismReplayabilityContracts is not None

    def test_determinism_replayability_contracts_callable(self):
        """Test determinism_replayability_contracts functions are callable."""
        from agentic_core import validate_determinism_replayability_contracts
        assert callable(validate_determinism_replayability_contracts)
