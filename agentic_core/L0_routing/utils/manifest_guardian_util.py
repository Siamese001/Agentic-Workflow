import hashlib
import logging
import os
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "manifest_guardian_util", "p0_governance")
_emit_snapshots_state("p0", "manifest_guardian_util", "state_snapshot")

logger = logging.getLogger(__name__)


class ManifestGuardian:
    """
    L0 Security Component: SSOT Integrity Enforcer.

    Responsibilities:
    1. Generate SHA-256 checksums of the manifest.json.
    2. Validate runtime manifest against the frozen boot checksum.
    3. Lock the manifest file system permissions (Linux/Unix).
    """

    MANIFEST_PATH = Path("manifest.json")
    LOCK_FILE = Path(".manifest.lock")

    @staticmethod
    def calculate_checksum(file_path: Path = MANIFEST_PATH) -> str:
        """Calculates the SHA-256 checksum of the manifest file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ManifestGuardian.calculate_checksum"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not file_path.exists():
            raise FileNotFoundError(f"SSOT Blueprint missing: {file_path}")
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @classmethod
    def seal_manifest(cls) -> str:
        """Generates the lock file containing the authoritative checksum."""
        checksum = cls.calculate_checksum()
        with open(cls.LOCK_FILE, "w") as f:
            f.write(checksum)
        try:
            os.chmod(cls.MANIFEST_PATH, 292)
            logger.info(f"Manifest sealed. Checksum: {checksum[:8]}...")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Could not enforce read-only permissions: {e}")
        return checksum

    @classmethod
    def verify_integrity(cls) -> bool:
        """
        Compares current manifest state against the .lock file.
        Returns True if integrity is preserved, False otherwise.
        """
        if not cls.LOCK_FILE.exists():
            logger.critical("Integrity Breach: .manifest.lock is missing!")
            return False
        with open(cls.LOCK_FILE) as f:
            stored_checksum = f.read().strip()
        current_checksum = cls.calculate_checksum()
        if stored_checksum != current_checksum:
            logger.critical(
                f"SSOT CORRUPTION DETECTED. \nExpected: {stored_checksum}\nActual:   {current_checksum}"
            )
            return False
        return True
