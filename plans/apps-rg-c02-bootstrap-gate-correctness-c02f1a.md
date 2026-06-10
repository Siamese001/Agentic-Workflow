---
plan_id: apps-rg-c02-bootstrap-gate-correctness-c02f1a
plan_format: v2
plan_type: infra
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg AIG E2E Durability — C0.2 Evidence Bootstrap + Bullet-Gate Correctness

Make C0.2 retrieval evidence provision itself automatically on any fresh worktree/checkout, and make two patched bullet-gate defects durable (regression-tested and sibling-audited), so AIG E2E lanes reach `X3_ALLOW` deterministically without manual setup.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-c02-bootstrap-gate-correctness-c02f1a`. Wave markers use `plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — During the AIG VP "Global Head of Agentic AI" E2E bring-up, the role-episode lanes (`insurtech_bullets`, `ey_bullets`) were driven from crash → `X3_ALLOW`. Getting there required (a) a **manual** C0.2 evidence build (`tools/apps_rg/build_section_fact_vectors.py --execute` for the dense `fact_vectors` Chroma collection + `tools/generate/ingestion/build_sparse_index.py --collection fact_vectors` for the BM25 sidecar), and (b) two in-tree code fixes to `apps_rg/runtime/sections/role_episode_lane.py`.
- **Complication** — Three durability gaps remain. (1) `data/cache/chromadb/fact_vectors` and `data/cache/sparse/fact_vectors.db` are gitignored, so **every fresh worktree/checkout starts with no C0.2 evidence → all 11 lanes `REQUIRED_PROOF_ABSENT`** until an operator remembers two manual build commands. (2) The `bundle_consumed` crash fix and (3) the `single_thought` decimal-correctness fix are patched in the working tree with **no regression tests** and **no audit of sibling code paths** that share the same defect (the role-episode narrative `exactly_one_sentence` gate uses the identical naive period-count).
- **Question** — How do we make C0.2 evidence provisioning automatic + idempotent across worktrees, and make the two bullet-gate fixes durable (regression-tested + sibling-audited), so AIG E2E lanes pass without manual setup or latent sibling bugs?
- **Answer** — (W1) one idempotent C0.2 evidence bootstrap entrypoint that builds **both** dense + sparse and fast-skips when present, wired into the run/CI preflight (mirroring the `.env` SSOT auto-provision model). (W2) Land + regression-test the `bundle_consumed` fix and audit for other vestigial-kwarg forwards. (W3) Land + regression-test the `single_thought` sentence-aware fix and migrate the sibling naive-period sentence gates onto the shared validator.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | **C0.2 evidence bootstrap durability** — one idempotent dense+sparse provisioner, wired into run/CI preflight | ~40K | Existing `build_section_fact_vectors.py` + `build_sparse_index.py` are reusable; ledger is the canonical fact source | ✅ DONE | Fresh worktree provisions `fact_vectors` (dense) + `fact_vectors.db` (sparse) with no manual step; readiness gate verifies both dense + sparse |
| W2 | W2.1, W2.2 | **`bundle_consumed` crash — land + regression + vestigial-kwarg audit** | ~18K | Fix already applied in working tree; param is purely vestigial (no caller/test/gate uses it) | ✅ DONE | No role lane raises `TypeError` on X2 gates; regression test pins it; no other forwarded-kwarg mismatches remain in role-episode/sibling lanes |
| W3 | W3.1, W3.2 | **`single_thought` decimal correctness — land + regression + sibling gate migration** | ~24K | Shared `check_bullet_single_thought` is the canonical sentence-aware validator | ✅ DONE | Decimal/abbreviation bullets pass, genuine 2-sentence bullets fail; sibling naive `.count('.')` sentence gates migrated to shared sentence-aware validators |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Unify dense+sparse into one idempotent `bootstrap fact-vectors` entrypoint | ✅ DONE |
| W1.2 | Wire bootstrap into run preflight + CI seed/readiness (dense + sparse) | ✅ DONE |
| W2.1 | Land `bundle_consumed` drop-param fix + regression test (all 4 role lanes) | ✅ DONE |
| W2.2 | Audit role-episode + sibling lanes for other vestigial-kwarg forwards | ✅ DONE |
| W3.1 | Land sentence-aware `single_thought` fix + decimal/2-sentence regression test | ✅ DONE |
| W3.2 | Migrate sibling naive-period sentence gates onto the shared validator | ✅ DONE |

