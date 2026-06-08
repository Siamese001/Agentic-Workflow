# apps_rg — fact_vectors Write-Back Discipline (transform-only, staged, gated)

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE — classifier + staging/promotion gate implemented, wired, tested (16+22 green, live no-regression)
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

Plan ID: `apps-rg-fact-vector-writeback-discipline-67652c`
Status: Not Started
Created: 2026-06-08
Scope boundary: **apps_rg only.** No `agentic_core` edits, no other `apps_*`.

## Mental model (customized for apps_rg)

> **Write back to `fact_vectors` only when inference TRANSFORMS already-grounded content — never when
> it GENERATES new content.** A chunk earns a spot in `fact_vectors` only if it traces back to a
> source document. Inference can reshape that grounding, not invent it.

Three safe write-back operations (the only ones allowed into `fact_vectors`):
- **EXTRACT** — atomize a retrieved/grounded paragraph into discrete claims (better retrieval granularity).
- **FUSE** — reconcile multiple grounded chunks into one canonical fact (evidence-fusion output).
- **ENRICH** — add metadata to an existing grounded fact (confidence, role-relevance, recency).

Boundary: **generated/synthesized** output (LLM rewrites, JD-tailored phrasings, cover-letter prose) →
**semantic cache** as intent vectors (`apps_rg_r1b_semantic_cache`, already tagged `not_c0_fact_vectors`).
If you can't point to the source document a fact came from, it does NOT belong in `fact_vectors`.

Gate: write-backs land in a **staging** collection (off the hot path), pass a **validation check**
(deterministic) or **HITL** before promotion to the live fact store. Keeps Chroma clean and auditable.

## Context (SCQA)

- **Situation:** `apps_rg/runtime/c0/c02_fact_vector_ingest.py` already writes C0.2 atoms into the live
  `fact_vectors` Chroma collection (`maybe_upsert_c02_fact_vectors`). The model already carries the
  primitives the discipline needs: `source_type` (provenance), `proof_status`
  (proof_eligible/targeting_only/not_proof), and `FORBIDDEN_PROOF_SOURCE_TYPES` (jd_payload, briefing,
  company_research, generic_best_practice, … = not grounded). The semantic cache
  (`apps_rg_r1b_semantic_cache`, `r1b_intent_vector.py`) already exists for intent vectors.
- **Complication:** The current eligibility gate (`c02_atom_ingest_eligible`) checks proof/confidence
  but (a) has **no operation taxonomy** (extract/fuse/enrich vs generated), (b) does **not explicitly
  reject generated content** or enforce **source-document provenance**, and (c) writes **directly to
  live** `fact_vectors` — no staging, no promotion gate, no audit of what transform produced a chunk.
- **Question:** How do we enforce the transform-only + source-traced + staged-and-gated discipline
  without breaking the working C0.2 retrieval path (live runs depend on `fact_vectors` being populated)?
- **Answer:** Add an apps_rg-scoped write-back discipline layer: a classifier (EXTRACT/FUSE/ENRICH/
  GENERATED) + source-grounding gate that routes each atom (stage-for-fact-vectors / semantic-cache /
  reject); a `fact_vectors_staging` collection; a deterministic validation **promotion gate** (auto-
  promote on pass, HITL-hold when `APPS_RG_FACT_VECTOR_PROMOTION_HITL=1`). Non-breaking: validated
  grounded transforms still reach live `fact_vectors`, now via staged + classified + audited hops.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | Write-back classifier + source-grounding gate + routing (pure, hermetic) | ~25k | atom carries source_type/proof_status/source_span_ref | DONE | EXTRACT/FUSE/ENRICH/GENERATED classified; 3 routes (stage/semantic_cache/reject) reachable; pure-testable |
