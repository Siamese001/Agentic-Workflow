# G4 — Storage and Infrastructure Topology

## 1. Sub-wave ID, title, one-line purpose

**G4** — *Storage and Infrastructure Topology*. Catalogue every persistent and semi-persistent storage surface in the repo with owners, readers, writers, lifecycle, and pipeline linkage, using G1/G1b/G2/G2b/G3 as the baseline.

## 2. Inputs

- **ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611). `adg_health` = healthy; `graph_projection.stale = false`. Same snapshot as G1 through G3.
- **G0 planning**: `output_contracts.md` §"Storage catalogue schema (G4)", `runtime_scope_map.md`, `dependency_and_risk_register.md`.
- **G1 / G1b**: `component_inventory.yaml`, `app_inventory.yaml`.
- **G2**: `import_edge_matrix.md` (cache/redis_cache_client fan=70/70 chokepoint), `boundary_violations.md` (L4 critical-write bucket: 7 `mkdir` + dict-`copy` sites), `canonical_request_walk.md`, `seam_usage_report.md`.
- **G2b**: `egress_points.yaml` (EGRESS-REDIS-01, EGRESS-NEO4J-01, EGRESS-HF-HUB-01, MCP loopback bucket), `provider_inventory.md` §P09 (ChromaDB embedded — NOT egress), `env_key_consumer_map.md` (MEMORY_DB, VECTOR_DB_CHROMA_PATH, REDIS_*, ADG_REDIS_URL).
- **G3**: `pipeline_catalogue.yaml` (17 pipelines; each store cross-linked via `pipelines_using_it`), `state_machines.md` (SM-06 MemoryEntity lifecycle, SM-07 Redis hot sentinel, SM-09 ADG staleness).
- **Live probes**: `mcp1_adg_health` (ADG snapshot ID + paths), `mcp9_redis_health` (2.38 M keys / 1.67 GB / expires=1), `mcp9_redis_namespace_stats` (adg=38,803; bench=11,228 in 50 k sample), `mcp9_redis_keys(pattern="adg:v1:*:_hot")` (1 current hot snapshot).
- **Filesystem inventory**: recursive file-count + size scan of `artifacts/`, `data/`, `logs/`, `test_artifacts/`, `system_learning/` subtrees. ChromaDB registry introspection (11 + 2 collections across two SQLite registries).

## 3. Outputs

- `README.md` — this index.
- `storage_catalogue.yaml` — **33 storage entries** conforming to G0 schema (+ the required `owner_modules`, `writer_modules`, `reader_modules`, `durability`, `retention_behavior`, `pipelines_using_it`, `notes` fields).
- `redis_namespace_map.md` — 6 namespaces + 1 orphan, per-namespace owner/writer/reader, ADG key schema, TTL audit.
- `vector_collections.md` — 11 canonical collections + 2 artefact collections + sparse cache, with per-collection owner/reader/pipeline binding.
- `artefact_lifecycle.md` — retention, staleness, purge/invalidation, kill-switches, aggregate size inventory.

## 4. Stop condition

Met.

- **All mandatory surfaces catalogued**:
  1. ADG SQLite artefacts → `STORE-ADG-SQLITE`, `STORE-ADG-GRAPH-PROJECTION`, `STORE-ADG-JSON-TIERS`, `STORE-ADG-LEGACY-ARCHIVES`, `STORE-ADG-RUNTIME-TRACES`, `STORE-ADG-ANOMALY-WATCHLIST`.
  2. Memory SQLite artefacts → `STORE-MEMORY-SQLITE-CANONICAL` + duplicates (`STORE-MEMORY-SQLITE-DUPLICATE`, `STORE-MEMORY-UNIFIED-DB`).
  3. Redis namespaces and hot-cache behaviour → 6 namespaces in `redis_namespace_map.md` + SM-07 state machine.
  4. ChromaDB / vector-store surfaces → `STORE-CHROMA-CANONICAL` (11 collections), `STORE-CHROMA-ARTEFACT` (2), `STORE-CHROMA-SPARSE` + `vector_collections.md`.
  5. Neo4j → `STORE-NEO4J`.
  6. App output/data directories → `STORE-REPORTS`, `STORE-EVIDENCE`, `STORE-HITL`, `STORE-CI-SCAN-OUTPUTS`, `STORE-WINDSURF-TELEMETRY`, etc.
  7. `artifacts/`, `data/`, `logs/`, `test_artifacts/`, `system_learning/` all enumerated in §5-7 of `artefact_lifecycle.md`.
  8. `infrastructure/` — G1 already classified; no new storage owned directly by this subtree beyond transport via `infrastructure/sdks_mcps/` (provider wrappers, not storage).
  9. Local cache directories + manifest/registry paths → `STORE-GPTCACHE`, `STORE-MEMORY-MANIFESTS`, `STORE-CORPUS`, `STORE-RAG-SEEDS`, `STORE-SNAPSHOTS`, `STORE-GOLDEN-STATE`, `STORE-PROMPT-GOVERNANCE`.
  10. Retention / staleness / purge / regeneration behaviour → `artefact_lifecycle.md` §§2, 3, 8, 9, 10.

