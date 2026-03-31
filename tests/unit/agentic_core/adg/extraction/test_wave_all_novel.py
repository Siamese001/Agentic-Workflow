"""Test WaveAllNovel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestWaveAllNovel:
    """Test WaveAllNovel functionality."""

    def test_wave_all_novel_imports(self):
        """Test wave_all_novel module imports."""
        from agentic_core import wave_all_novel
        assert wave_all_novel is not None

    def test_wave_all_novel_class(self):
        """Test WaveAllNovel class exists."""
        from agentic_core import WaveAllNovel
        assert WaveAllNovel is not None

    def test_wave_all_novel_callable(self):
        """Test wave_all_novel functions are callable."""
        from agentic_core import validate_wave_all_novel
        assert callable(validate_wave_all_novel)
