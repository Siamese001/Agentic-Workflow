"""
State Management for Canon Validator

Provides atomic blackboard pattern with lease locking, health score tracking,
and regression guards to prevent race conditions during concurrent healing.
"""
from .blackboard import AtomicBlackboard, FileHealthScore, HealingLease
from .memory_manager import MemoryManager, get_memory_manager

__all__ = [
    'AtomicBlackboard',
    'FileHealthScore',
    'HealingLease',
    'MemoryManager',
    'get_memory_manager'
]
