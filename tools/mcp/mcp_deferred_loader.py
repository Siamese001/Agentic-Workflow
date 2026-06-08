"""
Shared deferred resource loader.

Heavy resources must not block the MCP stdio handshake. This loader starts work
in a daemon thread and lets callers wait for a bounded period. It is suitable
for lazy model and database client initialization.
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Callable

logger = logging.getLogger(__name__)


class DeferredLoader:
    """Thread-safe deferred loader with bounded wait semantics."""

    _QUARANTINE_RELEASE_TIMEOUT: float = 5.0

    def __init__(
        self,
        name: str,
        factory: Callable[[], Any],
        *,
        timeout: float = 30.0,
    ) -> None:
        self.name = name
        self._factory = factory
        self.timeout = timeout
        self._result: list[Any] = []
        self._ready = threading.Event()
        self._load_gate = threading.Lock()
        self._loading = False
        self._last_error: BaseException | None = None
        self._worker: threading.Thread | None = None
        self._call_lock = threading.Lock()

    def get(self, wait_timeout: float | None = None) -> Any | None:
        """Return the resource, loading on first call."""
        if self._result:
            return self._result[0]

        effective_timeout = self.timeout if wait_timeout is None else wait_timeout

        acquired = self._load_gate.acquire(blocking=False)
        if acquired:
            try:
                if self._result:
                    return self._result[0]
                if not self._loading:
                    self._ready.clear()
                    self._loading = True
                    self._last_error = None
                    self._worker = threading.Thread(
                        target=self._run_factory,
                        daemon=True,
                        name=f"deferred-load:{self.name}",
                    )
                    self._worker.start()
            finally:
                self._load_gate.release()
        else:
            logger.info(
                "DEFERRED_LOAD_WAIT: %s — waiting for loader thread (%.0fs max)",
                self.name,
                effective_timeout,
            )

        if effective_timeout <= 0:
            return self._result[0] if self._result else None

        if self._ready.wait(timeout=effective_timeout):
            return self._result[0] if self._result else None

        logger.warning(
            "DEFERRED_LOAD_WAIT_TIMEOUT: %s — still loading after %.0fs",
            self.name,
            effective_timeout,
        )
        return None

    def call_serialized(
        self,
        fn: Callable[[Any], Any],
        *,
        wait_timeout: float | None = None,
        call_timeout: float | None = None,
        queue_wait_timeout: float | None = None,
        op_name: str | None = None,
    ) -> Any:
        """Run fn(resource) under a single-flight lock with bounded wait."""
        resource = self.get(wait_timeout=wait_timeout)
        effective_op_name = op_name or f"{self.name}-serialized-call"

        if resource is None:
            if self._loading:
                raise RuntimeError(
                    f"{self.name} still loading — retry shortly and check stderr for DEFERRED_LOAD logs"
                )
            if self._last_error is not None:
                raise RuntimeError(f"{self.name} unavailable — last error: {self._last_error}")
            raise RuntimeError(
                f"{self.name} unavailable — check server logs (stderr) for DEFERRED_LOAD errors"
            )

        acquire_timeout = call_timeout if queue_wait_timeout is None else queue_wait_timeout
        if acquire_timeout is None:
            acquire_timeout = self.timeout

        acquired = self._call_lock.acquire(timeout=max(acquire_timeout, 0.0))
        if not acquired:
            raise RuntimeError(
                f"{effective_op_name} could not start after waiting {acquire_timeout:.1f}s for the prior call"
            )

        result_q: queue.Queue[tuple[bool, object]] = queue.Queue(maxsize=1)

        def _worker() -> None:
            try:
                result_q.put((True, fn(resource)))
            except BaseException as exc:  # guardian: allow-broad-except
                result_q.put((False, exc))

        worker = threading.Thread(
            target=_worker,
            daemon=True,
            name=f"deferred-call:{self.name}:{effective_op_name}",
        )
        worker.start()

        effective_call_timeout = self.timeout if call_timeout is None else call_timeout
        if effective_call_timeout <= 0:
            self._release_lock_when_done(worker, effective_op_name)
            raise TimeoutError(f"{effective_op_name} timed out immediately (call_timeout <= 0)")

        try:
            ok, payload = result_q.get(timeout=effective_call_timeout)
        except queue.Empty as exc:
            logger.warning(
                "DEFERRED_SERIAL_CALL_TIMEOUT: %s — no result after %.1fs; quarantining "
                "subsequent calls until worker exits or bounded release fires",
                effective_op_name,
                effective_call_timeout,
            )
            self._release_lock_when_done(worker, effective_op_name)
            raise TimeoutError(f"{effective_op_name} timed out after {effective_call_timeout:.1f}s") from exc

        self._call_lock.release()
        if ok:
            return payload
        raise payload  # type: ignore[misc]

    def _release_lock_when_done(self, worker: threading.Thread, op_name: str) -> None:
        """Release the single-flight lock after worker exit or bounded wait."""

        def _releaser() -> None:
            worker.join(timeout=self._QUARANTINE_RELEASE_TIMEOUT)
            if worker.is_alive():
                logger.warning(
                    "DEFERRED_SERIAL_CALL_FORCE_RELEASE: %s worker still running after %.0fs — "
                    "releasing lock to unblock subsequent calls",
                    op_name,
                    self._QUARANTINE_RELEASE_TIMEOUT,
                )
            self._call_lock.release()
            logger.info("DEFERRED_SERIAL_CALL_RELEASED: %s lock released", op_name)

        threading.Thread(
            target=_releaser,
            daemon=True,
            name=f"deferred-call-release:{self.name}:{op_name}",
        ).start()

    def _run_factory(self) -> None:
        try:
            value = self._factory()
            self._result[:] = [value]
            logger.info("DEFERRED_LOAD_OK: %s loaded successfully", self.name)
        except ImportError as exc:
            self._last_error = exc
            logger.error("DEFERRED_LOAD_IMPORT: %s — %s", self.name, exc)
        except (RuntimeError, OSError, ValueError) as exc:
            self._last_error = exc
            logger.error("DEFERRED_LOAD_FAIL: %s — %s", self.name, exc)
        except BaseException as exc:  # guardian: allow-broad-except
            self._last_error = exc
            logger.exception("DEFERRED_LOAD_FAIL: %s — unexpected error", self.name)
        finally:
            self._loading = False
            self._ready.set()

    def is_loaded(self) -> bool:
        return bool(self._result)

    def is_loading(self) -> bool:
        return self._loading

    def invalidate(self) -> None:
        """Drop the cached resource so the next ``get()`` rebuilds it.

        Used when a cached resource is detected dead (e.g. a ChromaDB
        ``PersistentClient`` whose shared system was stopped, deleting its rust
        bindings -- surfacing as ``'RustBindingsAPI' object has no attribute
        'bindings'``). Thread-safe; a no-op if nothing is cached.

        Single-flight, not strict-consistency: under concurrent ``get()``/``invalidate()``
        (parallel callers sharing one loader) a stale in-flight factory result may be read
        once, bounded by ``timeout`` (the caller re-probes on its next call). The sequential
        rebuild path that motivates this method does not hit that race.
        """
        with self._load_gate:
            self._result.clear()
            self._loading = False
            self._last_error = None
            self._ready.clear()

    def require(self) -> Any:
        value = self.get()
        if value is not None:
            return value
        if self._loading:
            raise RuntimeError(
                f"{self.name} still loading — retry shortly and check stderr for DEFERRED_LOAD logs"
            )
        if self._last_error is not None:
            raise RuntimeError(f"{self.name} unavailable — last error: {self._last_error}")
        raise RuntimeError(f"{self.name} unavailable — check server logs (stderr) for DEFERRED_LOAD errors")
