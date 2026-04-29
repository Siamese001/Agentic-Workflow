"""Behavior tests for G06 InMemoryPermissionLadder (Wave B impl)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L5_safety.permissions import (
    InMemoryPermissionLadder,
    PermissionGrant,
    PermissionRung,
    default_ladder,
)


def _future_iso(seconds_ahead: int = 3600) -> str:
    dt = datetime.now(timezone.utc) + timedelta(seconds=seconds_ahead)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _past_iso(seconds_ago: int = 3600) -> str:
    dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def ladder() -> InMemoryPermissionLadder:
    return InMemoryPermissionLadder()


def test_no_grant_denies(ladder: InMemoryPermissionLadder) -> None:
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.READ)
    assert v.allowed is False
    assert v.held_rung is None
    assert "no grant" in v.reason


def test_exact_rung_match_allows(ladder: InMemoryPermissionLadder) -> None:
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.READ, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.READ)
    assert v.allowed is True
    assert v.held_rung == PermissionRung.READ


def test_higher_rung_implies_lower(ladder: InMemoryPermissionLadder) -> None:
    """Holding EXECUTE confers READ/SUGGEST/MUTATE for the same target."""
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.EXECUTE, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    for req in (PermissionRung.READ, PermissionRung.SUGGEST, PermissionRung.MUTATE, PermissionRung.EXECUTE):
        v = ladder.check("agent-A", "uwg:state:x", req)
        assert v.allowed is True, f"EXECUTE should imply {req.name}"


def test_lower_rung_does_not_satisfy_higher(ladder: InMemoryPermissionLadder) -> None:
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.READ, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.MUTATE)
    assert v.allowed is False
    assert v.held_rung == PermissionRung.READ
    assert "READ < requested MUTATE" in v.reason


def test_expired_grant_denies(ladder: InMemoryPermissionLadder) -> None:
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.MUTATE, granted_by="admin", expires_at_iso=_past_iso(),
    ))
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.READ)
    assert v.allowed is False
    assert "expired" in v.reason


def test_grant_overwrites_lower(ladder: InMemoryPermissionLadder) -> None:
    """Granting MUTATE after READ for same (agent,target) replaces the entry."""
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.READ, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.MUTATE, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.MUTATE)
    assert v.allowed is True


def test_revoke_removes_grant(ladder: InMemoryPermissionLadder) -> None:
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="uwg:state:x",
        rung=PermissionRung.MUTATE, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    assert ladder.revoke("agent-A", "uwg:state:x") is True
    v = ladder.check("agent-A", "uwg:state:x", PermissionRung.READ)
    assert v.allowed is False
    assert v.held_rung is None


def test_revoke_returns_false_for_unknown(ladder: InMemoryPermissionLadder) -> None:
    assert ladder.revoke("ghost-agent", "ghost-target") is False


def test_grants_are_per_agent_target_pair(ladder: InMemoryPermissionLadder) -> None:
    """Granting agent-A on resource X does NOT confer agent-B on X, nor agent-A on Y."""
    ladder.grant(PermissionGrant(
        agent_id="agent-A", target_resource="resource-X",
        rung=PermissionRung.MUTATE, granted_by="admin", expires_at_iso=_future_iso(),
    ))

    # Different agent
    v = ladder.check("agent-B", "resource-X", PermissionRung.READ)
    assert v.allowed is False

    # Different resource
    v = ladder.check("agent-A", "resource-Y", PermissionRung.READ)
    assert v.allowed is False


def test_default_ladder_is_fresh_each_call() -> None:
    a = default_ladder()
    a.grant(PermissionGrant(
        agent_id="agent-A", target_resource="r",
        rung=PermissionRung.MUTATE, granted_by="admin", expires_at_iso=_future_iso(),
    ))
    b = default_ladder()
    # b is a fresh instance — does not see a's grant
    v = b.check("agent-A", "r", PermissionRung.READ)
    assert v.allowed is False
