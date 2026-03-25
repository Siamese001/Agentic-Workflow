#!/usr/bin/env python3
"""
Basic tests for Phase 2.3 low severity fixes implementation.
Uses patch('fix_low_severity_swallowers.PROJECT_ROOT', ...) for isolation.
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
class TestPhase23Basic:
    """Basic tests for Phase 2.3 implementation."""

    @pytest.fixture
    def ws(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            (workspace / "tools").mkdir()
            yield workspace

    def _write_report(self, ws, violations_list):
        with open(ws / "tools" / "silent_swallower_report.json", 'w') as f:
            json.dump({'violations': violations_list}, f)

    def test_can_import_fixer(self):
        """Test that the fixer can be imported."""
        assert LowSeveritySilentSwallowerFixer is not None

    def test_fixer_with_empty_violations(self, ws):
        """Test fixer initialization with empty violations."""
        self._write_report(ws, [])
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0
            assert fixer.errors == 0

    def test_fixer_with_sample_violations(self, ws):
        """Test fixer initialization with sample violations."""
        violations = [
            {'file_path': 'test_file.py', 'line_number': 10,
             'exception_type': 'SyntaxError', 'handler_body': ['pass'],
             'context': 'syntax parsing error', 'severity': 'LOW'},
            {'file_path': 'test_file2.py', 'line_number': 20,
             'exception_type': 'OSError', 'handler_body': ['pass'],
             'context': 'file system error', 'severity': 'LOW'}
        ]
        self._write_report(ws, violations)
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()
            assert len(fixer.violations) == 2
            assert fixer.fixes_applied == 0
            assert fixer.errors == 0

    def test_exception_strategy_determination(self, ws):
        """Test exception strategy determination based on exception type."""
        self._write_report(ws, [])
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()

            strategy = fixer._determine_exception_fix_strategy('SyntaxError', 'syntax parsing')
            assert isinstance(strategy, dict)
            assert 'action' in strategy

            strategy = fixer._determine_exception_fix_strategy('OSError', 'file system')
            assert isinstance(strategy, dict)
            assert 'action' in strategy

            strategy = fixer._determine_exception_fix_strategy('UnicodeDecodeError', 'encoding')
            assert isinstance(strategy, dict)
            assert 'action' in strategy

    def test_targeted_exception_handler_creation(self, ws):
        """Test targeted exception handler creation."""
        self._write_report(ws, [])
        with patch(PATCH_TARGET, ws):
            fixer = LowSeveritySilentSwallowerFixer()

            original = "    except SyntaxError:"
            strategy = {'action': 'add_guardian_comment',
                        'comment': '# guardian: Syntax errors should be caught earlier'}
            new_handler = fixer._create_targeted_exception_handler(original, 'syntax', strategy)

            assert new_handler != original
            assert "# guardian:" in new_handler
