from __future__ import annotations

import logging
from typing import Any, Callable

from tools.mcp.mcp_deferred_loader import DeferredLoader

from tools.otel.otel_config import OTelServerConfig
from tools.otel.otel_state import RuntimeMetrics


logger = logging.getLogger(__name__)


class OTelLoaderBundle:
    """Owns heavy deferred resources and exposes blocking/non-blocking accessors."""

    def __init__(self, config: OTelServerConfig, metrics: RuntimeMetrics) -> None:
        self._config = config
        self._metrics = metrics
        self._store_loader = DeferredLoader(
            "runtime-adg-store",
            self._create_runtime_adg_store,
            timeout=config.status_store_timeout_seconds,
        )
        self._tracer_loader = DeferredLoader(
            "otel-tracer",
            self._create_tracer,
            timeout=config.status_tracer_timeout_seconds,
        )

    def _create_runtime_adg_store(self):
        from agentic_core.L6_system_learning.store import FileBackedRuntimeADGStore

        return FileBackedRuntimeADGStore(self._config.runtime_adg_dir)

    def _create_tracer(self):
        from apps_shared.utils.open_telemetry_tracing_adapter_util import get_tracer

        return get_tracer("otel-mcp-server")

    def get_tracer_blocking(self):
        return self._tracer_loader.get()

    def get_store_blocking(self):
        return self._store_loader.get()

    def get_tracer_nonblocking(self):
        return self._tracer_loader.get(wait_timeout=0)

    def get_store_nonblocking(self):
        return self._store_loader.get(wait_timeout=0)

    def tracer_loading(self) -> bool:
        return self._tracer_loader.is_loading()

    def store_loading(self) -> bool:
        return self._store_loader.is_loading()

    def tracer_loaded(self) -> bool:
        return self._tracer_loader.is_loaded()

    def store_loaded(self) -> bool:
        return self._store_loader.is_loaded()

    def prewarm(self) -> None:
        """Start heavy imports before the MCP event loop begins."""
        self._tracer_loader.get(wait_timeout=0)
        self._store_loader.get(wait_timeout=0)
        logger.info("Background prewarm started for tracer and runtime-adg-store")

    def safe_get(self, getter: Callable[[], Any], label: str) -> tuple[Any | None, str | None]:
        try:
            return getter(), None
        except Exception as exc:  # guardian: allow-broad-exception
            logger.warning("%s loader failed: %s", label, exc)
            self._metrics.mark_error()
            return None, str(exc)
