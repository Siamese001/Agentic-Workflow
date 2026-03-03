"""Concrete VersionStore — content-addressable storage for committed ChangePackages.

Provides file-backed and in-memory implementations of the ``VersionStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------


@dataclass
class InMemoryVersionStore:
    """In-memory version store for testing and single-process use."""

    _store: dict[str, bytes] = field(default_factory=dict)
    _metadata: dict[str, dict[str, Any]] = field(default_factory=dict)

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id.

        The package must have a ``canonical_bytes()`` method for
        content-hash computation.
        """
        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")

        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"

        if version_id not in self._store:
            self._store[version_id] = payload
            self._metadata[version_id] = {
                "content_hash": content_hash,
                "type": type(pkg).__name__,
            }

        return version_id

    def get(self, version_id: str) -> bytes | None:
        return self._store.get(version_id)

    def list_versions(self) -> list[str]:
        return sorted(self._store.keys())


# ---------------------------------------------------------------------------
# File-backed implementation
# ---------------------------------------------------------------------------


class FileBackedVersionStore:
    """File-backed version store with content-addressable directory layout.

    Directory layout::

        <base_dir>/
            <content_hash[:2]>/<content_hash>.json   # payload + metadata
            _index.json                               # version_id -> hash mapping
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._base_dir / "_index.json"
        self._index: dict[str, str] = self._load_index()

    def _load_index(self) -> dict[str, str]:
        if self._index_path.exists():
            try:
                return json.loads(self._index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_index(self) -> None:
        self._index_path.write_text(
            json.dumps(self._index, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id."""
        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")

        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"

        if version_id in self._index:
            return version_id  # Idempotent

        # Write payload
        shard_dir = self._base_dir / content_hash[:2]
        shard_dir.mkdir(exist_ok=True)
        entry_path = shard_dir / f"{content_hash}.json"

        meta = {
            "version_id": version_id,
            "content_hash": content_hash,
            "type": type(pkg).__name__,
            "payload_hex": payload.hex(),
        }
        entry_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        self._index[version_id] = content_hash
        self._save_index()

        return version_id

    def get(self, version_id: str) -> bytes | None:
        content_hash = self._index.get(version_id)
        if content_hash is None:
            return None
        entry_path = self._base_dir / content_hash[:2] / f"{content_hash}.json"
        if not entry_path.exists():
            return None
        try:
            meta = json.loads(entry_path.read_text(encoding="utf-8"))
            return bytes.fromhex(meta["payload_hex"])
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            return None

    def list_versions(self) -> list[str]:
        return sorted(self._index.keys())


__all__ = [
    "InMemoryVersionStore",
    "FileBackedVersionStore",
]
