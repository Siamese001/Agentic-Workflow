---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\embedding-population-index-lifecycle-plan-5c8684.md'
original_relative_path: 'embedding-population-index-lifecycle-plan-5c8684.md'
source_sha256: 1c3ab7a61e2d694485376a7200a8cc88e7e0b8c97630287acf0bdcb6f036997c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan A: Embedding Population and Index Lifecycle

Population owns determinism: extract, embed, canonicalize, build, version, prune, and rebuild FAISS indexes on local 4TB SSD with byte-reproducible artifacts and strict governance.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## SCOPE

- Data extraction and canonicalization from healing outcomes, telemetry events, DPO pairs
- Embedding batch generation via existing `EmbeddingSovereignAgent` / `BatchEmbeddingService`
- Local SSD cache layout and partition organization
- FAISS IVFPQ training, build, save with fixed seed
- Retention lifecycle: per-type TTL + drift-based pruning
- Rebuild-after-prune with deterministic re-sort
- Index versioning: `index_version_hash`, FAISS version pin, build metadata

---

## OUT OF SCOPE

- Query-time similarity search (Plan B)
- Proposer wiring or ChangePackage generation (Plan B)
- Any authority enforcement or routing decisions (Plan B)

---

## CONTRACT (Interface to Plan B)

```python
@dataclass(frozen=True, slots=True)
class IndexBuildMetadata:
    """Stable contract consumed by Plan B."""
    index_id: str                   # e.g., "healing_contexts_v1"
    faiss_version: str              # e.g., "1.7.4"
    build_seed: int                 # Always 42
    canonicalization_version: str   # e.g., "canon-v1"
    embedding_model_version: str    # e.g., "text-embedding-004-v1"  ← REQUIRED
    embedding_model_checksum: str   # SHA-256 of embedder identifier/weights hash  ← REQUIRED
    built_at_utc: int               # Injected, no wall clock
    index_version_hash: str         # SHA-256 of serialized index bytes
    vector_count: int
    dimension: int
    # INVARIANT: If embedding_model_version or embedding_model_checksum changes,
    # the index is invalid and must be fully rebuilt before reads are permitted.

class LocalFAISSStore:
    def open(self, index_id: str) -> tuple[Any, str, IndexBuildMetadata]:
        """Returns (index_handle, index_version_hash, build_metadata)."""
        ...

    def search(
        self, index_id: str, query_vector: list[float], top_k: int, cutoff: float
    ) -> list[tuple[str, str, float]]:
        """Returns [(content_hash, trace_id, score_round6)].
        Post-sort: (score_round6 DESC, content_hash ASC) — deterministic.
        """
        ...
```

---

## DETERMINISM INVARIANTS

```
D1. FAISS training: fixed seed=42 always. No override.
D2. Insertion order: global sort by (source_file_path ASC, record_index ASC) before any write.
D3. Vector normalization: unit L2 norm applied before storage, verified post-load.
D4. Search results post-sort: (round(score, 6) DESC, content_hash ASC) — tiebreak is deterministic.
D5. No concurrent index mutation: single-writer enforced via file lock.
D6. Rebuild-after-prune required: pruning invalidates index_version_hash; rebuild must run before index is readable.
D7. Index byte-reproducibility: same corpus + same seed → same serialized index bytes (verified in acceptance test).
D8. Within each record, canonical JSON serialization must be applied before embedding text extraction:
    - keys sorted ASC, no trailing whitespace, separators=(",", ":"), encoded as UTF-8.
    - Any raw JSON with whitespace/ordering drift produces a different content_hash and is rejected.
D9. Embedding model change invalidates all indexes: rebuild required before any search is permitted.
    Detected by: stored embedding_model_checksum != current embedder checksum.
```

---

## SSD LAYOUT

```
{base_path}/                         # e.g., /data/embeddings
├── indexes/
│   ├── healing_contexts/
│   │   ├── current.faiss            # Active FAISS index
│   │   ├── current.meta.json        # IndexBuildMetadata (canonical JSON)
│   │   └── archive/                 # Pruned versions (retained for replay)
│   ├── telemetry_events/
│   │   ├── current.faiss
│   │   └── current.meta.json
│   └── dpo_pairs/
│       ├── current.faiss
│       └── current.meta.json
├── embedding_cache/
│   ├── healing_contexts/            # LZ4-compressed .bin chunks (100K each)
│   ├── telemetry_events/
│   └── dpo_pairs/
└── raw_staging/                     # Temporary; cleared after population
```

---

## RETENTION LIFECYCLE

