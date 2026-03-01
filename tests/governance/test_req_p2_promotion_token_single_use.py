"""Tests for Wave 17 P2: Promotion token single-use enforcement."""

import pytest

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution" / "capability"))

from promotion_token import PromotionTokenIssuer, PromotionTokenStore, get_token_issuer, issue_promotion_token


class TestPromotionTokenSingleUse:
    """Test promotion token single-use enforcement."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing state
        PromotionTokenStore.clear_all()
        self.issuer = get_token_issuer()

    def test_token_single_use_basic(self):
        """Test basic single-use token behavior."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="single_use_basic", semantic_clock_tick=100)

        # When - Use token first time
        first_result = token.validate_scope_and_use()

        # Then - Should succeed
        assert first_result, "First use should succeed"

        # When - Try to use same token again
        second_result = token.validate_scope_and_use()

        # Then - Should fail
        assert not second_result, "Second use should fail"

    def test_nonce_tracking_across_tokens(self):
        """Test that nonces are tracked across different tokens."""
        # Given - Issue multiple tokens
        token1 = issue_promotion_token(target_namespace="nonce_test1", semantic_clock_tick=100)

        token2 = issue_promotion_token(target_namespace="nonce_test2", semantic_clock_tick=100)

        # When - Use both tokens
        result1 = token1.validate_scope_and_use()
        result2 = token2.validate_scope_and_use()

        # Then - Both should succeed (different nonces)
        assert result1, "Token1 should succeed"
        assert result2, "Token2 should succeed"

        # But second use of either should fail
        assert not token1.validate_scope_and_use(), "Token1 second use should fail"
        assert not token2.validate_scope_and_use(), "Token2 second use should fail"

    def test_nonce_uniqueness(self):
        """Test that each token gets a unique nonce."""
        # Given - Issue multiple tokens
        tokens = []
        for i in range(10):
            token = issue_promotion_token(target_namespace=f"unique_test_{i}", semantic_clock_tick=100)
            tokens.append(token)

        # When/Then - All nonces should be unique
        nonces = [token.single_use_nonce for token in tokens]
        assert len(set(nonces)) == len(nonces), "All nonces should be unique"

        # Each nonce should be non-empty
        for nonce in nonces:
            assert nonce, "Nonce should not be empty"
            assert len(nonce) > 0, "Nonce should have length"

    def test_nonce_persistence_across_validations(self):
        """Test that nonce usage persists across validations."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="persistence_test", semantic_clock_tick=100)

        # When - Use token
        token.validate_scope_and_use()

        # Then - Nonce should be marked as used
        assert PromotionTokenStore.is_nonce_used(token.single_use_nonce), "Nonce should be marked as used"

        # Even after creating new issuer instance
        new_issuer = PromotionTokenIssuer()
        assert PromotionTokenStore.is_nonce_used(token.single_use_nonce), "Nonce usage should persist"

    def test_single_use_with_issuer_validation(self):
        """Test single-use enforcement through issuer validation."""
        # Given - Issue token through issuer
        token = self.issuer.issue_promotion_token(
            target_namespace="issuer_single_use", semantic_clock_tick=100
        )

        # When - Validate through issuer first time
        first_validation = self.issuer.validate_token(token, "issuer_single_use", 100)

        # Then - Should succeed
        assert first_validation, "First validation through issuer should succeed"

        # When - Try to validate again
        second_validation = self.issuer.validate_token(token, "issuer_single_use", 100)

        # Then - Should fail
        assert not second_validation, "Second validation through issuer should fail"

    def test_single_use_with_different_validation_contexts(self):
        """Test single-use across different validation contexts."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="context_test", semantic_clock_tick=100)

        # When - Use token in direct validation
        direct_result = token.validate_scope_and_use()

        # Then - Should succeed
        assert direct_result, "Direct validation should succeed"

        # When - Try to use in issuer validation
        issuer_result = self.issuer.validate_token(token, "context_test", 100)

        # Then - Should fail (already used)
        assert not issuer_result, "Issuer validation should fail after direct use"

    def test_single_use_prevents_replay_attack(self):
        """Test that single-use prevents replay attacks."""
        # Given - Issue token and use it
        token = issue_promotion_token(target_namespace="replay_attack_test", semantic_clock_tick=100)

        # Simulate legitimate use
        legitimate_use = token.validate_scope_and_use()
        assert legitimate_use, "Legitimate use should succeed"

        # When - Attacker tries to replay the same token
        # (In a real attack, they'd capture and replay the token)
        replay_attempt = token.validate_scope_and_use()

        # Then - Replay should be blocked
        assert not replay_attempt, "Replay attack should be blocked"

    def test_single_use_with_time_window_expiration(self):
        """Test interaction between single-use and time window expiration."""
        # Given - Issue token with semantic_clock_tick that puts the window in the past
        # tick=100, window_size=5 -> window=(100, 105)
        # For token.validate_scope_and_use() to fail due to expiration,
        # we need semantic_clock_tick to be outside window (already past end)
        # Use tick=200 to issue so window=(200, 205), but stored tick=200,
        # then manually construct an expired token for this test
        import secrets

        from promotion_token import PromotionToken

        expired_token = PromotionToken(
            token_id=f"promo_{secrets.token_hex(8)}",
            target_namespace="time_single_use",
            semantic_clock_window=(50, 55),  # window ended at 55
            replay_digest_binding="",
            single_use_nonce=secrets.token_hex(16),
            guardian_signature="guardian_sig",
            semantic_clock_tick=100,  # current tick is 100, past window end 55
            allowed_action="pointer_update",
        )

        # When - Use after expiration (tick=100 > window_end=55)
        expired_use = expired_token.validate_scope_and_use()

        # Then - Should fail due to expiration
        assert not expired_use, "Expired token should not validate"

        # Even if we try to "use" it again, should still fail
        assert not expired_token.validate_scope_and_use(), "Expired token should not validate even on retry"

    def test_single_use_clear_all_resets_state(self):
        """Test that clear_all resets single-use state."""
        # Given - Issue and use token
        token = issue_promotion_token(target_namespace="clear_test", semantic_clock_tick=100)

        token.validate_scope_and_use()
        assert PromotionTokenStore.is_nonce_used(token.single_use_nonce), "Nonce should be marked as used"

        # When - Clear all state
        PromotionTokenStore.clear_all()

        # Then - Nonce should no longer be marked as used
        assert not PromotionTokenStore.is_nonce_used(token.single_use_nonce), (
            "Nonce should not be marked as used after clear"
        )

        # But the token object itself still remembers it was used
        # (This is expected behavior - the token object maintains its own state)

    def test_single_use_statistics_and_monitoring(self):
        """Test single-use statistics for monitoring."""
        # Given - Issue multiple tokens
        tokens = []
        for i in range(5):
            token = issue_promotion_token(target_namespace=f"stats_test_{i}", semantic_clock_tick=100)
            tokens.append(token)

        # When - Use some tokens
        used_count = 0
        for token in tokens[:3]:
            if token.validate_scope_and_use():
                used_count += 1

        # Then - Should track usage
        assert used_count == 3, "Should have used 3 tokens"

        # Check that used nonces are tracked
        used_nonces = 0
        for token in tokens:
            if PromotionTokenStore.is_nonce_used(token.single_use_nonce):
                used_nonces += 1

        assert used_nonces == 3, "Should have 3 used nonces"

    def test_single_use_error_handling(self):
        """Test error handling in single-use validation."""
        # Given - Token with invalid nonce (simulated)
        token = issue_promotion_token(target_namespace="error_test", semantic_clock_tick=100)

        # Manually mark nonce as used to test edge cases
        PromotionTokenStore.mark_nonce_used(token.single_use_nonce)

        # When/Then - Should handle gracefully
        assert not token.validate_scope_and_use(), "Should handle already used nonce gracefully"

        # Clear and try again
        PromotionTokenStore.clear_all()
        new_token = issue_promotion_token(target_namespace="error_test2", semantic_clock_tick=100)

        assert new_token.validate_scope_and_use(), "Should work normally after clear"


def test_req_p2_promotion_token_single_use():
    """Test P2 promotion token single-use requirements."""
    test = TestPromotionTokenSingleUse()
    test.setup_method()

    # Core single-use tests
    test.test_token_single_use_basic()
    test.test_nonce_tracking_across_tokens()
    test.test_nonce_uniqueness()
    test.test_nonce_persistence_across_validations()

    # Integration tests
    test.test_single_use_with_issuer_validation()
    test.test_single_use_with_different_validation_contexts()

    # Security tests
    test.test_single_use_prevents_replay_attack()
    test.test_single_use_with_time_window_expiration()

    # Management tests
    test.test_single_use_clear_all_resets_state()
    test.test_single_use_statistics_and_monitoring()
    test.test_single_use_error_handling()
