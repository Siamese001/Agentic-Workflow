---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-runtime-substitute-burndown-c4e8f1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-runtime-substitute-burndown-c4e8f1.md'
source_sha256: 10e31025e5cc2af336de40444d89c09437338bf799b8c7567debcd0a7490ab42
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-runtime-substitute-burndown-c4e8f1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg Runtime Substitute Burndown (Mocks, Fallbacks, Tool Swaps)

Eliminate silent substitutes on product paths: Chroma default MiniLM vs BGE-M3, pseudo-digest vectors, ledger-only C0 masquerading as retrieval, skipped spine dense query, section-lane C0.2 upsert side effects, Qwen/judge mocks, and modular `phase0_synthetic` lane fillers.

> **plan_id discipline**: `apps-rg-runtime-substitute-burndown-c4e8f1` · marker `plan=apps-rg-runtime-substitute-burndown-c4e8f1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W8
LAST_COMPLETED_WAVE: W8
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
PLAN_COMPLETE: plan=apps-rg-runtime-substitute-burndown-c4e8f1 note="W0-W8 contract closeout; optional X3 polish deferred to backlog"
NOTION_PAGE_ID: 36827693-f55c-8131-b393-f43334c46a10
NOTION_RECONCILED: 2026-05-24
ACTIVE_BACKLOG_MANIFEST: docs/reports/plans/active_in_progress_plans_manifest_20260524.md
ACTIVE_BACKLOG_ROLE: completed_2026_05_25
PARENT_PLAN: apps-rg-spine-only-unification-d8f4a2
CLOSEOUT_CLASS: PARTIAL_W0_W8_DONE_POLISH_OPEN
REVIEW_DECISIONS_LOCKED: W4,W1,W2
CLOSEOUT_RECEIPT: artifacts/apps_rg/plans/runtime_substitute_burndown_w0_w8_receipt.md
LIVE_PROOF_RECEIPT: artifacts/apps_rg/plans/runtime_substitute_burndown_live_proof_attempt_20260522.md
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF,IMPLEMENTATION_RECEIPT
PROOF_CLASSIFICATION_NOT_CLAIMED: LIVE_RUNTIME_PROOF,RELEASE_ELIGIBLE_PROOF

---

## Closeout (2026-05-22) — PARTIAL

**STATUS: PARTIAL** — W0–W8 implementation + contract done; child plan W1 **LIVE_RUNTIME_PROOF PASS** after BM25 seed.

| Proof class | This closeout |
|-------------|---------------|
| CONTRACT_TEST_PROOF | Yes (21 pytest) |
| IMPLEMENTATION_RECEIPT | Yes |
| LIVE_RUNTIME_PROOF | **PASS** (child) — [apps_rg_hybrid_live_proof_w1_receipt.md](docs/reports/apps_rg/apps_rg_hybrid_live_proof_w1_receipt.md); prior [live attempt](artifacts/apps_rg/plans/runtime_substitute_burndown_live_proof_attempt_20260522.md) was BLOCKED pre-sparse |
| RELEASE_ELIGIBLE_PROOF | **Not claimed** |

**Non-claims:** no release eligibility; no full résumé live run; child W2 still has auxiliary X2 FAIL (`x2_generic_filler_zero`).

**Done:** W6.1 import purge; **W4.3** product hybrid; child [apps-rg-hybrid-live-jd-selection-f8e2b3](apps-rg-hybrid-live-jd-selection-f8e2b3.md) W0b–W4 + [closeout](docs/reports/apps_rg/apps_rg_hybrid_live_jd_selection_closeout_receipt.md).  
**Open:** full X3/product_quality PASS (optional `x2_claim_ledger_materialized` stability). **Closed:** child W2d deferred scope — [apps_rg_hybrid_live_deferred_scope_receipt.md](docs/reports/apps_rg/apps_rg_hybrid_live_deferred_scope_receipt.md).

---

## Locked review decisions (2026-05-22)

| Wave | Status | One-line lock |
|------|--------|----------------|
| **W4** | Approved | Hybrid C0.2 retrieve (dense+sparse+metadata); ledger primary; C0.3 authority; FAIL if lane skipped; `c0_authority_mode=ledger_graph_primary` |
| **W1** | Approved | **Strict all CLI by default** (section, full run, any `python -m apps_rg`); opt-out `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` only |
| **W2** | Approved | Ingest ≠ retrieve; **no product per-run upsert**; batch canonical; PASS needs query not write |

### Architecture spine (approved)

```text
W1 = live runtime / proof strictness   (Qwen, BGE, no pseudo, all CLI default strict)
W2 = write / index lifecycle           (batch ingest, optional pre-run index maintenance)
W4 = read / retrieval lifecycle        (hybrid C0.2 on existing index; ledger primary)
```

**Mental-model fix:** Product section runs **consume** governed evidence; they do not **mutate** the retrieval substrate in the same run.

### Cursor enforcement rule (implement verbatim)

```text
Implement W2/W4 separation exactly:

