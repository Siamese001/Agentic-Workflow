"""RTC-REQ-004 — Acceptance Legality.

Validates that acceptance criteria follow legality rules and that
the acceptance validator correctly identifies legal vs illegal criteria.

W0 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.runtime.prove_requirements.acceptance_validator import (
    validate_acceptance_criteria,
    AcceptanceValidationResult,
    LEGALITY_RULES,
)


class TestRTC004AcceptanceLegality:
    """RTC-REQ-004: Acceptance legality validation."""

    def test_legal_criteria_pass(self) -> None:
        """Legal acceptance criteria pass validation."""
        criteria = {
            "req_id": "RTC-REQ-004",
            "title": "Legal Criterion",
            "acceptance": "Test passes with exit code 0",
        }
        result = validate_acceptance_criteria(criteria)
        assert result.is_legal
        assert not result.violations

    def test_empty_criteria_fails(self) -> None:
        """Empty acceptance criteria is illegal."""
        criteria = {
            "req_id": "RTC-REQ-004",
            "title": "Empty Criterion",
            "acceptance": "",
        }
        result = validate_acceptance_criteria(criteria)
        assert not result.is_legal
        assert any("empty" in v.lower() for v in result.violations)

    def test_missing_acceptance_field_fails(self) -> None:
        """Missing acceptance field is illegal."""
        criteria: dict[str, Any] = {
            "req_id": "RTC-REQ-004",
            "title": "No Acceptance",
        }
        result = validate_acceptance_criteria(criteria)
        assert not result.is_legal

    def test_placeholder_text_detected(self) -> None:
        """Placeholder text (TBD, TODO, etc.) is illegal."""
        criteria = {
            "req_id": "RTC-REQ-004",
            "title": "Placeholder Criterion",
            "acceptance": "TBD: write test later",
        }
        result = validate_acceptance_criteria(criteria)
        assert not result.is_legal
        assert any("placeholder" in v.lower() for v in result.violations)


class TestRTC004LegalityRules:
    """Legality rules enumeration tests."""

    def test_legality_rules_defined(self) -> None:
        """LEGALITY_RULES has at least 3 rules."""
        assert len(LEGALITY_RULES) >= 3

    def test_rules_have_descriptions(self) -> None:
        """Each rule has description and check function."""
        for rule_id, rule in LEGALITY_RULES.items():
            assert "description" in rule, f"Rule {rule_id} missing description"
            assert "check" in rule, f"Rule {rule_id} missing check function"


class TestRTC004ResultStructure:
    """AcceptanceValidationResult structure tests."""

    def test_result_has_is_legal(self) -> None:
        """Result has is_legal boolean."""
        result = AcceptanceValidationResult(is_legal=True, violations=[])
        assert isinstance(result.is_legal, bool)

    def test_result_has_violations_list(self) -> None:
        """Result has violations list."""
        result = AcceptanceValidationResult(is_legal=False, violations=["violation 1"])
        assert isinstance(result.violations, list)


class TestRTC004FailClosedPaths:
    """Fail-closed tests for acceptance validation."""

    def test_none_criteria_fails(self) -> None:
        """None criteria fails validation."""
        result = validate_acceptance_criteria(None)  # type: ignore[arg-type]
        assert not result.is_legal

    def test_non_dict_criteria_fails(self) -> None:
        """Non-dict criteria fails validation."""
        result = validate_acceptance_criteria("string criteria")  # type: ignore[arg-type]
        assert not result.is_legal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
