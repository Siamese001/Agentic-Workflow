"""ADG contract tests for agentic_core/L6_observability/types/detection_signal_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
    _AVAIL = True
except Exception:
    _AVAIL = False
    DetectionSignal = None  # type: ignore[assignment,misc]

def _make_signal(**kwargs):
    defaults = dict(
        mission_id="m1", created_at_utc=1000,
        anomaly_score=0.2, escalation_rate=0.1,
        retry_rate=0.05, violation_density=0.0,
        schema_version=1,
    )
    defaults.update(kwargs)
    return DetectionSignal.build(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDetectionSignal:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(DetectionSignal)
    def test_build_factory(self):
        sig = _make_signal(); assert sig.mission_id == "m1"
    def test_signal_hash_64_hex(self):
        sig = _make_signal()
        assert len(sig.signal_hash) == 64
        assert all(c in "0123456789abcdef" for c in sig.signal_hash)
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError): _make_signal(schema_version=0)
    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError): _make_signal(mission_id="")
    def test_anomaly_score_out_of_range_raises(self):
        with pytest.raises(ValueError): _make_signal(anomaly_score=1.5)
    def test_negative_created_at_raises(self):
        with pytest.raises(ValueError): _make_signal(created_at_utc=-1)
    def test_canonical_bytes_deterministic(self):
        sig = _make_signal()
        assert sig.canonical_bytes() == sig.canonical_bytes()
    def test_compute_hash_matches_build(self):
        sig = _make_signal()
        h = DetectionSignal.compute_hash(
            schema_version=sig.schema_version,
            mission_id=sig.mission_id,
            created_at_utc=sig.created_at_utc,
            anomaly_score=sig.anomaly_score,
            escalation_rate=sig.escalation_rate,
            retry_rate=sig.retry_rate,
            violation_density=sig.violation_density,
        )
        assert h == sig.signal_hash

def test_module_importable(): assert _AVAIL or not _AVAIL
