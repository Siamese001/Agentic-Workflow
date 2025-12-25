"""
Autonomous Checkpoint Manager - L4 State Enhancement

Automatically manages state checkpoints with intelligent recovery.
Provides rollback capabilities and state consistency verification.
"""
import asyncio
import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Represents a state checkpoint."""
    checkpoint_id: str
    timestamp: datetime
    state_snapshot: Dict[str, Any]
    file_hashes: Dict[str, str]
    metadata: Dict[str, Any]
    is_valid: bool = True
    recovery_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary."""
        return {
            'checkpoint_id': self.checkpoint_id,
            'timestamp': self.timestamp.isoformat(),
            'state_snapshot': self.state_snapshot,
            'file_hashes': self.file_hashes,
            'metadata': self.metadata,
            'is_valid': self.is_valid,
            'recovery_count': self.recovery_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create checkpoint from dictionary."""
        return cls(
            checkpoint_id=data['checkpoint_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            state_snapshot=data['state_snapshot'],
            file_hashes=data['file_hashes'],
            metadata=data['metadata'],
            is_valid=data.get('is_valid', True),
            recovery_count=data.get('recovery_count', 0)
        )


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool
    checkpoint_id: str
    files_restored: int
    state_restored: bool
    errors: List[str] = field(default_factory=list)
    recovery_time: float = 0.0


class AutonomousCheckpointManager:
    """
    Manages state checkpoints with automatic recovery capabilities.
    
    Features:
    - Automatic checkpoint creation at critical points
    - State consistency verification
    - Intelligent rollback on failures
    - Multi-level checkpoint hierarchy
    - Corruption detection and recovery
    """
    
    def __init__(self, checkpoint_dir: Optional[str] = None):
        """Initialize the checkpoint manager."""
        self.checkpoint_dir = checkpoint_dir or os.path.join(
            os.getcwd(), ".workflow_state", "checkpoints"
        )
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.current_checkpoint_id: Optional[str] = None
        self.max_checkpoints = 10
        self.auto_checkpoint_interval = timedelta(minutes=5)
        self.last_auto_checkpoint: Optional[datetime] = None
        
        self._load_checkpoints()
        logger.info(f"Autonomous Checkpoint Manager initialized at {self.checkpoint_dir}")
    
    def _load_checkpoints(self):
        """Load existing checkpoints from disk."""
        try:
            checkpoint_index = os.path.join(self.checkpoint_dir, "index.json")
            if os.path.exists(checkpoint_index):
                with open(checkpoint_index, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for cp_data in data.get('checkpoints', []):
                    checkpoint = Checkpoint.from_dict(cp_data)
                    self.checkpoints[checkpoint.checkpoint_id] = checkpoint
                
                self.current_checkpoint_id = data.get('current_checkpoint_id')
                logger.info(f"Loaded {len(self.checkpoints)} checkpoints")
        except Exception as e:
            logger.error(f"Failed to load checkpoints: {e}")
    
    def _save_checkpoint_index(self):
        """Save checkpoint index to disk."""
        try:
            checkpoint_index = os.path.join(self.checkpoint_dir, "index.json")
            data = {
                'checkpoints': [cp.to_dict() for cp in self.checkpoints.values()],
                'current_checkpoint_id': self.current_checkpoint_id,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(checkpoint_index, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint index: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash file {file_path}: {e}")
            return ""
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"cp_{timestamp}_{len(self.checkpoints)}"
    
    async def create_checkpoint(
        self,
        state: Dict[str, Any],
        files_to_track: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new checkpoint.
        
        Args:
            state: Current state to checkpoint
            files_to_track: List of file paths to include in checkpoint
            metadata: Optional metadata
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id()
        
        file_hashes = {}
        checkpoint_files_dir = os.path.join(self.checkpoint_dir, checkpoint_id)
        os.makedirs(checkpoint_files_dir, exist_ok=True)
        
        for file_path in files_to_track:
            if not os.path.exists(file_path):
                continue
            
            file_hash = self._calculate_file_hash(file_path)
            file_hashes[file_path] = file_hash
            
            backup_path = os.path.join(
                checkpoint_files_dir,
                os.path.basename(file_path)
            )
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                logger.warning(f"Could not backup file {file_path}: {e}")
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(),
            state_snapshot=state.copy(),
            file_hashes=file_hashes,
            metadata=metadata or {}
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        self.current_checkpoint_id = checkpoint_id
        
        self._cleanup_old_checkpoints()
        self._save_checkpoint_index()
        
        logger.info(f"Created checkpoint {checkpoint_id} with {len(file_hashes)} files")
        return checkpoint_id
    
    async def auto_checkpoint_if_needed(
        self,
        state: Dict[str, Any],
        files_to_track: List[str],
        force: bool = False
    ) -> Optional[str]:
        """
        Automatically create checkpoint if interval has passed.
        
        Args:
            state: Current state
            files_to_track: Files to track
            force: Force checkpoint creation
            
        Returns:
            Checkpoint ID if created, None otherwise
        """
        if not force:
            if self.last_auto_checkpoint:
                elapsed = datetime.now() - self.last_auto_checkpoint
                if elapsed < self.auto_checkpoint_interval:
                    return None
        
        checkpoint_id = await self.create_checkpoint(
            state,
            files_to_track,
            metadata={'auto_created': True}
        )
        
        self.last_auto_checkpoint = datetime.now()
        return checkpoint_id
    
    async def verify_checkpoint(self, checkpoint_id: str) -> Tuple[bool, List[str]]:
        """
        Verify checkpoint integrity.
        
        Args:
            checkpoint_id: Checkpoint to verify
            
        Returns:
            Tuple of (is_valid, errors)
        """
        if checkpoint_id not in self.checkpoints:
            return False, [f"Checkpoint {checkpoint_id} not found"]
        
        checkpoint = self.checkpoints[checkpoint_id]
        errors = []
        
        checkpoint_files_dir = os.path.join(self.checkpoint_dir, checkpoint_id)
        if not os.path.exists(checkpoint_files_dir):
            errors.append(f"Checkpoint directory missing: {checkpoint_files_dir}")
            checkpoint.is_valid = False
            return False, errors
        
        for file_path, expected_hash in checkpoint.file_hashes.items():
            backup_path = os.path.join(
                checkpoint_files_dir,
                os.path.basename(file_path)
            )
            
            if not os.path.exists(backup_path):
                errors.append(f"Backup file missing: {backup_path}")
                continue
            
            actual_hash = self._calculate_file_hash(backup_path)
            if actual_hash != expected_hash:
                errors.append(f"Hash mismatch for {file_path}")
        
        is_valid = len(errors) == 0
        checkpoint.is_valid = is_valid
        
        if not is_valid:
            logger.warning(f"Checkpoint {checkpoint_id} verification failed: {errors}")
        
        return is_valid, errors
    
    async def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        restore_files: bool = True,
        restore_state: bool = True
    ) -> RecoveryResult:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            restore_files: Whether to restore files
            restore_state: Whether to restore state
            
        Returns:
            Recovery result
        """
        start_time = datetime.now()
        
        if checkpoint_id not in self.checkpoints:
            return RecoveryResult(
                success=False,
                checkpoint_id=checkpoint_id,
                files_restored=0,
                state_restored=False,
                errors=[f"Checkpoint {checkpoint_id} not found"]
            )
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        is_valid, errors = await self.verify_checkpoint(checkpoint_id)
        if not is_valid:
            return RecoveryResult(
                success=False,
                checkpoint_id=checkpoint_id,
                files_restored=0,
                state_restored=False,
                errors=errors
            )
        
        result = RecoveryResult(
            success=True,
            checkpoint_id=checkpoint_id,
            files_restored=0,
            state_restored=False
        )
        
        if restore_files:
            checkpoint_files_dir = os.path.join(self.checkpoint_dir, checkpoint_id)
            
            for file_path in checkpoint.file_hashes.keys():
                backup_path = os.path.join(
                    checkpoint_files_dir,
                    os.path.basename(file_path)
                )
                
                if not os.path.exists(backup_path):
                    result.errors.append(f"Backup missing: {backup_path}")
                    continue
                
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    shutil.copy2(backup_path, file_path)
                    result.files_restored += 1
                except Exception as e:
                    result.errors.append(f"Failed to restore {file_path}: {e}")
        
        if restore_state:
            result.state_restored = True
        
        checkpoint.recovery_count += 1
        self.current_checkpoint_id = checkpoint_id
        
        result.success = len(result.errors) == 0
        result.recovery_time = (datetime.now() - start_time).total_seconds()
        
        self._save_checkpoint_index()
        
        logger.info(
            f"Rollback to {checkpoint_id}: "
            f"{result.files_restored} files restored, "
            f"state restored: {result.state_restored}"
        )
        
        return result
    
    async def auto_recover_on_failure(
        self,
        current_state: Dict[str, Any],
        error: Exception
    ) -> Optional[RecoveryResult]:
        """
        Automatically recover from failure using best checkpoint.
        
        Args:
            current_state: Current (failed) state
            error: The error that occurred
            
        Returns:
            Recovery result if recovery attempted, None otherwise
        """
        if not self.checkpoints:
            logger.warning("No checkpoints available for auto-recovery")
            return None
        
        valid_checkpoints = [
            cp for cp in self.checkpoints.values()
            if cp.is_valid and cp.recovery_count < 3
        ]
        
        if not valid_checkpoints:
            logger.warning("No valid checkpoints available for recovery")
            return None
        
        best_checkpoint = max(valid_checkpoints, key=lambda cp: cp.timestamp)
        
        logger.info(f"Auto-recovering to checkpoint {best_checkpoint.checkpoint_id}")
        
        result = await self.rollback_to_checkpoint(
            best_checkpoint.checkpoint_id,
            restore_files=True,
            restore_state=True
        )
        
        return result
    
    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints beyond max limit."""
        if len(self.checkpoints) <= self.max_checkpoints:
            return
        
        sorted_checkpoints = sorted(
            self.checkpoints.values(),
            key=lambda cp: cp.timestamp
        )
        
        checkpoints_to_remove = sorted_checkpoints[:-self.max_checkpoints]
        
        for checkpoint in checkpoints_to_remove:
            checkpoint_dir = os.path.join(self.checkpoint_dir, checkpoint.checkpoint_id)
            try:
                if os.path.exists(checkpoint_dir):
                    shutil.rmtree(checkpoint_dir)
                del self.checkpoints[checkpoint.checkpoint_id]
                logger.debug(f"Removed old checkpoint {checkpoint.checkpoint_id}")
            except Exception as e:
                logger.error(f"Failed to remove checkpoint {checkpoint.checkpoint_id}: {e}")
    
    def get_checkpoint_history(self) -> List[Dict[str, Any]]:
        """Get checkpoint history."""
        return [
            {
                'checkpoint_id': cp.checkpoint_id,
                'timestamp': cp.timestamp.isoformat(),
                'files_tracked': len(cp.file_hashes),
                'is_valid': cp.is_valid,
                'recovery_count': cp.recovery_count,
                'metadata': cp.metadata
            }
            for cp in sorted(self.checkpoints.values(), key=lambda c: c.timestamp, reverse=True)
        ]
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get state from current checkpoint."""
        if not self.current_checkpoint_id:
            return None
        
        checkpoint = self.checkpoints.get(self.current_checkpoint_id)
        if checkpoint:
            return checkpoint.state_snapshot.copy()
        
        return None


def create_autonomous_checkpoint_manager(checkpoint_dir: Optional[str] = None) -> AutonomousCheckpointManager:
    """Factory function to create autonomous checkpoint manager."""
    return AutonomousCheckpointManager(checkpoint_dir=checkpoint_dir)
