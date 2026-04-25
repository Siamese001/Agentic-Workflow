"""Unit tests for agentic_core.L5_safety.adapters.human_approval_adapter.

Targets Wave-2 / Phase P6. Source: 108 lines, fan_in=44 (L5, impact 88.0).
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcome,
    ApprovalOutcomeKind,
    HumanApprovalAdapter,
)


class TestApprovalOutcomeKind:
    def test_enum_values(self) -> None:
        assert ApprovalOutcomeKind.APPROVED.value == "approved"
        assert ApprovalOutcomeKind.DENIED.value == "denied"
        assert ApprovalOutcomeKind.TIMEOUT.value == "timeout"

    def test_is_str_enum(self) -> None:
        assert isinstance(ApprovalOutcomeKind.APPROVED, str)

    def test_enum_size(self) -> None:
        assert len(list(ApprovalOutcomeKind)) == 3

    def test_string_equality(self) -> None:
        assert ApprovalOutcomeKind.APPROVED == "approved"


class TestApprovalHandle:
    def test_minimal_construction(self) -> None:
        h = ApprovalHandle(adapter_kind="notion", external_id="page-123", ledger_id="L-1")
        assert h.adapter_kind == "notion"
        assert h.external_id == "page-123"
        assert h.ledger_id == "L-1"

    def test_is_frozen(self) -> None:
        h = ApprovalHandle(adapter_kind="slack", external_id="x", ledger_id="L")
        with pytest.raises(AttributeError):
            h.external_id = "other"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        h1 = ApprovalHandle(adapter_kind="x", external_id="1", ledger_id="L")
        h2 = ApprovalHandle(adapter_kind="x", external_id="1", ledger_id="L")
        assert h1 == h2
        assert hash(h1) == hash(h2)


class TestApprovalOutcome:
    def test_approved_minimal(self) -> None:
        o = ApprovalOutcome(kind=ApprovalOutcomeKind.APPROVED)
        assert o.kind == ApprovalOutcomeKind.APPROVED
        assert o.approver_id is None
        assert o.reason_code is None
        assert o.rationale is None

    def test_denied_full(self) -> None:
        o = ApprovalOutcome(
            kind=ApprovalOutcomeKind.DENIED,
            approver_id="user-1",
            reason_code="POLICY_BREACH",
            rationale="Too risky",
        )
        assert o.kind == ApprovalOutcomeKind.DENIED
        assert o.approver_id == "user-1"
        assert o.rationale == "Too risky"

    def test_frozen(self) -> None:
        o = ApprovalOutcome(kind=ApprovalOutcomeKind.TIMEOUT)
        with pytest.raises(AttributeError):
            o.approver_id = "x"  # type: ignore[misc]


class TestAdapterError:
    def test_is_runtime_error_subclass(self) -> None:
        assert issubclass(AdapterError, RuntimeError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(AdapterError, match="transport"):
            raise AdapterError("transport failure")


class TestHumanApprovalAdapterABC:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError, match="abstract"):
            HumanApprovalAdapter()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated

    def test_default_kind_is_abstract(self) -> None:
        assert HumanApprovalAdapter.kind == "abstract"

    def test_subclass_must_implement_all_three(self) -> None:
        class PartialImpl(HumanApprovalAdapter):
            def enqueue(self, entry):  # type: ignore[override]
                raise NotImplementedError

            # Missing poll and cancel

        with pytest.raises(TypeError, match="abstract"):
            PartialImpl()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated

    def test_concrete_subclass_instantiable(self) -> None:
        class FakeAdapter(HumanApprovalAdapter):
            kind = "fake"

            def enqueue(self, entry):
                return ApprovalHandle(adapter_kind="fake", external_id="e", ledger_id="L")

            def poll(self, handle):
                return None

            def cancel(self, handle, reason="CANCELLED"):
                return None

        a = FakeAdapter()
        assert a.kind == "fake"
        h = a.enqueue(entry=None)
        assert h.adapter_kind == "fake"
        assert a.poll(h) is None
        # Must not raise
        a.cancel(h)
        a.cancel(h, reason="double-cancel-idempotent")


class TestExports:
    def test_all_public_symbols_exported(self) -> None:
        import agentic_core.L5_safety.adapters.human_approval_adapter as mod

        assert set(mod.__all__) == {
            "AdapterError",
            "ApprovalHandle",
            "ApprovalOutcome",
            "ApprovalOutcomeKind",
            "HumanApprovalAdapter",
        }
