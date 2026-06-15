# ADG Edge Authority Axis (2026-04-28)

**Status:** Accepted
**Date:** 2026-04-28

## Problem

The ADG generator was emitting **unqualified edges** — every import edge had
the same shape regardless of whether the target was:

- A real on-disk file (verified)
- A name only superficially internal-looking but pointing at nothing (unresolved)
- A literal string passed to `importlib.import_module()` (dynamic, statically unverifiable)
- A third-party / stdlib package (external)
- A test-file edge (test_only, should not pollute production hotspot reports)
- An edge derived from runtime telemetry (runtime_observed, distinct provenance)

Downstream hotspot, coverage, and governance analyses had no way to filter by
**authority**, so 14k+ broken-target edges silently fed into every report.

## Solution

Every row in the canonical `edges` table now carries an explicit `authority`
field drawn from a closed enum. Materialized views project subsets of edges
by authority, and downstream consumers MUST query the appropriate projection.

### Closed Enum (SSOT: `agentic_core/adg/artifact/edge_authority.py`)

| Authority | Meaning |
|---|---|
| `verified` | Target node has a non-empty `resolved_path` on disk. |
| `unresolved` | Target name is internal-prefixed but has no resolved path. |
| `dynamic` | Edge originated from `importlib.import_module(literal)` / `__import__(literal)` / `find_spec(literal)` — statically unverifiable. |
| `external` | Target is third-party / stdlib (no expectation of in-repo resolution). |
| `test_only` | Source file lives under a `tests/` tree. Should not feed production hotspot/governance analyses. |
| `runtime_observed` | Edge was emitted by the runtime ADG ingest path (otel telemetry), not static AST scanning. |

### Precedence (highest to lowest)

```
runtime_observed > test_only > dynamic > external > verified > unresolved
```

Provenance dominates target-state. A test-file edge is `test_only` even if
its target resolves on disk. A dynamic-string import is `dynamic` even if
the literal happens to resolve today.

## Materialized Views

| View | Use Case | Filter |
|---|---|---|
| `mv_edges_verified` | Strict production analysis (only proven-resolved edges) | `authority = 'verified'` |
| `mv_edges_governance` | **Default downstream choice** for hotspot/coverage/governance | `authority IN ('verified', 'external', 'test_only', 'runtime_observed')` |
| `mv_edges_unresolved` | Governance / RCA bucket (broken-target signal) | `authority = 'unresolved'` |

`edge_view` (the projected fact table downstream consumers commonly join on)
now includes `authority` as a column so existing JOINs already pull it
through — no schema rewrite required at the consumer side.

## Migration Recipe

### Existing query (silently includes broken edges)

```sql
SELECT COUNT(*) FROM edges WHERE relation_type = 'imports' AND ...;
```

### Migrated query (verified-only, strict)

```sql
SELECT COUNT(*) FROM mv_edges_verified WHERE relation_type = 'imports' AND ...;
```

### Migrated query (governance — most common — excludes unresolved + dynamic)

```sql
SELECT COUNT(*) FROM mv_edges_governance WHERE relation_type = 'imports' AND ...;
```

### Migrated query (explicit filter, when you need fine-grained control)

```sql
SELECT COUNT(*)
FROM edges
WHERE relation_type = 'imports'
  AND authority IN ('verified', 'test_only', 'external', 'runtime_observed')
  AND ...;
```

### Governance / "what is broken?" queries

```sql
SELECT * FROM mv_edges_unresolved WHERE source_file LIKE 'agentic_core/L0_routing/%';
```

## CI Enforcement

| Gate | Tier | Purpose |
|---|---|---|
| `ops_scripts/ci/check_edge_authority_well_formed.py` | B (blocking) | Every edge must have a non-NULL authority drawn from the closed enum. |
| `ops_scripts/ci/check_unresolved_edges_ratchet.py` | R (ratchet) | Unresolved-edge count must not grow above baseline. Seeded at 14,475. |

## Pipeline Integration

| Stage | File | What it does |
|---|---|---|
| Schema definition | `agentic_core/adg/artifact/ArtifactPaths.py` (and `multi_writer.py`) | `authority TEXT DEFAULT NULL` column + `idx_edges_authority` index |
| Initial backfill | `ArtifactPaths._write_sqlite()` (and `multi_writer`) | After bulk insert + synthetic antipattern emissions, runs `SQL_AUTHORITY_BACKFILL` to populate authority on every edge. |
| Final-stage backfill | `tools/generate/generate_full_adg.py` | After late-stage scanners (entrypoint, gate_self_test, r6) — they insert edges AFTER `_write_sqlite`, so backfill is re-run idempotently. |
| Static dynamic-import emission | `agentic_core/adg/extraction/visitors/dynamic.py` | `_DynamicExecutionVisitor` emits a synthetic `imports` edge with `edge_kind='dynamic_import'` for every literal-string import-resolution call. |
| Runtime ADG | `tools/generate/generate_runtime_adg.py` | Schema includes `authority TEXT NOT NULL DEFAULT 'runtime_observed'`; every INSERT explicitly stamps it. |

## What This Replaces

The G-DANGLING-IMPORT external CI gate (filesystem-AST-based) becomes a
backstop / cross-check. The authority axis is the **first-class** signal —
every snapshot now carries the dangling-import data structurally, classified
at write time, queryable via SQL. Downstream consumers no longer need a
separate process to discover broken targets.
