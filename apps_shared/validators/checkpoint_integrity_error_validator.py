"""Secure Checkpoint Manager - Protected persistence with encryption and integrity.

This module provides a secure checkpoint implementation that encrypts data at rest,
validates integrity on load, and prevents tampering or unauthorized access.
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "checkpoint_integrity_error_validator", "p0_governance")
_emit_reads_policy_state("p0", "checkpoint_integrity_error_validator", "policy_binding")
_emit_snapshots_state("p0", "checkpoint_integrity_error_validator", "state_snapshot")
emit_replay_key("p0", "checkpoint_integrity_error_validator")
emit_determinism_digest("p0", "checkpoint_integrity_error_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class CheckpointIntegrityError(Exception):
    """Raised when checkpoint integrity validation fails."""

    pass


class SecureCheckpointManager:
    """Manages secure checkpoint persistence with encryption and integrity checks."""

    def __init__(
        self,
        hop_id: str,
        checkpoint_dir: Path,
        encryption_key: bytes | None = None,
        integrity_key: bytes | None = None,
    ):
        """Initialize the secure checkpoint manager.

        Args:
            hop_id: Unique identifier for the hop
            checkpoint_dir: Directory to store checkpoints
            encryption_key: Optional key for encryption (generated if not provided)
            integrity_key: Optional key for HMAC (generated if not provided)
        """
        self.hop_id = hop_id
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_key = encryption_key or self._generate_key()
        self.integrity_key = integrity_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key)
        logger.debug(f"Initialized SecureCheckpointManager for hop {hop_id}")

    def _generate_key(self) -> bytes:
        """Generate a cryptographically secure key."""
        return Fernet.generate_key()

    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt data using Fernet symmetric encryption.

        Args:
            data: String data to encrypt

        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption.

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted string
        """
        return self.cipher.decrypt(encrypted_data).decode()

    def _calculate_hmac(self, data: bytes) -> str:
        """Calculate HMAC-SHA256 for data integrity.

        Args:
            data: Data to sign

        Returns:
            Hexadecimal HMAC digest
        """
        return hmac.new(self.integrity_key, data, hashlib.sha256).hexdigest()

    def _verify_hmac(self, data: bytes, expected_hmac: str) -> bool:
        """Verify HMAC-SHA256 for data integrity.

        Args:
            data: Data to verify
            expected_hmac: Expected HMAC digest

        Returns:
            True if integrity is valid
        """
        calculated_hmac = self._calculate_hmac(data)
        return hmac.compare_digest(calculated_hmac, expected_hmac)

    async def save_checkpoint(self, checkpoint: MicroCheckpoint) -> None:
        """Save a checkpoint with encryption and integrity protection.

        Args:
            checkpoint: Checkpoint data to save

        Raises:
            IOError: If unable to save checkpoint
        """
        try:
            checkpoint_data = json.dumps(checkpoint.dict(), default=str)
            encrypted_data = self._encrypt_data(checkpoint_data)
            integrity_hmac = self._calculate_hmac(encrypted_data)
            secure_checkpoint = {
                "version": "1.0",
                "hop_id": self.hop_id,
                "timestamp": time.time(),
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "integrity_hmac": integrity_hmac,
            }
            checkpoint_file = self.checkpoint_dir / f"{self.hop_id}_{checkpoint.stage.value}.secure"
            temp_file = checkpoint_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(secure_checkpoint, f, indent=2)
            temp_file.replace(checkpoint_file)
            logger.debug(f"Saved secure checkpoint for stage {checkpoint.stage.value}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save secure checkpoint: {e}")
            raise OSError(f"Checkpoint save failed: {e}")

    async def load_latest_checkpoint(self) -> MicroCheckpoint | None:
        """Load the most recent checkpoint with integrity validation.

        Returns:
            The latest checkpoint or None if no valid checkpoint found

        Raises:
            CheckpointIntegrityError: If checkpoint integrity validation fails
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecureCheckpointManager.load_latest_checkpoint")

        latest_checkpoint = None
        latest_time = 0
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            try:
                checkpoint = await self._load_checkpoint_file(checkpoint_file)
                if checkpoint and checkpoint.timestamp > latest_time:
                    latest_time = checkpoint.timestamp
                    latest_checkpoint = checkpoint
            except CheckpointIntegrityError as e:
                logger.warning(f"Checkpoint integrity check failed for {checkpoint_file}: {e}")
                quarantine_file = checkpoint_file.with_suffix(".corrupt")
                checkpoint_file.replace(quarantine_file)
                logger.warning(f"Moved corrupted checkpoint to {quarantine_file}")
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")
        if latest_checkpoint:
            logger.info(f"Loaded secure checkpoint from stage {latest_checkpoint.stage.value}")
            return latest_checkpoint
        return None

    async def _load_checkpoint_file(self, checkpoint_file: Path) -> MicroCheckpoint | None:
        """Load and validate a single checkpoint file.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            Loaded checkpoint or None

        Raises:
            CheckpointIntegrityError: If integrity validation fails
        """
        with open(checkpoint_file) as f:
            secure_data = json.load(f)
        if not all(k in secure_data for k in ["encrypted_data", "integrity_hmac"]):
            raise CheckpointIntegrityError("Invalid checkpoint structure")
        encrypted_data = base64.b64decode(secure_data["encrypted_data"])
        expected_hmac = secure_data["integrity_hmac"]
        if not self._verify_hmac(encrypted_data, expected_hmac):
            raise CheckpointIntegrityError("Checkpoint integrity check failed")
        decrypted_data = self._decrypt_data(encrypted_data)
        checkpoint_dict = json.loads(decrypted_data)
        if "hop_id" in checkpoint_dict and checkpoint_dict["hop_id"] != self.hop_id:
            raise CheckpointIntegrityError(f"Checkpoint hop ID mismatch: {checkpoint_dict['hop_id']}")
        return MicroCheckpoint(**checkpoint_dict)

    def cleanup_old_checkpoints(self, keep_count: int = 3) -> None:
        """Clean up old checkpoints, keeping only the most recent ones.

        Args:
            keep_count: Number of recent checkpoints to keep per stage
        """
        stage_checkpoints = {}
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            stage = checkpoint_file.stem.split("_")[-1]
            if stage not in stage_checkpoints:
                stage_checkpoints[stage] = []
            stage_checkpoints[stage].append(checkpoint_file)
        for stage, files in stage_checkpoints.items():
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for old_file in files[keep_count:]:
                old_file.unlink()
                logger.debug(f"Removed old checkpoint: {old_file}")

    def quarantine_all_checkpoints(self) -> None:
        """Quarantine all checkpoints for this hop (emergency measure)."""
        quarantine_dir = self.checkpoint_dir / "quarantine"
        quarantine_dir.mkdir(exist_ok=True)
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            quarantine_file = quarantine_dir / checkpoint_file.name
            checkpoint_file.replace(quarantine_file)
            logger.warning(f"Quarantined checkpoint: {checkpoint_file.name}")


class CheckpointManagerFactory:
    """Factory for creating and managing secure checkpoint managers."""

    _managers: dict[str, SecureCheckpointManager] = {}
    _global_key: bytes | None = None

    @classmethod
    def get_manager(
        cls, hop_id: str, checkpoint_dir: Path, use_global_key: bool = True
    ) -> SecureCheckpointManager:
        """Get or create a checkpoint manager.

        Args:
            hop_id: Unique hop identifier
            checkpoint_dir: Directory for checkpoints
            use_global_key: Whether to use a global encryption key

        Returns:
            SecureCheckpointManager instance
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CheckpointManagerFactory.get_manager")

        if hop_id not in cls._managers:
            if use_global_key:
                if cls._global_key is None:
                    cls._global_key = Fernet.generate_key()
                    logger.info("Generated global checkpoint encryption key")
                manager = SecureCheckpointManager(hop_id, checkpoint_dir, encryption_key=cls._global_key)
            else:
                manager = SecureCheckpointManager(hop_id, checkpoint_dir)
            cls._managers[hop_id] = manager
        return cls._managers[hop_id]

    @classmethod
    def quarantine_all(cls, checkpoint_dir: Path) -> None:
        """Quarantine all checkpoints in a directory.

        Args:
            checkpoint_dir: Directory containing checkpoints
        """
        for manager in cls._managers.values():
            if manager.checkpoint_dir == checkpoint_dir:
                manager.quarantine_all_checkpoints()
