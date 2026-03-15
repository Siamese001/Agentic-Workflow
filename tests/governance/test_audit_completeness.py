"""W15: WaveAuditSummary emission; post-seal mutation raises; wildcard scope rejected.

REQ-243/244/247:
- WaveAuditSummary emitted per wave
- Post-seal mutation raises
- Wildcard scope rejected
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

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
# WaveAuditSummary
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WaveAuditSummary:
    wave_id: str
    reqs_closed: tuple
    prev_wave_hash: str
    blueprint_hash: str
    semantic_clock_tick: int
    sealed: bool = False
    summary_hash: str = ""

    def __post_init__(self):
        if not self.summary_hash:
            data = {
                "wave_id": self.wave_id,
                "reqs_closed": list(self.reqs_closed),
                "prev_wave_hash": self.prev_wave_hash,
                "blueprint_hash": self.blueprint_hash,
                "semantic_clock_tick": self.semantic_clock_tick,
            }
            h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            object.__setattr__(self, "summary_hash", h)

    def seal(self) -> WaveAuditSummary:
        """Return a new sealed version."""
        return WaveAuditSummary(
            wave_id=self.wave_id,
            reqs_closed=self.reqs_closed,
            prev_wave_hash=self.prev_wave_hash,
            blueprint_hash=self.blueprint_hash,
            semantic_clock_tick=self.semantic_clock_tick,
            sealed=True,
            summary_hash=self.summary_hash,
        )

    def assert_not_sealed(self) -> None:
        if self.sealed:
            raise RuntimeError(f"WaveAuditSummary '{self.wave_id}' is sealed — mutation forbidden")


class WaveAuditStore:
    """Stores wave audit summaries; enforces post-seal immutability."""

    def __init__(self):
        self._summaries: dict[str, WaveAuditSummary] = {}

    def emit(self, summary: WaveAuditSummary) -> None:
        self._summaries[summary.wave_id] = summary

    def seal(self, wave_id: str) -> None:
        if wave_id not in self._summaries:
            raise KeyError(f"Wave '{wave_id}' not found")
        self._summaries[wave_id] = self._summaries[wave_id].seal()

    def update(self, wave_id: str, new_summary: WaveAuditSummary) -> None:
        existing = self._summaries.get(wave_id)
        if existing and existing.sealed:
            raise RuntimeError(f"WaveAuditSummary '{wave_id}' is sealed — mutation forbidden")
        self._summaries[wave_id] = new_summary

    def get(self, wave_id: str) -> WaveAuditSummary | None:
        return self._summaries.get(wave_id)

    @property
    def wave_count(self) -> int:
        return len(self._summaries)


# ---------------------------------------------------------------------------
# Capability scope validator (REQ-247: wildcard scope rejected)
# ---------------------------------------------------------------------------


class CapabilityScopeError(ValueError):
    pass


def validate_capability_scope(scope: str) -> None:
    """Validate capability scope. Wildcard (*) is rejected."""
    if not scope:
        raise CapabilityScopeError("Empty scope is not allowed")
    if "*" in scope:
        raise CapabilityScopeError(f"Wildcard scope '{scope}' is rejected — scopes must be explicit")
    if scope.endswith(":*") or scope == "*":
        raise CapabilityScopeError(f"Wildcard scope rejected: '{scope}'")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def store() -> WaveAuditStore:
    return WaveAuditStore()


def _make_summary(wave_id: str, tick: int = 10) -> WaveAuditSummary:
    return WaveAuditSummary(
        wave_id=wave_id,
        reqs_closed=("REQ-001", "REQ-002"),
        prev_wave_hash="a" * 64,
        blueprint_hash="b" * 64,
        semantic_clock_tick=tick,
    )


@pytest.mark.governance
def test_req243_wave_audit_summary_emitted_per_wave(store):
    """REQ-243: WaveAuditSummary is emitted for each wave."""
    for wave_id in ["W11", "W12", "W13", "W14", "W15"]:
        store.emit(_make_summary(wave_id, tick=int(wave_id[1:])))

    assert store.wave_count == 5
    assert store.get("W13") is not None


@pytest.mark.governance
def test_req244_post_seal_mutation_raises(store):
    """REQ-244: Mutation of sealed WaveAuditSummary raises RuntimeError."""
    store.emit(_make_summary("W11"))
    store.seal("W11")

    sealed = store.get("W11")
    assert sealed.sealed is True

    with pytest.raises(RuntimeError, match="sealed"):
        store.update("W11", _make_summary("W11", tick=99))


@pytest.mark.governance
def test_req244_unsealed_summary_can_be_updated(store):
    """REQ-244: Unsealed WaveAuditSummary can be updated."""
    store.emit(_make_summary("W12", tick=5))
    # Update before sealing: OK
    store.update("W12", _make_summary("W12", tick=6))
    assert store.get("W12").semantic_clock_tick == 6


@pytest.mark.governance
def test_req247_wildcard_scope_rejected():
    """REQ-247: Wildcard capability scope is rejected."""
    with pytest.raises(CapabilityScopeError, match="Wildcard"):
        validate_capability_scope("pointer_update:*")

    with pytest.raises(CapabilityScopeError, match="Wildcard"):
        validate_capability_scope("*")


@pytest.mark.governance
def test_req247_explicit_scope_accepted():
    """REQ-247: Explicit non-wildcard scope is accepted."""
    # No exception expected
    validate_capability_scope("pointer_update:ns_alpha")
    validate_capability_scope("emit_metric:trace_001")
    validate_capability_scope("execute_tool:subprocess")


@pytest.mark.governance
def test_req247_empty_scope_rejected():
    """REQ-247: Empty scope string is rejected."""
    with pytest.raises(CapabilityScopeError, match="Empty"):
        validate_capability_scope("")


@pytest.mark.governance
def test_req243_summary_hash_deterministic():
    """REQ-243: WaveAuditSummary hash is deterministic."""
    s1 = _make_summary("W11")
    s2 = _make_summary("W11")
    assert s1.summary_hash == s2.summary_hash
    assert len(s1.summary_hash) == 64


@pytest.mark.governance
def test_req244_seal_preserves_hash(store):
    """REQ-244: Sealing does not change the summary_hash."""
    store.emit(_make_summary("W13"))
    original_hash = store.get("W13").summary_hash

    store.seal("W13")
    sealed_hash = store.get("W13").summary_hash

    assert original_hash == sealed_hash
