"""
Resource predictor engine for L2 execution learning.
Deterministic resource envelope prediction from failure signatures.
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.L2_execution.types.resource_prediction_types import (
    FailureSignature,
    ResourceEnvelope,
    ResourcePrediction,
)


class ResourcePredictor(Protocol):
    """Protocol for resource prediction engines."""

    def predict(
        *,
        signature: FailureSignature,
        history_bytes: bytes | None = None,
    ) -> ResourcePrediction:
        """Predict resource envelope for a failure signature."""
        ...


class DefaultDeterministicResourcePredictor:
    """Deterministic resource predictor with bounded outputs."""

    # Configuration bounds
    MIN_CPU_CORES: int = 1
    MAX_CPU_CORES: int = 16
    MIN_MEMORY_MB: int = 512
    MAX_MEMORY_MB: int = 16384
    MIN_TIMEOUT_S: int = 30
    MAX_TIMEOUT_S: int = 3600

    # Deterministic baseline envelopes by failure type
    _BASELINE_ENVELOPES: dict[str, ResourceEnvelope] = {
        "timeout": ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300),
        "memory_error": ResourceEnvelope(cpu_cores=1, memory_mb=2048, timeout_s=180),
        "cpu_error": ResourceEnvelope(cpu_cores=4, memory_mb=512, timeout_s=240),
        "io_error": ResourceEnvelope(cpu_cores=2, memory_mb=1536, timeout_s=600),
        "network_error": ResourceEnvelope(cpu_cores=1, memory_mb=768, timeout_s=120),
        "unknown": ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300),
    }

    def __init__(
        self,
        min_cpu_cores: int = MIN_CPU_CORES,
        max_cpu_cores: int = MAX_CPU_CORES,
        min_memory_mb: int = MIN_MEMORY_MB,
        max_memory_mb: int = MAX_MEMORY_MB,
        min_timeout_s: int = MIN_TIMEOUT_S,
        max_timeout_s: int = MAX_TIMEOUT_S,
    ):
        """Initialize with configurable bounds."""
        self.min_cpu_cores = min_cpu_cores
        self.max_cpu_cores = max_cpu_cores
        self.min_memory_mb = min_memory_mb
        self.max_memory_mb = max_memory_mb
        self.min_timeout_s = min_timeout_s
        self.max_timeout_s = max_timeout_s

    def predict(
        self,
        *,
        signature: FailureSignature,
        history_bytes: bytes | None = None,
    ) -> ResourcePrediction:
        """Predict resource envelope deterministically."""
        # Get baseline envelope for failure type
        baseline = self._BASELINE_ENVELOPES.get(signature.failure_type, self._BASELINE_ENVELOPES["unknown"])

        # Apply history-based adjustments if available
        envelope = self._apply_history_adjustments(baseline, signature, history_bytes)

        # Clamp to configured bounds
        envelope = self._clamp_envelope(envelope)

        # Generate deterministic confidence and reasons
        confidence, reasons = self._generate_confidence_and_reasons(signature, envelope, history_bytes)

        return ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=confidence,
            reasons=tuple(sorted(reasons)),  # Sort for determinism
        )

    def _apply_history_adjustments(
        self,
        baseline: ResourceEnvelope,
        signature: FailureSignature,
        history_bytes: bytes | None,
    ) -> ResourceEnvelope:
        """Apply deterministic adjustments based on history."""
        if not history_bytes:
            return baseline

        # Simple deterministic hash-based adjustment
        # In practice, this would parse history and compute statistics
        fingerprint_hash = int(signature.fingerprint[:8], 16)

        # Bounded adjustments based on fingerprint
        cpu_delta = (fingerprint_hash % 3) - 1  # -1, 0, or 1
        memory_delta = ((fingerprint_hash >> 4) % 5) - 2  # -2 to 2
        timeout_delta = ((fingerprint_hash >> 8) % 3) - 1  # -1, 0, or 1

        return ResourceEnvelope(
            cpu_cores=baseline.cpu_cores + cpu_delta,
            memory_mb=baseline.memory_mb + (memory_delta * 256),  # 256MB increments
            timeout_s=baseline.timeout_s + (timeout_delta * 60),  # 60s increments
        )

    def _clamp_envelope(self, envelope: ResourceEnvelope) -> ResourceEnvelope:
        """Clamp envelope to configured bounds."""
        return ResourceEnvelope(
            cpu_cores=max(self.min_cpu_cores, min(self.max_cpu_cores, envelope.cpu_cores)),
            memory_mb=max(self.min_memory_mb, min(self.max_memory_mb, envelope.memory_mb)),
            timeout_s=max(self.min_timeout_s, min(self.max_timeout_s, envelope.timeout_s)),
        )

    def _generate_confidence_and_reasons(
        self,
        signature: FailureSignature,
        envelope: ResourceEnvelope,
        history_bytes: bytes | None,
    ) -> tuple[float, tuple[str, ...]]:
        """Generate deterministic confidence and reasoning."""
        reasons = []

        # Base confidence by failure type
        base_confidence = {
            "timeout": 0.8,
            "memory_error": 0.9,
            "cpu_error": 0.7,
            "io_error": 0.6,
            "network_error": 0.5,
            "unknown": 0.4,
        }.get(signature.failure_type, 0.4)

        reasons.append(f"failure_type_{signature.failure_type}")

        # Adjust confidence based on history availability
        if history_bytes:
            base_confidence += 0.1
            reasons.append("history_available")
        else:
            reasons.append("baseline_only")

        # Adjust based on envelope size (larger envelopes have lower confidence)
        if envelope.cpu_cores > 8:
            base_confidence -= 0.1
            reasons.append("high_cpu")
        if envelope.memory_mb > 8192:
            base_confidence -= 0.1
            reasons.append("high_memory")

        # Clamp confidence to valid range
        confidence = max(0.0, min(1.0, base_confidence))

        return confidence, tuple(reasons)
