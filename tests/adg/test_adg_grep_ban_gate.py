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

    def test_grep_ban_gate_imports(self):
        """Test grep ban gate module imports."""
        assert _adg_ci_gates is not None

    def test_adg_grep_patterns_defined(self):
        """Test ADG grep ban patterns are defined."""
        assert isinstance(BANNED_PATTERNS, (list, tuple, set, frozenset, dict))

    def test_adg_grep_check_function(self):
        """Test ADG grep check function exists."""
        assert callable(check_banned_patterns)

    def test_adg_grep_scan_function(self):
        """Test ADG grep scan function exists."""
        assert callable(scan_for_banned)
