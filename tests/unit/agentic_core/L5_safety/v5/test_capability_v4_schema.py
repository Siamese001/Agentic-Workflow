"""Tests for `CapabilityTokenV5` v4 schema additions (G6)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import CapabilityTokenV5
from agentic_core.L5_safety.v5.types import (
    GrantMode,
    LifecycleState,
    PermissionLadderEntry,
)


def _base_token(**overrides):
    base = dict(
        token_id="tok",
        principal_chain_id="pri",
        scope=("read",),
        ttl_seconds=300,
        single_use=True,
        max_invocations=1,
        connector_allowlist=(),
        plan_digest="pd",
        route_contract_digest="rcd",
        evidence_contract_id="ec",
        permission_ladder=("read",),
        allowed_args_hash="aah",
    )
    base.update(overrides)
    return CapabilityTokenV5(**base)


def test_default_lifecycle_is_issued() -> None:
    t = _base_token()
    assert t.lifecycle_state == LifecycleState.ISSUED


def test_default_permission_ladder_entry_is_read() -> None:
    t = _base_token()
    assert t.permission_ladder_entry == PermissionLadderEntry.READ


def test_default_grant_mode_is_one_time() -> None:
    t = _base_token()
    assert t.grant_mode == GrantMode.ONE_TIME


def test_external_rung_requires_single_use_or_persistent_grant() -> None:
    """schema §2 — EXTERNAL rung is HIGH-band-only and single_use unless persistent."""

    # OK: single_use=True covers EXTERNAL rung
    _base_token(permission_ladder_entry=PermissionLadderEntry.EXTERNAL, single_use=True)
    # OK: persistent_grant_ref covers EXTERNAL rung
    _base_token(
        permission_ladder_entry=PermissionLadderEntry.EXTERNAL,
        single_use=False,
        max_invocations=5,
        persistent_grant_ref="grant-1",
    )
    # FAIL: neither
    with pytest.raises(ValueError, match="EXTERNAL rung"):
        _base_token(
            permission_ladder_entry=PermissionLadderEntry.EXTERNAL,
            single_use=False,
            max_invocations=5,
            persistent_grant_ref="",
        )


def test_revoked_requires_revoked_at() -> None:
    _base_token(revoked=True, revoked_at="2026-04-26T22:00:00Z", revocation_reason="admin")
    with pytest.raises(ValueError, match="revoked_at"):
        _base_token(revoked=True, revoked_at="")


def test_negative_delegation_depth_rejected() -> None:
    with pytest.raises(ValueError, match="delegation_depth"):
        _base_token(delegation_depth=-1)


def test_to_dict_carries_all_v4_fields() -> None:
    t = _base_token(
        permission_ladder_entry=PermissionLadderEntry.SUGGEST,
        step_up_required_for=("write_op",),
        persistent_grant_ref="g1",
        grant_mode=GrantMode.SESSIONED,
        plan_stream_endpoint="ws://stream",
        lifecycle_state=LifecycleState.IN_USE,
        hard_constraints_active=("F-01",),
        delegation_depth=2,
        tool_allowlist=("notion",),
    )
    d = t.to_dict()
    # All v4 schema fields surface in serialization
    expected_keys = {
        "permission_ladder_entry",
        "step_up_required_for",
        "persistent_grant_ref",
        "grant_mode",
        "plan_stream_endpoint",
        "lifecycle_state",
        "hard_constraints_active",
        "delegation_depth",
        "tool_allowlist",
        "revoked",
        "revoked_at",
        "revocation_reason",
    }
    missing = expected_keys - set(d.keys())
    assert not missing, f"missing v4 schema fields: {missing}"
    assert d["permission_ladder_entry"] == "suggest"
    assert d["grant_mode"] == "sessioned"
    assert d["lifecycle_state"] == "IN_USE"