- **Schema validation**: every entry records `id`, `kind`, `path_or_namespace`, `owner_modules`, `writer_modules`, `reader_modules`, `durability`, `retention_behavior`, `pipelines_using_it`, `notes`. Required `owner_modules` and `pipelines_using_it` fields populated (some explicitly `[]` for orphans/legacy, which is honest attribution — not omission).

- **Top-level storage taxonomy reconciled to `storage_catalogue.yaml::kind` (source of truth)**:
  - `disk_artefact`: **16**
  - `sqlite`: **5**
  - `redis`: **5**
  - `vector`: **3**
  - `in_process_cache`: **1**
  - `transient_output`: **1**
  - `test_only`: **1**
  - `other`: **1**
  - **Total**: **33**
- **Orphan / vestigial tally (reporting label, not a `kind`)**: **3**
  - `STORE-ADG-LEGACY-ARCHIVES`
  - `STORE-REDIS-BENCH`
  - `STORE-CHROMA-ARTEFACT`
- **Durability language reconciliation**:
  - Use `durability` values in `storage_catalogue.yaml` (`durable`, `ephemeral_cache`, `persistent_cache`, `transient`, `test_only`) as authoritative.
  - Treat phrases like "authoritative durable" as descriptive wording only, not a separate taxonomy class.

- **Pipeline-to-storage linkage complete**: every G3 pipeline that touches durable / cache state is cross-referenced in `storage_catalogue.yaml pipelines_using_it`. PIPE-ADG-GEN, PIPE-ADG-REDIS-INGEST, PIPE-MEMORY-LIFECYCLE, PIPE-APP-REQUEST, PIPE-EVAL-HITL, PIPE-VECTOR-RETRIEVAL, PIPE-EMBEDDING, PIPE-JUDGE-EVAL, PIPE-OBSERVABILITY, PIPE-HEALING all bound.

- **G2 / G2b signals consumed explicitly**:
  - Redis chokepoint (`cache/redis_cache_client.py` fan=70/70) → bound into `STORE-REDIS-CACHE-GENERIC` ownership.
  - L4 critical-write sovereignty bypasses (7 sites) → bound into `STORE-GPTCACHE`, `STORE-MEMORY-MANIFESTS`, and the vector persist-dir write noted in `vector_collections.md` §7.
  - vector_db / HF / Chroma split → `vector_collections.md` §§5 + `STORE-CHROMA-*`.
  - Neo4j store → `STORE-NEO4J`.
  - Memory lifecycle + purge → `STORE-MEMORY-SQLITE-CANONICAL` + `artefact_lifecycle.md` §2.3, §8.
  - ADG snapshot freshness / Redis hot sentinel → `SM-07 / SM-09` references + `redis_namespace_map.md` §2.

- **Honest gaps recorded** — see §5.

## 5. Risks encountered during execution

- **Memory SQLite triplet ambiguity** (`STORE-MEMORY-SQLITE-CANONICAL`, `STORE-MEMORY-SQLITE-DUPLICATE`, `STORE-MEMORY-UNIFIED-DB`): three SQLite files across two directories. Canonical determined by `MEMORY_DB` env default, not by code enforcement. Recorded as **B7-G4-03** rather than resolved — G4 does not reconcile live vs stale copies.
- **ChromaDB registry vs HNSW mismatch**: `artifacts/chromadb/chroma.sqlite3` registers 2 collections but has no adjacent HNSW persist dirs. `data/cache/chromadb/` has 11 registered collections but 56 HNSW dirs. Cannot verify which HNSW dir maps to which collection without reading binary manifests — recorded at collection-level granularity only. **B7-G4-05**.
- **`system_learning/` subtree storage attribution partial**: per G3 B7-G3-06, system_learning has 28+ subpackages only partially traced. G4 catalogues the visible subdirectories (`memory/`, `snapshots/`, `runtime_adg/`, `stores/`, `telemetry/`, `provenance/`, `raw/`, `logs/`) but does not attribute owner/writer for each. Deferred to G3b / G4b.
- **Redis TTL discipline**: `redis_health.expires=1` means effectively no TTL. Flagged in `redis_namespace_map.md` §5 as operational risk.
- **ADG retention absent**: 4.9 GB in `artifacts/adg/` + 229 MB in `_legacy_adg_archives/` with no auto-prune. Operational burden grows monotonically. **B7-G4-01 / B7-G4-02**.
- **Embedded-local-vs-network-egress boundary respected**: ChromaDB catalogued here as embedded local, explicitly NOT reclassified as egress. Consistent with G2b provider_inventory.md §P09.
- **Did not invent retention policies**: where no policy was observed, `retention_behavior` records "none observed" or "no auto-pruning observed" — not a fabricated SLA.
- **Did not reclassify providers**: Neo4j / Redis / HF Hub remain the egress points catalogued by G2b; G4 adds storage metadata only.

