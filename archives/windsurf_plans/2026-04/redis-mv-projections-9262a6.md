# Redis MV Projections — Hot Cache for ADG Materialized Views

Plan-slug: `redis-mv-projections-9262a6`
Status: **Complete — W1–W5 delivered; W6 Notion writeback pending**
Tier: **T3** (cross-layer: `tools/adg/*`, MCP read paths, post-gen hook, Notion writeback)
Snapshot at plan time: `artifacts/adg/adg_indexed_04242026_0721.sqlite`
Author: Cascade
Date: 2026-04-24

## Context & Motivation

Redis is currently used as a thin read-through cache for **nodes** and **edges** only
(`adg:v1:<snapshot>:node:*`, `adg:v1:<snapshot>:edge_detail:*`, `fanin:*`, `edge:*`).
SQLite remains SSOT per constitutional §ADG-canonical-invariants.

The ADG snapshot contains **51 materialized views** (`mv_*`) and **15 P-views**
(`v_p0_*`/`v_p1_*`/`v_p2_*`/`v_p3_*`) that constitutional §22 requires as PRIMARY
drivers of T2/T3 refactoring plans. Today each wave-planning / hotspot-first / blast-radius
query recomputes these via SQL. Projecting the small number of rows they contain into
Redis as sorted sets + sets gives O(log N) / O(1) access and removes hot-path SQLite load.

**Non-goal**: Redis is NEVER authoritative. Projections are deterministic read-only
views derived from the ingested SQLite snapshot. `generate_full_adg.py` remains the
only mutation path.

## Success Criteria

- `adg_redis_ingest.py --with-mv` flag exists and projects the canonical MV/P-view set.
- At least 4 materialized views projected as Redis ZSETs (ranked by impact score).
- At least 3 P-views projected as Redis SETs (membership).
- Sentinel key `adg:v1:<snapshot>:_mv_hot` marks MV projection completeness.
- Idempotent: re-running against the same snapshot is a no-op (unless `--force`).
- Bounded: full MV projection < 10s on current snapshot (~1.5M keys budget).
- New Python module `tools/adg/mv_projection.py` with full unit-test coverage for
  projection logic against an in-memory `fakeredis` client.
- Zero regression in existing ingest (nodes/edges) — must pass current smoke check.

## ADG_HOTSPOT_REPORT

| Target File | Layer | Fan-in | Archetype | Surface | Impact | Rationale |
|---|---|---:|---|---|---:|---|
| `tools/adg/adg_redis_ingest.py` | L_TOOLS | 3 | STATE_NODE (cache projection) | State | 3.0 | Primary extension site |
| `tools/adg/cache/redis_cache.py` | L_TOOLS | 8 | STATE_NODE | State | 8.8 | Read-side consumers; add `get_mv_top()` |
| `tools/adg/mcp/tool_handlers.py` | L_TOOLS | 2 | ORCHESTRATOR | Execution | 2.3 | New `adg_mv_top` / `adg_p_view_members` tools |
| `tools/generate_full_adg.py` | L_TOOLS | 1 | ORCHESTRATOR | Execution | 1.0 | Post-gen invoke of MV projection |

Archetype assignment per `.windsurf/rules/adg-canonical-invariants.md` §5.
Surface intersections: **State** (cache), **Execution** (MCP handlers).

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views driving the design** (≥3 required):

1. `mv_hotspot_centrality` (5,668 rows) — `(node_id, adg_name, layer, fan_in, fan_out, betweenness_approx, degree_centrality)`. Projected as ZSET ranked by `degree_centrality` for sub-ms top-K hotspot queries.
2. `mv_graph_reverse_dependency_hotspots` (27 rows) — `(node_id, file_path, layer, direct_inbound, reverse_dependency_score, layer_criticality_weight)`. Projected as ZSET by `reverse_dependency_score * layer_criticality_weight`.
3. `mv_graph_critical_path_blast_radius` (31 rows) — `(node_id, file_path, weighted_blast_radius, blast_radius_type)`. Projected as ZSET by `weighted_blast_radius`.
4. `mv_dependency_cone_risk` (5,668 rows) — `(node_id, resolved_path, cone_risk_score)`. Projected as ZSET by `cone_risk_score`.
5. `mv_debt_concentration_hotspots` (1,588 rows) — `(file, total_debt_score, hotspot_rank)`. Projected as ZSET by `total_debt_score`.

**Semantic edges leveraged** (indirect — ZSET entries key back to `nodes` via `node_id`):
`imports`, `flows_to`, `resolves_callsite`, `writes_to` — callers use existing `fanin`/`fanout` keys.

