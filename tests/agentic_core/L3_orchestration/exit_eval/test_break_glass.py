"""Tests for X3E break-glass authorization."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.break_glass import (
    MAX_EXPIRY_SECONDS,
    BreakGlassAuditRow,
    BreakGlassAuthority,
    BreakGlassError,
    BreakGlassToken,
    jsonl_audit_sink,
)


def _valid_token(now: float = 1000.0) -> BreakGlassToken:
    return BreakGlassToken(
        identity="op@example.com",
        capabilities=frozenset({"break_glass"}),
        issued_at=now - 10,
        expires_at=now + 3600,
    )


def _authority(tmp_path: Path) -> tuple[BreakGlassAuthority, Path]:
    audit_path = tmp_path / "audit.jsonl"
    auth = BreakGlassAuthority(
        audit_sink=jsonl_audit_sink(audit_path),
        now=lambda: 1000.0,
    )
    return auth, audit_path


def test_invoke_writes_audit_row(tmp_path: Path) -> None:
    auth, audit_path = _authority(tmp_path)
    inv = auth.invoke(
        token=_valid_token(),
        justification="production outage in refund path",
        bypassed_gates=("X1F",),
        run_id="run-1",
        expiry_seconds=900,
    )
    assert inv.audit_id.startswith("bg-")
    assert inv.bypassed_gates == ("X1F",)
    # Audit written
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["identity"] == "op@example.com"
    assert row["bypassed_gates"] == ["X1F"]
    assert row["run_id"] == "run-1"


def test_token_without_capability_refused(tmp_path: Path) -> None:
    auth, _ = _authority(tmp_path)
    bad = BreakGlassToken(
        identity="op",
        capabilities=frozenset({"other"}),
        issued_at=0.0,
        expires_at=1e9,
    )
    with pytest.raises(BreakGlassError, match="missing capability"):
        auth.invoke(
            token=bad,
            justification="x",
            bypassed_gates=("X1F",),
            run_id="r",
            expiry_seconds=60,
        )


def test_expired_token_refused(tmp_path: Path) -> None:
    auth = BreakGlassAuthority(
        audit_sink=lambda _r: None,
        now=lambda: 2000.0,  # current
    )
    expired = BreakGlassToken(
        identity="op",
        capabilities=frozenset({"break_glass"}),
        issued_at=0.0,
        expires_at=1000.0,  # already past
    )
    with pytest.raises(BreakGlassError):
        auth.invoke(
            token=expired,
            justification="x",
            bypassed_gates=("X1F",),
            run_id="r",
            expiry_seconds=60,
        )


def test_bypass_forbidden_gates_refused(tmp_path: Path) -> None:
    """H3.1: X1A and X1C cannot be bypassed."""
    auth, _ = _authority(tmp_path)
    for forbidden in ("X1A", "X1C"):
        with pytest.raises(BreakGlassError, match="cannot bypass"):
            auth.invoke(
                token=_valid_token(),
                justification="x",
                bypassed_gates=(forbidden,),
                run_id="r",
                expiry_seconds=60,
            )


def test_unknown_gate_name_refused(tmp_path: Path) -> None:
    auth, _ = _authority(tmp_path)
    with pytest.raises(BreakGlassError, match="unknown gate"):
        auth.invoke(
            token=_valid_token(),
            justification="x",
            bypassed_gates=("X9Z",),
            run_id="r",
            expiry_seconds=60,
        )


def test_expiry_cap_enforced(tmp_path: Path) -> None:
    auth, _ = _authority(tmp_path)
    with pytest.raises(BreakGlassError, match="expiry"):
        auth.invoke(
            token=_valid_token(),
            justification="x",
            bypassed_gates=("X1F",),
            run_id="r",
            expiry_seconds=MAX_EXPIRY_SECONDS + 1,
        )


def test_empty_justification_refused(tmp_path: Path) -> None:
    auth, _ = _authority(tmp_path)
    with pytest.raises(BreakGlassError, match="justification"):
        auth.invoke(
            token=_valid_token(),
            justification="   ",
            bypassed_gates=("X1F",),
            run_id="r",
            expiry_seconds=60,
        )


def test_audit_sink_failure_refuses_invocation() -> None:
    def sink(_row: BreakGlassAuditRow) -> None:
        raise OSError("disk full")

    auth = BreakGlassAuthority(audit_sink=sink, now=lambda: 1000.0)
    with pytest.raises(BreakGlassError, match="audit sink failed"):
        auth.invoke(
            token=_valid_token(),
            justification="x",
            bypassed_gates=("X1F",),
            run_id="r",
            expiry_seconds=60,
        )
