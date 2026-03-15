"""
Behavioral tests for TestQualityDetector.

Covers:
  VACUOUS_ASSERT    — assert True / always-true in any test function
  SOLE_TYPE_CHECK   — ALL assertions are isinstance/is-not-None/hasattr
  WRITE_WITHOUT_READ — write method called without read-back
  ADG stub exemption — *_adg.py skips SOLE_TYPE_CHECK and WRITE_WITHOUT_READ
  File-gate          — non-test files return empty results
  Whitelist          — guardian comment suppresses detection
  Category/severity  — metadata and enforcement level checks

Run with: pytest tests/guardian/test_test_quality_detector.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.test_quality_detector_validator import (
    TestQualityDetector,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def det():
    return TestQualityDetector(enforcement_level=EnforcementLevel.WARNING)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def _test_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "test_probe.py", content)


def _adg_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "test_probe_adg.py", content)


def _prod_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "module.py", content)


def _sub_patterns(result) -> set[str]:
    return {v.metadata.get("sub_pattern") for v in result.violations if not v.whitelisted}


# ===========================================================================
# VACUOUS_ASSERT — assert True
# ===========================================================================


class TestVacuousAssert:

    def test_detects_assert_true(self, det, tmp_path):
        code = """\
class TestFoo:
    def test_something(self):
        x = compute()
        assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_detects_assert_true_in_plain_function(self, det, tmp_path):
        code = """\
def test_standalone():
    result = do_thing()
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_severity_is_error(self, det, tmp_path):
        code = """\
def test_x():
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        errs = [v for v in result.violations if v.metadata.get("sub_pattern") == "VACUOUS_ASSERT"]
        assert errs
        assert all(v.severity == "error" for v in errs)

    def test_category_is_test_quality(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert all(v.category == AntiPatternCategory.TEST_QUALITY for v in result.violations)

    def test_metadata_has_test_function(self, det, tmp_path):
        code = "def test_my_func():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        v = next(v for v in result.violations if v.metadata.get("sub_pattern") == "VACUOUS_ASSERT")
        assert v.metadata["test_function"] == "test_my_func"

    def test_no_false_positive_assert_false(self, det, tmp_path):
        """assert False is a meaningful 'never reached' marker — not flagged by VACUOUS."""
        code = """\
def test_x():
    assert False, 'should not reach here'
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)

    def test_no_false_positive_real_assertion(self, det, tmp_path):
        code = """\
def test_x():
    x = compute()
    assert x == 42
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)

    def test_vacuous_also_in_adg_stub(self, det, tmp_path):
        """assert True is flagged even in *_adg.py stubs — no exemption for VACUOUS."""
        code = """\
def test_importable():
    assert True
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_guardian_comment_suppresses(self, det, tmp_path):
        code = """\
def test_noop_documented():
    # guardian: allow-test-quality -- operation is purely observational, no return value
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)


# ===========================================================================
# SOLE_TYPE_CHECK — all assertions are weak
# ===========================================================================


class TestSoleTypeCheck:

    def test_detects_only_isinstance(self, det, tmp_path):
        code = """\
def test_returns_something():
    result = compute()
    assert isinstance(result, dict)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_only_is_not_none(self, det, tmp_path):
        code = """\
def test_creates():
    obj = Factory().make()
    assert obj is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_only_hasattr(self, det, tmp_path):
        code = """\
def test_has_method():
    obj = build()
    assert hasattr(obj, 'run')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_mixed_weak_only(self, det, tmp_path):
        code = """\
def test_mixed_weak():
    obj = build()
    assert isinstance(obj, MyClass)
    assert obj is not None
    assert hasattr(obj, 'run')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_severity_is_warning(self, det, tmp_path):
        code = """\
def test_x():
    assert isinstance(x, int)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        stc = [v for v in result.violations if v.metadata.get("sub_pattern") == "SOLE_TYPE_CHECK"]
        assert stc
        assert all(v.severity == "warning" for v in stc)

    def test_no_false_positive_strong_assertion(self, det, tmp_path):
        """If any assertion is strong, no SOLE_TYPE_CHECK."""
        code = """\
def test_value():
    result = compute()
    assert isinstance(result, int)
    assert result > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_no_false_positive_equality(self, det, tmp_path):
        code = """\
def test_specific():
    result = compute()
    assert result == 42
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_no_false_positive_no_assertions(self, det, tmp_path):
        """Test with no assertions — SOLE_TYPE_CHECK requires at least one assert."""
        code = """\
