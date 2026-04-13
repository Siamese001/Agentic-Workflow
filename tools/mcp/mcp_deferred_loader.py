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

import concurrent.futures as _cf
import logging
import threading
from typing import Any, Callable

logger = logging.getLogger(__name__)


class DeferredLoader:
    """Thread-safe deferred resource loader with timeout.

    The resource factory runs in a ThreadPoolExecutor so it never blocks
    the asyncio event loop that powers the MCP stdio transport.

    Attributes:
        name: Human-readable name for logging
        timeout: Maximum seconds to wait for the factory
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
        self._result: list[Any] = []  # [] = not loaded; [value] = cached
        self._lock = threading.Lock()  # prevents duplicate executor spawns

    def get(self) -> Any | None:
        """Return the resource, loading it on first call.

        Thread-safe: concurrent callers wait on the lock for the first
        loader to finish — no duplicate ThreadPoolExecutors (MCP SDK #817).
        Returns None (never raises) if loading fails or times out.
        Logs detailed errors to stderr for diagnostics.
        """
        if self._result:
            return self._result[0]

        with self._lock:
            # Double-check after acquiring lock — another thread may have loaded it
            if self._result:
                return self._result[0]

            try:
                with _cf.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._factory)
                    value = future.result(timeout=self.timeout)
                self._result.append(value)
                logger.info("DEFERRED_LOAD_OK: %s loaded successfully", self.name)
                return value
            except _cf.TimeoutError:
                logger.error(
                    "DEFERRED_LOAD_TIMEOUT: %s did not load within %ss",
                    self.name,
                    self.timeout,
                )
                return None
            except ImportError as e:
                logger.error("DEFERRED_LOAD_IMPORT: %s — %s", self.name, e)
                return None
            except (RuntimeError, OSError, ValueError) as e:
                logger.error("DEFERRED_LOAD_FAIL: %s — %s", self.name, e)
                return None

    def is_loaded(self) -> bool:
        """Check if the resource has been loaded without triggering a load."""
        return bool(self._result)

    def require(self) -> Any:
        """Return the resource or raise RuntimeError with a helpful message."""
        value = self.get()
        if value is None:
            raise RuntimeError(
                f"{self.name} unavailable — check server logs (stderr) for DEFERRED_LOAD errors"
            )
        return value
