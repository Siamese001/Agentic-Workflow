---
plan_id: bge-m3-gap-closure-c8f3a2
plan_type: governance
parent_plans:
  - apps-qna-remaining-e1e2e3e5-54b6c7   (E1 C0 wiring — Wave 1 of this plan)
  - chromadb-bge-retrieval-hardening-e9aa09  (ADR-055 enforcement — Wave 3 of this plan)
dependencies:
  - apps-qna-e1-index-populate-d4366e (COMPLETE — index exists)
---

# BGE-M3 Gap Closure — Analysis Verification & Remediation

Close the five verified gaps surfaced during BGE-M3 cross-app analysis (2026-05-05):
Gap 2 (C0 stub still live), Gap 5 (reranker/embedder surface clarification), Gap 7 (healing_contexts
disambiguation), Gap 9 (GlobalcacheStrategy false positive), Gap 12 (ADR-055/056 Proposed, not enforced).

---

## Context (SCQA)

- **Situation** — The BGE-M3 analysis confirmed that `apps_qna` is the only app with an
  app-owned vector index today. The E1 plan (`apps-qna-e1-index-populate-d4366e`) populated
  that index (110 vectors, 1024-d, BAAI/bge-m3) and committed on 2026-05-05. ADR-055 and
  ADR-056 exist as `Proposed` ADRs governing embedding enforcement and multi-head usage.
- **Complication** — (a) `apps_qna/c0_adapter.py` still uses `_stub_fetch` — the index exists
  but retrieval is not live. (b) ADR-055 enforcement is soft (warn, not fail-closed), meaning
  the `apps_qna_interview_cards` collection has no hard protection against future dim-mismatch
  writes. (c) Three BGE-M3 surfaces (embedder, reranker, multi-head) are conflated in analysis
  and documentation, causing confusion about scope of future work.
- **Question** — How do we close the gap between "index populated" and "C0 retrieval live", while
  locking the collection against dim-corruption and clarifying BGE-M3 surface ownership?