| W2 | P2 | Staging collection + deterministic promotion gate (auto + HITL-hold) | ~25k | Chroma reachable via CHROMA_PERSIST_DIR | DONE | `fact_vectors_staging` round-trip: hostile re-validation promotes to live; APPS_RG_FACT_VECTOR_PROMOTION_HITL holds |
| W3 | P3 | Wire discipline into `c02_fact_vector_ingest` (non-breaking) + receipts + tests | ~25k | evidence_room call site unchanged | DONE | Routed via decide_write_back → staging → promote; receipt has operations/routing/promotion; 16 new + 22 evidence-room green; live run REAL_LLM+X3_ALLOW |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Classifier + grounding + routing | NEW `apps_rg/runtime/c0/fact_vector_write_back.py` | mapping source_type→operation; reject path must be conservative (default-reject when ambiguous) | ~25k | In Progress |
| P2 | Staging + promotion gate | same module (promotion fns) + `fact_vectors_staging` | re-validate at promotion (hostile verifier); HITL-hold without losing staged rows | ~25k | Not Started |
| P3 | Wire + receipts + tests | EDIT `c02_fact_vector_ingest.py`; NEW `tests/unit/apps_rg/test_fact_vector_write_back.py` | keep live store populated; receipt back-compat | ~25k | Not Started |

## Design

**New `apps_rg/runtime/c0/fact_vector_write_back.py`:**
- `WriteBackOperation`: `EXTRACT` / `FUSE` / `ENRICH` (allowed) + `GENERATED` (forbidden).
- `WriteBackRoute`: `STAGE_FOR_FACT_VECTORS` / `SEMANTIC_CACHE` / `REJECT`.
- `classify_write_back_operation(atom) -> (operation, reason)` — forbidden source_type or proof_status
  `not_proof` ⇒ GENERATED; explicit `atom["write_back_operation"] in {fuse,enrich}` honored; grounded
  source + non-empty span ⇒ EXTRACT; no provenance ⇒ GENERATED (default-reject).
- `source_grounding_ok(atom) -> (ok, reason)` — must trace to a source document (grounded source_type
  not in FORBIDDEN_PROOF_SOURCE_TYPES, AND non-empty `source_span_ref`/`source_ref`).
- `decide_write_back(atom) -> WriteBackDecision(route, operation, reason)` — the single routing call.
- `STAGING_COLLECTION_NAME = "fact_vectors_staging"`.
- `promote_staged_fact_vectors(*, chroma_path, require_hitl, ...)` — hostile re-validation of staged
  rows → auto-promote to live `fact_vectors` (clear staging), or hold when `require_hitl`.

**Edit `c02_fact_vector_ingest.py`:** route atoms through `decide_write_back`; only
`STAGE_FOR_FACT_VECTORS` atoms build chunks; chunks upsert to `fact_vectors_staging`; then
`promote_staged_fact_vectors` commits to live (auto unless HITL env set). Receipt gains `operations`
(counts per op), `routed_to_semantic_cache`, `rejected`, `staged_count`, `promoted_count`, `held_count`.

## Phase 0 — fact_vectors seed (PREREQUISITE; exists, verified 2026-06-08)

The write-back discipline governs **runtime augmentation**; it presumes `fact_vectors` is already
populated. Per `c02_chroma_lifecycle.py`, product runs **consume a pre-built governed index** and must
not depend on same-run upsert. So `fact_vectors` MUST be seeded offline first (cold-start / fresh
worktree has none — same gitignored-runtime-data class as `.env`/ChromaDB/sparse).

**Phase 0 seed EXISTS:** `tools/apps_rg/build_section_fact_vectors.py` walks the canonical candidate
fact ledger and upserts one BGE-M3 chunk per HIGH/proof-eligible fact into live `fact_vectors`. It
reuses `atoms_to_fact_vector_chunks` → `upsert_fact_vector_chunks` (so the write-back discipline applies
— ledger atoms classify as EXTRACT and pass; verified no regression: 42 facts → 13 grounded chunks).

