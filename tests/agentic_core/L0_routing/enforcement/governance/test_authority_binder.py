"""Tests for authority_binder.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.governance.authority_binder import (
    Identity,
    Credentials,
    AuthorityContext,
    AuthorityBinder,
)


class TestIdentity:
    """Tests for Identity dataclass."""

    def test_identity_creation(self):
        """Test Identity creation with all fields."""
        identity = Identity(actor_id="actor1", role="admin", tenant_id="tenant1")
        assert identity.actor_id == "actor1"
        assert identity.role == "admin"
        assert identity.tenant_id == "tenant1"

    def test_identity_default_tenant(self):
        """Test Identity with default tenant_id."""
        identity = Identity(actor_id="actor1", role="admin")
        assert identity.tenant_id == "default"

    def test_identity_to_hash(self):
        """Test Identity to_hash method."""
        identity = Identity(actor_id="actor1", role="admin", tenant_id="tenant1")
        hash_val = identity.to_hash()
        assert isinstance(hash_val, str)
        assert len(hash_val) == 16  # Truncated SHA-256

    def test_identity_to_hash_deterministic(self):
        """Test Identity to_hash is deterministic."""
        identity = Identity(actor_id="actor1", role="admin")
        hash1 = identity.to_hash()
        hash2 = identity.to_hash()
        assert hash1 == hash2

    def test_identity_to_hash_different_inputs(self):
        """Test Identity to_hash differs for different inputs."""
        identity1 = Identity(actor_id="actor1", role="admin")
        identity2 = Identity(actor_id="actor2", role="admin")
        hash1 = identity1.to_hash()
        hash2 = identity2.to_hash()
        assert hash1 != hash2


class TestCredentials:
    """Tests for Credentials dataclass."""

    def test_credentials_creation(self):
        """Test Credentials creation with all fields."""
        credentials = Credentials(
            token="token123",
            signature="sig456",
            expiry=1234567890.0,
            scopes=["read", "write"],
        )
        assert credentials.token == "token123"
        assert credentials.signature == "sig456"
        assert credentials.expiry == 1234567890.0
        assert credentials.scopes == ["read", "write"]

    def test_credentials_defaults(self):
        """Test Credentials with default values."""
        credentials = Credentials()
        assert credentials.token == ""
        assert credentials.signature == ""
        assert credentials.expiry == 0.0
        assert credentials.scopes == []


class TestAuthorityContext:
    """Tests for AuthorityContext dataclass."""

    def test_authority_context_creation(self):
        """Test AuthorityContext creation with all fields."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(token="token123")
        context = AuthorityContext(
            identity=identity,
            credentials=credentials,
            policy_hash="policy_hash1",
            compliance_hash="compliance_hash1",
            capability_tokens=["token1", "token2"],
            bound_at=1234567890.0,
        )
        assert context.identity == identity
        assert context.credentials == credentials
        assert context.policy_hash == "policy_hash1"
        assert context.compliance_hash == "compliance_hash1"
        assert context.capability_tokens == ["token1", "token2"]
        assert context.bound_at == 1234567890.0

    def test_authority_context_defaults(self):
        """Test AuthorityContext with default values."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials()
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.policy_hash == ""
        assert context.compliance_hash == ""
        assert context.capability_tokens == []
        assert context.bound_at == 0.0

    def test_is_authenticated_true(self):
        """Test is_authenticated returns True when authenticated."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(token="token123")
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.is_authenticated() is True

    def test_is_authenticated_false_no_actor_id(self):
        """Test is_authenticated returns False when no actor_id."""
        identity = Identity(actor_id="", role="admin")
        credentials = Credentials(token="token123")
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.is_authenticated() is False

    def test_is_authenticated_false_no_token(self):
        """Test is_authenticated returns False when no token."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(token="")
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.is_authenticated() is False

    def test_has_scope_true(self):
        """Test has_scope returns True when scope exists."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(scopes=["read", "write"])
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.has_scope("read") is True
        assert context.has_scope("write") is True

    def test_has_scope_false(self):
        """Test has_scope returns False when scope doesn't exist."""
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(scopes=["read"])
        context = AuthorityContext(identity=identity, credentials=credentials)
        assert context.has_scope("write") is False

    def test_to_audit_record(self):
        """Test to_audit_record returns audit-safe record."""
        identity = Identity(actor_id="actor1", role="admin", tenant_id="tenant1")
        credentials = Credentials(scopes=["read"])
        context = AuthorityContext(
            identity=identity,
            credentials=credentials,
            policy_hash="policy_hash1",
            bound_at=1234567890.0,
        )
        record = context.to_audit_record()
        
        assert "identity_hash" in record
        assert record["role"] == "admin"
        assert record["tenant_id"] == "tenant1"
        assert record["policy_hash"] == "policy_hash1"
        assert record["scopes"] == ["read"]
        assert record["bound_at"] == 1234567890.0
        # Sensitive data should not be in audit record
        assert "token" not in record
        assert "signature" not in record


