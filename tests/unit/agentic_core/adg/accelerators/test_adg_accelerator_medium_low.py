"""Test ADG accelerator medium/low priority functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorMediumLow:
    """Test ADG accelerator medium/low priority functionality."""