**Cold-start bootstrap sequence (verified end-to-end 2026-06-08):**
```
CHROMA_PERSIST_DIR=<store> python tools/apps_rg/build_section_fact_vectors.py --execute   # seed fact_vectors
CHROMA_PERSIST_DIR=<store> python tools/generate/ingestion/build_sparse_index.py --collection fact_vectors  # sparse sidecar
CHROMA_PERSIST_DIR=<store> python -m apps_rg --section <lane> ...                          # run
```
Seeding a fresh worktree store from the ledger (13 chunks) + building its sparse sidecar **cleared**
the `Collection [fact_vectors] does not exist` and sparse-`UNAVAILABLE` errors.

**Open finding (seed coverage):** a pure 13-fact seed yields `FEC support_status='WEAK'` for
`insurtech_bullets` — the candidate skills ledger has no InsurTech/EY *employment* facts (those live in
the base resume, surfaced authoritatively by the W3 base-resume role-episode planner; `fact_vectors` is
non-authoritative dense *enrichment*). The richer main store passed. Closing this requires either
extending the Phase 0 seed to also ingest base-resume employment bullets, or treating seed-coverage as
an operational pre-req. Captured under `## Deferred Follow-ups`.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | Generated/synthesized atoms (forbidden source_type or `not_proof`) never reach `fact_vectors` | classifier unit test: GENERATED → REJECT/SEMANTIC_CACHE |
| 2 | Only EXTRACT/FUSE/ENRICH transforms of grounded content are staged | routing unit test over grounded vs forbidden sources |
| 3 | Every staged/promoted chunk traces to a source document (source_type + span) | `source_grounding_ok` test; chunk `source_document_id` non-empty |
| 4 | Write-backs land in `fact_vectors_staging`, not directly in live | promotion test against a tmp Chroma store |
| 5 | Deterministic validation promotes staging→live; `APPS_RG_FACT_VECTOR_PROMOTION_HITL=1` holds | promotion gate test (auto vs hold) |
| 6 | Live `fact_vectors` still populated for grounded transforms (non-breaking) | end-to-end ingest test: eligible atom reaches live via staging |
| 7 | Receipt records operations breakdown + routing + promotion counts | receipt-shape test |
| 8 | Smoke: `import apps_rg.runtime.c0.fact_vector_write_back` + `c02_fact_vector_ingest` clean | import test |

Verification vs Deferral: items 1–3, 7–8 are pure/hermetic. Items 4–6 use a tmp ChromaDB (no live
provider). True async/background promotion queue is a `## Deferred Follow-ups` item — staging IS the
off-hot-path buffer; promotion is callable as a separate batch step.

## Out Of Scope

- Editing `agentic_core` (UWG, chroma_paths, bm25_store) or other `apps_*`.
- Re-architecting the semantic cache (`r1b_*`) — generated routing reuses the existing intent-vector path.
- A background async promotion daemon (deferred; staging + separately-callable promotion suffice now).

## Deferred Follow-ups

- Async/background promotion worker (drain `fact_vectors_staging` on a schedule) if the inline
  best-effort promotion becomes a hot-path cost.
- Wiring promotion through the formal UWG commit path (spine law alignment) if `fact_vectors` is
  reclassified as UWG-governed durable state rather than a rebuildable C0 cache.
- **Phase 0 seed coverage for InsurTech/EY:** `build_section_fact_vectors.py` seeds only the candidate
  skills ledger, so a pure cold-start seed gives `FEC support_status='WEAK'` for `insurtech_bullets`/
  `ey_bullets` (no employment facts in that ledger). Options: (a) extend the seed to also ingest the
  base-resume employment bullets (`base['facts']['employment']`, reusing the W3 base-resume extraction)
  as grounded EXTRACT chunks; (b) document seed-coverage as an operational pre-req and rely on
  accumulated runtime augmentation; (c) relax the FEC mandatory-grounding threshold for sections whose
  authoritative proof comes from the base-resume planner. Different blast radius — pending decision.
