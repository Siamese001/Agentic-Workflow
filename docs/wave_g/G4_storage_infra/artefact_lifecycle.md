# G4 — Artefact Lifecycle

Lifecycle, retention, staleness, and purge behaviour for every catalogued store, grouped by category.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## 1. Category summary

| Category | Stores | Total size | Retention policy |
|---|---:|---:|---|
| Durable (authoritative) | 7 | ~5 GB | varies; see §2 |
| Cache / semi-persistent | 5 | ~12 GB | varies; see §3 |
| Vector (embedded local) | 3 | ~10.2 GB | none observed (manual) |
| Disk artefact (reports, evidence) | 8 | ~230 MB live + 229 MB legacy | none observed |
| Transient output (logs) | 1 | 10.7 MB | none observed |
| Test-only | 1 | small | per-test-run |

## 2. Durable stores

### 2.1 ADG SQLite snapshot (`STORE-ADG-SQLITE`)

- **Creation**: `PIPE-ADG-GEN` stage `s05_write_sqlite`.
- **Invalidation**: full regeneration (new timestamp → new file).
- **Staleness**: tracked by `tools/adg/adg_stale_guard.py` + `mcp1_adg_health.graph_projection.stale`. State machine `SM-09`.
- **Retention**: **not enforced**. Observed: 4.9 GB across 166 files in `artifacts/adg/`. `artifacts/_legacy_adg_archives/` holds 229 MB additional.
- **B7-G4-01**: add retention policy (keep last N snapshots or last N days).

### 2.2 ADG graph projection + JSON tiers

- Same cadence as ADG SQLite; write in same pipeline stages.
- No separate retention.

### 2.3 Memory SQLite (`STORE-MEMORY-SQLITE-CANONICAL`)

- **Creation**: on first `create_entities` / `add_observations` call.
- **Purge**: `mem_cleanup_stale(older_than_days=N)` in `tools/memory/adg_memory_server.py` + `tools/memory/purge_sync.py`.
- **Protected types** (NEVER deleted): `ArchitectureLayer`, `ProjectContext`, `ConstitutionalRule`, `EpisodicEvent`, `ProceduralPattern`, `ArchitecturalDecision`.
- **Telemetry**: `docs/reports/telemetry/memory_purge_<ts>.json` per run.
- **State machine**: `SM-06 MemoryEntity` (FRESH / STALE / PROTECTED).

### 2.4 Memory SQLite duplicates

Three SQLite files present:

| Path | Size | Status |
|---|---:|---|
| `artifacts/memory/knowledge_graph.sqlite` | 1.5 MB | **canonical** (MEMORY_DB default) |
| `data/memory/knowledge_graph.sqlite` | 12 MB | duplicate — writer ambiguity |
| `data/memory/unified_memory.db` | 5.5 MB | orphan — no enumerated owner |

- **B7-G4-03**: ambiguous ownership. Either reconcile into one, or explicitly partition. Canonical declared by config convention, not by code enforcement.

### 2.5 Neo4j (`STORE-NEO4J`)

- External database at `NEO4J_URI`. Lifecycle managed outside repo.
- Retention = Neo4j instance policy.
- Retry posture unknown (B7-G2b-05).

### 2.6 Prompt governance (`STORE-PROMPT-GOVERNANCE`)

- **Creation**: curated via `agentic_core/knowledge/canonical/` + `engine/`.
- **Invalidation**: git-history driven (version-controlled corpus).
- **Retention**: indefinite (version control).
- **Readers**: `CompiledPromptArtifact` consumers + `SovereignLLMGateway` signature verification.

### 2.7 Golden state (`STORE-GOLDEN-STATE`)

- **Creation**: curated; writers in `system_learning/golden/**`.
- **Retention**: git-tracked; indefinite.
- **Readers**: eval judges + arbitration.

## 3. Cache / semi-persistent stores

### 3.1 Redis ADG hot cache (`STORE-REDIS-ADG-HOT`)

- **Creation**: `PIPE-ADG-REDIS-INGEST`.
- **Invalidation**: new snapshot id supersedes; `--force` flushes old namespace.
- **TTL**: none (per `redis_health.expires=1` — effectively no expiry).
- **Hot sentinel**: `adg:v1:<ts>:_hot` gates MCP Redis-first path.
- **Fallback**: `tools/adg/mcp/server.py` falls back to SQLite on cache miss.

### 3.2 Redis coordination / RAG / generic cache

