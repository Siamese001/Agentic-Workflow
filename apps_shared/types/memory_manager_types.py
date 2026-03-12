"""Memory Manager - Controls memory usage and prevents unbounded growth.

This module provides memory bounds enforcement, context pruning, and
monitoring to prevent memory leaks and OOM errors.
"""
import gc
import logging
import sys
import threading
import time
import tracemalloc
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any
import psutil
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class PruningStrategy(Enum):
    """Strategies for pruning context data."""
    LRU = 'lru'
    FIFO = 'fifo'
    SIZE_BASED = 'size_based'
    PRIORITY = 'priority'

@dataclass
class MemoryLimits:
    """configuration for memory limits."""
    max_context_size: int = 10 * 1024 * 1024
    max_context_items: int = 1000
    max_string_length: int = 10000
    max_list_size: int = 100
    max_dict_size: int = 100
    max_memory_mb: float = 512.0
    gc_threshold: float = 0.8

@dataclass
class ContextItem:
    """Item in context with metadata."""
    key: str
    value: Any
    size_bytes: int
    last_accessed: float
    priority: int = 0
    access_count: int = 0

class MemoryManager:
    """Manages memory usage and enforces limits."""

    def __init__(self, name: str='default', limits: MemoryLimits | None=None):
        """Initialize the memory manager.

        Args:
            name: Manager name for logging
            limits: Memory limits configuration
        """
        self.name = name
        self.limits = limits or MemoryLimits()
        self._context: OrderedDict[str, ContextItem] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {'total_size': 0, 'item_count': 0, 'pruned_count': 0, 'gc_count': 0, 'memory_violations': 0}
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()
        logger.debug(f'Initialized MemoryManager: {name}')

    # guardian: allow-magic-config
    def start_monitoring(self, interval_seconds: float=5.0) -> None:
        """Start memory monitoring.

        Args:
            interval_seconds: Monitoring interval
        """
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,), daemon=True)
        self._monitor_thread.start()
        logger.info(f'Started memory monitoring for {self.name}')

    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=DEFAULT_TIMEOUT)
        logger.info(f'Stopped memory monitoring for {self.name}')

    def add_context(self, key: str, value: Any, priority: int=0, max_size: int | None=None) -> bool:
        """Add an item to context with size limits.

        Args:
            key: Context key
            value: Context value
            priority: Priority for pruning
            max_size: Maximum size for this item

        Returns:
            True if added successfully
        """
        sanitized_value = self._sanitize_value(value, max_size)
        size_bytes = self._calculate_size(sanitized_value)
        with self._lock:
            self._ensure_capacity(size_bytes)
            if key in self._context:
                old_item = self._context[key]
                self._stats['total_size'] -= old_item.size_bytes
                self._stats['item_count'] -= 1
            item = ContextItem(key=key, value=sanitized_value, size_bytes=size_bytes, last_accessed=time.time(), priority=priority)
            self._context[key] = item
            self._context.move_to_end(key)
            self._stats['total_size'] += size_bytes
            self._stats['item_count'] += 1
            self._check_memory_limits()
            return True

    def get_context(self, key: str, default: Any=None) -> Any:
        """Get a context item.

        Args:
            key: Context key
            default: Default value if not found

        Returns:
            Context value or default
        """
        with self._lock:
            if key in self._context:
                item = self._context[key]
                item.last_accessed = time.time()
                item.access_count += 1
                self._context.move_to_end(key)
                return item.value
            return default

    def remove_context(self, key: str) -> bool:
        """Remove a context item.

        Args:
            key: Context key

        Returns:
            True if removed
        """
        with self._lock:
            if key in self._context:
                item = self._context.pop(key)
                self._stats['total_size'] -= item.size_bytes
                self._stats['item_count'] -= 1
                return True
            return False

    def prune_context(self, strategy: PruningStrategy=PruningStrategy.LRU, target_size: int | None=None) -> int:
        """Prune context items based on strategy.

        Args:
            strategy: Pruning strategy
            target_size: Target size to achieve

        Returns:
            Number of items pruned
        """
        with self._lock:
            if not self._context:
                return 0
            target = target_size or int(self.limits.max_context_size * 0.8)
            pruned = 0
            if strategy == PruningStrategy.LRU:
                while self._stats['total_size'] > target and self._context:
                    key, item = self._context.popitem(last=False)
                    self._stats['total_size'] -= item.size_bytes
                    self._stats['item_count'] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.FIFO:
                while self._stats['total_size'] > target and self._context:
                    key, item = self._context.popitem(last=False)
                    self._stats['total_size'] -= item.size_bytes
                    self._stats['item_count'] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.SIZE_BASED:
                items = sorted(self._context.values(), key=lambda x: x.size_bytes, reverse=True)
                for item in items:
                    if self._stats['total_size'] <= target:
                        break
                    del self._context[item.key]
                    self._stats['total_size'] -= item.size_bytes
                    self._stats['item_count'] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.PRIORITY:
                items = sorted(self._context.values(), key=lambda x: x.priority)
                for item in items:
                    if self._stats['total_size'] <= target:
                        break
                    del self._context[item.key]
                    self._stats['total_size'] -= item.size_bytes
                    self._stats['item_count'] -= 1
                    pruned += 1
            self._stats['pruned_count'] += pruned
            logger.debug(f'Pruned {pruned} items using {strategy.value} strategy')
            return pruned

    def clear_context(self) -> None:
        """Clear all context data."""
        with self._lock:
            self._context.clear()
            self._stats['total_size'] = 0
            self._stats['item_count'] = 0
            logger.debug('Cleared all context data')

    def _sanitize_value(self, value: Any, max_size: int | None=None) -> Any:
        """Sanitize a value to prevent memory issues.

        Args:
            value: Value to sanitize
            max_size: Maximum size for collections

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            max_len = max_size or self.limits.max_string_length
            if len(value) > max_len:
                logger.warning(f'Truncated string from {len(value)} to {max_len} characters')
                return value[:max_len]
        elif isinstance(value, list):
            max_len = max_size or self.limits.max_list_size
            if len(value) > max_len:
                logger.warning(f'Truncated list from {len(value)} to {max_len} items')
                return value[:max_len]
        elif isinstance(value, dict):
            max_len = max_size or self.limits.max_dict_size
            if len(value) > max_len:
                logger.warning(f'Truncated dict from {len(value)} to {max_len} items')
                return dict(list(value.items())[:max_len])
        return value

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of a value.

        Args:
            value: Value to measure

        Returns:
            Size in bytes
        """
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, list | tuple):
            return sum((self._calculate_size(v) for v in value)) + 64
        elif isinstance(value, dict):
            return sum((self._calculate_size(k) + self._calculate_size(v) for k, v in value.items())) + 64
        else:
            return sys.getsizeof(value)

    def _ensure_capacity(self, required_size: int) -> None:
        """Ensure enough capacity for new item.

        Args:
            required_size: Size of item to add
        """
        while self._stats['item_count'] >= self.limits.max_context_items and self._context:
            self.prune_context(PruningStrategy.LRU, target_size=self.limits.max_context_size - required_size)
        while self._stats['total_size'] + required_size > self.limits.max_context_size and self._context:
            self.prune_context(PruningStrategy.LRU, target_size=self.limits.max_context_size - required_size)

    def _check_memory_limits(self) -> None:
        """Check if process memory limits are exceeded."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > self.limits.max_memory_mb:
                self._stats['memory_violations'] += 1
                logger.warning(f'Memory limit exceeded: {memory_mb:.1f}MB > {self.limits.max_memory_mb}MB')
                self.prune_context(PruningStrategy.SIZE_BASED, target_size=int(self.limits.max_context_size * 0.5))
                gc.collect()
                self._stats['gc_count'] += 1
            elif memory_mb > self.limits.max_memory_mb * self.limits.gc_threshold:
                gc.collect()
                self._stats['gc_count'] += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_loop(self, interval_seconds: float) -> None:
        """Background monitoring loop.

        Args:
            interval_seconds: Monitoring interval
        """
        while self._monitoring:
            try:
                self._check_memory_limits()
                time.sleep(interval_seconds)
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f'Memory monitoring error: {e}')

    def get_stats(self) -> dict[str, Any]:
        """Get memory manager statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = self._stats.copy()
            try:
                process = psutil.Process()
                stats['process_memory_mb'] = process.memory_info().rss / 1024 / 1024
                stats['process_memory_percent'] = process.memory_percent()
            except Exception:
                raise
                stats['process_memory_mb'] = 0
                stats['process_memory_percent'] = 0
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                stats['traced_memory_mb'] = current / 1024 / 1024
                stats['peak_memory_mb'] = peak / 1024 / 1024
            return stats

    def get_memory_report(self) -> str:
        """Get a formatted memory report.

        Returns:
            Memory report string
        """
        stats = self.get_stats()
        report = f"\nMemory Manager Report: {self.name}\n========================================\nContext Items: {stats['item_count']}\nContext Size: {stats['total_size'] / 1024 / 1024:.2f} MB\nItems Pruned: {stats['pruned_count']}\nGC Runs: {stats['gc_count']}\nMemory Violations: {stats['memory_violations']}\nProcess Memory: {stats.get('process_memory_mb', 0):.2f} MB\nMemory Percent: {stats.get('process_memory_percent', 0):.1f}%\n"
        if 'traced_memory_mb' in stats:
            report += f"Traced Memory: {stats['traced_memory_mb']:.2f} MB\n"
            report += f"Peak Memory: {stats['peak_memory_mb']:.2f} MB\n"
        return report
