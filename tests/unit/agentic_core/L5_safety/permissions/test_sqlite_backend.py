"""Behavior tests for SqlitePermissionLadder (durable G06 backend)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agentic_core.L5_safety.permissions import (
    PermissionGrant,
    PermissionRung,
)
from agentic_core.L5_safety.permissions.sqlite_backend import (
    SqlitePermissionLadder,
    sqlite_ladder,
)


def _future_iso(seconds: int = 3600) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _past_iso(seconds: int = 60) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "perm.sqlite"


def test_no_grant_denies(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    v = ladder.check("agent-1", "uwg:state:foo", PermissionRung.READ)
    assert v.allowed is False
    assert v.held_rung is None


def test_grant_then_check_allows(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="agent-1", target_resource="uwg:state:foo",
        rung=PermissionRung.MUTATE, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    v = ladder.check("agent-1", "uwg:state:foo", PermissionRung.SUGGEST)
    assert v.allowed is True
    assert v.held_rung == PermissionRung.MUTATE


def test_higher_rung_implies_lower(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.EXECUTE, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    for r in (PermissionRung.READ, PermissionRung.SUGGEST,
              PermissionRung.MUTATE, PermissionRung.EXECUTE):
        assert ladder.check("a", "t", r).allowed is True


def test_lower_rung_does_not_imply_higher(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.SUGGEST, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    assert ladder.check("a", "t", PermissionRung.MUTATE).allowed is False
    assert ladder.check("a", "t", PermissionRung.EXECUTE).allowed is False


def test_expired_grant_denies(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.MUTATE, granted_by="ops",
        expires_at_iso=_past_iso(),
    ))
    v = ladder.check("a", "t", PermissionRung.READ)
    assert v.allowed is False
    assert "expired" in v.reason


def test_grant_overwrites_via_upsert(db_path: Path) -> None:
    """Granting same (agent, target) with different rung must overwrite via UPSERT."""
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.READ, granted_by="ops-1",
        expires_at_iso=_future_iso(),
    ))
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.EXECUTE, granted_by="ops-2",
        expires_at_iso=_future_iso(),
    ))
    v = ladder.check("a", "t", PermissionRung.EXECUTE)
    assert v.allowed is True
    assert v.held_rung == PermissionRung.EXECUTE


def test_revoke_removes_grant(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.MUTATE, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    assert ladder.revoke("a", "t") is True
    assert ladder.revoke("a", "t") is False  # second revoke returns False
    assert ladder.check("a", "t", PermissionRung.READ).allowed is False


def test_persistence_across_instances(db_path: Path) -> None:
    """Grant in one instance persists to a fresh instance reading the same file."""
    a = SqlitePermissionLadder(db_path)
    a.grant(PermissionGrant(
        agent_id="agent-X", target_resource="exec:shell",
        rung=PermissionRung.EXECUTE, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    a.close()

    b = SqlitePermissionLadder(db_path)
    v = b.check("agent-X", "exec:shell", PermissionRung.MUTATE)
    assert v.allowed is True
    assert v.held_rung == PermissionRung.EXECUTE


def test_factory_works(db_path: Path) -> None:
    ladder = sqlite_ladder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t",
        rung=PermissionRung.READ, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    assert ladder.check("a", "t", PermissionRung.READ).allowed is True


def test_independent_targets_isolated(db_path: Path) -> None:
    ladder = SqlitePermissionLadder(db_path)
    ladder.grant(PermissionGrant(
        agent_id="a", target_resource="t1",
        rung=PermissionRung.EXECUTE, granted_by="ops",
        expires_at_iso=_future_iso(),
    ))
    # No grant for t2
    assert ladder.check("a", "t1", PermissionRung.EXECUTE).allowed is True
    assert ladder.check("a", "t2", PermissionRung.READ).allowed is False
