# OTel MCP Refactor Bundle

## Intent
This refactor keeps the existing tool names and the uploaded loader fix, while splitting the server into smaller units:

- `otel_mcp_server.py` wires the app together
- `otel_services_ops.py` owns health and process identity
- `otel_services_query.py` owns trace fetch and cache-backed analytics
- `otel_services_ingest.py` owns materialization and persistence orchestration
- `otel_loaders.py` owns deferred heavy resources and prewarm behavior
- `otel_write_gateway.py` centralizes the write seam so direct store persistence can be replaced later
- `otel_lifecycle.py` makes lifecycle registration background and observable instead of inline on health calls

## Preserved behavior
- same FastMCP tool names
- same trace cache behavior
- same fallback order for trace lookup
- same mock trace toggle
- same fixed non-blocking loader checks in `otel_status`
- same background prewarm before `mcp.run()`

## Hardening applied
- `otel_status` is now zero-side-effect and never triggers lifecycle registration
- `otel_server_info` is also zero-side-effect
- lifecycle registration starts in a daemon thread during prewarm and is reported through `lifecycle` fields in status/info responses
- non-health tools only ensure lifecycle registration has started; they do not block on it

## Operational note
This shape is designed to avoid first-call hangs in MCP clients where background prewarm/import activity overlaps with synchronous lifecycle registration.
