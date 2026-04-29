"""Bridge: lifecycle_trace_contract `_emit_*` debug emissions -> OTEL spans.

Closes the documented gap in the 150-requirements baseline:
  ALL_REQUIREMENTS_ENFORCEMENT_BASELINE.md:181-185
    "Real OTEL emission proof — exporter-in-CI verifying span shapes match
     otel_span_refs declarations."

How it works
------------
The 600+ ``_emit_*`` functions in
``agentic_core/runtime/contracts/lifecycle_trace_contract.py`` call
``logging.getLogger("adg.<edge_kind>").debug(...)``. By default, root logger
level is WARNING so these emissions are silent no-ops.

This bridge:
  1. Installs a ``logging.Handler`` (``AdgEmissionToOtelBridge``) on the root
     logger that captures every record on any ``adg.*`` logger.
  2. Elevates ``adg`` and known ``adg.*`` sub-loggers to DEBUG so the
     emissions actually reach handlers.
  3. Buffers each captured record as a span-shaped dict matching the
     ``RuntimeADGMaterializer`` schema (the same shape ``otel_mcp`` ingests
     via ``otel_ingest_to_runtime_adg``).
  4. On flush, ships the buffered spans through ``OTelIngestService`` so they
     land in the runtime ADG store and ``otel_status.total_spans_processed``
     advances above zero — which the live-emission assertion test verifies.

Failure semantics: never crash the host. If OTEL services are unavailable,
``flush()`` logs a single warning and returns ``{"success": False, ...}``.
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# ── Regex to pull layer/op/source/target hints out of message body ──────────
_LAYER_RE = re.compile(r"layer=(L[0-6]_[A-Z]+|U0_[A-Z]+|C0_[A-Z]+|PA_[A-Z]+)")
_KV_RE = re.compile(r"(\w+)=(\S+)")


class AdgEmissionToOtelBridge(logging.Handler):
    """Capture ``adg.*`` DEBUG records and buffer them as span-shaped dicts.

    Buffer is bounded — older spans are dropped silently when the cap is hit
    (default 50_000 spans, ~10 MB at typical attribute sizes).
    """

    DEFAULT_MAX_BUFFER = 50_000

    def __init__(self, root_trace_id: str | None = None, max_buffer: int = DEFAULT_MAX_BUFFER) -> None:
        super().__init__(level=logging.DEBUG)
        self.root_trace_id = root_trace_id or uuid.uuid4().hex
        self.max_buffer = max_buffer
        self._spans: list[dict[str, Any]] = []
        self._dropped = 0
        self._start_ns = time.time_ns()

    # ------------------------------------------------------------------ emit
    def emit(self, record: logging.LogRecord) -> None:
        if not record.name.startswith("adg."):
            return
        if len(self._spans) >= self.max_buffer:
            self._dropped += 1
            return
        try:
            msg = record.getMessage()
        except (TypeError, ValueError):  # guardian: allow-defensive-fallback -- malformed log args; skip span
            return
        edge_kind = record.name[len("adg.") :]  # e.g. "records_execution_trace"

        attrs: dict[str, Any] = {"edge_kind": edge_kind, "logger": record.name}
        m = _LAYER_RE.search(msg)
        if m:
            attrs["layer"] = m.group(1)
        # Pull k=v pairs from the formatted message body (root_trace_id, source, etc.)
        for k, v in _KV_RE.findall(msg):
            if k not in attrs and len(attrs) < 16:  # cap attrs/span
                attrs[k] = v
        attrs["module"] = record.module
        attrs["pathname"] = record.pathname
        attrs["lineno"] = record.lineno

        span = {
            "trace_id": self.root_trace_id,
            "span_id": uuid.uuid4().hex,
            "parent_span_id": None,  # flat for now; lifecycle_trace_contract has no nesting via debug logs
            "name": f"adg.{edge_kind}",
            "kind": "INTERNAL",
            "start_time_ns": int(record.created * 1e9),
            "end_time_ns": int(record.created * 1e9),  # zero-duration marker span
            "status_code": "OK",
            "attributes": attrs,
            "events": [],
        }
        self._spans.append(span)

    # ----------------------------------------------------------------- spans
    def buffered_spans(self) -> list[dict[str, Any]]:
        return list(self._spans)

    def stats(self) -> dict[str, Any]:
        return {
            "buffered": len(self._spans),
            "dropped_overflow": self._dropped,
            "max_buffer": self.max_buffer,
            "root_trace_id": self.root_trace_id,
            "uptime_seconds": (time.time_ns() - self._start_ns) / 1e9,
        }

    # ----------------------------------------------------------------- flush
    def flush_to_runtime_adg(self, mission: str | None = None) -> dict[str, Any]:
        """Ship buffered spans through ``OTelIngestService.ingest_to_runtime_adg``.

        Returns the ingest result dict. On any failure, returns
        ``{"success": False, "error": "..."}`` and never raises.
        """
        if not self._spans:
            return {"success": True, "spans_ingested": 0, "note": "no buffered spans"}
        try:
            # IMPORTANT: When apps_rg is launched via `python -m apps_rg.scripts.X`,
            # Python adds `<repo>/apps_rg/` to sys.path[0]. apps_rg has its own
            # `tools/` subpackage (resume-generation utilities) which then
            # shadows the repo-root `tools/` package. A plain
            import sys as _sys  # noqa: PLC0415
            from pathlib import Path as _Path  # noqa: PLC0415

            # Bridge is at <repo>/agentic_core/runtime/contracts/otel_lifecycle_bridge.py
            # parents[3] = <repo>
            _repo_root = _Path(__file__).resolve().parents[3]
            _repo_root_str = str(_repo_root)

            # The cleanest bypass for the apps_rg/tools shadow is to temporarily
            # prepend the repo root to sys.path AND evict any cached `tools`,
            # `tools.mcp`, `tools.otel` namespaces that were resolved against
            # the shadow. After the imports succeed, restore the previous state.
            _orig_sys_path = list(_sys.path)
            _evicted: dict[str, Any] = {}
            # Unconditionally evict all `tools` / `tools.X` cache entries:
            # we can't tell from outside which finder resolved them, and we
            # need a clean reimport from the repo-root path. Restored in the
            # finally clause below.
            for _name in list(_sys.modules):
                if _name == "tools" or _name.startswith("tools."):
                    _evicted[_name] = _sys.modules.pop(_name)
            # Force repo root to the FRONT so it beats apps_rg/ at sys.path[0].
            _sys.path.insert(0, _repo_root_str)
            try:
                from tools.otel import otel_config as _otel_config  # noqa: PLC0415
                from tools.otel.otel_loaders import OTelLoaderBundle  # noqa: PLC0415
                from tools.otel.otel_services_ingest import OTelIngestService  # noqa: PLC0415
                from tools.otel.otel_state import RuntimeMetrics  # noqa: PLC0415
                from tools.otel.otel_write_gateway import RuntimeADGWriteGateway  # noqa: PLC0415
            finally:
                # Restore sys.path. Keep newly-loaded tools.otel.* in sys.modules
                # (they're correct repo-root copies) but put back the shadow
                # entries so apps_rg code that comes after us still works.
                _sys.path[:] = _orig_sys_path
                for _name, _mod in _evicted.items():
                    _sys.modules.setdefault(_name, _mod)

            config = _otel_config.build_config(_otel_config.__file__)
            metrics = RuntimeMetrics(last_updated=config.metrics_initial_last_updated)
            loaders = OTelLoaderBundle(config=config, metrics=metrics)
            gateway = RuntimeADGWriteGateway(loaders)
            service = OTelIngestService(config=config, metrics=metrics, write_gateway=gateway)

            # Ingest in chunks to respect max_spans_per_ingest.
            chunk_size = max(1, getattr(config, "max_spans_per_ingest", 1000))
            total_ingested = 0
            last_result: dict[str, Any] = {"success": True}
            try:
                from tqdm import tqdm  # noqa: PLC0415

                _iter = tqdm(
                    range(0, len(self._spans), chunk_size),
                    desc="OTEL ingest",
                    unit="chunk",
                    leave=False,
                )
            except ImportError:
                _iter = range(0, len(self._spans), chunk_size)
            for i in _iter:
                chunk = self._spans[i : i + chunk_size]
                payload = {
                    "trace_id": self.root_trace_id,
                    "mission": mission or f"lifecycle_trace_{self.root_trace_id}",
                    "spans": chunk,
                }
                last_result = service.ingest_to_runtime_adg(payload)
                if not last_result.get("success"):
                    return {
                        "success": False,
                        "error": last_result.get("error", "unknown ingest failure"),
                        "spans_ingested": total_ingested,
                        "spans_buffered": len(self._spans),
                    }
                total_ingested += len(chunk)
            return {
                "success": True,
                "spans_ingested": total_ingested,
                "trace_id": self.root_trace_id,
                "snapshot_id": last_result.get("snapshot_id"),
                "version_id": last_result.get("version_id"),
            }
        except ImportError as exc:  # guardian: allow-otel-unavailable -- otel optional; skip silently
            import traceback as _tb  # noqa: PLC0415

            tb = _tb.format_exc()
            logger.warning(
                "otel_lifecycle_bridge.flush: OTEL services unavailable (%s)\n%s",
                exc,
                tb,
            )
            return {
                "success": False,
                "error": f"otel services unavailable: {exc}",
                "traceback": tb,
            }
        except Exception as exc:  # guardian: allow-broad-exception -- observability never crashes host
            import traceback as _tb  # noqa: PLC0415

            tb = _tb.format_exc()
            logger.warning("otel_lifecycle_bridge.flush: ingest failed (%s)\n%s", exc, tb)
            return {"success": False, "error": str(exc), "traceback": tb}


# ── Module-level installer ───────────────────────────────────────────────────


_INSTALLED_BRIDGE: AdgEmissionToOtelBridge | None = None


def install_bridge(root_trace_id: str | None = None) -> AdgEmissionToOtelBridge:
    """Install the bridge as a root-logger handler. Idempotent.

    Returns the active bridge instance. Subsequent calls return the existing
    instance unchanged so callers can grab the buffer.
    """
    global _INSTALLED_BRIDGE
    if _INSTALLED_BRIDGE is not None:
        return _INSTALLED_BRIDGE
    bridge = AdgEmissionToOtelBridge(root_trace_id=root_trace_id)
    root = logging.getLogger()
    root.addHandler(bridge)
    # Elevate adg.* loggers to DEBUG so their records actually reach handlers.
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("adg"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    logging.getLogger("adg").setLevel(logging.DEBUG)
    _INSTALLED_BRIDGE = bridge
    return bridge


def get_bridge() -> AdgEmissionToOtelBridge | None:
    """Return the active bridge, or None if not installed."""
    return _INSTALLED_BRIDGE


def uninstall_bridge() -> None:
    """Remove the bridge handler. Mostly for tests."""
    global _INSTALLED_BRIDGE
    if _INSTALLED_BRIDGE is None:
        return
    logging.getLogger().removeHandler(_INSTALLED_BRIDGE)
    _INSTALLED_BRIDGE = None


# ── Context-manager helper for app entry points ─────────────────────────────


from contextlib import contextmanager  # noqa: E402


@contextmanager
def otel_lifecycle_capture(mission: str, root_trace_id: str | None = None):
    """Install the bridge, yield it, flush on exit (success or failure).

    Usage in an app entry point::

        from agentic_core.runtime.contracts.otel_lifecycle_bridge import otel_lifecycle_capture

        def main() -> int:
            with otel_lifecycle_capture(mission="apps_eval.run_eval"):
                ...  # orchestrator.run(...)
            return 0

    Fail-open: bridge installation never raises; flush failures only emit a
    warning on logger ``agentic_core.runtime.contracts.otel_lifecycle_bridge``.
    """
    bridge: AdgEmissionToOtelBridge | None
    try:
        bridge = install_bridge(root_trace_id=root_trace_id)
    except Exception as exc:  # guardian: allow-broad-exception -- observability never crashes host
        logger.warning("otel_lifecycle_capture: install failed (%s)", exc)
        bridge = None
    try:
        yield bridge
    finally:
        if bridge is not None:
            try:
                stats = bridge.stats()
                ingest = bridge.flush_to_runtime_adg(mission=mission)
                logger.info(
                    "otel_lifecycle_capture[%s]: buffered=%d ingested=%d success=%s",
                    mission,
                    stats.get("buffered", 0),
                    ingest.get("spans_ingested", 0),
                    ingest.get("success", False),
                )
                if not ingest.get("success"):
                    logger.warning(
                        "otel_lifecycle_capture[%s]: ingest issue: %s",
                        mission,
                        ingest.get("error"),
                    )
            except Exception as exc:  # guardian: allow-broad-exception -- observability never crashes host
                logger.warning("otel_lifecycle_capture[%s]: flush failed (%s)", mission, exc)
