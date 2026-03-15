"""W19: Side-effect registry + artifact legality + capability acquisition lock.

REQ-327/331/360/365:
- Side-effect registry comparison/query deterministic
- Artifact legality deterministic
- Capability acquisition lock enforced
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
# Side-effect registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SideEffectEntry:
    effect_id: str
    effect_type: str
    target: str
    authorized_by: str
    semantic_clock_tick: int

    @property
    def entry_hash(self) -> str:
        data = {
            "effect_id": self.effect_id,
            "effect_type": self.effect_type,
            "target": self.target,
            "authorized_by": self.authorized_by,
            "semantic_clock_tick": self.semantic_clock_tick,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class SideEffectRegistry:
    """Deterministic registry of authorised side effects."""

    def __init__(self):
        self._entries: dict[str, SideEffectEntry] = {}

    def register(self, entry: SideEffectEntry) -> None:
        if entry.effect_id in self._entries:
            raise ValueError(f"Duplicate effect_id: {entry.effect_id}")
        self._entries[entry.effect_id] = entry

    def query(self, effect_type: str) -> list[SideEffectEntry]:
        """Return all entries of a given type, sorted by effect_id (deterministic)."""
        return sorted(
            [e for e in self._entries.values() if e.effect_type == effect_type],
            key=lambda e: e.effect_id,
        )

    def registry_hash(self) -> str:
        """Deterministic hash of all entries (sorted by effect_id)."""
        sorted_entries = sorted(self._entries.values(), key=lambda e: e.effect_id)
        entries_data = [{"effect_id": e.effect_id, "hash": e.entry_hash} for e in sorted_entries]
        return hashlib.sha256(json.dumps(entries_data, sort_keys=True).encode()).hexdigest()

    def compare(self, other: SideEffectRegistry) -> bool:
        """Deterministic comparison — equal iff registry_hash matches."""
        return self.registry_hash() == other.registry_hash()


# ---------------------------------------------------------------------------
# Artifact legality
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArtifactLegalityRecord:
    artifact_id: str
    artifact_type: str
    signed_by: str
    policy_hash: str
    is_legal: bool

    @property
    def legality_hash(self) -> str:
        data = asdict_manual(self)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def asdict_manual(obj) -> dict:
    return {
        "artifact_id": obj.artifact_id,
        "artifact_type": obj.artifact_type,
        "signed_by": obj.signed_by,
        "policy_hash": obj.policy_hash,
        "is_legal": obj.is_legal,
    }


class ArtifactLegalityChecker:
    """Deterministic artifact legality checker."""

    def __init__(self, allowed_types: frozenset[str], required_signer: str):
        self._allowed_types = allowed_types
        self._required_signer = required_signer

    def check(self, artifact: ArtifactLegalityRecord) -> bool:
        """Return True iff artifact is legal under current policy."""
        if artifact.artifact_type not in self._allowed_types:
            return False
        if artifact.signed_by != self._required_signer:
            return False
        return artifact.is_legal


# ---------------------------------------------------------------------------
# Capability acquisition lock
# ---------------------------------------------------------------------------


class CapabilityAcquisitionLock:
    """Ensures capability acquisition is atomic and non-concurrent."""

    def __init__(self):
        self._held_by: str | None = None
        self._acquisitions: list[tuple[str, str]] = []  # (acquirer, capability)

    def acquire(self, acquirer_id: str, capability: str) -> None:
        if self._held_by is not None:
            raise RuntimeError(
                f"Capability lock held by '{self._held_by}'; '{acquirer_id}' cannot acquire '{capability}'"
            )
        self._held_by = acquirer_id
        self._acquisitions.append((acquirer_id, capability))

    def release(self, acquirer_id: str) -> None:
        if self._held_by != acquirer_id:
            raise RuntimeError(f"'{acquirer_id}' does not hold the lock")
        self._held_by = None

    @property
    def is_free(self) -> bool:
        return self._held_by is None

    @property
    def acquisition_log(self) -> list[tuple[str, str]]:
        return list(self._acquisitions)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> SideEffectRegistry:
    r = SideEffectRegistry()
    r.register(SideEffectEntry("se_001", "write", "ns_a/file.txt", "guardian", 10))
    r.register(SideEffectEntry("se_002", "read", "ns_b/data.json", "agent_x", 11))
    r.register(SideEffectEntry("se_003", "write", "ns_a/config.yaml", "guardian", 12))
    return r


@pytest.mark.governance
def test_req327_registry_query_deterministic(registry):
    """REQ-327: Side-effect registry query is deterministic."""
    results1 = registry.query("write")
    results2 = registry.query("write")
    assert [e.effect_id for e in results1] == [e.effect_id for e in results2]
    assert len(results1) == 2


@pytest.mark.governance
def test_req331_registry_comparison_deterministic(registry):
    """REQ-331: Registry comparison is deterministic."""
    # Two registries built identically must compare equal
    r2 = SideEffectRegistry()
    r2.register(SideEffectEntry("se_001", "write", "ns_a/file.txt", "guardian", 10))
    r2.register(SideEffectEntry("se_002", "read", "ns_b/data.json", "agent_x", 11))
    r2.register(SideEffectEntry("se_003", "write", "ns_a/config.yaml", "guardian", 12))

    assert registry.compare(r2) is True


@pytest.mark.governance
def test_registry_hash_two_run_identical(registry):
    """registry_hash() is identical across two calls."""
    h1 = registry.registry_hash()
    h2 = registry.registry_hash()
    assert h1 == h2
    assert len(h1) == 64


@pytest.mark.governance
def test_registry_hash_changes_on_new_entry(registry):
    """Adding an entry changes the registry hash."""
    h_before = registry.registry_hash()
    registry.register(SideEffectEntry("se_004", "delete", "ns_a/old.txt", "guardian", 13))
    h_after = registry.registry_hash()
    assert h_before != h_after


@pytest.mark.governance
def test_req360_artifact_legality_deterministic():
    """REQ-360: Artifact legality check is deterministic."""
    checker = ArtifactLegalityChecker(
        allowed_types=frozenset(["SurgicalManifest", "WaveAuditSummary"]),
        required_signer="guardian",
    )
    art = ArtifactLegalityRecord(
        artifact_id="art_001",
        artifact_type="SurgicalManifest",
        signed_by="guardian",
        policy_hash="policy_" + "a" * 57,
        is_legal=True,
    )
    result1 = checker.check(art)
    result2 = checker.check(art)
    assert result1 == result2 is True


@pytest.mark.governance
def test_req360_illegal_artifact_rejected():
    """REQ-360: Illegal artifact (wrong signer) is rejected."""
    checker = ArtifactLegalityChecker(
        allowed_types=frozenset(["SurgicalManifest"]),
        required_signer="guardian",
    )
    art = ArtifactLegalityRecord(
        artifact_id="art_bad",
        artifact_type="SurgicalManifest",
        signed_by="rogue_agent",  # wrong signer
        policy_hash="p" * 64,
        is_legal=True,
    )
    assert checker.check(art) is False


@pytest.mark.governance
def test_req365_capability_acquisition_lock():
    """REQ-365: Capability acquisition lock prevents concurrent acquisition."""
    lock = CapabilityAcquisitionLock()
    lock.acquire("agent_a", "pointer_update:ns_a")

    with pytest.raises(RuntimeError, match="held by"):
        lock.acquire("agent_b", "pointer_update:ns_a")

    lock.release("agent_a")
    assert lock.is_free

    # Now agent_b can acquire
    lock.acquire("agent_b", "pointer_update:ns_a")
    assert not lock.is_free


@pytest.mark.governance
def test_req365_acquisition_log_deterministic():
    """REQ-365: Acquisition log is deterministic and ordered."""
    lock = CapabilityAcquisitionLock()
    for i in range(3):
        lock.acquire(f"agent_{i}", f"cap_{i}")
        lock.release(f"agent_{i}")

    log = lock.acquisition_log
    assert len(log) == 3
    assert log[0] == ("agent_0", "cap_0")
    assert log[2] == ("agent_2", "cap_2")
