"""Tests for apps_rg historical research prerequisite (W2)."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from apps_rg.prerequisites.briefing_validator import (
    BriefingValidationResult,
    BriefingCheck,
    HistoricalBriefingValidator,
    check_briefing_prerequisite,
)


class TestBriefingValidationResult:
    """Test validation result enum."""

    def test_enum_values(self):
        """Enum has expected values."""
        assert BriefingValidationResult.VALID.value == "valid"
        assert BriefingValidationResult.MISSING.value == "missing"
        assert BriefingValidationResult.STALE.value == "stale"
        assert BriefingValidationResult.POLICY_MISMATCH.value == "policy_mismatch"
        assert BriefingValidationResult.BLUEPRINT_MISMATCH.value == "blueprint_mismatch"
        assert BriefingValidationResult.SCOPE_MISMATCH.value == "scope_mismatch"
        assert BriefingValidationResult.INCOMPLETE.value == "incomplete"


class TestBriefingCheck:
    """Test briefing check dataclass."""

    def test_valid_check(self):
        """Valid check has correct properties."""
        check = BriefingCheck(
            result=BriefingValidationResult.VALID,
            briefing={"company": "Acme"},
            reason="Valid briefing",
            freshness_hours=24.0,
        )

        assert check.is_valid is True
        assert check.requires_apps_research is False

    def test_missing_check_requires_research(self):
        """Missing briefing requires apps_research."""
        check = BriefingCheck(
            result=BriefingValidationResult.MISSING,
            briefing=None,
            reason="No briefing found",
        )

        assert check.is_valid is False
        assert check.requires_apps_research is True

    def test_stale_check_requires_research(self):
        """Stale briefing requires apps_research refresh."""
        check = BriefingCheck(
            result=BriefingValidationResult.STALE,
            briefing={"company": "Acme"},
            reason="Briefing too old",
            freshness_hours=1000.0,
        )

        assert check.is_valid is False
        assert check.requires_apps_research is True

    def test_policy_mismatch_fails_closed(self):
        """Policy mismatch fails closed (no apps_research help)."""
        check = BriefingCheck(
            result=BriefingValidationResult.POLICY_MISMATCH,
            briefing={"company": "Acme"},
            reason="Policy hash mismatch",
        )

        assert check.is_valid is False
        assert check.requires_apps_research is False

    def test_blueprint_mismatch_fails_closed(self):
        """Blueprint mismatch fails closed."""
        check = BriefingCheck(
            result=BriefingValidationResult.BLUEPRINT_MISMATCH,
            briefing={"company": "Acme"},
            reason="Blueprint hash mismatch",
        )

        assert check.is_valid is False
        assert check.requires_apps_research is False

    def test_scope_mismatch_fails_closed(self):
        """Scope mismatch fails closed."""
        check = BriefingCheck(
            result=BriefingValidationResult.SCOPE_MISMATCH,
            briefing={"company": "OtherCorp"},
            reason="Company mismatch",
        )

        assert check.is_valid is False
        assert check.requires_apps_research is False

    def test_incomplete_check_requires_research(self):
        """Incomplete briefing requires apps_research."""
        check = BriefingCheck(
            result=BriefingValidationResult.INCOMPLETE,
            briefing={"company": "Acme"},
            reason="Missing required fields",
        )

        assert check.is_valid is False
        assert check.requires_apps_research is True


class TestHistoricalBriefingValidatorInitialization:
    """Test validator initialization."""

    def test_validator_stores_policy_hash(self):
        """Validator stores policy hash."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        assert validator.policy_hash == "policy_v1"
        assert validator.blueprint_hash == "blueprint_v1"

    def test_validator_default_tenant(self):
        """Validator uses default tenant."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        assert validator.tenant_id == "default"

    def test_validator_custom_tenant(self):
        """Validator accepts custom tenant."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            tenant_id="enterprise_123",
        )

        assert validator.tenant_id == "enterprise_123"