## 6. B7 candidates surfaced

- **B7-G4-01** — **ADG retention policy missing**. `artifacts/adg/` (4.9 GB, 166 files) and `artifacts/reports/` (188.8 MB, 2,687 files) accumulate without pruning. Add retention config + purge tool.
- **B7-G4-02** — **`artifacts/_legacy_adg_archives/`** (229 MB, 1,162 files). Vestigial. No readers, no writers. Candidate for deletion or cold-storage move.
- **B7-G4-03** — **Memory SQLite triplet ambiguity**. Declare one canonical location in code (not just env default); reconcile or partition the other two.
- **B7-G4-04** — **Redis `bench:*` orphan namespace** (11,228 keys). No current writer in repo. Flush.
- **B7-G4-05** — **`artifacts/chromadb/chroma.sqlite3`** is a registry-only vestigial Chroma. Consolidate with the canonical `data/cache/chromadb/` or delete.
- **B7-G4-06** — **L4 direct-infra-write sites** (propagated from G2 boundary_violations.md + added `persist_dir.mkdir` in `retrieval_layers.py`). Either (a) formalise "mkdir is outside UWG scope" in v1.4, or (b) mediate dir-creation through UWG.
- **B7-G4-07** — **Redis ops posture**: `expires=1` (no TTL discipline), no eviction policy, single master at localhost, no shard strategy. Dev-only posture documented; not suitable for production.

## 7. Hand-off note for G4b and G5

### For G4b (control-plane / config-knob catalogue)

- G4 catalogued the **stores**; G4b catalogues the **knobs** that control them. Explicit hand-off items:
  - `MEMORY_DB` → which of the 3 memory SQLite files is live.
  - `VECTOR_DB_CHROMA_PATH` → which Chroma store is live.
  - `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_PASSWORD` / `REDIS_URL` / `ADG_REDIS_URL` → Redis binding.
  - `ADG_DIR`, `ADG_SKIP_REDIS`, `ADG_SKIP_GIT`, `ADG_SKIP_SELF_TEST` → ADG pipeline.
  - `VECTOR_DB_ALLOW_MODEL_DOWNLOAD`, `HF_HUB_OFFLINE`, `BGE_ALLOW_MODEL_DOWNLOAD` → embedding egress.
  - All 8 `VECTOR_DB_*_TIMEOUT` knobs → vector retrieval budgets.
- G4b should classify each knob as `secret` / `provider_config` / `runtime_tunable` / `feature_flag` / `path_override` / `retention_policy` and record defaults.

### For G5 (deployment / ops / MCP-server registry)

- Every durable store has deployment implications. G5 must record:
  - ADG snapshot lifecycle automation (CI regeneration cadence + retention enforcement).
  - Redis deployment posture (master/replica, eviction, TTL — B7-G4-07).
  - Chroma persist-path volumes + backup strategy.
  - Neo4j deployment (external dependency; auth model per G2b).
  - Memory SQLite backup + canonical location enforcement (B7-G4-03).
  - OTel collector binding (optional EGRESS-OTEL-01).
  - MCP server registry: already scoped in G2b `mcp_as_transport.md` — G5 adds deployment metadata.

- **G4 signs off**. **G4b can start immediately.** **G5 can start immediately in parallel** — only dependency is `storage_catalogue.yaml` (frozen here).

## Summary counts

| Dimension | Value |
|---|---:|
| Storage surfaces catalogued | **33** |
| Durable stores | 25 |
| Ephemeral cache stores | 5 |
| Persistent cache | 1 |
| Transient output | 1 |
| Test-only | 1 |
| Storage kind: sqlite / redis / vector / disk_artefact / in_process_cache / other / transient_output / test_only | 5 / 5 / 3 / 16 / 1 / 1 / 1 / 1 |
| Orphan / vestigial stores flagged | 4 (bench Redis, legacy ADG archives, artefact Chroma, unified_memory.db) |
| Redis namespaces | 6 (+ 1 orphan) |
| Chroma collections (canonical) | 11 |
| Chroma collections (artefact) | 2 |
| Total catalogued disk footprint | ~15.7 GB |
| B7 candidates surfaced | 7 |
| Mandatory surfaces covered | 10 / 10 |
