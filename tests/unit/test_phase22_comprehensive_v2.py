#!/usr/bin/env python3
"""
Comprehensive tests for Phase 2.2: MEDIUM severity broad exception fixes.
Tests follow windsurfrules §1.1-§1.8 requirements.

Uses patch('fix_medium_severity_swallowers.PROJECT_ROOT', ...) for proper
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
    from fix_medium_severity_swallowers import MediumSeveritySilentSwallowerFixer
    CAN_IMPORT = True
except ImportError as e:
    CAN_IMPORT = False

PATCH_TARGET = 'fix_medium_severity_swallowers.PROJECT_ROOT'


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase22EdgeCases:
    """§1.5 Edge case tests for Phase 2.2."""

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
            fixer = MediumSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0

    # ── Edge case 2: Malformed data (missing 'violations' key) ──────
    def test_malformed_data_missing_key(self, ws):
        """KeyError raised when report has no 'violations' key."""
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'invalid': 'data'}, f)
        with patch(PATCH_TARGET, ws):
            with pytest.raises(KeyError):
                MediumSeveritySilentSwallowerFixer()

    # ── Edge case 3: Violation with missing file_path field ─────────
    def test_missing_file_path_field(self, ws):
        """Violations without file_path are filtered to MEDIUM only; apply skips them."""
        violations = [
            {'line_number': 10, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'MEDIUM'},
            {'file_path': str(ws / 'ok.py'), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'data processing'}
        ]
        (ws / 'ok.py').write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 2  # both are MEDIUM
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert isinstance(result, dict)
            assert result['fixes_applied'] >= 0  # should not crash

    # ── Edge case 4: Non-existent file path ─────────────────────────
    def test_nonexistent_file_path(self, ws):
        """Fixer skips files that do not exist on disk."""
        violations = [
            {'file_path': str(ws / 'ghost.py'), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'phantom'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0
            assert 'errors' in result

    # ── Edge case 5: Unicode file paths ─────────────────────────────
    def test_unicode_file_path(self, ws):
        """Fixer handles Unicode file names without error."""
        ufile = ws / "tëst_ünïcødë.py"
        ufile.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(ufile), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'data processing'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 1
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

    # ── Edge case 6: Line number out of range ───────────────────────
    def test_line_number_out_of_range(self, ws):
        """Fixer skips violations whose line number exceeds file length."""
        src = ws / "short.py"
        src.write_text("x = 1\n")  # only 1 line
        violations = [
            {'file_path': str(src), 'line_number': 999,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'out of range'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0

    # ── Edge case 7: Only non-MEDIUM violations in report ───────────
    def test_only_non_medium_violations(self, ws):
        """Fixer loads zero violations when report contains only HIGH/LOW."""
        violations = [
            {'file_path': 'a.py', 'line_number': 1, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'HIGH'},
            {'file_path': 'b.py', 'line_number': 1, 'exception_type': 'SyntaxError',
             'handler_body': ['pass'], 'severity': 'LOW'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 0


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase22Determinism:
    """§1.7 Determinism tests for Phase 2.2."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def _make_workspace(self, ws, violations):
        for v in violations:
            fp = Path(v['file_path'])
            fp.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

    def test_identical_input_identical_output(self, ws):
        """Same violations file → same result dict (§1.7)."""
        src = ws / "det.py"
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'data processing'}
        ]
        self._make_workspace(ws, violations)

        with patch(PATCH_TARGET, ws):
            f1 = MediumSeveritySilentSwallowerFixer()
            r1 = f1.apply_fixes_to_all_remaining_violations()

        # Reset the file to original
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")

        with patch(PATCH_TARGET, ws):
            f2 = MediumSeveritySilentSwallowerFixer()
            r2 = f2.apply_fixes_to_all_remaining_violations()

        assert r1['fixes_applied'] == r2['fixes_applied']
        assert r1['errors'] == r2['errors']
        assert r1['remaining'] == r2['remaining']

    def test_exception_type_detection_consistency(self, ws):
        """_determine_specific_exception_types returns same list on repeat calls."""
        report = {'violations': []}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)
        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            t1 = fixer._determine_specific_exception_types("data processing error")
            t2 = fixer._determine_specific_exception_types("data processing error")
            assert t1 == t2


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase22FailClosed:
    """§1.8 Fail-closed tests for Phase 2.2."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_permission_error_on_read(self, ws):
        """Fixer records errors when file read raises PermissionError."""
        src = ws / "locked.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            with patch('pathlib.Path.read_text', side_effect=PermissionError("denied")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1

    def test_write_failure_does_not_claim_success(self, ws):
        """Fixer does not increment fixes_applied when write_text fails."""
        src = ws / "readonly.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'data processing'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            with patch('pathlib.Path.write_text', side_effect=IOError("disk full")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1
                assert result['fixes_applied'] == 0


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase22Integration:
    """End-to-end integration test for Phase 2.2."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_end_to_end_fixes(self, ws):
        """Full pipeline: load violations → apply fixes → verify file content."""
        files_and_contexts = [
            ("data_processor.py", "data processing error"),
            ("network_client.py", "network operation failed"),
            ("file_handler.py", "file read operation"),
            ("validator.py", "validation error"),
        ]
        violations = []
        for fname, ctx in files_and_contexts:
            fp = ws / fname
            fp.write_text("try:\n    operation()\nexcept Exception:\n    pass\n")
            violations.append({
                'file_path': str(fp), 'line_number': 3,
                'exception_type': 'Exception', 'handler_body': ['pass'],
                'severity': 'MEDIUM', 'context': ctx
            })
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()

        assert result['phase'] == '2.2'
        assert result['fixes_applied'] == 4
        assert result['errors'] == 0

        # Verify each file was actually modified
        for fname, _ in files_and_contexts:
            content = (ws / fname).read_text()
            assert content != "try:\n    operation()\nexcept Exception:\n    pass\n", \
                f"{fname} was not modified"

    def test_report_generation(self, ws):
        """generate_systematic_fix_report returns correct structure."""
        src = ws / "rpt.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'data processing'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        with patch(PATCH_TARGET, ws):
            fixer = MediumSeveritySilentSwallowerFixer()
            fixer.apply_fixes_to_all_remaining_violations()
            rpt = fixer.generate_systematic_fix_report()

        assert rpt['phase'] == '2.2'
        assert 'completion_percentage' in rpt
        assert 'fix_timestamp' in rpt
        assert rpt['total_medium_severity_violations'] >= 1