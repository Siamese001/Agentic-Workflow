"""Test ADG infusion phases verification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgInfusionPhasesVerification:
    """Test ADG infusion phases verification functionality."""