- Batch ingest is the canonical fact_vectors writer.
- Product section runs do not require and must not depend on same-run Chroma upsert.
- Lane upsert is disabled by default.
- APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1 permits explicit index refresh only,
  classified separately from product retrieval proof (pre-run maintenance action only).
- C0.2 retrieval queries existing dense/sparse/metadata indexes when required by profile.
- Product PASS may depend on c02_chroma_query, never on c02_chroma_write from the same section run.
- Receipts must separately report c02_chroma_write and c02_chroma_query.
- If required query/read index is missing, stale, blocked, or skipped, fail closed.
- Ledger/graph remains primary authority with c0_authority_mode=ledger_graph_primary.
- Retrieval hits are additive and cannot replace ledger/graph facts.
```

### Forbidden pattern (non-release — do not implement in v1)

```text
product section run
  -> upserts selected facts
  -> queries same index
  -> claims product PASS
```

Even with `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` inside a section lane, same-run write + read is **non-release proof**. Deferred: governed refresh-before-read with frozen snapshot semantics.

### Allowed pattern

```text
pre-run: batch ingest OR dedicated index_refresh command
  -> emits index_build_receipt.json (product_eligible=false for write action)
product section run
  -> c02_chroma_write.status = skipped_not_required
  -> c02_chroma_query.* = per profile (see Brown & Brown below)
  -> reads existing index only
