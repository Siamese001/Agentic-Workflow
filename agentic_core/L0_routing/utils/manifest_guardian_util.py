import hashlib
import logging
import os
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class ManifestGuardian:
    """
    L0 Security Component: SSOT Integrity Enforcer.

    Responsibilities:
    1. Generate SHA-256 checksums of the manifest.json.
    2. Validate runtime manifest against the frozen boot checksum.
    3. Lock the manifest file system permissions (Linux/Unix).
    """
    MANIFEST_PATH = Path('manifest.json')
    LOCK_FILE = Path('.manifest.lock')

    @staticmethod
    def calculate_checksum(file_path: Path=MANIFEST_PATH) -> str:
        """Calculates the SHA-256 checksum of the manifest file."""
        if not file_path.exists():
            raise FileNotFoundError(f'SSOT Blueprint missing: {file_path}')
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @classmethod
    def seal_manifest(cls) -> str:
        """Generates the lock file containing the authoritative checksum."""
        checksum = cls.calculate_checksum()
        with open(cls.LOCK_FILE, 'w') as f:
            f.write(checksum)
        try:
            os.chmod(cls.MANIFEST_PATH, 292)
            logger.info(f'Manifest sealed. Checksum: {checksum[:8]}...')
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f'Could not enforce read-only permissions: {e}')
        return checksum

    @classmethod
    def verify_integrity(cls) -> bool:
        """
        Compares current manifest state against the .lock file.
        Returns True if integrity is preserved, False otherwise.
        """
        if not cls.LOCK_FILE.exists():
            logger.critical('Integrity Breach: .manifest.lock is missing!')
            return False
        with open(cls.LOCK_FILE) as f:
            stored_checksum = f.read().strip()
        current_checksum = cls.calculate_checksum()
        if stored_checksum != current_checksum:
            logger.critical(f'SSOT CORRUPTION DETECTED. \nExpected: {stored_checksum}\nActual:   {current_checksum}')
            return False
        return True
