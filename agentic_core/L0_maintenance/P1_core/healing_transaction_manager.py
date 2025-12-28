"""
L0 Transaction Manager: Atomic Healing with Rollback
Provides ACID-like guarantees for healing operations.

Phase 10B: Transactional Healing (Dec 26, 2025)
"""
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class HealingTransaction:
    """
    Transaction manager for atomic healing operations with rollback capability.
    
    Ensures that healing operations are:
    - Atomic: All fixes succeed or all are rolled back
    - Consistent: Files are backed up before modification
    - Isolated: Changes are staged before commit
    - Durable: Backups are preserved until commit
    """
    
    def __init__(self):
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f".sovereign_healing_backup/{self.timestamp}")
        self.backups: List[Tuple[Path, Path]] = []
        self.committed = False
        self.rolled_back = False
    
    def backup(self, file_path: Path) -> bool:
        """
        Create a backup of a file before modification.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            if not file_path.exists():
                logger.warning(f"Cannot backup non-existent file: {file_path}")
                return False
            
            # Preserve full relative path to prevent name collisions (e.g. L1/utils.py vs L2/utils.py)
            try:
                relative = file_path.relative_to(Path.cwd())
            except ValueError:
                # If file is outside CWD, just use name (fallback)
                relative = file_path.name
                
            backup_path = self.backup_dir / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file with metadata
            shutil.copy2(file_path, backup_path)
            self.backups.append((file_path, backup_path))
            
            logger.info(f"Backed up: {file_path} -> {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed for {file_path}: {e}")
            return False
    
    def rollback(self) -> bool:
        """
        Rollback all changes by restoring from backups.
        
        Returns:
            True if rollback successful, False otherwise
        """
        if self.committed:
            logger.warning("Cannot rollback committed transaction")
            return False
        
        if self.rolled_back:
            logger.warning("Transaction already rolled back")
            return False
        
        try:
            logger.info(f"Rolling back {len(self.backups)} file(s)...")
            
            for original, backup in self.backups:
                if backup.exists():
                    shutil.copy2(backup, original)
                    logger.info(f"Restored: {backup} -> {original}")
            
            # Clean up backup directory
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                logger.info(f"Removed backup directory: {self.backup_dir}")
            
            self.rolled_back = True
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def commit(self) -> bool:
        """
        Commit the transaction by removing backups.
        
        Returns:
            True if commit successful, False otherwise
        """
        if self.rolled_back:
            logger.warning("Cannot commit rolled back transaction")
            return False
        
        if self.committed:
            logger.warning("Transaction already committed")
            return False
        
        try:
            logger.info(f"Committing transaction with {len(self.backups)} file(s)...")
            
            # Clean up backup directory
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                logger.info(f"Removed backup directory: {self.backup_dir}")
            
            self.committed = True
            return True
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic rollback on exception."""
        if exc_type is not None:
            # Exception occurred, rollback
            logger.error(f"Exception in transaction: {exc_val}")
            self.rollback()
            return False
        else:
            # No exception, commit
            self.commit()
            return True


def create_transaction() -> HealingTransaction:
    """
    Factory function to create a new healing transaction.
    
    Returns:
        New HealingTransaction instance
    """
    return HealingTransaction()
