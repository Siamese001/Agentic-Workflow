# ADR-079 — L2 Agent ↔ ADG Graph-Layer Integration Contract

**Status**: Accepted
**Date**: 2026-04-30
**Plan**: `.codex/plans/adg-three-bucket-unified-c4f8e2.md` (W3 P3.4)
**Pairs with**: ADR-074 (Runtime Bucket as OTel View), ADR-078 (apps_* Spine Delegation)
**Pilot consumer**: `agentic_core/L3_orchestration/execution_orchestrator.py::ExecutionOrchestrator._populate_d2_cache`
(W5 P5.3 of the unified plan)

## Context

W3 P3.3 just exposed four graph-layer primitives through the `adg_sqlite`
MCP server:

- `adg_mv_hotspot_centrality` — top-N structurally central nodes
- `adg_blast_radius` — downstream impact for a node
- `adg_semantic_fanout` — outgoing edges via canonical semantic relations
- `adg_p_view_query` — pre-classified architectural concerns (P0..P3 views)

Until now the graph-layer overlay (materialized views, semantic edges,
P-views) was a build-time analysis surface used only by CI gates. With these
four tools live, **L2 runtime agents** (orchestrators, executors, healers)
can consult the same data structurally — but without a contract, two
predictable failure modes emerge:

1. **Bypass-the-abstraction** — agents call `sqlite3.connect()` directly on
   the canonical snapshot, duplicating the MCP/service layer's caching,
   freshness, and read-only semantics.
2. **Stale-snapshot reads** — agents read graph data without aligning to the
   current `adg_snapshot_id`, producing stable but **wrong** decisions when
   the snapshot rotates mid-flight.

This ADR establishes the sanctioned consumption contract.

## Decision

### Approved surface

L2 runtime agents that consume the ADG graph layer MUST go through one of
these two paths:

| Path | When to use | Notes |
|---|---|---|
| **`adg_sqlite` MCP tools** (P3.3 surface) | Cross-process consumers, skill harnesses, Codex authoring, evaluation apps_* | Subject to MCP serialization (§25); use direct SQLite when blocked |
| **`tools.adg.core.service.ADGService`** (in-process) | Same-process agents that already share the runtime (e.g., L3 orchestrator) | Reuses the singleton SQLite connection + Redis cache; alignment to current `adg_snapshot_id` is automatic |

**Forbidden**:

- Direct `sqlite3.connect()` to `artifacts/adg/adg_indexed_*.sqlite` from L2
  agents. The constitutional §28 fallback only applies when MCP is
  unavailable and SQLite is reachable; that path is for emergency CI gates,
  not the runtime hot path.
- Writes of any kind to the graph. The graph is read-only; mutations go
  through `tools/generate_full_adg.py` only.
- Bypassing the service-layer `ADGResponse` envelope (`status` /
  `backend_used` / `data`). Consumers MUST honor the envelope so
  cache-hit/fallback telemetry stays attributable.

### Consumption modes (three-bucket alignment)

Every L2 agent file that consumes the graph layer MUST declare
`__adg_consumer_mode__` per `agentic_core/adg/artifact/consumer_mode.py`:

| Mode | What it asserts | Allowed surface |
|---|---|---|
| `proof` | Decisions binding state, eval, or governance | `proof_view`, `v_runtime_proof`, `mv_*` (after authority filter) |
| `risk` | Backlog/risk-triage/cleanup signals | `risk_view`, P-views (P0..P3), `mv_*` for ranking |
| `inventory` | Logging/observability/exploration only | All of the above + raw `nodes`/`edges` |

Mismatches fail closed under W5's strict-mode flip (`CONSUMER_MODE_GATE_STRICT=1`).

### Latency contract

| Surface | Cold p99 | Warm-cache p99 | Fallback |
|---|---:|---:|---|
| `adg_mv_hotspot_centrality` | <500ms | <50ms | empty list, log warning |
| `adg_blast_radius` | <500ms | <50ms | `available=False`, log warning |
| `adg_semantic_fanout` | <300ms | <50ms | empty list |
| `adg_p_view_query` | <200ms | n/a | error response with `available_p_views` |

Hot-path consumers (e.g., the W5 P5.3 pilot) MUST cache results within their
own scope (request, trace, or D2-cache window) — not by re-issuing tool
calls. The MCP/service surface is a **once-per-decision** read, not a
once-per-token read.

