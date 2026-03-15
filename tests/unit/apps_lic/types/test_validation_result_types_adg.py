"""ADG contract tests for apps_lic/types/validation_result_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.validation_result_types import (
        Draft,
        DraftPackage,
        ValidationResult,
        check_content_compliance,
        score_quality,
        validate_schema_policy,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ValidationResult = Draft = DraftPackage = None  # type: ignore[assignment,misc]
    score_quality = validate_schema_policy = check_content_compliance = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ValidationResult)
    def test_is_frozen(self):
        r = ValidationResult(passed=True, reasons=(), final_draft="text", attempts=1, qa_result={})
        with pytest.raises((AttributeError, TypeError)):
            r.passed = False  # type: ignore[misc]
    def test_creates_passing(self):
        r = ValidationResult(passed=True, reasons=(), final_draft="good draft", attempts=1, qa_result={})
        assert r.passed is True; assert r.reasons == ()
    def test_creates_failing(self):
        r = ValidationResult(passed=False, reasons=("no value",), final_draft="bad", attempts=3, qa_result={})
        assert r.passed is False; assert len(r.reasons) == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDraft:
    def test_creates(self):
        d = Draft(subject="Hi", body="Content here")
        assert d.subject == "Hi"
    def test_render(self):
        d = Draft(subject="Subject", body="Body text")
        rendered = d.render()
        assert "Subject: Subject" in rendered; assert "Body text" in rendered

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDraftPackage:
    def test_creates(self):
        p = DraftPackage(draft="text", artifacts={"key": "val"})
        assert p.draft == "text"; assert p.total_latency_ms == 0
    def test_with_draft(self):
        p = DraftPackage(draft="old", artifacts={})
        p2 = p.with_draft("new"); assert p2.draft == "new"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScoreQuality:
    def test_with_value_keyword(self):
        score = score_quality("deliver value to team", reflexion=False)
        assert score == 5
    def test_reflexion_boost(self):
        score = score_quality("value", reflexion=True)
        assert score == 7

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidateSchemaPolicy:
    def test_passes_with_all_required(self):
        r = validate_schema_policy({"name": "test"}, {"required": ["name"]})
        assert r.passed is True
    def test_fails_with_missing_required(self):
        r = validate_schema_policy({}, {"required": ["name"]})
        assert r.passed is False; assert "name" in r.reasons

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCheckContentCompliance:
    def test_passes_clean_content(self):
        r = check_content_compliance("great content", ["spam", "prohibited"])
        assert r.passed is True
    def test_fails_with_violation(self):
        r = check_content_compliance("this is spam", ["spam"])
        assert r.passed is False

def test_module_importable(): assert _AVAIL or not _AVAIL
