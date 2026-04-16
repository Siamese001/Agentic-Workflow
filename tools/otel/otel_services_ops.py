from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

from tools.otel.otel_config import OTelServerConfig
from tools.otel.otel_loaders import OTelLoaderBundle
from tools.otel.otel_state import RuntimeMetrics, TraceCache


logger = logging.getLogger(__name__)


class OTelOpsService:
    """Health, loading, and process identity surface."""

    def __init__(
        self,
        config: OTelServerConfig,
        loaders: OTelLoaderBundle,
        trace_cache: TraceCache,
        metrics: RuntimeMetrics,
    ) -> None:
        self._config = config
        self._loaders = loaders
        self._trace_cache = trace_cache
        self._metrics = metrics

    def status(self, lifecycle_status: dict[str, Any] | None = None) -> dict[str, Any]:
        tracer, tracer_error = self._loaders.safe_get(self._loaders.get_tracer_nonblocking, "tracer")
        store, store_error = self._loaders.safe_get(self._loaders.get_store_nonblocking, "runtime_adg_store")

        status = {
            "collector_available": tracer is not None and tracer.is_enabled(),
            "runtime_adg_store_available": store is not None,
            "tracer_loading": self._loaders.tracer_loading(),
            "store_loading": self._loaders.store_loading(),
            "tracer_loaded": self._loaders.tracer_loaded(),
            "store_loaded": self._loaders.store_loaded(),
            "last_trace_timestamp": self._metrics.last_updated,
            "cached_traces": len(self._trace_cache),
            "total_traces_processed": self._metrics.total_traces,
            "total_spans_processed": self._metrics.total_spans,
            "error_count": self._metrics.error_count,
            "anomaly_count": self._metrics.anomaly_count,
            "runtime_adg_snapshots": len(list(self._config.runtime_adg_dir.glob("*.json")))
            if self._config.runtime_adg_dir.exists()
            else 0,
            "tracer_error": tracer_error,
            "store_error": store_error,
            "lifecycle": lifecycle_status or {},
        }
        logger.info("otel_status_checked", extra=status)
        return status

    def server_info(self, lifecycle_status: dict[str, Any] | None = None) -> dict[str, Any]:
        git_sha = "unavailable"
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3,
                cwd=str(self._config.repo_root),
            )
            if proc.returncode == 0:
                git_sha = proc.stdout.strip()
        except Exception:  # guardian: allow-broad-exception
            pass

        current_mtime = Path(self._config.source_file).stat().st_mtime
        result = {
            "pid": self._config.server_pid,
            "start_time_utc": int(self._config.server_start_time),
            "source_file": str(self._config.source_file),
            "source_mtime_utc": int(self._config.server_source_mtime),
            "current_mtime_utc": int(current_mtime),
            "source_is_stale": current_mtime > self._config.server_source_mtime,
            "git_sha": git_sha,
            "store_cache_populated": self._loaders.store_loaded(),
            "lifecycle": lifecycle_status or {},
        }
        logger.info(
            "otel_server_info_checked",
            extra={"pid": result["pid"], "source_is_stale": result["source_is_stale"]},
        )
        return result
