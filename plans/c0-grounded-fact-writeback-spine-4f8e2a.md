---
plan_id: c0-grounded-fact-writeback-spine-4f8e2a
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/migration_receipts/PENDING_W4_core_fact_writeback_engine.json"
dod_exempt: false
supersedes: []
---

# C0 Grounded-Fact Write-Back Spine — Tiered fact_vectors, Async Staging, HITL Promotion

Close the gaps between the target C0→C7 grounded-fact write-back architecture (seed tier → retrieval → fusion → async staging → dedupe/score → HITL promotion gate → learned tier in ChromaDB) and the current implementation, and lift the generic mechanism into `agentic_core` so the spine — not an app overlay — owns C7.

> **plan_id discipline**: marker `plan=c0-grounded-fact-writeback-spine-4f8e2a`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — Plan `apps-rg-fact-vector-writeback-discipline-67652c` (DONE 2026-06-08) delivered a working write-back discipline in **apps_rg**: a pure routing classifier (`decide_write_back`: EXTRACT/FUSE/ENRICH → stage; GENERATED → semantic cache; no provenance → REJECT), a `fact_vectors_staging` Chroma collection, a hostile-verifier promotion gate (`promote_staged_fact_vectors`), and an env-flag HITL hold (`APPS_RG_FACT_VECTOR_PROMOTION_HITL`). Phase-0 seed (ledger + base-resume employment) populates the live `fact_vectors` collection at bootstrap; dense+sparse hybrid retrieval (RRF) is mandatory fail-closed for the 6 golden sections. The semantic-cache fork exists and is tagged `not_c0_fact_vectors`.
- **Complication** — The implementation diverges from the target two-tier architecture in eleven ways (Gap Register G1–G11). Highest-impact: (G1) no `tier: seed|learned` metadata anywhere, so the two tiers are indistinguishable at C2 read time; (G5) promotion upserts **dense Chroma only** — the mandatory fail-closed BM25/FTS5 sparse sidecar is never updated, so lanes diverge after every promotion; (G3) staging→promote runs **inline in the same call** (`c02_fact_vector_ingest.py:291`) — there is no async buffer, no dedupe beyond ID idempotency, no score floor; (G6) write-back forks at C0.2 retrieval time, not from post-fusion validated atoms, and promotion is not gated on the run's X3 disposition; (G7) the entire mechanism is app-locked in apps_rg while `agentic_core` has no C7 write-back stage/contract; (G8) durable vector writes bypass UWG and are invisible to `v_p0_write_bypass_uwg` (verified: 0 rows).
- **Question** — How do we make C0 follow the target write-back path — seed tier (R/O) + learned tier in `fact_vectors`, async staging with dedupe/score, HITL promotion, lane-parity-preserving writes — with the generic mechanism owned by `agentic_core` and apps supplying only meaning/config?
- **Answer** — Five waves: (W1) tier metadata + schema SSOT v2.1 + backfill; (W2) promotion correctness — dedupe, score floor, sparse-sidecar sync, standalone receipts; (W3) async decoupling — post-run X3-gated promotion, HITL drain CLI, FUSE/ENRICH fork; (W4) extract the generic write-back engine into `agentic_core/L4_state/fact_writeback/` behind an Author-Gate with profile-driven app config; (W5) governance visibility — UWG-visible mutation receipts, ADG detector coverage, CI parity + schema-conformance gates.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3, W1.4 | Tier metadata (`seed`/`learned`) + schema SSOT v2.1 + backfill | ~60K | Chroma store reachable; existing rows classifiable by `write_back_operation` presence | 🔲 TODO | 100% of fact_vectors rows carry `tier`; schema yaml declares all stamped fields; scoped tests green |
| W2 | W2.1, W2.2, W2.3, W2.4 | Promotion correctness: dedupe, score floor, sparse-sidecar sync, standalone receipt | ~85K | FTS5 sidecar schema supports incremental upsert; BGE-M3 embeds available | 🔲 TODO | Promotion updates BM25 sidecar; dense/sparse parity check in receipt; dup digests skipped |
| W3 | W3.1, W3.2, W3.3, W3.4 | Async decoupling: deferred X3-gated promotion, HITL drain CLI, FUSE/ENRICH fork | ~95K | Run completion seam (post-X3) accessible in apps_rg `__main__` flow | 🔲 TODO | Staged rows promote only after X3_ALLOW; drain CLI lists/approves/rejects held rows; fused atoms staged |
| W4 | W4.1, W4.2, W4.3 | Generic core engine in `agentic_core/L4_state/fact_writeback/` + app profile config | ~120K | Author-Gate approves core extraction; CoreAdditionAuthorGateReceipt issued | 🔲 TODO | Core engine has zero app literals; apps_rg is thin binding + profile; boundary audit PASS |
| W5 | W5.1, W5.2, W5.3 | Governance visibility: UWG-visible writes, ADG detector coverage, CI gates | ~70K | Ledger writer (`emit_ledger_event`) available; CI gate registry accepts new gates | 🔲 TODO | Promotion emits UWG-visible receipt; raw-`chromadb`-import detector fires; parity + schema gates green in CI |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | fact_vectors_schema.yaml v2.1 — declare tier + stamped fields | 🔲 TODO |
| W1.2 | Stamp `tier=seed` (bootstrap) and `tier=learned` (promotion) | 🔲 TODO |
| W1.3 | Backfill migration for existing rows + receipt | 🔲 TODO |
| W1.4 | Scoped tests + C2 read parity verification | 🔲 TODO |
| W2.1 | Digest-based dedupe at promotion | 🔲 TODO |
| W2.2 | Promotion score floor (confidence × proof_status × authority) | 🔲 TODO |
| W2.3 | Sparse FTS5 sidecar sync on promotion + lane-parity check | 🔲 TODO |
| W2.4 | Standalone promotion receipt artifact | 🔲 TODO |
| W3.1 | Deferred promotion mode (stage in-run, promote post-run) | 🔲 TODO |
| W3.2 | HITL drain CLI (list / approve / reject held rows) | 🔲 TODO |
| W3.3 | X3-disposition gate on promotion (ALLOW-only) | 🔲 TODO |
| W3.4 | FUSE/ENRICH write-back fork from evidence-contract path | 🔲 TODO |
| W4.1 | Author-Gate: core extraction decision + receipt | 🔲 TODO |
| W4.2 | Generic engine in agentic_core + writeback profile keys | 🔲 TODO |
| W4.3 | Rewire apps_rg as thin binding; contract tests | 🔲 TODO |
| W5.1 | UWG-visible mutation receipt / ledger event on promotion | 🔲 TODO |
| W5.2 | ADG detector coverage + fix raw `import chromadb` (G9) | 🔲 TODO |
| W5.3 | CI gates: lane parity + schema conformance | 🔲 TODO |

