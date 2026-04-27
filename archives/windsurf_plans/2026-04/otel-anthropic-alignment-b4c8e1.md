# OTel MCP + Runtime ADG — Anthropic Best-Practice Alignment

- **Plan ID**: otel-anthropic-alignment-b4c8e1
- **Tier**: T3 (cross-layer: L4_state snapshot store, L6_observability tracing adapter, tools/otel MCP server, system_learning/runtime_adg materializer)
- **Owner**: Cascade (paired with user)
- **Status**: Complete — 2026-04-22 (ADR-027 merged, 12/12 tests pass)
- **ADG Snapshot (to be pinned at execution)**: latest `artifacts/adg/adg_indexed_*.sqlite`
- **Date Drafted**: 2026-04-22

---

## Goal

Align `tools/otel/otel_mcp_server.py` + `system_learning/runtime_adg/` with Anthropic's published OTel observability guidance (Agent SDK + Claude Code docs) while preserving the Runtime ADG governance/replay capability that Anthropic's guidance does not cover.

## Non-Goals

- Replacing the file-backed Runtime ADG store with a live OTel collector (keep audit-grade snapshots).
- Moving Runtime ADG into SQLite or any RDBMS.
- Changing static ADG (`adg_sqlite`) behavior.

## Source of Truth — Anthropic Guidance Applied

1. Span taxonomy: `claude_code.interaction` → `claude_code.llm_request` | `claude_code.tool` → `claude_code.tool.execution` + `claude_code.tool.blocked_on_user`.
2. W3C trace context: accept/emit `TRACEPARENT` / `TRACESTATE` across process boundaries.
3. Resource attributes: `service.name`, `service.version`, `deployment.environment` at tracer init.
4. Privacy defaults: never log tool I/O unless explicit env opt-in; cap payload per span (60 KB precedent).
5. Export hygiene: batched OTLP export with bounded flush on clean exit; synchronous snapshot persist for audit.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-------------------|
| W1 | 1.1, 1.2 | Span taxonomy + resource attrs (non-breaking) | 6k 🟢 | Existing `_emit_*` helpers can be renamed/wrapped without breaking call sites | Todo | All new spans use Anthropic names; legacy `_emit_*` wrappers delegate to new names; `otel_status` shows `service.name=otel_mcp` |
| W2 | 2.1, 2.2 | Trace-context propagation + `traceparent` ingest | 5k 🟢 | `otel_ingest_to_runtime_adg` schema can add optional `traceparent` field without breaking existing callers | Todo | Snapshot persists `traceparent`; `otel_trace` returns it; round-trip test passes |
| W3 | 3.1, 3.2 | Privacy controls for snapshot I/O capture | 5k 🟢 | Materializer boundary is the single capture point for tool content | Todo | Default strips tool I/O from snapshot; `OTEL_MCP_LOG_TOOL_CONTENT=1` re-enables, capped at 60 KB/span; unit tests prove both modes |
| W4 | 4.1, 4.2 | Dual-export: keep file snapshots + add OTLP stream | 7k 🟡 | OTLP collector endpoint configurable via env; falls back to no-op when unset | Todo | OTel spans reach configured collector; file snapshot still written; both paths independent (collector outage does not block ingest) |
| W5 | 5.1, 5.2, 5.3 | ADR + tests + memory/Notion writeback | 4k 🟢 | ADR-NNN slot available; Notion ADR Registry writeable | Todo | New ADR merged; ≥6 new/updated tests green; Memory `ProceduralPattern:OTelAnthropicAlignment` + Notion ADR row + MCP Registry patch posted |

