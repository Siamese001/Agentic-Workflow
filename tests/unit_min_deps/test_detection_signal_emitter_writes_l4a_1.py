"""Tests for Detection Signal Emitter L4A writes - Phase 7 functionality.

Tests that detection signals are written to L4A state when writer is provided.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal_with_l4a,
)
from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal


class FakeL4StateWriter:
    """Fake L4 state writer that captures writes."""

    def __init__(self) -> None:
        self.l4a_writes: list[dict] = []

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Capture L4A detection signal writes."""
        self.l4a_writes.append(
            {"payload_bytes": payload_bytes, "component_name": component_name, "created_utc": created_utc}
        )
        # Return a fake version ID
        return f"fake_version_{len(self.l4a_writes)}"

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Not used in this test."""
        return "noop_l4b"


class TestDetectionSignalEmitterWritesL4A:
    """Test suite for detection signal L4A writing."""

    def test_emit_with_l4a_writer_calls_write_exactly_once(self):
        """Test that providing L4A writer results in exactly one write call."""
        fake_writer = FakeL4StateWriter()

        mission_id = "test_mission_123"
        created_at_utc = 1000
        anomaly_score = 0.5
        escalation_rate = 0.2
        retry_rate = 0.1
        violation_density = 0.3

        # Emit signal with L4A writer
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            l4a_writer=fake_writer,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
            schema_version=1,
        )

        # Verify signal was created correctly
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id
        assert signal.created_at_utc == created_at_utc
        assert signal.anomaly_score == anomaly_score
        assert signal.escalation_rate == escalation_rate
        assert signal.retry_rate == retry_rate
        assert signal.violation_density == violation_density
        assert signal.schema_version == 1

        # Verify L4A writer was called exactly once
        assert len(fake_writer.l4a_writes) == 1

        # Verify write parameters
        write = fake_writer.l4a_writes[0]
        assert write["component_name"] == "detection_signal_emitter"
        assert write["created_utc"] == created_at_utc

        # Verify payload bytes contain the serialized signal
        payload_bytes = write["payload_bytes"]
        assert isinstance(payload_bytes, bytes)
        # Should contain the mission_id in serialized form
        assert mission_id.encode() in payload_bytes

    def test_emit_without_l4a_writer_no_write_calls(self):
        """Test that not providing L4A writer results in no write calls."""
        fake_writer = FakeL4StateWriter()

        mission_id = "test_mission_456"
        created_at_utc = 2000

        # Emit signal without L4A writer
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            l4a_writer=None,  # No writer provided
        )

        # Verify signal was still created
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id

        # Verify no L4A writes occurred
        assert len(fake_writer.l4a_writes) == 0

    def test_emit_with_l4a_writer_deterministic_bytes(self):
        """Test that L4A writes use deterministic bytes."""
        fake_writer = FakeL4StateWriter()

        # Emit same signal twice
        mission_id = "deterministic_test"
        created_at_utc = 3000

        signal1 = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=fake_writer
        )

        signal2 = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=fake_writer
        )

        # Should have two writes
        assert len(fake_writer.l4a_writes) == 2

        # Payload bytes should be identical for same signal
        payload1 = fake_writer.l4a_writes[0]["payload_bytes"]
        payload2 = fake_writer.l4a_writes[1]["payload_bytes"]
        assert payload1 == payload2

        # Signals should also be identical
        assert signal1.canonical_bytes() == signal2.canonical_bytes()

    def test_emit_with_l4a_writer_handles_write_failure_gracefully(self):
        """Test that L4A write failures don't break signal emission."""

        class FailingL4StateWriter:
            """L4A writer that always fails."""

            def write_l4a_detection_signal(self, **kwargs) -> str:
                raise RuntimeError("Simulated write failure")

        failing_writer = FailingL4StateWriter()

        mission_id = "test_mission_failure"
        created_at_utc = 4000

        # Should not raise exception even if L4A write fails
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=failing_writer
        )

        # Signal should still be created successfully
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id

    def test_emit_with_l4a_writer_different_signals_different_bytes(self):
        """Test that different signals produce different payload bytes."""
        fake_writer = FakeL4StateWriter()

        # Emit two different signals
        signal1 = emit_detection_signal_with_l4a(
            mission_id="signal_1", created_at_utc=5000, anomaly_score=0.1, l4a_writer=fake_writer
        )

        signal2 = emit_detection_signal_with_l4a(
            mission_id="signal_2", created_at_utc=5000, anomaly_score=0.9, l4a_writer=fake_writer
        )

        # Should have two writes
        assert len(fake_writer.l4a_writes) == 2

        # Payload bytes should be different
        payload1 = fake_writer.l4a_writes[0]["payload_bytes"]
        payload2 = fake_writer.l4a_writes[1]["payload_bytes"]
        assert payload1 != payload2

        # Signals should also be different
        assert signal1.canonical_bytes() != signal2.canonical_bytes()
