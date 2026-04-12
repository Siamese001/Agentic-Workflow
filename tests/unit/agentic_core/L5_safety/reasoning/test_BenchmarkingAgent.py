"""Test Benchmarkingagent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBenchmarkingagent:
    """Test Benchmarkingagent functionality."""

    def test_BenchmarkingAgent_imports(self):
        """Test BenchmarkingAgent module imports."""
        from agentic_core import BenchmarkingAgent

        assert BenchmarkingAgent is not None

    def test_BenchmarkingAgent_class(self):
        """Test Benchmarkingagent class exists."""
        from agentic_core import Benchmarkingagent

        assert Benchmarkingagent is not None

    def test_BenchmarkingAgent_callable(self):
        """Test BenchmarkingAgent functions are callable."""
        from agentic_core import validate_BenchmarkingAgent

        assert callable(validate_BenchmarkingAgent)
