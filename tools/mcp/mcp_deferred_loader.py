"""
Shared MCP deferred resource loader.

Heavy resources (embedding models, gRPC tracers, database connections) MUST NOT
block the MCP stdio handshake. This module provides a standardized pattern for
lazy-loading expensive resources on first use, with timeout protection.
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Callable

logger = logging.getLogger(__name__)


class DeferredLoader:
    """Thread-safe deferred resource loader with bounded caller wait.

    Design:
    - The factory runs in a daemon thread so a stuck load cannot block process exit.
    - Callers wait on an Event with a bounded timeout.
    - The first caller starts background load and may optionally wait up to timeout.
    - Subsequent callers either get the cached value instantly or time out cleanly.
    - ``get(wait_timeout=0)`` is a true non-blocking kickoff — starts the factory
      in background and returns None immediately without waiting.
    - ``call_serialized()`` provides single-flight access to the loaded resource for
      callers that need to avoid concurrent use of a non-thread-friendly object.

    Important limitation:
    - Python cannot safely cancel an in-flight thread. When a serialized call times
      out, this loader keeps the single-flight lock held until the worker thread
      actually exits. That prevents cascading concurrent calls against the same
      resource and avoids poisoning a permanent worker thread.
    """

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
        """Return the resource, loading on first call. Always bounded."""
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
        """Run fn(resource) under a single-flight lock with timeout-aware quarantine."""
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
            except BaseException as exc:  # guardian: allow-broad-except -- worker boundary
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
                "DEFERRED_SERIAL_CALL_TIMEOUT: %s — no result after %.1fs; quarantining subsequent calls until worker exits",
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
        """Release the single-flight lock only after the timed-out worker actually exits."""

        def _releaser() -> None:
            worker.join()
            self._call_lock.release()
            logger.info("DEFERRED_SERIAL_CALL_RELEASED: %s finished after timeout", op_name)

        threading.Thread(
            target=_releaser,
            daemon=True,
            name=f"deferred-call-release:{self.name}:{op_name}",
        ).start()

    def _run_factory(self) -> None:
        """Run the factory in a daemon thread and publish result/error."""
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
        except BaseException as exc:  # guardian: allow-broad-except -- daemon thread must not crash silently
            self._last_error = exc
            logger.exception("DEFERRED_LOAD_FAIL: %s — unexpected error", self.name)
        finally:
            self._loading = False
            self._ready.set()

    def is_loaded(self) -> bool:
        """Check if the resource has been loaded without triggering a load."""
        return bool(self._result)

    def is_loading(self) -> bool:
        """Check if a background load attempt is currently running."""
        return self._loading

    def require(self) -> Any:
        """Return the resource or raise RuntimeError with a helpful message."""
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
