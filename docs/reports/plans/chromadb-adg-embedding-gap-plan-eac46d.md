# ChromaDB Embedding Gap Closure Plan

This plan uses the current ChromaDB state and hot ADG Redis context to identify topical and structural embedding gaps, then execute a staged remediation with measurable retrieval-quality outcomes.

## Scope and Intent
- Use ADG Redis for repository understanding and prioritization only (no ADG-to-Chroma ingestion in this wave).
- Close both topical coverage gaps (missing/imbalanced knowledge sources) and structural coverage gaps (missing repo architecture representation in retrievable embeddings).
- Keep implementation focused on existing collections and ingestion pipelines already in the repo.

## Current Baseline (Read-Only Findings)
### Chroma inventory snapshot
- `repo_adg_graph`: 594,637
- `traces`: 100,150
- `repo_code_chunks`: 56,454
- `code`: 15,071
- `repo_symbols`: 9,146
- `repo_tests_guardrails`: 6,230
- `agentic_best_practices`: 2,563
- `agentic_best_practices_semantic`: 2,317
- `repo_arch_docs`: 2,533
- `docs`: 724, `apps`: 295
- `repo_git_history`: collection read error (`Failed to apply logs to the metadata segment`)

### `agentic_best_practices` metadata quality
- Full-key coverage: `source_url`, `domain`, `document_title`, `content_hash`, `chunk_id`, `chunk_index`, `fetched_at`
- Partial-key coverage only: `source_type`/`line_number` (2,272 of 2,563), semantic fields (`chunk_type`, `section_title`, `semantic_chunk_id`, `token_estimate`) only 246 records
- Source type distribution is imbalanced: `governance` 2,183, `missing` 291, `framework` 53, `vendor_docs` 36

### `agentic_best_practices_semantic` metadata quality
- Strong enrichment coverage: `agentic_patterns`, `key_concepts`, `enrichment_hash`, `semantic_version` all present
- Inherits partial `source_type`/`line_number` coverage from source collection (still 2,272)

### ADG Redis context (hot cache)
- ADG status: HOT and fresh
- Nodes: 10,432; Edges: 681,161
- Layer distribution includes significant `L_TEST` and `L_TOOLS`; core layers L0–L6 are present and usable for prioritization
- Unresolved imports: 4,339 (signal for documentation/knowledge blind spots)
- Violation entries present at scale (5,301), useful as risk-prioritized retrieval targets

## Confirmed Gap Categories
1. Metadata consistency gaps
- Mixed schema across web chunks (legacy vs semantic chunk fields).
- Missing `source_type` for 291 base chunks.

2. Topical coverage gaps
- Heavy concentration in governance-tagged content; low representation of framework/vendor/runtime-oriented material.
- Failed/dynamic sources (JS-rendered pages, stale links) reduce usable ingestion quality.

3. Structural coverage gaps (repo understanding)
- No explicit ADG-aligned coverage matrix linking retrieval corpus to L0–L6 and key subsystems.
- High-value ADG hotspots are not explicitly used to steer ingestion prioritization.

4. Pipeline coherence gaps
- Multiple ingestion paths and embedding models exist across collections (BGE-M3, OpenAI embeddings, MiniLM), increasing cross-collection retrieval inconsistency risk.

## Implementation Plan (Phased)
### Phase 1 — Baseline Hardening and Observability
- Produce a deterministic collection audit artifact (counts, metadata completeness, source distribution, failure ledger).
- Add/refresh health checks for problematic collections (including `repo_git_history` read failure).
- Define canonical metadata contract for `agentic_best_practices*` collections.

Acceptance criteria:
- A reproducible baseline report exists in `docs/reports/` with collection counts and metadata completeness percentages.
- Known bad collections are flagged with actionable status.

### Phase 2 — Metadata Backfill and Schema Normalization
- Backfill `source_type` and `line_number` where absent for `agentic_best_practices`.
- Normalize semantic metadata fields on legacy chunks where derivable (`chunk_type`, section fields, token estimate).
- Enforce null-safe metadata serialization and key presence checks during ingestion.

Acceptance criteria:
- `source_type` coverage reaches 100% in `agentic_best_practices`.
- Semantic metadata coverage is materially improved and measured.

### Phase 3 — Topical Gap Closure (Corpus Expansion/Rebalancing)
- Build a prioritized seed refresh list from current failures + ADG hotspot needs.
- Replace stale/404/dynamic-only URLs with stable canonical alternatives.
- Re-run targeted ingestion batches for underrepresented categories (`framework`, `vendor_docs`, runtime architecture, eval/ops).

Acceptance criteria:
- Category balance improves against baseline (explicit before/after deltas).
- Net new high-quality chunks are added with low duplicate ratio.

### Phase 4 — ADG-Guided Structural Coverage Matrix
- Derive a retrieval coverage matrix keyed by ADG layers/subsystems/hotspots.
- Map existing corpus documents/chunks to ADG-informed structural tags (layer/subsystem/risk-theme).
- Identify remaining blind spots and queue targeted ingestion/doc curation.

Acceptance criteria:
- Coverage matrix exists with per-layer completeness and hotspot representation.
- A ranked backlog of unresolved structural gaps is produced.

### Phase 5 — Retrieval Quality Validation
- Execute representative query suite spanning topical + structural use-cases.
- Compare baseline vs post-gap-closure results (relevance proxy, source diversity, metadata filterability).
- Document residual risks and next wave recommendations.

Acceptance criteria:
- Query benchmarks show measurable improvement in diversity and relevance.
- Final report includes go/no-go and next-step backlog.

## Deliverables
- Baseline and post-change audit reports in `docs/reports/`
- Metadata contract and enforcement checklist for `agentic_best_practices*`
- ADG-driven embedding coverage matrix and prioritized gap backlog
- Validation summary with before/after retrieval evidence

## Out of Scope (This Wave)
- No ADG entity/edge bulk ingestion into Chroma.
- No refactor of all historical collections outside prioritized gap closure targets.
- No large architectural migration of existing vector DB stack.

## Execution Notes
- Start narrow: fix metadata/quality on `agentic_best_practices*` first, then expand.
- Keep all actions evidence-backed with deterministic counts and reproducible scripts.
- Preserve compatibility with existing retrieval consumers while improving coverage quality.
