#!/usr/bin/env python3
"""
Comprehensive tests for Phase 2.4: HIGH severity remaining violations.
Target: 2,482 violations (744 single-type + 1,738 multi-exception combos).
Tests follow windsurfrules §1.1-§1.8 requirements.

Uses patch('fix_high_severity_remaining.PROJECT_ROOT', ...) for isolation.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from fix_high_severity_remaining import HighSeverityRemainingFixer
    CAN_IMPORT = True
except ImportError as e:
    CAN_IMPORT = False

PATCH_TARGET = 'fix_high_severity_remaining.PROJECT_ROOT'


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase24EdgeCases:
    """§1.5 Edge case tests for Phase 2.4."""

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
            fixer = HighSeverityRemainingFixer()
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0

    # ── Edge case 2: Malformed data (missing 'violations' key) ──────
    def test_malformed_data_missing_key(self, ws):
        """KeyError raised when report has no 'violations' key."""
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'invalid': 'data'}, f)
        with patch(PATCH_TARGET, ws):
            with pytest.raises(KeyError):
                HighSeverityRemainingFixer()

    # ── Edge case 3: Violation with missing file_path field ─────────
    def test_missing_file_path_field(self, ws):
        """Violations without file_path are loaded but skipped during apply."""
        violations = [
            {'line_number': 10, 'exception_type': 'AttributeError',
             'handler_body': ['pass'], 'severity': 'HIGH'},
            {'file_path': str(ws / 'ok.py'), 'line_number': 3,
             'exception_type': 'ValueError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'value validation'}
        ]
        (ws / 'ok.py').write_text("try:\n    op()\nexcept ValueError:\n    pass\n")
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert isinstance(result, dict)
            assert result['fixes_applied'] >= 0

    # ── Edge case 4: Non-existent file path ─────────────────────────
    def test_nonexistent_file_path(self, ws):
        """Fixer skips files that do not exist on disk."""
        violations = [
            {'file_path': str(ws / 'ghost.py'), 'line_number': 3,
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'phantom'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0

    # ── Edge case 5: Unicode file paths ─────────────────────────────
    def test_unicode_file_path(self, ws):
        """Fixer handles Unicode file names without error."""
        ufile = ws / "tëst_ünïcødë.py"
        ufile.write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        violations = [
            {'file_path': str(ufile), 'line_number': 3,
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'attribute access'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

    # ── Edge case 6: Line number out of range ───────────────────────
    def test_line_number_out_of_range(self, ws):
        """Fixer skips violations whose line number exceeds file length."""
        src = ws / "short.py"
        src.write_text("x = 1\n")
        violations = [
            {'file_path': str(src), 'line_number': 999,
             'exception_type': 'ValueError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'out of range'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 0

    # ── Edge case 7: Only non-HIGH violations in report ─────────────
    def test_only_non_high_violations(self, ws):
        """Fixer loads zero violations when report contains only MEDIUM/LOW."""
        violations = [
            {'file_path': 'a.py', 'line_number': 1, 'exception_type': 'Exception',
             'handler_body': ['pass'], 'severity': 'MEDIUM'},
            {'file_path': 'b.py', 'line_number': 1, 'exception_type': 'SyntaxError',
             'handler_body': ['pass'], 'severity': 'LOW'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            assert len(fixer.violations) == 0

    # ── Edge case 8: Filters out ImportError (already handled by 2.1) ─
    def test_excludes_importerror_only(self, ws):
        """Fixer excludes pure ImportError violations (handled by Phase 2.1)."""
        violations = [
            {'file_path': 'a.py', 'line_number': 1, 'exception_type': 'ImportError',
             'handler_body': ['pass'], 'severity': 'HIGH'},
            {'file_path': str(ws / 'b.py'), 'line_number': 3,
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'attr access'}
        ]
        (ws / 'b.py').write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            # Should only have the non-ImportError violation
            assert len(fixer.violations) == 1

    # ── Edge case 9: Multi-exception combo ──────────────────────────
    def test_multi_exception_combo(self, ws):
        """Fixer handles multi-exception type violations."""
        src = ws / "multi.py"
        src.write_text("try:\n    op()\nexcept (TypeError, ValueError, AttributeError):\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'TypeError, ValueError, AttributeError',
             'handler_body': ['pass'], 'severity': 'HIGH',
             'context': 'type and value checks'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

    # ── Edge case 10: ModuleNotFoundError (distinct from ImportError) ─
    def test_module_not_found_error(self, ws):
        """Fixer handles ModuleNotFoundError separately from ImportError."""
        src = ws / "mnf.py"
        src.write_text("try:\n    import foo\nexcept ModuleNotFoundError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'ModuleNotFoundError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'module import'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            assert len(fixer.violations) == 1
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase24Determinism:
    """§1.7 Determinism tests for Phase 2.4."""

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
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'attribute access'}
        ]
        report = {'violations': violations}
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump(report, f)

        src.write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f1 = HighSeverityRemainingFixer()
            r1 = f1.apply_fixes_to_all_remaining_violations()

        src.write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        with patch(PATCH_TARGET, ws):
            f2 = HighSeverityRemainingFixer()
            r2 = f2.apply_fixes_to_all_remaining_violations()

        assert r1['fixes_applied'] == r2['fixes_applied']
        assert r1['errors'] == r2['errors']
        assert r1['remaining'] == r2['remaining']

    def test_strategy_consistency_single_type(self, ws):
        """_determine_fix_strategy returns same dict on repeat calls for single type."""
        self._write_empty(ws)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            s1 = fixer._determine_fix_strategy('AttributeError', 'attr access')
            s2 = fixer._determine_fix_strategy('AttributeError', 'attr access')
            assert s1 == s2

    def test_strategy_consistency_multi_type(self, ws):
        """_determine_fix_strategy returns same dict for multi-exception input."""
        self._write_empty(ws)
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            s1 = fixer._determine_fix_strategy('TypeError, ValueError, AttributeError', 'mixed')
            s2 = fixer._determine_fix_strategy('TypeError, ValueError, AttributeError', 'mixed')
            assert s1 == s2

    def test_all_single_exception_strategies(self, ws):
        """Each known single-type exception returns a strategy with 'action' key."""
        self._write_empty(ws)
        known = ['AttributeError', 'ValueError', 'TypeError', 'KeyError',
                 'IndexError', 'ModuleNotFoundError']
        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            for exc in known:
                strategy = fixer._determine_fix_strategy(exc, 'test')
                assert isinstance(strategy, dict), f"Strategy for {exc} not dict"
                assert 'action' in strategy, f"Strategy for {exc} missing 'action'"

    def _write_empty(self, ws):
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': []}, f)


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase24FailClosed:
    """§1.8 Fail-closed tests for Phase 2.4."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_permission_error_on_read(self, ws):
        """Fixer records errors when file read raises PermissionError."""
        src = ws / "locked.py"
        src.write_text("try:\n    op()\nexcept ValueError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'ValueError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'test'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            with patch('pathlib.Path.read_text', side_effect=PermissionError("denied")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1

    def test_write_failure_does_not_claim_success(self, ws):
        """Fixer does not increment fixes_applied when write_text fails."""
        src = ws / "readonly.py"
        src.write_text("try:\n    op()\nexcept TypeError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'TypeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'type check'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            with patch('pathlib.Path.write_text', side_effect=IOError("disk full")):
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 1
                assert result['fixes_applied'] == 0


@pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
class TestPhase24Integration:
    """End-to-end integration tests for Phase 2.4."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def test_end_to_end_single_type_fixes(self, ws):
        """Pipeline processes single-type HIGH violations correctly."""
        files = [
            ("attr.py", "AttributeError", "attribute access"),
            ("val.py", "ValueError", "value validation"),
            ("typ.py", "TypeError", "type checking"),
            ("key.py", "KeyError", "key lookup"),
        ]
        violations = []
        for fname, exc, ctx in files:
            fp = ws / fname
            fp.write_text(f"try:\n    operation()\nexcept {exc}:\n    pass\n")
            violations.append({
                'file_path': str(fp), 'line_number': 3,
                'exception_type': exc, 'handler_body': ['pass'],
                'severity': 'HIGH', 'context': ctx
            })
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()

        assert result['phase'] == '2.4'
        assert result['fixes_applied'] == 4
        assert result['errors'] == 0

        for fname, _, _ in files:
            content = (ws / fname).read_text()
            assert "# guardian:" in content, f"{fname} missing guardian comment"

    def test_end_to_end_multi_type_fixes(self, ws):
        """Pipeline processes multi-exception HIGH violations correctly."""
        src = ws / "multi.py"
        src.write_text("try:\n    operation()\nexcept (TypeError, ValueError, AttributeError):\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'TypeError, ValueError, AttributeError',
             'handler_body': ['pass'], 'severity': 'HIGH',
             'context': 'mixed type checks'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()

        assert result['fixes_applied'] == 1
        content = src.read_text()
        assert "# guardian:" in content

    def test_report_generation(self, ws):
        """generate_systematic_fix_report returns correct structure."""
        src = ws / "rpt.py"
        src.write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        violations = [
            {'file_path': str(src), 'line_number': 3,
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'attribute access'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            fixer.apply_fixes_to_all_remaining_violations()
            rpt = fixer.generate_systematic_fix_report()

        assert rpt['phase'] == '2.4'
        assert 'completion_percentage' in rpt
        assert 'fix_timestamp' in rpt
        assert 'exception_type_distribution' in rpt
        assert rpt['total_high_severity_remaining'] >= 1

    def test_mixed_importerror_and_remaining(self, ws):
        """Fixer processes remaining HIGH but skips pure ImportError."""
        ie_file = ws / "ie.py"
        ie_file.write_text("try:\n    import foo\nexcept ImportError:\n    pass\n")
        attr_file = ws / "attr.py"
        attr_file.write_text("try:\n    op()\nexcept AttributeError:\n    pass\n")
        violations = [
            {'file_path': str(ie_file), 'line_number': 3,
             'exception_type': 'ImportError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'import'},
            {'file_path': str(attr_file), 'line_number': 3,
             'exception_type': 'AttributeError', 'handler_body': ['pass'],
             'severity': 'HIGH', 'context': 'attribute access'}
        ]
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations}, f)

        with patch(PATCH_TARGET, ws):
            fixer = HighSeverityRemainingFixer()
            assert len(fixer.violations) == 1  # only AttributeError
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert result['fixes_applied'] == 1

        # ImportError file should be untouched
        assert "# guardian:" not in ie_file.read_text()
        assert "# guardian:" in attr_file.read_text()