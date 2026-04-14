"""Test ADG G23 G27 completeness accuracy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG23G27CompletenessAccuracy:
    """Test ADG G23 G27 completeness accuracy functionality."""