---

## Out Of Scope

- Semantic (embedding-cosine) near-duplicate detection beyond chunk-digest dedupe — deferred (recorded in DoD Verification-vs-Deferral).
- L6 confidence adjustment / usage-feedback / eviction loop for learned-tier facts (corpus graduation) — separate follow-up plan.
- A graphical HITL review UI — the W3.2 CLI is the review surface; UI deferred.
- apps_qna / apps_lic adoption of the generic engine — W4 makes it possible; adoption is per-app follow-up work.
- Rebuilding the C0.3 graph lane or the BM25 ranking algorithm itself.

---

## Target Architecture (the contract this plan implements)

```
C0 seed bootstrap ──► fact_vectors (tier=seed, R/O)
C1 intent ──► C2 retrieval (dense+sparse+graph; reads BOTH tiers) ──► C3 fusion
C3 ──(solid)──► C4 validate ──► C5 HITL ──► C6 assemble ──► semantic cache (intent vectors)
C3 ──(dashed)─► STAGING BUFFER (async; dedupe, score) ──► HITL PROMO GATE ──► C7 write-back
                                                            └──► fact_vectors (tier=learned)
Next query reads both tiers at C2. The two paths fork at C3 and write to different stores.
```

Mapping to seams (current locations):

| Box | Current seam | State |
|---|---|---|
| C0 seed | [build_section_fact_vectors.py](tools/apps_rg/build_section_fact_vectors.py), [bootstrap_fact_vectors.py](tools/apps_rg/bootstrap_fact_vectors.py) | ✅ exists; ❌ no tier tag |
| C1 intent | [r1b_intent_vector.py](apps_rg/cache/r1b_intent_vector.py) | ✅ |
| C2 retrieval | `agentic_core/L0_routing/c0_retrieval/` + [c02_product_hybrid_retrieval.py](apps_rg/runtime/c0/c02_product_hybrid_retrieval.py) | ✅ dense+sparse mandatory; ❌ tier-blind |
| C3 fusion | `c0_retrieval/shape.py`, `evidence_contract.py` | ✅; ❌ no write-back fork from FUSE/ENRICH outputs |
| C4 validate | `c0_retrieval/gates.py` G0–G10 + X2 | ✅; ❌ not bound to promotion |
| C5 HITL | `agentic_core/L5_safety/contracts/hitl.py` (+adapters) | ⚠️ exists; unused by promotion |
| C6 assemble | `c0_retrieval/final_contract.py` | ✅ |
| Staging buffer | [fact_vector_write_back.py:55](apps_rg/runtime/c0/fact_vector_write_back.py) `fact_vectors_staging` | ⚠️ pass-through, not async, no dedupe/score |
| HITL promo gate | [fact_vector_write_back.py:174-286](apps_rg/runtime/c0/fact_vector_write_back.py) | ⚠️ env-flag hold only; no drain surface |
| C7 write-back | [c02_fact_vector_ingest.py:291](apps_rg/runtime/c0/c02_fact_vector_ingest.py) inline | ⚠️ same-call; dense-only |
| Semantic cache | `r1b_semantic_cache` (`not_c0_fact_vectors` marker) | ✅ |
| Tier separation | — | ❌ missing entirely |

