"""Unit tests for agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger.

Targets Wave-3 / Phase P9. Source: 382 lines, fan_in=48 (L3, impact 84.0).
"""

from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
    _hash_payload,
    _row_to_entry,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass


@pytest.fixture
def ledger(tmp_path: Path) -> RuntimeHitlLedger:
    """Fresh ledger rooted at a tmp path with a deterministic clock."""
    counter = itertools.count(start=1000.0, step=1.0)
    clk = lambda: next(counter)  # noqa: E731
    led = RuntimeHitlLedger(path=tmp_path / "hitl.db", now=clk)
    try:
        yield led
    finally:
        led.close()


def _any_hitl_class() -> HitlClass:
    return list(HitlClass)[0]


class TestLedgerStateEnum:
    def test_values(self) -> None:
        assert LedgerState.PENDING.value == "pending"
        assert LedgerState.APPROVED.value == "approved"
        assert LedgerState.DENIED.value == "denied"
        assert LedgerState.TIMEOUT.value == "timeout"

    def test_is_str(self) -> None:
        assert isinstance(LedgerState.PENDING, str)


class TestHashPayload:
    def test_deterministic(self) -> None:
        p = {"b": 2, "a": 1}
        assert _hash_payload(p) == _hash_payload({"a": 1, "b": 2})

    def test_different_for_different_payloads(self) -> None:
        assert _hash_payload({"a": 1}) != _hash_payload({"a": 2})

    def test_hex_sha256_length(self) -> None:
        assert len(_hash_payload({"x": 1})) == 64


class TestRecordEscalation:
    def test_creates_pending_entry(self, ledger: RuntimeHitlLedger) -> None:
        entry = ledger.record_escalation(
            run_id="r-1",
            trace_id="t-1",
            hitl_class=_any_hitl_class(),
            approver_pool="ops",
            timeout_s=60,
            policy_snapshot="policy-v1",
            envelope={"reason": "test"},
        )
        assert isinstance(entry, LedgerEntry)
        assert entry.state == LedgerState.PENDING
        assert entry.run_id == "r-1"
        assert entry.trace_id == "t-1"
        assert entry.approver_pool == "ops"
        assert entry.timeout_s == 60
        assert entry.envelope == {"reason": "test"}
        assert entry.resolved_at is None
        assert len(entry.ledger_id) == 32  # uuid4 hex
        assert len(entry.entry_hash) == 64

    def test_get_round_trips(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r-1",
            trace_id="t-1",
            hitl_class=_any_hitl_class(),
            approver_pool="ops",
            timeout_s=30,
            policy_snapshot="ps",
        )
        got = ledger.get(e.ledger_id)
        assert got is not None
        assert got.ledger_id == e.ledger_id
        assert got.state == LedgerState.PENDING

    def test_get_missing_returns_none(self, ledger: RuntimeHitlLedger) -> None:
        assert ledger.get("nonexistent-id") is None

    def test_envelope_default_empty(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=5,
            policy_snapshot="s",
        )
        assert e.envelope == {}

    def test_chain_links_prev_hash(self, ledger: RuntimeHitlLedger) -> None:
        a = ledger.record_escalation(
            run_id="SAME",
            trace_id="t1",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=1,
            policy_snapshot="s",
        )
        b = ledger.record_escalation(
            run_id="SAME",
            trace_id="t2",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=1,
            policy_snapshot="s",
        )
        # b's prev_hash should equal a's entry_hash
        assert b.prev_hash == a.entry_hash


class TestResolveStates:
    def test_approve_pending(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=5,
            policy_snapshot="s",
        )
        result = ledger.record_approved(e.ledger_id, approver_id="alice", rationale="ok")
        assert result.state == LedgerState.APPROVED
        assert result.approver_id == "alice"
        assert result.rationale == "ok"
        assert result.resolved_at is not None

    def test_deny_pending(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=5,
            policy_snapshot="s",
        )
        result = ledger.record_denied(
            e.ledger_id, approver_id="bob", reason_code="POLICY", rationale="blocked"
        )
        assert result.state == LedgerState.DENIED
        assert result.approver_id == "bob"
        assert result.reason_code == "POLICY"

    def test_timeout_pending(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=1,
            policy_snapshot="s",
        )
        result = ledger.record_timeout(e.ledger_id)
        assert result.state == LedgerState.TIMEOUT
        assert result.reason_code == "TIMEOUT"

    def test_double_resolve_rejected(self, ledger: RuntimeHitlLedger) -> None:
        e = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=5,
            policy_snapshot="s",
        )
        ledger.record_approved(e.ledger_id, approver_id="a")
        with pytest.raises(ValueError, match="already resolved"):
            ledger.record_approved(e.ledger_id, approver_id="b")

    def test_resolve_missing_raises_keyerror(self, ledger: RuntimeHitlLedger) -> None:
        with pytest.raises(KeyError, match="not found"):
            ledger.record_approved("no-such-id", approver_id="a")


class TestListQueries:
    def test_list_by_run_returns_chronological(self, ledger: RuntimeHitlLedger) -> None:
        for trace_id in ("t1", "t2", "t3"):
            ledger.record_escalation(
                run_id="R",
                trace_id=trace_id,
                hitl_class=_any_hitl_class(),
                approver_pool="p",
                timeout_s=1,
                policy_snapshot="s",
            )
        entries = ledger.list_by_run("R")
        assert len(entries) == 3
        assert [e.trace_id for e in entries] == ["t1", "t2", "t3"]

    def test_list_by_run_empty(self, ledger: RuntimeHitlLedger) -> None:
        assert ledger.list_by_run("no-such-run") == []

    def test_list_pending_excludes_resolved(self, ledger: RuntimeHitlLedger) -> None:
        e1 = ledger.record_escalation(
            run_id="R",
            trace_id="t1",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=1,
            policy_snapshot="s",
        )
        ledger.record_escalation(
            run_id="R",
            trace_id="t2",
            hitl_class=_any_hitl_class(),
            approver_pool="p",
            timeout_s=1,
            policy_snapshot="s",
        )
        ledger.record_approved(e1.ledger_id, approver_id="a")
        pending = ledger.list_pending()
        assert len(pending) == 1
        assert pending[0].trace_id == "t2"


class TestContextManager:
    def test_context_manager_closes(self, tmp_path: Path) -> None:
        with RuntimeHitlLedger(path=tmp_path / "cm.db") as led:
            assert led is not None
        # Closing twice should not raise
        led.close()