Totals: ~27k tokens (🟢 green overall, single 🟡 phase W4).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Adopt Anthropic span names | `tools/otel/otel_lifecycle.py`, `tools/otel/otel_tool_registry.py`, `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | 20+ `_emit_*` call sites; must preserve backward compatibility for any downstream consumers of current span names | 4k | Todo |
| 1.2 | Inject resource attributes | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (tracer factory), `tools/otel/otel_loaders.py` | `service.version` needs git_sha at tracer init — already available from `otel_server_info`; need to plumb it into resource | 2k | Todo |
| 2.1 | Accept `traceparent` on ingest | `tools/otel/otel_services_ingest.py`, `system_learning/runtime_adg/materializer.py`, snapshot schema | Snapshot schema change — additive field; downstream `convert_snapshot_to_adg_edges` unaffected; `_trace_index.json` unchanged | 3k | Todo |
| 2.2 | Emit `traceparent` on trace reads | `tools/otel/otel_services_query.py` | Must handle snapshots without the field (back-compat for older JSON files) | 2k | Todo |
| 3.1 | Strip tool I/O from snapshots by default | `system_learning/runtime_adg/materializer.py` | Identify every path where tool input/output enters a span attribute; single redaction boundary preferred | 3k | Todo |
| 3.2 | Env opt-in + 60 KB per-span cap | `tools/otel/otel_config.py`, materializer | Need a deterministic truncation marker (e.g. `…[truncated]`); ensure cap applies per-span, not per-snapshot | 2k | Todo |
| 4.1 | Add OTLP batch exporter (optional) | `apps_shared/utils/open_telemetry_tracing_adapter_util.py`, `tools/otel/otel_config.py` | New env vars (`OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`); must fail-soft when unset | 4k | Todo |
| 4.2 | Decouple file snapshot from OTLP path | `tools/otel/otel_services_ingest.py` | Ingest MUST NOT block on collector; collector failure logged and counted via `RuntimeMetrics.error_count` | 3k | Todo |
| 5.1 | Tests — taxonomy, traceparent, privacy, dual-export | `tests/tools/otel/test_otel_*.py`, `tests/system_learning/runtime_adg/test_materializer_*.py` | 4 new test modules; pytest collection integrity required; no skips | 2k | Todo |
| 5.2 | ADR | `docs/architecture/adr/ADR-NNN-otel-anthropic-alignment.md` | Must reference ADR-023 (runtime HITL) and declare Runtime ADG as complementary, not a replacement for, OTLP collector | 1k | Todo |
| 5.3 | Memory + Notion writeback | Memory entity, Notion ADR Registry row, MCP Registry patch row | Follow `memory-notion-writeback.md`; include DECISION_CAPTURED for any Author-Gate during execution | 1k | Todo |

---

## Dependency Graph

```
W1.1 ──┐
W1.2 ──┤
        ├─► W2.1 ──► W2.2 ──┐
W3.1 ──► W3.2 ──────────────┤
                             ├─► W4.1 ──► W4.2 ──► W5.1 ──► W5.2 ──► W5.3
                             │
