## §9 — OTel Telemetry

**In-house.** Runtime telemetry: OTEL spans, healing chains, anomaly detection, policy decisions, runtime ADG.

### When To Use

| Intent | Use? |
|--------|------|
| Runtime trace inspection | ✅ Yes |
| What happened during agent X's run? | ✅ Yes |
| Anomaly/failure spans | ✅ Yes |
| Policy decision history | ✅ Yes |
| Healing chain replay | ✅ Yes |
| Static dependency analysis | ❌ No — `adg_sqlite` |
| Agent source code | ❌ No — `read_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| Process identity (check stale) | `otel_server_info` — **call FIRST** |
| Server status | `otel_status` |
| Metrics summary | `otel_metrics_summary` |
| Anomaly list | `otel_anomalies` |
| Policy decisions | `otel_policy_decisions` |
| Full trace | `otel_trace` |
| Spans by agent | `otel_spans_by_agent` |
| Healing chain | `otel_healing_chain` |
| Ingest to runtime ADG | `otel_ingest_to_runtime_adg` |

### Hard Rules
1. **Stale-process runbook** — `otel_server_info` FIRST if MCP appears stale
2. **Static vs runtime separation** — structural → `adg_sqlite`, runtime → `otel_mcp`

---
