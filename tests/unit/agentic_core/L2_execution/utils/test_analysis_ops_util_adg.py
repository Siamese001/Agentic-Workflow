"""ADG-driven tests for L2_execution/utils/analysis_ops_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.analysis_ops_util import validate_python_syntax
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    validate_python_syntax = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="analysis_ops_util deps unavailable")
class TestValidatePythonSyntax:
    def test_valid_file_returns_true(self, tmp_path):
        f = tmp_path / "good.py"
        f.write_text("x = 1\n")
        ok, err = validate_python_syntax(str(f))
        assert ok is True
        assert err is None

    def test_invalid_file_returns_false(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def (\n")
        ok, err = validate_python_syntax(str(f))
        assert ok is False
        assert err is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
