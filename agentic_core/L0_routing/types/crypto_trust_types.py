"""
V15 P5 Typed Artifacts — Cryptographic Trust & Signing.

Typed artifacts required by Prompt v5.0 Enhanced for P5 (Tokenized
Authority / Cryptographic Trust) invariants. All artifacts are frozen
dataclasses with strict field validation enforced at construction time.

Artifact version: 1.0.0
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, emit_replay_key, emit_determinism_digest


class KeyStatus(Enum):
    """Status of a key in the trust root."""

    ACTIVE = "active"
    REVOKED = "revoked"


class SigningAlgorithm(Enum):
    """Supported signing algorithms."""

    HMAC_SHA256 = "hmac-sha256"


@dataclass(frozen=True)
class KeyRecord:
    """§7.4.2 — A single key record in the trust root.

    Fields: key_id, public_key, created_tick, status, algorithm.
    """

    key_id: str
    public_key: bytes
    created_tick: int
    status: KeyStatus
    algorithm: SigningAlgorithm = SigningAlgorithm.HMAC_SHA256

    def __post_init__(self) -> None:
        if not self.key_id:
            raise ValueError("KeyRecord: key_id must be non-empty")
        if not self.public_key:
            raise ValueError("KeyRecord: public_key must be non-empty")
        if self.created_tick < 0:
            raise ValueError(f"KeyRecord: created_tick must be >= 0, got {self.created_tick}")
        if not isinstance(self.status, KeyStatus):
            raise TypeError(f"KeyRecord: status must be KeyStatus, got {type(self.status).__name__}")
        if not isinstance(self.algorithm, SigningAlgorithm):
            raise TypeError(
                f"KeyRecord: algorithm must be SigningAlgorithm, got {type(self.algorithm).__name__}"
            )


@dataclass(frozen=True)
class TrustRoot:
    """§7.4.2 — Pinned trust root containing all known keys.

    Immutable once constructed. Keys are looked up by key_id.
    """

    keys: tuple[KeyRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.keys, tuple):
            raise TypeError("TrustRoot: keys must be a tuple")
        ids = [k.key_id for k in self.keys]
        if len(ids) != len(set(ids)):
            raise ValueError("TrustRoot: duplicate key_id detected")

    def get_key(self, key_id: str) -> KeyRecord | None:
        """Look up a key by ID. Returns None if not found."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "TrustRoot.get_key")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        for k in self.keys:
            if k.key_id == key_id:
                return k
        return None


@dataclass(frozen=True)
class SignatureEnvelope:
    """§7.4 / §7.2.1 — Cryptographic signature wrapping any artifact.

    Fields: trace_id, artifact_hash, key_id, signature, algorithm,
    semantic_clock_tick.
    """

    trace_id: str
    artifact_hash: str
    key_id: str
    signature: str
    algorithm: SigningAlgorithm
    semantic_clock_tick: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("SignatureEnvelope: trace_id must be non-empty")
        if not self.artifact_hash:
            raise ValueError("SignatureEnvelope: artifact_hash must be non-empty")
        if not self.key_id:
            raise ValueError("SignatureEnvelope: key_id must be non-empty")
        if not self.signature:
            raise ValueError("SignatureEnvelope: signature must be non-empty")
        if not isinstance(self.algorithm, SigningAlgorithm):
            raise TypeError(
                f"SignatureEnvelope: algorithm must be SigningAlgorithm, got {type(self.algorithm).__name__}"
            )
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"SignatureEnvelope: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}"
            )


@dataclass(frozen=True)
class SignedGuardianArtifact:
    """§7.2.1 / §7.4 — A signed guardian artifact with all required fields.

    Required per spec: trace_id, signature, prestaged_perms,
    environment_metadata, commit_hash, pass_fail.
    """

    trace_id: str
    signature: str
    prestaged_perms: tuple[str, ...]
    environment_metadata: dict[str, str]
    commit_hash: str
    pass_fail: bool

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("SignedGuardianArtifact: trace_id must be non-empty")
        if not self.signature:
            raise ValueError("SignedGuardianArtifact: signature must be non-empty")
        if not isinstance(self.prestaged_perms, tuple):
            raise TypeError("SignedGuardianArtifact: prestaged_perms must be a tuple")
        if not isinstance(self.environment_metadata, dict):
            raise TypeError("SignedGuardianArtifact: environment_metadata must be a dict")
        if not self.commit_hash:
            raise ValueError("SignedGuardianArtifact: commit_hash must be non-empty")


