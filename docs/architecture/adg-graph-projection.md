# ADG Graph Projection — Derived Graph Artifact

**Document type**: Architecture Decision Record (ADR)
**Status**: Accepted
**Wave**: W3.1 (Increment 1–5)

---

## What It Is

`adg_graph_<ts>.sqlite` is a **derived, non-canonical** graph artifact built by
`tools/generate/graph_projection.py` from the canonical `adg_indexed_<ts>.sqlite`.

It stores pre-computed graph-native metrics — centrality, SCCs, reachability, impact
deltas — that cannot be expressed efficiently in the Phase A–E SQL materialized views.
These metrics are read by `GraphProjectionBackend` and surfaced via the analyst CLI
and (in a future increment) the ADG MCP server.

**The canonical `adg_indexed_<ts>.sqlite` remains the source of truth for all structural
queries.** The projection only extends it with graph-algorithm outputs.

### ADG Graph Topology

The canonical ADG uses a **bipartite module↔symbol graph**. `imports` edges go
`module → symbol`, not `module → module`. There are no `calls` edges in the canonical
artifact. The projection builds its DiGraph by including both module and symbol nodes,
using the following relation types that encode meaningful dependency structure:

| Relation type | Direction | Meaning |
|---|---|---|
| `imports` | module → symbol | Module reads an external or project symbol |
| `exports` | module → symbol | Module publishes a symbol |
| `reads_from` | module → symbol | Module reads from a resource/symbol |
| `resolves_callsite` | symbol → module | Project symbol resolves into its containing module |
| `emits_side_effect` | symbol → module | Project symbol causes a side effect in a module |

`proj_nodes` and `proj_centrality` store **module-level** metrics only — symbol nodes
are included in the DiGraph for correct topology but are not written to the projection
tables. `blast_radius_direct` for a module = its in-degree counting all inbound edges
from symbols and other modules.

---

## What It Is Not

| NOT true of `adg_graph_<ts>.sqlite` | What is true instead |
|---|---|
| Not canonical | Canonical DB is `adg_indexed_<ts>.sqlite` |
| Not authoritative for nodes or edges | Read nodes/edges from canonical only |
| Not required for CI to pass | Projection build is non-blocking in the pipeline |
| Not a replacement for Phase A–E views | Complements `mv_*` views; does not duplicate them |
| Not always fresh | Freshness is determined by `source_artifact_digest` comparison |
| Not written to by any query path | Read-only after construction |

---

## Hook Point in the Generation Pipeline

The projection is built in `tools/generate/generate_full_adg.py` as step **P6**,
inserted immediately after `_materialize_adg_views(paths.sqlite)` and before
`_check_witness_tier_gates(...)`.

```
_materialize_adg_views(paths.sqlite)          # Phase A–E SQL views
                                               # ← P6 inserted here (non-blocking)
_check_witness_tier_gates(...)                 # CI gates (unaffected by P6)
```

Failure in P6 prints `[ADG] P6 graph projection skipped: <reason>` and falls through.
The canonical artifact, all CI gates, and all downstream pipeline steps run unaffected.

---

## Projection Tables

All tables use `adg_name` as the stable cross-table identity key. `adg_name` is the
canonical string identity of a node (e.g. `ADG::Module::tools/adg/core/sqlite_backend`)
and is stable across runs as long as the file path does not change.

| Table | Content |
|---|---|
| `proj_meta` | Key-value store: schema version, build timestamp, source artifact digest, node/edge counts |
| `proj_nodes` | Mirror of canonical `nodes` (adg_name, entity_type, layer, resolved_path) — no foreign data added |
| `proj_centrality` | Per-node graph metrics: fan-in, fan-out, betweenness approximation, blast-radius direct and 2-hop, bridge score and type |
| `proj_scc` | Strongly-connected component membership: scc_id, scc_size, scc_type, risk score |
| `proj_violations` | Canonical violations enriched with blast-radius impact from projection data |
| `proj_reachability` | Pairwise shortest-path table (src_adg_name → dst_adg_name, hop count, path weight) for high-centrality seeds |
| `proj_diff` | Cross-run metric deltas: prev/curr values, delta, delta_pct, direction (increased/decreased/unchanged) |

### `proj_meta` Keys

| Key | Value |
|---|---|
| `schema_version` | Projection schema version (currently `"1.0"`) |
| `built_at` | ISO-8601 build timestamp |
| `source_artifact_digest` | Digest from canonical `meta.artifact_digest` at build time |
| `canonical_schema_version` | Canonical artifact schema version at build time |
| `node_count` | Number of rows in `proj_nodes` |
| `edge_count` | Number of edges read from canonical |
| `snapshot_id` | Canonical snapshot ID |

---

## Stable Identity Strategy

