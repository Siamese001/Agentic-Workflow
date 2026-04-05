"""Test AppSignalAggregation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppSignalAggregation:
    """Test AppSignalAggregation functionality."""

    def test_signal_aggregation_imports(self):
        """Test signal aggregation module imports."""
        from apps_shared import signal_aggregation
        assert signal_aggregation is not None

    def test_signal_aggregator_class(self):
        """Test signal aggregator class exists."""
        from apps_shared.signal_aggregation import SignalAggregator
        assert SignalAggregator is not None

    def test_aggregate_signals(self):
        """Test aggregate signals function."""
        from apps_shared.signal_aggregation import aggregate_signals
        assert callable(aggregate_signals)