def test_runs_without_error():
    compute()
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_adg_stub_exempt(self, det, tmp_path):
        """*_adg.py importability stubs must NOT trigger SOLE_TYPE_CHECK."""
        code = """\
def test_module_importable():
    assert _AVAILABLE is not None
    assert isinstance(MyClass, type) or MyClass is None
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_guardian_comment_suppresses(self, det, tmp_path):
        code = """\
# guardian: allow-test-quality -- smoke test only, full behavior tested elsewhere
def test_smoke():
    assert isinstance(obj, MyClass)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_metadata_assertion_count(self, det, tmp_path):
        code = """\
def test_count():
    assert isinstance(a, int)
    assert b is not None
    assert hasattr(c, 'x')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        v = next((v for v in result.violations if v.metadata.get("sub_pattern") == "SOLE_TYPE_CHECK"), None)
        assert v is not None
        assert v.metadata["assertion_count"] == 3


# ===========================================================================
# WRITE_WITHOUT_READ
# ===========================================================================


class TestWriteWithoutRead:

    def test_detects_create_no_read(self, det, tmp_path):
        code = """\
def test_creates_entity():
    bridge = GraphMemoryBridge()
    bridge.create_agent_entity('MyAgent')
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" in _sub_patterns(result)

    def test_detects_save_no_read(self, det, tmp_path):
        code = """\
def test_saves():
    store = Store()
    store.save(item)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" in _sub_patterns(result)

    def test_no_false_positive_write_then_search(self, det, tmp_path):
        code = """\
def test_persists():
    bridge = GraphMemoryBridge()
    bridge.create_agent_entity('MyAgent')
    results = bridge.search_entities('MyAgent')
    assert len(results) > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_no_false_positive_write_then_get(self, det, tmp_path):
        code = """\
def test_round_trip():
    store.save(item)
    fetched = store.get_item(item.id)
    assert fetched == item
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_no_false_positive_write_then_sqlite(self, det, tmp_path):
        code = """\
def test_sqlite_persists():
    bridge.create_agent_entity('X')
    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT * FROM entities').fetchall()
    assert len(rows) > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_adg_stub_exempt(self, det, tmp_path):
        code = """\
def test_create_method_exists():
    obj = MyClass()
    obj.create_entity('x')
    assert isinstance(obj, MyClass)
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_metadata_has_write_call(self, det, tmp_path):
        code = """\
def test_stores():
    db.insert_record(rec)
    assert db is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        v = next(
            (v for v in result.violations if v.metadata.get("sub_pattern") == "WRITE_WITHOUT_READ"),
            None,
        )
        assert v is not None
        assert v.metadata["write_call"] == "insert_record"

    def test_severity_is_warning(self, det, tmp_path):
        code = """\
def test_writes():
    store.save(x)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        wwr = [v for v in result.violations if v.metadata.get("sub_pattern") == "WRITE_WITHOUT_READ"]
        assert wwr
        assert all(v.severity == "warning" for v in wwr)


# ===========================================================================
# File-gate
# ===========================================================================


class TestFileGate:

    def test_production_file_skipped(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_prod_file(tmp_path, code))
        assert result.violation_count == 0

    def test_conftest_skipped(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        p = tmp_path / "conftest.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.violation_count == 0

    def test_test_prefix_scanned(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations

    def test_test_suffix_scanned(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        p = tmp_path / "module_test.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations


# ===========================================================================
# Multiple patterns in same file
# ===========================================================================


class TestMultiplePatterns:

    def test_multiple_violations_reported(self, det, tmp_path):
        code = """\
def test_vacuous():
    assert True

def test_type_only():
    obj = build()
    assert isinstance(obj, dict)

def test_write_no_read():
    store.add_item(x)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        patterns = _sub_patterns(result)
        assert "VACUOUS_ASSERT" in patterns
        assert "SOLE_TYPE_CHECK" in patterns
        assert "WRITE_WITHOUT_READ" in patterns


# ===========================================================================
# Category and wiring
# ===========================================================================


class TestCategoryAndWiring:

    def test_category_value(self):
        assert AntiPatternCategory.TEST_QUALITY == "test_quality"

    def test_detector_category_property(self):
        d = TestQualityDetector()
        assert d.category == AntiPatternCategory.TEST_QUALITY

    def test_default_enforcement_is_warning(self):
        d = TestQualityDetector()
        assert d.enforcement_level == EnforcementLevel.WARNING

    def test_to_dict_has_sub_pattern(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        d = result.violations[0].to_dict()
        assert "sub_pattern" in d["metadata"]
