"""File system watcher — event-driven scan triggers.

Plan: ``.codex/plans/apps-architect-deferred-scope-b8e3f1.md`` DW3 DS-4.

Watches plans/rules/core directories for changes and triggers pattern scans.
Polling-based (no external deps). Configurable poll interval and debounce.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Callable, Set

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_WATCH_PATHS = (
    _REPO_ROOT / ".windsurf" / "plans",
    _REPO_ROOT / ".windsurf" / "rules",
    _REPO_ROOT / "agentic_core",
)

ScanCallback = Callable[[Set[Path]], None]


def _hash_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


class FileWatcher:
    """Polls directories for changes and invokes callback on detection."""

    def __init__(
        self,
        watch_paths: tuple[Path, ...] = DEFAULT_WATCH_PATHS,
        poll_interval_s: float = 5.0,
        debounce_s: float = 2.0,
    ) -> None:
        self._watch_paths = watch_paths
        self._poll_interval = poll_interval_s
        self._debounce = debounce_s
        self._hashes: dict[Path, str] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._callback: ScanCallback | None = None
        self._last_event: float = 0.0

    def _snapshot(self) -> dict[Path, str]:
        result: dict[Path, str] = {}
        for wp in self._watch_paths:
            if not wp.exists():
                continue
            for fp in wp.rglob("*"):
                if fp.is_file() and fp.suffix in (".md", ".py", ".yaml"):
                    result[fp] = _hash_file(fp)
        return result

    def _diff(self, current: dict[Path, str]) -> Set[Path]:
        changed: set[Path] = set()
        for path, h in current.items():
            if self._hashes.get(path) != h:
                changed.add(path)
        for path in self._hashes:
            if path not in current:
                changed.add(path)
        return changed

    def start(self, callback: ScanCallback) -> None:
        if self._running:
            return
        self._callback = callback
        self._hashes = self._snapshot()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="architect-watcher")
        self._thread.start()
        _log.info("FileWatcher started on %d paths", len(self._watch_paths))

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=self._poll_interval + 2.0)
            self._thread = None
        _log.info("FileWatcher stopped")

    def _loop(self) -> None:
        while self._running:
            time.sleep(self._poll_interval)
            try:
                current = self._snapshot()
                changed = self._diff(current)
                if changed:
                    now = time.monotonic()
                    if now - self._last_event >= self._debounce:
                        self._last_event = now
                        if self._callback:
                            self._callback(changed)
                self._hashes = current
            except Exception as exc:
                _log.error("FileWatcher loop error: %s", exc)


__all__ = ["FileWatcher", "DEFAULT_WATCH_PATHS"]