```

### Cross-cutting invariant (W2 + W4)

Product PASS may depend on **read/query receipts** (`c02_chroma_query`, per-lane completion) and **graph/ledger authority receipts** (`c0_authority_mode=ledger_graph_primary`, C0.3 bindings), **never** on same-run Chroma **write** receipts (`c02_chroma_write` from the section generation run).

---

## Context (SCQA)

- **Situation** — Brown & Brown exec-summary runs exercise live Qwen vLLM and BGE, but the pipeline also performs automatic C0.2 `fact_vectors` upserts, bounded-section C0 skips hybrid retrieve, and product fail-closed is not the default for every `python -m apps_rg` invocation. Chroma default EF guard landed in `chroma_precomputed_collection.py` (2026-05-22) but legacy collections and env gaps remain.
- **Complication** — Operators cannot tell whether BGE ran for *selection* vs *index refresh*; R1B can fall back to 32-dim `pseudo_digest`; C0 retrieve fail-soft continues without hybrid lanes; substitutes remain legal unless whole-run envelope or explicit flags are set; modular phase0 synthetic artifacts can stand in for real lanes.
- **Question** — How do we make product/runtime proof paths use exactly one embedding authority (BGE-M3 explicit) and one generation authority (Qwen vLLM), with receipts that name any intentional non-live path?
- **Answer** — Tighten defaults and flags, add opt-out for lane upsert, fail-closed dense C0 on product, audit Chroma EF + vector dims, and extend contract tests so substitutes cannot PASS product bars without explicit harness env.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Audit receipt + env runbook (no code) | ~8K | Chroma forbid-EF merge present | 🔲 TODO | Operator runbook + gap inventory on disk |
| W1 | W1.1–W1.4 | Fail-closed **all CLI** by default | ~30K | Opt-out explicit only | 🔲 TODO | Every `python -m apps_rg` invocation strict unless shortcuts |
| W2 | W2.1–W2.5 | Ingest ≠ retrieval; product **no** lane upsert | ~28K | Batch index pre-built | 🔲 TODO | PASS = hybrid read OK; write optional index refresh only |
| W3 | W3.1–W3.3 | Chroma/BGE hardening + legacy collection audit | ~35K | Operator can re-run batch ingest | 🔲 TODO | CI/advisory script detects DefaultEmbeddingFunction collections |
| W4 | W4.1–W4.5 | C0 hybrid retrieval + ledger-primary FEC + B&B strict profile | ~75K | **Approved** contract locked | 🔲 TODO | All required query lanes or BLOCKED; `ledger_graph_primary` |
| W5 | W5.1–W5.2 | R1B pseudo-digest + dim guards | ~20K | R1B collection separate from fact_vectors | 🔲 TODO | No 32-dim upsert into BGE collections on product |
| W6 | W6.1–W6.3 | Qwen/judge/assembly substitute cleanup | ~25K | Offline stub stays disabled | 🔲 TODO | No live path references effective offline stub; mock matrix green |
| W7 | W7.1 | Modular phase0 vs product bar | ~15K | Tied to assembly debt plan | 🔲 TODO | Phase1 cannot PASS with only phase0_synthetic lanes |
| W8 | W8.1–W8.2 | Verification, docs, Notion backlog linkage | ~12K | NOTION_TOKEN for registration | 🔲 TODO | Contract gates + operator checklist |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Substitute inventory receipt | `docs/reports/apps_rg/` | Confusion at exec-summary run | ~8K | 🔲 TODO |
| W1.1 | Default strict all CLI entry | `__main__.py`, `product_output_policy.py` | Any invocation | ~10K | 🔲 TODO |
| W1.2 | Receipt `proof_class` + startup policy | embedding settings receipt | Operator visibility | ~8K | 🔲 TODO |
| W1.3 | Section+files proof bar (additive) | preflight, lane CLIs | Brown & Brown | ~7K | 🔲 TODO |
| W1.4 | Block bypass env paths | `qwen_live_only_guard`, guards | Regression | ~5K | 🔲 TODO |
| W2.1 | Product section: skip lane upsert by default | `evidence_room.py`, `c02_fact_vector_ingest.py` | Per-run BGE churn | ~8K | 🔲 TODO |
| W2.2 | `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH` | opt-in non-product write | Index refresh class | ~6K | 🔲 TODO |
| W2.3 | Receipts: `c02_chroma_write` vs `c02_chroma_query` | `c0_evidence_room_receipt.json` | Operator confusion | ~6K | 🔲 TODO |
| W2.4 | Product PASS: query required, not write | `product_output_policy.py`, lane bar | Upsert mistaken for proof | ~5K | 🔲 TODO |
| W2.5 | Align ingest runbook (batch canonical) | `chroma_ingest_pipeline`, docs | Stale index | ~3K | 🔲 TODO |
| W3.1 | Centralize all Chroma opens | `c0_binding.py`, any stray `get_or_create_collection` | MiniLM leakage | ~15K | 🔲 TODO |
| W3.2 | Legacy collection audit script | `ops_scripts/ci/check_*` or `tools/apps_rg/` | Old DB rows | ~12K | 🔲 TODO |
| W3.3 | Re-ingest runbook | `tools/ingestion/chroma_ingest_pipeline.py` docs | 384d vs 1024d mix | ~8K | 🔲 TODO |
| W4.1 | C0 hybrid retrieval fail-soft → product fail-closed | `c0_binding.py`, `c05_fec_packet.py` | Silent skipped hybrid lanes | ~18K | 🔲 TODO |
| W4.2 | Bounded section retrieval mode receipt | `section_fec_bridge.py`, `c0_metrics.json` | spine_c0_retrieve_skipped opaque | ~12K | 🔲 TODO |
| W4.3 | Wire hybrid C0.2 retrieve on bounded lanes | `c05_fec_packet.py`, `evidence_room.py`, `c0_binding.py` | skip root cause | ~20K | 🔲 TODO |
| W4.4 | Ledger-primary FEC merge policy | `c05_fec_packet.py`, `c04_stratify.py` | retrieval replaces authority | ~15K | 🔲 TODO |
| W4.5 | Brown & Brown strict query profile | section profile / role_family | empty_allowed leak | ~10K | 🔲 TODO |
| W5.1 | Block pseudo in Chroma upsert paths | `r1b_chroma_read_surface_projection.py`, `r1b_bge_embedding.py` | 32d vs 1024d | ~12K | 🔲 TODO |
| W5.2 | R1B query vector receipt | `r1b_governed_receipt_emission.py` | mapping_policy pseudo | ~8K | 🔲 TODO |
| W6.1 | Purge offline-stub call sites | `headline_lane.py`, `competencies_lane_runtime.py`, docs | Dead imports / branches | ~10K | 🔲 TODO |
| W6.2 | Assembly structural_only receipts | `full_resume_llm_coherence.py`, `final_resume_assembler.py` | Hidden judge skip | ~8K | 🔲 TODO |
| W6.3 | Cross-lane mock contract expansion | `tests/_apps_contract/` | Mock judges on product | ~7K | 🔲 TODO |
| W7.1 | Phase1 product bar vs phase0_synthetic | `modular_resume_generation.py`, `product_output_policy.py` | Fake lane PASS | ~15K | 🔲 TODO |
| W8.1 | Contract tests bundle | `tests/unit/apps_rg/`, `tests/_apps_contract/` | Regression | ~8K | 🔲 TODO |
| W8.2 | Operator checklist + AGENTS pointer | `AGENTS.md` or `docs/cursor/apps_rg_runtime_proof.md` | Run discipline | ~4K | 🔲 TODO |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Audit receipt | ✅ PASS | — | inventory doc |
| W1 | Fail-closed all CLI | ✅ PASS | policy tests | product_output_policy, __main__ |
| W2 | Ingest ≠ retrieval | ✅ PASS | lifecycle tests | c02_chroma_lifecycle, evidence_room |
| W3 | Chroma/BGE hardening | ✅ PASS | chroma tests | c0_binding, EF audit script |
| W4 | C0 retrieval policy | ✅ PASS | — | c05_fec_packet, c0_binding |
| W5 | R1B pseudo guards | ✅ PASS | — | r1b_chroma_read_surface_projection |
| W6 | Qwen/judge cleanup | ✅ PASS | test_w6_offline_stub_lane_imports | W6.1 import purge |
| W7 | phase0 synthetic bar | ✅ PASS | — | product_output_policy |
| W8 | Verification + docs | ✅ PASS | test_c02_chroma_lifecycle_* | operator checklist |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Substitute inventory receipt | 🔲 TODO |
| W1.1 | Default strict all CLI | 🔲 TODO |
| W1.2 | proof_class receipts | 🔲 TODO |
| W1.3 | Section+files proof bar | 🔲 TODO |
| W1.4 | Block bypass paths | 🔲 TODO |
| W2.1 | Product skip lane upsert | 🔲 TODO |
| W2.2 | Index refresh opt-in | 🔲 TODO |
| W2.3 | write vs query receipts | 🔲 TODO |
| W2.4 | PASS needs query not write | 🔲 TODO |
| W2.5 | Batch ingest runbook | 🔲 TODO |
| W3.1 | Centralize Chroma opens | 🔲 TODO |
| W3.2 | Legacy EF audit script | 🔲 TODO |
| W3.3 | Re-ingest runbook | 🔲 TODO |
| W4.1 | C0 hybrid retrieval fail-closed | 🔲 TODO |
| W4.2 | Retrieval mode receipt | 🔲 TODO |
| W5.1 | Pseudo Chroma block | 🔲 TODO |
| W5.2 | R1B vector receipt | 🔲 TODO |
| W6.1 | Offline-stub purge | 🔲 TODO |
| W6.2 | Assembly receipts | 🔲 TODO |
| W6.3 | Mock contract tests | 🔲 TODO |
| W7.1 | phase0 product bar | 🔲 TODO |
| W8.1 | Contract tests | 🔲 TODO |
| W8.2 | Operator checklist | 🔲 TODO |

---

## Out Of Scope

- Editing `agentic_core` GPTCache / L2 semantic cache Chroma paths (document + quarantine only; see `semantic_cache_persistence_quarantine.py`).
- Replacing ledger/graph authority with retrieval hits (retrieval is additive only — see W4 design contract).
- Hugging Face hub download of BGE weights (local path / pre-provisioned only).
- Notion backlog row creation for each wave (optional post-approval).

---

## Substitute Inventory (baseline — pre-implementation)

| ID | Substitute | Authority replaced | Trigger today | Target behavior |
|----|------------|-------------------|---------------|-----------------|
| S1 | Chroma `DefaultEmbeddingFunction` (MiniLM 384d) | BGE-M3 1024d | Unguarded `get_or_create_collection` | **Blocked** on all apps_rg opens; audit legacy DB |
| S2 | `pseudo_digest_fallback` (32d) | BGE-M3 | BGE load fail + not fail-closed | **Fail-closed** on product; never upsert 32d to Chroma |
| S3 | Ledger/graph slice (C0.2 fetch) | Retrieval authority | Bounded evidence room | **Primary** — `C0_AUTHORITY=ledger_graph_primary` |
| S4 | Skipped C0.2 **hybrid retrieval** lane | Dense + sparse/BM25 + metadata/exact | C05 skip / fail-soft | **Product FAIL** if any required lane skipped |
| S5 | C0 Chroma retrieve fail-soft | Hybrid retrieval completion | Exception in `c0_retrieve_apps_rg` | **FAIL** on product when C0.2 mandatory |
| S6 | C0.2 lane `maybe_upsert` | Index **write** (ingest) | Every section lane + Chroma dir | **Product: write OFF**; opt-in `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH` only |
| S7 | `APPS_RG_ALLOW_PRODUCT_SHORTCUTS` | Fail-closed | Opt-in shortcuts only | **W1:** strict **all** `python -m apps_rg` by default |
| S8 | Qwen offline stub env | Live vLLM | Env (disabled in code) | Keep **exit 2** in guard; remove dead branches |
| S9 | `--mock-judges` / MOCKED X1D | Live judges | Test harness | Already blocked on product CLI; extend tests |
| S10 | `APPS_RG_ASSEMBLY_STRUCTURAL_ONLY` | Full-resume LLM judge | Env | Receipt on package; off when fail-closed |
| S11 | `phase0_synthetic` lane L2 | REAL_LLM lanes | Modular phase0 / missing lanes | **Block** product PASS |
| S12 | X1D cloud judges (Gemini/OpenAI/Anthropic) | — (not Qwen mock) | Always on exec summary | **Document** as separate providers; BLOCKED ≠ MOCKED |

**Already landed (do not re-implement):** `chroma_precomputed_collection.py`, `APPS_RG_FORBID_CHROMA_DEFAULT_EF`, `qwen_offline_contract_stub` hard-off, `require_live_bge_embeddings()` on product path.

---

## Wave 0 — Audit Receipt (review only)

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Write `docs/reports/apps_rg/runtime_substitute_inventory_20260522.md` mirroring S1–S12 with file:line refs | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Receipt lists every env flag, receipt field, and operator symptom (e.g. “BGE loaded but briefing not embedded”).
- Links to exec_summary artifact examples under `artifacts/apps_rg/runtime_proofs/`.

---

## Wave 1 — Product Fail-Closed (all CLI by default)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: ACCEPTED
CHECKPOINT: B

**User decision (2026-05-22, revised):** **All** `python -m apps_rg` invocations are strict by default — section lanes, full integrated run, diagnostics, any entry path. No weaker envelope for non-section commands.

**Strict means (uniform):**
- Live Qwen vLLM (no offline stub / force-stub env)
- Live BGE when Chroma configured (`require_live_bge_embeddings()`)
- No pseudo-digest vectors on product paths
- Mock judges blocked on product CLI (existing `assert_production_runtime`)
- **Opt-out only:** `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` or `APPS_RG_TEST_HARNESS=1`

**Implementation sequence (phased delivery, same policy everywhere):**

```text
W1.1: product_fail_closed_runtime() default true at __main__ (all argv shapes)
W1.2: startup + apps_rg_embedding_settings.json → proof_class, product_fail_closed=true
W1.3: section runs additionally require JD + briefing file paths for SECTION_FILES_PROOF bar
W1.4: remove/weaken bypass paths; document opt-out env
```

**Phases**:
- **W1.1** — Change `product_output_policy.product_fail_closed_runtime()` default: true for all `python -m apps_rg` unless `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` or test harness (invert today’s `APPS_RG_ALLOW_PRODUCT_SHORTCUTS` default-off behavior) | ~10K | PHASE_STATUS: TODO
- **W1.2** — Print and persist `product_fail_closed=true` on every CLI start; extend embedding settings receipt | ~8K | PHASE_STATUS: TODO
- **W1.3** — **Additive** bar for `--section` lanes: resolvable `--jd` + `--manual-brief` files → `proof_class=SECTION_FILES_PROOF` (Brown & Brown); does not relax global strictness | ~7K | PHASE_STATUS: TODO
- **W1.4** — Audit `APPS_RG_WHOLE_RUN_ENVELOPE` / `APPS_RG_CORRELATED_CLI_RUN` as redundant triggers once default is strict; keep as explicit receipts only | ~5K | PHASE_STATUS: TODO

**Acceptance**:
- `python -m apps_rg` (no args), `--section …`, whole-run envelope: all log `product_fail_closed=true` without extra env.
- `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` → substitutes allowed (dev/plumbing only; receipt `proof_class=SHORTCUTS_ALLOWED`).
- Full run and section run share same embedding/C0 fail-closed policy (W1 strict all CLI; W2 write vs W4 read).

---

## Wave 2 — Ingest ≠ retrieval (approved design)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: ACCEPTED
CHECKPOINT: B

**User decision (2026-05-22, revised):** Separate **ingestion (write)** from **retrieval (read)**. Product section runs must not depend on same-run Chroma upsert.

### W2 design contract (7 rules)

| # | Rule |
|---|------|
| 1 | **Batch ingest** (`chroma_ingest_pipeline --collection fact_vectors`) is the **canonical** `fact_vectors` index build. |
| 2 | **Product section runs** must **not require** per-run Chroma upsert (`maybe_upsert_c02_fact_vectors` skipped by default on product). |
| 3 | **C0.2 hybrid retrieval** reads **existing** indexes and **must run** when required by section profile (W4 fail-closed if lane skipped). |
| 4 | **Lane upsert disabled by default**; `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` only on **dedicated pre-run index maintenance** (separate receipt `index_build_receipt`) — never product-classified, never same-run as section generation. |
| 5 | Receipts **must distinguish** `c02_chroma_write` (ingest/upsert) from `c02_chroma_query` (hybrid retrieve lanes). |
| 6 | **Product PASS** may require successful **query/read** (per profile + W4); must **not** require successful **same-run upsert/write**. |
| 7 | No dense/BM25/metadata hit may **replace** ledger/graph authority (W4 `c0_authority_mode=ledger_graph_primary`). |

**Pipeline (locked):**

```text
[Batch ingest]     → fact_vectors index (canonical write path)
[Product section]  → authority load (ledger) + hybrid retrieve (read index) — NO default lane write
[Index refresh]    → lane upsert only when APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1
```

| Path | `c02_chroma_write` | `c02_chroma_query` | Product PASS depends on |
|------|-------------------|-------------------|-------------------------|
| Product section | `skipped_not_required` | **Required** per profile (W4) | Query lanes + ledger authority only |
| Pre-run index maintenance | `ATTEMPTED` → `index_build_receipt` | N/A (separate command) | `product_eligible=false`; not section PASS |
| Test harness | May skip both | Mock/pseudo per harness | Harness rules |

**Phases**:
- **W2.1** — Default: `maybe_upsert_c02_fact_vectors` **not called** for product section evidence room; receipt `c02_chroma_write.status=skipped_not_required` | ~8K | PHASE_STATUS: TODO
- **W2.2** — `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` for **operator/CI index maintenance** (dedicated pre-run entrypoint preferred; emit `index_build_receipt.json`; `proof_class=INDEX_MAINTENANCE`). If refresh runs **inside the same section run**, it must **not** produce release-eligible product proof: same-run write+read cannot be used as product PASS evidence. Reject refresh flag on `--section` product paths | ~6K | PHASE_STATUS: TODO
- **W2.3** — Split receipt fields: `c02_chroma_write` (upsert_count, bge_embed_for_write) vs `c02_chroma_query` (dense/sparse/metadata lane completion per W4) | ~6K | PHASE_STATUS: TODO
- **W2.4** — `lane_run_dir_meets_product_bar` / package gates: do not require `c02_fact_vectors_ingest_receipt.status=PASS`; require hybrid retrieve receipt OK when profile mandates (W4) | ~5K | PHASE_STATUS: TODO
- **W2.5** — Operator doc: preflight `check_apps_rg_fact_vectors_readiness` / batch ingest before product Brown & Brown runs | ~3K | PHASE_STATUS: TODO

**Acceptance**:
- Brown & Brown product exec-summary: **no BGE write/upsert path** for lane upsert; BGE may still load for **query embeddings** when retrieval runs; `c02_chroma_write.status=skipped_not_required`.
- Product PASS with stale/missing index → **FAIL at retrieve** (W4), not hidden by same-run upsert.
- Pre-run index maintenance produces `index_build_receipt`; section run never claims product PASS from write.

### Brown & Brown product profile (exec_summary — strict)

Pre-run: batch ingest or CI-seeded `fact_vectors` (readiness gate).

```text
exec-summary product run:
  c02_chroma_write.status     = skipped_not_required
  c02_chroma_query.dense      = required → completed | failed_BLOCKED
  c02_chroma_query.sparse     = required → completed | failed_BLOCKED
  c02_chroma_query.metadata   = required → completed | failed_BLOCKED
  c0_authority_mode           = ledger_graph_primary
