"""AutoPersistenceTracingAdapter — Wave 3: Runtime ADG persistence integration.

Extends OpenTelemetryTracingAdapter with automatic runtime ADG persistence.
Hooks into UWG path to ensure every write emits execution trace with snapshot ID.

Design:
- Inherits all OpenTelemetryTracingAdapter functionality
- Automatically materializes spans into RuntimeADGSnapshot on drain
- Persists snapshots via UWG (Universal Write Gateway)
- Propagates snapshot_id through execution traces
- Graceful degradation when persistence unavailable

Usage:
    from agentic_core.L6_observability import AutoPersistenceTracingAdapter

    adapter = AutoPersistenceTracingAdapter(
        service_name="my-service",
        auto_persist=True,
        uwg_endpoint="http://localhost:8000",
    )

    with adapter.trace_orchestrator("my-mission"):
        # Run orchestration...
        pass

    # Automatically drains and persists runtime ADG snapshot
    spans = adapter.drain_completed_spans()
"""

from __future__ import annotations

import logging
import time
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_links_execution_to_snapshot,
    _emit_records_execution_trace,
    _emit_snapshots_state,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# Deferred imports for graceful degradation
try:
    from apps_shared.utils.open_telemetry_tracing_adapter_util import (
        OpenTelemetryTracingAdapter,
    )

    OTEL_ADAPTER_AVAILABLE = True
except ImportError:
    OTEL_ADAPTER_AVAILABLE = False
    OpenTelemetryTracingAdapter = object  # type: ignore[misc, assignment]

try:
    from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
    from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot

    MATERIALIZER_AVAILABLE = True
except ImportError:
    MATERIALIZER_AVAILABLE = False
    RuntimeADGMaterializer = None  # type: ignore[misc, assignment]
    RuntimeADGSnapshot = None  # type: ignore[misc, assignment]

# Bootstrap ADG edge emission
emit_replay_key("auto_persistence_adapter", "L4_STATE")
emit_determinism_digest("auto_persistence_adapter", "auto_persistence_adapter_digest")
_emit_snapshots_state("L4_STATE", "auto_persistence_adapter", "snapshot_binding")
_emit_writes_via_uwg("L4_STATE", "auto_persistence_adapter", "uwg_write_binding")

logger = logging.getLogger(__name__)


