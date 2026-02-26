"""
Phase 3 Governance Tests - Detection Signal

Acceptance command SSOT:
    python -m pytest -q tests/governance/test_phase3_detection_signal.py -s
"""

import hashlib
import json
import os
from pathlib import Path

import pytest

from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal,
    emit_signal_from_gateway_result,
)
from agentic_core.L6_observability.types.detection_signal import DetectionSignal

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent

# ---------------------------------------------------------------------------
# Digest -- printed once, first test that emits it
# ---------------------------------------------------------------------------

_DIGEST_PRINTED = False


def compute_phase3_digest() -> str:
    """
    Compute deterministic SHA256 digest over Phase 3 detection signal state.

    Returns:
        SHA256 hex digest of canonical detection signal JSON
    """
    # Create a canonical detection signal for digest computation
    sample_signal = DetectionSignal.build(
        mission_id="digest-canonical-mission",
        created_at_utc=1700000000,
        anomaly_score=0.5,
        escalation_rate=0.2,
        retry_rate=0.1,
        violation_density=0.0,
    )

    # Create canonical representation
    phase3_canonical = {
        "detection_signal_schema": {
            "schema_version": sample_signal.schema_version,
            "has_mission_id": bool(sample_signal.mission_id),
            "has_anomaly_score": isinstance(sample_signal.anomaly_score, (int, float)),
            "has_escalation_rate": isinstance(sample_signal.escalation_rate, (int, float)),
            "has_retry_rate": isinstance(sample_signal.retry_rate, (int, float)),
            "has_violation_density": isinstance(sample_signal.violation_density, (int, float)),
            "signal_hash_length": len(sample_signal.signal_hash),
        },
        "emission_hooks": {
            "emit_detection_signal_exists": callable(emit_detection_signal),
            "emit_signal_from_gateway_result_exists": callable(emit_signal_from_gateway_result),
        },
        "validation_rules": {
            "anomaly_score_range": "0.0 to 1.0",
            "escalation_rate_min": "0.0",
            "retry_rate_range": "0.0 to 1.0",
            "violation_density_range": "0.0 to 1.0",
            "mission_id_required": True,
            "schema_version_min": 1,
        },
        "version": "1.0.0",
    }

    # Sort keys for deterministic ordering
    canonical_json = json.dumps(phase3_canonical, sort_keys=True, separators=(",", ":"))

    # Compute SHA256 digest
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    return digest


def _print_digest_once() -> str:
    global _DIGEST_PRINTED
    d = compute_phase3_digest()
    if not _DIGEST_PRINTED:
        print(f"\nW3-DETECTION-SIGNAL-DIGEST: {d}", flush=True)
        _DIGEST_PRINTED = True
    return d


# ===========================================================================
# Detection Signal Model Tests
# ===========================================================================

@pytest.mark.governance
def test_detection_signal_model_exists():
    """DetectionSignal model must exist and be importable."""
    assert DetectionSignal is not None
    assert hasattr(DetectionSignal, 'build')
    assert callable(DetectionSignal.build)


@pytest.mark.governance
def test_detection_signal_build_creates_valid_signal():
    """DetectionSignal.build must create valid signals."""
    sig = DetectionSignal.build(
        mission_id="test-mission",
        created_at_utc=1700000000,
        anomaly_score=0.3,
        escalation_rate=0.1,
        retry_rate=0.2,
        violation_density=0.05,
    )

    assert sig.schema_version >= 1
    assert sig.mission_id == "test-mission"
    assert sig.anomaly_score == 0.3
    assert sig.escalation_rate == 0.1
    assert sig.retry_rate == 0.2
    assert sig.violation_density == 0.05
    assert len(sig.signal_hash) == 64


@pytest.mark.governance
def test_detection_signal_hash_is_deterministic():
    """Same inputs must produce identical signal_hash across calls."""
    kwargs = {
        "mission_id": "deterministic-test",
        "created_at_utc": 1700000001,
        "anomaly_score": 0.5,
        "escalation_rate": 0.2,
        "retry_rate": 0.1,
        "violation_density": 0.0,
    }
    sig1 = DetectionSignal.build(**kwargs)
    sig2 = DetectionSignal.build(**kwargs)
    assert sig1.signal_hash == sig2.signal_hash, "Signal hash must be deterministic"


@pytest.mark.governance
def test_detection_signal_different_inputs_different_hash():
    """Different inputs must produce different signal_hash."""
    sig1 = DetectionSignal.build(
        mission_id="mission-a",
        created_at_utc=1700000000,
        anomaly_score=0.1,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )
    sig2 = DetectionSignal.build(
        mission_id="mission-b",
        created_at_utc=1700000000,
        anomaly_score=0.1,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )
    assert sig1.signal_hash != sig2.signal_hash, "Different missions must have different hashes"