`adg_name` is used as the primary key across all `proj_*` tables instead of integer
node IDs. Integer IDs are internal to a specific canonical sqlite run and are not stable
across regenerations. `adg_name` is stable as long as the module path is unchanged.

This means:
- `proj_centrality.adg_name` → join directly to `nodes.adg_name` in the canonical DB
- `proj_scc.adg_name` → stable SCC membership lookup across pipeline runs
- All query methods in `GraphProjectionBackend` accept and return `adg_name` strings

---

## Freshness and Staleness Contract

On every `GraphProjectionBackend` construction:

1. The backend reads `proj_meta.source_artifact_digest` from the projection.
2. It opens the canonical `adg_indexed_<ts>.sqlite` and reads `meta.artifact_digest`.
3. If the two digests match → `is_stale() == False`.
4. If they differ (canonical was regenerated since the projection was built) → `is_stale() == True`.
5. If no projection file exists → `is_available() == False`.

A stale projection is **still queryable** — all query methods return results with
`"stale": True` in the response dict. The backend never silently returns fresh data when
stale; callers must check `is_stale()` or inspect the `stale` field in each result.

```
Freshness check (per connection open)
  proj_meta.source_artifact_digest
    == canonical meta.artifact_digest  →  fresh
    != canonical meta.artifact_digest  →  stale (still available, results carry stale=True)
    (canonical not found)              →  stale (conservative)
    (projection not found)             →  unavailable (is_available() = False)
```

---

## Rebuild Flow

### Via full pipeline (normal path)

```
python tools/generate/generate_full_adg.py
```

P6 runs automatically and writes `artifacts/adg/adg_graph_<ts>.sqlite`.

### Standalone rebuild

```
python tools/generate/graph_projection.py artifacts/adg/adg_indexed_<ts>.sqlite
```

Derives `out_dir` and `ts` from the input path. Writes
`artifacts/adg/adg_graph_<ts>.sqlite` atomically (`.tmp` → rename).

The standalone rebuild is idempotent: running it twice on the same canonical artifact
produces the same `source_artifact_digest` in `proj_meta`.

---

## Archive Rotation

The archiver (`tools/generate/archiving/archiver.py`) already covers `adg_*.sqlite`
via its glob pattern, which matches both `adg_indexed_<ts>.sqlite` and
`adg_graph_<ts>.sqlite`. Old projection files rotate on the same schedule as canonical
artifacts. No separate retention configuration is required.

---

## Analyst CLI

```
python tools/adg/adg_graph_query.py <subcommand> [options]
```

### Subcommands

| Subcommand | Options | What it does |
|---|---|---|
| `status` | — | Show availability, staleness, projection path, source digest, node count |
| `blast-radius <adg_name>` | `--hops N` (default 2) | Print direct and k-hop blast radius for a node |
| `scc <adg_name>` | — | Print SCC ID, size, type, risk score, and all member nodes |
| `violations` | `--layer L`, `--severity S`, `--limit N` | List violations sorted by blast-radius impact descending |
| `diff` | `--metric M`, `--direction D`, `--layer L`, `--limit N` | Print cross-run metric deltas from `proj_diff` |
| `bridges` | `--limit N` | List top bridge/chokepoint nodes by `bridge_score` |
| `regressions` | `--metric M`, `--limit N` | List top metric regressions (largest worsened deltas) |
| `reachability <adg_name>` | `--limit N` | Show nodes reachable from a seed module |

`--direction` values: `worsened` \| `improved` \| `unchanged` (matches `proj_diff.direction` vocabulary).

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success — result found and printed |
| `1` | Unavailable — no projection file exists or could not be opened |
| `2` | Stale — projection exists but `source_artifact_digest` does not match current canonical |

---

## Source-of-Truth Boundaries

| Question | Answer | Source |
|---|---|---|
| Which modules exist? | Canonical `nodes` table | `adg_indexed_<ts>.sqlite` |
| Which edges exist? | Canonical `edges` table | `adg_indexed_<ts>.sqlite` |
| Which violations exist? | Canonical `violations` table | `adg_indexed_<ts>.sqlite` |
| What is a node's blast radius? | `proj_centrality.blast_radius_direct/2hop` | `adg_graph_<ts>.sqlite` |
| Is this node in a cycle? | `proj_scc.scc_type`, `scc_size` | `adg_graph_<ts>.sqlite` |
| Is the projection current? | `proj_meta.source_artifact_digest` vs canonical | Both files |
| Did metrics worsen? | `proj_diff.direction`, `delta` | `adg_graph_<ts>.sqlite` |

The projection **never** overrides canonical data. If a projection row conflicts with
a canonical row (e.g. node count differs), the canonical row wins.

---

## Backend and Service Query Surface

All projection-native queries are now accessible at three levels:

