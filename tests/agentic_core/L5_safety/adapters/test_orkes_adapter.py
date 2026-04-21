"""Contract + unit tests for the Orkes approval adapter.

Hermetic: uses an in-memory ``FakeOrkesTransport``. No Orkes API calls.
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
from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcomeKind,
)
from agentic_core.L5_safety.adapters.orkes_approval_adapter import (
    DECISION_APPROVE,
    DECISION_DENY,
    OrkesApprovalAdapter,
    TASK_CANCELED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_IN_PROGRESS,
    TASK_SCHEDULED,
    TASK_TERMINATED,
    TASK_TIMED_OUT,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

from tests.agentic_core.L5_safety.adapters.contract import (
    CONTRACT_ASSERTIONS,
    AdapterContractHarness,
)


@dataclass
class FakeOrkesTransport:
    tasks: dict[str, dict[str, Any]] = field(default_factory=dict)
    create_should_fail: bool = False
    get_should_fail: bool = False
    terminate_should_fail: bool = False

    def create_human_task(self, task_def_name, input_data):
        if self.create_should_fail:
            raise RuntimeError("orkes outage")
        task_id = f"tk-{uuid.uuid4().hex[:8]}"
        self.tasks[task_id] = {
            "task_id": task_id,
            "task_def_name": task_def_name,
            "input": dict(input_data),
            "status": TASK_IN_PROGRESS,
            "output": {},
        }
        return {"task_id": task_id}

    def get_human_task(self, task_id):
        if self.get_should_fail:
            raise RuntimeError("orkes outage")
        task = self.tasks.get(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    def terminate_human_task(self, task_id, reason):
        if self.terminate_should_fail:
            raise RuntimeError("orkes outage")
        task = self.tasks.get(task_id)
        if task:
            task["status"] = TASK_TERMINATED
            task.setdefault("output", {})["terminate_reason"] = reason
        return {"ok": True}

    # test-only resolve helper
    def resolve(self, task_id, outcome, *, approver_id=None, reason_code=None, rationale=None):
        task = self.tasks[task_id]
        if outcome is ApprovalOutcomeKind.APPROVED:
            task["status"] = TASK_COMPLETED
            task["output"] = {
                "decision": DECISION_APPROVE,
                "approver_id": approver_id,
                "rationale": rationale,
            }
        elif outcome is ApprovalOutcomeKind.DENIED:
            task["status"] = TASK_COMPLETED
            task["output"] = {
                "decision": DECISION_DENY,
                "approver_id": approver_id,
                "reason_code": reason_code,
                "rationale": rationale,
            }
        elif outcome is ApprovalOutcomeKind.TIMEOUT:
            task["status"] = TASK_TIMED_OUT


@pytest.fixture
def transport():
    return FakeOrkesTransport()


@pytest.fixture
def adapter(transport):
    return OrkesApprovalAdapter(task_def_name="hitl_approval", transport=transport)


@pytest.fixture
def ledger_entry():
    return LedgerEntry(
        ledger_id="led-o1", run_id="r1", trace_id="t1",
        hitl_class=HitlClass.REGULATED, approver_pool="compliance_oncall",
        timeout_s=7200, policy_snapshot="snap", envelope={"filing": "10-K"},
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
def test_orkes_adapter_contract(assertion, harness):
    assertion(harness)


# -- Orkes-specific unit tests ------------------------------------------


def test_constructor_rejects_empty_task_def(transport):
    with pytest.raises(ValueError, match="task_def_name is required"):
        OrkesApprovalAdapter(task_def_name="", transport=transport)


def test_enqueue_wraps_transport_error(adapter, transport, ledger_entry):
    transport.create_should_fail = True
    with pytest.raises(AdapterError, match="create_human_task failed"):
        adapter.enqueue(ledger_entry)


def test_enqueue_raises_when_no_task_id(ledger_entry):
    class BadTransport:
        def create_human_task(self, *_a, **_k): return {"nothing": 1}
        def get_human_task(self, *_a, **_k): ...
        def terminate_human_task(self, *_a, **_k): ...

    adapter = OrkesApprovalAdapter(task_def_name="x", transport=BadTransport())
    with pytest.raises(AdapterError, match="no task_id"):
        adapter.enqueue(ledger_entry)


def test_poll_pending_scheduled_returns_none(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = TASK_SCHEDULED
    assert adapter.poll(handle) is None


def test_poll_completed_approve(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.resolve(
        handle.external_id, ApprovalOutcomeKind.APPROVED,
        approver_id="alice", rationale="ok",
    )
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.APPROVED
    assert outcome.approver_id == "alice"


def test_poll_completed_deny_with_reason(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.resolve(
        handle.external_id, ApprovalOutcomeKind.DENIED,
        approver_id="bob", reason_code="NON_COMPLIANT",
    )
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.DENIED
    assert outcome.reason_code == "NON_COMPLIANT"


def test_poll_completed_deny_default_reason(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = TASK_COMPLETED
    transport.tasks[handle.external_id]["output"] = {"decision": DECISION_DENY}
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.reason_code == "ORKES_DENIED"


def test_poll_completed_unknown_decision_raises(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = TASK_COMPLETED
    transport.tasks[handle.external_id]["output"] = {"decision": "maybe"}
    with pytest.raises(AdapterError, match="Unrecognized Orkes decision"):
        adapter.poll(handle)


def test_poll_failed_maps_to_denied(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = TASK_FAILED
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.DENIED
    assert outcome.reason_code == "ORKES_FAILED"


def test_poll_terminated_maps_to_timeout_cancelled(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = TASK_CANCELED
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.TIMEOUT
    assert outcome.reason_code == "CANCELLED"


def test_poll_unknown_status_raises(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.tasks[handle.external_id]["status"] = "WEIRD"
    with pytest.raises(AdapterError, match="task status"):
        adapter.poll(handle)


def test_poll_wraps_transport_error(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.get_should_fail = True
    with pytest.raises(AdapterError, match="get_human_task failed"):
        adapter.poll(handle)


def test_cancel_wraps_transport_error(adapter, transport, ledger_entry):
    handle = adapter.enqueue(ledger_entry)
    transport.terminate_should_fail = True
    with pytest.raises(AdapterError, match="terminate_human_task failed"):
        adapter.cancel(handle)


def test_handle_kind_mismatch_rejected(adapter):
    wrong = ApprovalHandle(adapter_kind="slack", external_id="x", ledger_id="l")
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.poll(wrong)
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.cancel(wrong)


def test_handle_empty_external_id_rejected(adapter):
    bad = ApprovalHandle(adapter_kind="orkes", external_id="", ledger_id="l")
    with pytest.raises(ValueError, match="external_id"):
        adapter.poll(bad)


def test_adapter_errors_pass_through(ledger_entry):
    class RaisingTransport:
        def create_human_task(self, *_a, **_k):
            raise AdapterError("upstream-create")
        def get_human_task(self, *_a, **_k):
            raise AdapterError("upstream-get")
        def terminate_human_task(self, *_a, **_k):
            raise AdapterError("upstream-term")

    adapter = OrkesApprovalAdapter(task_def_name="x", transport=RaisingTransport())
    with pytest.raises(AdapterError, match="upstream-create"):
        adapter.enqueue(ledger_entry)


def test_read_helper_non_mapping_returns_none():
    from agentic_core.L5_safety.adapters.orkes_approval_adapter import _read
    assert _read("not-a-mapping", "key") is None
    assert _read(None, "key") is None


def test_adapter_errors_pass_through_poll_cancel(ledger_entry):
    class TwoStageTransport:
        _created = False

        def create_human_task(self, *_a, **_k):
            self._created = True
            return {"task_id": "t1"}

        def get_human_task(self, *_a, **_k):
            raise AdapterError("upstream-get")

        def terminate_human_task(self, *_a, **_k):
            raise AdapterError("upstream-term")

    transport = TwoStageTransport()
    adapter = OrkesApprovalAdapter(task_def_name="x", transport=transport)
    handle = adapter.enqueue(ledger_entry)
    with pytest.raises(AdapterError, match="upstream-get"):
        adapter.poll(handle)
    with pytest.raises(AdapterError, match="upstream-term"):
        adapter.cancel(handle)
