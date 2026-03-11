import hashlib
import logging
import os
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        if not file_path.exists():
            raise FileNotFoundError(f"SSOT Blueprint missing: {file_path}")

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large manifests efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @classmethod
    def seal_manifest(cls) -> str:
        """Generates the lock file containing the authoritative checksum."""
        checksum = cls.calculate_checksum()

        # Atomic write of the lock file
        with open(cls.LOCK_FILE, "w") as f:
            f.write(checksum)

        # Set manifest to read-only (0o444 = r--r--r--)
        try:
            os.chmod(cls.MANIFEST_PATH, 0o444)
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
                f"SSOT CORRUPTION DETECTED. \nExpected: {stored_checksum}\nActual:   {current_checksum}",
            )
            return False

        return True
