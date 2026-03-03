"""
Phase 3 — Wave 1 Tests: DetectionSignal model + emission hook.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal,
    emit_signal_from_gateway_result,
)
from agentic_core.L6_observability.types.detection_signal import DetectionSignal

pytestmark = pytest.mark.unit_min_deps


class TestDetectionSignalModel:
    def test_build_produces_valid_signal(self):
        sig = DetectionSignal.build(
            mission_id="m-001",
            created_at_utc=1_700_000_000,
            anomaly_score=0.3,
            escalation_rate=0.1,
            retry_rate=0.2,
            violation_density=0.05,
        )
        assert sig.schema_version == 1
        assert sig.mission_id == "m-001"
        assert sig.anomaly_score == 0.3
        assert len(sig.signal_hash) == 64

    def test_detection_signal_hash_stable(self):
        """Same inputs must produce identical signal_hash across calls."""
        kwargs = {
            "mission_id": "m-stable",
            "created_at_utc": 1_700_000_001,
            "anomaly_score": 0.5,
            "escalation_rate": 0.2,
            "retry_rate": 0.1,
            "violation_density": 0.0,
        }
        sig1 = DetectionSignal.build(**kwargs)
        sig2 = DetectionSignal.build(**kwargs)
        assert sig1.signal_hash == sig2.signal_hash

    def test_different_inputs_produce_different_hash(self):
        sig1 = DetectionSignal.build(
            mission_id="m-a",
            created_at_utc=100,
            anomaly_score=0.1,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        sig2 = DetectionSignal.build(
            mission_id="m-b",
            created_at_utc=100,
            anomaly_score=0.1,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig1.signal_hash != sig2.signal_hash

    def test_canonical_bytes_is_deterministic(self):
        sig = DetectionSignal.build(
            mission_id="m-canon",
            created_at_utc=200,
            anomaly_score=0.0,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig.canonical_bytes() == sig.canonical_bytes()

    def test_canonical_bytes_excludes_signal_hash(self):
        """signal_hash must not appear in canonical_bytes (no circular dependency)."""
        sig = DetectionSignal.build(
            mission_id="m-excl",
            created_at_utc=300,
            anomaly_score=0.2,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig.signal_hash.encode() not in sig.canonical_bytes()
        assert b"signal_hash" not in sig.canonical_bytes()


class TestDetectionSignalValidation:
    def test_detection_signal_rejects_out_of_range_anomaly_score(self):
        with pytest.raises(ValueError, match="anomaly_score"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=1.5,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_negative_escalation_rate(self):
        with pytest.raises(ValueError, match="escalation_rate"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=-0.1,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_out_of_range_values(self):
        for field_name, kwargs in [
            ("retry_rate", {"retry_rate": 2.0}),
            ("violation_density", {"violation_density": -1.0}),
        ]:
            base = {
                "mission_id": "m",
                "created_at_utc": 1,
                "anomaly_score": 0.0,
                "escalation_rate": 0.0,
                "retry_rate": 0.0,
                "violation_density": 0.0,
            }
            base.update(kwargs)
            with pytest.raises(ValueError, match=field_name):
                DetectionSignal.build(**base)

    def test_detection_signal_rejects_empty_mission_id(self):
        with pytest.raises(ValueError, match="mission_id"):
            DetectionSignal.build(
                mission_id="",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_bad_schema_version(self):
        with pytest.raises(ValueError, match="schema_version"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
                schema_version=0,
            )


class TestEmissionHook:
    def test_emit_detection_signal_returns_valid_signal(self):
        sig = emit_detection_signal(
            mission_id="emit-001",
            created_at_utc=1_700_000_100,
            anomaly_score=0.4,
        )
        assert isinstance(sig, DetectionSignal)
        assert sig.mission_id == "emit-001"
        assert sig.anomaly_score == 0.4

    def test_emission_is_side_effect_free_on_result(self):
        """
        Emitting a signal from a GatewayResult must not modify the result.
        The returned signal is a new object; gateway_result is unchanged.
        """

        class FakeResult:
            success = True
            error = None
            healing_output = {"errors": 0}

        result = FakeResult()
        original_success = result.success
        original_error = result.error

        sig = emit_signal_from_gateway_result(
            mission_id="side-effect-test",
            created_at_utc=1_700_000_200,
            gateway_result=result,
        )

        assert isinstance(sig, DetectionSignal)
        assert result.success == original_success
        assert result.error == original_error

    def test_emit_from_failed_result_raises_anomaly_score(self):
        class FakeFailedResult:
            success = False
            error = "heal failed"

        sig = emit_signal_from_gateway_result(
            mission_id="fail-test",
            created_at_utc=1_700_000_300,
            gateway_result=FakeFailedResult(),
        )
        assert sig.anomaly_score > 0.0

    def test_emit_from_success_result_has_zero_anomaly(self):
        class FakeSuccessResult:
            success = True
            error = None

        sig = emit_signal_from_gateway_result(
            mission_id="success-test",
            created_at_utc=1_700_000_400,
            gateway_result=FakeSuccessResult(),
        )
        assert sig.anomaly_score == 0.0
