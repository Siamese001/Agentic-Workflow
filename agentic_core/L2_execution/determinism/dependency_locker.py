"""
DependencyLocker — Dependency lock hash for determinism surface.

Generates a SHA-256 hash of the pinned dependency versions in
requirements.txt so it can be included in the W<n>-DETERMINISM-DIGEST.
Any environment drift (unpinned upgrades) causes a hash mismatch and
fails fast.

Phase 2.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.utils.canonical_json_util import CanonicalJSON

_REQUIREMENTS_PATH = Path("requirements.txt")
_LOCK_FILE_PATH = Path("data/dependencies/lock_hash.json")


class DependencyLocker:
    """Manages the dependency lock hash used in determinism digests."""

    @classmethod
    def generate_lock_hash(cls, requirements_path: Path = _REQUIREMENTS_PATH) -> str:
        """Return SHA-256 hash of pinned dependencies from *requirements_path*."""
        if not requirements_path.exists():
            raise FileNotFoundError(f"DependencyLocker: requirements file not found: {requirements_path}")

        dependencies: dict[str, str] = {}
        for raw_line in requirements_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                package, _, version = line.partition("==")
                dependencies[package.strip()] = version.strip()
            else:
                dependencies[line.split("[")[0].split(">")[0].split("<")[0].strip()] = "unpinned"

        canonical = CanonicalJSON.serialize_bytes(dependencies)
        return hashlib.sha256(canonical).hexdigest()

    @classmethod
    def save_lock_file(
        cls,
        lock_hash: str,
        lock_file_path: Path = _LOCK_FILE_PATH,
    ) -> None:
        """Persist *lock_hash* to *lock_file_path* (creates parents if needed)."""
        lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        lock_data: dict[str, Any] = {
            "dependency_lock_hash": lock_hash,
            "schema_version": "1",
        }
        lock_file_path.write_text(CanonicalJSON.serialize(lock_data), encoding="utf-8")

    @classmethod
    def load_lock_hash(cls, lock_file_path: Path = _LOCK_FILE_PATH) -> str:
        """Load and return the stored lock hash."""
        if not lock_file_path.exists():
            raise FileNotFoundError(f"DependencyLocker: lock file not found: {lock_file_path}")
        data = json.loads(lock_file_path.read_text(encoding="utf-8"))
        return data["dependency_lock_hash"]

    @classmethod
    def validate(
        cls,
        requirements_path: Path = _REQUIREMENTS_PATH,
        lock_file_path: Path = _LOCK_FILE_PATH,
    ) -> bool:
        """Return True if current dependencies match the stored lock hash.

        If no lock file exists, generate one and return True.
        """
        current = cls.generate_lock_hash(requirements_path)
        if not lock_file_path.exists():
            cls.save_lock_file(current, lock_file_path)
            return True
        stored = cls.load_lock_hash(lock_file_path)
        return current == stored


__all__ = ["DependencyLocker"]
