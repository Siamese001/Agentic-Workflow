"""Unit tests for :mod:`system_learning.engines.eval_gated_l4_writer`."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.eval_freshness_gate import (
    EvalFreshnessGate,
    EvalFreshnessViolation,
)
from agentic_core.L6_system_learning.eval_gated_l4_writer import (
    EvalGatedL4StateWriter,
)


class _RecordingWriter:
    """Minimal stand-in matching the 5 L4 Protocol methods we wrap."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def _record(self, bucket: str, **kwargs) -> str:
        self.calls.append((bucket, kwargs))
        return f"v-{bucket}"

    def write_l4a_detection_signal(self, **kwargs) -> str:
        return self._record("l4a_detection_signal", **kwargs)

    def write_l4b_healing_snapshot(self, **kwargs) -> str:
        return self._record("l4b_healing_snapshot", **kwargs)

    def write_l4c_shadow_drift(self, **kwargs) -> str:
        return self._record("l4c_shadow_drift", **kwargs)

    def write_l4c_policy_recommendation(self, **kwargs) -> str:
        return self._record("l4c_policy_recommendation", **kwargs)

    def write_l4c_retrieval_profile_proposal(self, **kwargs) -> str:
        return self._record("l4c_retrieval_profile_proposal", **kwargs)


def _gate(ttl: dict[str, float | None]) -> EvalFreshnessGate:
    return EvalFreshnessGate.from_mapping(
        {
            "version": 1,
            "schema": "test",
            "ttl_seconds": ttl,
            "default_on_unknown_class": "block",
            "fail_open": False,
        }
    )


def test_fresh_write_delegates_to_inner() -> None:
    inner = _RecordingWriter()
    gate = _gate({"policy": 3600.0})
    writer = EvalGatedL4StateWriter(inner=inner, gate=gate)

    version = writer.write_l4c_policy_recommendation(
        payload_bytes=b"x",
        component_name="component",
        created_utc=1500,
        eval_record_timestamp=1000,
    )
    assert version == "v-l4c_policy_recommendation"
    assert len(inner.calls) == 1
    assert inner.calls[0][0] == "l4c_policy_recommendation"
    check = writer.last_check()
    assert check is not None
    assert check.decision.blocked is False


def test_stale_write_raises_and_inner_untouched() -> None:
    inner = _RecordingWriter()
    gate = _gate({"policy": 10.0})
    writer = EvalGatedL4StateWriter(inner=inner, gate=gate)

    with pytest.raises(EvalFreshnessViolation, match="exceeds TTL"):
        writer.write_l4c_policy_recommendation(
            payload_bytes=b"x",
            component_name="component",
            created_utc=5000,
            eval_record_timestamp=100,
        )
    assert inner.calls == []  # stale write must not reach the inner writer
    assert writer.last_check() is not None
    assert writer.last_check().decision.blocked is True


def test_missing_eval_record_blocks_when_ttl_required() -> None:
    inner = _RecordingWriter()
    gate = _gate({"policy": 3600.0})
    writer = EvalGatedL4StateWriter(inner=inner, gate=gate)

    with pytest.raises(EvalFreshnessViolation):
        writer.write_l4c_policy_recommendation(
            payload_bytes=b"x",
            component_name="component",
            created_utc=1000,
        )
    assert inner.calls == []


def test_null_ttl_bucket_passes_without_eval() -> None:
    inner = _RecordingWriter()
    gate = _gate({"baseline": None})
    writer = EvalGatedL4StateWriter(inner=inner, gate=gate)

    version = writer.write_l4a_detection_signal(
        payload_bytes=b"x",
        component_name="c",
        created_utc=1000,
    )
    assert version == "v-l4a_detection_signal"
    assert len(inner.calls) == 1


def test_custom_mapping_is_honored() -> None:
    inner = _RecordingWriter()
    gate = _gate({"custom_prompt_class": 3600.0})
    writer = EvalGatedL4StateWriter(
        inner=inner,
        gate=gate,
        change_class_for_bucket=lambda _b: "custom_prompt_class",
    )
    # Fresh — should pass
    writer.write_l4a_detection_signal(
        payload_bytes=b"x",
        component_name="c",
        created_utc=1500,
        eval_record_timestamp=1000,
    )
    assert writer.last_check().change_class == "custom_prompt_class"


def test_all_five_write_methods_gate() -> None:
    inner = _RecordingWriter()
    # Map every bucket to a single class so one stale eval blocks all of them.
    gate = _gate({"baseline": 10.0, "policy": 10.0, "retrieval_profile": 10.0})
    writer = EvalGatedL4StateWriter(inner=inner, gate=gate)
    for method in (
        writer.write_l4a_detection_signal,
        writer.write_l4b_healing_snapshot,
        writer.write_l4c_shadow_drift,
        writer.write_l4c_policy_recommendation,
        writer.write_l4c_retrieval_profile_proposal,
    ):
        with pytest.raises(EvalFreshnessViolation):
            method(
                payload_bytes=b"x",
                component_name="c",
                created_utc=5000,
                eval_record_timestamp=100,
            )
    assert inner.calls == []


def test_eval_timestamp_callback_override() -> None:
    inner = _RecordingWriter()
    gate = _gate({"baseline": 3600.0})
    writer = EvalGatedL4StateWriter(
        inner=inner,
        gate=gate,
        eval_record_timestamp_for_bucket=lambda bucket: 1000.0,
    )
    # No per-call eval_record_timestamp supplied — callback fills it in.
    version = writer.write_l4a_detection_signal(payload_bytes=b"x", component_name="c", created_utc=1500)
    assert version == "v-l4a_detection_signal"
