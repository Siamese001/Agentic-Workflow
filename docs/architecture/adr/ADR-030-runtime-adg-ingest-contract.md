# ADR-030: Runtime ADG Ingest Contract

- **Status**: Accepted
- **Date**: 2026-04-23
- **Deciders**: Codex (paired with user)
- **Related**:
  - Constitutional §22 (graph-layer evidence)
  - `@c:/Git/Agentic-Workflow/.claude/rules/adg-canonical-invariants.md` §8 (static-vs-runtime ADG)
  - ADR-025 (unified heal_router OTEL schema)
  - ADR-026 (consensus validator governance)
  - ADR-027 (OTel Anthropic alignment)
- **Plan**: `@c:/Git/Agentic-Workflow/.claude/plans/otel-runtime-adg-ingest-7a3f12.md`
- **Implementation commits**: `1f20f41f26` (W1), `53bb12a38c` (W2), `b94a900db0` (W3), `7390b74899` (W4)

## Context

The canonical invariants rule (§8) defines two distinct ADGs:

- **Static ADG** (`adg_sqlite` MCP): AST scan of code; structural dependencies.
- **Runtime ADG** (`otel_mcp` MCP): OTel spans from live runs; observed behavior.

Prior to this ADR the runtime-ADG ingest surface existed only as an **external** MCP tool (`otel_mcp::otel_ingest_to_runtime_adg`). No in-process producer in `agentic_core/L6_observability/` or `system_learning/` emitted spans that landed in the runtime ADG store. This created a zero-coverage hole: every "what happened at runtime when Y was called?" question fell through to stale or empty snapshots, forcing fallback to static-ADG reasoning even for runtime concerns.

Three producers already shipped OTel-shaped records (`HealRouterTelemetryEmitter`, `ConsensusTelemetryEmitter`, `system_learning._tracing.sl_span`) but none of them fed the runtime ADG store. The MCP tool was never called in-process, and external OTel backends were not configured in the typical dev/CI environment.

## Decision

Adopt a **Runtime ADG Ingest Contract** with four invariants:

### Invariant 1 — In-Process Ingest Helper as SSOT

A single helper module `@c:/Git/Agentic-Workflow/agentic_core/L6_observability/otel_runtime_ingest.py` exposes:

```python
emit_span_to_runtime_adg(span: dict, *, mission=None, trace_id=None) -> dict
emit_spans_to_runtime_adg(spans: list[dict], *, mission=None, trace_id=None) -> dict
```

These are the **only** in-process surfaces that land OTel-shaped spans in the runtime ADG store (`system_learning.runtime_adg.store.FileBackedRuntimeADGStore`). The helper uses a process-level singleton store and materializes via `RuntimeADGMaterializer`.

### Invariant 2 — Best-Effort Mirroring Never Breaks Hot Paths

Every producer that forwards to the helper MUST wrap the call in a precise except clause covering `ImportError, AttributeError, TypeError, ValueError` with a `guardian: allow-log-and-swallow` comment. Runtime-ADG mirroring is telemetry — it MUST NOT disturb the producer's primary responsibility (routing, voting, reasoning).

### Invariant 3 — Producer Wiring Is Coverage-Gated

A CI gate `@c:/Git/Agentic-Workflow/ops_scripts/ci/check_runtime_adg_coverage.py` scans a static EMITTER_PATHS list for the sanctioned ingest markers:

- `emit_span_to_runtime_adg` / `emit_spans_to_runtime_adg`
- `sl_span_with_ingest`
- `_forward_to_runtime_adg`

Currently audit-only with a 20% floor; flips to enforce when all three producers (heal_router, consensus, sl `_tracing`) ship in `main`.

### Invariant 4 — Roundtrip Observable Within 1s

The integration test `@c:/Git/Agentic-Workflow/tests/integration/otel/test_runtime_adg_ingest_roundtrip.py` asserts `emit → index → retrieve-by-trace_id` completes in under 1 second. This is the minimum liveness contract between producers and the store.

## Consequences

### Positive

- §8 static-vs-runtime gap closes for the three highest-signal emitters (heal_router, consensus, sl `_tracing`).
- Runtime ADG snapshots now populate without requiring an external OTel collector.
- Coverage gate makes the producer set explicit and non-growable.

### Negative / Watch Items

- Helper uses a process-level singleton store; multi-process producers (future) will need a sharded or locked variant.
- `FileBackedRuntimeADGStore` validates L4 compliance on construction, so tests swap in `InMemoryRuntimeADGStore` for shape coverage.
- W5 (this ADR) is the last step of plan `otel-runtime-adg-ingest-7a3f12.md`. Further producer wiring (e.g., `orchestrator_engine.py`) is a separate wave.

## Alternatives Considered

1. **Route all in-process producers through the MCP tool.** Rejected: MCPs are out-of-process, so the hop adds latency and introduces a dependency on server liveness for telemetry that must never fail silently.
2. **Emit via OTLP gRPC collector.** Rejected for dev/CI: requires an external backend, adds serialization overhead, and produces no in-process guarantees about landing in the runtime ADG store used by `otel_mcp` queries.
3. **Add a dedicated `runtime_adg` module at L6.** Rejected as overengineered — the helper is ~130 LOC and fits cleanly beside the existing L6 emitters.

## Compliance Checklist

- [x] In-process helper exposes `emit_span_to_runtime_adg` / `emit_spans_to_runtime_adg`
- [x] `heal_router_otel.emit_route_span` forwards to helper (best-effort)
- [x] `consensus_otel.emit_judge_span` forwards to helper (best-effort)
- [x] `system_learning._tracing.sl_span_with_ingest` forwards to helper (best-effort)
- [x] Roundtrip integration test under 1s
- [x] Coverage gate present; audit mode; threshold 20%
- [x] Filesystem ADR retained as source of truth; Notion ADR Registry mirroring is retired
- [ ] Gate flipped to enforce (future wave, after producer set stabilizes)
