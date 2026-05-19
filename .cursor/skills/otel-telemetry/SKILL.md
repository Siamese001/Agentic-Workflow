---
name: otel-telemetry
description: OpenTelemetry traces, anomaly detection, policy decisions, healing chain inspection, runtime ADG ingest, and per-agent span analysis via the in-house otel_mcp server. Invoke when the user asks about runtime behavior — traces, spans, anomalies, policy decisions, agent invocation history, healing chains, or when telemetry must be ingested into the runtime ADG. Distinguishes runtime ADG (otel_mcp — what happened at.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---
# ⚠️ DEPRECATED — Redirected to mcp-integration §9

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §9 — OTel Telemetry (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §9 for current guidance.

---

# OTel MCP Skill (Legacy)

In-house. The canonical surface for runtime telemetry: OTEL spans, healing chains, anomaly detection, policy decisions, runtime ADG.

## When To Use This MCP

| User intent | Use otel_mcp? |
|---|---|
| Runtime trace inspection | ✅ Yes |
| What happened during agent X's last run? | ✅ Yes |
| Anomaly / failure spans | ✅ Yes |
| Policy decision history | ✅ Yes |
| Healing chain replay | ✅ Yes |
| Static dependency / import analysis | ❌ No | `adg_sqlite` |
| Agent source code | ❌ No | native `read_file` |

## Tool Routing

| Goal | Tool |
|---|---|
| Process identity (verify restart, stale-process check) | `otel_server_info` — **call this FIRST** when MCP appears stale |
| Server status | `otel_status` |
| Metrics summary | `otel_metrics_summary` |
| Anomaly list (filter by severity) | `otel_anomalies` |
| Policy decisions (last N hours) | `otel_policy_decisions` |
| Full trace by ID | `otel_trace` |
| Spans for a specific agent class | `otel_spans_by_agent` |
| Healing chain for a trace | `otel_healing_chain` |
| Ingest trace into runtime ADG | `otel_ingest_to_runtime_adg` |

## Hard Rules

1. **Stale-process runbook:** When `otel_mcp` tools appear unhealthy, call `otel_server_info` FIRST. If `source_is_stale=true`, restart the MCP server. Do not debug internals before this check.
2. **Static vs runtime separation:** Structural questions ("who imports X?") go to `adg_sqlite`. Runtime questions ("what happened when Y was called?") go to `otel_mcp`. Mixing them up wastes tool budget and produces wrong answers.

## Common Workflows

**Diagnose a failed agent run:**
1. `otel_status` → confirm collector + store healthy
2. `otel_anomalies(severity='high')` → recent failures
3. `otel_trace(trace_id=...)` → full span tree
4. `otel_healing_chain(trace_id=...)` → did self-healing fire?
5. `otel_spans_by_agent(agent_class='X', limit=20)` → other recent runs of same agent

**Ingest a trace into runtime ADG (for what-happened analysis):**
1. `otel_ingest_to_runtime_adg(trace_data={...})`

## Configuration Notes

The `runtime_adg_store_available` flag in `otel_status` reports whether `FileBackedRuntimeADGStore` initialized successfully. Path-validation issues here are an L4 allowlist concern in `path_constants.py`.
