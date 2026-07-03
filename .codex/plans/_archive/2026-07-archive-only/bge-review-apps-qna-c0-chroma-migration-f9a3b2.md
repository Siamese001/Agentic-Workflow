---
description: BGE review child plan to migrate apps_qna C0 retrieval from C:/AgenticEmbeddings flat files to canonical Chroma
tags: [bge-review, apps_qna, chromadb, c0, child-plan]
status: Completed
created: 2026-06-08
branch: codex/BGE-review
depends_on:
  - bge-review-apps-qna-cache-init-9a4c2e
supersedes:
  - apps-embedding-deferred-scope-f9a3b2
---

# BGE Review: apps_qna C0 Chroma Migration

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: NONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

## Context

Situation: `apps_qna` is the only live `apps_*` code path that directly defaults to `C:/AgenticEmbeddings`, using the flat `apps_qna_interview_cards` index.

Complication: That index works today and must not be deleted, but it is a transitional artifact outside the canonical Chroma path used by newer app retrieval surfaces.

Question: How should `apps_qna` migrate without breaking grounded C0 retrieval or parent cache initialization?

Answer: Complete the parent L4 cache plan first, then migrate `apps_qna_interview_cards` to canonical Chroma with a reversible read-through phase and focused CI gates.

## Supersedes

| Plan | Status | Reason |
|---|---|---|
| `apps-embedding-deferred-scope-f9a3b2` | Archived | Broad deferred embedding cleanup. This child plan narrows the `apps_qna` C0 migration scope for BGE review execution. |

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W0 | C0.1-C0.2 | Inventory and preservation | 2k | Parent plan complete | DONE | Flat index manifest captured; target confirmed |
| W1 | C1.1-C1.2 | Migration tool and canonical collection | 4k | Parent plan complete | DONE | Chroma collection populated from flat index |
| W2 | C2.1-C2.2 | `apps_qna` read path migration | 4k | W1 complete | DONE | C0 adapter reads Chroma first with fallback |
| W3 | C3.1-C3.2 | Gates and fallback retirement decision | 3k | W2 complete | DONE | CI green; retention decision recorded |

### Phase Progress

| Phase | Title | Status | Notes |
|---|---|---|---|
| C0.1 | Capture flat index inventory | DONE | `docs/reports/apps_qna/bge_review_c0_inventory_20260608.md` |
| C0.2 | Confirm parent cache plan complete | DONE | `bge-review-apps-qna-cache-init-9a4c2e` completed W1-W3 |
| C1.1 | Build migration utility | DONE | `tools/indexing/migrate_apps_qna_flat_index_to_chroma.py` |
| C1.2 | Populate canonical Chroma target | DONE | 110 vectors in `data/cache/chromadb`, collection `apps_qna_interview_cards` |
| C2.1 | Add Chroma-backed fetcher | DONE | `_real_fetch()` queries Chroma before flat fallback |
| C2.2 | Keep flat fallback behind explicit config | DONE | `APPS_QNA_C0_ENABLE_FLAT_FALLBACK` gates external flat fallback |
| C3.1 | Update CI/index checks | DONE | `ops_scripts/ci/check_apps_qna_c0_index.py` validates Chroma primary and flat fallback separately |
| C3.2 | Decide external artifact retention | DONE | `docs/reports/apps_qna/bge_review_c0_retention_decision_20260608.md` |

## Wave Details

### W0: Inventory and Preservation

Scope:
- Record current `apps_qna_interview_cards` manifest and seed pack metadata.
- Confirm source index remains readable.
- Confirm target Chroma path and collection naming.

Completed behavior:
- Captured flat index, manifest, meta, and seed-pack checksums in `docs/reports/apps_qna/bge_review_c0_inventory_20260608.md`.
- Confirmed `C:/AgenticEmbeddings/indexes/apps_qna_interview_cards` remains readable.
- Confirmed 110 vectors, BGE-M3, 1024 dimensions, cosine metric.
- Confirmed parent L4 semantic-cache substrate is complete and separate from the child C0 target.
- Confirmed target for child C0 retrieval migration: `data/cache/chromadb`, collection `apps_qna_interview_cards`.
- Preserved `C:/AgenticEmbeddings`; no migration or mutation performed in W0.

Verification:
- `python ops_scripts/ci/check_apps_qna_c0_index.py --json`

### W1: Migration Tool and Collection

Scope:
- Add a deterministic utility to ingest the existing flat index into Chroma.
- Preserve BGE-M3 model metadata and 1024-dim assumptions.
- Avoid any mutation of `healing_contexts`.

