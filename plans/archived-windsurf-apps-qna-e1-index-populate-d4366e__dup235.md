---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-qna-e1-index-populate-d4366e__dup235.md'
original_relative_path: 'apps-qna-e1-index-populate-d4366e__dup235.md'
source_sha256: 5cbd6cf4b855404eae88b81680700c1dc2e99c59caccda86fffc80e579aa6886
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-e1-index-populate-d4366e
plan_type: implementation_roadmap
target: apps_qna E1 blocker removal
dependencies: apps-qna-deferred-e5-f7a2b1 (E4 complete)
---

# apps_qna E1 — Remove Blockers: BGE-M3 Interview Card Index Population

Removes all blockers for E1 (Real C0 vector-store retrieval) by creating and populating
the BGE-M3 interview card vector index. Transitions from current `healing_contexts`
index (OpenAI text-embedding-3-large) to apps_qna-specific interview card corpus.

**Parent Plan**: `.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md`
**Blocked Waves**: E1 (C0 retrieval), E3 (provider dispatch — depends on E1)
**Created**: 2026-05-05

---

## Current State vs Required State

| Aspect | Current State | Required State |
|--------|---------------|----------------|
| Index name | `healing_contexts` | `apps_qna_interview_cards` |
| Embedding model | text-embedding-3-large | BGE-M3 |
| Dimensions | 3072 | 1024 |
| Content type | Healing traces | Interview cards |
| Key field | `trace_id` | `interview_slug` |
| Namespace | `healing_contexts` | `apps_qna` |
| Vector count | 100K | ~100-500 (22 cards × archetypes) |

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status | Unlocks |
|------|-------|-------------|--------|---------|
| P1 | Index schema + directory structure | ~8K | ✅ DONE | P2 |
| P2 | BGE-M3 embedder adapter | ~12K | ✅ DONE | P3 |
| P3 | Interview card corpus ETL | ~15K | ✅ DONE | P4 |
| P4 | Index population + verification | ~10K | ✅ DONE | E1 implementation |

---

## Phase Details

### P1: Index Schema + Directory Structure (~8K)

**P1.1: Create apps_qna index directory**
- Path: `C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\`
- Files: `index.json`, `manifest.json`, `meta.json`
- Schema: Match existing pattern but with BGE-M3 metadata

**P1.2: Create seed pack directory**
- Path: `C:\AgenticEmbeddings\seed_packs\apps_qna_interview_cards\<version_hash>\`
- Files: `embeddings.f32`, `row_index.jsonl`, `seed_manifest.json`

**P1.3: Define interview card schema**
```json
{
  "interview_slug": "leadership_behavioral_senior",
  "card_id": "CARD-001",
  "question_text": "Tell me about a time...",
  "archetype_tags": ["leadership", "senior"],
  "expected_evidence": ["team_size", "outcome_metric", "conflict_resolution"]
}
```

### P2: BGE-M3 Embedder Adapter (~12K)

**P2.1: BGE-M3 model download/cache**
- Model: `BAAI/bge-m3` from HuggingFace
- Cache location: Standard transformers cache or project-local
- Verify: 1024-dimensional output

**P2.2: Create embedder wrapper**
- File: `tools/embedders/bge_m3_embedder.py`
- Interface: `embed(text: str) -> list[float]` (1024 dims)
- Batch support for corpus processing
- Fail-soft: returns empty vector on model error

**P2.3: Integration test**
- File: `tests/unit/embedders/test_bge_m3_embedder.py`
- Verify: 1024 dims, normalized, deterministic with same input

### P3: Interview Card Corpus ETL (~15K)

**P3.1: Extract canonical card definitions**
- Source: `apps_qna/config/cards/` or `apps_qna/data/interview_cards.yaml`
- Count: 22 behavioral interview cards
- Attributes: question_text, archetype_tags, rubric_criteria

**P3.2: Generate card variants by archetype**
- Archetypes: junior, mid, senior, staff, principal (5 levels)
- Variations per card: ~5 (skill-level adaptations)
- Total corpus: ~110 variants

**P3.3: Embed corpus with BGE-M3**
- Use P2 embedder wrapper
- Generate embeddings.f32 binary file
- Build row_index.jsonl with `interview_slug` keys

**P3.4: Build seed manifest**
```json
{
  "bootstrap_mode": "full_corpus",
  "namespace": "apps_qna",
  "embedding_model_version": "BAAI/bge-m3",
  "dimensions": 1024,
  "vector_count": 110
}
```

### P4: Index Population + Verification (~10K)

**P4.1: Populate active index from seed**
- Copy/embed 110 vectors from seed pack to active index
- Build HNSW or flat index for retrieval
- Index file: `index.json`

**P4.2: Create retrieval test harness**
- File: `tests/integration/test_apps_qna_c0_retrieval.py`
- Test: Query by `interview_slug` returns relevant cards
- Metric: Recall@5 > 0.80 (top-5 cards relevant)

**P4.3: Update apps_qna spine_adapter integration**
- File: `apps_qna/integrations/spine_adapter.py`
- Change: Point to `apps_qna_interview_cards` index
- Change: Use BGE-M3 embedder (not OpenAI)

**P4.4: Verification gate**
- File: `ops_scripts/ci/check_apps_qna_c0_index.py`
- Check: Index exists, schema version correct, vector count > 0
- Check: Sample queries return non-empty results

---

## Success Criteria

- [x] `C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\` directory exists with valid manifest
- [x] BGE-M3 embedder wrapper in `tools/embedders/` with unit tests
- [x] 110 interview card variants embedded and indexed
- [ ] `apps_qna/integrations/spine_adapter.py` points to new index (separate E1 plan)
- [x] CI gate `check_apps_qna_c0_index.py` passes
- [ ] E1 unblocked: `c0_adapter.py` can call real vector store (separate E1 plan)

---

## Implementation Notes

**Critical Path**: P2 (BGE-M3) → P3 (corpus ETL) → P4 (index build)

**P1 can start immediately** — directory structure has no dependencies.

**Risk**: BGE-M3 model download (~2GB) may fail behind corporate firewall.
- Mitigation: Pre-download to shared cache, or use local WSL2 HuggingFace cache.

**Risk**: Interview card corpus source may not exist in structured form.
- Mitigation: Cards may need manual extraction from existing YAML/config files.

**Cost**: ~45K tokens across 4 phases. Can be done in single session if model cached.

---

## Post-Completion

Once this plan completes:
1. Return to parent plan `apps-qna-deferred-e5-f7a2b1.md`
2. Implement E1.1: Replace stub fetcher with real C0 retrieval
3. Implement E1.2: Wire `evidence_sufficiency = "grounded"` path
4. Then E3 (provider dispatch) becomes unblocked

---

## Non-Goals (Explicitly Out of Scope)

- Do NOT implement E1.1/E1.2 (C0 adapter wiring) — that's a separate plan
- Do NOT implement E3 (provider SDK dispatch) — blocked on E1 anyway
- Do NOT modify existing `healing_contexts` index — leave it untouched
- Do NOT create LLM judges (E2) — that's a separate deferred scope

---

PLAN_CREATED: slug=apps-qna-e1-index-populate-d4366e path=.windsurf/plans/apps-qna-e1-index-populate-d4366e.md waves=4 phases=11 tokens=45K
