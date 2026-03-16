"""
Behavioral tests for TestSilentSkipDetector.

Covers:
  - BROAD_EXCEPT_AVAILABILITY_FLAG detection (positive cases)
  - Safe except ImportError pattern (negative / no false-positive)
  - Bare except, except BaseException (positive)
  - Tuple except (E1, E2) variants
  - Non-test files are skipped entirely
  - Guardian exemption comment suppresses detection
  - Severity is always error
  - Category is TEST_SILENT_SKIP
  - ADG integration: AntiPatternCategory enum has TEST_SILENT_SKIP

Run with: pytest tests/guardian/test_test_silent_skip_detector.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_test_silent_skip_detector")
_emit_applies_guardrail("p0", "test_test_silent_skip_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_test_silent_skip_detector", "policy_binding")
_emit_snapshots_state("p0", "test_test_silent_skip_detector", "state_snapshot")
emit_replay_key("p0", "test_test_silent_skip_detector")
emit_determinism_digest("p0", "test_test_silent_skip_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def det():
    return TestSilentSkipDetector(enforcement_level=EnforcementLevel.HARD_BLOCK)


@pytest.fixture
def test_py(tmp_path):
    """Write content into a test_probe.py file (test file name)."""

    def _make(content: str) -> Path:
        p = tmp_path / "test_probe.py"
        p.write_text(content, encoding="utf-8")
        return p

    return _make


@pytest.fixture
def prod_py(tmp_path):
    """Write content into a production (non-test) file."""

    def _make(content: str) -> Path:
        p = tmp_path / "my_module.py"
        p.write_text(content, encoding="utf-8")
        return p

    return _make


def _sub_patterns(result):
    return {v.metadata.get("sub_pattern") for v in result.violations if not v.whitelisted}


# ===========================================================================
# Positive cases — should detect
# ===========================================================================


class TestBroadExceptAvailabilityFlag:
    """except Exception: _AVAILABLE = False must be flagged."""

    def test_detects_except_exception(self, det, test_py):
        code = """\
try:
    from some.module import Foo, NONEXISTENT
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_bare_except(self, det, test_py):
        code = """\
try:
    from some.module import Foo
    _AVAILABLE = True
except:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_except_base_exception(self, det, test_py):
        code = """\
try:
    from some.module import Foo
    _AVAILABLE = True
except BaseException:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_except_exception_with_alias(self, det, test_py):
        """except Exception as exc: _AVAILABLE = False must also be flagged."""
        code = """\
try:
    from some.module import Foo
    _AVAILABLE = True
except Exception as exc:
    _AVAILABLE = False
    Foo = None
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_various_flag_names(self, det, tmp_path):
        """All availability flag suffixes must be detected."""
        for flag in ("_AVAILABLE", "_AVAIL", "_ENABLED", "_LOADED", "_IMPORTED", "_READY"):
            code = f"""\
try:
    from mod import X
    {flag} = True
except Exception:
    {flag} = False
"""
            p = tmp_path / f"test_{flag.lower()}.py"
            p.write_text(code, encoding="utf-8")
            result = det.scan_file(p)
            assert result.has_violations, f"Should flag {flag} = False under except Exception"

    def test_detects_custom_availability_flag(self, det, test_py):
        """Custom names ending in _AVAILABLE must also be caught."""
        code = """\
try:
    from mod import X
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations

    def test_metadata_flag_name_captured(self, det, test_py):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        v = result.violations[0]
        assert v.metadata["flag"] == "_AVAILABLE"
        assert "Exception" in v.metadata["caught"]

    def test_error_severity(self, det, test_py):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert all(v.severity == "error" for v in result.violations if not v.whitelisted)

    def test_category_is_test_silent_skip(self, det, test_py):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert all(v.category == AntiPatternCategory.TEST_SILENT_SKIP for v in result.violations)

    def test_suggested_fix_mentions_import_error(self, det, test_py):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        v = result.violations[0]
        assert "ImportError" in v.suggested_fix

    def test_real_world_adg_stub_pattern(self, det, test_py):
        """The exact pattern used in 1569 ADG stubs must be flagged."""
        code = """\
from __future__ import annotations
import pytest

try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import (
        EntityDefinition,
        GraphMemoryBridge,
        RelationDefinition,
        MAX_RETRIES,
        DEFAULT_SLEEP,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EntityDefinition = None
    GraphMemoryBridge = None
    RelationDefinition = None

@pytest.mark.skipif(not _AVAILABLE, reason="deps unavailable")
class TestGraphMemoryBridgeImportability:
    def test_module_importable(self):
        assert _AVAILABLE
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)


# ===========================================================================
# Negative cases — must NOT detect (no false positives)
# ===========================================================================


class TestNoFalsePositives:
    """Safe patterns must not be flagged."""

    def test_safe_except_import_error(self, det, test_py):
        """except ImportError: _AVAILABLE = False — the correct pattern."""
        code = """\
