"""Tests for policy_hash_enforcer.py module."""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
    PolicyHashViolation,
    PolicyHashValidationResult,
    PolicyHashEnforcer,
    _safe_str,
)


class TestPolicyHashViolation:
    """Tests for PolicyHashViolation exception."""

    def test_policy_hash_violation_creation(self):
        """Test PolicyHashViolation can be raised and caught."""
        with pytest.raises(PolicyHashViolation) as exc_info:
            raise PolicyHashViolation("Test violation", packet_id="packet123")
        
        assert "Test violation" in str(exc_info.value)
        assert "packet123" in str(exc_info.value)

    def test_policy_hash_violation_default_packet_id(self):
        """Test PolicyHashViolation with default packet_id."""
        with pytest.raises(PolicyHashViolation) as exc_info:
            raise PolicyHashViolation("Test violation")
        
        assert "Test violation" in str(exc_info.value)


class TestPolicyHashValidationResult:
    """Tests for PolicyHashValidationResult dataclass."""

    def test_policy_hash_validation_result_creation(self):
        """Test PolicyHashValidationResult dataclass initialization."""
        result = PolicyHashValidationResult(
            passed=True,
            packet_id="packet123",
            policy_hash_present=True,
            policy_hash_matches=True,
            active_root="abc123",
            packet_hash="abc123",
            reason="Valid",
        )
        
        assert result.passed is True
        assert result.packet_id == "packet123"
        assert result.policy_hash_present is True
        assert result.policy_hash_matches is True
        assert result.active_root == "abc123"
        assert result.packet_hash == "abc123"
        assert result.reason == "Valid"

    def test_policy_hash_validation_result_format_pass(self):
        """Test PolicyHashValidationResult.format() for passing result."""
        result = PolicyHashValidationResult(
            passed=True,
            packet_id="packet123",
            policy_hash_present=True,
            policy_hash_matches=True,
            active_root="abc123",
            packet_hash="abc123",
        )
        
        formatted = result.format()
        assert "PASS" in formatted
        assert "packet123" in formatted
        assert "present=True" in formatted
        assert "matches=True" in formatted

    def test_policy_hash_validation_result_format_fail(self):
        """Test PolicyHashValidationResult.format() for failing result."""
        result = PolicyHashValidationResult(
            passed=False,
            packet_id="packet123",
            policy_hash_present=False,
            policy_hash_matches=False,
            active_root="abc123",
            packet_hash="",
            reason="Missing hash",
        )
        
        formatted = result.format()
        assert "FAIL" in formatted
        assert "packet123" in formatted
        assert "present=False" in formatted
        assert "Missing hash" in formatted


class TestSafeStr:
    """Tests for _safe_str helper function."""

    def test_safe_str_with_string(self):
        """Test _safe_str returns string unchanged."""
        assert _safe_str("test") == "test"

    def test_safe_str_with_none(self):
        """Test _safe_str returns empty string for None."""
        assert _safe_str(None) == ""

    def test_safe_str_with_int(self):
        """Test _safe_str converts int to string."""
        assert _safe_str(123) == "123"