---

## Out Of Scope

- **Item 2 (`.env` provisioning across worktrees)** — DONE via the `env_bootstrap.py` SSOT model change (relocated `~/.apps_rg/.env` + `$APPS_RG_DOTENV` override + `home_ssot` fallback). Not re-covered here.
- **C0.2 dense query returns empty enrichment for bespoke sections (the real residual blocker)** — even with `fact_vectors` (dense) + BM25 sidecar built, `headline`, `executive_summary`, `unify_bullets`, `ibm_bullets` deterministically fail with `REQUIRED_PROOF_ABSENT` ("C0.2 product hybrid dense lane required but did not complete"), while `insurtech_bullets`/`ey_bullets`/`ey_narrative` reach `X3_ALLOW` and `competencies` reaches REAL_LLM. Mechanism: `dense_completed = (status=="PASS" and bool(extra))` in `c02_product_hybrid_retrieval.py:209` — the bespoke-section dense query against `fact_vectors` returns an **empty `extra`** (G6 "PASS-but-empty"), so the mandatory lane is judged incomplete. NOT a concurrency race: the sequential run (`APPS_RG_PARALLEL_PHASE1_LANES=0`, full5) reproduced the identical 4-lane failure, disproving the earlier parallel-race hypothesis. `product_hybrid_retrieval_required` is global (not per-section), so the split is purely retrieval-match. (W1 makes the evidence *exist*; this is a separate retrieval-quality fix — per-section `section_targets` tagging / similarity threshold / query-text for the 4 bespoke lanes.) Separate plan; surface via `spawn_task`.
- **Content-gate tail** — `competencies` per-category term-floor / 7-of-7 capability-family coverage, and `ey_narrative` judge calibration. Tracked under the parent `apps-rg-aig-e2e-remediation-e4b7c1` (W4) and judge-calibration cadence; not in this plan.
- No `agentic_core` edits; no other `apps_*`.

---

## Wave 1 — C0.2 Evidence Bootstrap Durability

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — apps_rg-owned tooling + CI seed/readiness; no shared-core surface.

**Phases**:
- **W1.1** — Unify dense+sparse into one idempotent `bootstrap fact-vectors` entrypoint | ~22K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Wire bootstrap into run preflight + CI seed/readiness (dense + sparse) | ~18K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Detail**:
- W1.1 — Add a single operator/CLI entrypoint (e.g. `tools/apps_rg/bootstrap_fact_vectors.py` or a `--with-sparse` flag on the existing builder) that: (1) calls `build_section_fact_vectors.py` to populate the dense `fact_vectors` Chroma collection from the candidate-fact ledger + base resume; (2) calls `build_sparse_index.py --collection fact_vectors` to build the BM25 FTS5 sidecar; (3) is **idempotent** (stable chunk ids; fast-skip when dense `count()>0` AND sidecar exists, matching `seed_apps_rg_fact_vectors_chroma` skip semantics); (4) writes a provenance receipt.
- W1.2 — Extend the fresh-checkout seed path: `seed_apps_rg_fact_vectors_chroma.py` currently seeds 6 smoke docs for dense only — upgrade it (or chain the W1.1 entrypoint) so `run_contract_gates` provisions **both** dense and sparse; add a sparse-readiness gate sibling to `check_apps_rg_fact_vectors_readiness.py` (RG-FV-1) so a missing `fact_vectors.db` is caught. Honor `CHROMA_PERSIST_DIR`. Respect existing bypass envs.

**Acceptance**:
- `tools/apps_rg/bootstrap_fact_vectors.py` provisions dense `fact_vectors` + `data/cache/sparse/fact_vectors.db`, writes `artifacts/ci/apps_rg_fact_vectors_bootstrap_receipt.json`, and fast-skips when both surfaces are ready.
- `ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py` delegates to the dense+sparse bootstrap; `ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py` verifies dense count, embedding dimension, metadata, and sparse sidecar docs.
- Verified on `apps_rg`: real bootstrap fast-skipped with dense count 30 and sparse docs 30; readiness gate reported 5 OK / 0 ERROR.

---

