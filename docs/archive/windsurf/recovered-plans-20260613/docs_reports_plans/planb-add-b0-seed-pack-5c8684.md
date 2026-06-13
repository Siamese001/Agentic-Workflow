# Plan B Phase B0 — Seed Embedding Pack Bootstrap

Add Phase B0 to Plan B before B1 to provide a governed, deterministic bootstrap embedding snapshot that enables immediate similarity-based proposals without waiting for full historical ingestion.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Changes to planB_refreshed.md

### 1. Insert new Phase B0 section before current B1

**Location**: After §1 (Plan A Completed Artifacts), before §2 (Plan B Phase Definitions)

**Content**:
```markdown
## 2. Phase B0 — Seed Embedding Pack (Bootstrap Snapshot)

**Objective**: Provide a governed, deterministic embedding snapshot available immediately to drive similarity-based proposals from day 1, without waiting for full historical corpus ingestion.

**New files**:
- `system_learning/engines/seed_embedding_pack_builder.py`
- `system_learning/types/seed_embedding_pack_types.py`

**Artifacts**:
```
@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackManifest:
    embedding_model_version: str
    embedding_model_checksum: str  # 64-hex SHA-256
    canonicalization_version: str
    dimensions: int                # MUST match IndexBuildMetadata.dimension
    vector_count: int
    index_version_hash: str        # from Plan A IndexBuildMetadata
    matrix_hash: str               # SHA-256 of embeddings.f32 bytes
    built_at_utc: int
    bootstrap_mode: str            # "minimal_seed" | "curated_seed"

    def to_canonical_json_bytes() -> bytes: ...
```

**File layout** (per namespace):
```
<base_path>/seed_packs/<namespace>/
  row_index.jsonl          # canonical sort by (content_hash ASC, trace_id ASC)
                           # fields: row_id, content_hash, trace_id, namespace, created_utc
  embeddings.f32           # float32 little-endian, row-aligned to row_index
  seed_manifest.json       # SeedEmbeddingPackManifest canonical JSON
```

**Bootstrap modes**:

**Mode 1: Minimal seed (fast start)**
- Select first N records from Plan A JSONL corpus after canonical sort
- Deterministic selection: `sorted(records, key=lambda r: (r['content_hash'], r['trace_id']))[:N]`
- N configurable (e.g., 100 for smoke tests, 1000 for production bootstrap)

**Mode 2: Curated seed (higher quality)**
- Hand-curated list of `(trace_id, content_hash)` tuples from known-good cases
- Still sorted canonically before embedding
- Provides better signal-to-noise on day 1

**Invariants**:
- Seed Pack is **read-only** after build; no incremental updates
- If Seed Pack missing → `MetaLearningEmbeddingService` (B2) returns neutral empty artifact
- If Seed Pack present → service produces stable `index_version_hash` and NN-set across repeated runs
- Dimensions read from manifest at runtime; never hardcoded in Plan B code
- `matrix_hash` = SHA-256 of entire `embeddings.f32` file bytes (deterministic)

**Tests** (`tests/unit_min_deps/system_learning/test_seed_embedding_pack_b0.py`):
1. `test_minimal_seed_deterministic` — same corpus + same N → same row_index + same matrix_hash
2. `test_curated_seed_deterministic` — same curated list → same output
3. `test_manifest_dimensions_match_embeddings` — manifest.dimensions == embeddings.shape[1]
4. `test_row_index_canonical_sort` — rows sorted by (content_hash, trace_id)
5. `test_matrix_hash_matches_file_bytes` — manifest.matrix_hash == SHA-256(embeddings.f32)
6. `test_missing_seed_pack_returns_empty_artifact` — graceful degradation in B2
7. `test_seed_pack_read_only` — no write methods exposed

**Acceptance gate**: `python -m pytest -q --color=no tests/unit_min_deps/system_learning/test_seed_embedding_pack_b0.py` exits 0.
```

### 2. Renumber existing phases

- Current B1 → becomes B1 (no change, but now follows B0)
- Current B2 → update to consume Seed Pack
- Current B3-B6 → no changes needed

### 3. Update B2 to consume Seed Pack

**Add to B2 Invariants section**:
```markdown
- `MetaLearningEmbeddingService` constructor accepts optional `seed_pack_path: Path | None`
- If `seed_pack_path` is None or missing → returns neutral empty artifact (graceful degradation)
- If Seed Pack present → loads manifest, validates `matrix_hash`, opens read-only index
- Seed Pack is never mutated; all operations are read-only queries
```

**Add to B2 Tests**:
```markdown
9. `test_seed_pack_loaded_on_construction` — manifest validated, matrix_hash checked
10. `test_missing_seed_pack_graceful_degradation` — returns empty artifact, no exception
11. `test_seed_pack_read_only_enforced` — no write operations possible
```

### 4. Update B3 ReplayValidator

**Add to B3 Invariants**:
```markdown
- `validate_seed_pack_stable()` — two independent loads of same Seed Pack → identical `index_version_hash` and `matrix_hash`
- NN-set equality test includes Seed Pack scenario
```

**Add to B3 Tests**:
```markdown
6. `test_seed_pack_replay_stable` — load twice → identical hashes
7. `test_nn_set_stable_with_seed_pack` — same query on Seed Pack → same NN-set
```

### 5. Update Execution Order section

**Change from**:
```
B1 → B2 → B3 → B4 → B5 → [gate check] → B6 → B7+
```

**To**:
```
B0 → B1 → B2 → B3 → B4 → B5 → [gate check] → B6 → B7+
```

### 6. Update File Inventory

**Add to source files**:
```
system_learning/engines/seed_embedding_pack_builder.py   # B0
system_learning/types/seed_embedding_pack_types.py       # B0
```

**Add to test files**:
```
tests/unit_min_deps/system_learning/test_seed_embedding_pack_b0.py
```

**Update totals**:
```
**Total new files**: 16 (10 source + 6 test)
```

## Rationale

- **Immediate availability**: B0 provides embeddings on day 1 without waiting for full historical ingestion
- **Governed**: Seed Pack has manifest with hashes, canonical sort, deterministic build
- **Graceful degradation**: Missing Seed Pack → neutral empty artifact (Plan B works without it)
- **Read-only**: Seed Pack never mutated; all Plan A write paths remain exclusive to Plan A
- **Deterministic**: Same inputs → same `matrix_hash`, `index_version_hash`, NN-sets

## Scope

- **1 file modified**: `artifacts/windsurf/planB_refreshed.md`
- **No source files yet** (B0 implementation comes after plan approval)
- Commit message: "plan: add Phase B0 Seed Embedding Pack bootstrap to Plan B"

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

