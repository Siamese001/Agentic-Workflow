"""Contract + unit tests for the email magic-link adapter.

Hermetic: in-memory ``FakeEmailTransport`` + ``FakeMagicLinkStore``.
No email is sent.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
)
from agentic_core.L5_safety.adapters.email_magic_link_adapter import (
    EmailMagicLinkAdapter,
    StoredOutcome,
)
from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcomeKind,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

from tests.agentic_core.L5_safety.adapters.contract import (
    CONTRACT_ASSERTIONS,
    AdapterContractHarness,
)


@dataclass
class FakeEmailTransport:
    sent: list[dict[str, Any]] = field(default_factory=list)
    should_fail: bool = False

    def send(self, to, subject, body):
        if self.should_fail:
            raise RuntimeError("smtp outage")
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        self.sent.append({"to": to, "subject": subject, "body": body, "id": message_id})
        return message_id


@dataclass
class FakeMagicLinkStore:
    entries: dict[str, StoredOutcome | None] = field(default_factory=dict)
    record_should_fail: bool = False
    get_should_fail: bool = False
    cancel_should_fail: bool = False

    def record_pending(self, ledger_id):
        if self.record_should_fail:
            raise RuntimeError("store down")
        self.entries[ledger_id] = None  # pending sentinel

    def get(self, ledger_id):
        if self.get_should_fail:
            raise RuntimeError("store down")
        return self.entries.get(ledger_id)

    def cancel(self, ledger_id):
        if self.cancel_should_fail:
            raise RuntimeError("store down")
        self.entries[ledger_id] = StoredOutcome(
            kind=ApprovalOutcomeKind.TIMEOUT, reason_code="CANCELLED"
        )

    # test-only helper
    def resolve(self, ledger_id, outcome, *, approver_id=None, reason_code=None, rationale=None):
        self.entries[ledger_id] = StoredOutcome(
            kind=outcome,
            approver_id=approver_id,
            reason_code=reason_code,
            rationale=rationale,
        )


@pytest.fixture
def email():
    return FakeEmailTransport()


@pytest.fixture
def store():
    return FakeMagicLinkStore()


@pytest.fixture
def adapter(email, store):
    return EmailMagicLinkAdapter(
        base_url="https://hitl.example.com",
        signing_secret=b"test-secret-32-bytes-long-xxxxxx",
        email=email,
        store=store,
    )


@pytest.fixture
def ledger_entry():
    return LedgerEntry(
        ledger_id="led-e1", run_id="r1", trace_id="t1",
        hitl_class=HitlClass.FINANCIAL, approver_pool="finance@example.com",
        timeout_s=3600, policy_snapshot="snap", envelope={"amount": 5000},
        state=LedgerState.PENDING, created_at=1.0,
    )


@pytest.fixture
def harness(adapter, store, ledger_entry):
    def resolve(handle, outcome, **kw):
        store.resolve(handle.ledger_id, outcome, **kw)

    def fail_transport():
        # Fail the email send so enqueue raises.
        adapter._email.should_fail = True  # type: ignore[attr-defined]

    return AdapterContractHarness(
        adapter=adapter, ledger_entry=ledger_entry,
        resolve=resolve, fail_transport=fail_transport,
    )


@pytest.mark.parametrize(
    "assertion", CONTRACT_ASSERTIONS, ids=[a.__name__ for a in CONTRACT_ASSERTIONS]
)
def test_email_magic_link_contract(assertion, harness):
    assertion(harness)


# -- Email-specific unit tests ------------------------------------------


def test_constructor_rejects_empty_base_url(email, store):
    with pytest.raises(ValueError, match="base_url"):
        EmailMagicLinkAdapter(
            base_url="", signing_secret=b"s", email=email, store=store
        )


def test_constructor_rejects_empty_secret(email, store):
    with pytest.raises(ValueError, match="signing_secret"):
        EmailMagicLinkAdapter(
            base_url="https://x", signing_secret=b"", email=email, store=store
        )


def test_enqueue_records_pending_and_sends_email(adapter, email, store, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    assert handle.ledger_id in store.entries
    assert store.entries[ledger_entry.ledger_id] is None
    assert len(email.sent) == 1
    body = email.sent[0]["body"]
    assert "Approve:" in body
    assert "Deny:" in body
    assert ledger_entry.ledger_id in body
    assert email.sent[0]["to"] == ledger_entry.approver_pool


def test_url_signing_and_verify_round_trip(adapter):
    sig = adapter.sign("led-1", "approve")
    assert adapter.verify("led-1", "approve", sig) is True
    assert adapter.verify("led-1", "deny", sig) is False
    assert adapter.verify("led-2", "approve", sig) is False
    assert adapter.verify("led-1", "approve", "deadbeef") is False


def test_enqueue_wraps_store_error(adapter, store, ledger_entry):
    store.record_should_fail = True
    with pytest.raises(AdapterError, match="record_pending failed"):
        adapter.enqueue(ledger_entry)


def test_enqueue_wraps_email_error(adapter, email, ledger_entry):
    email.should_fail = True
    with pytest.raises(AdapterError, match="Email send failed"):
        adapter.enqueue(ledger_entry)


def test_enqueue_raises_when_no_message_id(store, ledger_entry):
    class NullEmail:
        def send(self, to, subject, body): return ""

    adapter = EmailMagicLinkAdapter(
        base_url="https://x", signing_secret=b"s", email=NullEmail(), store=store
    )
    with pytest.raises(AdapterError, match="no message_id"):
        adapter.enqueue(ledger_entry)


def test_poll_pending_returns_none(adapter, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    assert adapter.poll(handle) is None


def test_poll_approved(adapter, store, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    store.resolve(
        handle.ledger_id, ApprovalOutcomeKind.APPROVED,
        approver_id="alice", rationale="looks good",
    )
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.APPROVED
    assert outcome.approver_id == "alice"
    assert outcome.rationale == "looks good"


def test_poll_wraps_store_error(adapter, store, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    store.get_should_fail = True
    with pytest.raises(AdapterError, match="MagicLinkStore.get failed"):
        adapter.poll(handle)


def test_cancel_sets_cancelled_outcome(adapter, store, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    adapter.cancel(handle)
    entry = store.entries[handle.ledger_id]
    assert entry is not None
    assert entry.kind is ApprovalOutcomeKind.TIMEOUT
    assert entry.reason_code == "CANCELLED"


def test_cancel_wraps_store_error(adapter, store, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    store.cancel_should_fail = True
    with pytest.raises(AdapterError, match="MagicLinkStore.cancel failed"):
        adapter.cancel(handle)


def test_handle_kind_mismatch_rejected(adapter):
    wrong = ApprovalHandle(adapter_kind="slack", external_id="x", ledger_id="l")
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.poll(wrong)
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.cancel(wrong)


def test_handle_empty_external_id_rejected(adapter):
    bad = ApprovalHandle(adapter_kind="email_magic_link", external_id="", ledger_id="l")
    with pytest.raises(ValueError, match="external_id"):
        adapter.poll(bad)


def test_adapter_errors_pass_through(store, ledger_entry):
    class RaisingEmail:
        def send(self, to, subject, body):
            raise AdapterError("upstream-email")

    class RaisingStore:
        def record_pending(self, ledger_id):
            raise AdapterError("upstream-record")
        def get(self, ledger_id):
            raise AdapterError("upstream-get")
        def cancel(self, ledger_id):
            raise AdapterError("upstream-cancel")

    # Record failure
    adapter = EmailMagicLinkAdapter(
        base_url="https://x", signing_secret=b"s",
        email=FakeEmailTransport(), store=RaisingStore(),
    )
    with pytest.raises(AdapterError, match="upstream-record"):
        adapter.enqueue(ledger_entry)

    # Email failure as AdapterError (skip store record)
    adapter2 = EmailMagicLinkAdapter(
        base_url="https://x", signing_secret=b"s",
        email=RaisingEmail(), store=store,
    )
    with pytest.raises(AdapterError, match="upstream-email"):
        adapter2.enqueue(ledger_entry)

    # Poll + cancel pass-through
    class PollRaiseStore(RaisingStore):
        def record_pending(self, ledger_id): return None

    adapter3 = EmailMagicLinkAdapter(
        base_url="https://x", signing_secret=b"s",
        email=FakeEmailTransport(), store=PollRaiseStore(),
    )
    handle = adapter3.enqueue(ledger_entry)
    with pytest.raises(AdapterError, match="upstream-get"):
        adapter3.poll(handle)
    with pytest.raises(AdapterError, match="upstream-cancel"):
        adapter3.cancel(handle)
