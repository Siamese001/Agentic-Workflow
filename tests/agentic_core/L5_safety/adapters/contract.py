"""Shared contract test suite for ``HumanApprovalAdapter`` implementations.

Every concrete adapter (Notion, Slack, Orkes, email magic link, …) MUST pass
this suite unchanged. Adapters provide a ``contract_fixture`` in their test
module that yields an ``AdapterContractHarness`` — the parametrized test
class below consumes it.

The harness exposes:

- ``.adapter`` — the adapter under test
- ``.ledger_entry`` — a ready-to-enqueue ``LedgerEntry``
- ``.resolve(handle, outcome_kind, **kw)`` — simulate the human act on the
  external surface (test-only; each adapter implements its own hook)

Hermetic: no network, no external state. See ``test_notion_adapter.py`` for
the Notion concrete harness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

import pytest

from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcome,
    ApprovalOutcomeKind,
    HumanApprovalAdapter,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
)


class ResolveFn(Protocol):
    def __call__(
        self,
        handle: ApprovalHandle,
        outcome: ApprovalOutcomeKind,
        *,
        approver_id: str | None = None,
        reason_code: str | None = None,
        rationale: str | None = None,
    ) -> None: ...


@dataclass
class AdapterContractHarness:
    adapter: HumanApprovalAdapter
    ledger_entry: LedgerEntry
    resolve: ResolveFn
    fail_transport: Callable[[], None]


def run_contract_suite(harness_factory: Callable[[], AdapterContractHarness]) -> None:
    """Driver exposed to adapter test modules.

    Each adapter test module calls this once; the enclosed function creates
    pytest tests dynamically via parametrization is not used — we re-run the
    body inline so pytest discovers adapter-specific IDs.
    """
    # Not parametrized — adapter tests call the individual assertions directly.
    # Kept as a docstring anchor for contributors.
    _ = harness_factory
    raise NotImplementedError(  # pragma: no cover — reference only
        "run_contract_suite is documentation; adapters use contract_assertions directly"
    )


# ---------------------------------------------------------------------------
# Contract assertions — called by each adapter's test module
# ---------------------------------------------------------------------------


def assert_enqueue_returns_handle(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    assert isinstance(handle, ApprovalHandle)
    assert handle.adapter_kind == h.adapter.kind
    assert handle.external_id
    assert handle.ledger_id == h.ledger_entry.ledger_id


def assert_poll_pending_returns_none(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    assert h.adapter.poll(handle) is None


def assert_poll_approved(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    h.resolve(
        handle,
        ApprovalOutcomeKind.APPROVED,
        approver_id="alice",
        rationale="ok",
    )
    outcome = h.adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.APPROVED
    assert outcome.approver_id == "alice"
    assert outcome.rationale == "ok"


def assert_poll_denied(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    h.resolve(
        handle,
        ApprovalOutcomeKind.DENIED,
        approver_id="bob",
        reason_code="NON_COMPLIANT",
    )
    outcome = h.adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.DENIED
    assert outcome.reason_code == "NON_COMPLIANT"


def assert_poll_timeout(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    h.resolve(handle, ApprovalOutcomeKind.TIMEOUT)
    outcome = h.adapter.poll(handle)
    assert outcome is not None
    assert outcome.kind is ApprovalOutcomeKind.TIMEOUT


def assert_cancel_is_idempotent(h: AdapterContractHarness) -> None:
    handle = h.adapter.enqueue(h.ledger_entry)
    h.adapter.cancel(handle)
    # Second cancel must not raise.
    h.adapter.cancel(handle, reason="again")


def assert_transport_error_wraps_to_adapter_error(h: AdapterContractHarness) -> None:
    h.fail_transport()
    with pytest.raises(AdapterError):
        h.adapter.enqueue(h.ledger_entry)


# The canonical ordered list of contract assertions, used by adapter tests.
CONTRACT_ASSERTIONS: list[Callable[[AdapterContractHarness], None]] = [
    assert_enqueue_returns_handle,
    assert_poll_pending_returns_none,
    assert_poll_approved,
    assert_poll_denied,
    assert_poll_timeout,
    assert_cancel_is_idempotent,
    assert_transport_error_wraps_to_adapter_error,
]


__all__ = [
    "AdapterContractHarness",
    "CONTRACT_ASSERTIONS",
    "assert_cancel_is_idempotent",
    "assert_enqueue_returns_handle",
    "assert_poll_approved",
    "assert_poll_denied",
    "assert_poll_pending_returns_none",
    "assert_poll_timeout",
    "assert_transport_error_wraps_to_adapter_error",
    "run_contract_suite",
]
