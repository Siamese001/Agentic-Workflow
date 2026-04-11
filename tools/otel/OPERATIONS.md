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

## Status Field Meanings

### `otel_status` Response

| Field | Meaning |
|-------|---------|
| `collector_available` | `true` if OpenTelemetry tracer is enabled and reachable |
| `runtime_adg_store_available` | `false` if FileBackedRuntimeADGStore cannot be initialized (expected if no traces ingested yet) |
| `last_trace_timestamp` | Unix timestamp of most recent trace processed |
| `cached_traces` | Number of traces currently in in-memory cache |
| `total_traces_processed` | Total traces processed since server start |
| `total_spans_processed` | Total spans processed since server start |
| `error_count` | Number of errors encountered during trace processing |
| `anomaly_count` | Number of spans flagged as anomalous |
| `runtime_adg_snapshots` | Count of JSON snapshot files in `agentic_core/L4_state/memory/runtime_adg/` |

### Common Patterns

- **`collector_available: true, runtime_adg_store_available: false`**: Normal when no traces have been ingested yet. The server can still respond to queries (returns mock data or empty results).
- **`collector_available: false`**: OpenTelemetry tracer is disabled or misconfigured.
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

## Troubleshooting

### Server fails to start

1. Verify `PYTHONPATH` is set in the MCP config `env` block.
2. Verify `cwd` points to the repo root.
3. Check that `mcp` package is installed: `pip install mcp`
4. Check stderr in Windsurf MCP logs for import errors.

### Lifecycle contract unavailable warning

If you see `[otel_mcp] WARNING: lifecycle_trace_contract unavailable`, the server will still start and tools will work. Lifecycle ADG edge emission is disabled, but this is non-critical for basic operation.

### `runtime_adg_store_available: false`

This is expected if no traces have been ingested. The server still responds to queries with mock/empty data. To enable persistence, ensure the `system_learning/runtime_adg/` infrastructure is initialized.
