# ADR-027: OTel MCP + Runtime ADG Anthropic-Alignment

- **Status**: Accepted
- **Date**: 2026-04-22
- **Deciders**: Codex (paired with user)
- **Related**:
  - ADR-023 Runtime HITL Exit Control
  - ADR-025 Unified Heal-Router OTel Schema
- **Plan**: `.claude/plans/otel-anthropic-alignment-b4c8e1.md`

## Context

Anthropic's published OpenTelemetry observability guidance for the Claude Agent SDK
and Claude Code (see references) defines a canonical span taxonomy, W3C trace-context
propagation, standard OTel resource attributes, and privacy defaults for tool I/O
capture. The repo's existing OTel MCP server (`tools/otel/`) and Runtime ADG
materializer (`system_learning/runtime_adg/`) ship an audit-grade graph extension
that Anthropic's guidance does not cover, but diverged from Anthropic's wire-format
conventions on four axes:

1. Span names did not match `claude_code.interaction` / `claude_code.llm_request` /
   `claude_code.tool` / `claude_code.tool.execution` / `claude_code.tool.blocked_on_user`.
2. W3C `traceparent` / `tracestate` were not accepted on ingest or emitted on read,
   preventing trace stitching with upstream infra spans.
3. Only `service.name` was set as a resource attribute; `service.version`,
   `deployment.environment`, and `rpc.system` were absent.
4. Tool I/O (inputs/outputs/parameters) could reach on-disk snapshot JSON with no
   redaction and no per-span byte cap.

## Decision

Adopt Anthropic's wire-format conventions as an **additive** layer over the existing
Runtime ADG governance/replay capability. The file-backed content-addressed Runtime
ADG store is **preserved** and remains the canonical audit substrate — it
complements, rather than replaces, a live OTLP collector.

Concretely:

### Span Taxonomy (additive)
Add `trace_interaction`, `trace_llm_request`, `trace_claude_tool`, and
`trace_tool_blocked_on_user` context managers on `OpenTelemetryTracingAdapter`
emitting the Anthropic span names. Existing `trace_orchestrator` / `trace_cognitive`
/ `trace_action` / `trace_tool` methods remain unchanged.

### W3C Trace Context
`otel_ingest_to_runtime_adg` accepts optional `traceparent` and `tracestate` in the
trace_data payload. When present, they are stamped onto the root span's
`attributes` dict before materialization, so the content-addressed snapshot schema
does not change. On read (`otel_trace`), `_attach_trace_context` lifts them from
the root node back into the response envelope.

### Resource Attributes
`OpenTelemetryTracingAdapter.__init__` sets:
- `service.name` (env `OTEL_SERVICE_NAME`, default "otel-mcp")
- `service.version` (env `OTEL_SERVICE_VERSION`, default "unknown")
- `deployment.environment` (env `OTEL_DEPLOYMENT_ENVIRONMENT`, default "unknown")
- `rpc.system = "mcp"`
- Any additional key=value pairs in `OTEL_RESOURCE_ATTRIBUTES`

### Privacy Defaults
`system_learning/runtime_adg/materializer.py` redacts `_TOOL_CONTENT_KEYS`
(`tool_input`, `tool_output`, `tool_parameters`, `tool.parameters`, `input`,
`output`, `content`, `prompt`, `response`, `result`, `message`, `body`) at span
extraction time. Redaction is bypassed only when `OTEL_MCP_LOG_TOOL_CONTENT=1`.
After serialization, `attributes_json` is capped at `OTEL_MCP_SPAN_ATTR_MAX_BYTES`
bytes (default 60000) with a `...[truncated]` marker.

### OTLP Auto-Enable
`get_tracer()` honors `OTEL_TRACES_EXPORTER=otlp` with
`OTEL_EXPORTER_OTLP_PROTOCOL` choosing HTTP vs gRPC. This makes the existing OTLP
exporter support usable from env configuration without call-site changes.

## Consequences

### Positive
- Snapshots are portable to any OTel backend (Honeycomb / Tempo / Jaeger) without
  semantic translation.
- Upstream trace stitching works via `traceparent`.
- Privacy posture is safe-by-default and matches Anthropic's 60 KB/span precedent.
- Runtime ADG preserves ADR-023 governance/replay role explicitly.

### Negative / Trade-offs
- Existing span names continue to be emitted; new code should prefer Anthropic
  taxonomy. Dual emission is acceptable during migration.
- Snapshots of older traces (pre-ADR-027) will not carry `traceparent`;
  `_attach_trace_context` tolerates this.
- Redaction changes observable `attributes_json` content — downstream consumers
  that relied on raw tool I/O must set `OTEL_MCP_LOG_TOOL_CONTENT=1` explicitly
  (with stated privacy awareness).

### Deferred Scope
None captured at ADR authorship. If batched OTLP export or live-dashboard stream
needs special tuning (queue size, flush interval), capture via `DEFERRED_SCOPE:`
at discovery.

## Rejected Alternatives

| Alternative | Rejection Reason |
|---|---|
| Replace Runtime ADG with live OTLP collector | Loses content-addressed replay and ADR-023 runtime-HITL audit substrate |
| Hard-switch span names (breaking) | Unnecessary — additive context managers preserve consumers |
| Extend snapshot schema with `traceparent`/`tracestate` top-level fields | Would invalidate content-hash for existing snapshots; root-span attribute stamping avoids schema change |

## References

- Anthropic Agent SDK Observability: https://code.claude.com/docs/en/agent-sdk/observability
- Anthropic Claude Code Monitoring: https://docs.anthropic.com/en/docs/claude-code/monitoring-usage
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- OTel Semantic Conventions (Resource): https://opentelemetry.io/docs/specs/semconv/resource/