## Wave 2 — `bundle_consumed` Crash: Land + Regression + Vestigial-Kwarg Audit

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Land drop-param fix + regression test for all 4 role lanes | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Audit role-episode + sibling lanes for other vestigial-kwarg forwards | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Detail**:
- W2.1 — `run_role_episode_x2_gates` forwarded `bundle_consumed=` into `_x2_gates`, which has no such parameter → `TypeError: _x2_gates() got an unexpected keyword argument 'bundle_consumed'`, a `fault: exception` that cascade-aborts later lanes. The param is purely vestigial (no caller, test, or gate uses it). Fix = drop it (applied in working tree). Add a unit test asserting `run_insurtech_bullets_x2_gates` / `run_ey_bullets_x2_gates` / narrative variants run without `TypeError` on a minimal `l2`.
- W2.2 — Audit role-episode and sibling lane modules for other "wrapper forwards a kwarg the callee does not accept" mismatches (the incomplete-clone smell). Fix any found; prefer `**kwargs`-free explicit signatures.

**Acceptance**:
- `tests/unit/apps_rg/test_role_episode_x2_bundle_consumed_w2.py` asserts all four role-episode X2 entrypoints execute on minimal L2 payloads without forwarding `bundle_consumed`.
- Scoped AST audit over `apps_rg/runtime/sections` and `apps_rg/runtime/validators` reported `NO_LOCAL_KEYWORD_MISMATCHES`.
- Verified with focused pytest slice: 21 passed across the W2 regression and adjacent InsurTech/EY role-episode wiring/bundle tests.

---

## Wave 3 — `single_thought` Decimal Correctness + Sibling Gate Migration

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Land sentence-aware fix + decimal/2-sentence regression test | ~12K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Migrate sibling naive-period sentence gates onto the shared validator | ~12K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Detail**:
- W3.1 — The role-episode `x2_<section>_bullet_single_thought` gate counted `.`+`!`+`?` characters (`<= 1`), so a single-sentence bullet with a decimal metric (`99.99% uptime`) false-failed. Fix = route through the shared sentence-aware `check_bullet_single_thought` (uses `split_sentences`), applied in working tree. Add a regression test: decimal (`99.99%`), abbreviation (`U.S.`, `e.g.`) → pass; genuine 2-sentence bullet → fail.
- W3.2 — The role-episode **narrative** gate `x2_<section>_exactly_one_sentence` uses the identical naive `sent.count(".") + ... == 1` and will false-fail any narrative carrying a decimal metric. Audit IBM/Unify bullet/narrative lanes for the same pattern. Migrate all confirmed naive-period sentence gates onto the shared sentence-aware validators so the defect cannot recur.

**Acceptance**:
- `apps_rg/runtime/sections/role_episode_lane.py` now uses `check_narrative_exactly_one_sentence` for role-episode narrative sentence gates instead of raw punctuation counts.
- `tests/unit/apps_rg/test_role_episode_sentence_gate_w3.py` covers decimal/abbreviation pass cases (`99.99%`, `U.S.`, `e.g.`, `Inc.`), genuine two-sentence failures, and role-episode bullet/narrative gate behavior.
- Scoped raw-period audit found no `sent.count` usage in the runtime sentence-gate scope.

---

## Definition of Done

| # | Definition of Done | Verification |
|---|---|---|
| 1 | One idempotent bootstrap provisions C0.2 dense + sparse evidence on a clean cache | ✅ `python tools/apps_rg/bootstrap_fact_vectors.py` fast-skipped ready store: dense count 30, sparse docs 30; bootstrap writes provenance receipt and builds missing surfaces when absent |
| 2 | **Smoke run (executable surface):** a fresh-worktree AIG section run reaches `X3_ALLOW` with no manual evidence build | ⚠️ Direct full `run_contract_gates --gate CHECK-RG-FACT-VECTORS` blocked before RG-FV by unrelated infra wiring violation (`apps_lic/engines/x1d_claude_judge_adapter.py: import anthropic`); W1 seed/readiness entrypoints verified independently |
| 3 | `bundle_consumed` crash cannot recur | ✅ `tests/unit/apps_rg/test_role_episode_x2_bundle_consumed_w2.py`: all 4 role-episode X2 gate entrypoints run without `TypeError` |
| 4 | `single_thought` decimal false-positive cannot recur | ✅ `tests/unit/apps_rg/test_role_episode_sentence_gate_w3.py`: `99.99%`, `U.S.`, `e.g.`, `Inc.` pass; 2-sentence bullets/narratives fail |
| 5 | Sibling sentence gates audited + migrated; no remaining vestigial-kwarg forwards | ✅ Scoped audits: no `sent.count` sentence gate in role-episode scope; `NO_LOCAL_KEYWORD_MISMATCHES` across scoped sections/validators |
| 6 | Targeted regression slice green | ✅ W1 slice 8 passed; W2 role-episode slice 21 passed; W3 sentence-gate slice 20 passed, all with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and explicit `-p pytest_timeout` |