try:
    from some.module import Foo
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Foo = None
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_safe_except_module_not_found(self, det, test_py):
        """except ModuleNotFoundError: _AVAILABLE = False — also acceptable."""
        code = """\
try:
    import optional_dep
    _AVAILABLE = True
except ModuleNotFoundError:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_safe_except_tuple_all_import_errors(self, det, test_py):
        """except (ImportError, ModuleNotFoundError): — all safe."""
        code = """\
try:
    import optional_dep
    _AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_no_flag_no_detection(self, det, test_py):
        """except Exception: without availability flag — must not flag."""
        code = """\
try:
    x = int("bad")
except Exception:
    x = 0
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_except_exception_sets_flag_to_none_not_false(self, det, test_py):
        """Setting flag to None (not False) — must not flag."""
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    X = None
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_except_import_error_raises(self, det, test_py):
        """except ImportError: raise — no false positive."""
        code = """\
try:
    from mod import X
except ImportError as exc:
    raise RuntimeError("mod required") from exc
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations


# ===========================================================================
# Test-file gate — non-test files must be skipped entirely
# ===========================================================================


class TestFileGate:
    """Non-test files must return empty results regardless of content."""

    def test_production_file_skipped(self, det, prod_py):
        """A production file with the dangerous pattern must NOT be scanned."""
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(prod_py(code))
        assert result.violation_count == 0

    def test_conftest_skipped(self, det, tmp_path):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "conftest.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.violation_count == 0

    def test_test_suffix_file_scanned(self, det, tmp_path):
        """Files ending in _test.py must also be scanned."""
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "module_test.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations

    def test_test_prefix_file_scanned(self, det, tmp_path):
        """Files starting with test_ must be scanned."""
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "test_my_module.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations


# ===========================================================================
# Whitelist / guardian exemption
# ===========================================================================


class TestWhitelistMechanics:

    def test_guardian_comment_suppresses(self, det, test_py):
        code = """\
# guardian: allow-test-silent-skip -- optional GPU dep, absent in CPU CI
try:
    from gpu_module import CUDA
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_wrong_guardian_type_does_not_suppress(self, det, test_py):
        """A guardian comment for a different type must NOT suppress this violation."""
        code = """\
# guardian: allow-silent-degradation -- wrong type
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations

    def test_distant_guardian_does_not_suppress(self, det, test_py):
        """A guardian comment >3 lines above must NOT suppress."""
        code = """\
# guardian: allow-test-silent-skip -- too far above



try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations


# ===========================================================================
# Category enum and detector wiring
# ===========================================================================


class TestCategoryAndWiring:

    def test_category_value(self):
        assert AntiPatternCategory.TEST_SILENT_SKIP == "test_silent_skip"

    def test_detector_category_property(self):
        d = TestSilentSkipDetector()
        assert d.category == AntiPatternCategory.TEST_SILENT_SKIP

    def test_to_dict_has_sub_pattern(self, det, test_py):
        code = """\
try:
    from mod import X
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        d = result.violations[0].to_dict()
        assert d["metadata"]["sub_pattern"] == "BROAD_EXCEPT_AVAILABILITY_FLAG"

    def test_enforcement_level_hard_block_by_default(self):
        d = TestSilentSkipDetector()
        assert d.enforcement_level == EnforcementLevel.HARD_BLOCK
