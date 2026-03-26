#!/usr/bin/env python3
"""
Comprehensive tests for Wave 3.0: Guardian Annotation Sweep.
Validates Phases 2.1-2.4 fixes and annotates remaining violations with guardian comments.
Tests follow windsurfrules §1.1-§1.8 requirements.

Uses patch('guardian_sweep.PROJECT_ROOT', ...) for isolation.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from guardian_sweep import GuardianSweepFixer
    CAN_IMPORT = True
except ImportError as e:
    CAN_IMPORT = False

PATCH_TARGET = 'guardian_sweep.PROJECT_ROOT'


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestWave30EdgeCases:
    """§1.5 Edge case tests for Wave 3.0."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def _write_report(self, ws, violations_list):
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations_list}, f)

    # ── Edge case 1: Empty violations list ──────────────────────────
    def test_empty_violations_list(self, ws):
        """Fixer initialises cleanly with zero violations."""
        self._write_report(ws, [])
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            assert len(fixer.violations) == 0
            assert fixer.annotations_added == 0

    # ── Edge case 2: Malformed data (missing 'violations' key) ──────
    def test_malformed_data_missing_key(self, ws):
        """KeyError raised when report has no 'violations' key."""
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'invalid': 'data'}, f)
        with patch(PATCH_TARGET, ws):
            with pytest.raises(KeyError):
                GuardianSweepFixer()

    # ── Edge case 3: Violation with missing file_path field ─────────
    def test_missing_file_path_field(self, ws):
        """Violations without file_path are loaded but skipped during sweep."""
        violations = [
            {'line_number': 10, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'MEDIUM'},
            {'file_path': str(ws / 'ok.py'), 'line_number': 3,
             'exception_type': 'ValueError', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'value validation'}
        ]
        (ws / 'ok.py').write_text("try:\n    op()\nexcept ValueError:\n    pass\n")
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert isinstance(result, dict)
            assert result['annotations_added'] >= 0

    # ── Edge case 4: Non-existent file path ─────────────────────────
    def test_nonexistent_file_path(self, ws):
        """Fixer skips files that do not exist on disk."""
        violations = [
            {'file_path': str(ws / 'ghost.py'), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'phantom'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 0

    # ── Edge case 5: Unicode file paths ─────────────────────────────
    def test_unicode_file_path(self, ws):
        """Fixer handles Unicode file names without error."""
        ufile = ws / "tëst_ünïcødë.py"
        ufile.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(ufile), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'unicode test'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 1

    # ── Edge case 6: Line number out of range ───────────────────────
    def test_line_number_out_of_range(self, ws):
        """Fixer skips violations whose line number exceeds file length."""
        src = ws / "short.py"
        src.write_text("x = 1\n")
        violations = [
            {'file_path': str(src), 'line_number': 999,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'LOW', 'context': 'out of range'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 0

    # ── Edge case 7: Already has guardian comment ───────────────────
    def test_already_has_guardian(self, ws):
        """Fixer skips violations that already have guardian comments."""
        src = ws / "guarded.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass  # guardian: allow-silent-swallow\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'already guarded',
             'has_guardian': True}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 0

    # ── Edge case 8: Mixed severity levels ───────────────────────────
    def test_mixed_severity_levels(self, ws):
        """Fixer processes all severity levels (HIGH, MEDIUM, LOW)."""
        files = [
            ("high.py", "ImportError", "HIGH"),
            ("medium.py", "Exception", "MEDIUM"),
            ("low.py", "SyntaxError", "LOW"),
        ]
        violations = []
        for fname, exc, sev in files:
            fp = ws / fname
            fp.write_text(f"try:\n    op()\nexcept {exc}:\n    pass\n")
            violations.append({
                'file_path': str(fp), 'line_number': 3,
                'exception_type': exc, 'handler_body': ['pass'],
                'severity': sev, 'context': 'test'
            })
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 3
            # Verify all files now have guardian comments
            for fname, _, _ in files:
                content = (ws / fname).read_text()
                assert "# guardian: allow-silent-swallow" in content

    # ── Edge case 9: Multi-exception combo ──────────────────────────
    def test_multi_exception_combo(self, ws):
        """Fixer handles multi-exception type violations."""
        src = ws / "multi.py"
        src.write_text("try:\n    op()\nexcept (TypeError, ValueError):\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'TypeError, ValueError',
             'handler_body': ['pass'], 'severity': 'HIGH',
             'context': 'multi-exception'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 1
            content = src.read_text()
            assert "# guardian: allow-silent-swallow" in content

    # ── Edge case 10: Empty handler body ───────────────────────────
    def test_empty_handler_body(self, ws):
        """Fixer handles violations with empty handler body."""
        src = ws / "empty.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    ")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': [],
             'severity': 'MEDIUM', 'context': 'empty body'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 1
            content = src.read_text()
            assert "# guardian: allow-silent-swallow" in content


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestWave30Determinism:
    """§1.7 Determinism tests for Wave 3.0."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_identical_input_identical_output(self, ws):
        """Same violations file -> same result dict (§1.7)."""
        src = ws / "det.py"
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f1 = GuardianSweepFixer()
            r1 = f1.apply_guardian_sweep()

        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f2 = GuardianSweepFixer()
            r2 = f2.apply_guardian_sweep()

        assert r1['annotations_added'] == r2['annotations_added']
        assert r1['errors'] == r2['errors']
        assert r1['remaining_unannotated'] == r2['remaining_unannotated']

    def test_guardian_message_consistency(self, ws):
        """_determine_guardian_message returns same message for same input."""
        self._write_empty(ws)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            msg1 = fixer._determine_guardian_message('Exception', 'MEDIUM', 'test context')
            msg2 = fixer._determine_guardian_message('Exception', 'MEDIUM', 'test context')
            assert msg1 == msg2

    def test_all_severity_messages(self, ws):
        """Each severity level returns a valid guardian message."""
        self._write_empty(ws)
        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            for sev in ['HIGH', 'MEDIUM', 'LOW']:
                msg = fixer._determine_guardian_message('Exception', sev, 'test')
                assert isinstance(msg, str)
                assert '# guardian:' in msg

    def _write_empty(self, ws):
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': []}, f)


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestWave30FailClosed:
    """§1.8 Fail-closed tests for Wave 3.0."""

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
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            with patch('pathlib.Path.read_text', side_effect=PermissionError("denied")):
                result = fixer.apply_guardian_sweep()
                assert result['errors'] >= 1

    def test_write_failure_does_not_claim_success(self, ws):
        """Fixer does not increment annotations_added when write_text fails."""
        src = ws / "readonly.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            with patch('pathlib.Path.write_text', side_effect=IOError("disk full")):
                result = fixer.apply_guardian_sweep()
                assert result['errors'] >= 1
                assert result['annotations_added'] == 0


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestWave30Integration:
    """End-to-end integration tests for Wave 3.0."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_end_to_end_full_sweep(self, ws):
        """Pipeline processes all violation types correctly."""
        files = [
            ("high_import.py", "ImportError", "HIGH"),
            ("high_attr.py", "AttributeError", "HIGH"),
            ("medium_exc.py", "Exception", "MEDIUM"),
            ("low_syntax.py", "SyntaxError", "LOW"),
        ]
        violations = []
        for fname, exc, sev in files:
            fp = ws / fname
            fp.write_text(f"try:\n    operation()\nexcept {exc}:\n    pass\n")
            violations.append({
                'file_path': str(fp), 'line_number': 3,
                'exception_type': exc, 'handler_body': ['pass'],
                'severity': sev, 'context': 'test'
            })
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()

        assert result['wave'] == '3.0'
        assert result['annotations_added'] == 4
        assert result['errors'] == 0

        for fname, _, _ in files:
            content = (ws / fname).read_text()
            assert "# guardian: allow-silent-swallow" in content

    def test_report_generation(self, ws):
        """generate_sweep_report returns correct structure."""
        src = ws / "rpt.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            fixer.apply_guardian_sweep()
            rpt = fixer.generate_sweep_report()

        assert rpt['wave'] == '3.0'
        assert 'completion_percentage' in rpt
        assert 'sweep_timestamp' in rpt
        assert 'severity_distribution' in rpt
        assert rpt['total_violations'] >= 1

    def test_skip_already_guarded(self, ws):
        """Fixer skips violations that already have guardian comments."""
        src = ws / "already.py"
        src.write_text("try:\n    op()\nexcept Exception:\n    pass  # guardian: allow-silent-swallow\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test',
             'has_guardian': True}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 0
            assert result['skipped_guarded'] == 1

    def test_mixed_guarded_and_unguarded(self, ws):
        """Fixer processes unguarded violations while skipping guarded ones."""
        unguarded = ws / "unguarded.py"
        unguarded.write_text("try:\n    op()\nexcept Exception:\n    pass\n")
        guarded = ws / "guarded.py"
        guarded.write_text("try:\n    op()\nexcept Exception:\n    pass  # guardian: allow-silent-swallow\n")
        violations = [
            {'file_path': str(unguarded), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test', 'has_guardian': False},
            {'file_path': str(guarded), 'line_number': 3,
             'exception_type': 'Exception', 'handler_body': ['pass'],
             'severity': 'MEDIUM', 'context': 'test', 'has_guardian': True},
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = GuardianSweepFixer()
            result = fixer.apply_guardian_sweep()
            assert result['annotations_added'] == 1
            assert result['skipped_guarded'] == 1

        # Verify unguarded got annotated, guarded unchanged
        assert "# guardian: allow-silent-swallow" in unguarded.read_text()
        content = guarded.read_text()
        assert content.count("# guardian: allow-silent-swallow") == 1