"""Tests for Wave 17 P2: Promotion capability scope limitations."""

import hashlib

import pytest

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution" / "capability"))

from promotion_token import PromotionTokenStore, get_token_issuer, issue_promotion_token


class TestPromotionCapabilityScope:
    """Test promotion capability token scope limitations."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing state
        PromotionTokenStore.clear_all()
        self.issuer = get_token_issuer()

    def test_token_limited_to_pointer_updates(self):
        """Test that promotion tokens are limited to pointer updates only."""
        # Given - Issue promotion token
        token = issue_promotion_token(target_namespace="test_namespace", semantic_clock_tick=100)

        # When/Then - Token should only allow pointer_update action
        assert token.allowed_action == "pointer_update", "Token should only allow pointer_update action"

        # Should not allow other actions
        assert token.allowed_action != "file_write", "Token should not allow file_write"
        assert token.allowed_action != "config_change", "Token should not allow config_change"

    def test_token_namespace_scope_validation(self):
        """Test token namespace scope validation."""
        # Given - Token for specific namespace
        token = issue_promotion_token(target_namespace="specific_namespace", semantic_clock_tick=100)

        # When/Then - Should validate for correct namespace
        assert token.is_valid_for_namespace("specific_namespace"), "Should be valid for correct namespace"

        # Should not validate for wrong namespace
        assert not token.is_valid_for_namespace("wrong_namespace"), "Should not be valid for wrong namespace"

        assert not token.is_valid_for_namespace(""), "Should not be valid for empty namespace"

    def test_token_semantic_clock_window_enforcement(self):
        """Test token semantic clock window enforcement."""
        # Given - Token with specific window
        token = issue_promotion_token(
            target_namespace="test_namespace", semantic_clock_tick=100, window_size=10
        )

        # When/Then - Should be valid within window
        assert not token.is_expired(100), "Should not be expired at start"
        assert not token.is_expired(105), "Should not be expired in middle"
        assert not token.is_expired(110), "Should not be expired at end"

        # Should be expired outside window
        assert token.is_expired(111), "Should be expired after window"
        assert token.is_expired(150), "Should be expired far after window"

    def test_token_single_use_enforcement(self):
        """Test that promotion tokens are single-use."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="single_use_test", semantic_clock_tick=100)

        # When - Use token first time
        first_use = token.validate_scope_and_use()

        # Then - Should succeed first time
        assert first_use, "Token should validate on first use"

        # When - Try to use same token again
        second_use = token.validate_scope_and_use()

        # Then - Should fail second time
        assert not second_use, "Token should not validate on second use"

        # Verify nonce is marked as used
        assert PromotionTokenStore.is_nonce_used(token.single_use_nonce), "Nonce should be marked as used"

    def test_token_replay_digest_binding(self):
        """Test token replay digest binding."""
        # Given - Token with replay digest
        replay_digest = hashlib.sha256(b"replay_data").hexdigest()
        token = issue_promotion_token(
            target_namespace="replay_test", semantic_clock_tick=100, replay_digest=replay_digest
        )

        # When/Then - Token should be bound to replay digest
        assert token.replay_digest_binding == replay_digest, "Token should be bound to replay digest"

        # Different replay digest should create different token
        token2 = issue_promotion_token(
            target_namespace="replay_test", semantic_clock_tick=100, replay_digest="different_digest"
        )

        assert token.replay_digest_binding != token2.replay_digest_binding, (
            "Different replay digests should create different tokens"
        )

    def test_token_scope_validation_combination(self):
        """Test combination of all scope validations."""
        # Given - Token with all constraints
        token = issue_promotion_token(
            target_namespace="combo_test",
            semantic_clock_tick=100,
            window_size=10,
            replay_digest="test_digest",
        )

        # When/Then - All validations should pass
        assert token.allowed_action == "pointer_update", "Action scope check"
        assert token.is_valid_for_namespace("combo_test"), "Namespace scope check"
        assert not token.is_expired(105), "Time window check"
        assert token.validate_scope_and_use(), "Single-use check"

        # Second use should fail
        assert not token.validate_scope_and_use(), "Single-use should fail"

    def test_token_issuer_validation(self):
        """Test token issuer validation logic."""
        # Given - Token issuer
        current_tick = 200

        # When - Issue token
        token = self.issuer.issue_promotion_token(
            target_namespace="issuer_test", semantic_clock_tick=current_tick
        )

        # Then - Should validate through issuer
        assert self.issuer.validate_token(token, "issuer_test", current_tick), "Issuer should validate token"

        # Wrong namespace should fail
        assert not self.issuer.validate_token(token, "wrong_namespace", current_tick), (
            "Issuer should reject wrong namespace"
        )

        # Expired token should fail
        assert not self.issuer.validate_token(token, "issuer_test", current_tick + 101), (
            "Issuer should reject expired token"
        )

    def test_token_storage_and_retrieval(self):
        """Test token storage and retrieval."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="storage_test", semantic_clock_tick=100)

        # When - Retrieve from store
        retrieved = PromotionTokenStore.get_token(token.token_id)

        # Then - Should retrieve identical token
        assert retrieved is not None, "Token should be stored"
        assert retrieved.token_id == token.token_id, "Token ID should match"
        assert retrieved.target_namespace == token.target_namespace, "Namespace should match"
        assert retrieved.single_use_nonce == token.single_use_nonce, "Nonce should match"

    def test_token_revocation(self):
        """Test token revocation."""
        # Given - Issue token
        token = issue_promotion_token(target_namespace="revoke_test", semantic_clock_tick=100)

        # When - Revoke token
        revoked = PromotionTokenStore.revoke_token(token.token_id)

        # Then - Should be revoked
        assert revoked, "Token should be revoked"

        # Should not be retrievable
        retrieved = PromotionTokenStore.get_token(token.token_id)
        assert retrieved is None, "Revoked token should not be retrievable"

        # Revoking non-existent token should fail
        assert not PromotionTokenStore.revoke_token("non_existent"), "Should not revoke non-existent token"

    def test_multiple_tokens_different_scopes(self):
        """Test multiple tokens with different scopes."""
        # Given - Issue multiple tokens
        token1 = issue_promotion_token(target_namespace="namespace1", semantic_clock_tick=100)

        token2 = issue_promotion_token(target_namespace="namespace2", semantic_clock_tick=150)

        # When/Then - Tokens should have different scopes
        assert token1.target_namespace != token2.target_namespace, "Tokens should have different namespaces"

        assert token1.semantic_clock_window != token2.semantic_clock_window, (
            "Tokens should have different time windows"
        )

        # Each token should only validate for its namespace
        assert token1.validate_scope_and_use(), "Token1 should validate"
        assert token2.validate_scope_and_use(), "Token2 should validate"

        # But not for wrong namespaces
        token3 = issue_promotion_token(target_namespace="namespace3", semantic_clock_tick=200)

        assert not token3.is_valid_for_namespace("namespace1"), "Token3 should not validate for namespace1"
        assert not token3.is_valid_for_namespace("namespace2"), "Token3 should not validate for namespace2"


def test_req_p2_promotion_capability_scope():
    """Test P2 promotion capability scope requirements."""
    test = TestPromotionCapabilityScope()
    test.setup_method()

    # Core scope tests
    test.test_token_limited_to_pointer_updates()
    test.test_token_namespace_scope_validation()
    test.test_token_semantic_clock_window_enforcement()
    test.test_token_single_use_enforcement()

    # Advanced scope tests
    test.test_token_replay_digest_binding()
    test.test_token_scope_validation_combination()
    test.test_token_issuer_validation()

    # Storage and management tests
    test.test_token_storage_and_retrieval()
    test.test_token_revocation()
    test.test_multiple_tokens_different_scopes()