class TestAuthorityBinder:
    """Tests for AuthorityBinder class."""

    def test_binder_init(self):
        """Test AuthorityBinder initialization."""
        binder = AuthorityBinder()
        assert binder._identity_registry == {}
        assert binder._policy_registry == {}
        assert binder._compliance_registry == {}

    def test_bind_with_registered_identity(self):
        """Test bind with registered identity."""
        binder = AuthorityBinder()
        identity = Identity(actor_id="actor1", role="admin")
        binder.register_identity(identity)
        
        credentials = Credentials(token="token123")
        context = binder.bind("actor1", credentials)
        
        assert context.identity == identity
        assert context.credentials == credentials
        assert context.identity.role == "admin"

    def test_bind_with_unregistered_identity(self):
        """Test bind with unregistered identity uses default."""
        binder = AuthorityBinder()
        
        credentials = Credentials(token="token123")
        context = binder.bind("actor1", credentials)
        
        assert context.identity.actor_id == "actor1"
        assert context.identity.role == "unknown"

    def test_bind_with_policy_hash(self):
        """Test bind with policy_hash."""
        binder = AuthorityBinder()
        binder.register_policy("default", "policy_hash1")
        
        credentials = Credentials(token="token123")
        context = binder.bind("actor1", credentials, policy_hash="custom_policy")
        
        assert context.policy_hash == "custom_policy"

    def test_bind_with_default_policy(self):
        """Test bind uses default policy when none provided."""
        binder = AuthorityBinder()
        binder.register_policy("default", "policy_hash1")
        
        credentials = Credentials(token="token123")
        context = binder.bind("actor1", credentials)
        
        assert context.policy_hash == "policy_hash1"
        assert context.compliance_hash == ""  # No default compliance registered

    def test_register_identity(self):
        """Test register_identity stores identity."""
        binder = AuthorityBinder()
        identity = Identity(actor_id="actor1", role="admin")
        binder.register_identity(identity)
        
        assert "actor1" in binder._identity_registry
        assert binder._identity_registry["actor1"] == identity

    def test_register_policy(self):
        """Test register_policy stores policy hash."""
        binder = AuthorityBinder()
        binder.register_policy("policy1", "hash1")
        
        assert "policy1" in binder._policy_registry
        assert binder._policy_registry["policy1"] == "hash1"

    def test_verify_binding_valid(self):
        """Test verify_binding returns True for valid context."""
        binder = AuthorityBinder()
        identity = Identity(actor_id="actor1", role="admin")
        binder.register_identity(identity)
        binder.register_policy("default", "policy_hash1")
        
        credentials = Credentials(token="token123")
        context = binder.bind("actor1", credentials)
        
        assert binder.verify_binding(context) is True

    def test_verify_binding_unregistered_identity(self):
        """Test verify_binding returns False for unregistered identity."""
        binder = AuthorityBinder()
        binder.register_policy("default", "policy_hash1")
        
        identity = Identity(actor_id="actor1", role="admin")
        credentials = Credentials(token="token123")
        context = AuthorityContext(identity=identity, credentials=credentials, policy_hash="policy_hash1")
        
        assert binder.verify_binding(context) is False

    def test_verify_binding_invalid_policy(self):
        """Test verify_binding returns False for invalid policy hash."""
        binder = AuthorityBinder()
        identity = Identity(actor_id="actor1", role="admin")
        binder.register_identity(identity)
        binder.register_policy("default", "policy_hash1")
        
        credentials = Credentials(token="token123")
        context = AuthorityContext(identity=identity, credentials=credentials, policy_hash="invalid_policy")
        
        assert binder.verify_binding(context) is False
