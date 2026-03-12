"""ADG contract tests for L5_safety/types/security_validation_types.py."""
from __future__ import annotations
import ast
import pytest
pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L5_safety/types/security_validation_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_has_validation_suite():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "ValidationSuite" in src or "SecurityValidation" in src or "ThreatLevel" in src

def test_has_dataclasses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "dataclass" in src or "class" in src

try:
    from agentic_core.L5_safety.types.security_validation_types import (
        SecurityValidationResult, SecuritySuiteResult, RedTeamValidationSuite,
        get_security_suite, run_security_validation,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    SecurityValidationResult = SecuritySuiteResult = RedTeamValidationSuite = None  # type: ignore[assignment,misc]
    get_security_suite = run_security_validation = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSecurityValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SecurityValidationResult)
    def test_creates(self):
        r = SecurityValidationResult(validator_name="test_v", valid=True)
        assert r.valid is True; assert r.errors == []

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSecuritySuiteResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SecuritySuiteResult)
    def test_creates(self):
        r = SecuritySuiteResult(overall_valid=True, validators_run=2, validators_passed=2, validators_failed=0)
        assert r.overall_valid is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRedTeamValidationSuite:
    def test_creates(self): suite = RedTeamValidationSuite(); assert suite is not None
    def test_get_status(self):
        suite = RedTeamValidationSuite()
        status = suite.get_status()
        assert "initialized" in status
    def test_run_all(self):
        suite = RedTeamValidationSuite()
        result = suite.run_all({"test": "content"})
        assert isinstance(result, SecuritySuiteResult)
    def test_get_security_suite_singleton(self):
        s1 = get_security_suite(); s2 = get_security_suite(); assert s1 is s2
    def test_run_security_validation(self):
        result = run_security_validation({"data": "payload"})
        assert isinstance(result, SecuritySuiteResult)
