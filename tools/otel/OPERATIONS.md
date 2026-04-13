# OpenTelemetry MCP Server — Operations

## Launch Command

The otel_mcp server is launched by Windsurf via the MCP config. The canonical entry is in both:

- `.windsurf/mcp_config.json` (repo-local reference)
- `C:/Users/amita/.codeium/windsurf/mcp_config.json` (global Windsurf config)

### Exact Config Entry

```json
"otel_mcp": {
  "command": "python",
  "args": [
    "-c",
    "import sys; sys.path.insert(0, r'C:/Git/Agentic-Workflow'); __file__ = r'C:/Git/Agentic-Workflow/tools/otel/otel_mcp_server.py'; exec(open(r'C:/Git/Agentic-Workflow/tools/otel/otel_mcp_server.py', encoding='utf-8').read())"
  ],
  "cwd": "C:/Git/Agentic-Workflow",
  "disabled": false,
  "env": {
    "PYTHONPATH": "C:/Git/Agentic-Workflow"
  }
}
```

### Manual Launch (for debugging)

```bash
cd C:/Git/Agentic-Workflow
python -c "import sys; sys.path.insert(0, r'C:/Git/Agentic-Workflow'); __file__ = r'C:/Git/Agentic-Workflow/tools/otel/otel_mcp_server.py'; exec(open(r'C:/Git/Agentic-Workflow/tools/otel/otel_mcp_server.py', encoding='utf-8').read())"
```

## Required Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHONPATH` | `C:/Git/Agentic-Workflow` | Ensures `agentic_core` and `mcp` packages resolve |
| `cwd` | `C:/Git/Agentic-Workflow` | Working directory for path calculations |
| `OTEL_MCP_ALLOW_MOCK_TRACES` | `0` (default) or `1` | When `1`, `otel_trace` returns synthetic mock data for unknown trace IDs instead of an error. Useful for testing. |
| `OTEL_MCP_MAX_TRACE_CACHE` | `256` (default) | Maximum number of traces held in the in-memory LRU cache. Minimum clamped to 16. |

## Status Field Meanings

### `otel_status` Response

| Field | Meaning |
|-------|---------|
| `collector_available` | `true` if OpenTelemetry tracer is enabled and reachable |
| `runtime_adg_store_available` | `false` if FileBackedRuntimeADGStore cannot be loaded (see `store_error` for reason). Expected `false` when no traces have been ingested yet or the store loader timed out. |
| `last_trace_timestamp` | Unix timestamp of most recent trace processed |
| `cached_traces` | Number of traces currently in in-memory cache |
| `total_traces_processed` | Total traces processed since server start |
| `total_spans_processed` | Total spans processed since server start |
| `error_count` | Number of errors encountered during trace processing |
| `anomaly_count` | Number of spans flagged as anomalous |
| `runtime_adg_snapshots` | Count of JSON snapshot files in `agentic_core/L4_state/memory/runtime_adg/` |
| `tracer_error` | `null` if tracer loaded successfully, or error message string on failure |
| `store_error` | `null` if runtime ADG store loaded successfully, or error message string on failure |

### Common Patterns

- **`collector_available: true, runtime_adg_store_available: false`**: Normal when no traces have been ingested yet. The server can still respond to queries. If `OTEL_MCP_ALLOW_MOCK_TRACES=1`, unknown trace IDs return synthetic mock data; otherwise they return `{"success": false, "error": "trace not found"}`.
- **`collector_available: false`**: OpenTelemetry tracer is disabled or misconfigured. Check `tracer_error` for details.
- **`runtime_adg_store_available: true`**: Runtime ADG store is operational and traces can be persisted.

## Available Tools

- `otel_status` — Health check and freshness
- `otel_trace` — Fetch trace by CID as ADG edges
- `otel_spans_by_agent` — Get spans for specific agent class/instance
- `otel_healing_chain` — Follow healing dispatch→outcome→escalation chain
- `otel_policy_decisions` — Path A/B/C/D verdicts with safety plane
- `otel_metrics_summary` — Aggregated runtime edge counters
- `otel_anomalies` — Spans flagged by circuit breaker or safety plane
- `otel_ingest_to_runtime_adg` — Push collected spans to runtime ADG SQLite store
- `otel_server_info` — Process identity for stale-process detection (pid, startup time, source mtime)

## Troubleshooting

### Server fails to start

1. Verify `PYTHONPATH` is set in the MCP config `env` block.
2. Verify `cwd` points to the repo root.
3. Check that `mcp` package is installed: `pip install mcp`
4. Check stderr in Windsurf MCP logs for import errors.

### Lifecycle contract unavailable warning

If you see `lifecycle_trace_contract unavailable, continuing without lifecycle emission`, the server will still start and all tools will work. Lifecycle ADG edge emission is deferred to first tool call and disabled entirely if the import fails. This is non-critical for basic operation.

### `runtime_adg_store_available: false`

This is expected if no traces have been ingested. Check `store_error` in the `otel_status` response for the specific reason. The server still responds to queries. To enable persistence, ensure the `system_learning/runtime_adg/` infrastructure is initialized.

### Missing traces / no mock data

By default, `otel_trace` returns `{"success": false, "error": "trace not found"}` for unknown trace IDs. Set `OTEL_MCP_ALLOW_MOCK_TRACES=1` in the MCP config `env` block to enable synthetic mock traces for development and testing.