class AutoPersistenceTracingAdapter(OpenTelemetryTracingAdapter):  # type: ignore[no-redef]
    """Extended tracing adapter with automatic runtime ADG persistence.

    Wave 3: Runtime ADG persistence integration
    - Automatically materializes spans into RuntimeADGSnapshot
    - Persists snapshots via UWG (Universal Write Gateway)
    - Propagates snapshot_id through execution traces

    Attributes:
        auto_persist: Whether to auto-persist snapshots on drain
        uwg_endpoint: UWG endpoint for snapshot persistence
        _materializer: RuntimeADGMaterializer instance
        _persisted_snapshots: List of persisted snapshot IDs
    """

    def __init__(
        self,
        service_name: str = "agentic-workflow",
        enable_console_export: bool = False,
        enable_logging: bool = True,
        enable_otlp_grpc: bool = False,
        enable_otlp_http: bool = False,
        otlp_grpc_endpoint: str | None = None,
        otlp_http_endpoint: str | None = None,
        # Wave 3: Auto-persistence options
        auto_persist: bool = True,
        uwg_endpoint: str | None = None,
        adg_storage_path: str | None = None,
    ):
        """Initialize adapter with auto-persistence capabilities.

        Args:
            service_name: Name of the service for tracing
            enable_console_export: Export spans to console
            enable_logging: Enable logging of span events
            enable_otlp_grpc: Enable OTLP gRPC exporter
            enable_otlp_http: Enable OTLP HTTP exporter
            otlp_grpc_endpoint: Custom OTLP gRPC endpoint
            otlp_http_endpoint: Custom OTLP HTTP endpoint
            auto_persist: Enable automatic snapshot persistence (Wave 3)
            uwg_endpoint: UWG endpoint for snapshot persistence (Wave 3)
            adg_storage_path: Path for local ADG storage fallback (Wave 3)
        """
        # Initialize parent OpenTelemetryTracingAdapter
        super().__init__(
            service_name=service_name,
            enable_console_export=enable_console_export,
            enable_logging=enable_logging,
            enable_otlp_grpc=enable_otlp_grpc,
            enable_otlp_http=enable_otlp_http,
            otlp_grpc_endpoint=otlp_grpc_endpoint,
            otlp_http_endpoint=otlp_http_endpoint,
        )

        # Wave 3: Auto-persistence configuration
        self.auto_persist = auto_persist and MATERIALIZER_AVAILABLE
        self.uwg_endpoint = uwg_endpoint
        self.adg_storage_path = adg_storage_path or "artifacts/adg"
        self._materializer = RuntimeADGMaterializer() if MATERIALIZER_AVAILABLE else None
        self._persisted_snapshots: list[str] = []
        self._current_snapshot_id: str | None = None
        self._current_trace_id: str | None = None

        if self.enable_logging:
            logger.info(
                "auto_persistence_adapter_initialized",
                extra={
                    "service_name": service_name,
                    "auto_persist": self.auto_persist,
                    "materializer_available": MATERIALIZER_AVAILABLE,
                    "uwg_endpoint": uwg_endpoint,
                },
            )

    def drain_completed_spans(self, mission: str = "", persist: bool | None = None) -> list[dict[str, Any]]:
        """Drain completed spans and optionally auto-persist as RuntimeADGSnapshot.

        Wave 3: Extended to automatically materialize and persist spans.

        Args:
            mission: Mission label for the snapshot
            persist: Override auto_persist setting (default: use self.auto_persist)

        Returns:
            List of drained span dictionaries
        """
        # Drain spans from parent adapter
        spans = super().drain_completed_spans()

        # Determine whether to persist
        should_persist = persist if persist is not None else self.auto_persist

        if should_persist and spans and self._materializer:
            try:
                self._materialize_and_persist(spans, mission)
            except Exception as e:
                # Graceful degradation: log error but don't fail
                if self.enable_logging:
                    logger.warning(
                        "auto_persistence_failed",
                        extra={"error": str(e), "mission": mission, "span_count": len(spans)},
                    )

        return spans

    def _materialize_and_persist(
        self,
        spans: list[dict[str, Any]],
        mission: str = "",
    ) -> RuntimeADGSnapshot | None:
        """Materialize spans into RuntimeADGSnapshot and persist.

        Args:
            spans: List of span dictionaries
            mission: Mission label

        Returns:
            Created RuntimeADGSnapshot or None if failed
        """
        if not self._materializer:
            return None

        # Generate trace ID for this batch
        trace_id = self._current_trace_id or f"auto-{time.time_ns():x}"

        # Materialize spans into snapshot
        snapshot = self._materializer.materialize(
            spans=spans,
            mission=mission or "auto-persisted",
            trace_id=trace_id,
        )

        # Store snapshot ID for propagation
        self._current_snapshot_id = snapshot.snapshot_id
        self._persisted_snapshots.append(snapshot.snapshot_id)

        # Emit trace linking execution to snapshot
        _emit_links_execution_to_snapshot(
            trace_id,
            "L4_STATE",
            snapshot.snapshot_id,
        )
        _emit_records_execution_trace(
            snapshot.snapshot_id,
            LayerSegment.L4_STATE,
            "snapshot_materialized",
        )

        # Persist via UWG if available
        if self.uwg_endpoint:
            self._persist_via_uwg(snapshot)
        else:
            # Local persistence fallback
            self._persist_locally(snapshot)

        if self.enable_logging:
            logger.info(
                "snapshot_materialized_and_persisted",
                extra={
                    "snapshot_id": snapshot.snapshot_id[:16] + "...",
                    "mission": snapshot.mission,
                    "node_count": snapshot.node_count(),
                    "edge_count": snapshot.edge_count(),
                    "trace_id": trace_id,
                },
            )

        return snapshot

    def _persist_via_uwg(self, snapshot: RuntimeADGSnapshot) -> bool:
        """Persist snapshot via Universal Write Gateway (UWG).

        Args:
            snapshot: RuntimeADGSnapshot to persist

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import UWG utilities
            from agentic_core.L4_state.uwg_util import write_through_uwg

            # Prepare snapshot data
            snapshot_data = snapshot.to_dict()

            # Write through UWG
            write_through_uwg(
                content=snapshot_data,
                resource_type="runtime_adg_snapshot",
                resource_id=snapshot.snapshot_id,
                trace_id=snapshot.trace_id,
            )

            _emit_writes_via_uwg(
                "L4_STATE",
                "auto_persistence_adapter",
                snapshot.snapshot_id,
            )

            if self.enable_logging:
                logger.debug(
                    "snapshot_persisted_via_uwg",
                    extra={"snapshot_id": snapshot.snapshot_id[:16] + "..."},
                )

            return True

        except ImportError:
            # UWG not available, fall back to local
            if self.enable_logging:
                logger.debug("uwg_not_available_using_local_fallback")
            return self._persist_locally(snapshot)

        except Exception as e:
            if self.enable_logging:
                logger.warning("uwg_persist_failed", extra={"error": str(e)})
            return self._persist_locally(snapshot)

    def _persist_locally(self, snapshot: RuntimeADGSnapshot) -> bool:
        """Persist snapshot to local storage.

        Args:
            snapshot: RuntimeADGSnapshot to persist

        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            from pathlib import Path

            # Create storage directory
            storage_dir = Path(self.adg_storage_path)
            storage_dir.mkdir(parents=True, exist_ok=True)

            # Write snapshot to file
            filename = f"{snapshot.snapshot_id}.json"
            filepath = storage_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(snapshot.to_dict(), f, indent=2)

            if self.enable_logging:
                logger.debug(
                    "snapshot_persisted_locally",
                    extra={
                        "snapshot_id": snapshot.snapshot_id[:16] + "...",
                        "path": str(filepath),
                    },
                )

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("local_persist_failed", extra={"error": str(e)})
            return False

    def get_snapshot_id(self) -> str | None:
        """Get current snapshot ID for trace propagation.

        Returns:
            Current snapshot ID or None
        """
        return self._current_snapshot_id

    def get_persisted_snapshots(self) -> list[str]:
        """Get list of persisted snapshot IDs.

        Returns:
            List of snapshot IDs
        """
        return self._persisted_snapshots.copy()

    def set_trace_id(self, trace_id: str) -> None:
        """Set trace ID for next snapshot materialization.

        Args:
            trace_id: Trace ID to use
        """
        self._current_trace_id = trace_id

    def create_snapshot_for_spans(
        self,
        spans: list[dict[str, Any]],
        mission: str = "",
    ) -> RuntimeADGSnapshot | None:
        """Manually create snapshot from spans without draining.

        Args:
            spans: List of span dictionaries
            mission: Mission label

        Returns:
            Created RuntimeADGSnapshot or None
        """
        if not self._materializer:
            return None

        trace_id = self._current_trace_id or f"manual-{time.time_ns():x}"

        return self._materializer.materialize(
            spans=spans,
            mission=mission or "manual",
            trace_id=trace_id,
        )

    def get_persistence_status(self) -> dict[str, Any]:
        """Get current persistence status.

        Returns:
            Dictionary with status information
        """
        return {
            "auto_persist_enabled": self.auto_persist,
            "materializer_available": self._materializer is not None,
            "uwg_endpoint": self.uwg_endpoint,
            "local_storage_path": self.adg_storage_path,
            "persisted_snapshot_count": len(self._persisted_snapshots),
            "current_snapshot_id": self._current_snapshot_id,
            "current_trace_id": self._current_trace_id,
        }


# Convenience function for getting auto-persistence tracer
def get_auto_persistence_tracer(
    service_name: str = "agentic-workflow",
    auto_persist: bool = True,
    uwg_endpoint: str | None = None,
    **kwargs: Any,
) -> AutoPersistenceTracingAdapter:
    """Get or create AutoPersistenceTracingAdapter instance.

    Args:
        service_name: Service name
        auto_persist: Enable auto-persistence
        uwg_endpoint: UWG endpoint
        **kwargs: Additional arguments for OpenTelemetryTracingAdapter

    Returns:
        AutoPersistenceTracingAdapter instance
    """
    return AutoPersistenceTracingAdapter(
        service_name=service_name,
        auto_persist=auto_persist,
        uwg_endpoint=uwg_endpoint,
        **kwargs,
    )
