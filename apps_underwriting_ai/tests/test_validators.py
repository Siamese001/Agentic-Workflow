"""Tests for apps_underwriting_ai additional validator components."""

from datetime import datetime, timezone

from apps_underwriting_ai.validators.authority_limit_validator import (
    AuthorityLimitValidator,
)
from apps_underwriting_ai.validators.stale_data_validator import (
    StaleDataValidator,
)


class TestAuthorityLimitValidator:
    """Test AuthorityLimitValidator."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = AuthorityLimitValidator()
        assert validator is not None

    def test_validate_within_limit(self):
        """Test validation within authority limit."""
        validator = AuthorityLimitValidator()
        result = validator.validate({"amount": 1000, "limit": 5000})
        assert result is not None
        assert result.within_authority is True
        assert result.requested_amount == 1000.0
        assert result.human_review_required is False

    def test_validate_exceeds_limit(self):
        """Test failure path: requested amount exceeds authority limit."""
        validator = AuthorityLimitValidator()
        result = validator.validate({"amount": 6000, "limit": 5000})
        assert result.within_authority is False
        assert result.human_review_required is True
        assert result.excess_amount == 1000.0


class TestStaleDataValidator:
    """Test StaleDataValidator."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = StaleDataValidator()
        assert validator is not None

    def test_validate_fresh_data(self):
        """Test validation of fresh data."""
        import time

        validator = StaleDataValidator()
        result = validator.validate({"timestamp": time.time()})
        assert result is not None
        assert result.fresh is True
        assert result.stale_items == []
        assert result.requires_update is False

    def test_validate_stale_appraisal_with_now_provider(self):
        """Edge case: now_provider injection detects stale appraisal via UTC-aware comparison."""
        frozen_now = datetime(2024, 6, 1, tzinfo=timezone.utc)
        validator = StaleDataValidator(now_provider=lambda: frozen_now)
        result = validator.validate({"appraisal_date": "2022-01-01"})
        assert result.fresh is False
        assert len(result.stale_items) == 1
        assert result.stale_items[0]["document_type"] == "appraisal"
        assert result.stale_items[0]["severity"] == "critical"
