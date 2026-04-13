"""
Shared MCP deferred resource loader.

Heavy resources (embedding models, gRPC tracers, database connections) MUST NOT
block the MCP stdio handshake.  This module provides a standardized pattern for
lazy-loading expensive resources on first use, with timeout protection.

Pattern:
  1. Module-level: just declare the loader
  2. First tool call: loader initializes the resource (with timeout)
  3. Subsequent calls: cached result returned instantly

Usage::

    from tools.mcp.mcp_deferred_loader import DeferredLoader

    def _load_model():
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")

    embedding_model = DeferredLoader("embedding-model", _load_model, timeout=120)

    @mcp.tool()
    def query(text: str) -> str:
        model = embedding_model.get()  # loads on first call, cached after
        if model is None:
            return "Model unavailable — check server logs"
        return str(model.encode([text]))
"""

from __future__ import annotations

import logging
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

    Attributes:
        name: Human-readable name for logging
        timeout: Maximum seconds to wait for the factory (default for get())
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

    def get(self, wait_timeout: float | None = None) -> Any | None:
        """Return the resource, loading on first call.  Always bounded.

        - If already loaded: returns instantly.
        - If not loaded and no other thread is loading: starts the factory
          in a daemon thread (never blocks MCP stdio).
        - If another thread is loading: waits on Event with bounded timeout.
        - ``wait_timeout=0``: starts background load without blocking caller.
        - Returns None on timeout/failure — never raises, never hangs.
        """
        # Fast path — already loaded
        if self._result:
            return self._result[0]

        effective_timeout = self.timeout if wait_timeout is None else wait_timeout

        # Try to become the loader (non-blocking acquire)
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
            # Another thread is loading — wait for it (bounded)
            logger.info(
                "DEFERRED_LOAD_WAIT: %s — waiting for loader thread (%.0fs max)", self.name, effective_timeout
            )

        # Non-blocking kickoff: return immediately
        if effective_timeout <= 0:
            return self._result[0] if self._result else None

        # Wait for ready signal (bounded — Event.wait always returns)
        if self._ready.wait(timeout=effective_timeout):
            return self._result[0] if self._result else None

        logger.warning(
            "DEFERRED_LOAD_WAIT_TIMEOUT: %s — still loading after %.0fs", self.name, effective_timeout
        )
        return None

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
