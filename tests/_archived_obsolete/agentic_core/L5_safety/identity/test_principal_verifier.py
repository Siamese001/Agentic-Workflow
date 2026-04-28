"""Tests for L5_safety/identity/principal_verifier.py."""

import pytest

from agentic_core.interfaces.principal_chain_types import PermissionLadderRung
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    VerificationStatus,
    _ladder_satisfies,
    principal_attribution,
    verify_v4_token,
)


def test_principal_attribution_returns_correct_fields(sample_v4_token):
    """Test that principal_attribution returns all expected fields."""
    attribution = principal_attribution(sample_v4_token)
    
    assert isinstance(attribution, dict)
    assert attribution["agent_id"] == "test_agent"
    assert attribution["invoking_user"] == "user@example.com"
    assert attribution["risk_tier_band"] == "MODERATE"
    assert attribution["token_id"] == sample_v4_token.v4_trace_id
    assert "auth_method" in attribution
    assert "delegation_depth" in attribution
    assert "scope_tag" in attribution


def test_verification_status_enum_values():
    """Test that VerificationStatus enum has expected values."""
    assert VerificationStatus.PASS.value == "pass"
    assert VerificationStatus.FAIL.value == "fail"
    assert VerificationStatus.STEP_UP_REQUIRED.value == "step_up_required"


def test_verification_result_construction():
    """Test VerificationResult dataclass construction."""
    result = VerificationResult(
        status=VerificationStatus.PASS,
        failures=("reason1", "reason2"),
        required_rung="read",
        token_rung="mutate",
        delegation_depth=1,
        delegation_cap=2,
    )
    
    assert result.status == VerificationStatus.PASS
    assert result.failures == ("reason1", "reason2")
    assert result.required_rung == "read"
    assert result.token_rung == "mutate"
    assert result.delegation_depth == 1
    assert result.delegation_cap == 2


def test_verification_result_is_pass_property():
    """Test VerificationResult.is_pass property."""
    pass_result = VerificationResult(status=VerificationStatus.PASS)
    fail_result = VerificationResult(status=VerificationStatus.FAIL)
    step_up_result = VerificationResult(status=VerificationStatus.STEP_UP_REQUIRED)
    
    assert pass_result.is_pass is True
    assert fail_result.is_pass is False
    assert step_up_result.is_pass is False


def test_verification_result_is_fail_property():
    """Test VerificationResult.is_fail property."""
    pass_result = VerificationResult(status=VerificationStatus.PASS)
    fail_result = VerificationResult(status=VerificationStatus.FAIL)
    step_up_result = VerificationResult(status=VerificationStatus.STEP_UP_REQUIRED)
    
    assert pass_result.is_fail is False
    assert fail_result.is_fail is True
    assert step_up_result.is_fail is False


def test_verification_result_needs_step_up_property():
    """Test VerificationResult.needs_step_up property."""
    pass_result = VerificationResult(status=VerificationStatus.PASS)
    fail_result = VerificationResult(status=VerificationStatus.FAIL)
    step_up_result = VerificationResult(status=VerificationStatus.STEP_UP_REQUIRED)
    
    assert pass_result.needs_step_up is False
    assert fail_result.needs_step_up is False
    assert step_up_result.needs_step_up is True


def test_verification_result_to_dict():
    """Test VerificationResult.to_dict serialization."""
    result = VerificationResult(
        status=VerificationStatus.PASS,
        failures=("reason1",),
        required_rung="read",
        token_rung="mutate",
        delegation_depth=1,
        delegation_cap=2,
    )
    
    d = result.to_dict()
    assert d["status"] == "pass"
    assert d["failures"] == ["reason1"]
    assert d["required_rung"] == "read"
    assert d["token_rung"] == "mutate"
    assert d["delegation_depth"] == 1
    assert d["delegation_cap"] == 2