_managers: dict[str, MemoryManager] = {}
_manager_lock = threading.Lock()

def get_memory_manager(name: str='default', limits: MemoryLimits | None=None) -> MemoryManager:
    """Get or create a memory manager.

    Args:
        name: Manager name
        limits: Optional memory limits

    Returns:
        MemoryManager instance
    """
    with _manager_lock:
        if name not in _managers:
            manager = MemoryManager(name, limits)
            _managers[name] = manager
        return _managers[name]

def cleanup_all_managers() -> None:
    """Cleanup all memory managers."""
    with _manager_lock:
        for manager in _managers.values():
            manager.stop_monitoring()
            manager.clear_context()
        _managers.clear()

@contextmanager
def memory_bound(manager: MemoryManager, max_memory_mb: float):
    """Context manager for memory-bound operations.

    Args:
        manager: Memory manager to use
        max_memory_mb: Maximum memory for operation
    """
    initial_memory = manager.get_stats().get('process_memory_mb', 0)
    try:
        yield
    finally:
        current_memory = manager.get_stats().get('process_memory_mb', 0)
        if current_memory - initial_memory > max_memory_mb:
            logger.warning(f'Operation exceeded memory bound: {current_memory - initial_memory:.1f}MB')
            manager.prune_context(PruningStrategy.SIZE_BASED)
