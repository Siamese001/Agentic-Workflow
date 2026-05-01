"""Baseline registry for G25 RuntimeAnomalyGate.

Stores per-task-class baselines with rolling-window exponential moving average
(EMA) updates. Persists to a JSON file via atomic write so the registry
survives process restarts.

Out of scope (see plan): SQLite/Redis backend, multi-tenant isolation.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

DEFAULT_ALPHA = 0.2
TRACKED_METRICS: tuple[str, ...] = (
    "tokens",
    "cost_usd",
    "latency_ms",
    "tool_count",
    "retry_count",
)


@dataclass(slots=True)
class Baseline:
    """Per-task-class rolling baseline."""

    task_class: str
    metrics: dict[str, float] = field(default_factory=dict)
    sample_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_class": self.task_class,
            "metrics": dict(self.metrics),
            "sample_count": self.sample_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Baseline":
        return cls(
            task_class=str(data["task_class"]),
            metrics={k: float(v) for k, v in (data.get("metrics") or {}).items()},
            sample_count=int(data.get("sample_count", 0)),
        )


class BaselineRegistry:
    """Persistent baseline store with EMA updates.

    Thread-safe via an internal RLock. Persistence uses atomic
    write-to-temp + rename so partial writes never corrupt the file.
    """

    def __init__(self, path: str | Path | None = None, alpha: float = DEFAULT_ALPHA) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError(f"alpha must be in (0, 1], got {alpha}")
        self._path = Path(path) if path else None
        self._alpha = alpha
        self._lock = RLock()
        self._baselines: dict[str, Baseline] = {}
        if self._path and self._path.exists():
            self._load()

    @property
    def alpha(self) -> float:
        return self._alpha

    def get(self, task_class: str) -> dict[str, float]:
        """Return a snapshot of the baseline metrics for the given task class."""
        with self._lock:
            b = self._baselines.get(task_class)
            return dict(b.metrics) if b else {}

    def has(self, task_class: str) -> bool:
        with self._lock:
            return task_class in self._baselines

    def update(self, task_class: str, observed: dict[str, float]) -> dict[str, float]:
        """Apply EMA update for tracked metrics. First sample seeds baseline.

        Returns the updated baseline metrics snapshot.
        """
        with self._lock:
            b = self._baselines.get(task_class)
            if b is None:
                b = Baseline(task_class=task_class)
                self._baselines[task_class] = b
            for metric in TRACKED_METRICS:
                if metric not in observed:
                    continue
                obs = float(observed[metric])
                if metric not in b.metrics or b.sample_count == 0:
                    b.metrics[metric] = obs
                else:
                    prev = b.metrics[metric]
                    b.metrics[metric] = self._alpha * obs + (1.0 - self._alpha) * prev
            b.sample_count += 1
            self._persist()
            return dict(b.metrics)

    def reset(self, task_class: str) -> None:
        with self._lock:
            self._baselines.pop(task_class, None)
            self._persist()

    def all_classes(self) -> list[str]:
        with self._lock:
            return sorted(self._baselines.keys())

    # ---- persistence ----

    def _load(self) -> None:
        assert self._path is not None
        try:
            raw = self._path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):  # guardian: allow-return-none-swallow -- baseline file unreadable: load silently skipped; registry stays empty
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:  # guardian: allow-return-none-swallow -- baseline file corrupt JSON: load silently skipped; registry stays empty
            return
        if not isinstance(payload, dict):
            return
        for key, value in payload.items():
            if isinstance(value, dict):
                try:
                    self._baselines[key] = Baseline.from_dict(value)
                except (KeyError, TypeError, ValueError):
                    continue

    def _persist(self) -> None:
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {k: v.to_dict() for k, v in self._baselines.items()}
        # Atomic write: temp file in same dir, then rename.
        fd, tmp_path = tempfile.mkstemp(prefix=".baseline_", suffix=".json.tmp", dir=str(self._path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, sort_keys=True)
            os.replace(tmp_path, self._path)
        except OSError:
            # Best-effort cleanup on failure.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


__all__ = ["Baseline", "BaselineRegistry", "DEFAULT_ALPHA", "TRACKED_METRICS"]