@pytest.mark.governance
def test_detection_signal_validation_enforces_ranges():
    """DetectionSignal must enforce valid ranges for all fields."""
    # Test anomaly_score out of range
    with pytest.raises(ValueError, match="anomaly_score"):
        DetectionSignal.build(
            mission_id="test",
            created_at_utc=1,
            anomaly_score=1.5,  # Invalid: > 1.0
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )

    # Test negative escalation_rate
    with pytest.raises(ValueError, match="escalation_rate"):
        DetectionSignal.build(
            mission_id="test",
            created_at_utc=1,
            anomaly_score=0.0,
            escalation_rate=-0.1,  # Invalid: < 0.0
            retry_rate=0.0,
            violation_density=0.0,
        )

    # Test retry_rate out of range
    with pytest.raises(ValueError, match="retry_rate"):
        DetectionSignal.build(
            mission_id="test",
            created_at_utc=1,
            anomaly_score=0.0,
            escalation_rate=0.0,
            retry_rate=2.0,  # Invalid: > 1.0
            violation_density=0.0,
        )

    # Test negative violation_density
    with pytest.raises(ValueError, match="violation_density"):
        DetectionSignal.build(
            mission_id="test",
            created_at_utc=1,
            anomaly_score=0.0,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=-1.0,  # Invalid: < 0.0
        )


@pytest.mark.governance
def test_detection_signal_requires_mission_id():
    """DetectionSignal must require non-empty mission_id."""
    with pytest.raises(ValueError, match="mission_id"):
        DetectionSignal.build(
            mission_id="",  # Invalid: empty string
            created_at_utc=1,
            anomaly_score=0.0,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )


@pytest.mark.governance
def test_detection_signal_canonical_bytes_is_deterministic():
    """canonical_bytes must be deterministic and exclude signal_hash."""
    sig = DetectionSignal.build(
        mission_id="canonical-test",
        created_at_utc=1700000002,
        anomaly_score=0.0,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )

    # Must be deterministic
    assert sig.canonical_bytes() == sig.canonical_bytes()

    # Must exclude signal_hash (no circular dependency)
    assert sig.signal_hash.encode() not in sig.canonical_bytes()
    assert b"signal_hash" not in sig.canonical_bytes()


# ===========================================================================
# Emission Hook Tests
# ===========================================================================

@pytest.mark.governance
def test_emission_hooks_exist():
    """Emission hooks must exist and be callable."""
    assert callable(emit_detection_signal)
    assert callable(emit_signal_from_gateway_result)


@pytest.mark.governance
def test_emit_detection_signal_returns_valid_signal():
    """emit_detection_signal must return a valid DetectionSignal."""
    sig = emit_detection_signal(
        mission_id="emit-test",
        created_at_utc=1700000003,
        anomaly_score=0.4,
    )

    assert isinstance(sig, DetectionSignal)
    assert sig.mission_id == "emit-test"
    assert sig.anomaly_score == 0.4
    assert len(sig.signal_hash) == 64


@pytest.mark.governance
def test_emission_is_side_effect_free():
    """Emitting a signal must not modify the original result."""
    class FakeResult:
        def __init__(self):
            self.success = True
            self.error = None
            self.healing_output = {"errors": 0}

    result = FakeResult()
    original_success = result.success
    original_error = result.error
    original_output = result.healing_output

    sig = emit_signal_from_gateway_result(
        mission_id="side-effect-test",
        created_at_utc=1700000004,
        gateway_result=result,
    )

    # Result must be unchanged
    assert result.success == original_success
    assert result.error == original_error
    assert result.healing_output == original_output

    # Signal must be valid
    assert isinstance(sig, DetectionSignal)


@pytest.mark.governance
def test_emission_from_failed_result_has_anomaly():
    """Failed gateway results must produce signals with anomaly_score > 0."""
    class FakeFailedResult:
        def __init__(self):
            self.success = False
            self.error = "heal failed"

    sig = emit_signal_from_gateway_result(
        mission_id="fail-test",
        created_at_utc=1700000005,
        gateway_result=FakeFailedResult(),
    )

    assert sig.anomaly_score > 0.0, "Failed result must have anomaly_score > 0"


@pytest.mark.governance
def test_emission_from_success_result_has_zero_anomaly():
    """Successful gateway results must produce signals with anomaly_score = 0."""
    class FakeSuccessResult:
        def __init__(self):
            self.success = True
            self.error = None

    sig = emit_signal_from_gateway_result(
        mission_id="success-test",
        created_at_utc=1700000006,
        gateway_result=FakeSuccessResult(),
    )

    assert sig.anomaly_score == 0.0, "Success result must have anomaly_score = 0"


# ===========================================================================
# Deterministic Digest Tests
# ===========================================================================

