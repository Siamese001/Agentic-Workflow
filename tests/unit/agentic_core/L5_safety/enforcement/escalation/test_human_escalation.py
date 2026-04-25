"""Unit tests for agentic_core.L5_safety.enforcement.escalation.human_escalation.

Targets Wave-5 / Phase P13. Source: 586 lines, fan_in=29 (L5, impact 58.0).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from agentic_core.L5_safety.enforcement.escalation.human_escalation import (
    EscalationTriggerType,
    HumanEscalationError,
    HumanEscalationRecord,
    HumanEscalationRegistry,
    ReviewerOutcome,
    get_human_escalation_registry,
    reset_human_escalation_registry,
)


@pytest.fixture(autouse=True)
def _fresh_registry() -> Iterator[None]:
    reset_human_escalation_registry()
    yield
    reset_human_escalation_registry()


class TestEnums:
    def test_escalation_trigger_types(self) -> None:
        expected = {
            "IRREVERSIBLE_DESTRUCTIVE",
            "POLICY_AMBIGUITY",
            "UNKNOWN_SAFETY_RESULT",
            "PRIVILEGED_ACTION",
            "SENSITIVE_REASONING",
            "DISPUTED_AUTHORIZATION",
        }
        assert {t.value for t in EscalationTriggerType} == expected

    def test_reviewer_outcomes(self) -> None:
        expected = {"APPROVED", "DENIED", "MODIFIED", "ESCALATE_FURTHER", "DEFERRED"}
        assert {o.value for o in ReviewerOutcome} == expected

    def test_human_escalation_error_exception(self) -> None:
        assert issubclass(HumanEscalationError, Exception)


class TestHumanEscalationRecord:
    def _base_kwargs(self, **overrides) -> dict:
        defaults = dict(
            escalation_id="esc-1",
            run_id="r-1",
            trace_id="t-1",
            policy_hash="policy-abc",
            action_class="destructive",
            escalation_reason="User requested deletion",
            escalation_trigger_type=EscalationTriggerType.IRREVERSIBLE_DESTRUCTIVE,
            reviewer_queue_id="ops-queue",
        )
        defaults.update(overrides)
        return defaults

    def test_create_factory_hashes_reason(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.escalation_id == "esc-1"
        # Reason gets hashed to 16 hex chars
        assert len(rec.escalation_reason_hash) == 16
        assert rec.escalation_trigger_type == "IRREVERSIBLE_DESTRUCTIVE"

    def test_frozen(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        with pytest.raises(AttributeError):
            rec.run_id = "other"  # type: ignore[misc]

    def test_final_decision_hash_when_provided(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(final_decision="APPROVED with conditions"))
        assert rec.final_decision_hash is not None
        assert len(rec.final_decision_hash) == 16

    def test_final_decision_hash_none_when_absent(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.final_decision_hash is None

    def test_reviewer_outcome_string(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(reviewer_outcome=ReviewerOutcome.APPROVED))
        assert rec.reviewer_outcome == "APPROVED"

    def test_has_policy_designated_escalation(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.has_policy_designated_escalation() is True

    def test_has_policy_designated_false_when_no_policy(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(policy_hash=""))
        assert rec.has_policy_designated_escalation() is False

    def test_has_reviewer_queue_assignment(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.has_reviewer_queue_assignment() is True

    def test_has_reviewer_queue_false_when_empty(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(reviewer_queue_id=""))
        assert rec.has_reviewer_queue_assignment() is False

    def test_has_reviewer_outcome_initially_false(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.has_reviewer_outcome() is False

    def test_has_reviewer_outcome_true_after_set(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(reviewer_outcome=ReviewerOutcome.APPROVED))
        assert rec.has_reviewer_outcome() is True

    def test_is_blocking_when_no_outcome(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs())
        assert rec.is_blocking_automated_completion() is True

    def test_is_blocking_when_deferred(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(reviewer_outcome=ReviewerOutcome.DEFERRED))
        assert rec.is_blocking_automated_completion() is True

    def test_is_blocking_when_escalate_further(self) -> None:
        rec = HumanEscalationRecord.create(
            **self._base_kwargs(reviewer_outcome=ReviewerOutcome.ESCALATE_FURTHER)
        )
        assert rec.is_blocking_automated_completion() is True

    def test_is_not_blocking_when_approved(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(reviewer_outcome=ReviewerOutcome.APPROVED))
        assert rec.is_blocking_automated_completion() is False

    def test_has_explicit_override_requires_both(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(override_flag=True, final_decision="forced"))
        assert rec.has_explicit_override() is True

    def test_has_explicit_override_false_without_flag(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(override_flag=False, final_decision="x"))
        assert rec.has_explicit_override() is False

    def test_has_explicit_override_false_without_decision(self) -> None:
        rec = HumanEscalationRecord.create(**self._base_kwargs(override_flag=True))
        assert rec.has_explicit_override() is False


class TestHumanEscalationRegistry:
    def _make(
        self, esc_id: str = "e1", run_id: str = "r1", trace_id: str = "t1", queue_id: str = "q1"
    ) -> HumanEscalationRecord:
        return HumanEscalationRecord.create(
            escalation_id=esc_id,
            run_id=run_id,
            trace_id=trace_id,
            policy_hash="p",
            action_class="a",
            escalation_reason="reason",
            escalation_trigger_type=EscalationTriggerType.POLICY_AMBIGUITY,
            reviewer_queue_id=queue_id,
        )

    def test_singleton(self) -> None:
        r1 = get_human_escalation_registry()
        r2 = get_human_escalation_registry()
        assert r1 is r2

    def test_reset_creates_fresh_instance(self) -> None:
        r1 = get_human_escalation_registry()
        r1.persist_record(self._make())
        reset_human_escalation_registry()
        r2 = get_human_escalation_registry()
        assert r1 is not r2
        assert r2.get_record_count() == 0

    def test_query_by_escalation_id(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1"))
        assert reg.query_by_escalation_id("e1") is not None
        assert reg.query_by_escalation_id("nope") is None

    def test_query_by_run_id(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1", run_id="RUN"))
        reg.persist_record(self._make("e2", run_id="RUN"))
        reg.persist_record(self._make("e3", run_id="OTHER"))
        assert len(reg.query_by_run_id("RUN")) == 2
        assert len(reg.query_by_run_id("OTHER")) == 1
        assert reg.query_by_run_id("missing") == []

    def test_query_by_trace_id(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1", trace_id="T"))
        reg.persist_record(self._make("e2", trace_id="T"))
        assert len(reg.query_by_trace_id("T")) == 2
        assert reg.query_by_trace_id("missing") == []

    def test_query_by_queue_id(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1", queue_id="Q"))
        reg.persist_record(self._make("e2", queue_id="Q"))
        assert len(reg.query_by_queue_id("Q")) == 2

    def test_get_record_count_total(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1"))
        reg.persist_record(self._make("e2"))
        assert reg.get_record_count() == 2

    def test_get_record_count_by_outcome(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1"))
        # No outcomes yet
        assert reg.get_record_count(outcome=ReviewerOutcome.APPROVED) == 0

    def test_verify_policy_designated_for_known(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1"))
        assert reg.verify_policy_designated_escalation("e1") is True
        assert reg.verify_policy_designated_escalation("unknown") is False

    def test_update_reviewer_outcome_raises_for_unknown(self) -> None:
        reg = get_human_escalation_registry()
        with pytest.raises(HumanEscalationError, match="No escalation"):
            reg.update_reviewer_outcome(
                escalation_id="no-such",
                reviewer_id="r",
                reviewer_outcome=ReviewerOutcome.APPROVED,
            )

    def test_update_reviewer_outcome_persists(self) -> None:
        reg = get_human_escalation_registry()
        reg.persist_record(self._make("e1"))
        updated = reg.update_reviewer_outcome(
            escalation_id="e1",
            reviewer_id="alice",
            reviewer_outcome=ReviewerOutcome.APPROVED,
        )
        assert updated.reviewer_id == "alice"
        assert updated.reviewer_outcome == "APPROVED"
        # Record-by-id now returns the updated version
        latest = reg.query_by_escalation_id("e1")
        assert latest is not None
        assert latest.reviewer_outcome == "APPROVED"
