from __future__ import annotations
import gc
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import json
import logging
import re
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)
memory_threshold_mb: Any = 100
snapshot_interval: Any = 60
max_snapshots: Any = 100

class MemorySnapshot:
    """A snapshot of memory usage at a point in time."""

    def __init__(self, label: str='') -> None:
        self.label = label
        self.timestamp = datetime.utcnow()
        self.total_allocated = 0
        self.total_peaked = 0
        self.current_allocated = 0
        self.current_peaked = 0
        self.top_allocations = []
        if tracemalloc.is_tracing():
            self.take_snapshot()

    def take_snapshot(self) -> Any:
        """Take a memory snapshot."""
        try:
            current, peak = tracemalloc.get_traced_memory()
            self.current_allocated = current
            self.current_peaked = peak
            snapshot: Any = tracemalloc.take_snapshot()
            self.top_allocations = snapshot.statistics('lineno')[:10]
        except Exception as e:
            LOGGER.error(f'Failed to take memory snapshot: {e}')

    def get_size_mb(self, size_bytes: int) -> float:
        """Convert bytes to megabytes."""
        return size_bytes / (1024 * 1024)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {'label': self.label, 'timestamp': self.timestamp.isoformat(), 'total_allocated_mb': self.get_size_mb(self.total_allocated), 'total_peaked_mb': self.get_size_mb(self.total_peaked), 'current_allocated_mb': self.get_size_mb(self.current_allocated), 'current_peaked_mb': self.get_size_mb(self.current_peaked), 'top_allocations': [{'file': str(stat.traceback[0].filename), 'line': stat.traceback[0].lineno, 'size_mb': self.get_size_mb(stat.size), 'count': stat.count} for stat in self.top_allocations[:5]]}

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class MemoryLeakDetectorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Detects memory leaks in the agentic system.

    Features:
    - Tracks memory usage across cycles
    - Compares snapshots to detect growth
    - Identifies allocation hotspots
    - Automatic garbage collection
    """

    def __init__(self) -> None:
        """Initialize the MemoryLeakDetectorAgent."""
        self.enabled = True
        self.snapshots: List[MemorySnapshot] = []
        self.cycle_snapshots: Dict[str, List[MemorySnapshot]] = {}
        self.current_cycle: Optional[str] = None
        if not tracemalloc.is_tracing():
            try:
                tracemalloc.start(25)
                LOGGER.info('Started tracemalloc')
            except Exception as e:
                LOGGER.error(f'Failed to start tracemalloc: {e}')
                self.enabled = False
        LOGGER.info('MemoryLeakDetectorAgent initialized')

    def start_cycle(self, cycle_id: str) -> Any:
        """
        Start monitoring a new cycle.

        Args:
            cycle_id: Identifier for the cycle
        """
        self.current_cycle = cycle_id
        self.cycle_snapshots[cycle_id] = []
        self.take_snapshot('cycle_start')
        gc.collect()
        LOGGER.info(f'Started memory monitoring for cycle {cycle_id}')

    def end_cycle(self, cycle_id: str=None) -> Any:
        """
        End monitoring for a cycle.

        Args:
            cycle_id: Cycle ID (uses current if None)
        """
        cycle_id: Any = cycle_id or self.current_cycle
        if not cycle_id:
            return
        self.take_snapshot('cycle_end')
        self._analyze_cycle(cycle_id)
        self.current_cycle = None
        LOGGER.info(f'Ended memory monitoring for cycle {cycle_id}')

    def take_snapshot(self, label: str='') -> Any:
        """
        Take a memory snapshot.

        Args:
            label: Label for the snapshot
        """
        if not self.enabled:
            return
        snapshot: Any = MemorySnapshot(label)
        self.snapshots.append(snapshot)
        if self.current_cycle:
            self.cycle_snapshots[self.current_cycle].append(snapshot)
        if len(self.snapshots) > MAX_SNAPSHOTS:
            self.snapshots = self.snapshots[-MAX_SNAPSHOTS:]
        LOGGER.debug(f'Memory snapshot: {label} - {snapshot.get_size_mb(snapshot.current_allocated):.1f}MB allocated')

    def _analyze_cycle(self, cycle_id: str):
        """
        Analyze memory usage for a cycle.

        Args:
            cycle_id: Cycle to analyze
        """
        if cycle_id not in self.cycle_snapshots:
            return
        snapshots = self.cycle_snapshots[cycle_id]
        if len(snapshots) < 2:
            return
        start = snapshots[0]
        end = snapshots[-1]
        growth_mb = end.get_size_mb(end.current_allocated) - start.get_size_mb(start.current_allocated)
        peak_growth_mb = end.get_size_mb(end.current_peaked) - start.get_size_mb(start.current_peaked)
        if growth_mb > MEMORY_THRESHOLD_MB:
            self._alert_memory_leak(cycle_id, growth_mb, peak_growth_mb, start, end)
        elif growth_mb > 50:
            LOGGER.warning(f'High memory growth in cycle {cycle_id}: {growth_mb:.1f}MB')
        LOGGER.info(f'Cycle {cycle_id} memory summary:')
        LOGGER.info(f'  Growth: {growth_mb:.1f}MB')
        LOGGER.info(f'  Peak growth: {peak_growth_mb:.1f}MB')
        LOGGER.info(f'  End usage: {end.get_size_mb(end.current_allocated):.1f}MB')

    def _alert_memory_leak(self, cycle_id: str, growth_mb: float, peak_growth_mb: float, start: MemorySnapshot, end: MemorySnapshot):
        """Alert about potential memory leak."""
        alert = {'type': 'MEMORY_LEAK_DETECTED', 'cycle_id': cycle_id, 'growth_mb': growth_mb, 'peak_growth_mb': peak_growth_mb, 'threshold_mb': MEMORY_THRESHOLD_MB, 'start_snapshot': start.to_dict(), 'end_snapshot': end.to_dict(), 'top_allocations': end.top_allocations[:5], 'timestamp': datetime.utcnow().isoformat()}
        LOGGER.error(f'[ALERT] MEMORY LEAK DETECTED in cycle {cycle_id}')
        LOGGER.error(f'  Growth: {growth_mb:.1f}MB (threshold: {MEMORY_THRESHOLD_MB}MB)')
        LOGGER.error(f'  Peak growth: {peak_growth_mb:.1f}MB')
        if end.top_allocations:
            LOGGER.error('  Top allocations:')
            for i, stat in enumerate(end.top_allocations[:3]):
                LOGGER.error(f'    {i + 1}. {stat.traceback[0].filename}:{stat.traceback[0].lineno} ({end.get_size_mb(stat.size):.1f}MB)')
        alert_file = Path('observability/alerts/memory_leaks.json')
        alert_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []
            alerts.append(alert)
            if len(alerts) > 50:
                alerts = alerts[-50:]
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            LOGGER.error(f'Failed to save memory leak alert: {e}')

    def get_current_usage(self) -> Dict:
        """Get current memory usage."""
        if not self.enabled or not self.snapshots:
            return {'enabled': False}
        latest: Any = self.snapshots[-1]
        return {'enabled': True, 'allocated_mb': latest.get_size_mb(latest.current_allocated), 'peaked_mb': latest.get_size_mb(latest.current_peaked), 'timestamp': latest.timestamp.isoformat()}

    def get_cycle_summary(self, cycle_id: str) -> Dict:
        """Get memory summary for a cycle."""
        if cycle_id not in self.cycle_snapshots:
            return {'error': 'Cycle not found'}
        snapshots: Any = self.cycle_snapshots[cycle_id]
        if not snapshots:
            return {'error': 'No snapshots for cycle'}
        start: Any = snapshots[0]
        end: Any = snapshots[-1]
        return {'cycle_id': cycle_id, 'snapshots_count': len(snapshots), 'growth_mb': end.get_size_mb(end.current_allocated) - start.get_size_mb(start.current_allocated), 'peak_growth_mb': end.get_size_mb(end.current_peaked) - start.get_size_mb(start.current_peaked), 'start_usage_mb': start.get_size_mb(start.current_allocated), 'end_usage_mb': end.get_size_mb(end.current_allocated), 'top_allocations': [{'file': str(stat.traceback[0].filename), 'line': stat.traceback[0].lineno, 'size_mb': end.get_size_mb(stat.size)} for stat in end.top_allocations[:5]]}

    def force_gc(self) -> Any:
        """Force garbage collection and take snapshot."""
        before: Any = self.get_current_usage()
        collected: Any = gc.collect()
        self.take_snapshot('after_gc')
        after: Any = self.get_current_usage()
        freed_mb: Any = before.get('allocated_mb', 0) - after.get('allocated_mb', 0)
        LOGGER.info(f'Garbage collection: collected {collected} objects, freed {freed_mb:.1f}MB')
        return {'objects_collected': collected, 'memory_freed_mb': freed_mb}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_memory_detector: Optional[MemoryLeakDetectorAgent] = None

def get_memory_detector() -> MemoryLeakDetectorAgent:
    """Get or create the global MemoryLeakDetectorAgent instance."""
    global _memory_detector
    if _memory_detector is None:
        _memory_detector = MemoryLeakDetectorAgent()
    return _memory_detector

def initialize_memory_detector() -> Any:
    """Initialize the MemoryLeakDetectorAgent system."""
    get_memory_detector()
    LOGGER.info('MemoryLeakDetectorAgent system initialized')

def start_memory_cycle(cycle_id: str) -> Any:
    """Start monitoring memory for a cycle."""
    detector: Any = get_memory_detector()
    detector.start_cycle(cycle_id)

def end_memory_cycle(cycle_id: str=None) -> Any:
    """End monitoring memory for a cycle."""
    detector: Any = get_memory_detector()
    detector.end_cycle(cycle_id)

def take_memory_snapshot(label: str='') -> Any:
    """Take a memory snapshot."""
    detector: Any = get_memory_detector()
    detector.take_snapshot(label)
