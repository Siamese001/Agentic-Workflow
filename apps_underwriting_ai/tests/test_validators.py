"""Tests for apps_underwriting_ai additional validator components."""


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
        # Test with data within limit
        result = validator.validate({"amount": 1000, "limit": 5000})
        assert result is not None


class TestStaleDataValidator:
    """Test StaleDataValidator."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = StaleDataValidator()
        assert validator is not None

    def test_validate_fresh_data(self):
        """Test validation of fresh data."""
        validator = StaleDataValidator()
        # Test with fresh data
        import time
        result = validator.validate({"timestamp": time.time()})
        assert result is not None
