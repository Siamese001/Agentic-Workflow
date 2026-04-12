"""Test ReplayEnvelopeTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayEnvelopeTypesAdg:
    """Test ReplayEnvelopeTypesAdg functionality."""

    def test_replay_envelope_types_adg_imports(self):
        """Test replay_envelope_types_adg module imports."""
        from agentic_core import replay_envelope_types_adg

        assert replay_envelope_types_adg is not None

    def test_replay_envelope_types_adg_class(self):
        """Test ReplayEnvelopeTypesAdg class exists."""
        from agentic_core import ReplayEnvelopeTypesAdg

        assert ReplayEnvelopeTypesAdg is not None

    def test_replay_envelope_types_adg_callable(self):
        """Test replay_envelope_types_adg functions are callable."""
        from agentic_core import validate_replay_envelope_types_adg

        assert callable(validate_replay_envelope_types_adg)
