"""Transaction Manager V1 Shim - Minimal stub for deprecated transactional state manager.

This module provides a minimal stub implementation of the deprecated transactional
state manager for backward compatibility with legacy systems.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum
import threading
import uuid

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """States of a transaction."""
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class IsolationLevel(Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class Transaction:
    """Legacy transaction representation."""
    transaction_id: str
    state: TransactionState
    isolation_level: IsolationLevel
    start_time: datetime
    operations: List[Dict[str, Any]] = field(default_factory=list)
    savepoints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionConfig:
    """Configuration for transaction manager."""
    default_isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    timeout_seconds: float = 30.0
    max_active_transactions: int = 100
    enable_savepoints: bool = True
    auto_rollback_on_error: bool = True


class TransactionManagerV1Shim:
    """Shim implementation of deprecated transaction manager v1."""
    
    def __init__(self, config: Optional[TransactionConfig] = None):
        self.config = config or TransactionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._active_transactions: Dict[str, Transaction] = {}
        self._transaction_stack: List[str] = []
        self._lock = threading.Lock()
        self._state_storage: Dict[str, Any] = {}
        self._backup_storage: Dict[str, Any] = {}
    
    def begin_transaction(self, isolation_level: Optional[IsolationLevel] = None) -> str:
        """Begin a new transaction.
        
        Args:
            isolation_level: Optional isolation level
            
        Returns:
            str: Transaction ID
        """
        with self._lock:
            # Check limit
            if len(self._active_transactions) >= self.config.max_active_transactions:
                raise RuntimeError("Maximum active transactions reached")
            
            # Create transaction
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                transaction_id=transaction_id,
                state=TransactionState.ACTIVE,
                isolation_level=isolation_level or self.config.default_isolation_level,
                start_time=datetime.utcnow()
            )
            
            self._active_transactions[transaction_id] = transaction
            self._transaction_stack.append(transaction_id)
            
            # Backup current state
            self._backup_storage[transaction_id] = self._state_storage.copy()
            
            self.logger.info(f"Began transaction: {transaction_id}")
            return transaction_id
    
    def commit_transaction(self, transaction_id: Optional[str] = None) -> bool:
        """Commit a transaction.
        
        Args:
            transaction_id: Transaction ID (uses current if not provided)
            
        Returns:
            bool: True if committed successfully
        """
        with self._lock:
            if transaction_id is None:
                if not self._transaction_stack:
                    raise RuntimeError("No active transaction")
                transaction_id = self._transaction_stack[-1]
            
            transaction = self._active_transactions.get(transaction_id)
            if not transaction:
                raise RuntimeError(f"Transaction not found: {transaction_id}")
            
            if transaction.state != TransactionState.ACTIVE:
                raise RuntimeError(f"Transaction not active: {transaction_id}")
            
            # Commit transaction
            transaction.state = TransactionState.COMMITTED
            
            # Remove from stack
            if transaction_id in self._transaction_stack:
                self._transaction_stack.remove(transaction_id)
            
            # Clean up backup
            if transaction_id in self._backup_storage:
                del self._backup_storage[transaction_id]
            
            self.logger.info(f"Committed transaction: {transaction_id}")
            return True
    
    def rollback_transaction(self, transaction_id: Optional[str] = None) -> bool:
        """Rollback a transaction.
        
        Args:
            transaction_id: Transaction ID (uses current if not provided)
            
        Returns:
            bool: True if rolled back successfully
        """
        with self._lock:
            if transaction_id is None:
                if not self._transaction_stack:
                    raise RuntimeError("No active transaction")
                transaction_id = self._transaction_stack[-1]
            
            transaction = self._active_transactions.get(transaction_id)
            if not transaction:
                raise RuntimeError(f"Transaction not found: {transaction_id}")
            
            if transaction.state != TransactionState.ACTIVE:
                raise RuntimeError(f"Transaction not active: {transaction_id}")
            
            # Restore state from backup
            if transaction_id in self._backup_storage:
                self._state_storage = self._backup_storage[transaction_id].copy()
                del self._backup_storage[transaction_id]
            
            # Mark as rolled back
            transaction.state = TransactionState.ROLLED_BACK
            
            # Remove from stack
            if transaction_id in self._transaction_stack:
                self._transaction_stack.remove(transaction_id)
            
            self.logger.info(f"Rolled back transaction: {transaction_id}")
            return True
    
    def create_savepoint(self, name: str, transaction_id: Optional[str] = None) -> bool:
        """Create a savepoint.
        
        Args:
            name: Savepoint name
            transaction_id: Transaction ID
            
        Returns:
            bool: True if created successfully
        """
        if not self.config.enable_savepoints:
            return False
        
        with self._lock:
            if transaction_id is None:
                if not self._transaction_stack:
                    raise RuntimeError("No active transaction")
                transaction_id = self._transaction_stack[-1]
            
            transaction = self._active_transactions.get(transaction_id)
            if not transaction:
                raise RuntimeError(f"Transaction not found: {transaction_id}")
            
            # Create savepoint
            transaction.savepoints[name] = {
                "state": self._state_storage.copy(),
                "operations_count": len(transaction.operations),
                "created_at": datetime.utcnow()
            }
            
            self.logger.debug(f"Created savepoint {name} in transaction {transaction_id}")
            return True
    
    def rollback_to_savepoint(self, name: str, transaction_id: Optional[str] = None) -> bool:
        """Rollback to a savepoint.
        
        Args:
            name: Savepoint name
            transaction_id: Transaction ID
            
        Returns:
            bool: True if rolled back successfully
        """
        if not self.config.enable_savepoints:
            return False
        
        with self._lock:
            if transaction_id is None:
                if not self._transaction_stack:
                    raise RuntimeError("No active transaction")
                transaction_id = self._transaction_stack[-1]
            
            transaction = self._active_transactions.get(transaction_id)
            if not transaction:
                raise RuntimeError(f"Transaction not found: {transaction_id}")
            
            # Get savepoint
            savepoint = transaction.savepoints.get(name)
            if not savepoint:
                raise RuntimeError(f"Savepoint not found: {name}")
            
            # Restore state
            self._state_storage = savepoint["state"].copy()
            
            # Remove later savepoints
            to_remove = []
            for sp_name, sp_data in transaction.savepoints.items():
                if sp_data["created_at"] > savepoint["created_at"]:
                    to_remove.append(sp_name)
            
            for sp_name in to_remove:
                del transaction.savepoints[sp_name]
            
            self.logger.debug(f"Rolled back to savepoint {name} in transaction {transaction_id}")
            return True
    
    def get_transaction_state(self, transaction_id: str) -> Optional[TransactionState]:
        """Get transaction state.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Optional[TransactionState]: Transaction state
        """
        transaction = self._active_transactions.get(transaction_id)
        return transaction.state if transaction else None
    
    def set_state(self, key: str, value: Any, transaction_id: Optional[str] = None) -> None:
        """Set state value.
        
        Args:
            key: State key
            value: State value
            transaction_id: Transaction ID
        """
        with self._lock:
            if transaction_id is None:
                if self._transaction_stack:
                    transaction_id = self._transaction_stack[-1]
            
            if transaction_id:
                # Record operation
                transaction = self._active_transactions.get(transaction_id)
                if transaction and transaction.state == TransactionState.ACTIVE:
                    transaction.operations.append({
                        "type": "set",
                        "key": key,
                        "old_value": self._state_storage.get(key),
                        "new_value": value,
                        "timestamp": datetime.utcnow()
                    })
            
            # Set value
            self._state_storage[key] = value
    
    def get_state(self, key: str, transaction_id: Optional[str] = None) -> Any:
        """Get state value.
        
        Args:
            key: State key
            transaction_id: Transaction ID
            
        Returns:
            Any: State value
        """
        with self._lock:
            return self._state_storage.get(key)
    
    def delete_state(self, key: str, transaction_id: Optional[str] = None) -> bool:
        """Delete state value.
        
        Args:
            key: State key
            transaction_id: Transaction ID
            
        Returns:
            bool: True if deleted
        """
        with self._lock:
            if transaction_id is None:
                if self._transaction_stack:
                    transaction_id = self._transaction_stack[-1]
            
            if transaction_id:
                # Record operation
                transaction = self._active_transactions.get(transaction_id)
                if transaction and transaction.state == TransactionState.ACTIVE:
                    transaction.operations.append({
                        "type": "delete",
                        "key": key,
                        "old_value": self._state_storage.get(key),
                        "timestamp": datetime.utcnow()
                    })
            
            # Delete key
            if key in self._state_storage:
                del self._state_storage[key]
                return True
            
            return False
    
    def list_active_transactions(self) -> List[Transaction]:
        """List all active transactions.
        
        Returns:
            List[Transaction]: Active transactions
        """
        with self._lock:
            return [t for t in self._active_transactions.values() 
                   if t.state == TransactionState.ACTIVE]
    
    def cleanup_expired_transactions(self) -> int:
        """Clean up expired transactions.
        
        Returns:
            int: Number of cleaned up transactions
        """
        with self._lock:
            now = datetime.utcnow()
            expired = []
            
            for transaction_id, transaction in self._active_transactions.items():
                if transaction.state == TransactionState.ACTIVE:
                    elapsed = (now - transaction.start_time).total_seconds()
                    if elapsed > self.config.timeout_seconds:
                        # Auto rollback
                        self.rollback_transaction(transaction_id)
                        expired.append(transaction_id)
            
            self.logger.info(f"Cleaned up {len(expired)} expired transactions")
            return len(expired)


# Factory function for easy instantiation
def create_transaction_manager_v1(
    default_isolation_level: str = "read_committed",
    timeout_seconds: float = 30.0,
    **kwargs
) -> TransactionManagerV1Shim:
    """Create a configured transaction manager v1."""
    config = TransactionConfig(
        default_isolation_level=IsolationLevel(default_isolation_level),
        timeout_seconds=timeout_seconds,
        **kwargs
    )
    return TransactionManagerV1Shim(config)


# Global transaction manager instance
_global_manager = create_transaction_manager_v1()


def begin_transaction(isolation_level: Optional[str] = None) -> str:
    """Begin a new transaction.
    
    Args:
        isolation_level: Optional isolation level
        
    Returns:
        str: Transaction ID
    """
    if isolation_level:
        return _global_manager.begin_transaction(IsolationLevel(isolation_level))
    return _global_manager.begin_transaction()


def commit_transaction(transaction_id: Optional[str] = None) -> bool:
    """Commit a transaction.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        bool: True if committed successfully
    """
    return _global_manager.commit_transaction(transaction_id)


def rollback_transaction(transaction_id: Optional[str] = None) -> bool:
    """Rollback a transaction.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        bool: True if rolled back successfully
    """
    return _global_manager.rollback_transaction(transaction_id)


def transaction_state(key: str, value: Any) -> None:
    """Set state in current transaction.
    
    Args:
        key: State key
        value: State value
    """
    _global_manager.set_state(key, value)
