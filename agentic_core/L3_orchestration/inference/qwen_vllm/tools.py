from __future__ import annotations

from dataclasses import dataclass
import math
import threading
import time
from typing import Callable


@dataclass(frozen=True)
class GPUMemoryInfo:
    total_mb: int
    used_mb: int
    free_mb: int
    utilization_percent: float
    timestamp: float

    def __post_init__(self) -> None:
        if self.total_mb <= 0:
            raise ValueError("total_mb must be positive")
        if self.used_mb < 0:
            raise ValueError("used_mb must be non-negative")
        if self.free_mb < 0:
            raise ValueError("free_mb must be non-negative")
        if not 0.0 <= float(self.utilization_percent) <= 100.0:
            raise ValueError("utilization_percent must be between 0 and 100")


@dataclass(frozen=True)
class GPURecommendation:
    batch_size: int
    max_concurrent: int
    should_throttle: bool
    should_cooldown: bool
    free_mb: int

    def __post_init__(self) -> None:
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        if self.free_mb < 0:
            raise ValueError("free_mb must be non-negative")


class GPUMemoryMonitor:
    """Small runtime-safe monitor with deterministic fallback behavior.

    The monitor defaults to a static synthetic snapshot so it remains safe in test
    and CI environments without GPU APIs, but callers may inject a provider to
    supply live memory data.
    """

    def __init__(
        self,
        check_interval_sec: float = 5.0,
        min_batch_size: int = 1,
        max_batch_size: int = 16,
        metrics_provider: Callable[[], tuple[int, int] | GPUMemoryInfo | dict[str, int]] | None = None,
        default_total_mb: int = 16_384,
        target_headroom_mb: int = 2_048,
    ):
        self.check_interval_sec = max(0.0, float(check_interval_sec))
        self.min_batch_size = max(1, int(min_batch_size))
        self.max_batch_size = max(self.min_batch_size, int(max_batch_size))
        self.metrics_provider = metrics_provider
        self.default_total_mb = max(1, int(default_total_mb))
        self.target_headroom_mb = max(0, int(target_headroom_mb))
        self._lock = threading.Lock()
        self._last_snapshot: GPUMemoryInfo | None = None

    def _coerce_snapshot(
        self, payload: tuple[int, int] | GPUMemoryInfo | dict[str, int] | None
    ) -> GPUMemoryInfo:
        if isinstance(payload, GPUMemoryInfo):
            return payload

        total = self.default_total_mb
        used = total // 4
        timestamp = time.time()

        if isinstance(payload, tuple) and len(payload) == 2:
            total, used = payload
        elif isinstance(payload, dict):
            total = int(payload.get("total_mb", total))
            used = int(payload.get("used_mb", payload.get("used", used)))
            timestamp = float(payload.get("timestamp", timestamp))

        total = max(1, int(total))
        used = max(0, min(total, int(used)))
        free = max(0, total - used)
        utilization = (used / total) * 100.0 if total else 100.0
        return GPUMemoryInfo(
            total_mb=total,
            used_mb=used,
            free_mb=free,
            utilization_percent=max(0.0, min(100.0, utilization)),
            timestamp=timestamp,
        )

    def snapshot(self, force_refresh: bool = False) -> GPUMemoryInfo:
        now = time.time()
        with self._lock:
            if (
                not force_refresh
                and self._last_snapshot is not None
                and self.check_interval_sec > 0.0
                and (now - self._last_snapshot.timestamp) < self.check_interval_sec
            ):
                return self._last_snapshot

            payload = None
            if callable(self.metrics_provider):
                try:
                    payload = self.metrics_provider()
                except Exception:
                    payload = None

            snapshot = self._coerce_snapshot(payload)
            self._last_snapshot = snapshot
            return snapshot

    def recommend(self, info: GPUMemoryInfo | None = None) -> GPURecommendation:
        info = info or self.snapshot()

        total = max(1, info.total_mb)
        free_ratio = max(0.0, min(1.0, info.free_mb / total))
        effective_free = max(0, info.free_mb - self.target_headroom_mb)

        if effective_free <= 0:
            batch = self.min_batch_size
        else:
            spread = self.max_batch_size - self.min_batch_size
            batch = self.min_batch_size + int(math.floor(spread * free_ratio))
            batch = max(self.min_batch_size, min(self.max_batch_size, batch))

        max_concurrent = max(1, min(self.max_batch_size * 2, batch * 2))
        should_throttle = info.utilization_percent >= 85.0 or info.free_mb < self.target_headroom_mb
        should_cooldown = info.utilization_percent >= 95.0 or info.free_mb < max(
            512, self.target_headroom_mb // 2
        )

        return GPURecommendation(
            batch_size=batch,
            max_concurrent=max_concurrent,
            should_throttle=should_throttle,
            should_cooldown=should_cooldown,
            free_mb=info.free_mb,
        )


__all__ = ["GPUMemoryInfo", "GPUMemoryMonitor", "GPURecommendation"]