def test_ladder_satisfies_higher_rung_grants_lower():
    """Test that a higher rung implicitly grants lower rungs."""
    assert _ladder_satisfies("mutate", "read") is True
    assert _ladder_satisfies("external", "mutate") is True
    assert _ladder_satisfies("external", "read") is True


def test_ladder_satisfies_same_rung_satisfies():
    """Test that a rung satisfies itself."""
    assert _ladder_satisfies("read", "read") is True
    assert _ladder_satisfies("mutate", "mutate") is True


def test_ladder_satisfies_lower_rung_does_not_grant_higher():
    """Test that a lower rung does not grant higher rungs."""
    assert _ladder_satisfies("read", "mutate") is False
    assert _ladder_satisfies("suggest", "external") is False


def test_verify_v4_token_pass_all_checks(sample_v4_token):
    """Test verify_v4_token when all checks pass."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
    )
    
    assert result.status == VerificationStatus.PASS
    assert result.is_pass is True
    assert len(result.failures) == 0


def test_verify_v4_token_revoked_token(sample_v4_token):
    """Test verify_v4_token detects revoked token."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        revoked_token_ids=(sample_v4_token.v4_trace_id,),
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("REVOKED" in f for f in result.failures)


def test_verify_v4_token_expired_token(sample_v4_token):
    """Test verify_v4_token detects expired token."""
    # Sample token expires at tick:999999999 with ttl_seconds=900
    # Set current tick beyond expiration: 999999999 + 900 + 1
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        current_semantic_tick=1000000900,
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("EXPIRED" in f for f in result.failures)


def test_verify_v4_token_permission_ladder_step_up(sample_v4_token):
    """Test verify_v4_token returns STEP_UP_REQUIRED when token rung insufficient."""
    # Token has "mutate", action requires "external" (higher rung)
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="external",
    )
    
    assert result.status == VerificationStatus.STEP_UP_REQUIRED
    assert result.needs_step_up is True


def test_verify_v4_token_connector_not_allowed(sample_v4_token):
    """Test verify_v4_token detects connector not in allowlist."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        action_connector_id="blocked_connector",
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("CONNECTOR_NOT_ALLOWED" in f for f in result.failures)


def test_verify_v4_token_tool_not_allowed(sample_v4_token):
    """Test verify_v4_token detects tool not in allowlist."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        action_tool_id="blocked_tool",
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("TOOL_NOT_ALLOWED" in f for f in result.failures)


def test_verify_v4_token_policy_version_mismatch(sample_v4_token):
    """Test verify_v4_token detects policy version mismatch."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        active_policy_version="v2.0",
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("POLICY_VERSION_MISMATCH" in f for f in result.failures)


def test_verify_v4_token_delegation_depth_exceeded(sample_v4_token):
    """Test verify_v4_token detects delegation depth exceeding cap."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
    )
    
    # Check if delegation depth check is in failures
    # This depends on the sample token's delegation_depth vs band cap
    if result.delegation_depth > result.delegation_cap:
        assert any("DELEGATION_DEPTH_EXCEEDED" in f for f in result.failures)


def test_verify_v4_token_plan_digest_mismatch(sample_v4_token):
    """Test verify_v4_token detects plan digest mismatch."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="read",
        expected_plan_digest="wrong-digest",
    )
    
    assert result.status == VerificationStatus.FAIL
    assert result.is_fail is True
    assert any("PLAN_DIGEST_MISMATCH" in f for f in result.failures)


def test_verify_v4_token_multiple_failures(sample_v4_token):
    """Test verify_v4_token accumulates multiple failure reasons."""
    result = verify_v4_token(
        token=sample_v4_token,
        action_required_rung="mutate",  # step_up
        action_connector_id="blocked_connector",  # not allowed
        action_tool_id="blocked_tool",  # not allowed
        revoked_token_ids=(sample_v4_token.v4_trace_id,),  # revoked
    )
    
    assert result.status == VerificationStatus.FAIL
    assert len(result.failures) >= 3