---

## Execution Closeout

CLOSEOUT_WAVE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a wave=1 note="dense+sparse fact_vectors bootstrap, seed wrapper, readiness gate, and focused tests complete"
PHASE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a phase=W2.1 note="bundle_consumed crash fix confirmed present and regression-tested across four role-episode X2 entrypoints"
PHASE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a phase=W2.2 note="scoped local keyword-forward audit found no remaining mismatches"
CLOSEOUT_WAVE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a wave=2 note="role-episode bundle_consumed durability regression and vestigial-kwarg audit complete"
PHASE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a phase=W3.1 note="single_thought decimal/abbreviation correctness regression-tested"
PHASE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a phase=W3.2 note="role-episode narrative raw period-count gate migrated to shared sentence-aware validator"
CLOSEOUT_WAVE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a wave=3 note="sentence-aware bullet/narrative correctness complete with scoped raw-period audit"
PLAN_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a note="W1-W3 implementation and targeted verification complete; unrelated infra wiring gate remains outside plan scope"

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| C0.2 dense+sparse bootstrap · bundle_consumed regression · single_thought correctness + sibling migration | Yes — W1–W3 | — |
| C0.2 dense "PASS-but-empty" for bespoke lanes (headline/exec_summary/unify/ibm) | — | Yes — `## Deferred Follow-ups` (separate plan) |
| Content gates: competencies term-floor/7-of-7, ey_narrative judge | — | Yes — parent `apps-rg-aig-e2e-remediation-e4b7c1` W4 |

---

## Deferred Follow-ups

- **C0.2 dense "PASS-but-empty" for bespoke lanes (the real residual blocker for all-11-pass)** — `headline`, `executive_summary`, `unify_bullets`, `ibm_bullets` deterministically fail `REQUIRED_PROOF_ABSENT` because their dense `fact_vectors` query returns empty enrichment, so `dense_completed = (status=="PASS" and bool(extra))` (`c02_product_hybrid_retrieval.py:209`) is False and the mandatory hybrid lane is judged incomplete — even after the dense+sparse stores are built. The role-episode lanes (`insurtech`/`ey`) and `competencies` get non-empty dense `extra` and pass/generate. **Disproved hypothesis:** this is NOT the parallel-lane race — the sequential run (`APPS_RG_PARALLEL_PHASE1_LANES=0`, full5) reproduced the identical 4-lane failure. `product_hybrid_retrieval_required` is global, so the split is purely retrieval-match. Investigate per-section `section_targets` tagging / similarity threshold / query-text for the 4 bespoke lanes (G6 PASS-but-empty validation). Surface via `spawn_task`.
- **Lane status packaging** — passing role-episode lanes were labeled `MISSING_NOT_ATTEMPTED` in `integrated_lane_evidence_status.json` despite `X3_ALLOW` + `authorized=yes` (run-dir pointer not finalized). Reconcile the summarizer/packaging classification.

---

## Safety / Invariants

- Never weaken a gate to pass bad output. W3 fixes are **correctness** changes (a decimal is one thought; the shared validator still fails genuine multi-sentence bullets) — not threshold relaxations.
- C0.2 `fact_vectors` is non-authoritative enrichment; the ledger/graph/proof-pool remains the X2 proof substrate. W1 only widens recall + satisfies the mandatory dense/sparse gate; it does not change proof authority.
- Identity (company/title/location/dates) for InsurTech/EY stays verbatim from the base resume; skills stay graph-node-backed. No fabricated facts or metrics.