Completed behavior:
- Added `tools/indexing/migrate_apps_qna_flat_index_to_chroma.py`.
- Validates flat-index shape, BGE-M3 model identity, cosine metric, 1024 dimensions, vector count, unique ids, embedding width, and metadata shape before any write.
- Supports `--dry-run`, `--reset`, custom index directory, custom persist directory, custom collection name, and batch size.
- Populates canonical repo-local Chroma path `data/cache/chromadb`, collection `apps_qna_interview_cards`.
- Stamps collection/row metadata with BGE-M3, 1024 dimensions, cosine space, source index SHA256, and this migration plan slug.
- Treats missing target collection during `--reset` as a harmless no-op, including Chroma `NotFoundError`.
- Does not mutate `C:/AgenticEmbeddings`.

Verification:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/tools/indexing/test_migrate_apps_qna_flat_index_to_chroma.py -q`
- `python tools/indexing/migrate_apps_qna_flat_index_to_chroma.py --dry-run`
- `python tools/indexing/migrate_apps_qna_flat_index_to_chroma.py --reset`
- Read-back: `apps_qna_interview_cards` count `110`, metadata `embedding_model=BAAI/bge-m3`, `embedding_dim=1024`, `hnsw:space=cosine`, `source_index_sha256=ec2439cfeaf3155cf7d7d4497317be5634c90c3994229e2ab17603961bda4671`.

### W2: Read Path Migration

Scope:
- Update `apps_qna/c0_adapter.py` to prefer Chroma-backed retrieval.
- Retain flat-file fallback for one wave.
- Preserve `evidence_sufficiency="grounded"` behavior when candidates are returned.

Completed behavior:
- Refactored `_real_fetch()` to resolve the query, embed once, query canonical Chroma first, and return Chroma hits when present.
- Added `_chroma_fetch()` for `apps_qna_interview_cards` under canonical `data/cache/chromadb`.
- Added `_flat_fetch()` as the old flat-index cosine scorer.
- Added `APPS_QNA_C0_ENABLE_FLAT_FALLBACK` gate so the external `C:/AgenticEmbeddings` fallback can be disabled explicitly.
- Preserved grounded/template-only behavior in `call_c0()` and the final evidence contract wrapper.

Verification:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_qna/test_c0_adapter_real_fetch.py -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/apps_qna/test_w0_thin_slice.py tests/apps_qna/test_w2_evidence_paths.py -q`

### W3: Gates and Retention Decision

Scope:
- Update CI checks to validate the canonical collection.
- Keep a separate fallback check while external artifacts remain required.
- Produce a recommendation for `C:/AgenticEmbeddings` retention after migration proof.

Completed behavior:
- Updated `ops_scripts/ci/check_apps_qna_c0_index.py` to report separate `primary_chroma` and `flat_fallback` checks.
- Added unit coverage for the two-source gate in `tests/unit/ops_scripts/ci/test_check_apps_qna_c0_index.py`.
- Recorded retention decision in `docs/reports/apps_qna/bge_review_c0_retention_decision_20260608.md`.
- Recommendation: do not delete `C:/AgenticEmbeddings` in this BGE review branch; keep it as rollback/provenance material while canonical Chroma is primary.
- Verified app C0 tests pass with `APPS_QNA_C0_ENABLE_FLAT_FALLBACK=0`.

Verification:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/ops_scripts/ci/test_check_apps_qna_c0_index.py -q`
- `python ops_scripts/ci/check_apps_qna_c0_index.py --json`
- `APPS_QNA_C0_ENABLE_FLAT_FALLBACK=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_qna/test_c0_adapter_real_fetch.py tests/apps_qna/test_w0_thin_slice.py tests/apps_qna/test_w2_evidence_paths.py -q`

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| Parent cache init plan | Complete | `bge-review-apps-qna-cache-init-9a4c2e` W1-W3 complete |
| Existing flat index | Available | `C:/AgenticEmbeddings/indexes/apps_qna_interview_cards` |
| BGE-M3 model/runtime | Available for tests via mocks | Do not require live model download in unit tests |
| Notion Plans registration | Registered | https://app.notion.com/p/37927693f55c81608e47f527350a59fe |

## Definition Of Done

- [x] Parent plan completed.
- [x] Flat index inventory captured.
- [x] Canonical Chroma collection populated.
- [x] `apps_qna` C0 adapter reads from Chroma first.
- [x] Flat fallback remains reversible during rollout.
- [x] Focused apps_qna and cache tests pass.
- [x] Retention decision for `C:/AgenticEmbeddings` recorded with evidence.

PLAN_CREATED: slug=bge-review-apps-qna-c0-chroma-migration-f9a3b2 path=.codex/plans/bge-review-apps-qna-c0-chroma-migration-f9a3b2.md status=Not Started
