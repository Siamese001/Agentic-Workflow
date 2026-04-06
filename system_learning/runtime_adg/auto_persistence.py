"""Runtime ADG Auto-Persistence - Automatic snapshot storage after execution traces.

Hooks into OpenTelemetry tracing pipeline to automatically persist runtime ADG
snapshots to L4 storage and L6 meta-learning after each execution trace.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

# Import OpenTelemetryTracingAdapter at module level for inheritance
try:
    from apps_shared.utils.open_telemetry_tracing_adapter_util import OpenTelemetryTracingAdapter
    OTEL_ADAPTER_AVAILABLE = True
except ImportError:
    OTEL_ADAPTER_AVAILABLE = False
    # Create a dummy base class if not available
    class OpenTelemetryTracingAdapter:  # type: ignore[no-redef]
        """Dummy base class when OpenTelemetry is not available."""
        pass

from system_learning.runtime_adg import (
    FileBackedRuntimeADGStore,
    L6MetaLearningBridge,
    RuntimeADGMaterializer,
)

logger = logging.getLogger(__name__)


class AutoPersistenceTracingAdapter(OpenTelemetryTracingAdapter):
    """Enhanced tracing adapter with automatic runtime ADG persistence.

    Extends OpenTelemetryTracingAdapter to automatically:
    1. Materialize runtime ADG snapshots after trace completion
    2. Persist snapshots to L4 storage territory
    3. Store snapshots in L6 for meta-learning analysis
    """

    def __init__(
        self,
        service_name: str = "agentic-workflow",
        enable_console_export: bool = False,
        enable_logging: bool = True,
        enable_auto_persistence: bool = True,
        l4_store_path: str | None = None,
        l6_base_dir: str | None = None,
    ):
        """Initialize auto-persistence tracing adapter.

        Parameters
        ----------
        service_name: Service name for tracing
        enable_console_export: Export spans to console
        enable_logging: Enable logging of span events
        enable_auto_persistence: Enable automatic snapshot persistence
        l4_store_path: Custom L4 storage path (uses default if None)
        l6_base_dir: Custom L6 base directory (uses default if None)
        """
        super().__init__(service_name, enable_console_export, enable_logging)

        self._auto_persistence_enabled = enable_auto_persistence
        self._l4_store = None
        self._l6_bridge = None

        if enable_auto_persistence:
            try:
                # Initialize L4 store
                if l4_store_path:
                    from pathlib import Path
                    self._l4_store = FileBackedRuntimeADGStore(Path(l4_store_path))
                else:
                    self._l4_store = FileBackedRuntimeADGStore()  # Uses L4 default

                # Initialize L6 bridge
                if l6_base_dir:
                    from pathlib import Path
                    self._l6_bridge = L6MetaLearningBridge(Path(l6_base_dir))
                else:
                    self._l6_bridge = L6MetaLearningBridge()  # Uses L6 default

                if enable_logging:
                    logger.info(
                        "auto_persistence_enabled",
                        extra={
                            "l4_store_path": str(self._l4_store._base_dir),
                            "l6_base_dir": str(self._l6_bridge._l6_base_dir),
                        },
                    )

            except Exception as e:
                if enable_logging:
                    logger.error(
                        "auto_persistence_init_failed",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
                # Disable auto-persistence if initialization fails
                self._auto_persistence_enabled = False

    @contextmanager
    def trace_orchestrator(self, mission: str, metadata: dict[str, Any] | None = None):
        """Trace orchestrator execution with automatic runtime ADG persistence.

        Extends the base orchestrator tracing to automatically persist runtime ADG
        snapshots when the trace completes.

        Parameters
        ----------
        mission: Mission being executed
        metadata: Additional metadata

        Yields
        ------
        Span context
        """
        start_time = time.time()

        with super().trace_orchestrator(mission, metadata) as span:
            yield span

        # Auto-persist runtime ADG after trace completion
        if self._auto_persistence_enabled:
            try:
                self._auto_persist_runtime_adg(mission, start_time)
            except Exception as e:
                if self.enable_logging:
                    logger.error(
                        "auto_persistence_failed",
                        extra={"mission": mission, "error": str(e)},
                        exc_info=True,
                    )

    def _auto_persist_runtime_adg(self, mission: str, start_time: float) -> dict[str, Any]:
        """Automatically persist runtime ADG snapshot.

        Parameters
        ----------
        mission: Mission identifier
        start_time: Trace start time

        Returns
        -------
        dict[str, Any]
            Persistence results
        """
        if not self._auto_persistence_enabled:
            return {"success": False, "reason": "Auto-persistence disabled"}

        # Drain completed spans
        spans = self.drain_completed_spans()
        if not spans:
            return {"success": False, "reason": "No spans to persist"}

        try:
            # Materialize runtime ADG snapshot
            materializer = RuntimeADGMaterializer()
            snapshot = materializer.materialize(spans, mission=mission)

            # Persist to L4 storage
            l4_version_id = self._l4_store.persist(snapshot)

            # Store in L6 for meta-learning
            l6_meta_id = self._l6_bridge.store_snapshot_for_meta_learning(snapshot)

            persistence_result = {
                "success": True,
                "mission": mission,
                "span_count": len(spans),
                "node_count": len(snapshot.nodes),
                "edge_count": len(snapshot.edges),
                "duration_ms": (time.time() - start_time) * 1000,
                "l4_version_id": l4_version_id,
                "l6_meta_id": l6_meta_id,
                "trace_id": snapshot.trace_id,
            }

            if self.enable_logging:
                logger.info(
                    "runtime_adg_auto_persisted",
                    extra=persistence_result,
                )

            return persistence_result

        except Exception as e:
            error_result = {
                "success": False,
                "mission": mission,
                "span_count": len(spans),
                "error": str(e),
                "duration_ms": (time.time() - start_time) * 1000,
            }

            if self.enable_logging:
                logger.error(
                    "runtime_adg_persistence_error",
                    extra=error_result,
                    exc_info=True,
                )

            return error_result

    def get_auto_persistence_status(self) -> dict[str, Any]:
        """Get auto-persistence status and statistics.

        Returns
        -------
        dict[str, Any]
            Auto-persistence status
        """
        status = {
            "enabled": self._auto_persistence_enabled,
            "l4_store_available": self._l4_store is not None,
            "l6_bridge_available": self._l6_bridge is not None,
        }

        if self._l4_store:
            status["l4_store_path"] = str(self._l4_store._base_dir)
            status["l4_snapshot_count"] = len(self._l4_store.list_snapshots())

        if self._l6_bridge:
            status["l6_base_dir"] = str(self._l6_bridge._l6_base_dir)
            status["l6_snapshot_count"] = len(self._l6_bridge._snapshot_index)

        return status

    def force_persist_current_spans(self, mission: str = "manual") -> dict[str, Any]:
        """Force persistence of currently buffered spans.

        Parameters
        ----------
        mission: Mission identifier for the manual persistence

        Returns
        -------
        dict[str, Any]
            Persistence results
        """
        return self._auto_persist_runtime_adg(mission, time.time())


def get_auto_persistence_tracer(
    service_name: str = "agentic-workflow",
    enable_console_export: bool = False,
    enable_auto_persistence: bool = True,
    **kwargs: Any,
) -> AutoPersistenceTracingAdapter:
    """Get or create global auto-persistence tracer instance.

    Parameters
    ----------
    service_name: Service name
    enable_console_export: Enable console export
    enable_auto_persistence: Enable automatic persistence
    **kwargs: Additional arguments for AutoPersistenceTracingAdapter

    Returns
    -------
    AutoPersistenceTracingAdapter
        Enhanced tracer with auto-persistence
    """
    return AutoPersistenceTracingAdapter(
        service_name=service_name,
        enable_console_export=enable_console_export,
        enable_auto_persistence=enable_auto_persistence,
        **kwargs,
    )


emit_determinism_digest("runtime_adg_auto_persistence", "runtime_adg_auto_persistence_digest")
record_execution_trace("runtime_adg_auto_persistence", "runtime_adg_auto_persistence_trace")
