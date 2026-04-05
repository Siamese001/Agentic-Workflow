"""Test ADG G7 G16 creative extensions functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG7G16CreativeExtensions:
    """Test ADG G7 G16 creative extensions functionality."""
