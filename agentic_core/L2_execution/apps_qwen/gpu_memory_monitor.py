"""GPU Memory Monitor for Qwen vLLM Optimization.

Provides real-time GPU memory monitoring to dynamically adjust
batch sizes and concurrency limits based on available VRAM.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GPUMemoryInfo:
    """GPU memory snapshot."""
    total_mb: float
    used_mb: float
    free_mb: float
    utilization_percent: float
    timestamp: float


@dataclass(frozen=True)
class GPURecommendation:
    """Recommendations based on GPU memory state."""
    batch_size: int
    max_concurrent: int
    should_throttle: bool
    should_cooldown: bool
    free_mb: float


class GPUMemoryMonitor:
    """Monitors GPU memory and provides dynamic optimization recommendations.

    Monitors:
    - Total/used/free VRAM
    - GPU utilization
    - Memory pressure thresholds

    Provides:
    - Dynamic batch size adjustment
    - Concurrency limit tuning
    - Throttling recommendations
    """

    # Memory pressure thresholds (percentages)
    THRESHOLD_LOW = 50.0      # Normal operation
    THRESHOLD_MEDIUM = 75.0   # Reduce batch sizes
    THRESHOLD_HIGH = 85.0     # Throttle new requests
    THRESHOLD_CRITICAL = 95.0 # Emergency cooldown

    def __init__(
        self,
        check_interval_sec: float = 5.0,
        min_batch_size: int = 1,
        max_batch_size: int = 16,
        min_concurrent: int = 1,
        max_concurrent: int = 16,
    ):
        self.check_interval_sec = check_interval_sec
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.min_concurrent = min_concurrent
        self.max_concurrent = max_concurrent

        self._history: list[GPUMemoryInfo] = []
        self._max_history_len = 100
        self._callbacks: list[Callable[[GPUMemoryInfo], None]] = []
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False

    def start(self) -> None:
        """Start background monitoring."""
        if not self._running:
            self._running = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("GPU memory monitor started")

    def stop(self) -> None:
        """Stop background monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()

    async def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                info = self._get_gpu_memory()
                if info:
                    self._history.append(info)
                    if len(self._history) > self._max_history_len:
                        self._history.pop(0)

                    # Notify callbacks
                    for callback in self._callbacks:
                        try:
                            callback(info)
                        except Exception as e:
                            logger.error("GPU monitor callback error: %s", e)

                await asyncio.sleep(self.check_interval_sec)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("GPU monitor loop error: %s", e)
                await asyncio.sleep(self.check_interval_sec)

    def _get_gpu_memory(self) -> Optional[GPUMemoryInfo]:
        """Get current GPU memory info via nvidia-smi."""
        try:
            import subprocess

            # Query memory info
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.used,memory.free,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                if len(parts) >= 4:
                    total = float(parts[0].strip())
                    used = float(parts[1].strip())
                    free = float(parts[2].strip())
                    util = float(parts[3].strip())

                    return GPUMemoryInfo(
                        total_mb=total,
                        used_mb=used,
                        free_mb=free,
                        utilization_percent=util,
                        timestamp=time.time(),
                    )
        except Exception as e:
            logger.debug("Failed to get GPU memory: %s", e)

        return None

    def get_current_memory(self) -> Optional[GPUMemoryInfo]:
        """Get current GPU memory snapshot."""
        if self._history:
            return self._history[-1]
        return self._get_gpu_memory()

    def get_recommendations(self) -> GPURecommendation:
        """Get optimization recommendations based on current GPU state."""
        info = self.get_current_memory()

        if not info:
            # No GPU info available, use conservative defaults
            return GPURecommendation(
                batch_size=2,
                max_concurrent=4,
                should_throttle=True,
                should_cooldown=False,
                free_mb=0,
            )

        used_percent = (info.used_mb / info.total_mb) * 100 if info.total_mb > 0 else 0

        # Determine batch size based on memory pressure
        if used_percent >= self.THRESHOLD_CRITICAL:
            batch_size = self.min_batch_size
            max_concurrent = self.min_concurrent
            should_throttle = True
            should_cooldown = True
        elif used_percent >= self.THRESHOLD_HIGH:
            batch_size = max(self.min_batch_size, self.max_batch_size // 4)
            max_concurrent = max(self.min_concurrent, self.max_concurrent // 4)
            should_throttle = True
            should_cooldown = False
        elif used_percent >= self.THRESHOLD_MEDIUM:
            batch_size = max(self.min_batch_size, self.max_batch_size // 2)
            max_concurrent = max(self.min_concurrent, self.max_concurrent // 2)
            should_throttle = False
            should_cooldown = False
        else:
            batch_size = self.max_batch_size
            max_concurrent = self.max_concurrent
            should_throttle = False
            should_cooldown = False

        return GPURecommendation(
            batch_size=batch_size,
            max_concurrent=max_concurrent,
            should_throttle=should_throttle,
            should_cooldown=should_cooldown,
            free_mb=info.free_mb,
        )

    def register_callback(self, callback: Callable[[GPUMemoryInfo], None]) -> None:
        """Register callback for memory updates."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[GPUMemoryInfo], None]) -> None:
        """Unregister callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get_metrics(self) -> dict[str, Any]:
        """Get monitoring metrics."""
        if not self._history:
            return {"status": "no_data"}

        recent = self._history[-10:]  # Last 10 samples
        avg_util = sum(i.utilization_percent for i in recent) / len(recent)
        avg_free = sum(i.free_mb for i in recent) / len(recent)

        return {
            "status": "active" if self._running else "inactive",
            "samples_collected": len(self._history),
            "avg_gpu_utilization": avg_util,
            "avg_free_mb": avg_free,
            "current": self._history[-1].__dict__ if self._history else None,
        }


# Singleton monitor instance
_gpu_monitor: Optional[GPUMemoryMonitor] = None


def get_gpu_monitor() -> GPUMemoryMonitor:
    """Get or create singleton GPU memory monitor."""
    global _gpu_monitor
    if _gpu_monitor is None:
        _gpu_monitor = GPUMemoryMonitor()
    return _gpu_monitor


def stop_gpu_monitor() -> None:
    """Stop singleton GPU memory monitor."""
    global _gpu_monitor
    if _gpu_monitor:
        _gpu_monitor.stop()
        _gpu_monitor = None


__all__ = [
    "GPUMemoryInfo",
    "GPURecommendation",
    "GPUMemoryMonitor",
    "get_gpu_monitor",
    "stop_gpu_monitor",
]