(W1/W2/W3 parallelizable)   ─┘
```

- W1, W2, W3 touch disjoint concerns and can proceed in parallel by independent author.
- W4 depends on W1 (needs correct span names) and W3 (must not re-introduce tool I/O through the OTLP path).
- W5 runs last and is the writeback/validation gate.

---

## ADG_HOTSPOT_REPORT (to be filled at execution start)

Must be populated via `adg_edge_fanin(relation_type="imports")` against:

- `tools/otel/otel_lifecycle.py`
- `tools/otel/otel_services_ingest.py`
- `tools/otel/otel_services_query.py`
- `system_learning/runtime_adg/materializer.py`
- `system_learning/runtime_adg/store.py`
- `apps_shared/utils/open_telemetry_tracing_adapter_util.py`

Columns required per constitutional §23: file | layer | fan_in | archetype (CENTRAL_DEPENDENCY / ORCHESTRATOR / STATE_NODE / SAFETY_GATEKEEPER) | surface intersections (Execution/Write/Security/State/Observability) | layer_multiplier | impact_score.

**Layer guess (to be verified):**
- `tools/otel/*` → L6 observability (×0.75) — note: multiplier argues for LOW intrinsic risk BUT Observability Surface intersection is non-trivial for governance use cases
- `system_learning/runtime_adg/*` → L4 state (×1.75) — STATE_NODE
- `apps_shared/utils/open_telemetry_tracing_adapter_util.py` → shared util (×1.0) — CENTRAL_DEPENDENCY (high fan-in expected)

## ADG_GRAPH_LAYER_EVIDENCE (to be filled at execution start)

Required per constitutional §22. Must cite ≥3 materialized views:

- `mv_hotspot_centrality` — rank OTel/runtime_adg nodes
- `mv_graph_reverse_dependency_hotspots` — identify blast radius of tracer adapter changes
- `mv_dependency_cone_risk` — risk cone for W4 (dual-export) changes
- Semantic edges to query: `flows_to` (span attrs → snapshot), `writes_to` (store persist paths), `emits_side_effect` (OTLP export)
- P-view cross-references: `v_p0_write_bypass_uwg` (confirm store persist is governed), `v_p1_mis_layered_infra` (confirm no cross-layer violations introduced)

---

## Gap Register

| Gap | Severity | Resolution Wave |
|-----|:---:|:---:|
| No `claude_code.*` span names emitted | Medium | W1.1 |
| No `service.name` / `service.version` resource attributes | Low | W1.2 |
| No `traceparent` ingest or emission | Medium | W2 |
| Snapshot JSON may contain raw tool I/O | **High** (privacy/security surface) | W3 |
| No live OTLP exporter — only file snapshots | Low (audit-grade present; live dashboards absent) | W4 |
| No dedicated tests for any of the above | Medium | W5.1 |
| No ADR anchoring the runtime-ADG-vs-OTLP distinction | Medium (governance doc) | W5.2 |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Renaming spans breaks existing dashboards/queries | Keep legacy `_emit_*` names as thin wrappers emitting BOTH old and new span names for 1 release cycle; deprecate in follow-up |
| Snapshot schema change breaks replay | Additive-only fields; `convert_snapshot_to_adg_edges` must tolerate missing `traceparent` |
| OTLP collector downtime blocks ingest | W4.2 decouples paths; collector failure increments `error_count`, does not raise |
| Privacy default hides diagnostics users rely on | Document `OTEL_MCP_LOG_TOOL_CONTENT=1` prominently; emit one-line stderr hint at first redaction per process |
| ADG layer violations introduced by new imports | Pre-edit check via `adg_edge_fanout` on modified files; re-run `adg_violations` before W5 commit |

---

## Author-Gate Decision Points (anticipated during execution)

| Decision | Options | Likely Surface |
|---|---|---|
| Span rename strategy | (a) dual-emit for 1 cycle (b) hard-switch + migration note (c) feature-flag | Yes — refactor_scope |
| Privacy redaction granularity | (a) drop whole tool_input/tool_output keys (b) truncate strings >8 KB (c) allowlist of safe fields | Yes — error_handling |
| OTLP exporter choice | (a) official opentelemetry-sdk BatchSpanProcessor (b) thin in-house batcher (c) defer | Yes — dependency_addition |

Each must follow `author-gate-enforcement.md`: score 0.00–1.00, filter at 0.72, dominance rule 0.85/0.12, `ask_user_question` with `AUTHOR-GATE DECISION — <type>` header, emit `DECISION_CAPTURED:` marker on resolution.

---

## Deferred Scope (captured per constitutional §24 at execution time)

To emit `DEFERRED_SCOPE:` marker(s) for anything not completed in this plan — e.g. if W4 OTLP exporter slips to a follow-up.

---

## Exit Criteria (all required before plan marked complete)

1. All 5 waves at status=Done in the Phase-Level Summary table.
2. `pytest tests/tools/otel tests/system_learning/runtime_adg` green with coverage ≥ baseline; no skips.
3. `python tools/generate_full_adg.py` clean (no NEW SC/AP defects attributable to this plan).
4. ADR-NNN merged; Notion ADR Registry row posted via `API-post-page`.
5. Memory `ProceduralPattern:OTelAnthropicAlignment` written with session-recoverable observations.
6. MCP Registry Notion row for `otel_mcp` patched with Notes + Last Validated.
7. This plan header flipped from "Draft — awaiting approval" to "Complete — <YYYY-MM-DD>".

---

## References

- Anthropic — Observability with OpenTelemetry (Agent SDK): https://code.claude.com/docs/en/agent-sdk/observability
- Anthropic — Monitoring (Claude Code): https://docs.anthropic.com/en/docs/claude-code/monitoring-usage
- ADR-023 Runtime HITL Exit Control (in-repo): `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`
- Constitutional invariants: `.windsurf/rules/constitutional.md` §15, §22, §23, §24
- Writeback discipline: `.windsurf/rules/memory-notion-writeback.md`
- Runtime ADG canonical invariants: `.windsurf/rules/adg-canonical-invariants.md` §8 (Static vs Runtime)