---

## Gap Register

**G1 — No tier separation (seed vs learned).** No `tier` field in [fact_vectors_schema.yaml](apps_rg/config/domain_contract/fact_vectors_schema.yaml) (v2.0); neither the seed path nor `promote_staged_fact_vectors` stamps a tier. C2 cannot distinguish, weight, or audit the tiers. *Impact: the central two-tier contract of the target architecture does not exist.*

**G2 — Schema SSOT drift.** Ingest stamps `candidate_fact_id`, `confidence`, `proof_status`, `source_span_ref`, `source_type`, `write_back_operation` ([c02_fact_vector_ingest.py:54-67](apps_rg/runtime/c0/c02_fact_vector_ingest.py)) — none declared in the schema SSOT yaml. *Impact: schema gate cannot validate what's actually written.*

**G3 — Staging is pass-through, not an async buffer.** `maybe_upsert_c02_fact_vectors` stages then promotes in the same call (line 291). No dedupe beyond Chroma ID idempotency; no scoring; "async, dedupe, score" semantics absent. *Impact: staging adds a hop, not a control point.*

**G4 — HITL gate has no review surface.** `APPS_RG_FACT_VECTOR_PROMOTION_HITL=1` holds rows in staging forever; no list/approve/reject drain; L5 `human_approval_adapter` unused. Default is OFF ⇒ fully automatic promotion. *Impact: C5 box is theater unless the env flag is set, and a dead-end if it is.*

**G5 — Sparse sidecar diverges after promotion.** Promotion upserts dense Chroma only ([fact_vector_write_back.py:266-278](apps_rg/runtime/c0/fact_vector_write_back.py)); the FTS5/BM25 sidecar (`data/cache/sparse/fact_vectors.db`, built offline by [build_sparse_index.py](tools/generate/ingestion/build_sparse_index.py)) is never updated. Sparse is mandatory fail-closed for the 6 golden sections. *Impact: learned facts invisible to the sparse lane; RRF merge asymmetric; parity decays with every promotion.*

**G6 — Write-back forks at the wrong point and ignores run disposition.** Staging fires from [evidence_room.py:132](apps_rg/runtime/c0/evidence_room.py) during C0.2 retrieval — before section generation, X2 validation, judges, or X3. Target forks at C3 (transformed grounded atoms) with C4/C5 upstream of promotion. *Impact: atoms from runs that later X3_BLOCK still get promoted.*