class TestBriefingValidatorScopeMatch:
    """Test scope matching logic."""

    def test_company_name_match(self):
        """Exact company name match works."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme Corp"}
        result = validator._check_scope_match(briefing, "Acme Corp", "Engineer")

        assert result is True

    def test_company_name_case_insensitive(self):
        """Company name match is case insensitive."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "ACME CORP"}
        result = validator._check_scope_match(briefing, "acme corp", "Engineer")

        assert result is True

    def test_company_name_mismatch(self):
        """Different company names don't match."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme Corp"}
        result = validator._check_scope_match(briefing, "Other Corp", "Engineer")

        assert result is False

    def test_role_context_match(self):
        """Role context matching works."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme", "role_context": "Senior ML Engineer"}
        result = validator._check_scope_match(briefing, "Acme", "ML Engineer")

        assert result is True

    def test_role_context_no_overlap(self):
        """No role overlap returns False."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme", "role_context": "Sales Representative"}
        result = validator._check_scope_match(briefing, "Acme", "ML Engineer")

        assert result is False


class TestBriefingValidatorCompleteness:
    """Test completeness checking."""

    def test_complete_briefing(self):
        """Briefing with all required fields is complete."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {
            "company": "Acme",
            "mission": "Build great things",
            "culture": "Innovative",
            "recent_news": ["Launch"],
        }

        assert validator._check_completeness(briefing) is True

    def test_missing_mission(self):
        """Briefing missing mission is incomplete."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {
            "company": "Acme",
            "culture": "Innovative",
            "recent_news": ["Launch"],
        }

        assert validator._check_completeness(briefing) is False

    def test_missing_culture(self):
        """Briefing missing culture is incomplete."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {
            "company": "Acme",
            "mission": "Build great things",
            "recent_news": ["Launch"],
        }

        assert validator._check_completeness(briefing) is False

    def test_empty_recent_news(self):
        """Empty recent news list is incomplete."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {
            "company": "Acme",
            "mission": "Build great things",
            "culture": "Innovative",
            "recent_news": [],
        }

        assert validator._check_completeness(briefing) is False


class TestBriefingValidatorFreshness:
    """Test freshness checking."""

    def test_fresh_briefing(self):
        """Recent briefing is fresh."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        recent = datetime.now(timezone.utc) - timedelta(days=5)
        briefing = {"fetched_at": recent.isoformat()}

        freshness = validator._calculate_freshness(briefing)
        assert freshness < validator.DEFAULT_TTL_HOURS

    def test_stale_briefing(self):
        """Old briefing is stale."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        old = datetime.now(timezone.utc) - timedelta(days=60)
        briefing = {"fetched_at": old.isoformat()}

        freshness = validator._calculate_freshness(briefing)
        assert freshness > validator.DEFAULT_TTL_HOURS

    def test_unknown_freshness(self):
        """Briefing without timestamp is treated as stale."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme"}

        freshness = validator._calculate_freshness(briefing)
        assert freshness == float("inf")


class TestBriefingValidatorPolicyCompatibility:
    """Test policy compatibility checking."""

    def test_matching_policy(self):
        """Matching policy hash is compatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v2",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"policy_hash": "policy_v2"}

        assert validator._check_policy_compatibility(briefing) is True

    def test_mismatched_policy(self):
        """Different policy hash is incompatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v2",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"policy_hash": "policy_v1"}

        assert validator._check_policy_compatibility(briefing) is False

    def test_no_policy_hash_legacy(self):
        """Legacy briefing without policy hash is assumed compatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v2",
            blueprint_hash="blueprint_v1",
        )

        briefing = {"company": "Acme"}

        assert validator._check_policy_compatibility(briefing) is True


class TestBriefingValidatorBlueprintCompatibility:
    """Test blueprint compatibility checking."""

    def test_matching_blueprint(self):
        """Matching blueprint hash is compatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v2",
        )

        briefing = {"blueprint_hash": "blueprint_v2"}

        assert validator._check_blueprint_compatibility(briefing) is True

    def test_mismatched_blueprint(self):
        """Different blueprint hash is incompatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v2",
        )

        briefing = {"blueprint_hash": "blueprint_v1"}

        assert validator._check_blueprint_compatibility(briefing) is False

    def test_no_blueprint_hash_legacy(self):
        """Legacy briefing without blueprint hash is assumed compatible."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v2",
        )

        briefing = {"company": "Acme"}

        assert validator._check_blueprint_compatibility(briefing) is True


class TestCheckBriefingPrerequisite:
    """Test high-level prerequisite check function."""

    def test_function_exists(self):
        """High-level check function exists."""
        assert callable(check_briefing_prerequisite)

    def test_check_with_missing_briefing(self):
        """Check returns missing result when no briefing."""
        # This will fail because there's no actual briefing file
        # but we can verify the function runs without error
        result = check_briefing_prerequisite(
            target_company="NonExistentCompanyXYZ123",
            target_role="Engineer",
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        assert result.result == BriefingValidationResult.MISSING
        assert result.is_valid is False


class TestRoleSimilarity:
    """Test role similarity calculation."""

    def test_exact_match(self):
        """Exact role match has similarity 1.0."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        similarity = validator._role_similarity("senior engineer", "senior engineer")
        assert similarity == 1.0

    def test_partial_match(self):
        """Partial word overlap has similarity between 0 and 1."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        similarity = validator._role_similarity("senior ml engineer", "senior engineer")
        assert 0 < similarity < 1

    def test_no_match(self):
        """No word overlap has similarity 0."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        similarity = validator._role_similarity("sales representative", "ml engineer")
        assert similarity == 0.0

    def test_empty_strings(self):
        """Empty strings have similarity 0."""
        validator = HistoricalBriefingValidator(
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
        )

        similarity = validator._role_similarity("", "engineer")
        assert similarity == 0.0