- **Answer** — Four waves: (1) wire C0 adapter to real index, (2) document the three BGE-M3
  surfaces in an ADR amendment, (3) promote ADR-055 enforcement from soft-warn to hard-fail
  for the `apps_qna_interview_cards` collection specifically, (4) verify and close the
  `healing_contexts` / dual-reranker false-positive findings with NEXT_STEP markers.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_qna/c0_adapter.py` | Gap 2 — `_stub_fetch` confirmed present, lines 96–100 | ✅ VERIFIED |
| `apps_qna/engines/router/reranker.py` + `apps_qna/router/reranker.py` | Gap 5 — two reranker paths confirmed; cross-encoder vs shim | ✅ VERIFIED |
| `system_learning/config/embedding_storage_layout.py` (14 matches) | Gap 7 — `healing_contexts` is system_learning, not apps_qna | ✅ VERIFIED |
| `apps_shared/enforcement/GlobalcacheStrategy.py` | Gap 9 — BAAI match is OTel emit, not embedder config | ✅ VERIFIED |
| `docs/architecture/adr/ADR-055-embedding-model-enforcement.md` | Gap 12 — Status: Proposed; enforcement not implemented | ✅ VERIFIED |
| `docs/architecture/adr/ADR-056-bge-m3-multi-head.md` | Gap 12 — Status: Proposed; multi-head not yet default | ✅ VERIFIED |
| `.windsurf/plans/apps-qna-remaining-e1e2e3e5-54b6c7.md` | E1.1/E1.2 already scoped as Wave 1 of sibling plan | ✅ VERIFIED |
| `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md` | ADR-055 implementation already scoped in W1-W2 of that plan | ✅ VERIFIED |

---

## Gap Register (verified)

| ID | Gap | Severity | Wave | Pre-existing plan? |
|---|---|:---:|:---:|---|
| **G1** | `apps_qna/c0_adapter.py` `_stub_fetch` still live — index exists but retrieval returns EMPTY/WEAK | **P0** | W1 | `apps-qna-remaining-e1e2e3e5-54b6c7` E1.1/E1.2 |
| **G2** | ADR-055 enforcement soft (warn, not fail-closed) — `apps_qna_interview_cards` collection unprotected against dim-mismatch writes | **P1** | W3 | `chromadb-bge-retrieval-hardening-e9aa09` W1.3 |
| **G3** | Two reranker files (`apps_qna/router/reranker.py` vs `apps_qna/engines/router/reranker.py`) — one may be dead code / shim; not documented | P2 | W2 | None |
| **G4** | BGE-M3 surfaces undocumented — embedder (dense 1024-d), cross-encoder reranker (BGE-reranker-v2), multi-head (ADR-056 Proposed) conflated in analysis | P2 | W2 | None |
| **G5** | `healing_contexts` collection disambiguation — not documented anywhere that it is a `system_learning` surface, not `apps_qna` | P3 | W2 | None |
| **G6** | `apps_shared/enforcement/GlobalcacheStrategy.py` BAAI grep hit — documented as false positive but not annotated in code | P3 | W2 | None |
| **G7** | ADR-056 multi-head (sparse + ColBERT) status Proposed; `BGE_MULTI_HEAD=1` not default; no plan to flip | P3 | W4 | `chromadb-bge-retrieval-hardening-e9aa09` W5.3 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|:---:|---|
| **W1** | W1.1, W1.2 | Wire C0 adapter to real `apps_qna_interview_cards` index | ~25K | Index at `C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\` exists (✅) | 🔲 TODO | `evidence_sufficiency` = `grounded` in runtime; C0 adapter returns real candidates; existing tests green |
| **W2** | W2.1, W2.2, W2.3 | Documentation and disambiguation — three BGE-M3 surfaces, dual-reranker dead-code verdict, `healing_contexts` annotation | ~8K | No code changes required | 🔲 TODO | ADR-055/056 cross-ref added; reranker shim classified; `healing_contexts` comment added to system_learning layout |
| **W3** | W3.1 | Promote ADR-055 enforcement to hard-fail scoped to `apps_qna_interview_cards` collection | ~15K | W1 complete (collection actively used) | 🔲 TODO | `EmbeddingProvenanceMismatchError` raised on dim mismatch write attempt; unit test passes; CI gate registered |
| **W4** | W4.1 | Track ADR-056 multi-head flip — NEXT_STEP marker only; no implementation | ~2K | Depends on `chromadb-bge-retrieval-hardening-e9aa09` W5.3 | 🔲 TODO | `NEXT_STEP:` marker emitted referencing `e9aa09` W5.3; no code written |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|:---:|
| W1.1 | Replace `_stub_fetch` in `c0_adapter.py` | `apps_qna/c0_adapter.py` | Must query `index.json` via `tools.embedders.get_embedder()`; embed query with BGE-M3; return top-k as `CandidateEvidencePool` | ~12K | 🔲 TODO |
| W1.2 | Wire grounded evidence path | `apps_qna/c0_adapter.py`, `apps_qna/cert/fec_producer.py` | `grounded=True` requires `c0_retrieval_sources` in `run_context`; FEC producer forward-compat already handles this | ~13K | 🔲 TODO |
| W2.1 | Classify dual reranker files | `apps_qna/router/reranker.py`, `apps_qna/engines/router/reranker.py` | Read both; determine if `engines/router/reranker.py` is dead code, shim, or separate surface; add `# NOTE:` comment or deprecation notice | ~3K | 🔲 TODO |
| W2.2 | Document BGE-M3 three surfaces | `docs/architecture/adr/ADR-055-embedding-model-enforcement.md` (cross-ref ADR-056 + ADR-046) | Add §"Surface Map" table: Dense embedder / Cross-encoder reranker / Multi-head (proposed). No code. | ~3K | 🔲 TODO |
| W2.3 | Annotate `healing_contexts` and `GlobalcacheStrategy` | `system_learning/config/embedding_storage_layout.py`, `apps_shared/enforcement/GlobalcacheStrategy.py` | One-line comments clarifying surface ownership; not functional changes | ~2K | 🔲 TODO |
| W3.1 | Hard-fail enforcement for `apps_qna_interview_cards` | `agentic_core/L4_state/utils/client/chroma_client.py`, new `agentic_core/embeddings/exceptions.py`, `tests/unit/agentic_core/L4_state/utils/client/test_chroma_client_behavior.py` | Scoped enforcement (collection-name allowlist initially); ADR-055 pre-write check; CI gate entry | ~15K | 🔲 TODO |
| W4.1 | NEXT_STEP marker for ADR-056 multi-head flip | Response only — no file write | Emit `NEXT_STEP:` marker referencing `chromadb-bge-retrieval-hardening-e9aa09` W5.3 as the action item | ~2K | 🔲 TODO |

