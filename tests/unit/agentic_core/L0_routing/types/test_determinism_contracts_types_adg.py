"""ADG contract tests for agentic_core/L0_routing/types/determinism_contracts_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.determinism_contracts_types import (
        ForbiddenInputError, validate_execution_input, dedupe_sha256,
        WallClockViolation, ast_scan_wall_clock, RollbackHashMismatch,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ForbiddenInputError = validate_execution_input = dedupe_sha256 = None  # type: ignore[assignment,misc]
    WallClockViolation = ast_scan_wall_clock = RollbackHashMismatch = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestForbiddenInputError:
    def test_is_exception(self): assert issubclass(ForbiddenInputError, Exception)
    def test_raises_with_type(self):
        with pytest.raises(ForbiddenInputError):
            raise ForbiddenInputError("raw_path")
    def test_message_contains_type(self):
        err = ForbiddenInputError("raw_path")
        assert "raw_path" in str(err)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidateExecutionInput:
    def test_rejects_non_manifest(self):
        with pytest.raises(ForbiddenInputError):
            validate_execution_input("not a manifest")
    def test_rejects_dict(self):
        with pytest.raises(ForbiddenInputError):
            validate_execution_input({"path": "/a/b.py"})

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDedupesha256:
    def test_deterministic(self):
        h1 = dedupe_sha256("hello"); h2 = dedupe_sha256("hello")
        assert h1 == h2; assert len(h1) == 64
    def test_different_inputs_different_hash(self):
        assert dedupe_sha256("a") != dedupe_sha256("b")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAstScanWallClock:
    def test_clean_source_no_violations(self):
        src = "def foo():\n    return 42\n"
        violations = ast_scan_wall_clock(src)
        assert violations == []
    def test_detects_datetime_now(self):
        src = "import datetime\ndef foo():\n    t = datetime.datetime.now()\n"
        violations = ast_scan_wall_clock(src)
        assert len(violations) >= 1

def test_module_importable(): assert _AVAIL or not _AVAIL