**G7 — Mechanism is app-locked; agentic_core has no C7.** The whole write-back surface lives in `apps_rg/runtime/c0/`. `agentic_core/L0_routing/c0_retrieval/` defines C0.0–C0.6 but no write-back stage, contract, or engine. *Impact: every future app re-implements staging/promotion/tiering; core spine cannot enforce the discipline.*

**G8 — Durable vector writes bypass UWG and are invisible to governance.** Spine law: "UWG commits, L4 stores; no direct durable write path from L2, L3, tools." `v_p0_write_bypass_uwg` returns **0 rows** for these writes (verified against snapshot `06082026_1212`) because ChromaDB upserts aren't modeled as L4 durable writes. *Impact: a durable, learning-relevant write path with zero governance witness.*

**G9 — Raw `import chromadb` in apps_rg ingest.** [c02_fact_vector_ingest.py:169](apps_rg/runtime/c0/c02_fact_vector_ingest.py) imports the raw SDK while the promotion path correctly routes through `agentic_core.L4_state.utils.client.chroma_client.chromadb_module`. `v_p0_apps_direct_infra` does not flag it (only sqlite3 import patterns currently detected). *Impact: infra-wiring inconsistency + detector blind spot.*

**G10 — No L6 learning loop for the learned tier.** No usage stats, freshness updates, confidence adjustment, or eviction for promoted facts; `freshness_status` exists in schema but is never maintained. *Impact (bounded here): W5 emits the receipts/ledger events L6 needs; the loop itself is deferred scope.*

**G11 — Semantic-cache boundary untested at the contract level.** The `not_c0_fact_vectors` marker exists; a contract test asserting GENERATED atoms can never reach `fact_vectors` (under both inline and deferred promotion modes) should pin it. *Impact: regression risk on the C3 fork.*

---

## ADG_HOTSPOT_REPORT

ADG Provenance: backend=sqlite+projection, snapshot=adg_indexed_06082026_1212.sqlite (182,313 nodes / 1,072,457 edges; Redis healthy, cache-hit capable)

P0 open (relevant views): `v_p0_write_bypass_uwg` = 0 rows (see G8 — absence is itself the finding); `v_p0_apps_direct_infra` = 1 row (unrelated app: `apps_01_bank_grade_servicing_ai_worker_runtime/.../ledger.py` sqlite3 import).

| rank | file | layer | violations | fan_in | impact | archetype | surfaces |
|------|------|-------|-----------|--------|--------|-----------|----------|
| 1 | apps_rg/runtime/c0/fact_vector_write_back.py (node 3748) | L_APP (×1.0) | 0 indexed (G5/G8 latent) | 2 verified (ingest, tests) | promotion gate = single choke | SAFETY_GATEKEEPER | Write, State, Security |
| 2 | apps_rg/runtime/c0/c02_fact_vector_ingest.py | L_APP (×1.0) | 1 (raw chromadb import, G9) | 1 verified (evidence_room) | durable-write entry | STATE_NODE | Write, State |
| 3 | apps_rg/runtime/c0/evidence_room.py | L_APP (×1.0) | 0 | section runners | orchestrates C0.2 fetch+ingest | ORCHESTRATOR | Execution, Write |
| 4 | agentic_core/L4_state/utils/client/chroma_client.py | L4 (×1.75) | 0 | sanctioned adapter | all governed Chroma I/O | CENTRAL_DEPENDENCY | State, Write |

Note: the three apps_rg seam modules are recent additions; their `imports`/`resolves_callsite` edges are not yet materialized in snapshot `06082026_1212` (fan-in queries on node 3748 / symbol 61972 returned 0 edges; projection blast radius 0 rows). Consumer counts above are DIRECTLY OBSERVED from file reads ([c02_fact_vector_ingest.py:22-27](apps_rg/runtime/c0/c02_fact_vector_ingest.py), [evidence_room.py:12,132](apps_rg/runtime/c0/evidence_room.py)), not graph-derived. Regenerate ADG after W1 lands to materialize edges.

