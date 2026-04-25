"""Tests for registry_validator.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.governance.registry_validator import (
    ValidationResult,
    RegistryValidator,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_valid(self):
        """Test ValidationResult with all valid flags."""
        result = ValidationResult(
            is_valid=True,
            identity_valid=True,
            model_allowed=True,
            execution_mode_locked=True,
            digest_match=True,
            acl_verified=True,
        )
        assert result.is_valid is True
        assert result.identity_valid is True
        assert result.model_allowed is True
        assert result.execution_mode_locked is True
        assert result.digest_match is True
        assert result.acl_verified is True
        assert result.rejection_reason == ""

    def test_validation_result_invalid(self):
        """Test ValidationResult with some invalid flags."""
        result = ValidationResult(
            is_valid=False,
            identity_valid=True,
            model_allowed=False,
            execution_mode_locked=True,
            digest_match=True,
            acl_verified=True,
            rejection_reason="model_not_allowed",
        )
        assert result.is_valid is False
        assert result.model_allowed is False
        assert result.rejection_reason == "model_not_allowed"

    def test_validation_result_multiple_reasons(self):
        """Test ValidationResult with multiple rejection reasons."""
        result = ValidationResult(
            is_valid=False,
            identity_valid=False,
            model_allowed=False,
            execution_mode_locked=False,
            digest_match=False,
            acl_verified=False,
            rejection_reason="identity_not_registered;model_not_allowed;execution_mode_locked;digest_mismatch;acl_denied",
        )
        assert result.is_valid is False
        assert "identity_not_registered" in result.rejection_reason
        assert "model_not_allowed" in result.rejection_reason
        assert "execution_mode_locked" in result.rejection_reason
        assert "digest_mismatch" in result.rejection_reason
        assert "acl_denied" in result.rejection_reason


class TestRegistryValidator:
    """Tests for RegistryValidator class."""

    def test_validator_init(self):
        """Test RegistryValidator initialization."""
        validator = RegistryValidator()
        assert validator._allowed_models == set()
        assert validator._allowed_identities == set()
        assert validator._execution_mode_locks == {}
        assert validator._digest_registry == {}
        assert validator._acl_rules == []

    def test_validate_all_valid(self):
        """Test validate returns valid when all checks pass."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        validator.add_acl_rule("user1", "/api/")
        
        result = validator.validate(
            identity="user1",
            model="model1",
            requested_mode="read",
            digest="digest123",
            resource="/api/data",
        )
        
        assert result.is_valid is True
        assert result.identity_valid is True
        assert result.model_allowed is True
        assert result.execution_mode_locked is True
        assert result.digest_match is True
        assert result.acl_verified is True

    def test_validate_identity_not_registered(self):
        """Test validate rejects when identity not registered."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        
        result = validator.validate(
            identity="user2",
            model="model1",
            requested_mode="read",
            digest="digest123",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        assert result.identity_valid is False
        assert "identity_not_registered" in result.rejection_reason

    def test_validate_model_not_allowed(self):
        """Test validate rejects when model not allowed."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        validator.add_acl_rule("user1", "/api/")
        
        result = validator.validate(
            identity="user1",
            model="model2",
            requested_mode="read",
            digest="digest123",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        assert result.model_allowed is False
        assert "model_not_allowed" in result.rejection_reason

    def test_validate_execution_mode_locked(self):
        """Test validate rejects when execution mode locked."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        validator.add_acl_rule("user1", "/api/")
        
        result = validator.validate(
            identity="user1",
            model="model1",
            requested_mode="write",
            digest="digest123",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        assert result.execution_mode_locked is False
        assert "execution_mode_locked" in result.rejection_reason

    def test_validate_digest_mismatch(self):
        """Test validate rejects when digest mismatch."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        validator.add_acl_rule("user1", "/api/")
        
        result = validator.validate(
            identity="user1",
            model="model1",
            requested_mode="read",
            digest="wrong_digest",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        assert result.digest_match is False
        assert "digest_mismatch" in result.rejection_reason

    def test_validate_acl_denied(self):
        """Test validate rejects when ACL denies access."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        validator.add_acl_rule("user1", "/admin/")
        
        result = validator.validate(
            identity="user1",
            model="model1",
            requested_mode="read",
            digest="digest123",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        assert result.acl_verified is False
        assert "acl_denied" in result.rejection_reason

    def test_validate_open_registries(self):
        """Test validate passes when all registries are open (empty)."""
        validator = RegistryValidator()
        
        result = validator.validate(
            identity="any_user",
            model="any_model",
            requested_mode="any_mode",
            digest="any_digest",
            resource="any_resource",
        )
        
        assert result.is_valid is True
        assert result.identity_valid is True
        assert result.model_allowed is True
        assert result.execution_mode_locked is True
        assert result.digest_match is True
        assert result.acl_verified is True

    def test_validate_multiple_failures(self):
        """Test validate accumulates multiple rejection reasons."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        validator.register_allowed_model("model1")
        validator.lock_execution_mode("user1", "read")
        validator.register_digest("user1", "digest123")
        
        result = validator.validate(
            identity="user2",
            model="model2",
            requested_mode="write",
            digest="wrong_digest",
            resource="/api/data",
        )
        
        assert result.is_valid is False
        reasons = result.rejection_reason.split(";")
        assert "identity_not_registered" in reasons
        assert "model_not_allowed" in reasons
        assert "execution_mode_locked" in reasons
        assert "digest_mismatch" in reasons
        assert "acl_denied" in reasons

    def test_validate_identity_open_registry(self):
        """Test _validate_identity returns True when registry is open."""
        validator = RegistryValidator()
        
        assert validator._validate_identity("any_user") is True

    def test_validate_identity_registered(self):
        """Test _validate_identity returns True when identity is registered."""
        validator = RegistryValidator()
        validator.register_allowed_identity("user1")
        
        assert validator._validate_identity("user1") is True
        assert validator._validate_identity("user2") is False

    def test_validate_model_open_registry(self):
        """Test _validate_model returns True when registry is open."""
        validator = RegistryValidator()
        
        assert validator._validate_model("any_model") is True

    def test_validate_model_allowed(self):
        """Test _validate_model returns True when model is allowed."""
        validator = RegistryValidator()
        validator.register_allowed_model("model1")
        
        assert validator._validate_model("model1") is True
        assert validator._validate_model("model2") is False

    def test_validate_execution_mode_no_lock(self):
        """Test _validate_execution_mode returns True when no lock."""
        validator = RegistryValidator()
        
        assert validator._validate_execution_mode("user1", "any_mode") is True

    def test_validate_execution_mode_matches(self):
        """Test _validate_execution_mode returns True when mode matches lock."""
        validator = RegistryValidator()
        validator.lock_execution_mode("user1", "read")
        
        assert validator._validate_execution_mode("user1", "read") is True
        assert validator._validate_execution_mode("user1", "write") is False

    def test_validate_digest_open_registry(self):
        """Test _validate_digest returns True when registry is open."""
        validator = RegistryValidator()
        
        assert validator._validate_digest("user1", "any_digest") is True

    def test_validate_digest_match(self):
        """Test _validate_digest returns True when digest matches."""
        validator = RegistryValidator()
        validator.register_digest("user1", "digest123")
        
        assert validator._validate_digest("user1", "digest123") is True
        assert validator._validate_digest("user1", "wrong_digest") is False

    def test_validate_acl_open_registry(self):
        """Test _validate_acl returns True when ACL is open."""
        validator = RegistryValidator()
        
        assert validator._validate_acl("user1", "any_resource") is True

    def test_validate_acl_allowed(self):
        """Test _validate_acl returns True when ACL allows access."""
        validator = RegistryValidator()
        validator.add_acl_rule("user1", "/api/")
        
        assert validator._validate_acl("user1", "/api/data") is True
        assert validator._validate_acl("user1", "/admin/") is False

    def test_register_allowed_model(self):
        """Test register_allowed_model adds model to allowed set."""
        validator = RegistryValidator()
        
        validator.register_allowed_model("model1")
        assert "model1" in validator._allowed_models
        assert "model2" not in validator._allowed_models

    def test_register_allowed_identity(self):
        """Test register_allowed_identity adds identity to allowed set."""
        validator = RegistryValidator()
        
        validator.register_allowed_identity("user1")
        assert "user1" in validator._allowed_identities
        assert "user2" not in validator._allowed_identities

    def test_lock_execution_mode(self):
        """Test lock_execution_mode sets mode for identity."""
        validator = RegistryValidator()
        
        validator.lock_execution_mode("user1", "read")
        assert validator._execution_mode_locks["user1"] == "read"

    def test_lock_execution_mode_overwrite(self):
        """Test lock_execution_mode overwrites existing mode."""
        validator = RegistryValidator()
        validator.lock_execution_mode("user1", "read")
        
        validator.lock_execution_mode("user1", "write")
        assert validator._execution_mode_locks["user1"] == "write"

    def test_register_digest(self):
        """Test register_digest sets digest for identity."""
        validator = RegistryValidator()
        
        validator.register_digest("user1", "digest123")
        assert validator._digest_registry["user1"] == "digest123"

    def test_register_digest_overwrite(self):
        """Test register_digest overwrites existing digest."""
        validator = RegistryValidator()
        validator.register_digest("user1", "digest123")
        
        validator.register_digest("user1", "new_digest")
        assert validator._digest_registry["user1"] == "new_digest"

    def test_add_acl_rule(self):
        """Test add_acl_rule adds rule to list."""
        validator = RegistryValidator()
        
        validator.add_acl_rule("user1", "/api/")
        assert ("user1", "/api/") in validator._acl_rules
        assert len(validator._acl_rules) == 1

    def test_add_acl_rule_multiple(self):
        """Test add_acl_rule can add multiple rules."""
        validator = RegistryValidator()
        
        validator.add_acl_rule("user1", "/api/")
        validator.add_acl_rule("user2", "/admin/")
        validator.add_acl_rule("user1", "/data/")
        
        assert len(validator._acl_rules) == 3
