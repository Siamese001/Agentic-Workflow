"""Test ADG accelerator hardening functionality."""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorHardening:
    """Test ADG accelerator hardening functionality."""

    def test_p0_gap_files_returns_list(self):
        """Test get_gap_files returns a list of files."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG, get_gap_files

        # Mock should return list even if no DB found
        result = get_gap_files("L3", DIMENSION_CONFIG["evidence"])
        assert isinstance(result, list)

    def test_p0_has_wirable_functions_detects_functions(self):
        """Test _has_wirable_functions detects wirable functions."""
        from tools.p0_batch_wirer import _has_wirable_functions

        # Source with substantial function
        src = """
def substantial():
    x = 1
    y = 2
    return x + y
"""
        assert _has_wirable_functions(src) is True

    def test_p0_has_wirable_functions_skips_short(self):
        """Test _has_wirable_functions skips short functions."""
        from tools.p0_batch_wirer import _has_wirable_functions

        # Source with short function
        src = """
def short(): return 1
"""
        assert _has_wirable_functions(src) is False

    def test_p0_has_wirable_handles_syntax_error(self):
        """Test _has_wirable_functions handles syntax errors gracefully."""
        from tools.p0_batch_wirer import _has_wirable_functions

        result = _has_wirable_functions("def broken(: pass")
        assert result is False

    def test_p1_should_process_file_filters_extensions(self):
        """Test should_process_file filters by extension."""
        from tools.p1_batch_wire import should_process_file

        assert should_process_file(Path("test.py")) is True
        assert should_process_file(Path("test.txt")) is False
        assert should_process_file(Path("test.md")) is False

    def test_p1_should_process_file_excludes_directories(self):
        """Test should_process_file excludes certain directories."""
        from tools.p1_batch_wire import should_process_file

        assert should_process_file(Path("__pycache__/test.py")) is False
        assert should_process_file(Path(".git/hook.py")) is False
        assert should_process_file(Path("artifacts/data.py")) is False

    def test_p0_dimension_config_evidence_has_check_edges(self):
        """Test evidence dimension has required check edges."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG

        config = DIMENSION_CONFIG["evidence"]
        edges = config["check_edges"]

        assert "records_execution_trace" in edges
        assert "emits_replay_key" in edges
        assert "emits_determinism_digest" in edges

    def test_p0_dimension_config_governance_has_guardrail(self):
        """Test governance dimension includes guardrail edges."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG

        config = DIMENSION_CONFIG["governance"]
        edges = config["check_edges"]

        assert "applies_guardrail" in edges
        assert "validated_by_safety_plane" in edges
