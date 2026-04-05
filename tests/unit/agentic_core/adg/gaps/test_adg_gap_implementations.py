"""Test ADG gap remediation P0 P4 functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgGapRemediationP0P4:
    """Test ADG gap remediation P0 P4 functionality."""