---

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views / Projections Consulted
- `mv_hotspot_centrality` (top-10): none of the four seam files rank — highest apps_rg entry is `executive_summary_x2.py` (fan_in 299). Blast radius of this plan is bounded; the global hotspots (`lifecycle_trace_contract.py` fan_in 99,302; `path_constants.py` fan_in 1,131) are untouched.
- Graph projection blast radius (node 3748, 2 hops): 0 reachability rows — confirms new-module edge sparsity; treat blast estimates as file-read-derived until post-W1 ADG regen.
- `v_p0_write_bypass_uwg` + `v_p0_apps_direct_infra` (P-view cross-reference below). Additional MV families (`mv_graph_reverse_dependency_hotspots`, `mv_debt_concentration_hotspots`) are not exposed by the current `adg_sqlite` MCP toolset; evidence gathered via the exposed MV + projection + P-views.

### Semantic Edges Used
- relation_type: `imports` — Query: fan-in to module node 3748 (`fact_vector_write_back.py`). Finding: 0 edges in snapshot (new module); consumers verified by direct read instead.
- relation_type: `resolves_callsite` — Query: fan-in to symbol 61972 (`promote_staged_fact_vectors`). Finding: 0 edges in snapshot; the only call site is [c02_fact_vector_ingest.py:291](apps_rg/runtime/c0/c02_fact_vector_ingest.py) (DIRECTLY OBSERVED).

### Pre-Built P-Views Cross-Referenced
- `v_p0_write_bypass_uwg`: 0 rows — ChromaDB durable writes are structurally invisible to the UWG-bypass detector (G8). W5.2 extends coverage.
- `v_p0_apps_direct_infra`: 1 row, unrelated app — the raw `import chromadb` at c02_fact_vector_ingest.py:169 (G9) is NOT detected; detector only models sqlite3-style infra imports. W5.2 closes the blind spot.

### Graph-Layer-Derived Priority
Wave order is driven by: (a) SAFETY_GATEKEEPER seam (`fact_vector_write_back.py`) must gain tier stamping + parity BEFORE async decoupling multiplies write volume (W1→W2→W3); (b) L4 CENTRAL_DEPENDENCY adapter (`chroma_client.py`, ×1.75 layer multiplier) is touched only in W4/W5 with Author-Gate + receipts; (c) detector gaps (G8/G9) land last (W5) because they verify the end-state, not the transition.

---

## Wave 1 — Tier Metadata + Schema SSOT v2.1

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — apps_rg-owned schema + tools; no `agentic_core` edits in this wave.

**Phases**:
- **W1.1** — Schema v2.1: add `tier` (required; `seed|learned`), declare `candidate_fact_id`, `confidence`, `proof_status`, `source_span_ref`, `source_type`, `write_back_operation`, `promoted_at_utc`, `promotion_run_id` in [fact_vectors_schema.yaml](apps_rg/config/domain_contract/fact_vectors_schema.yaml); update `FactVectorSchema.validate_chunk` | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Stamp `tier=seed` in `chunk_to_chroma_document`/seed builders ([build_section_fact_vectors.py](tools/apps_rg/build_section_fact_vectors.py)); stamp `tier=learned` + `promoted_at_utc` + `promotion_run_id` inside `promote_staged_fact_vectors` at upsert-to-live | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Backfill: `ops_scripts/maintenance/backfill_fact_vectors_tier.py` (rows with `write_back_operation` ⇒ learned; else seed); idempotent; emits receipt `artifacts/apps_rg/fact_vectors_tier_backfill_receipt.json` | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — Tests: `tests/unit/apps_rg/runtime/c0/test_fact_vector_tiering.py` (stamping both paths, schema validation, backfill inference); verify C2 read parity (tier metadata present in query hits, retrieval results unchanged) | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- 100% of `fact_vectors` rows carry `tier` after backfill (receipt shows `untagged_after=0`).
- Schema yaml v2.1 declares every field the code stamps; `validate_chunk` enforces `tier`.
- Scoped pytest green; golden-section retrieval results byte-identical pre/post (tier is additive metadata).

---

