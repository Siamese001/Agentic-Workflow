"""Unit tests for agentic_core.L4_state.uwg.touch_state_writer.

Wave 3.2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 state surface.
``touch_state_writer`` (fan_in=10, L4_STATE) defines the apps_lic touch-state
UWG write request / receipt value objects + the write-class severity helper.
The ``TouchStateUWGAdapter`` requires a live DurableWriteGateway, so coverage
here targets the cleanly-constructible/pure surface: request validation
(ValueError paths), receipt shapes, defaults, frozen immutability, and the
write-class severity tuple.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from agentic_core.L4_state.uwg.touch_state_writer import (
    TOUCH_STATE_SEVERITY,
    TOUCH_STATE_WRITE_CLASS,
    TouchStateBlockedReceipt,
    TouchStateCommitReceipt,
    TouchStateWriteRequest,
    get_touch_state_write_class_severity,
)
from agentic_core.L4_state.uwg.write_class_severity import WriteClassSeverity


def _request(**kw: object) -> TouchStateWriteRequest:
    base = dict(
        touch_id="touch-1", recipient_hash="hash-abc", campaign_id="camp-1",
        touch_sequence=1, touch_state="scheduled",
    )
    base.update(kw)
    return TouchStateWriteRequest(**base)  # type: ignore[arg-type]


class TestTouchStateWriteRequest:
    def test_construction_and_defaults(self) -> None:
        r = _request()
        assert r.next_scheduled_wake is None
        assert r.context_carry_forward == {}
        assert r.trigger_signal is None
        assert r.trigger_confidence == 0.0
        assert r.hitl_review_required is False
        assert r.metadata == {}

    @pytest.mark.parametrize(
        "state",
        ["scheduled", "sent", "replied", "bounced", "converted", "expired", "cancelled"],
    )
    def test_all_valid_states_accepted(self, state: str) -> None:
        assert _request(touch_state=state).touch_state == state

    def test_invalid_state_raises(self) -> None:
        with pytest.raises(ValueError):
            _request(touch_state="pending")

    @pytest.mark.parametrize("conf", [-0.01, 1.01, 2.0, -1.0])
    def test_trigger_confidence_out_of_range_raises(self, conf: float) -> None:
        with pytest.raises(ValueError):
            _request(trigger_confidence=conf)

    @pytest.mark.parametrize("conf", [0.0, 0.5, 1.0])
    def test_trigger_confidence_boundaries_accepted(self, conf: float) -> None:
        assert _request(trigger_confidence=conf).trigger_confidence == conf

    def test_distinct_dict_instances_per_request(self) -> None:
        r1 = _request()
        r2 = _request()
        assert r1.context_carry_forward is not r2.context_carry_forward

    def test_frozen(self) -> None:
        r = _request()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.touch_state = "sent"  # type: ignore[misc]


class TestReceipts:
    def test_commit_receipt_fields(self) -> None:
        now = datetime.now(timezone.utc)
        rec = TouchStateCommitReceipt(
            touch_id="touch-1", commit_timestamp=now,
            bundle_digest="digest", state_diff_applied=True,
        )
        assert rec.touch_id == "touch-1"
        assert rec.state_diff_applied is True

    def test_commit_receipt_frozen(self) -> None:
        rec = TouchStateCommitReceipt(
            touch_id="t", commit_timestamp=datetime.now(timezone.utc),
            bundle_digest="d", state_diff_applied=True,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.bundle_digest = "x"  # type: ignore[misc]

    def test_blocked_receipt_defaults(self) -> None:
        rec = TouchStateBlockedReceipt(
            touch_id="t", blocked_reason="locked",
            blocked_at=datetime.now(timezone.utc),
        )
        assert rec.resolution_hint is None

    def test_blocked_receipt_with_hint(self) -> None:
        rec = TouchStateBlockedReceipt(
            touch_id="t", blocked_reason="locked",
            blocked_at=datetime.now(timezone.utc), resolution_hint="retry",
        )
        assert rec.resolution_hint == "retry"


class TestWriteClassSeverity:
    def test_severity_is_durable(self) -> None:
        assert TOUCH_STATE_SEVERITY == WriteClassSeverity.DURABLE

    def test_write_class_constant(self) -> None:
        assert TOUCH_STATE_WRITE_CLASS == "apps_lic.touch_state"

    def test_helper_returns_class_and_severity(self) -> None:
        write_class, severity = get_touch_state_write_class_severity()
        assert write_class == TOUCH_STATE_WRITE_CLASS
        assert severity == TOUCH_STATE_SEVERITY
