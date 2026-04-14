"""Test ADG G17 G22 completeness accuracy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG17G22CompletenessAccuracy:
    """Test ADG G17 G22 completeness accuracy functionality."""