## Wave 2 — Promotion Correctness: Dedupe, Score Floor, Sparse Parity

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Dedupe at promotion: before upsert-to-live, check `chunk_digest` against live collection (metadata `where` query); duplicates skipped + recorded `{"id", "reason": "duplicate_digest:<live_id>"}` in receipt | ~20K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Score floor: compute `promotion_score` from `confidence` (HIGH=1.0/MEDIUM=0.6/LOW=0.3) × `proof_status` (proof_eligible=1.0 else 0.5) × `authority_class` (PRIMARY=1.0/SUPPORTING=0.8); floor default 0.48, configurable; below-floor rows held (not deleted), reason recorded | ~20K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Sparse sync: add incremental `upsert_documents()` to [build_sparse_index.py](tools/generate/ingestion/build_sparse_index.py) (FTS5 + term_freq delete-then-insert by id); call from promotion after live upsert; fallback = full per-collection rebuild; record `sparse_synced`, `dense_count`, `sparse_doc_count` in receipt | ~30K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.4** — Standalone receipt: persist `fact_vector_promotion_receipt.json` into the run `artifact_dir` (today the promotion dict is only embedded in the ingest receipt) | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Promoting a batch updates BOTH dense collection and FTS5 sidecar; `dense_count == sparse_doc_count` parity recorded.
- Re-promoting identical content yields `promoted_count=0` with duplicate reasons.
- Below-floor atoms remain in staging with reasons; never silently deleted.

---

## Wave 3 — Async Decoupling, X3 Gate, HITL Drain, FUSE/ENRICH Fork

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Deferred mode: `APPS_RG_FACT_VECTOR_PROMOTION_MODE=inline|deferred` (default `inline` for back-compat). Deferred: `maybe_upsert_c02_fact_vectors` stages only; staged metadata gains `run_id`, `staged_at_utc`; promotion runs at run completion | ~25K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Drain CLI: `tools/apps_rg/promote_fact_vectors.py` — `--list` (held/staged rows with reasons), `--promote [--ids ...]`, `--reject --ids ... --reason ...`, `--drain-held` (interactive approve/reject). This is the C5 review surface for HITL-held rows | ~30K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — X3 gate: in deferred mode, promotion (wired into the post-run seam in `apps_rg/__main__` after X3 disposition) only promotes rows whose `run_id` produced `X3_ALLOW`; rows from blocked runs are held with `reason=run_not_x3_allow`. Inline mode unchanged (documented as legacy) | ~25K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.4** — FUSE/ENRICH fork: stage post-fusion atoms (evidence-contract enrichments / fused canonical facts) with `write_back_operation=fuse|enrich` from the C0.4/C0.5 path — today only C0.2 EXTRACT-shaped atoms ever reach staging; contract test pins GENERATED → semantic cache only (G11) | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Deferred mode: zero live-collection writes during section execution; promotion fires once post-run; receipt references run_id + X3 code.
- Drain CLI smoke: `--list` and `--promote` exit 0 against a seeded staging collection.
- Contract test proves a `generated` atom cannot reach `fact_vectors` in either mode.

---

## Wave 4 — Generic Core Engine (agentic_core) + App Profile Config

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization**: REQUIRED — `agentic_core` addition. Fire native `AskUserQuestion` at wave start (decision class `architecture_choice`): **(A, recommended)** extract generic engine to `agentic_core/L4_state/fact_writeback/` (mechanics: staging, tiering, dedupe, score, promotion, receipts — zero app literals) with apps supplying meaning via a `writeback` profile block; **(B)** keep engine app-side, add only a core abstract contract; **(C)** status quo + contract tests. CoreAdditionAuthorGateReceipt (verdict=PASS) + migration receipt at `artifacts/governance/migration_receipts/` MUST exist before any `agentic_core` edit; update `author_gate_receipt_ref` frontmatter.

