# apps_qna C0 Retention Decision - BGE Review

Date: 2026-06-08

Plan: `.claude/plans/bge-review-apps-qna-c0-chroma-migration-f9a3b2.md`

## Decision

Keep `C:/AgenticEmbeddings` for now, but no longer treat it as the primary `apps_qna` runtime retrieval store.

`apps_qna` C0 retrieval now uses canonical Chroma first:

- Persist path: `data/cache/chromadb`
- Collection: `apps_qna_interview_cards`
- Embedding model: `BAAI/bge-m3`
- Dimensions: `1024`
- Distance: `cosine`
- Vector count: `110`

The external flat index remains as a gated fallback and provenance artifact only:

- Fallback path: `C:/AgenticEmbeddings/indexes/apps_qna_interview_cards`
- Runtime gate: `APPS_QNA_C0_ENABLE_FLAT_FALLBACK`
- Current default: enabled for this rollout wave

## Evidence

The migration utility populated the canonical Chroma collection from the existing flat index without mutating `C:/AgenticEmbeddings`.

Source hash:

- `index.json`: `ec2439cfeaf3155cf7d7d4497317be5634c90c3994229e2ab17603961bda4671`

Verification run:

- `python tools/indexing/migrate_apps_qna_flat_index_to_chroma.py --dry-run`
- `python tools/indexing/migrate_apps_qna_flat_index_to_chroma.py --reset`
- `python ops_scripts/ci/check_apps_qna_c0_index.py --json`

The CI gate now separately validates:

- Primary Chroma collection exists, has compatible metadata, has 110 vectors, and returns a sample row.
- Flat fallback index exists, has required files, has BGE-M3 metadata, has 1024 dimensions, has 110 vectors, and has a valid sample vector.

## Recommendation

Do not delete `C:/AgenticEmbeddings` during this BGE review branch.

Next safe retirement step:

1. Run app-level C0 tests with `APPS_QNA_C0_ENABLE_FLAT_FALLBACK=0`.
2. Keep the canonical Chroma gate green without reading the flat fallback in runtime.
3. Confirm seed-pack regeneration or backup instructions are sufficient to recreate the flat artifact if needed.
4. Only after that, archive or remove the external flat index in a separate cleanup plan.

Until those conditions pass, `C:/AgenticEmbeddings` is still needed as rollback/provenance material, but `apps_qna` should not be considered blocked on it for primary retrieval.