| Query | `GraphProjectionBackend` | `SQLiteBackend` | `ADGService` |
|---|---|---|---|
| Availability/staleness | `get_status()` | `get_projection_status()` | `get_projection_status()` |
| Centrality metrics | `get_centrality(adg_name)` | `get_centrality(node_id)` ¹ | — |
| Blast radius | `get_blast_radius(adg_name, hops)` | `get_blast_radius(node_id, hops)` | `get_blast_radius(node_id, hops)` |
| SCC membership | `get_scc(adg_name)` | `get_scc(node_id)` | `get_scc(node_id)` |
| Violations with impact | `get_violations_with_impact(layer, severity, limit)` | `get_violations_with_impact(...)` | `get_violations_with_impact(...)` |
| Cross-run diff | `get_diff(metric, direction, layer, limit)` | `get_diff(...)` | `get_diff(...)` |
| Top bridges | `get_top_bridges(limit)` | `get_top_bridges(limit)` | `get_top_bridges(limit)` |
| Top regressions | `get_top_regressions(metric, limit)` | `get_top_regressions(...)` | `get_top_regressions(...)` |
| Reachability rows | `get_reachability(src, limit)` | `get_reachability(src, limit)` | `get_reachability(src, limit)` |

¹ `SQLiteBackend.get_centrality()` returns a scalar float (blast_radius_direct); use `GraphProjectionBackend.get_centrality()` directly for the full dict.

All methods return `[]` / `None` / empty dict when the projection is unavailable — never raise.

---

## Schema 1.1 — Hardening (Increment 5)

Schema version `1.1` was introduced to bound query cost and table growth on large live artifacts.

### Indexes added

| Index | Table | Columns | Covers |
|---|---|---|---|
| `idx_proj_diff_metric_dir` | `proj_diff` | `(metric, direction)` | `get_diff(metric=X, direction=Y)` filter |
| `idx_proj_diff_delta` | `proj_diff` | `(metric, delta DESC)` | `get_top_regressions()` ORDER BY delta |
| `idx_proj_viol_blast` | `proj_violations` | `(blast_radius_direct DESC)` | `get_violations_with_impact()` sorted output |
| `idx_proj_reach_src_hop` | `proj_reachability` | `(src_adg_name, hop_count)` | `get_reachability()` hop-filtered queries |

### Growth controls

| Control | Value | Effect |
|---|---|---|
| `_DIFF_STORE_UNCHANGED` | `False` | Unchanged metric rows are not written — eliminates ~59% of `proj_diff` rows on real artifacts |
| `_REACHABILITY_PER_SEED_LIMIT` | `2000` | Hard cap on rows stored per reachability seed; nearest-hop rows kept when cap exceeded |

### Build metadata in `proj_meta`

Schema 1.1 writes these additional keys to `proj_meta` on every build:

| Key | Type | Description |
|---|---|---|
| `build_duration_s` | float | Wall-clock seconds for graph load + compute phases |
| `graph_node_count` | int | Total nodes in the in-memory DiGraph (modules + symbols) |
| `graph_edge_count` | int | Total edges in the in-memory DiGraph |
| `reachability_seed_count` | int | Number of seed nodes that triggered reachability BFS |
| `reachability_row_count` | int | Total rows written to `proj_reachability` |
| `reachability_per_seed_cap` | int | Cap applied per seed (constant `_REACHABILITY_PER_SEED_LIMIT`) |
| `reachability_max_hops` | int | BFS depth limit (constant `_REACHABILITY_MAX_HOPS`) |
| `diff_row_count` | int | Total rows written to `proj_diff` |
| `diff_changed_count` | int | Rows with direction `worsened` or `improved` |
| `diff_store_unchanged` | bool str | `"false"` in 1.1+ — confirms unchanged rows were excluded |

`get_status()` exposes `build_duration_s`, `reachability_seed_count`, `reachability_row_count`,
`reachability_per_seed_cap`, `diff_row_count`, and `diff_changed_count` directly.

### Backward compatibility

Schema 1.0 projections remain readable. `GraphProjectionBackend.get_diff()` detects `schema_version < 1.1`
and re-applies the `direction != 'unchanged'` WHERE clause to avoid returning stored unchanged rows.

---

## Deferred Items

The following are explicitly out of scope until a future increment:

| Item | Status |
|---|---|
| Redis ingest for `adg_graph_<ts>.sqlite` | Deferred — Redis projection cache not implemented |
| ADG MCP server tool-level exposure | Deferred — `SQLiteBackend`/`ADGService` wired but MCP tools not yet extended |
| Archive zip inclusion of projection | **Implemented** — projection included in `adg_run_<ts>.zip` if built |
| Reachability table for all nodes | Partial — only high-centrality seed nodes have reachability rows |
| `get_diff()` method on backend | **Implemented** — `GraphProjectionBackend`, `SQLiteBackend`, `ADGService` all expose it |
| Schema 1.1 hardening | **Implemented** — indexes, growth controls, build metadata (Increment 5) |
