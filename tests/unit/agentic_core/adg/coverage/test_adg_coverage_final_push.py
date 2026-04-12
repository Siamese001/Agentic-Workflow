"""Test ADG coverage final push functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgCoverageFinalPush:
    """Test ADG coverage final push functionality."""


if __name__ == "__main__":
    unittest.main()
