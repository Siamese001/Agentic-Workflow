#!/usr/bin/env python3
"""
Tests for plan format compliance CI gate.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Tuple

import pytest

from ops_scripts.ci.check_plan_format_compliance import (
    PlanFormatValidator,
    Severity,
    Violation,
    validate_file,
    has_unclassified_warn,
)


class TestRequiredMarkers:
    """TLM-1 through TLM-5: Required top-level markers."""
    
    def test_missing_format_version_fails(self):
        content = """---
plan_id: test
---

# Test Plan

PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any("TLM-1" in v.rule_id for v in fail_violations)
    
    def test_valid_plan_passes(self):
        content = """---
plan_id: test
---

# Test Plan

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert len(fail_violations) == 0


class TestFormatVersion:
    """TLM-1b: FORMAT_VERSION value validation."""
    
    def test_invalid_format_version_fails(self):
        content = """FORMAT_VERSION: old-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "TLM-1b" for v in fail_violations)
    
    def test_correct_format_version_passes(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert not any(v.rule_id == "TLM-1b" for v in fail_violations)


class TestEnumValidation:
    """ENUM-1 through ENUM-5: Status enum validation."""
    
    def test_invalid_plan_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: INVALID_STATUS
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "ENUM-1" for v in fail_violations)
    
    def test_invalid_wave_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: INVALID
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "ENUM-2" for v in fail_violations)
    
    def test_invalid_authorization_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: UNKNOWN
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "ENUM-5" for v in fail_violations)


class TestFencedCodeExclusion:
    """Fenced code blocks must be excluded from strict validation."""
    
    def test_fenced_code_enum_not_validated(self):
        """Example enum values in fenced code should not cause FAIL."""
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED

Example:
```
WAVE_STATUS: <TODO|IN_PROGRESS|DONE>
PHASE_STATUS: <TODO|IN_PROGRESS|DONE>
```
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        # Should not fail on the example in fenced code
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        for v in fail_violations:
            assert "<TODO" not in v.message  # Should not flag the example
    
    def test_fenced_code_emoji_not_validated(self):
        """Example emojis in fenced code should not cause FAIL."""
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED

Status reference:
```
| Status | Icon |
|--------|------|
| Done   | ✅   |
```
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        # Should not fail on emoji in fenced code
        emoji_fail_violations = [v for v in violations 
                                 if v.severity == Severity.FAIL 
                                 and "EMOJI" in v.rule_id]
        assert len(emoji_fail_violations) == 0


class TestEmojiValidation:
    """EMOJI-1 through EMOJI-7: Emoji prohibition in markers."""
    
    def test_emoji_in_plan_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: ✅ DONE
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "EMOJI-1" for v in fail_violations)
    
    def test_emoji_in_wave_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: 🟢 DONE
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "EMOJI-2" for v in fail_violations)
    
    def test_emoji_in_prose_warns(self):
        """Emojis in prose should trigger WARN only (EMOJI-7)."""
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

This plan is ✅ ready.

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        warn_violations = [v for v in violations if v.severity == Severity.WARN]
        assert any(v.rule_id == "EMOJI-7" for v in warn_violations)


class TestWaveStructure:
    """COMP-3, COMP-4: Wave section completeness."""
    
    def test_missing_wave_status_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "COMP-3" for v in fail_violations)
    
    def test_missing_wave_complete_fails(self):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        validator = PlanFormatValidator(content, "test.md")
        violations = validator.validate()
        
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert any(v.rule_id == "COMP-4" for v in fail_violations)


class TestValidateFile:
    """Test validate_file() function."""
    
    def test_file_not_found(self):
        violations, success = validate_file("/nonexistent/file.md")
        assert not success
        assert any(v.rule_id == "FILE-NOT-FOUND" for v in violations)
    
    def test_valid_file(self, tmp_path):
        content = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Wave 1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)
        
        violations, success = validate_file(str(test_file))
        assert success
        fail_violations = [v for v in violations if v.severity == Severity.FAIL]
        assert len(fail_violations) == 0


class TestUnclassifiedWarn:
    """Test has_unclassified_warn() function."""
    
    def test_only_emoji7_is_classified(self):
        violations = [
            Violation(Severity.WARN, "EMOJI-7", 1, "Emoji in prose"),
        ]
        assert not has_unclassified_warn(violations)
    
    def test_other_warns_are_unclassified(self):
        violations = [
            Violation(Severity.WARN, "SOME-OTHER", 1, "Other warning"),
        ]
        assert has_unclassified_warn(violations)


class TestW3PilotPlans:
    """Regression tests for the 3 W3 pilot migrated plans."""
    
    def test_canonical_plan_passes(self):
        """The main plan-format-simplification plan should pass."""
        import subprocess
        result = subprocess.run(
            ["python", "ops_scripts/ci/check_plan_format_compliance.py",
             "--advisory", "--paths", "docs/archive/windsurf/legacy-tree/plans/plan-format-simplification-rca-d4f8e2.md"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "FAIL]" not in result.stdout or "0 FAIL" in result.stdout
    
    def test_template_passes(self):
        """The execution plan template should pass."""
        import subprocess
        result = subprocess.run(
            ["python", "ops_scripts/ci/check_plan_format_compliance.py",
             "--advisory", "--paths", ".cursor/templates/execution-plan-template.md"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "FAIL]" not in result.stdout or "0 FAIL" in result.stdout