- **Owner**: `agentic_core/cache/redis_cache_client.py` (G2 chokepoint bridge, fan=70/70).
- **TTL**: per key-builder recipe; not globally enforced.
- **Invalidation**: no global flush path. `mcp9_redis_flush_namespace` is the operator-level tool.

### 3.3 Redis bench (orphan, `STORE-REDIS-BENCH`)

- **Status**: 11,228 keys with no current writer.
- **Recommendation**: flush via `mcp9_redis_flush_namespace(pattern="bench:*")`.

### 3.4 GPTCache (`STORE-GPTCACHE`)

- **Creation**: `agentic_core/L4_state/cache/gptcache_client.py::__init__` → `self.cache_dir.mkdir` (L4 critical-write per G2).
- **Invalidation**: manual (delete cache dir).
- **Retention**: indefinite on disk; semantic-similarity dedup within.

### 3.5 In-process vector cache

- Process-lifetime only. No disk.
- Reset on process exit.

## 4. Vector stores

See `vector_collections.md` for full detail.

- **`STORE-CHROMA-CANONICAL`**: 11 collections, 56 HNSW dirs, ~10.2 GB. No auto-prune.
- **`STORE-CHROMA-ARTEFACT`**: 2 collections, registry-only (188 KB). Vestigial.
- **`STORE-CHROMA-SPARSE`**: sparse-vector cache under `data/cache/sparse/`. Owner not enumerated.

## 5. Disk artefacts

### 5.1 Reports (`STORE-REPORTS`) — largest by file count

- **Size**: `artifacts/reports/` = 188.8 MB across 2,687 files.
- **Writers**: CI gate scripts, diagnostic runners, memory purge telemetry.
- **Retention**: none. Largest long-term accumulator.
- **B7-G4-01**: retention policy needed.

### 5.2 Evidence bundles (`STORE-EVIDENCE`)

- `artifacts/evidence/`: 115 files / 1.5 MB.
- Used by `PIPE-JUDGE-EVAL` evidence assembler.

### 5.3 HITL packets (`STORE-HITL`)

- `artifacts/hitl/`: 1 file / 0.3 MB.
- Authored during H1 freeze; no auto-prune.
- Lifecycle tied to `PIPE-EVAL-HITL` state machine (`SM-02`).

### 5.4 Runtime-ADG traces

- `artifacts/runtime_adg/` + `artifacts/runtime_adg_snapshots/`: 0.5 MB total.
- Per-request traces.
- Feed `otel_mcp` and `PIPE-REPLAY`.

### 5.5 CI scan outputs

- `artifacts/ci/`, `artifacts/ci_gates/`, `artifacts/guardian_analysis/`, `artifacts/import_health/`, `artifacts/ssot_scans/`, `artifacts/structure/`, `artifacts/audits/`.
- Accumulate per CI run.

### 5.6 Windsurf telemetry

- `artifacts/windsurf/`: 14 files / 0.4 MB. Includes `adg_first_violations.jsonl` (append-only).
- Authored by `.windsurf/scripts/post_*` hooks.

### 5.7 Anomaly watchlist

- `artifacts/adg/adg_anomaly_watchlist_<ts>.json` + `adg_graph_watchlist_<ts>.json`.
- Per-scan; multiple timestamps observed (9 anomaly + 11 graph in top listing).
- Retention: none.

## 6. System-learning subtrees

Per G3 B7-G3-06, `system_learning/` has partial coverage:

| Subtree | Files | Role (inferred) |
|---|---:|---|
| `system_learning/memory/` | 4 | meta-learning memory |
| `system_learning/snapshots/` | 2 | state snapshots |
| `system_learning/runtime_adg/` | 13 | runtime-ADG ingest |
| `system_learning/golden/` | 1 | golden anchors |
| `system_learning/state/` | 2 | pipeline state |
| `system_learning/stores/` | 14 | domain stores |
| `system_learning/telemetry/` | 2 | telemetry |
| `system_learning/provenance/` | 5 | provenance records |
| `system_learning/raw/` | 1 | raw input |
| `system_learning/logs/` | 1 | logs |

Writer / reader attribution deferred to G3b (partial pipeline coverage).

## 7. Transient storage

### 7.1 Logs (`STORE-LOGS`)

- `logs/`: 14 files / 10.7 MB.
- No centralised rotation at repo level. Python `logging.FileHandler` usage scattered.

### 7.2 Test artefacts (`STORE-TEST-ARTIFACTS`)