**Phases**:
- **W4.1** — Author-Gate decision + receipts (blocking precondition for W4.2/W4.3) | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Generic engine: `agentic_core/L4_state/fact_writeback/{engine.py,contracts.py}` — `FactWritebackEngine(profile)` with `stage()`, `promote()`, `drain()`; profile dataclass (collection names, forbidden source types, score floor, HITL mode, dedupe policy) resolved from app domain contract; add `writeback:` block to apps_rg profile ([section_retrieval_profile.yaml](apps_rg/config/domain_contract/section_retrieval_profile.yaml) or sibling `fact_writeback_profile.yaml`) + U0 package ref | ~70K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Rewire apps_rg: `fact_vector_write_back.py` / `c02_fact_vector_ingest.py` become thin bindings delegating to the core engine (public API preserved); unit tests for generic engine in `tests/unit/agentic_core/L4_state/`; contract tests in `tests/_apps_contract/test_apps_rg_fact_writeback_contract.py`; run `/core-boundary-audit` | ~40K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `agentic_core/L4_state/fact_writeback/` contains no `apps_rg`/`apps_*` literals (boundary audit ALLOW/ALLOW_WITH_GENERIC_REFACTOR + receipt on disk).
- apps_rg behavior unchanged under both promotion modes (existing W1–W3 tests still green).
- A second hypothetical app can configure the engine purely via profile (demonstrated in unit test with a synthetic profile).

---

## Wave 5 — Governance Visibility: UWG Witness, ADG Coverage, CI Gates

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — UWG-visible writes: promotion emits a durable mutation witness — ledger event via `tools.ledgers.hook_helpers.emit_ledger_event` (`L4/uwg` router family, `ROUTER_DECISION:` pairing per constitutional §29) carrying `promotion_receipt` digest + counts; document whether full UWG MutationRecord routing is adopted or receipt-witness suffices (decision recorded in plan body at execution) | ~25K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Detector coverage + G9 fix: route `upsert_fact_vector_chunks` Chroma access through the sanctioned `chroma_client` adapter (remove raw `import chromadb`); extend ADG infra-import detection so raw `chromadb` imports under `apps_*` surface in `v_p0_apps_direct_infra`, and chroma upserts outside the L4 adapter surface in `v_p0_write_bypass_uwg`; regen ADG and verify rows appear/clear as expected | ~25K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** — CI gates: `ops_scripts/ci/check_fact_vectors_lane_parity.py` (dense count vs FTS5 doc count for `fact_vectors`, advisory→strict env flip) and `ops_scripts/ci/check_fact_vectors_schema_conformance.py` (sampled live rows validate against schema yaml v2.1, incl. `tier`); register in `run_contract_gates.py` | ~20K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Promotion produces a ledger event + receipt pair (verified in E2E run artifact).
- Post-regen ADG: raw-SDK import P-view row appears on an injected violation fixture and clears on the fixed code.
- Both CI gates registered and green on main.

---

## Execution Details

### W1.3 — Backfill commands
```bash
# Dry-run, then execute against the canonical store
python ops_scripts/maintenance/backfill_fact_vectors_tier.py --dry-run
python ops_scripts/maintenance/backfill_fact_vectors_tier.py --execute
# Receipt: artifacts/apps_rg/fact_vectors_tier_backfill_receipt.json (untagged_after MUST be 0)
```

### W2.3 — Sparse parity proof
```bash
python tools/apps_rg/bootstrap_fact_vectors.py            # ensure dense+sparse ready
pytest tests/unit/apps_rg/runtime/c0/test_fact_vector_promotion.py -q
python ops_scripts/ci/check_fact_vectors_lane_parity.py    # (after W5.3; until then assert via receipt fields)
```

### W3.2 — Drain CLI smoke
```bash
python tools/apps_rg/promote_fact_vectors.py --list
python tools/apps_rg/promote_fact_vectors.py --promote
APPS_RG_FACT_VECTOR_PROMOTION_HITL=1 python tools/apps_rg/promote_fact_vectors.py --drain-held
```

### W4.3 — Boundary audit
```bash
# After rewiring: classify core files, scan literals, write boundary receipt
# (workflow /core-boundary-audit) then:
pytest tests/unit/agentic_core/L4_state/test_fact_writeback_engine.py tests/_apps_contract/test_apps_rg_fact_writeback_contract.py -q
```

