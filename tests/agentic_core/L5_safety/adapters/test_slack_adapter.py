"""Contract + unit tests for the Slack approval adapter.

Hermetic: uses an in-memory ``FakeSlackTransport``. No Slack API calls.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
)
from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcomeKind,
)
from agentic_core.L5_safety.adapters.slack_approval_adapter import (
    STATUS_APPROVED,
    STATUS_CANCELLED,
    STATUS_DENIED,
    STATUS_PENDING,
    STATUS_TIMEOUT,
    SlackApprovalAdapter,
    build_approval_blocks,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

from tests.agentic_core.L5_safety.adapters.contract import (
    CONTRACT_ASSERTIONS,
    AdapterContractHarness,
)


@dataclass
class FakeSlackTransport:
    messages: dict[str, dict[str, Any]] = field(default_factory=dict)
    create_should_fail: bool = False
    get_should_fail: bool = False
    delete_should_fail: bool = False

    def post_message(self, channel, text, blocks):
        if self.create_should_fail:
            raise RuntimeError("slack outage")
        ts = f"ts-{uuid.uuid4().hex[:8]}"
        self.messages[ts] = {
            "ts": ts,
            "channel": channel,
            "text": text,
            "blocks": blocks,
            "status": STATUS_PENDING,
            "metadata": {},
        }
        return {"ts": ts, "channel": channel}

    def get_message(self, channel, ts):
        if self.get_should_fail:
            raise RuntimeError("slack outage")
        msg = self.messages.get(ts)
        if msg is None:
            raise KeyError(ts)
        return msg

    def delete_message(self, channel, ts):
        if self.delete_should_fail:
            raise RuntimeError("slack outage")
        msg = self.messages.get(ts)
        if msg:
            msg["status"] = STATUS_CANCELLED
        return {"ok": True}

    # test-only resolve helper
    def resolve(self, ts, outcome, *, approver_id=None, reason_code=None, rationale=None):
        status = {
            ApprovalOutcomeKind.APPROVED: STATUS_APPROVED,
            ApprovalOutcomeKind.DENIED: STATUS_DENIED,
            ApprovalOutcomeKind.TIMEOUT: STATUS_TIMEOUT,
        }[outcome]
        msg = self.messages[ts]
        msg["status"] = status
        msg["metadata"] = {
            "approver_id": approver_id,
            "reason_code": reason_code,
            "rationale": rationale,
        }


@pytest.fixture
def transport():
    return FakeSlackTransport()


@pytest.fixture
def adapter(transport):
    return SlackApprovalAdapter(channel="C123", transport=transport)


@pytest.fixture
def ledger_entry():
    return LedgerEntry(
        ledger_id="led-s1", run_id="r1", trace_id="t1",
        hitl_class=HitlClass.SAFETY, approver_pool="safety_oncall",
        timeout_s=1800, policy_snapshot="snap", envelope={"risk": "high"},
        state=LedgerState.PENDING, created_at=1.0,
    )


@pytest.fixture
def harness(adapter, transport, ledger_entry):
    def resolve(handle, outcome, **kw):
        transport.resolve(handle.external_id, outcome, **kw)

    def fail_transport():
        transport.create_should_fail = True

    return AdapterContractHarness(
        adapter=adapter, ledger_entry=ledger_entry,
        resolve=resolve, fail_transport=fail_transport,
    )


@pytest.mark.parametrize(
    "assertion", CONTRACT_ASSERTIONS, ids=[a.__name__ for a in CONTRACT_ASSERTIONS]
)
def test_slack_adapter_contract(assertion, harness):
    assertion(harness)


# -- Slack-specific unit tests ------------------------------------------


def test_constructor_rejects_empty_channel(transport):
    with pytest.raises(ValueError, match="channel is required"):
        SlackApprovalAdapter(channel="", transport=transport)


def test_build_approval_blocks_contains_ledger_id(ledger_entry):
    blocks = build_approval_blocks(ledger_entry)
    assert any(
        b.get("block_id") == ledger_entry.ledger_id
        for b in blocks
        if isinstance(b, dict)
    )


def test_enqueue_wraps_transport_error(adapter, transport, ledger_entry):
    transport.create_should_fail = True
    with pytest.raises(AdapterError, match="post_message failed"):
        adapter.enqueue(ledger_entry)


def test_enqueue_raises_when_no_ts(ledger_entry):
    class BadTransport:
        def post_message(self, channel, text, blocks):
            return {"no_ts": True}

        def get_message(self, channel, ts): ...
        def delete_message(self, channel, ts): ...

    adapter = SlackApprovalAdapter(channel="C", transport=BadTransport())
    with pytest.raises(AdapterError, match="no ts"):
        adapter.enqueue(ledger_entry)


def test_poll_wraps_transport_error(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.get_should_fail = True
    with pytest.raises(AdapterError, match="get_message failed"):
        adapter.poll(handle)


def test_poll_unknown_status_raises(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.messages[handle.external_id]["status"] = "weird"
    with pytest.raises(AdapterError, match="Unrecognized"):
        adapter.poll(handle)


def test_poll_cancelled_maps_to_timeout(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.messages[handle.external_id]["status"] = STATUS_CANCELLED
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.TIMEOUT
    assert outcome.reason_code == STATUS_CANCELLED.upper()


def test_cancel_wraps_transport_error(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.delete_should_fail = True
    with pytest.raises(AdapterError, match="delete_message failed"):
        adapter.cancel(handle)


def test_handle_kind_mismatch_rejected(adapter):
    wrong = ApprovalHandle(adapter_kind="notion", external_id="x", ledger_id="l")
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.poll(wrong)
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.cancel(wrong)


def test_handle_empty_external_id_rejected(adapter):
    bad = ApprovalHandle(adapter_kind="slack", external_id="", ledger_id="l")
    with pytest.raises(ValueError, match="external_id"):
        adapter.poll(bad)


def test_adapter_error_passes_through_enqueue(ledger_entry):
    class RaisingTransport:
        def post_message(self, channel, text, blocks):
            raise AdapterError("upstream")
        def get_message(self, channel, ts):
            raise AdapterError("upstream")
        def delete_message(self, channel, ts):
            raise AdapterError("upstream")

    adapter = SlackApprovalAdapter(channel="C", transport=RaisingTransport())
    with pytest.raises(AdapterError, match="upstream"):
        adapter.enqueue(ledger_entry)


def test_adapter_error_passes_through_poll_cancel(ledger_entry):
    class RaisingTransport:
        def post_message(self, channel, text, blocks):
            return {"ts": "ok"}
        def get_message(self, channel, ts):
            raise AdapterError("poll upstream")
        def delete_message(self, channel, ts):
            raise AdapterError("cancel upstream")

    adapter = SlackApprovalAdapter(channel="C", transport=RaisingTransport())
    handle = adapter.enqueue(ledger_entry)
    with pytest.raises(AdapterError, match="poll upstream"):
        adapter.poll(handle)
    with pytest.raises(AdapterError, match="cancel upstream"):
        adapter.cancel(handle)


def test_poll_handles_non_string_metadata(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.messages[handle.external_id]["status"] = STATUS_APPROVED
    transport.messages[handle.external_id]["metadata"] = "not-a-mapping"
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.APPROVED
    assert outcome.approver_id is None


def test_poll_missing_status_treated_as_pending(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.messages[handle.external_id].pop("status")
    assert adapter.poll(handle) is None


def test_read_status_non_mapping_returns_pending():
    from agentic_core.L5_safety.adapters.slack_approval_adapter import _read_status
    assert _read_status("not-a-mapping") == STATUS_PENDING  # type: ignore[arg-type]
    assert _read_status(None) == STATUS_PENDING  # type: ignore[arg-type]