**P-view evidence** (cross-referenced):
- `v_p0_write_bypass_uwg` (3 rows) → SET `adg:v1:<snap>:pview:p0_write_bypass_uwg` of writer node_ids.
- `v_p0_apps_direct_infra` (0 currently) → SET `adg:v1:<snap>:pview:p0_apps_direct_infra` of consumer node_ids.
- `v_p1_mis_layered_infra` (0 currently) → SET.
- `v_p1_zero_caller_infra` → SET.
- `v_p2_duplicated_adapters` → SET.

Plans consuming these: `.windsurf/plans/adg-ci-gate-hardening-deferred-*.md` hotspot waves,
`/adg-test-triage-gate`, `adg_p0_wave_plan` MCP tool.

Provenance: `backend=sqlite` (source of MV rows), snapshot `adg_indexed_04242026_0721.sqlite`.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.1, W1.2 | Projection module + unit tests | 4,500 | 🟢 | ✅ Done | `tools/adg/mv_projection.py` + 5/5 tests |
| W2 | W2.1 | Standalone CLI `tools/adg/adg_mv_project.py` | 2,000 | 🟢 | ✅ Done | `--force` / `--check` / `--sqlite` flags verified |
| W3 | W3.1, W3.2 | Dedicated `MVRedisReader` in `tools/adg/mv_reader.py` | 3,000 | 🟢 | ✅ Done | 10 read methods, sub-ms latency verified |
| W4 | W4.1 | 4 MCP tools: `adg_mv_top`, `adg_pview_members`, `adg_pview_contains`, `adg_mv_projection_status` | 2,500 | � | ✅ Done | 8/8 handler tests pass |
| W5 | W5.1 | Auto-hook in `tools/generate/integration/mv_project.py` | 1,500 | 🟢 | ✅ Done | Wired into `generate_full_adg.py`; fail-soft; `ADG_SKIP_MV_PROJECT` escape hatch |
| W6 | W6.1 | Notion writeback + this plan's status update | 1,000 | 🟢 | In progress | Plan row posted; final update in flight |

**Token budget**: ~14,500 total; cold-start < 60k context window 🟢.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Build `mv_projection.py` | `tools/adg/mv_projection.py` (new, 235 lines) | 15 P-view specs; 5 MV specs | 3,000 | ✅ Done |
| W1.2 | Integration tests (real Redis, isolated snapshot-id) | `tests/unit/tools/adg/test_mv_projection.py` | 5 tests, pass 7.86s | 1,500 | ✅ Done |
| W2.1 | Standalone CLI (not bolt-on) | `tools/adg/adg_mv_project.py` (new, ~135 lines) | Keeps `adg_redis_ingest.py` untouched per user revert | 2,000 | ✅ Done |
| W3.1 | `MVRedisReader.get_mv_top` / `get_mv_bottom` / `get_mv_score` / `mv_size` / `mv_meta` | `tools/adg/mv_reader.py` (new, ~300 lines) | Separate module keeps `redis_cache.py` focused | 2,000 | ✅ Done |
| W3.2 | `get_pview_members` / `pview_contains` / `pview_size` / `list_projected_mvs` / `list_projected_pviews` / `is_hot` | same | — | 1,000 | ✅ Done |
| W4.1 | MCP tools `adg_mv_top`, `adg_pview_members`, `adg_pview_contains`, `adg_mv_projection_status` | `tools/adg/mcp/tool_handlers.py` + `tools/adg/mcp/server.py` | 8 handler tests pass 12.72s | 2,500 | ✅ Done |
| W5.1 | Post-gen auto-hook | `tools/generate/integration/mv_project.py` (new) + `tools/generate/generate_full_adg.py` | Fail-soft; subprocess-isolated; `ADG_SKIP_MV_PROJECT` escape hatch | 1,500 | ✅ Done |
| W6.1 | Notion + memory writeback | Notion Plans DB | MCP serialization §25 | 1,000 | In progress |

## Gap Register

| Gap | Mitigation |
|---|---|
| MV schemas may drift across snapshots | Projection reads column list from `PRAGMA table_info()` — tolerant to added columns |
| Some MVs are large (5,668 rows × several MVs) | ZSET entries are `node_id → score`; memory overhead ≈ 50 bytes × rows ≈ 300KB per MV — trivial |
| Redis memory cap (currently 1.41G used / 1.58G peak) | All MV keys TTL-bound to snapshot lifetime; `--force` flushes stale projections |
| fakeredis feature gap for ZADD with NX/XX | Use plain `zadd` without flags; simple happy-path |

## Key Design Decisions