---

## Relationship to Pre-existing Plans

| This plan's wave | Overlapping plan | Relationship |
|---|---|---|
| W1.1/W1.2 | `apps-qna-remaining-e1e2e3e5-54b6c7` E1.1/E1.2 | **SAME WORK** — W1 of this plan IS E1.1/E1.2 of the sibling plan. Execute once; mark done in both. |
| W3.1 | `chromadb-bge-retrieval-hardening-e9aa09` W1.3 | **SUBSET** — this plan scopes enforcement to `apps_qna_interview_cards` only; sibling plan extends to all collections in its W2. Execute W3.1 here first; sibling plan W1.3 generalises the pattern. |
| W4.1 | `chromadb-bge-retrieval-hardening-e9aa09` W5.3 | **UPSTREAM DEPENDENCY** — multi-head is deferred to sibling plan W5.3. W4.1 emits only the NEXT_STEP marker. |

---

## Non-Goals

- Do NOT implement LLM judges (E2) — holdout corpus required first
- Do NOT implement provider dispatch (E3) — E1 must be live first
- Do NOT flip `BGE_MULTI_HEAD=1` to default — gated on `chromadb-bge-retrieval-hardening-e9aa09` W5.3
- Do NOT modify `healing_contexts` collection data — it is a `system_learning` surface
- Do NOT promote ADR-055/056 from `Proposed` to `Accepted` — that requires a separate ADR amendment decision; W3.1 implements the enforcement code under the existing Proposed status
- Do NOT close `chromadb-bge-retrieval-hardening-e9aa09` — it has broader scope (all collections, BM25, multi-head, orchestrator consolidation); this plan is a narrower focus scoped to verified BGE-M3 analysis gaps

---

## Success Criteria

- [ ] **W1**: `apps_qna/c0_adapter.py` `_stub_fetch` replaced; `call_c0` returns `evidence_sufficiency="grounded"` when index has results; FEC producer sets `grounded=True` via forward-compat path
- [ ] **W2**: Dual reranker files classified (dead/live verdict documented); BGE-M3 surface map added to ADR-055; `healing_contexts` annotation added to `embedding_storage_layout.py`
- [ ] **W3**: `EmbeddingProvenanceMismatchError` raised on dim-mismatch write to `apps_qna_interview_cards`; unit test in `test_chroma_client_behavior.py` passes; CI gate entry registered
- [ ] **W4**: `NEXT_STEP:` marker emitted for multi-head flip; no regression

---

## Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| BGE-M3 model not loaded at test time (no GPU in CI) | P1 | W1 tests mock `get_embedder()` — no live model load required |
| `CandidateEvidencePool` type mismatch from real index schema | P1 | Read `index.json` schema before W1.1 implementation; add integration test with real index |
| `apps_qna_interview_cards` collection written by another process before W3.1 lands | P2 | Time-bounded risk; W1 → W3 executed in same session if possible |
| W1 changes break existing `test_apps_qna_c0_retrieval.py` stubs | P2 | Update test expectations in same W1 commit; no regressions allowed |

---

## References

- `apps_qna/c0_adapter.py` — stub fetcher, lines 96–100
- `apps_qna/router/reranker.py` — canonical cross-encoder path
- `apps_qna/engines/router/reranker.py` — secondary path (W2.1 to classify)
- `system_learning/config/embedding_storage_layout.py` — `healing_contexts` owner
- `tools/retrieval/vector_config.py` — platform default `BAAI/bge-m3`
- `tools/indexing/populate_apps_qna_index.py` — E1 populator (COMPLETE)
- `ops_scripts/ci/check_apps_qna_c0_index.py` — E1 CI gate (COMPLETE)
- `docs/architecture/adr/ADR-055-embedding-model-enforcement.md` (Status: Proposed)
- `docs/architecture/adr/ADR-056-bge-m3-multi-head.md` (Status: Proposed)
- `docs/architecture/adr/ADR-046-rerank-revival.md` (cross-encoder reranker)
- `.windsurf/plans/apps-qna-remaining-e1e2e3e5-54b6c7.md` (E1 wiring sibling)
- `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md` (ADR-055 impl sibling)

PLAN_CREATED: slug=bge-m3-gap-closure-c8f3a2 path=.windsurf/plans/bge-m3-gap-closure-c8f3a2.md waves=4 phases=7 tokens=~50K