### End-to-end smoke (DoD-2)
```bash
# Seeded store, deferred mode, one golden section; expects exit 0 + promotion receipt in run dir
APPS_RG_FACT_VECTOR_PROMOTION_MODE=deferred python -m apps_rg --section competencies <required inputs per wizard>
python tools/apps_rg/render_run_summary.py
```

---

## Definition of Done

DoD-1: Two-tier model live — every `fact_vectors` row carries `tier` (`seed`|`learned`); promotion stamps `learned` + provenance.
- Evidence: backfill receipt `untagged_after=0`; unit test asserts both stamping paths.
- Status: TODO

DoD-2: Smoke run — deferred-mode end-to-end section run exits 0 and emits `fact_vector_promotion_receipt.json` referencing `run_id` + X3 code.
- Evidence: `python -m apps_rg --section competencies ...` exit 0; receipt in `artifacts/apps_rg/runs/<id>/`.
- Status: TODO

DoD-3: Lane parity preserved across promotion — dense and FTS5 sparse counts equal after promote; parity gate green.
- Evidence: `python ops_scripts/ci/check_fact_vectors_lane_parity.py` exit 0; receipt fields `dense_count == sparse_doc_count`.
- Status: TODO

DoD-4: HITL surface real — held rows are listable and drainable; X3-blocked runs never promote.
- Evidence: drain CLI smoke exits 0; contract test `run_not_x3_allow` hold path passes.
- Status: TODO

DoD-5: Core/app boundary clean — generic engine in `agentic_core` with zero app literals; receipts on disk.
- Evidence: `/core-boundary-audit` outcome ALLOW*; CoreAdditionAuthorGateReceipt + migration receipt paths recorded in frontmatter.
- Status: TODO

DoD-6: Tests + gates — scoped suites green, zero regressions; new CI gates registered.
- Evidence: `pytest tests/unit/apps_rg/runtime/c0/ tests/unit/agentic_core/L4_state/ tests/_apps_contract/test_apps_rg_fact_writeback_contract.py -q` all pass; `python ops_scripts/ci/run_contract_gates.py` exit 0.
- Status: TODO

DoD-7: Governance witness — promotion emits paired ledger event + receipt; ADG detector coverage proven post-regen.
- Evidence: ledger row in `artifacts/ledgers/router_l4_uwg.sqlite`; P-view rows appear/clear on fixture.
- Status: TODO

### Verification vs Deferral

| Item | Verify in this plan | Deferred (where) |
|---|---|---|
| Tier stamping + backfill | ✅ W1 | — |
| Digest dedupe + score floor | ✅ W2 | Embedding-cosine near-dup → follow-up plan |
| Sparse sidecar sync + parity | ✅ W2/W5.3 | — |
| X3-gated deferred promotion | ✅ W3 | — |
| HITL drain CLI | ✅ W3.2 | Graphical review UI → deferred |
| Generic core engine | ✅ W4 (Author-Gate) | apps_qna/apps_lic adoption → per-app plans |
| UWG witness | ✅ W5.1 (ledger event + receipt) | Full UWG MutationRecord routing if Author-Gate selects it |
| L6 learning loop (usage/eviction/confidence) | ❌ | Dedicated follow-up plan (consumes W5 receipts) |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=c0-grounded-fact-writeback-spine-4f8e2a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=c0-grounded-fact-writeback-spine-4f8e2a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=c0-grounded-fact-writeback-spine-4f8e2a reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

> **Documentation ≠ Authorization.** Retroactive plan updates are not governance.

---

## Supersedes

> This plan **extends** (does not supersede) `apps-rg-fact-vector-writeback-discipline-67652c`
> (Completed 2026-06-08) — that plan built the classifier/staging/promotion seam this plan
> hardens and generalizes.

| Predecessor slug | Reason |
|---|---|

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=c0-grounded-fact-writeback-spine-4f8e2a wave=<N>
WAVE_COMPLETE: plan=c0-grounded-fact-writeback-spine-4f8e2a wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=c0-grounded-fact-writeback-spine-4f8e2a phase=<W1.1>
PLAN_COMPLETE: plan=c0-grounded-fact-writeback-spine-4f8e2a note="<final outcome>"
```