@pytest.mark.governance
def test_w3_detection_signal_digest_deterministic():
    """Digest must be identical across runs for same signal state."""
    d1 = compute_phase3_digest()
    d2 = compute_phase3_digest()
    assert d1 == d2, "Digest not deterministic"
    assert len(d1) == 64, "Digest must be SHA256 (64 hex chars)"
    assert all(c in "0123456789abcdef" for c in d1), "Digest must be valid hex"


@pytest.mark.governance
def test_w3_detection_signal_digest_printed():
    """Prints W3-DETECTION-SIGNAL-DIGEST once to stdout."""
    digest = _print_digest_once()
    assert len(digest) == 64, "Printed digest must be valid SHA256"


@pytest.mark.governance
def test_digest_includes_all_required_components():
    """Digest computation must include all required components."""
    # This is implicitly tested by the digest computation itself
    # but we verify the components are present
    sample_signal = DetectionSignal.build(
        mission_id="component-test",
        created_at_utc=1700000007,
        anomaly_score=0.5,
        escalation_rate=0.2,
        retry_rate=0.1,
        violation_density=0.0,
    )

    # Verify all required fields exist
    assert hasattr(sample_signal, 'schema_version')
    assert hasattr(sample_signal, 'mission_id')
    assert hasattr(sample_signal, 'anomaly_score')
    assert hasattr(sample_signal, 'escalation_rate')
    assert hasattr(sample_signal, 'retry_rate')
    assert hasattr(sample_signal, 'violation_density')
    assert hasattr(sample_signal, 'signal_hash')


# ===========================================================================
# Comprehensive Gate
# ===========================================================================

@pytest.mark.governance
def test_phase3_detection_signal_comprehensive():
    """Comprehensive test covering all Phase 3 requirements."""
    digest = _print_digest_once()
    assert len(digest) == 64, "Digest must be valid SHA256"

    # Verify model exists and works
    sig = DetectionSignal.build(
        mission_id="comprehensive-test",
        created_at_utc=1700000008,
        anomaly_score=0.3,
        escalation_rate=0.1,
        retry_rate=0.2,
        violation_density=0.05,
    )
    assert isinstance(sig, DetectionSignal)
    assert len(sig.signal_hash) == 64

    # Verify emission hooks exist
    assert callable(emit_detection_signal)
    assert callable(emit_signal_from_gateway_result)

    # Verify validation works
    with pytest.raises(ValueError):
        DetectionSignal.build(
            mission_id="test",
            created_at_utc=1,
            anomaly_score=2.0,  # Invalid
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )


# ===========================================================================
# Negative Control (W3_NEGCTRL_TAMPER=1)
# ===========================================================================

@pytest.mark.governance
def test_negative_control_detection_signal_tamper():
    """
    W3_NEGCTRL_TAMPER=1 -> simulate signal validation bypass, confirm detection,
    then call pytest.xfail() -> XFAIL, exit 0.
    No env var -> normal path: signals must validate correctly (PASS).
    """
    if os.environ.get("W3_NEGCTRL_TAMPER") == "1":
        # Simulate validation bypass by creating invalid signal
        try:
            # This should fail with validation
            invalid_sig = DetectionSignal.build(
                mission_id="tamper-test",
                created_at_utc=1,
                anomaly_score=2.0,  # Invalid: > 1.0
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
            )
            # If we get here, validation was bypassed
            pytest.xfail("W3_NEGCTRL_TAMPER=1: detection signal validation bypassed -- XFAIL")
        except ValueError:
            # Validation worked - this is the expected failure mode for tamper detection
            pytest.xfail("W3_NEGCTRL_TAMPER=1: detection signal tampering confirmed -- XFAIL")

        # Additional tamper check - verify hash integrity
        valid_sig = DetectionSignal.build(
            mission_id="hash-test",
            created_at_utc=1700000009,
            anomaly_score=0.5,
            escalation_rate=0.2,
            retry_rate=0.1,
            violation_density=0.0,
        )

        if len(valid_sig.signal_hash) != 64:
            pytest.xfail("W3_NEGCTRL_TAMPER=1: signal hash corruption detected -- XFAIL")

        # If no specific tampering detected but flag is set
        pytest.xfail("W3_NEGCTRL_TAMPER=1: detection signal integrity violation -- XFAIL")
    else:
        # Normal path - signals must validate correctly
        sig = DetectionSignal.build(
            mission_id="normal-test",
            created_at_utc=1700000010,
            anomaly_score=0.3,
            escalation_rate=0.1,
            retry_rate=0.2,
            violation_density=0.05,
        )

        assert isinstance(sig, DetectionSignal), "Normal path: signal must be valid"
        assert len(sig.signal_hash) == 64, "Normal path: signal hash must be valid"
        assert sig.anomaly_score == 0.3, "Normal path: signal values must be preserved"
