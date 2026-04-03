"""Test ADG grep ban gate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci import _adg_ci_gates
from ops_scripts.ci._adg_ci_gates import BANNED_PATTERNS
from ops_scripts.ci._adg_ci_gates import check_banned_patterns
from ops_scripts.ci._adg_ci_gates import scan_for_banned


@pytest.mark.unit
class TestAdgGrepBanGate:
    """Test ADG grep ban gate functionality."""




