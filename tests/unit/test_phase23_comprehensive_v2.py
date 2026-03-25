#!/usr/bin/env python3
"""
Comprehensive tests for Phase 2.3: LOW severity specific exception fixes.
Tests follow windsurfrules §1.1-§1.8 requirements.

Uses patch('fix_low_severity_swallowers.PROJECT_ROOT', ...) for proper
test isolation — matching the working Phase 2.1 pattern.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from fix_low_severity_swallowers import LowSeveritySilentSwallowerFixer
    CAN_IMPORT = True
except ImportError as e:
    CAN_IMPORT = False

PATCH_TARGET = 'fix_low_severity_swallowers.PROJECT_ROOT'


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase23EdgeCases:
    """§1.5 Edge case tests for Phase 2.3."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def _write_report(self, ws, violations_list):
        report = {'violations': violations_list}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

    # ── Edge case 1: Empty violations list ──────────────────────────
    def test_empty_violations_list(self, ws):
        """Fixer initialises cleanly with zero violations."""
        self._write_report(ws, [])
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0

    # ── Edge case 2: Malformed data (missing 'violations' key) ──────
    def test_malformed_data_missing_key(self, ws):
        """KeyError raised when report has no 'violations' key."""
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'invalid': 'data'}, f)
        with patch(PATCH_TARGET, ws):
            with pytest.raises(KeyError):
                LowSeveritySilentSwallowerFixer()

    # ── Edge case 3: Violation with missing file_path field ─────────
    def test_missing_file_path_field(self, ws):
        """Violations without file_path are still loaded; apply skips them."""
        violations = [
            {'line_number': 10, 'exception_type': 'SyntaxError',
             'handler_body': ['pass'], 'severity': 'LOW'},
            {'file_path': str(ws / 'ok.py'), 'line_number': 3,
             'exception_type': 'OSError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'file system error'}
        ]
        (ws / 'ok.py').write_text("try:\n    op()\nexcept OSError:\n    pass\n")
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 2
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert isinstance(result, dict)
            assert result['fixes_applied'] >= 0

    # ── Edge case 4: Non-existent file path ─────────────────────────
    def test_nonexistent_file_path(self, ws):
        """Fixer skips files that do not exist on disk."""
        violations = [
            {'file_path': str(ws / 'ghost.py'), 'line_number': 3,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'phantom'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0

    # ── Edge case 5: Unicode file paths ─────────────────────────────
    def test_unicode_file_path(self, ws):
        """Fixer handles Unicode file names without error."""
        ufile = ws / "tëst_ünïcødë.py"
        ufile.write_text("try:\n    op()\nexcept OSError:\n    pass\n")
        violations = [
            {'file_path': str(ufile), 'line_number': 3,
             'exception_type': 'OSError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'file system error'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 1
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

    # ── Edge case 6: Line number out of range ───────────────────────
    def test_line_number_out_of_range(self, ws):
        """Fixer skips violations whose line number exceeds file length."""
        src = ws / "short.py"
        src.write_text("x = 1\n")
        violations = [
            {'file_path': str(src), 'line_number': 999,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'out of range'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0

    # ── Edge case 7: Only non-LOW violations in report ──────────────
    def test_only_non_low_violations(self, ws):
        """Fixer loads zero violations when report contains only HIGH/MEDIUM."""
        violations = [
            {'file_path': 'a.py', 'line_number': 1, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'HIGH'},
            {'file_path': 'b.py', 'line_number': 1, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'MEDIUM'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 0

    # ── Edge case 8: Multiple exception types (comma-separated) ─────
    def test_multiple_exception_types(self, ws):
        """Fixer handles comma-separated exception types in violation data."""
        src = ws / "multi.py"
        src.write_text("try:\n    op()\nexcept (SyntaxError, UnicodeDecodeError):\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'SyntaxError, UnicodeDecodeError',
             'handler_body': ['pass'], 'severity': 'LOW',
             'context': 'parsing with encoding issues'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

    # ── Edge case 9: _SCENARIO_EXCEPTIONS sentinel type ─────────────
    def test_scenario_exceptions_type(self, ws):
        """Fixer handles the _SCENARIO_EXCEPTIONS sentinel type."""
        src = ws / "scenario.py"
        src.write_text("try:\n    op()\nexcept _SCENARIO_EXCEPTIONS:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': '_SCENARIO_EXCEPTIONS',
             'handler_body': ['pass'], 'severity': 'LOW',
             'context': 'test scenario exceptions'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase23Determinism:
    """§1.7 Determinism tests for Phase 2.3."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_identical_input_identical_output(self, ws):
        """Same violations file → same result dict (§1.7)."""
        src = ws / "det.py"
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'syntax parsing error'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        src.write_text("try:\n    op()\nexcept SyntaxError:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f1 = LowSeveritySilentSwallowerFixer()
            r1 = f1.apply_fixes_to_all_remaining_violations()

        src.write_text("try:\n    op()\nexcept SyntaxError:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f2 = LowSeveritySilentSwallowerFixer()
            r2 = f2.apply_fixes_to_all_remaining_violations()

        assert r1['fixes_applied'] == r2['fixes_applied']
        assert r1['errors'] == r2['errors']
        assert r1['remaining'] == r2['remaining']

    def test_exception_strategy_consistency(self, ws):
        """_determine_exception_fix_strategy returns same dict on repeat calls."""
        report = {'violations': []}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            s1 = fixer._determine_exception_fix_strategy('SyntaxError', 'parsing')
            s2 = fixer._determine_exception_fix_strategy('SyntaxError', 'parsing')
            assert s1 == s2

    def test_all_known_exception_strategies(self, ws):
        """Each known exception type returns a strategy with 'action' key."""
        report = {'violations': []}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)
        known_types = [
            'SyntaxError', 'OSError', 'UnicodeDecodeError', 'PermissionError',
            'RuntimeError', 'FileNotFoundError', 'ValueError', 'TypeError',
            'KeyError', 'AttributeError', 'IndexError', '_SCENARIO_EXCEPTIONS'
        ]
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            for exc_type in known_types:
                strategy = fixer._determine_exception_fix_strategy(exc_type, 'test context')
                assert isinstance(strategy, dict), f"Strategy for {exc_type} is not a dict"
                assert 'action' in strategy, f"Strategy for {exc_type} missing 'action'"


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase23FailClosed:
    """§1.8 Fail-closed tests for Phase 2.3."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_permission_error_on_read(self, ws):
        """Fixer records errors when file read raises PermissionError."""
        src = ws / "locked.py"
        src.write_text("try:\n    op()\nexcept SyntaxError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'test'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            with patch('pathlib.Path.read_text', side_effect=PermissionError("denied")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1

    def test_write_failure_does_not_claim_success(self, ws):
        """Fixer does not increment fixes_applied when write_text fails."""
        src = ws / "readonly.py"
        src.write_text("try:\n    op()\nexcept OSError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'OSError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'file system error'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            with patch('pathlib.Path.write_text', side_effect=IOError("disk full")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1
                assert result['fixes_applied'] == 0


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase23Integration:
    """End-to-end integration test for Phase 2.3."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_end_to_end_fixes(self, ws):
        """Full pipeline: load violations → apply fixes → verify file content."""
        files_and_types = [
            ("syntax_handler.py", "SyntaxError", "except SyntaxError:\n    pass"),
            ("file_handler.py", "OSError", "except OSError:\n    pass"),
            ("encoding_handler.py", "UnicodeDecodeError", "except UnicodeDecodeError:\n    pass"),
            ("perm_handler.py", "PermissionError", "except PermissionError:\n    pass"),
        ]
        violations = []
        for fname, exc, _ in files_and_types:
            fp = ws / fname
            fp.write_text(f"try:\n    operation()\nexcept {exc}:\n    pass\n")
            violations.append({
                'file_path': str(fp), 'line_number': 3,
                'exception_type': exc, 'handler_body': ['pass'],
                'severity': 'LOW', 'context': f'{exc} handling'
            })
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()

        assert result['phase'] == '2.3'
        assert result['fixes_applied'] == 4
        assert result['errors'] == 0

        # Verify each file was actually modified (guardian comment added)
        for fname, exc, _ in files_and_types:
            content = (ws / fname).read_text()
            assert "# guardian:" in content, f"{fname} missing guardian comment"

    def test_report_generation(self, ws):
        """generate_systematic_fix_report returns correct structure."""
        src = ws / "rpt.py"
        src.write_text("try:\n    op()\nexcept SyntaxError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'syntax parsing error'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            fixer.apply_fixes_to_all_remaining_violations()
            rpt = fixer.generate_systematic_fix_report()

        assert rpt['phase'] == '2.3'
        assert 'completion_percentage' in rpt
        assert 'fix_timestamp' in rpt
        assert 'exception_type_distribution' in rpt
        assert rpt['total_low_severity_violations'] >= 1