### Failure mode: graceful degradation with feature flag

L2 consumers MUST wrap graph-layer reads in a feature-flag guard so the
agent reverts to its pre-graph-layer behavior on:

- MCP unavailable (`adg_health` reports red)
- SQLite snapshot missing or stale beyond a configurable max age
- Tool call returns `status="error"`
- Latency budget exceeded

The feature flag MUST be operator-controllable via env var
(`<AGENT>_ADG_GRAPH_LAYER_ENABLED ∈ {auto, on, off}`, default `auto`).

The pilot's reference implementation:

```python
# agentic_core/L3_orchestration/execution_orchestrator.py (W5 P5.3)
__adg_consumer_mode__ = "risk"  # blast-radius drives D2-cache priority

def _populate_d2_cache(self, node_id: str) -> None:
    if not self._adg_graph_layer_enabled():
        return self._populate_d2_cache_legacy(node_id)
    try:
        resp = self._adg_service.get_blast_radius(node_id, hops=2)
        if resp.status != "ok" or not resp.data.get("available", True):
            return self._populate_d2_cache_legacy(node_id)
        self._d2_cache_from_blast_radius(resp.data)
    except (RuntimeError, OSError, TimeoutError) as exc:
        self._otel_log("adg_graph_layer_fallback", reason=str(exc))
        return self._populate_d2_cache_legacy(node_id)
```

### Snapshot-ID alignment

Each `ADGResponse` carries `backend_used`. Consumers MUST log this on every
read and MUST surface `adg_snapshot_id` on the consuming span so downstream
analysis can correlate decisions to the snapshot they were made against.
Snapshot rotation is not atomic across MCP + Redis; consumers see a
read-your-writes window of up to ~60 seconds during regen. Hot-path agents
MUST tolerate this either by:

- Holding the snapshot_id observed at decision-start for the rest of the
  span (preferred), or
- Failing soft to the legacy path when the snapshot_id changes mid-decision.

### Layer-gravity check

L2 agents consuming graph-layer reads from L6 observability is **downward**
consumption — allowed by constitutional §22. The reverse (L6 calling L2 to
shape the graph) is **forbidden** and CI-gated.

## Consequences

### Positive

- L2 agents can finally exploit the graph-layer overlay without bypassing
  the abstraction or duplicating cache/freshness logic.
- The `__adg_consumer_mode__` declaration ties runtime consumption to the
  three-bucket authority model (P1.2/P1.3) — no fresh classification.
- Feature-flag guard makes adoption reversible per agent without a global
  rollback.

### Negative / risks

- Adds an MCP/service hop on the hot path for agents that previously held
  data in-memory. Mitigation: latency contract + warm-cache p99 budgets +
  feature-flag fallback.
- The "once-per-decision" rule depends on agent discipline. Mitigation:
  weekly calibration report that flags agents issuing >N tool calls per
  decision (added in W6).

### Neutral

- This contract does not block L2 agents from consuming the canonical
  surface (`adg_node`, `adg_edge_fanout`, etc.) — those existed pre-P3.3
  and are unchanged.

## Out of scope

- L0/L1 agents are NOT yet authorized to consume the graph layer. The
  routing and cognition layers must remain graph-naive until a successor
  ADR (TBD post-W6) establishes their contract.
- Write-side integration (e.g., agents emitting graph-layer hints back to
  the snapshot) is explicitly out of scope and currently forbidden.
- Real-time graph mutations during a span are forbidden; only build-time
  regen via `tools/generate_full_adg.py` may write.

## References

- Plan: `.codex/plans/adg-three-bucket-unified-c4f8e2.md` (W3 P3.4 +
  W5 P5.3 pilot)
- Constitutional §22 (graph-layer primary driver), §25 (MCP serialization),
  §28 (SQLite-direct fallback hierarchy)
- ADR-074 (Runtime Bucket as OTel View)
- ADR-078 (apps_* Spine Delegation)
- `.codex/rules/adg-canonical-invariants.md` (5 surfaces, 4 archetypes,
  layer multipliers)
- `agentic_core/adg/artifact/consumer_mode.py` (mode declaration enforcement)
- W3 P3.3 surface: `tools/adg/mcp/server.py`, `tools/adg/core/service.py`
