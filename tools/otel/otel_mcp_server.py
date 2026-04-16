"""OpenTelemetry Runtime ADG MCP Server.

Refactored surface that preserves the tool contract while separating:
- ops and process identity
- trace query and analytics
- ingest and persistence seam
- lifecycle registration
- deferred resource loading

This version preserves the known non-blocking loader fix and hardens the
health path so `otel_status` and `otel_server_info` stay side-effect free.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_SELF = Path(__file__).resolve()
_REPO_ROOT_BOOTSTRAP = _SELF.parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    print(f"[otel_mcp] FATAL: mcp package not found - {exc}. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from tools.otel.otel_config import build_config
from tools.otel.otel_lifecycle import LifecycleRegistrar
from tools.otel.otel_loaders import OTelLoaderBundle
from tools.otel.otel_services_ingest import OTelIngestService
from tools.otel.otel_services_ops import OTelOpsService
from tools.otel.otel_services_query import OTelQueryService
from tools.otel.otel_state import RuntimeMetrics, TraceCache
from tools.otel.otel_tool_registry import register_tools
from tools.otel.otel_write_gateway import RuntimeADGWriteGateway


logger = logging.getLogger(__name__)
config = build_config(__file__)
mcp = FastMCP(config.mcp_server_name)
metrics = RuntimeMetrics(last_updated=config.metrics_initial_last_updated)
trace_cache = TraceCache(config.cache_max_traces)
lifecycle = LifecycleRegistrar()
loaders = OTelLoaderBundle(config=config, metrics=metrics)
write_gateway = RuntimeADGWriteGateway(loaders)
ops_service = OTelOpsService(config=config, loaders=loaders, trace_cache=trace_cache, metrics=metrics)
query_service = OTelQueryService(config=config, loaders=loaders, trace_cache=trace_cache, metrics=metrics)
ingest_service = OTelIngestService(config=config, metrics=metrics, write_gateway=write_gateway)

register_tools(
    mcp=mcp,
    lifecycle=lifecycle,
    ops_service=ops_service,
    query_service=query_service,
    ingest_service=ingest_service,
)


def _prewarm() -> None:
    loaders.prewarm()
    lifecycle.start_background()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger.info("Starting OpenTelemetry MCP Server")
    _prewarm()
    mcp.run(transport=config.tool_transport)