```

- **`empty_allowed`** is profile-specific only; **not** for Brown & Brown product proof.
- If any required query lane is skipped or errors: `STATUS=BLOCKED`, `product_eligible=false`.
- Implement via section profile / role_family `INSURANCE_BROKERAGE_IT_INNOVATION` + `executive_summary` mandatory lane set (W4.2 + W4.5).

---

## Wave 3 — Chroma / BGE Hardening

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Route any remaining apps_rg `get_or_create_collection` through `get_precomputed_embeddings_collection` | ~15K | PHASE_STATUS: TODO
- **W3.2** — Add `ops_scripts/ci/check_apps_rg_chroma_collection_ef.py` (advisory): flag collections whose EF is DefaultEmbeddingFunction | ~12K | PHASE_STATUS: TODO
- **W3.3** — Operator runbook: re-run `chroma_ingest_pipeline --collection fact_vectors --execute` after EF fix | ~8K | PHASE_STATUS: TODO

**Acceptance**:
- Grep gate or CI script fails if raw `get_or_create_collection` appears in `apps_rg/` outside helper.
- Audit script prints collection name + EF class for `fact_vectors`.

---

## Wave 4 — C0 Retrieval Policy

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: ACCEPTED
CHECKPOINT: C

### W4 design contract (approved 2026-05-22)

**Fail-closed:** Product **FAIL** if any **required C0.2 retrieval lane** is skipped, unavailable, or fail-soft-swallowed when `apps_rg_c0_dense_sparse_mandatory()` (and product fail-closed).

**C0.2 hybrid retrieval** (product language — implement via `c0_retrieve_apps_rg` / `_perform_bounded_section_retrieval`, merged in C0.5 FEC; distinct from ledger **fetch** in `fetch_c02_evidence_atoms`):

| Lane | Mechanism | Role |
|------|-----------|------|
| Dense | BGE-M3 vector query on `fact_vectors` | Add candidate evidence, support, exclusions |
| Sparse | BM25 / lexical lane (`query_sparse_lexical_lane`, RRF merge) | Same — additive |
| Metadata / exact | Metadata filter + exact lookup seam | Citation hydration, bounded lookups |

**Authority (non-negotiable):**
- **Ledger/graph facts remain primary** (`proof_pool` / `augmented_skills_graph` slice).
- C0.2 retrieval may **add**: candidates, support, exclusions, citation hydration.
- C0.2 retrieval may **not replace** ledger/graph authority (no retrieval-only FEC for product).
- **C0.3** (`expand_c03_graph_bindings`) validates **lineage, contradiction, supersession, authority relationship** — graph decides claim support; retrieval does not override C0.3 verdicts.

**C0 pipeline (conceptual — approved wording):**

```text
C0.2 authority load      → ledger/graph primary facts     (code: c02_evidence_fetch.py)
C0.2 hybrid retrieve     → dense + sparse + metadata      (code: c0_binding.py)
C0.3 graph validation    → lineage / contradiction / supersession / authority
C0.4 stratify            → MUST_USE from ledger slice; retrieval informs support tiers
C0.5 FEC                 → merge without replacement      (c0_authority_mode=ledger_graph_primary)
```

**Code map:** Authority load ≠ hybrid retrieve — do not label ledger load as “retrieval” in receipts or docs.

**Phases**:
- **W4.1** — C0 hybrid retrieval fail-soft → product fail-closed: any skipped/unavailable **required** C0.2 lane (dense, sparse/BM25 if profile-enabled, metadata/exact if enabled) → `C0EvidenceGapError` / X3_BLOCK; no fail-soft on product | ~18K | PHASE_STATUS: TODO
- **W4.2** — Receipts: `c0_retrieval_lanes` (per-lane status); **`c0_authority_mode=ledger_graph_primary` (mandatory)**; `c0_retrieval_mode` lane-specific values (see list below) | ~12K | PHASE_STATUS: TODO
  - `ledger_plus_hybrid_retrieval` (all required lanes for profile completed)
  - `ledger_plus_dense_only_profile`
  - `ledger_plus_sparse_only_profile`
  - `ledger_plus_metadata_exact_only_profile`
  - `C0_RETRIEVAL_LANE_SKIPPED` (FAIL on product)
  - `C0_RETRIEVAL_LANE_FAILED` (FAIL on product)
  - `C0_RETRIEVAL_INDEX_MISSING` (FAIL on product)
  - `C0_RETRIEVAL_INDEX_STALE` (FAIL on product)
- **W4.3** — Wire bounded-section C0.5 to invoke full hybrid retrieve on product (fix `spine_c0_retrieve_skipped:bounded_section_path` root cause) | ~20K | PHASE_STATUS: TODO
- **W4.4** — FEC merge policy: retrieval items appended; ledger atoms retain MUST_USE strata; retrieval cannot demote ledger facts to EXCLUDED without C0.3 graph rule | ~15K | PHASE_STATUS: TODO
- **W4.5** — Profile registry: Brown & Brown `executive_summary` → dense+sparse+metadata all **required** (no `empty_allowed`); per-lane `completed` \| `failed_BLOCKED` in `c02_chroma_query` | ~10K | PHASE_STATUS: TODO

**Acceptance**:
- Product exec-summary: all mandatory C0.2 lanes complete OR hard fail (no PASS with only ledger fetch).
- `c0_evidence_room_receipt.json` shows hybrid lane completion + C0.3 bindings unchanged in authority role.
- Dense uses explicit BGE `query_embeddings` only; sparse/metadata receipt refs present when profile requires them.

---

## Wave 5 — R1B Pseudo-Digest Guards

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W5.1** — Before Chroma upsert in R1B projection, assert `dimensions == 1024` and `embedding_model == BAAI/bge-m3` | ~12K | PHASE_STATUS: TODO
- **W5.2** — Receipt field `query_vector_source: bge_m3|pseudo_digest` on R1B read surface | ~8K | PHASE_STATUS: TODO

**Acceptance**:
- Product path cannot upsert 32-dim vectors into `apps_rg_r1b_semantic_cache_projection`.
- Test: BGE unavailable + fail-closed → raise before Chroma write.

---

## Wave 6 — Qwen / Judge / Assembly Substitutes

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W6.1** — Remove dead `synthetic_qwen_provider_result` / `OFFLINE_CONTRACT_STUB` branches where stub is always false | ~10K | PHASE_STATUS: TODO
- **W6.2** — Package assembly receipt: `structural_only`, `coherence_judges_skipped` when `APPS_RG_ASSEMBLY_STRUCTURAL_ONLY` | ~8K | PHASE_STATUS: TODO
- **W6.3** — Extend `test_apps_rg_section_mock_provider_policy.py` for all seven generated lanes | ~7K | PHASE_STATUS: TODO

**Acceptance**:
- `live_qwen_mock_env_violations()` covered by CLI integration test.
- Assembly package JSON includes judge skip reason when structural-only.

---

## Wave 7 — Modular phase0 Synthetic Bar

WAVE_ID: W7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W7.1** — Phase1 merge / `lane_run_dir_meets_product_bar` rejects `phase0_synthetic` in path or `runtime_generation_status != REAL_LLM` | ~15K | PHASE_STATUS: TODO

**Acceptance**:
- Integrated run cannot emit `generated_resume.json` PASS with only synthetic lane artifacts.
- Aligns with [apps-rg-resume-assembly-debt-burndown-56c022.md](.cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md) W3 product SSOT.

---

## Wave 8 — Verification & Operator Docs

WAVE_ID: W8
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W8.1** — Run contract bundle (embedding, chroma EF, mock policy, product policy). **Required test:** contract proves same-run `c02_chroma_write.status=ATTEMPTED` does **not** satisfy product PASS unless a separate pre-run `index_build_receipt` (or bound index-maintenance snapshot) is present **and** product `c02_chroma_query` receipts still pass | ~8K | PHASE_STATUS: TODO
- **W8.2** — Publish operator checklist: Brown & Brown exec summary env block | ~4K | PHASE_STATUS: TODO

**Commands**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/test_chroma_precomputed_collection.py tests/unit/apps_rg/test_embedding_settings_fail_closed.py tests/unit/apps_rg/test_product_output_policy.py -q
python -m pytest tests/_apps_contract/test_apps_rg_section_mock_provider_policy.py -q
```

