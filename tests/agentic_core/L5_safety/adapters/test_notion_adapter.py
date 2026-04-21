"""Contract + unit tests for the Notion approval adapter.

Hermetic: uses an in-memory ``FakeNotionTransport`` that implements the
``NotionTransport`` protocol. No Notion API calls are made.

Runs the full contract suite from ``contract.py`` plus Notion-specific
property-shape assertions.
"""

from __future__ import annotations

import json
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
from agentic_core.L5_safety.adapters.notion_approval_adapter import (
    NotionApprovalAdapter,
    NotionProperties,
    STATUS_APPROVED,
    STATUS_CANCELLED,
    STATUS_DENIED,
    STATUS_PENDING,
    STATUS_TIMEOUT,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

from tests.agentic_core.L5_safety.adapters.contract import (
    CONTRACT_ASSERTIONS,
    AdapterContractHarness,
)


# ---------------------------------------------------------------------------
# Fake Notion transport
# ---------------------------------------------------------------------------


@dataclass
class FakeNotionTransport:
    pages: dict[str, dict[str, Any]] = field(default_factory=dict)
    create_should_fail: bool = False
    retrieve_should_fail: bool = False
    archive_should_fail: bool = False

    def create_page(self, database_id: str, properties: Mapping[str, Any]) -> Mapping[str, Any]:
        if self.create_should_fail:
            raise RuntimeError("simulated Notion outage")
        page_id = f"page-{uuid.uuid4().hex[:8]}"
        page = {
            "id": page_id,
            "database_id": database_id,
            "properties": dict(properties),
            "archived": False,
        }
        self.pages[page_id] = page
        return page

    def retrieve_page(self, page_id: str) -> Mapping[str, Any]:
        if self.retrieve_should_fail:
            raise RuntimeError("simulated Notion outage")
        page = self.pages.get(page_id)
        if page is None:
            raise KeyError(page_id)
        return page

    def archive_page(self, page_id: str) -> Mapping[str, Any]:
        if self.archive_should_fail:
            raise RuntimeError("simulated Notion outage")
        page = self.pages.get(page_id)
        if page is None:
            return {"id": page_id, "archived": True}
        page["archived"] = True
        _set_select(page, "Status", STATUS_CANCELLED)
        return page

    # -- test-only resolve helper --------------------------------------

    def resolve(
        self,
        page_id: str,
        outcome: ApprovalOutcomeKind,
        *,
        approver_id: str | None = None,
        reason_code: str | None = None,
        rationale: str | None = None,
    ) -> None:
        page = self.pages[page_id]
        status = {
            ApprovalOutcomeKind.APPROVED: STATUS_APPROVED,
            ApprovalOutcomeKind.DENIED: STATUS_DENIED,
            ApprovalOutcomeKind.TIMEOUT: STATUS_TIMEOUT,
        }[outcome]
        _set_select(page, "Status", status)
        if approver_id:
            _set_text(page, "Approver", approver_id)
        if reason_code:
            _set_select(page, "Reason", reason_code)
        if rationale:
            _set_text(page, "Rationale", rationale)


def _set_select(page: dict[str, Any], prop: str, value: str) -> None:
    page.setdefault("properties", {})[prop] = {"select": {"name": value}}


def _set_text(page: dict[str, Any], prop: str, value: str) -> None:
    page.setdefault("properties", {})[prop] = {
        "rich_text": [{"text": {"content": value}}]
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def transport() -> FakeNotionTransport:
    return FakeNotionTransport()


@pytest.fixture
def adapter(transport: FakeNotionTransport) -> NotionApprovalAdapter:
    return NotionApprovalAdapter(database_id="db-runtime-hitl", transport=transport)


@pytest.fixture
def ledger_entry() -> LedgerEntry:
    return LedgerEntry(
        ledger_id="led-123",
        run_id="run-abc",
        trace_id="tr-def",
        hitl_class=HitlClass.FINANCIAL,
        approver_pool="finance_oncall",
        timeout_s=3600,
        policy_snapshot="snap-xyz",
        envelope={"amount": 10_000},
        state=LedgerState.PENDING,
        created_at=1_700_000_000.0,
        prev_hash="",
        entry_hash="h1",
    )


@pytest.fixture
def harness(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
) -> AdapterContractHarness:
    def resolve(handle, outcome, **kw):
        transport.resolve(handle.external_id, outcome, **kw)

    def fail_transport() -> None:
        transport.create_should_fail = True

    return AdapterContractHarness(
        adapter=adapter,
        ledger_entry=ledger_entry,
        resolve=resolve,
        fail_transport=fail_transport,
    )


# ---------------------------------------------------------------------------
# Contract suite — parametrized over the seven canonical assertions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "assertion",
    CONTRACT_ASSERTIONS,
    ids=[a.__name__ for a in CONTRACT_ASSERTIONS],
)
def test_notion_adapter_contract(assertion, harness: AdapterContractHarness):
    assertion(harness)


# ---------------------------------------------------------------------------
# Notion-specific unit tests
# ---------------------------------------------------------------------------


def test_constructor_rejects_empty_database_id(transport: FakeNotionTransport):
    with pytest.raises(ValueError, match="database_id is required"):
        NotionApprovalAdapter(database_id="", transport=transport)


def test_enqueue_writes_expected_property_shape(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    page = transport.pages[handle.external_id]
    props = page["properties"]
    assert props["Ledger ID"]["title"][0]["text"]["content"] == "led-123"
    assert props["Run ID"]["rich_text"][0]["text"]["content"] == "run-abc"
    assert props["Class"]["select"]["name"] == "financial"
    assert props["Approver Pool"]["select"]["name"] == "finance_oncall"
    assert props["Timeout (s)"]["number"] == 3600
    assert props["Status"]["select"]["name"] == STATUS_PENDING
    assert props["Policy Snapshot"]["rich_text"][0]["text"]["content"] == "snap-xyz"
    envelope_rt = props["Envelope"]["rich_text"][0]["text"]["content"]
    assert json.loads(envelope_rt) == {"amount": 10_000}


def test_enqueue_raises_when_transport_returns_no_id(
    ledger_entry: LedgerEntry,
):
    class BadTransport:
        def create_page(self, database_id, properties):
            return {"no_id_field": True}

        def retrieve_page(self, page_id):
            raise NotImplementedError

        def archive_page(self, page_id):
            raise NotImplementedError

    adapter = NotionApprovalAdapter(database_id="db", transport=BadTransport())
    with pytest.raises(AdapterError, match="no page id"):
        adapter.enqueue(ledger_entry)


def test_poll_wraps_retrieve_error(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    transport.retrieve_should_fail = True
    with pytest.raises(AdapterError, match="retrieve_page failed"):
        adapter.poll(handle)


def test_poll_rejects_unknown_status(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    _set_select(transport.pages[handle.external_id], "Status", "BOGUS")
    with pytest.raises(AdapterError, match="Unrecognized Notion Status"):
        adapter.poll(handle)


def test_poll_cancelled_maps_to_timeout(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    _set_select(transport.pages[handle.external_id], "Status", STATUS_CANCELLED)
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.TIMEOUT
    assert outcome.reason_code == STATUS_CANCELLED


def test_cancel_archives_page(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    adapter.cancel(handle)
    assert transport.pages[handle.external_id]["archived"] is True


def test_cancel_wraps_archive_error(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    transport.archive_should_fail = True
    with pytest.raises(AdapterError, match="archive_page failed"):
        adapter.cancel(handle)


def test_handle_kind_mismatch_rejected(
    adapter: NotionApprovalAdapter,
    ledger_entry: LedgerEntry,
):
    wrong = ApprovalHandle(adapter_kind="slack", external_id="x", ledger_id="l")
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.poll(wrong)
    with pytest.raises(ValueError, match="adapter_kind"):
        adapter.cancel(wrong)


def test_handle_empty_external_id_rejected(
    adapter: NotionApprovalAdapter,
):
    bad = ApprovalHandle(adapter_kind="notion", external_id="", ledger_id="l")
    with pytest.raises(ValueError, match="external_id"):
        adapter.poll(bad)


def test_read_helpers_handle_malformed_shapes():
    """Defensive branches in _read_select / _read_text / _read_status."""
    from agentic_core.L5_safety.adapters.notion_approval_adapter import (
        _read_select,
        _read_status,
        _read_text,
    )

    # Non-mapping page → None / PENDING fallback
    assert _read_select({}, "Status") is None
    assert _read_status({}) == STATUS_PENDING
    # properties is not a mapping
    assert _read_select({"properties": "bad"}, "Status") is None
    assert _read_text({"properties": "bad"}, "Approver") is None
    # entry is not a mapping
    assert _read_select({"properties": {"Status": "bad"}}, "Status") is None
    assert _read_text({"properties": {"Approver": "bad"}}, "Approver") is None
    # select present but no name
    assert _read_select({"properties": {"Status": {"select": {}}}}, "Status") is None
    # select is not a mapping (e.g. string, None) → None
    assert _read_select({"properties": {"Status": {"select": "raw"}}}, "Status") is None
    # rich_text empty list
    assert _read_text({"properties": {"Approver": {"rich_text": []}}}, "Approver") is None
    # rich_text[0] not a mapping
    assert _read_text({"properties": {"Approver": {"rich_text": ["raw"]}}}, "Approver") is None
    # rich_text[0] mapping but no text/plain_text content
    assert (
        _read_text({"properties": {"Approver": {"rich_text": [{"foo": "bar"}]}}}, "Approver")
        is None
    )


def test_notion_properties_round_trip():
    props = NotionProperties(
        ledger_id="l",
        run_id="r",
        trace_id="t",
        hitl_class="financial",
        approver_pool="finance_oncall",
        timeout_s=60,
        status=STATUS_PENDING,
        envelope_json="{}",
        policy_snapshot="snap",
    )
    payload = props.to_notion_payload()
    assert payload["Ledger ID"]["title"][0]["text"]["content"] == "l"
    assert payload["Timeout (s)"]["number"] == 60
    assert payload["Status"]["select"]["name"] == STATUS_PENDING


def test_read_text_handles_title_shape(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    # Notion returns title rather than rich_text for some property types.
    handle = adapter.enqueue(ledger_entry)
    page = transport.pages[handle.external_id]
    page["properties"]["Approver"] = {"title": [{"text": {"content": "eve"}}]}
    _set_select(page, "Status", STATUS_APPROVED)
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.APPROVED
    assert outcome.approver_id == "eve"


def test_read_text_handles_plain_text_fallback(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    page = transport.pages[handle.external_id]
    page["properties"]["Approver"] = {"rich_text": [{"plain_text": "zed"}]}
    _set_select(page, "Status", STATUS_APPROVED)
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.approver_id == "zed"


def test_enqueue_reraises_adapter_error_directly(ledger_entry: LedgerEntry):
    """AdapterError from transport must pass through, not be re-wrapped."""
    from agentic_core.L5_safety.adapters.human_approval_adapter import AdapterError

    class RaisingTransport:
        def create_page(self, database_id, properties):
            raise AdapterError("upstream boom")

        def retrieve_page(self, page_id):
            raise AdapterError("upstream boom")

        def archive_page(self, page_id):
            raise AdapterError("upstream boom")

    adapter = NotionApprovalAdapter(database_id="db", transport=RaisingTransport())
    with pytest.raises(AdapterError, match="upstream boom"):
        adapter.enqueue(ledger_entry)


def test_poll_and_cancel_reraise_adapter_error_directly(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)

    # Swap in a transport that raises AdapterError from poll/cancel.
    class RaisingTransport:
        def create_page(self, database_id, properties):
            raise AssertionError("not called")

        def retrieve_page(self, page_id):
            raise AdapterError("poll boom")

        def archive_page(self, page_id):
            raise AdapterError("archive boom")

    adapter2 = NotionApprovalAdapter(database_id="db", transport=RaisingTransport())
    bad_handle = ApprovalHandle(
        adapter_kind="notion", external_id="x", ledger_id="l"
    )
    with pytest.raises(AdapterError, match="poll boom"):
        adapter2.poll(bad_handle)
    with pytest.raises(AdapterError, match="archive boom"):
        adapter2.cancel(bad_handle)


def test_read_missing_properties_returns_none_approver(
    adapter: NotionApprovalAdapter,
    transport: FakeNotionTransport,
    ledger_entry: LedgerEntry,
):
    handle = adapter.enqueue(ledger_entry)
    page = transport.pages[handle.external_id]
    _set_select(page, "Status", STATUS_APPROVED)
    # No Approver / Reason / Rationale set.
    outcome = adapter.poll(handle)
    assert outcome is not None
    assert outcome.approver_id is None
    assert outcome.reason_code is None
    assert outcome.rationale is None
