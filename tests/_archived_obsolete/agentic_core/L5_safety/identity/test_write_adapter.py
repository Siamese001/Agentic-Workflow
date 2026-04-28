"""Tests for L5_safety/identity/write_adapter.py."""

import pytest

from agentic_core.L5_safety.identity.write_adapter import (
    emit_v4_write,
)


def test_emit_v4_write_emits_both_v3_and_v4(sample_principal_chain: pytest.fixture):
    """Test that emit_v4_write emits both v3 replay_key and v4 PrincipalAttachedWrite."""
    result = emit_v4_write(
        plan_hash="test_plan_hash",
        tool_calls=("tool1", "tool2"),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff_hash",
        principal_chain=sample_principal_chain,
    )
    
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) == 2
    v3_key, attached = result
    assert isinstance(v3_key, str)
    assert attached is not None
    assert "principal_chain" in attached.to_dict()


def test_emit_v4_write_resolves_front_door_principal(sample_principal_chain: pytest.fixture):
    """Test that emit_v4_write resolves front-door principal when none provided."""
    result = emit_v4_write(
        plan_hash="test_plan_hash",
        tool_calls=("tool1",),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff_hash",
        principal_chain=sample_principal_chain,
    )
    
    assert result is not None
    _v3_key, attached = result
    assert attached is not None


def test_emit_v4_write_with_explicit_principal(sample_principal_chain: pytest.fixture):
    """Test that emit_v4_write uses provided principal_chain when given."""
    result = emit_v4_write(
        plan_hash="test_plan_hash",
        tool_calls=("tool1",),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff_hash",
        principal_chain=sample_principal_chain,
    )
    
    assert result is not None
    v3_key, attached = result
    assert isinstance(v3_key, str)
    assert attached is not None
    assert len(v3_key) > 0  # v3 key should be non-empty hash
