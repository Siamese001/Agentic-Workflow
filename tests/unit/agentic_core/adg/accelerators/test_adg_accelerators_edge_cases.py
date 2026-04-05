"""Test ADG accelerators edge cases."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorsEdgeCases:
    """Test ADG accelerators edge cases."""