class TestPolicyHashEnforcer:
    """Tests for PolicyHashEnforcer class."""

    def test_enforcer_init_valid_root(self):
        """Test PolicyHashEnforcer initialization with valid root."""
        enforcer = PolicyHashEnforcer("abc123def456")
        
        assert enforcer.active_merkle_root == "abc123def456"

    def test_enforcer_init_empty_root(self):
        """Test PolicyHashEnforcer raises on empty root."""
        with pytest.raises(ValueError) as exc_info:
            PolicyHashEnforcer("")
        
        assert "non-empty active_merkle_root" in str(exc_info.value)

    def test_enforcer_init_whitespace_root(self):
        """Test PolicyHashEnforcer raises on whitespace-only root."""
        with pytest.raises(ValueError) as exc_info:
            PolicyHashEnforcer("   ")
        
        assert "non-empty active_merkle_root" in str(exc_info.value)

    def test_enforcer_init_invalid_mode(self):
        """Test PolicyHashEnforcer raises on invalid mode."""
        with pytest.raises(ValueError) as exc_info:
            PolicyHashEnforcer("abc123", mode="INVALID")
        
        assert "Unknown mode" in str(exc_info.value)

    def test_enforcer_init_log_only_mode(self):
        """Test PolicyHashEnforcer initialization with LOG_ONLY mode."""
        enforcer = PolicyHashEnforcer("abc123", mode="LOG_ONLY")
        
        assert enforcer.active_merkle_root == "abc123"

    def test_enforce_valid_packet(self):
        """Test enforce passes with valid packet."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "abc123"
        
        # Should not raise
        enforcer.enforce(MockPacket())

    def test_enforce_missing_hash_hard_fail(self):
        """Test enforce raises when policy_hash is missing (HARD_FAIL mode)."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = ""
        
        with pytest.raises(PolicyHashViolation) as exc_info:
            enforcer.enforce(MockPacket())
        
        assert "policy_hash is absent or empty" in str(exc_info.value)

    def test_enforce_missing_hash_log_only(self):
        """Test enforce logs but does not raise when policy_hash is missing (LOG_ONLY mode)."""
        enforcer = PolicyHashEnforcer("abc123", mode="LOG_ONLY")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = ""
        
        # Should not raise in LOG_ONLY mode
        enforcer.enforce(MockPacket())

    def test_enforce_hash_mismatch_hard_fail(self):
        """Test enforce raises when policy_hash does not match (HARD_FAIL mode)."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "wrong_hash"
        
        with pytest.raises(PolicyHashViolation) as exc_info:
            enforcer.enforce(MockPacket())
        
        assert "policy_hash mismatch" in str(exc_info.value)

    def test_enforce_hash_mismatch_log_only(self):
        """Test enforce logs but does not raise when hash mismatch (LOG_ONLY mode)."""
        enforcer = PolicyHashEnforcer("abc123", mode="LOG_ONLY")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "wrong_hash"
        
        # Should not raise in LOG_ONLY mode
        enforcer.enforce(MockPacket())

    def test_enforce_case_insensitive(self):
        """Test enforce is case-insensitive for hash comparison."""
        enforcer = PolicyHashEnforcer("ABC123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "abc123"  # Lowercase
        
        # Should not raise (case-insensitive)
        enforcer.enforce(MockPacket())

    def test_validate_valid_packet(self):
        """Test validate returns passing result for valid packet."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "abc123"
        
        result = enforcer.validate(MockPacket())
        
        assert result.passed is True
        assert result.packet_id == "packet123"
        assert result.policy_hash_present is True
        assert result.policy_hash_matches is True
        assert result.active_root == "abc123"

    def test_validate_missing_hash(self):
        """Test validate returns failing result when policy_hash is missing."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = ""
        
        result = enforcer.validate(MockPacket())
        
        assert result.passed is False
        assert result.policy_hash_present is False
        assert result.policy_hash_matches is False
        assert "absent or empty" in result.reason

    def test_validate_hash_mismatch(self):
        """Test validate returns failing result when hash does not match."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = "packet123"
            policy_hash = "wrong_hash"
        
        result = enforcer.validate(MockPacket())
        
        assert result.passed is False
        assert result.policy_hash_present is True
        assert result.policy_hash_matches is False
        assert "mismatch" in result.reason

    def test_validate_missing_instruction_id(self):
        """Test validate handles missing instruction_id gracefully."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            policy_hash = "abc123"
            # instruction_id missing
        
        result = enforcer.validate(MockPacket())
        
        assert result.passed is True  # Hash matches, ID is not required for validation
        assert result.packet_id == ""

    def test_validate_none_attributes(self):
        """Test validate handles None attributes gracefully."""
        enforcer = PolicyHashEnforcer("abc123")
        
        class MockPacket:
            instruction_id = None
            policy_hash = None
        
        result = enforcer.validate(MockPacket())
        
        assert result.passed is False
        assert result.policy_hash_present is False
        assert result.packet_id == ""

    def test_derive_root_simple_dict(self):
        """Test derive_root computes SHA-256 of policy config dict."""
        policy_config = {"key1": "value1", "key2": "value2"}
        
        root = PolicyHashEnforcer.derive_root(policy_config)
        
        assert isinstance(root, str)
        assert len(root) == 64  # SHA-256 hex length

    def test_derive_root_deterministic(self):
        """Test derive_root produces same hash for same config."""
        policy_config = {"key": "value"}
        
        root1 = PolicyHashEnforcer.derive_root(policy_config)
        root2 = PolicyHashEnforcer.derive_root(policy_config)
        
        assert root1 == root2

    def test_derive_root_order_independent(self):
        """Test derive_root is independent of key order."""
        config1 = {"a": 1, "b": 2}
        config2 = {"b": 2, "a": 1}
        
        root1 = PolicyHashEnforcer.derive_root(config1)
        root2 = PolicyHashEnforcer.derive_root(config2)
        
        assert root1 == root2

    def test_derive_root_nested_dict(self):
        """Test derive_root handles nested dicts."""
        policy_config = {"outer": {"inner": "value"}}
        
        root = PolicyHashEnforcer.derive_root(policy_config)
        
        assert isinstance(root, str)
        assert len(root) == 64

    def test_derive_root_with_lists(self):
        """Test derive_root handles lists in config."""
        policy_config = {"items": ["a", "b", "c"]}
        
        root = PolicyHashEnforcer.derive_root(policy_config)
        
        assert isinstance(root, str)
        assert len(root) == 64

    def test_derive_root_case_sensitive(self):
        """Test derive_root is case-sensitive for values."""
        config1 = {"key": "Value"}
        config2 = {"key": "value"}
        
        root1 = PolicyHashEnforcer.derive_root(config1)
        root2 = PolicyHashEnforcer.derive_root(config2)
        
        assert root1 != root2  # Different case should produce different hash
