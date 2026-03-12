"""L4 State Writer — Write-once, versioned, idempotent state persistence.

Provides content-hash keyed writes for L4A detection signals, L4B healing
snapshots, and L4C shadow drift / policy recommendation / retrieval profile
artifacts.  All writes are idempotent: re-writing the same payload_bytes for
the same component returns the existing version_id without mutation.

Two concrete implementations:
  - ``InMemoryL4StateWriter``  — test / single-process use
  - ``FileBackedL4StateWriter`` — persistent across restarts
  - ``NoOpL4StateWriter``      — safe default when persistence is disabled
"""
from __future__ import annotations
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class L4StateWriter(Protocol):
    """Protocol for L4 state writer with write-once semantics.

    All writes are content-hash keyed and idempotent.
    Returns version IDs for tracking and activation.
    """

    def write_l4a_detection_signal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        ...

    def write_l4b_healing_snapshot(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        ...

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        ...

    def write_l4c_policy_recommendation(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        ...

    def write_l4c_retrieval_profile_proposal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        ...

    def read_latest_detection_signal(self) -> bytes | None:
        ...

    def read_latest_drift_snapshot(self) -> bytes | None:
        ...

def _content_hash(payload_bytes: bytes) -> str:
    """SHA-256 content hash of payload bytes (deterministic)."""
    return hashlib.sha256(payload_bytes).hexdigest()

@dataclass(frozen=True, slots=True)
class _VersionEntry:
    """Immutable record of a single L4 write."""
    version_id: str
    bucket: str
    component_name: str
    created_utc: int
    payload_bytes: bytes

@dataclass
class InMemoryL4StateWriter:
    """In-memory L4 state writer for tests and single-process pipelines."""
    _store: dict[str, _VersionEntry] = field(default_factory=dict)
    _latest: dict[str, bytes] = field(default_factory=dict)

    def _write(self, bucket: str, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        content_key = _content_hash(payload_bytes)
        version_id = f'{bucket}_{component_name}_{content_key[:16]}_{created_utc}'
        if version_id not in self._store:
            self._store[version_id] = _VersionEntry(version_id=version_id, bucket=bucket, component_name=component_name, created_utc=created_utc, payload_bytes=payload_bytes)
        self._latest[bucket] = payload_bytes
        return version_id

    def write_l4a_detection_signal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4a_detection', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4b_healing_snapshot(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4b_healing', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_shadow_drift', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_policy_recommendation(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_policy_rec', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_retrieval_profile_proposal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_profile_prop', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def read_latest_detection_signal(self) -> bytes | None:
        return self._latest.get('l4a_detection')

    def read_latest_drift_snapshot(self) -> bytes | None:
        return self._latest.get('l4c_shadow_drift')

class FileBackedL4StateWriter:
    """File-backed L4 state writer with content-addressable storage.

    Directory layout::

        <base_dir>/
            l4a_detection/<content_hash>.json
            l4b_healing/<content_hash>.json
            l4c_shadow_drift/<content_hash>.json
            l4c_policy_rec/<content_hash>.json
            l4c_profile_prop/<content_hash>.json
            _latest/<bucket>.bin          # raw payload of most recent write
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        (self._base_dir / '_latest').mkdir(exist_ok=True)

    def _write(self, bucket: str, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        content_key = _content_hash(payload_bytes)
        version_id = f'{bucket}_{component_name}_{content_key[:16]}_{created_utc}'
        bucket_dir = self._base_dir / bucket
        bucket_dir.mkdir(exist_ok=True)
        entry_path = bucket_dir / f'{content_key}.json'
        if not entry_path.exists():
            meta = {'version_id': version_id, 'bucket': bucket, 'component_name': component_name, 'created_utc': created_utc, 'content_hash': content_key, 'payload_hex': payload_bytes.hex()}
            entry_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        latest_path = self._base_dir / '_latest' / f'{bucket}.bin'
        latest_path.write_bytes(payload_bytes)
        return version_id

    def write_l4a_detection_signal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4a_detection', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4b_healing_snapshot(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4b_healing', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_shadow_drift', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_policy_recommendation(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_policy_rec', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_retrieval_profile_proposal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('l4c_profile_prop', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def read_latest_detection_signal(self) -> bytes | None:
        p = self._base_dir / '_latest' / 'l4a_detection.bin'
        return p.read_bytes() if p.exists() else None

    def read_latest_drift_snapshot(self) -> bytes | None:
        p = self._base_dir / '_latest' / 'l4c_shadow_drift.bin'
        return p.read_bytes() if p.exists() else None

class NoOpL4StateWriter:
    """No-op implementation that does nothing.

    Used as safe default when L4 state writing is not configured.
    """

    def write_l4a_detection_signal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f'noop_l4a_{created_utc}'

    def write_l4b_healing_snapshot(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f'noop_l4b_{created_utc}'

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f'noop_l4c_drift_{created_utc}'

    def write_l4c_policy_recommendation(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f'noop_l4c_policy_{created_utc}'

    def write_l4c_retrieval_profile_proposal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f'noop_l4c_profile_{created_utc}'

    def read_latest_detection_signal(self) -> bytes | None:
        return None

    def read_latest_drift_snapshot(self) -> bytes | None:
        return None

@dataclass
class SimpleChangePackage:
    """Minimal ChangePackage suitable for L4 state writes.

    Implements the ``canonical_bytes()`` contract required by
    ``L4VersionStore.commit_change_package``.
    """
    component: str
    payload_bytes: bytes
    metadata: dict

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes representation of this package."""
        meta_str = json.dumps({k: str(v) for k, v in sorted(self.metadata.items())}, separators=(',', ':'))
        return f'{self.component}:{self.payload_bytes.hex()}:{meta_str}'.encode()

class DefaultL4StateWriter:
    """L4 state writer backed by an L4VersionStore.

    Delegates all writes to the provided version store.  Each call creates a
    ``SimpleChangePackage`` and commits it via
    ``version_store.commit_change_package``, returning the resulting version_id.
    Idempotency is enforced by the store's content-hash keying.
    """

    def __init__(self, version_store) -> None:
        self._store = version_store

    def _write(self, signal_type: str, signal_prefix: str, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        pkg = SimpleChangePackage(component=f'{signal_prefix}_{component_name}', payload_bytes=payload_bytes, metadata={'component_name': component_name, 'created_utc': created_utc, 'type': signal_type})
        return self._store.commit_change_package(pkg, parent_version_id=None, change_spec_hash=hashlib.sha256(payload_bytes).hexdigest(), committed_at_utc=created_utc)

    def write_l4a_detection_signal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('detection_signal', 'l4a_detection_signal', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4b_healing_snapshot(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('healing_snapshot', 'l4b_healing_snapshot', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('shadow_drift', 'l4c_shadow_drift', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_policy_recommendation(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('policy_recommendation', 'l4c_policy_rec', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def write_l4c_retrieval_profile_proposal(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write('retrieval_profile_proposal', 'l4c_profile_prop', payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc)

    def read_latest_detection_signal(self) -> bytes | None:
        return None

    def read_latest_drift_snapshot(self) -> bytes | None:
        return None
__all__ = ['L4StateWriter', 'InMemoryL4StateWriter', 'FileBackedL4StateWriter', 'NoOpL4StateWriter', 'DefaultL4StateWriter', 'SimpleChangePackage']
