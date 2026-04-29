"""
Integration tests for L5/G06 PermissionLadder + L5/G08 EgressFirewall wired
into the UniversalWriteGateway.

Per ADR-070 production-wiring deferred-scope (closed 2026-04-29).
The wiring contract:

  - permission_ladder=None  → identical legacy behavior
  - egress_firewall=None    → identical legacy behavior
  - permission_ladder set   → write_through() consults ladder.check() before
                              the existing path/permission checks
  - egress_firewall set     → write_through() consults firewall.inspect() for
                              user-facing paths before commit

Backward-compatibility test: every existing UWG test passes with both
optional kwargs left unset (verified by running the existing suite).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L2_execution.enforcement.UniversalWriteGateway import (
    UniversalWriteGateway,
)
from agentic_core.L5_safety.egress import DefaultEgressFirewall
from agentic_core.L5_safety.permissions import (
    InMemoryPermissionLadder,
    PermissionGrant,
    PermissionRung,
)


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


# -----------------------------------------------------------------------------
# Backward compatibility — default behavior is unchanged
# -----------------------------------------------------------------------------


def test_uwg_default_behavior_unchanged() -> None:
    """Constructing UWG without L5 wiring matches the legacy contract."""
    uwg = UniversalWriteGateway(replay_mode=True)
    assert uwg._permission_ladder is None
    assert uwg._egress_firewall is None
    # Replay-mode write succeeds (existing behavior)
    result = uwg.write_through("artifacts/test.txt", "hello")
    assert result is not None


def test_uwg_default_no_ladder_calls() -> None:
    """When no ladder wired, no ladder calls happen — write proceeds."""
    uwg = UniversalWriteGateway(replay_mode=True)
    result = uwg.write_through("artifacts/anything.txt", "data")
    assert result is not None


# -----------------------------------------------------------------------------
# G06 PermissionLadder wiring
# -----------------------------------------------------------------------------


def test_uwg_with_ladder_blocks_when_no_grant() -> None:
    """Wired ladder with no matching grant → write_through raises PermissionError."""
    ladder = InMemoryPermissionLadder()
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x", permission_ladder=ladder,
    )
    with pytest.raises(PermissionError, match="REQ-L5-G06"):
        uwg.write_through("artifacts/secret.txt", "data")


def test_uwg_with_ladder_allows_when_grant_held() -> None:
    """Wired ladder with MUTATE grant → write_through succeeds."""
    ladder = InMemoryPermissionLadder()
    ladder.grant(PermissionGrant(
        agent_id="agent-x", target_resource="artifacts/test.txt",
        rung=PermissionRung.MUTATE, granted_by="ops",
        expires_at_iso=_future(),
    ))
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x", permission_ladder=ladder,
    )
    result = uwg.write_through("artifacts/test.txt", "data")
    assert result is not None


def test_uwg_with_ladder_blocks_when_only_read_held() -> None:
    """READ grant is insufficient for a MUTATE write."""
    ladder = InMemoryPermissionLadder()
    ladder.grant(PermissionGrant(
        agent_id="agent-x", target_resource="artifacts/foo.txt",
        rung=PermissionRung.READ, granted_by="ops",
        expires_at_iso=_future(),
    ))
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x", permission_ladder=ladder,
    )
    with pytest.raises(PermissionError, match="REQ-L5-G06.*READ.*MUTATE"):
        uwg.write_through("artifacts/foo.txt", "data")


def test_uwg_with_ladder_blocks_expired_grant() -> None:
    past = (datetime.now(timezone.utc) - timedelta(seconds=60)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    ladder = InMemoryPermissionLadder()
    ladder.grant(PermissionGrant(
        agent_id="agent-x", target_resource="artifacts/expired.txt",
        rung=PermissionRung.EXECUTE, granted_by="ops",
        expires_at_iso=past,
    ))
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x", permission_ladder=ladder,
    )
    with pytest.raises(PermissionError, match="REQ-L5-G06.*expired"):
        uwg.write_through("artifacts/expired.txt", "data")


# -----------------------------------------------------------------------------
# G08 EgressFirewall wiring
# -----------------------------------------------------------------------------


def test_uwg_with_firewall_clean_data_passes() -> None:
    """Clean text data → firewall passes, write proceeds."""
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(replay_mode=True, egress_firewall=fw)
    result = uwg.write_through(
        "artifacts/published/report.txt", "Q3 revenue increased 12%.",
    )
    assert result is not None


def test_uwg_with_firewall_blocks_credential_leak() -> None:
    """AWS-shape credential in user-facing payload → blocked at firewall."""
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(replay_mode=True, egress_firewall=fw)
    with pytest.raises(PermissionError, match="REQ-L5-G08"):
        uwg.write_through(
            "artifacts/published/report.txt",
            "Use AKIAIOSFODNN7EXAMPLE for access",
        )


def test_uwg_with_firewall_blocks_github_token() -> None:
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(replay_mode=True, egress_firewall=fw)
    with pytest.raises(PermissionError, match="REQ-L5-G08.*github_token"):
        uwg.write_through(
            "egress:slack:announcement",
            "Token: ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789",
        )


def test_uwg_firewall_only_runs_on_egress_paths() -> None:
    """Firewall does NOT inspect non-egress paths even with credential payload."""
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(replay_mode=True, egress_firewall=fw)
    # artifacts/internal/ is not user-facing; firewall should not fire
    result = uwg.write_through(
        "artifacts/internal/scratch.txt",
        "AKIAIOSFODNN7EXAMPLE",  # would block on egress path
    )
    assert result is not None  # Internal write allowed


# -----------------------------------------------------------------------------
# Both wired together
# -----------------------------------------------------------------------------


def test_uwg_both_ladder_and_firewall_wired() -> None:
    """Both L5 components active; clean data + valid grant → success."""
    ladder = InMemoryPermissionLadder()
    ladder.grant(PermissionGrant(
        agent_id="agent-x", target_resource="artifacts/published/ok.txt",
        rung=PermissionRung.EXECUTE, granted_by="ops",
        expires_at_iso=_future(),
    ))
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x",
        permission_ladder=ladder, egress_firewall=fw,
    )
    result = uwg.write_through(
        "artifacts/published/ok.txt", "Clean public-facing content.",
    )
    assert result is not None


def test_uwg_ladder_check_runs_before_firewall() -> None:
    """Ladder rejection happens FIRST — firewall never sees the data."""
    ladder = InMemoryPermissionLadder()  # no grants
    fw = DefaultEgressFirewall()
    uwg = UniversalWriteGateway(
        replay_mode=True, actor_id="agent-x",
        permission_ladder=ladder, egress_firewall=fw,
    )
    # Even with credential in payload, ladder error should fire first
    with pytest.raises(PermissionError, match="REQ-L5-G06"):
        uwg.write_through(
            "artifacts/published/x.txt",
            "AKIAIOSFODNN7EXAMPLE",
        )
