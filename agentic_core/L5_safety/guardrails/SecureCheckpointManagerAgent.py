from __future__ import annotations
from dataclasses import dataclass
"""Secure Checkpoint Manager - Protected persistence with encryption and integrity.

This module provides a secure Checkpoint implementation that encrypts data at rest,
validates integrity on load, and prevents tampering or unauthorized access.
"""

import hashlib
import hmac
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from agentic_core.schemas.models.runtime_models import MicroCheckpoint
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


class CheckpointIntegrityError(Exception):
    """Raised when Checkpoint integrity validation fails."""
    pass


@dataclass
class SecureCheckpointManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Manages secure Checkpoint persistence with encryption and integrity checks."""
    
    def __init__(
        self,
        hop_id: str,
        checkpoint_dir: Path,
        encryption_key: Optional[bytes] = None,
        integrity_key: Optional[bytes] = None
    ):
        """Initialize the secure Checkpoint manager.
        
        Args:
            hop_id: Unique identifier for the hop
            checkpoint_dir: Directory to store checkpoints
            encryption_key: Optional key for encryption (generated if not provided)
            integrity_key: Optional key for HMAC (generated if not provided)
        """
        self.hop_id = hop_id
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate or use provided keys
        self.encryption_key = encryption_key or self._generate_key()
        self.integrity_key = integrity_key or self._generate_key()
        
        # Initialize cipher
        self.cipher = Fernet(self.encryption_key)
        
        Logger.debug(f"Initialized SecureCheckpointManagerAgent for hop {hop_id}")
    
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
        return hmac.new(
            self.integrity_key,
            data,
            hashlib.sha256
        ).hexdigest()
    
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
    
    async def save_checkpoint(self, Checkpoint: MicroCheckpoint) -> None:
        """Save a Checkpoint with encryption and integrity protection.
        
        Args:
            Checkpoint: Checkpoint data to save
            
        Raises:
            IOError: If unable to save Checkpoint
        """
        try:
            # Serialize Checkpoint
            checkpoint_data = json.dumps(Checkpoint.dict(), default=str)
            
            # Encrypt the data
            encrypted_data = self._encrypt_data(checkpoint_data)
            
            # Calculate HMAC for integrity
            integrity_hmac = self._calculate_hmac(encrypted_data)
            
            # Prepare secure Checkpoint file
            secure_checkpoint = {
                "version": "1.0",
                "hop_id": self.hop_id,
                "timestamp": time.time(),
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "integrity_hmac": integrity_hmac
            }
            
            # Write to file with atomic operation
            checkpoint_file = self.checkpoint_dir / f"{self.hop_id}_{Checkpoint.stage.value}.secure"
            temp_file = checkpoint_file.with_suffix(".tmp")
            
            with open(temp_file, 'w') as f:
                json.dump(secure_checkpoint, f, indent=2)
            
            # Atomic rename
            temp_file.replace(checkpoint_file)
            
            Logger.debug(f"Saved secure Checkpoint for stage {Checkpoint.stage.value}")
            
        except Exception as e:
            Logger.error(f"Failed to save secure Checkpoint: {e}")
            raise IOError(f"Checkpoint save failed: {e}")
    
    async def load_latest_checkpoint(self) -> Optional[MicroCheckpoint]:
        """Load the most recent Checkpoint with integrity validation.
        
        Returns:
            The latest Checkpoint or None if no valid Checkpoint found
            
        Raises:
            CheckpointIntegrityError: If Checkpoint integrity validation fails
        """
        latest_checkpoint = None
        latest_time = 0
        
        # Find all secure Checkpoint files
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            try:
                Checkpoint = await self._load_checkpoint_file(checkpoint_file)
                
                if Checkpoint and Checkpoint.timestamp > latest_time:
                    latest_time = Checkpoint.timestamp
                    latest_checkpoint = Checkpoint
                    
            except CheckpointIntegrityError as e:
                Logger.warning(f"Checkpoint integrity check failed for {checkpoint_file}: {e}")
                # Move corrupted Checkpoint to quarantine
                quarantine_file = checkpoint_file.with_suffix(".corrupt")
                checkpoint_file.replace(quarantine_file)
                Logger.warning(f"Moved corrupted Checkpoint to {quarantine_file}")
                
            except Exception as e:
                Logger.warning(f"Failed to load Checkpoint {checkpoint_file}: {e}")
        
        if latest_checkpoint:
            Logger.info(f"Loaded secure Checkpoint from stage {latest_checkpoint.stage.value}")
            return latest_checkpoint
        
        return None
    
    async def _load_checkpoint_file(self, checkpoint_file: Path) -> Optional[MicroCheckpoint]:
        """Load and validate a single Checkpoint file.
        
        Args:
            checkpoint_file: Path to Checkpoint file
            
        Returns:
            Loaded Checkpoint or None
            
        Raises:
            CheckpointIntegrityError: If integrity validation fails
        """
        with open(checkpoint_file, 'r') as f:
            secure_data = json.load(f)
        
        # Verify basic structure
        if not all(k in secure_data for k in ["encrypted_data", "integrity_hmac"]):
            raise CheckpointIntegrityError("Invalid Checkpoint structure")
        
        # Decode and verify integrity
        encrypted_data = base64.b64decode(secure_data["encrypted_data"])
        expected_hmac = secure_data["integrity_hmac"]
        
        if not self._verify_hmac(encrypted_data, expected_hmac):
            raise CheckpointIntegrityError("Checkpoint integrity check failed")
        
        # Decrypt data
        decrypted_data = self._decrypt_data(encrypted_data)
        checkpoint_dict = json.loads(decrypted_data)
        
        # Validate hop ID matches
        if "hop_id" in checkpoint_dict and checkpoint_dict["hop_id"] != self.hop_id:
            raise CheckpointIntegrityError(f"Checkpoint hop ID mismatch: {checkpoint_dict['hop_id']}")
        
        return MicroCheckpoint(**checkpoint_dict)
    
    def cleanup_old_checkpoints(self, keep_count: int = 3) -> None:
        """Clean up old checkpoints, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent checkpoints to keep per stage
        """
        # Group checkpoints by stage
        stage_checkpoints = {}
        
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            stage = checkpoint_file.stem.split("_")[-1]
            if stage not in stage_checkpoints:
                stage_checkpoints[stage] = []
            stage_checkpoints[stage].append(checkpoint_file)
        
        # Keep only the most recent checkpoints for each stage
        for stage, files in stage_checkpoints.items():
            # Sort by modification time
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove excess checkpoints
            for old_file in files[keep_count:]:
                old_file.unlink()
                Logger.debug(f"Removed old Checkpoint: {old_file}")
    
    def quarantine_all_checkpoints(self) -> None:
        """Quarantine all checkpoints for this hop (emergency measure)."""
        quarantine_dir = self.checkpoint_dir / "quarantine"
        quarantine_dir.mkdir(exist_ok=True)
        
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            quarantine_file = quarantine_dir / checkpoint_file.name
            checkpoint_file.replace(quarantine_file)
            Logger.warning(f"Quarantined Checkpoint: {checkpoint_file.name}")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# Factory for managing Checkpoint managers
class CheckpointManagerFactory:
    """Factory for creating and managing secure Checkpoint managers."""
    
    _managers: Dict[str, SecureCheckpointManagerAgent] = {}
    _global_key: Optional[bytes] = None
    
    @classmethod
    def get_manager(
        cls,
        hop_id: str,
        checkpoint_dir: Path,
        use_global_key: bool = True
    ) -> SecureCheckpointManagerAgent:
        """Get or create a Checkpoint manager.
        
        Args:
            hop_id: Unique hop identifier
            checkpoint_dir: Directory for checkpoints
            use_global_key: Whether to use a global encryption key
            
        Returns:
            SecureCheckpointManagerAgent instance
        """
        if hop_id not in cls._managers:
            if use_global_key:
                if cls._global_key is None:
                    cls._global_key = Fernet.generate_key()
                    Logger.info("Generated global Checkpoint encryption key")
                
                manager = SecureCheckpointManagerAgent(
                    hop_id,
                    checkpoint_dir,
                    encryption_key=cls._global_key
                )
            else:
                manager = SecureCheckpointManagerAgent(hop_id, checkpoint_dir)
            
            cls._managers[hop_id] = manager
        
        return cls._managers[hop_id]
    
    @classmethod
    def quarantine_all(cls, checkpoint_dir: Path) -> None:
        """Quarantine all checkpoints in a directory."""
        for manager in cls._managers.values():
            if manager.checkpoint_dir == checkpoint_dir:
                manager.quarantine_all_checkpoints()

def get_secure_checkpoint_manager(checkpoint_dir: Optional[Path] = None) -> SecureCheckpointManagerAgent:
    """Factory function to get secure checkpoint manager."""
    if checkpoint_dir is None:
        checkpoint_dir = Path("checkpoints")
    return CheckpointManagerFactory.get_manager("default", checkpoint_dir)

@timeout(300)
def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """L5 safety/guardrails - operational only."""
    if _call_path is None:
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

    agent_name = "SecureCheckpointManagerAgent"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] L5 safety/guardrails - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)


# Add heal_repository as a class method for compliance
SecureCheckpointManagerAgent.heal_repository = heal_repository
