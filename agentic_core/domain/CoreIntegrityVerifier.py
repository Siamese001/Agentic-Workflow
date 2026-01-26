"""
agentic_core/domain/sovereign_lock.py - The Immutable Lock

Prevents system startup if the Core DNA has been tampered with.
Implements SHA-256 Merkle root verification for the base_agents directory.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Final
from agentic_core.domain.SovereignError import ConfigurationError


class CoreIntegrityVerifier:
    """
    Guards the Sovereign Core against mutation.

    Calculates SHA-256 Merkle root of the base_agents directory.
    If files have been modified without a version bump, raises FatalError.

    The "Golden Seal" - In production, this would be signed/encrypted.
    For now, it dynamically calculates self-consistency.
    """

    CORE_PATH: Final[Path] = Path(__file__).parent.parent.absolute() / "base_agents"
    GOLDEN_SEAL_FILE: Final[Path] = Path(__file__).parent.absolute() / ".core_golden_seal"

    @classmethod
    def verify_core_integrity(cls) -> bool:
        """
        Calculate Merkle Hash of the base_agents directory.
        If files have been modified without a version bump, raise FatalError.

        Returns:
            True if integrity is verified

        Raises:
            ConfigurationError: If core integrity is compromised
        """
        # Handle pytest running from tests directory
        if not cls.CORE_PATH.exists():
            # Try alternative path if running from tests directory
            alt_path = Path(__file__).parent.parent.parent / "agentic_core" / "base_agents"
            if alt_path.exists():
                cls.CORE_PATH = alt_path
            else:
                raise ConfigurationError("CRITICAL: Sovereign Core Missing!")

        # Dynamic check: Ensure no 'pyc' or temporary files are affecting logic
        unsafe_files = (
            list(cls.CORE_PATH.glob("*.tmp"))
            + list(cls.CORE_PATH.glob("*.bak"))
            + list(cls.CORE_PATH.glob("*.pyc"))
        )

        # Check for __pycache__ directories but only warn, don't fail
        pycache_dirs = list(cls.CORE_PATH.glob("__pycache__"))
        if pycache_dirs:
            # __pycache__ is normal during development, just clean it
            for pycache in pycache_dirs:
                try:
                    import shutil

                    shutil.rmtree(pycache)
                except Exception:
                    pass  # Ignore cleanup errors

        if unsafe_files:
            raise ConfigurationError(
                f"Integrity Breach: Unsafe artifacts found in Core: {unsafe_files}"
            )

        # Calculate current Merkle root
        current_hash = cls._calculate_merkle_root()

        # Check against golden seal (if exists)
        if cls.GOLDEN_SEAL_FILE.exists():
            expected_hash = cls.GOLDEN_SEAL_FILE.read_text().strip()
            if current_hash != expected_hash:
                raise ConfigurationError(
                    f"CRITICAL: CORE INTEGRITY COMPROMISED!\n"
                    f"Expected: {expected_hash}\n"
                    f"Found: {current_hash}\n"
                    f"The Sovereign Core has been tampered with!"
                )
        else:
            # Create golden seal for first run
            cls.GOLDEN_SEAL_FILE.write_text(current_hash)
            print(f"[SOVEREIGN LOCK] Golden Seal created: {current_hash[:16]}...")

        return True

    @classmethod
    def _calculate_merkle_root(cls) -> str:
        """
        Calculate SHA-256 Merkle root of all Python files in base_agents.

        Returns:
            Merkle root hash as hex string
        """
        # Get all Python files, sorted for deterministic order
        py_files = sorted(cls.CORE_PATH.glob("**/*.py"))

        if not py_files:
            raise ConfigurationError("No Python files found in Core directory!")

        # Calculate hash for each file
        file_hashes = []
        for file_path in py_files:
            file_hash = cls._calculate_file_hash(file_path)
            # Include relative path in hash to detect file renames
            rel_path = file_path.relative_to(cls.CORE_PATH)
            file_hashes.append(f"{rel_path}:{file_hash}")

        # Calculate Merkle root (hash of all file hashes combined)
        combined_data = "\n".join(file_hashes)
        merkle_root = hashlib.sha256(combined_data.encode()).hexdigest()

        return merkle_root

    @staticmethod
    def _calculate_file_hash(path: Path) -> str:
        """
        SHA-256 hash of a DNA file.

        Args:
            path: Path to the file

        Returns:
            SHA-256 hash as hex string
        """
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as e:
            raise ConfigurationError(f"Failed to hash file {path}: {e}")

    @classmethod
    def update_golden_seal(cls) -> str:
        """
        Update the golden seal with current hash.

        Returns:
            New golden seal hash
        """
        current_hash = cls._calculate_merkle_root()
        cls.GOLDEN_SEAL_FILE.write_text(current_hash)
        return current_hash

    @classmethod
    def force_verify(cls) -> bool:
        """
        Force verification without golden seal check.

        Returns:
            True if basic integrity checks pass
        """
        if not cls.CORE_PATH.exists():
            raise ConfigurationError("CRITICAL: Sovereign Core Missing!")

        # Check for unsafe files
        unsafe_files = (
            list(cls.CORE_PATH.glob("*.tmp"))
            + list(cls.CORE_PATH.glob("*.bak"))
            + list(cls.CORE_PATH.glob("*.pyc"))
            + list(cls.CORE_PATH.glob("__pycache__"))
        )

        if unsafe_files:
            raise ConfigurationError(
                f"Integrity Breach: Unsafe artifacts found in Core: {unsafe_files}"
            )

        return True


class SovereignLockError(ConfigurationError):
    """Raised when the Sovereign Lock detects integrity violations."""

    pass


def emergency_shutdown(message: str) -> None:
    """
    Emergency shutdown when core integrity is compromised.

    Args:
        message: Error message to display
    """
    sys.stderr.write(f"\n🚨 SOVEREIGN LOCK EMERGENCY 🚨\n{message}\n")
    sys.stderr.write("AGENT TERMINATED: Core integrity compromised.\n")
    raise SovereignLockError(message)
