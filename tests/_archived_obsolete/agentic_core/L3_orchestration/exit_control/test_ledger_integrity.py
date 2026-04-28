"""Tests for the runtime HITL audit chain (W7 P7.1)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
    AuditChain,
    AuditEventType,
    IntegrityReport,
    compute_entry_hash,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeSigningKey:
    """Deterministic 'signing' key for tests — signs with reversed bytes."""

    def __init__(self, secret: bytes = b"secret-key") -> None:
        self._secret = secret

    def sign(self, payload: bytes) -> bytes:
        return bytes((b ^ 0x55) for b in payload)  # reversible

    @property
    def public_key_bytes(self) -> bytes:
        return self._secret


class _FakeVerifyingKey:
    """Verifier for the FakeSigningKey — XOR inverse."""

    def verify(self, signature: bytes, payload: bytes) -> bool:
        return signature == bytes((b ^ 0x55) for b in payload)


class _MismatchedVerifyingKey:
    """Always rejects."""

    def verify(self, signature: bytes, payload: bytes) -> bool:
        return False


@pytest.fixture
def chain_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.db"


# ---------------------------------------------------------------------------
# compute_entry_hash — pure function contract
# ---------------------------------------------------------------------------


class TestComputeEntryHash:
    def test_is_deterministic(self) -> None:
        h1 = compute_entry_hash(
            ledger_id="l",
            run_id="r",
            event_type="created",
            event_ts=100.0,
            payload={"a": 1, "b": 2},
            prev_hash="",
        )
        h2 = compute_entry_hash(
            ledger_id="l",
            run_id="r",
            event_type="created",
            event_ts=100.0,
            payload={"b": 2, "a": 1},
            prev_hash="",
        )
        assert h1 == h2  # key order must not matter

    def test_changes_when_any_field_changes(self) -> None:
        h0 = compute_entry_hash(
            ledger_id="l",
            run_id="r",
            event_type="created",
            event_ts=100.0,
            payload={"a": 1},
            prev_hash="",
        )
        assert (
            compute_entry_hash(
                ledger_id="other",
                run_id="r",
                event_type="created",
                event_ts=100.0,
                payload={"a": 1},
                prev_hash="",
            )
            != h0
        )
        assert (
            compute_entry_hash(
                ledger_id="l",
                run_id="r2",
                event_type="created",
                event_ts=100.0,
                payload={"a": 1},
                prev_hash="",
            )
            != h0
        )
        assert (
            compute_entry_hash(
                ledger_id="l",
                run_id="r",
                event_type="approved",
                event_ts=100.0,
                payload={"a": 1},
                prev_hash="",
            )
            != h0
        )
        assert (
            compute_entry_hash(
                ledger_id="l",
                run_id="r",
                event_type="created",
                event_ts=101.0,
                payload={"a": 1},
                prev_hash="",
            )
            != h0
        )
        assert (
            compute_entry_hash(
                ledger_id="l",
                run_id="r",
                event_type="created",
                event_ts=100.0,
                payload={"a": 1},
                prev_hash="abc",
            )
            != h0
        )

    def test_payload_change_shifts_hash(self) -> None:
        a = compute_entry_hash(
            ledger_id="l",
            run_id="r",
            event_type="created",
            event_ts=1.0,
            payload={"x": 1},
            prev_hash="",
        )
        b = compute_entry_hash(
            ledger_id="l",
            run_id="r",
            event_type="created",
            event_ts=1.0,
            payload={"x": 2},
            prev_hash="",
        )
        assert a != b


# ---------------------------------------------------------------------------
# AuditChain.append — basic behavior
# ---------------------------------------------------------------------------


class TestAppend:
    def test_first_event_has_empty_prev_hash(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        ev = chain.append(
            ledger_id="l1",
            run_id="r1",
            event_type=AuditEventType.CREATED,
            payload={"k": "v"},
        )
        assert ev.prev_hash == ""
        assert ev.entry_hash  # non-empty
        assert ev.event_type is AuditEventType.CREATED

    def test_second_event_links_to_first(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        e1 = chain.append(
            ledger_id="l1",
            run_id="r1",
            event_type=AuditEventType.CREATED,
            payload={"k": 1},
            event_ts=100.0,
        )
        e2 = chain.append(
            ledger_id="l1",
            run_id="r1",
            event_type=AuditEventType.APPROVED,
            payload={"approver_id": "alice"},
            event_ts=200.0,
        )
        assert e2.prev_hash == e1.entry_hash
        assert e2.entry_hash != e1.entry_hash

    def test_non_serializable_payload_raises(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        with pytest.raises(ValueError, match="JSON-serializable"):
            chain.append(
                ledger_id="l",
                run_id="r",
                event_type=AuditEventType.CREATED,
                payload={"bad": {1, 2, 3}},  # sets are not JSON
            )

    def test_append_without_signing_key_stores_no_signature(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        ev = chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
        )
        assert ev.signature == ""
        assert ev.public_key == ""

    def test_append_with_signing_key_stores_signature(self, chain_path: Path) -> None:
        key = _FakeSigningKey()
        chain = AuditChain(chain_path, now=lambda: 100.0, signing_key=key)
        ev = chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
        )
        assert ev.signature  # hex string
        assert ev.public_key == key.public_key_bytes.hex()


# ---------------------------------------------------------------------------
# list_events
# ---------------------------------------------------------------------------


class TestListEvents:
    def test_list_all_ordered_by_audit_id(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        chain.append(ledger_id="l1", run_id="r1", event_type=AuditEventType.CREATED, payload={})
        chain.append(ledger_id="l2", run_id="r2", event_type=AuditEventType.CREATED, payload={})
        chain.append(ledger_id="l1", run_id="r1", event_type=AuditEventType.APPROVED, payload={})
        events = chain.list_events()
        assert [e.audit_id for e in events] == sorted(e.audit_id for e in events)
        assert len(events) == 3

    def test_filter_by_ledger_id(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        chain.append(ledger_id="l1", run_id="r1", event_type=AuditEventType.CREATED, payload={})
        chain.append(ledger_id="l2", run_id="r2", event_type=AuditEventType.CREATED, payload={})
        filtered = chain.list_events(ledger_id="l1")
        assert len(filtered) == 1
        assert filtered[0].ledger_id == "l1"

    def test_filter_by_run_id(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        chain.append(ledger_id="l1", run_id="rA", event_type=AuditEventType.CREATED, payload={})
        chain.append(ledger_id="l2", run_id="rB", event_type=AuditEventType.CREATED, payload={})
        filtered = chain.list_events(run_id="rA")
        assert len(filtered) == 1
        assert filtered[0].run_id == "rA"


# ---------------------------------------------------------------------------
# verify — the core integrity property
# ---------------------------------------------------------------------------


class TestVerify:
    def test_empty_chain_is_ok(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        report = chain.verify()
        assert isinstance(report, IntegrityReport)
        assert report.ok is True
        assert report.total_events == 0

    def test_clean_chain_verifies(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        for i in range(5):
            chain.append(
                ledger_id=f"l{i}",
                run_id="r",
                event_type=AuditEventType.CREATED,
                payload={"i": i},
                event_ts=100.0 + i,
            )
        report = chain.verify()
        assert report.ok
        assert report.total_events == 5
        assert report.verified_events == 5
        assert report.violations == ()

    def test_tampered_payload_detected(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={"x": 1},
            event_ts=100.0,
        )
        chain.close()
        # Tamper: overwrite the payload JSON directly
        conn = sqlite3.connect(chain_path)
        conn.execute(
            "UPDATE hitl_audit_chain SET payload_json = ? WHERE audit_id = 1",
            ('{"x": 2}',),
        )
        conn.commit()
        conn.close()
        chain2 = AuditChain(chain_path)
        report = chain2.verify()
        assert report.ok is False
        assert any(v.reason == "entry_hash_mismatch" for v in report.violations)

    def test_broken_linkage_detected(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0)
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
            event_ts=100.0,
        )
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.APPROVED,
            payload={},
            event_ts=101.0,
        )
        chain.close()
        # Tamper: change prev_hash of row 2
        conn = sqlite3.connect(chain_path)
        conn.execute(
            "UPDATE hitl_audit_chain SET prev_hash = 'deadbeef' WHERE audit_id = 2",
        )
        conn.commit()
        conn.close()
        chain2 = AuditChain(chain_path)
        report = chain2.verify()
        assert report.ok is False
        # Both prev_hash_mismatch AND entry_hash_mismatch (because entry_hash
        # was computed over the real prev_hash)
        reasons = {v.reason for v in report.violations}
        assert "prev_hash_mismatch" in reasons

    def test_signature_verified_when_key_matches(self, chain_path: Path) -> None:
        key = _FakeSigningKey()
        chain = AuditChain(chain_path, now=lambda: 100.0, signing_key=key)
        for i in range(3):
            chain.append(
                ledger_id=f"l{i}",
                run_id="r",
                event_type=AuditEventType.CREATED,
                payload={"i": i},
            )
        report = chain.verify(verifying_key=_FakeVerifyingKey())
        assert report.ok is True
        assert report.signed_events == 3
        assert report.verified_signatures == 3

    def test_signature_rejected_when_key_wrong(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0, signing_key=_FakeSigningKey())
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
        )
        report = chain.verify(verifying_key=_MismatchedVerifyingKey())
        assert report.ok is False
        assert any(v.reason == "signature_invalid" for v in report.violations)
        assert report.verified_signatures == 0

    def test_signed_rows_without_verifier_get_note(self, chain_path: Path) -> None:
        chain = AuditChain(chain_path, now=lambda: 100.0, signing_key=_FakeSigningKey())
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
        )
        report = chain.verify()  # no verifying_key
        assert report.ok is True  # chain still intact
        assert report.signed_events == 1
        assert report.verified_signatures == 0
        assert "signature_check" in report.notes


# ---------------------------------------------------------------------------
# Ledger integration — events emitted on all lifecycle transitions
# ---------------------------------------------------------------------------


class TestLedgerAuditWiring:
    def test_escalation_emits_created_event(self, tmp_path: Path) -> None:
        chain = AuditChain(tmp_path / "audit.db")
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db", audit_chain=chain)
        entry = ledger.record_escalation(
            run_id="r1",
            trace_id="t1",
            hitl_class=HitlClass.FINANCIAL,
            approver_pool="finance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        events = chain.list_events(ledger_id=entry.ledger_id)
        assert len(events) == 1
        assert events[0].event_type is AuditEventType.CREATED
        assert events[0].payload["hitl_class"] == "financial"

    def test_approval_emits_approved_event(self, tmp_path: Path) -> None:
        chain = AuditChain(tmp_path / "audit.db")
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db", audit_chain=chain)
        entry = ledger.record_escalation(
            run_id="r1",
            trace_id="t1",
            hitl_class=HitlClass.FINANCIAL,
            approver_pool="finance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        ledger.record_approved(entry.ledger_id, approver_id="alice", rationale="ok")
        events = chain.list_events(ledger_id=entry.ledger_id)
        kinds = [e.event_type for e in events]
        assert kinds == [AuditEventType.CREATED, AuditEventType.APPROVED]
        assert events[1].payload["approver_id"] == "alice"

    def test_denial_emits_denied_event(self, tmp_path: Path) -> None:
        chain = AuditChain(tmp_path / "audit.db")
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db", audit_chain=chain)
        entry = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=HitlClass.SAFETY,
            approver_pool="safety",
            timeout_s=60,
            policy_snapshot="snap",
        )
        ledger.record_denied(entry.ledger_id, approver_id="bob", reason_code="X")
        events = chain.list_events(ledger_id=entry.ledger_id)
        assert events[-1].event_type is AuditEventType.DENIED
        assert events[-1].payload["reason_code"] == "X"

    def test_timeout_emits_timeout_event(self, tmp_path: Path) -> None:
        chain = AuditChain(tmp_path / "audit.db")
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db", audit_chain=chain)
        entry = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=HitlClass.REGULATED,
            approver_pool="compliance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        ledger.record_timeout(entry.ledger_id)
        events = chain.list_events(ledger_id=entry.ledger_id)
        assert events[-1].event_type is AuditEventType.TIMEOUT

    def test_ledger_without_audit_chain_is_noop(self, tmp_path: Path) -> None:
        # Backward-compat: no audit_chain → no audit rows, no errors
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db")  # no audit_chain
        entry = ledger.record_escalation(
            run_id="r",
            trace_id="t",
            hitl_class=HitlClass.FINANCIAL,
            approver_pool="finance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        ledger.record_approved(entry.ledger_id, approver_id="alice")
        # Ledger row updated; no second DB to check.
        resolved = ledger.get(entry.ledger_id)
        assert resolved is not None
        assert resolved.approver_id == "alice"

    def test_end_to_end_chain_verifies(self, tmp_path: Path) -> None:
        chain = AuditChain(tmp_path / "audit.db")
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db", audit_chain=chain)
        # 3 escalations, one of each resolution kind
        e1 = ledger.record_escalation(
            run_id="r1",
            trace_id="t1",
            hitl_class=HitlClass.FINANCIAL,
            approver_pool="finance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        e2 = ledger.record_escalation(
            run_id="r2",
            trace_id="t2",
            hitl_class=HitlClass.SAFETY,
            approver_pool="safety",
            timeout_s=60,
            policy_snapshot="snap",
        )
        e3 = ledger.record_escalation(
            run_id="r3",
            trace_id="t3",
            hitl_class=HitlClass.REGULATED,
            approver_pool="comp",
            timeout_s=60,
            policy_snapshot="snap",
        )
        ledger.record_approved(e1.ledger_id, approver_id="a1")
        ledger.record_denied(e2.ledger_id, approver_id="a2", reason_code="X")
        ledger.record_timeout(e3.ledger_id)

        report = chain.verify()
        assert report.ok
        assert report.total_events == 6
        assert report.verified_events == 6


# ---------------------------------------------------------------------------
# Real ed25519 round-trip (skipped if cryptography not installed)
# ---------------------------------------------------------------------------


cryptography = pytest.importorskip("cryptography")


class TestEd25519RoundTrip:
    def test_sign_and_verify_round_trip(self, tmp_path: Path) -> None:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
            Ed25519SigningKey,
            Ed25519VerifyingKey,
        )

        priv = ed25519.Ed25519PrivateKey.generate()
        priv_bytes = priv.private_bytes_raw()  # type: ignore[attr-defined]
        signing = Ed25519SigningKey(priv_bytes)
        verifying = Ed25519VerifyingKey(signing.public_key_bytes)

        chain = AuditChain(tmp_path / "audit.db", now=lambda: 100.0, signing_key=signing)
        for i in range(3):
            chain.append(
                ledger_id=f"l{i}",
                run_id="r",
                event_type=AuditEventType.CREATED,
                payload={"i": i},
            )
        report = chain.verify(verifying_key=verifying)
        assert report.ok
        assert report.signed_events == 3
        assert report.verified_signatures == 3

    def test_wrong_key_fails_verification(self, tmp_path: Path) -> None:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
            Ed25519SigningKey,
            Ed25519VerifyingKey,
        )

        signer = Ed25519SigningKey(
            ed25519.Ed25519PrivateKey.generate().private_bytes_raw()  # type: ignore[attr-defined]
        )
        wrong_pub = Ed25519SigningKey(
            ed25519.Ed25519PrivateKey.generate().private_bytes_raw()  # type: ignore[attr-defined]
        ).public_key_bytes
        verifier = Ed25519VerifyingKey(wrong_pub)

        chain = AuditChain(tmp_path / "audit.db", signing_key=signer)
        chain.append(
            ledger_id="l",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={},
        )
        report = chain.verify(verifying_key=verifier)
        assert report.ok is False
        assert any(v.reason == "signature_invalid" for v in report.violations)