class HumanResolution(Enum):
    """§2.7 — Ternary resolution from human review."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"


@dataclass(frozen=True)
class SignedModify:
    """§2.7.1 — Human MODIFY resolution generates a signed artifact.

    Required fields: trace_id, human_reviewer_id, resolution,
    modified_manifest, signature.
    """

    trace_id: str
    human_reviewer_id: str
    resolution: HumanResolution
    modified_manifest: str
    signature: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("SignedModify: trace_id must be non-empty")
        if not self.human_reviewer_id:
            raise ValueError("SignedModify: human_reviewer_id must be non-empty")
        if not isinstance(self.resolution, HumanResolution):
            raise TypeError(
                f"SignedModify: resolution must be HumanResolution, got {type(self.resolution).__name__}"
            )
        if not self.modified_manifest:
            raise ValueError("SignedModify: modified_manifest must be non-empty")
        if not self.signature:
            raise ValueError("SignedModify: signature must be non-empty")


@dataclass
class ReplayGuardRecord:
    """§7.2 — Tracks artifact_hash sightings for replay detection.

    Not frozen: seen_count is mutable for tracking.
    """

    artifact_hash: str
    first_seen_tick: int
    seen_count: int = 1

    def __post_init__(self) -> None:
        if not self.artifact_hash:
            raise ValueError("ReplayGuardRecord: artifact_hash must be non-empty")
        if self.first_seen_tick < 0:
            raise ValueError(f"ReplayGuardRecord: first_seen_tick must be >= 0, got {self.first_seen_tick}")
        if self.seen_count < 1:
            raise ValueError(f"ReplayGuardRecord: seen_count must be >= 1, got {self.seen_count}")


@dataclass
class HashMismatchTracker:
    """§2.6 — Tracks hash mismatches within a healing wave.

    ≥2 mismatches in a single wave forces human escalation.
    """

    wave_id: str
    mismatch_count: int = 0
    escalation_threshold: int = 2
    escalated: bool = False

    def __post_init__(self) -> None:
        if not self.wave_id:
            raise ValueError("HashMismatchTracker: wave_id must be non-empty")

    def record_mismatch(self) -> bool:
        """Record a mismatch. Returns True if escalation is now required."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "HashMismatchTracker.record_mismatch")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self.mismatch_count += 1
        if self.mismatch_count >= self.escalation_threshold:
            self.escalated = True
        return self.escalated


class SignatureEnclave(ABC):
    """§7.4.1 — Abstract interface for the signing enclave.

    All signing operations MUST occur within a SignatureEnclave.
    Implementations must be deterministic, with no wall-clock or env reads.
    """

    @abstractmethod
    def sign(self, artifact_bytes: bytes, key_id: str) -> str:
        """Sign artifact bytes with the given key. Returns signature hex string."""

    @abstractmethod
    def verify(self, artifact_bytes: bytes, signature: str, key_id: str) -> bool:
        """Verify signature against artifact bytes and key. Returns True if valid."""

    @abstractmethod
    def get_key_record(self, key_id: str) -> KeyRecord | None:
        """Retrieve a key record from the enclave's trust root."""


class DeterministicTestEnclave(SignatureEnclave):
    """§7.4.1 — Deterministic test enclave using HMAC-SHA256 with fixed keys.

    No network, no env reads, no wall-clock. Purely deterministic.
    """

    def __init__(self, trust_root: TrustRoot) -> None:
        self._trust_root = trust_root

    def sign(self, artifact_bytes: bytes, key_id: str) -> str:
        """HMAC-SHA256 sign using the key's public_key as the HMAC secret."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "DeterministicTestEnclave.sign")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        import hmac

        key_record = self._trust_root.get_key(key_id)
        if key_record is None:
            raise KeyError(f"SignatureEnclave: unknown key_id '{key_id}'")
        if key_record.status == KeyStatus.REVOKED:
            raise PermissionError(f"SignatureEnclave: key '{key_id}' is REVOKED")
        return hmac.new(key_record.public_key, artifact_bytes, hashlib.sha256).hexdigest()

    def verify(self, artifact_bytes: bytes, signature: str, key_id: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        import hmac as hmac_mod

        key_record = self._trust_root.get_key(key_id)
        if key_record is None:
            return False
        if key_record.status == KeyStatus.REVOKED:
            return False
        expected = hmac_mod.new(key_record.public_key, artifact_bytes, hashlib.sha256).hexdigest()
        return hmac_mod.compare_digest(expected, signature)

    def get_key_record(self, key_id: str) -> KeyRecord | None:
        return self._trust_root.get_key(key_id)


__all__ = [
    "DeterministicTestEnclave",
    "HashMismatchTracker",
    "HumanResolution",
    "KeyRecord",
    "KeyStatus",
    "ReplayGuardRecord",
    "SignatureEnclave",
    "SignatureEnvelope",
    "SignedGuardianArtifact",
    "SignedModify",
    "SigningAlgorithm",
    "TrustRoot",
]
