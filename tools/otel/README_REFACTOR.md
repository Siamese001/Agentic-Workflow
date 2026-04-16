# OTel MCP Refactor Bundle

## Intent
This refactor keeps the existing tool names and the uploaded bug fix, while splitting the server into smaller units:

- `otel_mcp_server.py` wires the app together
- `otel_services_ops.py` owns health and process identity
- `otel_services_query.py` owns trace fetch and cache-backed analytics
- `otel_services_ingest.py` owns materialization and persistence orchestration
- `otel_loaders.py` owns deferred heavy resources and prewarm behavior
- `otel_write_gateway.py` centralizes the write seam so direct store persistence can be replaced later

## Preserved behavior
- same FastMCP tool names
- same trace cache behavior
- same fallback order for trace lookup
- same mock trace toggle
- same fixed non-blocking `otel_status`
- same background prewarm before `mcp.run()`

## Notable improvement
The tool layer no longer directly owns store persistence. It routes writes through `RuntimeADGWriteGateway`, which is a cleaner boundary for eventual Universal Write Gateway adoption.
