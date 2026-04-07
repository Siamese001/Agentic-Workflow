"""W16: Metrics artifact emitted from single control-spine point; duplicate emissions rejected.

REQ-060/063/298/337: Single authoritative metrics emission point.
Duplicate emissions per trace_id are rejected at runtime.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Metrics emission types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricsArtifact:
    trace_id: str
    metric_name: str
    value: Any
    semantic_clock_tick: int
    emitter_id: str
    artifact_hash: str = ""

    def __post_init__(self):
        if not self.artifact_hash:
            data = {
                "trace_id": self.trace_id,
                "metric_name": self.metric_name,
                "value": str(self.value),
                "semantic_clock_tick": self.semantic_clock_tick,
                "emitter_id": self.emitter_id,
            }
            h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            object.__setattr__(self, "artifact_hash", h)


class DuplicateEmissionError(RuntimeError):
    """Raised when metrics are emitted twice for the same trace_id."""


class MetricsEmissionChokepoint:
    """
    Single authoritative control-spine emission point.
    Rejects duplicate emissions per trace_id.
    All metric emissions MUST go through this chokepoint.
    """

    def __init__(self, emitter_id: str):
        self._emitter_id = emitter_id
        self._emitted_trace_ids: set[str] = set()
        self._emissions: list[MetricsArtifact] = []

    def emit(self, trace_id: str, metric_name: str, value: Any, tick: int) -> MetricsArtifact:
        """Emit a metric. Raises DuplicateEmissionError if trace_id already emitted."""
        if trace_id in self._emitted_trace_ids:
            raise DuplicateEmissionError(
                f"Duplicate metric emission for trace_id='{trace_id}' — "
                "each trace_id may only emit once through the control spine",
            )
        artifact = MetricsArtifact(
            trace_id=trace_id,
            metric_name=metric_name,
            value=value,
            semantic_clock_tick=tick,
            emitter_id=self._emitter_id,
        )
        self._emitted_trace_ids.add(trace_id)
        self._emissions.append(artifact)
        return artifact

    @property
    def emission_count(self) -> int:
        return len(self._emissions)

    @property
    def emitted_trace_ids(self) -> set[str]:
        return frozenset(self._emitted_trace_ids)

    def get_emission(self, trace_id: str) -> MetricsArtifact | None:
        for a in self._emissions:
            if a.trace_id == trace_id:
                return a
        return None

    def reset_for_test(self) -> None:
        """Reset state for test isolation."""
        self._emitted_trace_ids.clear()
        self._emissions.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def chokepoint() -> MetricsEmissionChokepoint:
    return MetricsEmissionChokepoint(emitter_id="control_spine_emitter")


@pytest.mark.governance
def test_metrics_single_emission_succeeds(chokepoint):
    """First emission for a trace_id succeeds."""
    artifact = chokepoint.emit("trace_001", "latency_ms", 42, tick=10)

    assert chokepoint.emission_count == 1
    assert len(artifact.artifact_hash) == 64
    assert artifact.trace_id == "trace_001"


@pytest.mark.governance
def test_metrics_duplicate_emission_rejected(chokepoint):
    """Duplicate emission for same trace_id raises DuplicateEmissionError."""
    chokepoint.emit("trace_001", "latency_ms", 42, tick=10)

    with pytest.raises(DuplicateEmissionError, match="Duplicate metric emission"):
        chokepoint.emit("trace_001", "latency_ms", 99, tick=11)

    assert chokepoint.emission_count == 1


@pytest.mark.governance
def test_metrics_different_trace_ids_allowed(chokepoint):
    """Different trace_ids can each emit once."""
    for i in range(5):
        chokepoint.emit(f"trace_{i:03d}", "metric_x", i, tick=i)

    assert chokepoint.emission_count == 5


@pytest.mark.governance
def test_metrics_artifact_hash_deterministic(chokepoint):
    """MetricsArtifact hash is deterministic for identical inputs."""
    a1 = MetricsArtifact(
        trace_id="trace_hash_test",
        metric_name="speed",
        value=100,
        semantic_clock_tick=7,
        emitter_id="emitter_a",
    )
    a2 = MetricsArtifact(
        trace_id="trace_hash_test",
        metric_name="speed",
        value=100,
        semantic_clock_tick=7,
        emitter_id="emitter_a",
    )
    assert a1.artifact_hash == a2.artifact_hash


@pytest.mark.governance
def test_metrics_emitter_id_in_artifact(chokepoint):
    """Emitter_id from control spine is recorded in emitted artifact."""
    artifact = chokepoint.emit("trace_emitter", "cpu_pct", 55.5, tick=20)
    assert artifact.emitter_id == "control_spine_emitter"


@pytest.mark.governance
def test_metrics_get_emission_by_trace_id(chokepoint):
    """get_emission returns correct artifact for trace_id."""
    chokepoint.emit("trace_lookup", "memory_mb", 512, tick=15)
    result = chokepoint.get_emission("trace_lookup")

    assert result is not None
    assert result.metric_name == "memory_mb"
    assert result.value == 512


@pytest.mark.governance
def test_metrics_emitted_trace_ids_tracked(chokepoint):
    """emitted_trace_ids tracks all emitted trace_ids."""
    traces = [f"t_{i}" for i in range(3)]
    for t in traces:
        chokepoint.emit(t, "metric", 1, tick=1)

    assert chokepoint.emitted_trace_ids == frozenset(traces)


@pytest.mark.governance
def test_metrics_reset_clears_state(chokepoint):
    """reset_for_test clears all state for test isolation."""
    chokepoint.emit("trace_reset", "m", 1, tick=1)
    chokepoint.reset_for_test()

    assert chokepoint.emission_count == 0
    assert len(chokepoint.emitted_trace_ids) == 0

    # Can emit again after reset
    chokepoint.emit("trace_reset", "m", 1, tick=1)
    assert chokepoint.emission_count == 1