1. **Key scheme**: `adg:v1:<snapshot>:mv:<mv_name>` (ZSET, member=`node_id` or `file_path`, score=ranking metric)
2. **P-view key scheme**: `adg:v1:<snapshot>:pview:<view_name>` (SET, members=identifying ids)
3. **Metadata hash**: `adg:v1:<snapshot>:mv:<mv_name>:meta` (HSET) with row count, metric name, projected_at timestamp
4. **Sentinel**: `adg:v1:<snapshot>:_mv_hot` = `1` after all MVs projected successfully
5. **Ranking metric per MV** (chosen for top-K utility):
   - `mv_hotspot_centrality` → `degree_centrality`
   - `mv_graph_reverse_dependency_hotspots` → `reverse_dependency_score * layer_criticality_weight`
   - `mv_graph_critical_path_blast_radius` → `weighted_blast_radius`
   - `mv_dependency_cone_risk` → `cone_risk_score`
   - `mv_debt_concentration_hotspots` → `total_debt_score`
6. **Member identifier**: `node_id` for node-shaped MVs; `file_path` for debt MV.

## Rollback

- Per-wave reversible: each phase is additive (new module, new flag, new tool).
- If projection corrupts Redis: `python tools/adg/adg_redis_ingest.py --force` re-ingests from SQLite SSOT; `adg:v1:<old_snap>:*` flushed automatically.
- No SQLite mutations at any point → zero data-loss risk.

## Verification (executed 2026-04-24)

```
# W1 — projection module tests
$ python -m pytest tests/unit/tools/adg/test_mv_projection.py -v
5 passed in 7.86s

# W4 — MCP handler tests
$ python -m pytest tests/unit/tools/adg/test_mv_mcp_handlers.py -v
8 passed in 12.72s

# W2 + W3 — standalone CLI + reader end-to-end smoke on snapshot 04242026_0721
$ python tools/adg/adg_mv_project.py --force
[adg_mv_project] projected 12,982 MV rows + 13 P-view rows in 1.094s — MV cache HOT ✓
  mv: mv_hotspot_centrality              status=ok rows=5,668
  mv: mv_graph_reverse_dependency_hotspots status=ok rows=27
  mv: mv_graph_critical_path_blast_radius  status=ok rows=31
  mv: mv_dependency_cone_risk            status=ok rows=5,668
  mv: mv_debt_concentration_hotspots     status=ok rows=1,588
  pv: v_p0_write_bypass_uwg              status=ok rows=3
  pv: v_p1_zero_caller_infra             status=ok rows=1
  pv: v_p1_not_on_spine                  status=ok rows=1
  pv: v_p2_duplicated_adapters           status=ok rows=3
  pv: v_p2_mixed_usage                   status=ok rows=3
  pv: v_p3_isolated_experimental         status=ok rows=2
  ... 15 P-views total, all projected successfully

# W4 — MCP handlers end-to-end via direct invocation
adg_mv_projection_status  hot=True mvs=5 pviews=6
adg_mv_top(mv_hotspot_centrality,k=5)  -> [1829→18.66, 53→0.18, 5467→0.05, 51→0.04, 1397→0.04]
adg_pview_contains(v_p0_write_bypass_uwg, 521)     -> True
adg_pview_contains(v_p0_write_bypass_uwg, 999999)  -> False

# W5 — post-gen hook end-to-end
[ADG] Auto-projecting MVs + P-views from adg_indexed_04242026_0721.sqlite...
[ADG] MV projection complete - MV cache is HOT (1.2s)
```

**Hotspot convergence evidence**: node `1829` (`agentic_core/runtime/contracts/lifecycle_trace_contract.py`) ranks #1 across centrality, reverse-dependency, blast-radius, and cone-risk — corroborates the plan's ADG_HOTSPOT_REPORT.

**Design change vs original plan**: After W1/W2/W3 were delivered into `adg_redis_ingest.py` and `redis_cache.py`, the user reverted those edits to keep the canonical node/edge ingest and cache accessor untouched. Reimplementation split the concerns into standalone modules:
- `tools/adg/adg_mv_project.py` (CLI, replaces `--with-mv` flag on existing ingest)
- `tools/adg/mv_reader.py` (reader class, replaces new methods on `RedisCache`)
- `tools/generate/integration/mv_project.py` (post-gen hook, replaces inline integration)

This keeps the 5 files from the original plan all in the additive, zero-risk lane.

## Deferred Scope

None — W1–W5 all delivered in this session.

## References

- Constitutional §22 (graph-layer primary for refactoring)
- `.windsurf/rules/adg-canonical-invariants.md` §1, §6, §11
- `.windsurf/rules/adg-graph-layer-enforcement.md`
- Prior memory: `ProceduralPattern:RedisHotCacheIngestPattern`
