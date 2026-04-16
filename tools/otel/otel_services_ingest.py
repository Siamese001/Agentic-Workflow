from __future__ import annotations

import logging
import time
from typing import Any

from tools.otel.otel_config import OTelServerConfig
from tools.otel.otel_state import RuntimeMetrics
from tools.otel.otel_write_gateway import RuntimeADGWriteGateway


logger = logging.getLogger(__name__)


class OTelIngestService:
    """Ingestion service that materializes spans and persists through a write seam."""

    def __init__(
        self,
        config: OTelServerConfig,
        metrics: RuntimeMetrics,
        write_gateway: RuntimeADGWriteGateway,
    ) -> None:
        self._config = config
        self._metrics = metrics
        self._write_gateway = write_gateway

    def ingest_to_runtime_adg(self, trace_data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(trace_data, dict):
            return {"success": False, "error": "trace_data must be a dict"}

        spans = trace_data.get("spans", [])
        if not isinstance(spans, list):
            return {"success": False, "error": "trace_data['spans'] must be a list"}
        if len(spans) > self._config.max_spans_per_ingest:
            return {
                "success": False,
                "error": f"Too many spans for single ingestion (max {self._config.max_spans_per_ingest})",
            }

        try:
            from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

            mission = trace_data.get("mission") or trace_data.get("trace_id") or f"trace_{int(time.time())}"
            materializer = RuntimeADGMaterializer()
            snapshot = materializer.materialize(spans, mission=mission)
            version_id = self._write_gateway.persist_snapshot(snapshot)
            self._metrics.record_ingest(len(spans))

            result = {
                "success": True,
                "trace_id": trace_data.get("trace_id"),
                "snapshot_id": snapshot.snapshot_id,
                "version_id": version_id,
                "spans_ingested": len(spans),
                "timestamp": int(time.time()),
            }
            logger.info("otel_ingest_success", extra=result)
            return result
        except Exception as exc:
            logger.error(
                "otel_ingest_error",
                extra={"trace_id": trace_data.get("trace_id", "unknown"), "error": str(exc)},
            )
            self._metrics.mark_error()
            return {
                "success": False,
                "error": str(exc),
                "trace_id": trace_data.get("trace_id", "unknown"),
            }