**Acceptance**:
- All above tests pass; `run_contract_gates.py` green for new CI script if added in W3.2.
- Contract test: `c02_chroma_write.status=ATTEMPTED` in same section run → product PASS denied without bound pre-run `index_build_receipt`; PASS allowed only when query receipts + ledger authority receipts satisfy bar.

---

## Gap Register

**GAP-1: Bounded C0 — ledger vs hybrid retrieval semantics** — **RESOLVED**
- Product **FAIL** if any required C0.2 retrieval lane skipped.
- Ledger/graph **primary**; hybrid retrieval **additive** only; C0.3 graph **authority** for lineage/contradiction/supersession.
- W4.3–W4.4 implement merge + fail-closed lanes.

**GAP-2: Legacy Chroma data mixed dimensions**
- Re-ingest duration and downtime for `data/cache/chromadb`.
- Impact: W3.3 operator-run only; defer automated migration.

**GAP-3: Core GPTCache Chroma (agentic_core)**
- Separate MiniLM EF in L4 cache; not apps_rg SSOT.
- Impact: Document in W0 receipt; no code change in this plan.

**GAP-4: X1D judges are non-Qwen by design**
- Not a mock of Qwen but alternate providers; BLOCKED judges vs MOCKED must stay distinct in X3.
- Impact: W6 documentation only.