| Index | Retention | Prune Strategy | Governance Layer | Rebuild Required |
|---|---|---|---|---|
| `healing_contexts` |  | Drift-based (remove low-use patterns) | L6 → L4 write | Yes |
| `telemetry_events` |  | Rolling window eviction | L6 observe only | Yes |
| `dpo_pairs` | Permanent (versioned) | None; append-only | L4 content-hash | On new version only |

---

## KEY NEW COMPONENTS

### `LocalFAISSStore`
```
Location: system_learning/engines/local_faiss_store.py
Responsibilities:
  - train(index_id, vectors, seed=42)
  - add(index_id, vectors, metadata)
  - save(index_id) -> index_version_hash
  - load(index_id) -> (index, metadata)
  - search(index_id, query, top_k, cutoff) -> deterministic results
  - prune(index_id, predicate) -> invalidates hash; marks rebuild_required=True
FAISS params: IndexIVFPQ, nlist=2048, M=64, nbits=8
```

### `LocalEmbeddingPopulationService`
```
Location: system_learning/engines/local_embedding_population_service.py
Responsibilities:
  - Orchestrates extraction → embed → normalize → write pipeline
  - Deterministic file ordering (D2)
  - Canonical JSON serialization per record before embed text extraction (D8)
  - Chunked batch writing (BATCH_SIZE=5000)
  - MAX_WORKERS=8 for embedding; single-writer for index (D5)
  - Captures embedding_model_version + embedding_model_checksum at build time
  - Emits IndexBuildMetadata on completion (including embedder fields)
```

### `EmbeddingRetentionScheduler`
```
Location: ops_scripts/maintenance/embedding_retention_scheduler.py
Responsibilities:
  - Per-index TTL enforcement
  - Drift-based pruning signal consumption from L4
  - Triggers rebuild after prune (D6)
  - Updates IndexBuildMetadata with new index_version_hash
```

---

## STORAGE ESTIMATES

| Item | Size | Notes |
|---|---|---|
| Healing embeddings (768-dim, 1M contexts) | ~200GB | LZ4: ~80GB on disk |
| Telemetry embeddings (384-dim, 30-day window) | ~80GB | LZ4: ~35GB on disk |
| DPO embeddings (768-dim, 100K pairs × 2) | ~50GB | LZ4: ~20GB on disk |
| FAISS IVFPQ indexes | ~300GB | Compressed index structures |
| L4 versioned metadata | ~20GB | `meta.json` + archive |
| Raw staging (temp) | ~150GB | Cleared post-population |
| **Total active** | **~650GB** | Well within 4TB partition |

---

## FAISS CONFIGURATION

```python
class FAISSConfig:
    SEED = 42
    NLIST = 2048      # IVF cells — optimized for SSD random access
    M = 64            # PQ subquantizers
    NBITS = 8         # Bits per subquantizer
    NPROBE = 64       # Cells to probe at query time
    BATCH_SIZE = 5000 # Optimal for SSD sequential write
    COMPRESSION = "lz4"
    DIMENSION_HEALING = 768    # text-embedding-004
    DIMENSION_TELEMETRY = 384  # all-MiniLM-L6-v2
    DIMENSION_DPO = 768        # text-embedding-004
```

---

## ACCEPTANCE CRITERIA

1. **Rebuild reproducibility**: Given identical input corpus, two independent builds produce `index_version_hash` equality and identical top-5 nearest neighbors for a fixed 100-query test set.
2. **Prune determinism**: After pruning N vectors, `index_version_hash` changes; re-querying pruned `trace_id`s returns no results.
3. **Metadata completeness**: Every `current.meta.json` contains `faiss_version`, `build_seed`, `canonicalization_version`, `embedding_model_version`, `embedding_model_checksum`, `index_version_hash`, `vector_count`, `dimension`, `built_at_utc`.
4. **No concurrent mutation**: Attempting parallel writes raises `IndexWriteLockError`.
5. **Retention enforcement**: Telemetry embeddings older than  are absent from index after prune cycle.

---

## IMPLEMENTATION PHASES

| Week | Deliverable |
|---|---|
| 1 | `LocalFAISSStore` skeleton + SSD partition layout + `IndexBuildMetadata` type (with embedder fields) |
| 2 | `LocalEmbeddingPopulationService` + deterministic batch pipeline |
| 3 | Historical data ingestion: healing + telemetry + DPO |
| 4 | Retention scheduler + prune/rebuild cycle |
| 5 | Acceptance tests (D7 reproducibility + prune determinism) |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