- `test_artifacts/`, `artifacts/test_g1/`..`artifacts/test_g4/`.
- Test-run-scoped. No runtime role.

## 8. Purge / invalidation surfaces

| Surface | Tool / command | Affects |
|---|---|---|
| Memory stale entity purge | `python tools/memory/purge_sync.py` or `mem_cleanup_stale(older_than_days=N)` | `STORE-MEMORY-SQLITE-CANONICAL` |
| ADG Redis force re-ingest | `python tools/adg/adg_redis_ingest.py --force` | `STORE-REDIS-ADG-HOT` |
| Redis namespace flush | `mcp9_redis_flush_namespace(pattern=..., dry_run=False)` | any Redis namespace |
| Redis single key delete | `mcp9_redis_del_key(key=...)` | single key |
| Chroma collection delete | `vector_db` MCP tool `delete_collection` | single Chroma collection |
| ADG snapshot regen | `python tools/generate_full_adg.py` (or `/adg-redis-refresh`) | `STORE-ADG-SQLITE`, `STORE-ADG-GRAPH-PROJECTION`, `STORE-ADG-JSON-TIERS`; triggers re-ingest |

**No observed automation** for: legacy ADG archive pruning, reports pruning, Chroma collection pruning, logs rotation. All purges are operator-initiated.

## 9. Kill-switch interactions

Per G2b env-key map, these env vars mutate lifecycle behaviour:

| Env var | Effect | Affected stores |
|---|---|---|
| `ADG_SKIP_REDIS` | skip Redis auto-ingest | `STORE-REDIS-ADG-HOT` (stays cold) |
| `ADG_SKIP_GIT` | skip auto-commit | version control of ADG artefacts |
| `ADG_SKIP_SELF_TEST` | skip scanner self-test | none (gate only) |
| `MEMORY_DB` | relocate memory SQLite | selects which of the 3 memory SQLite files is live |
| `VECTOR_DB_CHROMA_PATH` | relocate Chroma store | selects which Chroma store is live |
| `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` | permit HF Hub fetch | gates `EGRESS-HF-HUB-01` → affects `STORE-CHROMA-CANONICAL` ingest |

## 10. Staleness surfaces

| Surface | Indicator | Source |
|---|---|---|
| ADG SQLite vs graph projection | `mcp1_adg_health.graph_projection.stale` | `tools/adg/mcp/server.py` |
| ADG snapshot freshness | `tools/adg/adg_stale_guard.py` | module |
| Redis hot sentinel | `adg:v1:<ts>:_hot` presence | `tools/adg/adg_redis_ingest.py --check` |
| Memory entity age | `updated_at` column | `sqlite_memory_store.py` |
| Dashboard health | `HEALTHY / DEGRADED / CRITICAL / UNKNOWN` | `L6_observability/utils/dashboard/dashboard_aggregate.py` |

## 11. Aggregate size inventory

| Directory | Size | Role |
|---|---:|---|
| `data/cache/` | ~10.5 GB | vector + gptcache + sparse |
| `artifacts/adg/` | 4.9 GB | ADG snapshots + projections + JSON tiers + watchlists |
| `artifacts/_legacy_adg_archives/` | 229 MB | vestigial ADG |
| `artifacts/reports/` | 188.8 MB | reports accumulation |
| `data/snapshots/` | 22.3 MB | cross-repo snapshots |
| `data/corpus/` | 18.8 MB | seed corpus |
| `data/memory/` | 17.5 MB | memory SQLite duplicates |
| `logs/` | 10.7 MB | transient logs |
| other | ~5 MB | everything else catalogued |
| **Total catalogued** | **~15.7 GB** | |

**Largest single file**: `artifacts/adg/adg_indexed_<older>.sqlite` (up to 294 MB per snapshot).

## 12. Summary and handoff items

| Item | Status |
|---|---|
| All mandatory surfaces catalogued | ✓ |
| Pipeline linkage complete | ✓ (via `pipelines_using_it` field in catalogue) |
| Retention policies documented where present | ✓ (most: "none observed") |
| Purge / invalidation surfaces enumerated | ✓ (§8) |
| Duplicate / orphan stores flagged | ✓ (3 memory SQLite, 3 Chroma, `bench:*`, legacy ADG archives) |
| Staleness detection surfaces | ✓ (§10) |

**Key lifecycle risks**: no auto-pruning on any of the large accumulators (ADG snapshots, reports, Chroma collections). Operational burden will grow monotonically.