---

## Definition of Done

DoD-1: Plan registered in Notion Plans DB with Exists On Disk=true.
- Evidence: Notion page `36827693-f55c-8131-b393-f43334c46a10`; plan file present.
- Status: PASS

DoD-2: W0 audit receipt published with S1–S12 file references.
- Evidence: `docs/reports/apps_rg/runtime_substitute_inventory_20260522.md`
- Status: PASS

DoD-3: W1 all-CLI fail-closed + W2 product no lane write / retrieve required for PASS.
- Evidence: code + pytest; **live section receipt not captured** in this closeout.
- Status: PARTIAL (contract only)

DoD-4: Chroma EF audit script + centralized collection helper coverage.
- Evidence: `ops_scripts/ci/check_apps_rg_chroma_collection_ef.py`; `get_precomputed_embeddings_collection` on fact_vectors path.
- Status: PASS (advisory script; live DB audit optional)

DoD-5: Operator runtime proof checklist on disk.
- Evidence: `docs/cursor/apps_rg_runtime_proof.md`
- Status: PASS

DoD-6 (plan-level): W6 complete + Brown & Brown live exec-summary proof.
- Evidence: **missing** — W6.1 open; no `LIVE_RUNTIME_PROOF` run dir.
- Status: TODO — blocks PLAN_STATUS=PASS

