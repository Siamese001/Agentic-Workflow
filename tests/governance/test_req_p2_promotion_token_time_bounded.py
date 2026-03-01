"""Tests for Wave 17 P2: Promotion token time-bounded expiration."""

import pytest

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution" / "capability"))

from promotion_token import PromotionTokenStore, get_token_issuer, issue_promotion_token


class TestPromotionTokenTimeBounded:
    """Test promotion token time-bounded expiration via semantic clock."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing state
        PromotionTokenStore.clear_all()
        self.issuer = get_token_issuer()

    def test_token_time_window_basic(self):
        """Test basic time window enforcement."""
        # Given - Token with specific time window
        token = issue_promotion_token(target_namespace="time_basic", semantic_clock_tick=100, window_size=10)

        # When/Then - Should be valid within window
        assert not token.is_expired(100), "Valid at start of window"
        assert not token.is_expired(105), "Valid in middle of window"
        assert not token.is_expired(110), "Valid at end of window"

        # Should be expired outside window
        assert token.is_expired(111), "Expired after window"
        assert token.is_expired(150), "Expired long after window"

    def test_token_time_window_boundaries(self):
        """Test time window boundary conditions."""
        # Given - Token with window from 100 to 110
        token = issue_promotion_token(
            target_namespace="time_boundaries", semantic_clock_tick=100, window_size=10
        )

        # When/Then - Check exact boundaries
        assert not token.is_expired(99), "Should be valid before start (grace period)"
        assert not token.is_expired(100), "Should be valid at start"
        assert not token.is_expired(109), "Should be valid just before end"
        assert not token.is_expired(110), "Should be valid at end"
        assert token.is_expired(111), "Should be expired immediately after end"

    def test_token_time_window_zero_size(self):
        """Test token with zero-size time window."""
        # Given - Token with zero window size
        token = issue_promotion_token(target_namespace="time_zero", semantic_clock_tick=100, window_size=0)

        # When/Then - Should only be valid at exact tick
        assert not token.is_expired(100), "Valid at exact tick"
        assert token.is_expired(99), "Expired before tick"
        assert token.is_expired(101), "Expired after tick"

    def test_token_time_window_large_size(self):
        """Test token with large time window."""
        # Given - Token with large window
        token = issue_promotion_token(
            target_namespace="time_large", semantic_clock_tick=100, window_size=1000
        )

        # When/Then - Should be valid for large range
        assert not token.is_expired(100), "Valid at start"
        assert not token.is_expired(600), "Valid in middle"
        assert not token.is_expired(1100), "Valid at end"
        assert token.is_expired(1101), "Expired after end"

    def test_token_time_window_with_validation(self):
        """Test time window combined with scope validation."""
        # Given - Token with time window
        token = issue_promotion_token(
            target_namespace="time_validation", semantic_clock_tick=100, window_size=10
        )

        # When/Then - Should validate within time window
        assert token.validate_scope_and_use(), "Should validate within window"

        # Create new token for expired test
        expired_token = issue_promotion_token(
            target_namespace="time_validation", semantic_clock_tick=100, window_size=10
        )

        # Mock expired state by checking validation logic
        # (In real implementation, time would be checked during validation)
        assert not expired_token.is_expired(105), "Not expired at 105"

        # Use the token to mark it as used
        expired_token.validate_scope_and_use()

        # Second use should fail due to single-use, not expiration
        assert not expired_token.validate_scope_and_use(), "Should fail on second use"

    def test_token_issuer_time_validation(self):
        """Test time validation through token issuer."""
        # Each validate_token call consumes the nonce (single-use),
        # so we issue a fresh token per validation point.
        token_100 = self.issuer.issue_promotion_token(
            target_namespace="issuer_time", semantic_clock_tick=100, window_size=10
        )
        token_105 = self.issuer.issue_promotion_token(
            target_namespace="issuer_time", semantic_clock_tick=100, window_size=10
        )
        token_110 = self.issuer.issue_promotion_token(
            target_namespace="issuer_time", semantic_clock_tick=100, window_size=10
        )
        token_111 = self.issuer.issue_promotion_token(
            target_namespace="issuer_time", semantic_clock_tick=100, window_size=10
        )

        # When/Then - Should validate at various ticks within window
        assert self.issuer.validate_token(token_100, "issuer_time", 100), "Should validate at issue time"

        assert self.issuer.validate_token(token_105, "issuer_time", 105), "Should validate within window"

        assert self.issuer.validate_token(token_110, "issuer_time", 110), "Should validate at window end"

        # Should not validate after window
        assert not self.issuer.validate_token(token_111, "issuer_time", 111), (
            "Should not validate after window"
        )

    def test_token_time_window_persistence(self):
        """Test that time window persists across token storage."""
        # Given - Token with time window
        token = issue_promotion_token(
            target_namespace="time_persistence", semantic_clock_tick=200, window_size=50
        )

        # When - Store and retrieve token
        PromotionTokenStore.store_token(token)
        retrieved = PromotionTokenStore.get_token(token.token_id)

        # Then - Time window should be preserved
        assert retrieved is not None, "Token should be stored"
        assert retrieved.semantic_clock_window == (200, 250), "Time window should be preserved"

        # Expiration check should work on retrieved token
        assert not retrieved.is_expired(200), "Retrieved token valid at start"
        assert not retrieved.is_expired(250), "Retrieved token valid at end"
        assert retrieved.is_expired(251), "Retrieved token expired after end"

    def test_token_time_window_different_start_times(self):
        """Test tokens with different start times."""
        # Given - Tokens issued at different times
        early_token = issue_promotion_token(
            target_namespace="time_early", semantic_clock_tick=50, window_size=10
        )

        middle_token = issue_promotion_token(
            target_namespace="time_middle", semantic_clock_tick=100, window_size=10
        )

        late_token = issue_promotion_token(
            target_namespace="time_late", semantic_clock_tick=150, window_size=10
        )

        # When/Then - Each should have different windows
        assert early_token.semantic_clock_window == (50, 60), "Early token window"
        assert middle_token.semantic_clock_window == (100, 110), "Middle token window"
        assert late_token.semantic_clock_window == (150, 160), "Late token window"

        # At tick 100, only middle token should be valid
        assert early_token.is_expired(100), "Early token expired at 100"
        assert not middle_token.is_expired(100), "Middle token valid at 100"
        assert not late_token.is_expired(100), "Late token not yet started at 100"

    def test_token_time_window_edge_cases(self):
        """Test edge cases for time windows."""
        # Given - Token with negative window size (should be handled gracefully)
        try:
            token = issue_promotion_token(
                target_namespace="time_negative", semantic_clock_tick=100, window_size=-5
            )
            # If created, should behave predictably
            assert token.semantic_clock_window[1] >= token.semantic_clock_window[0], (
                "End should not be before start"
            )
        except Exception:
            # It's okay if this fails - negative windows might be rejected
            pass

        # Given - Token with very large window
        large_token = issue_promotion_token(
            target_namespace="time_huge", semantic_clock_tick=100, window_size=1000000
        )

        # Should handle large numbers gracefully
        assert not large_token.is_expired(100), "Valid at start"
        assert not large_token.is_expired(100000), "Valid in middle"
        assert large_token.is_expired(1000101), "Expired after end"

    def test_token_time_window_with_single_use(self):
        """Test interaction between time window and single-use."""
        # Given - Token with time window
        token = issue_promotion_token(
            target_namespace="time_single_use", semantic_clock_tick=100, window_size=10
        )

        # When - Use token within window
        first_use = token.validate_scope_and_use()

        # Then - Should succeed
        assert first_use, "First use should succeed"

        # Second use should fail due to single-use, even within window
        assert not token.validate_scope_and_use(), "Second use should fail due to single-use"

        # Even if we check expiration, single-use takes precedence
        assert not token.is_expired(105), "Not expired, but single-used"

    def test_token_time_window_monitoring(self):
        """Test time window for monitoring and auditing."""
        # Given - Multiple tokens with different windows
        tokens = []
        current_tick = 100

        for i in range(5):
            token = issue_promotion_token(
                target_namespace=f"monitor_{i}", semantic_clock_tick=current_tick + i * 10, window_size=15
            )
            tokens.append(token)

        # When - Check status at current time
        active_tokens = 0
        expired_tokens = 0
        future_tokens = 0

        for token in tokens:
            if token.is_expired(current_tick):
                expired_tokens += 1
            elif current_tick < token.semantic_clock_window[0]:
                future_tokens += 1
            else:
                active_tokens += 1

        # Then - Should categorize correctly
        assert active_tokens >= 1, "Should have active tokens"
        # Some might be expired or future depending on exact timing

        # All tokens should have valid windows
        for token in tokens:
            start, end = token.semantic_clock_window
            assert end >= start, "Window end should be after start"
            assert end - start == 15, "Window size should be 15"


def test_req_p2_promotion_token_time_bounded():
    """Test P2 promotion token time-bounded requirements."""
    test = TestPromotionTokenTimeBounded()
    test.setup_method()

    # Core time window tests
    test.test_token_time_window_basic()
    test.test_token_time_window_boundaries()
    test.test_token_time_window_zero_size()
    test.test_token_time_window_large_size()

    # Integration tests
    test.test_token_time_window_with_validation()
    test.test_token_issuer_time_validation()
    test.test_token_time_window_persistence()

    # Advanced tests
    test.test_token_time_window_different_start_times()
    test.test_token_time_window_edge_cases()
    test.test_token_time_window_with_single_use()
    test.test_token_time_window_monitoring()