---

## Verification vs Deferral

| Item | Verify in plan | Defer |
|------|----------------|-------|
| Chroma forbid-EF helper | ✅ Already in repo | — |
| Fail-closed all CLI by default | W1 | **Approved** (revised 2026-05-22; opt-out only) |
| Ingest ≠ retrieve; no product lane write | W2 | **Approved** (7 rules; PASS = query not write) |
| C0.2 hybrid lanes + ledger primary | W4 | **Approved** (FAIL if skipped; additive retrieval; C0.3 authority) |
| GPTCache core Chroma | W0 doc | Implementation |
| Full fact_vectors re-ingest automation | W3 runbook | CI automation |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=apps-rg-runtime-substitute-burndown-c4e8f1 path=.cursor/plans/apps-rg-runtime-substitute-burndown-c4e8f1.md status=Not Started
WAVE_START: plan=apps-rg-runtime-substitute-burndown-c4e8f1 wave=1
WAVE_COMPLETE: plan=apps-rg-runtime-substitute-burndown-c4e8f1 wave=1 note="+N tests, scope=fail-closed-defaults"
PLAN_COMPLETE: plan=apps-rg-runtime-substitute-burndown-c4e8f1 note="substitute burndown shipped"
```

---

## Related Plans

- [apps-rg-resume-assembly-debt-burndown-56c022.md](.cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md) — product SSOT / phase1 gates (W7 alignment)
- [_archive/2026-05/apps-rg-cross-section-mock-judge-policy-d8e4f2.md](.cursor/plans/_archive/2026-05/apps-rg-cross-section-mock-judge-policy-d8e4f2.md) — mock judge precedent
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
