---
plan_id: apps-rg-aig-remaining-lanes-closeout-d4e1f7
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg AIG E2E — Close the Remaining Lanes to X3_ALLOW

Drive the AIG VP "Global Head of Agentic AI" run from 3/11 lanes authorized to **all 11 at `X3_ALLOW`** by fixing three independent residual blockers: C0.2 dense "PASS-but-empty" for the bespoke lanes, the competencies graph-term content gate, and the lane-status packaging mislabel that cascade-blocks narratives.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-aig-remaining-lanes-closeout-d4e1f7`. Wave markers use `plan=apps-rg-aig-remaining-lanes-closeout-d4e1f7`.

> **Relationship**: this plan promotes the `## Deferred Follow-ups` items of `apps-rg-c02-bootstrap-gate-correctness-c02f1a` (C0.2 dense PASS-but-empty; lane-status packaging) into executable scope, and picks up the live content tail deferred from `apps-rg-aig-e2e-remediation-e4b7c1` W4 (competencies). It assumes the four landed fixes (C0.2 evidence built; `.env` SSOT; `bundle_consumed`; `single_thought`) are in place.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS — 8/11 X3_ALLOW live; all deterministic defects fixed+proven; residual = stochastic/judge content tail
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-10

> **W4 closeout runs (2026-06-10).** Run 1: 7/11 ALLOW, 10/11 executed. Run 2 (after the
> narrative fixes): **8/11 ALLOW** — exec_summary, competencies, unify_bullets, unify_narrative,
> insurtech_bullets, insurtech_narrative, ey_bullets, ey_narrative. Both narrative fixes proven
> live (off-by-one char budget + em-dash normalize; per-lane judge roster from
> section_judge_policy). **ibm_bullets passed ALL deterministic X2 gates (x2_failed=0)** —
> every code fix proven — and now blocks only on a LEGITIMATE decisive gemini_pro verdict
> (score 1.0/5 vs 4.0 floor: bullet content drifts from per-slot facts, e.g. "$10M ARR" on a
> bullet whose source fact doesn't carry it). That is the parent plan's explicitly-deferred
> "bullet content-quality dig" (unbounded scope), NOT a wiring defect. headline flapped on one
> stochastic content gate (`x2_headline_governance_or_regulated_ai_signal_required` — passed
> in full6 and closeout1). ibm_narrative remains a pure cascade behind ibm_bullets.
>
> **Residual to 11/11:** (a) IBM per-slot fact↔content grounding quality (deferred content dig —
> needs its own scoped effort: slot-fact semantic alignment in generation/selection);
> (b) headline governance-signal stochastic miss (passes most rolls; candidate for a regen
> trigger or prompt emphasis); (c) ibm_narrative cascade (clears with (a)).

> **W1 DONE (2026-06-09).** Root cause was `metadata_filter_profile.yaml` hard-`$eq`-filtering candidate
> `fact_vectors` by the TARGET company/role (`company == "AIG"`) — candidate facts never match, so dense
> returned 0 hits → `REQUIRED_PROOF_ABSENT`. Removed `company`/`role` from the hard `where` filter (soft
> `metadata_score` only, per the file's `score_separation` contract). **Result: every lane now generates
> REAL_LLM** (zero `REQUIRED_PROOF_ABSENT`); authoritative `integrated_lane_evidence_status.json` =
> 8 executed / 3 not-run; **4 lanes at X3_ALLOW** (headline, insurtech_bullets, ey_bullets, ey_narrative).
>
> **Post-W1 corrections to remaining waves:**
> - **W3 is mostly a SUMMARIZER display bug, not a packaging failure.** The authoritative status already
>   classifies the 4 X3_ALLOW lanes as executed; only `tools/apps_rg/summarize_e2e_run.py` mislabels them
>   `MISSING_NOT_ATTEMPTED`. Real W3 residual = the `insurtech_narrative` cascade anomaly (its upstream
>   `insurtech_bullets` is X3_ALLOW yet the narrative shows `upstream_not_finalized`, while `ey_narrative`
>   ran fine).
> - **NEW dominant blocker (was hidden behind W1): the bespoke bullet-pool produces ZERO merged bullets**
>   for `unify_bullets`/`ibm_bullets` (`selection_gate.slots_missing` = all 6, `bullets_in_merged: 0`,
>   `selector_subthreshold_scores: []` — NOT the 0.72 threshold; 7 paths executed, 0 merged). This is a
>   generation/merge defect in `employment_bullet_pool`, distinct from the parent plan's "< 0.72" item.
>   It blocks 4 lanes (unify/ibm bullets + their narratives) and is the real gate to 11/11. Captured below.
> - **W2 NOT auto-resolved by W1** — competencies still fails `x2_competencies_generic_category_blocked_without_graph` + gemini judge.

---

## Context (SCQA)

- **Situation** — After the C0.2 evidence build + four fixes, the live AIG E2E reaches `X3_ALLOW` on `insurtech_bullets`, `ey_bullets`, `ey_narrative` (3/11). `competencies` generates REAL_LLM but content-fails. The remaining seven lanes do not authorize.
- **Complication** — Three independent, now-characterized blockers stand between 3/11 and 11/11:
  1. **C0.2 dense "PASS-but-empty"** — `headline`, `executive_summary`, `unify_bullets`, `ibm_bullets` deterministically fail `REQUIRED_PROOF_ABSENT`. Mechanism: `dense_completed = (status=="PASS" and bool(extra))` (`c02_product_hybrid_retrieval.py:209`); the bespoke-section dense query against the populated `fact_vectors` returns an **empty `extra`**, so the mandatory hybrid lane is judged incomplete. Reproduced identically under sequential execution (`APPS_RG_PARALLEL_PHASE1_LANES=0`), ruling out a concurrency race; `product_hybrid_retrieval_required` is global, so the split is purely per-section retrieval-match.
  2. **competencies content gate** — fails `x2_competencies_generic_category_blocked_without_graph` (generic categories lacking ≥ the required graph-backed terms) + an X1D `gemini_pro` judge fail. This is the live term-floor / capability-family-coverage tail deferred from `apps-rg-aig-e2e-remediation-e4b7c1` W4.
  3. **Lane-status packaging** — passing `insurtech_bullets`/`ey_bullets` are labeled `MISSING_NOT_ATTEMPTED` in `integrated_lane_evidence_status.json` despite `X3_ALLOW` + `authorized=yes` (run-dir pointer not finalized), which makes dependent narratives read their upstream as not finalized and `PRE_RUN_BLOCKED` (`upstream_not_finalized`).
- **Question** — How do we make every required lane reach `X3_ALLOW` (or an explicitly accepted product-review state) on the live AIG run without weakening gates or fabricating proof?
- **Answer** — (W1) Diagnose and fix the bespoke-section dense PASS-but-empty so the four lanes complete C0.2 and generate (also unblocks unify/ibm narratives). (W2) Close the competencies graph-term coverage so generic categories carry ≥ the required graph-backed terms. (W3) Reconcile the run-dir-pointer/packaging so passing lanes are not mislabeled and their narratives finalize. (W4) Full AIG E2E proves all 11 authorized.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | **C0.2 dense PASS-but-empty (bespoke lanes)** — diagnose empty `extra`, fix per-section retrieval match | ~55K | `fact_vectors` is populated + section-tagged; bug is tagging/threshold/query-text, not infra | ✅ DONE | All lanes now generate REAL_LLM (target-company `$eq` filter removed from `metadata_filter_profile.yaml`); 4 lanes X3_ALLOW |
| W5 | W5.1 | **Bespoke bullet-pool produces 0 merged bullets (NEW, dominant 11/11 blocker)** — `unify_bullets`/`ibm_bullets` generate 7 paths but merge 0 bullets (slots_missing=all 6) | ~50K | Defect in `employment_bullet_pool` generation/merge, not the 0.72 threshold | ✅ DONE — **ibm_bullets live X3_ALLOW (ibm_final6: exit 0, x2_failed=0, proof_eligible, gemini 5.0/5)**. Closing fixes beyond the run-2 list: slot_fact_story X1D grading anchor injected into the evidence pack (generator was structurally blind to the plan-fact stories the judge grades — gemini flipped 0.0→5.0); phase-true IBM Positioning (career phase blends platform + pre-sales/GTM per user directive); parallel-session slot→bundle GTM realignment; clause-aware cross-slot plan-metric scrub; selector compliance extended with seniority+specificity quality floors; all-floors composition instruction. (ibm_final5 regression was a transient race with parallel-session mid-edit state — max_tokens 2200 snapshot; not a code defect) | **unify_bullets live: exit 0, x2_failed=0, `X3_ALLOW`, proof_eligible.** Six root-caused fixes: (1) token caps 2200/2400→8000 (mid-JSON truncation = the 0-merged cause); (2) leakage scan excludes the model's `self_check` attestation (false-positive on `"no_bul_ibm_references"` key); (3) selector all-paths line-discipline scan when the single Claude winner is non-compliant; (4) per-bullet `change_log` merge from each bullet's source path; (5) 320-char budget added to PRODUCT_SHAPE shape_summary (SSOT; numeric-parity gate green); (6) metric derivation via canonical `UNIFY_BULLET_SLOT_BUNDLE_MAP`, guarded by cites-own-slot so adversarial negative tests still reject. ibm_bullets spot-check running |
| W6 | W6.1 | **exec_summary judge-wiring self-contradiction (NEW, found+fixed during W2/W3 pass)** — `RELEASE_POST_X2_JUDGE_REFRESH_ENABLED=False` made `x2_x1d_required_judges_present` structurally unsatisfiable (only judge path was the disabled refresh) | ~10K | Gate stays; re-enable refresh (env opt-out retained) | ✅ DONE | Live verify: exit 0, x2_failed=0, **2 MODEL_BACKED judges both pass, `X3_ALLOW`** |
| W2 | W2.1, W2.2 | **competencies graph-term content gate** — generic-category graph-term coverage + judge | ~40K | Graph nodes exist for the required capability families; no fabricated terms | ✅ DONE | Root cause = gate conflict: `MIN_ITEMS_PER_CATEGORY=2` let the model emit exactly 2 graph-backed terms while the graph gate needs 3. Floor raised 2→3 in `competencies_rigor.py` (tightening). **Live verify: exit 0, x2_failed=0, `X3_ALLOW`** (judge concern also cleared with richer content) |
| W3 | W3.1, W3.2 | **Lane-status packaging + narrative cascade** — finalize run-dir pointer for authorized lanes | ~30K | Passing lanes already emit `X3_ALLOW`; only the pointer/classification is wrong | ✅ DONE | (a) `_normalize_bullets` now always assigns canonical `bul_<employer>_NNN` slot ids (was trusting model ids like `ins_b1` → `bullet_ids_mismatch` → narrative `upstream_not_finalized`); live verify: fresh insurtech_bullets = X3_ALLOW with canonical ids, companion gate `ACCEPTED_FINALIZED\|ok`. (b) summarizer derives `EXECUTED_<x3>` from run-dir evidence when no pre-run-failure file exists; full6 re-summarized = `EXECUTED_X3_ALLOW: 4`. 175 role_episode + 7 summarizer tests green |
| W4 | W4.1 | **Full AIG E2E all-11 verification + root X3 reconcile** | ~25K | W1–W3 landed | 🔄 **final11: 11/11 EXECUTED, zero missing (program first); 9/11 authorized** (8 X3_ALLOW + ibm_bullets accepted-review `X3_REVIEW_JUDGE_SOFT_FAIL` gemini 3.5 vs 4.0 — scored 5.0 the two prior rolls; zero X2 fails). ibm_narrative executed for the FIRST time (soft-fail review correctly un-cascaded downstream per dec_19e6e344d5db19589). Residual to 11/11-authorized: ① ibm_narrative first-run wiring (change_log bundle-id echo + theme coverage 004 — same derivation classes already fixed for bullets); ② unify_narrative `x2_no_companion_ngram_copy` stochastic flap (passed closeout2; echoed a 4-gram from its companion bullets) | All 11 lanes authorized (`X3_ALLOW` or accepted review); `integrated_lane_evidence_status.json` zero missing lanes; exit code matches disposition. IBM additional fixes landed before this run: anchor-gate plan-shape adaptation (slot-keyed plans reach the no-metric escape — kills the 30%/25%/$15M anchor↔HOLD contradiction); plan-seam HOLD demotion (ledger assigned bul_ibm_002 "30% cost optimization"); `inject_ibm_locked_metric_anchors` now injects metrics as an IN-SENTENCE clause with char-cap fallback (the injector itself was appending the 2-sentence "Delivered X at enterprise scale." tail that deterministically failed single_thought/paragraph_block — including the historical "velocity Delivered outcomes" mangle); sentence-aware HOLD demote backstop; PA METRIC SURFACING rewritten promotable-only + same-sentence |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Trace empty dense `extra` for the 4 bespoke sections (tagging vs threshold vs query-text) | 🔲 TODO |
| W1.2 | Fix per-section dense match; lanes complete C0.2 + generate | 🔲 TODO |
| W2.1 | Inject ≥ required graph-backed terms per generic competency category | 🔲 TODO |
| W2.2 | Reconcile competencies X1D judge (gemini_pro) content/rubric | 🔲 TODO |
| W3.1 | Finalize run-dir pointer so authorized lanes are classified EXECUTED | 🔲 TODO |
| W3.2 | Verify narrative upstream-finalized check passes for authorized bullets | 🔲 TODO |
| W4.1 | Full AIG E2E + summarizer; all 11 authorized | 🔲 TODO |

---

## Out Of Scope

- The four already-landed fixes (C0.2 evidence build, `.env` SSOT, `bundle_consumed`, `single_thought`) — owned by `apps-rg-c02-bootstrap-gate-correctness-c02f1a`; verify-only here.
- Making C0.2 evidence provisioning automatic/idempotent for fresh worktrees — that is `c02f1a` W1; this plan assumes the stores exist.
- `agentic_core` edits; other `apps_*`.
- Lowering any deterministic gate or fabricating proof/metrics to reach `X3_ALLOW`.

---

## Wave 1 — C0.2 Dense PASS-but-Empty (Bespoke Lanes)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — apps_rg C0.2 retrieval path; no shared-core surface.

**Phases**:
- **W1.1** — Trace empty dense `extra` for the 4 bespoke sections | ~30K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Fix per-section dense match; lanes complete C0.2 + generate | ~25K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W1.1 — Instrument `_perform_bounded_section_retrieval` / `perform_product_hybrid_retrieval` for `headline`, `executive_summary`, `unify_bullets`, `ibm_bullets`: capture the dense query text, the BGE query embedding, the `section_targets` metadata filter applied, the raw Chroma hit count, and any similarity-threshold cutoff. Compare against a passing lane (`insurtech_bullets`, `competencies`) to isolate which differs. Candidate root causes (rank by evidence): (a) `section_targets` tag mismatch — the build tagged chunks for these sections but the query filters on a different value; (b) similarity threshold too high for the bespoke-section query vs its chunks; (c) query-text/embedding for these sections retrieves nothing relevant.
- W1.2 — Apply the minimal correct fix for the identified cause (align the `section_targets` filter to the build tags, and/or calibrate the dense floor, and/or fix the per-section query text). Re-validate each of the 4 lanes standalone reaches REAL_LLM. Do **not** relax the mandatory-hybrid policy or mark empty as complete — fix the *match*, not the gate.

**Acceptance**:
- Each of the 4 bespoke lanes completes the C0.2 dense lane (`dense_completed=True`) and reaches REAL_LLM on a standalone AIG section run.
- `unify_narrative` / `ibm_narrative` are no longer `upstream_not_finalized` once their bullets generate.

---

## Wave 2 — competencies Graph-Term Content Gate

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Inject ≥ required graph-backed terms per generic competency category | ~24K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Reconcile competencies X1D judge (gemini_pro) | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W2.1 — `x2_competencies_generic_category_blocked_without_graph` fails when a generic category carries fewer than the required graph-backed terms. Ensure `augment_bound_category_family_terms` injects ≥ the threshold graph-node-backed terms per generic category and covers the required capability families (the live term-floor / 7-of-7 tail deferred from `apps-rg-aig-e2e-remediation-e4b7c1` W4). Terms must trace to real `augmented_skills_graph` nodes — no fabrication.
- W2.2 — Inspect the `gemini_pro` X1D verdict for competencies; if it is a genuine content/rubric issue, address the content; if a calibration/transport issue, route per judge-calibration cadence (do not mock).

**Acceptance**:
- competencies has zero X2 failures (`x2_competencies_generic_category_blocked_without_graph` passes); every category carries lineage.
- competencies reaches `X3_ALLOW`, or an explicitly accepted product-review state with one named blocker.

---

## Wave 3 — Lane-Status Packaging + Narrative Cascade

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Finalize run-dir pointer so authorized lanes classify EXECUTED | ~18K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Verify narrative upstream-finalized check passes for authorized bullets | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W3.1 — `insurtech_bullets`/`ey_bullets` emit `X3_ALLOW` + `authorized=yes` yet are bucketed `MISSING_NOT_ATTEMPTED` (no resolvable run-dir pointer at packaging time). Make the lane finalize its `latest_real_run.json` / run-dir pointer so the integrated packaging classifies it `EXECUTED`. (Sibling to the `apps-rg-aig-e2e-remediation-e4b7c1` E2E-05 three-state classification.)
- W3.2 — Confirm the narrative lanes' upstream-finalized precondition reads the authorized bullet as finalized, clearing `insurtech_narrative` `upstream_not_finalized` (ey_narrative already authorizes; unify/ibm narratives depend on W1).

**Acceptance**:
- No lane with `X3_ALLOW` + `authorized=yes` is classified `MISSING_NOT_ATTEMPTED`.
- `insurtech_narrative` is no longer blocked on an already-authorized `insurtech_bullets`.

---

## Wave 4 — Full AIG E2E All-11 Verification

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Full AIG E2E + summarizer; all 11 authorized | ~25K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W4.1 — Run the full live AIG E2E; render `tools/apps_rg/summarize_e2e_run.py`; confirm all 11 lanes authorized (`X3_ALLOW` or accepted review) with zero missing lanes and a single root X3 vocabulary / matching exit code.

**Acceptance**:
- All 11 lanes authorized; `integrated_lane_evidence_status.json` reports zero missing lanes.

---

## Definition of Done

| # | Definition of Done | Verification |
|---|---|---|
| 1 | The 4 bespoke lanes complete C0.2 dense and generate REAL_LLM | standalone AIG section runs for headline/exec_summary/unify_bullets/ibm_bullets → `RUNTIME_GENERATION_STATUS: REAL_LLM` |
| 2 | competencies passes `x2_competencies_generic_category_blocked_without_graph` with graph-backed terms | competencies section run → zero X2 failures; coverage test green |
| 3 | No authorized lane is mislabeled `MISSING_NOT_ATTEMPTED`; dependent narratives finalize | `integrated_lane_evidence_status.json` classification + narrative runs |
| 4 | **Smoke run (executable surface):** full AIG E2E authorizes all 11 lanes | `python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd ... --manual-brief ... --artifact-dir artifacts/apps_rg/e2e_aig_verify/closeout` → summarizer shows 11 authorized, zero missing |
| 5 | No gate weakened, no proof fabricated | diff review: W1 fixes retrieval match (not the gate); W2 terms trace to graph nodes; W3 fixes classification only |
| 6 | Targeted regression slice green | `python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "c0 or competencies or role_episode or bullet or narrative or lane_evidence"` |

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| Dense PASS-but-empty · competencies graph-terms · packaging/cascade · full-run all-11 | Yes — W1–W4 | — |
| C0.2 evidence auto-bootstrap for fresh worktrees | — | Yes — `apps-rg-c02-bootstrap-gate-correctness-c02f1a` W1 |
| Bullet-pool selector content-quality (< 0.72 root question) | — | Yes — `apps-rg-aig-e2e-remediation-e4b7c1` Deferred Follow-ups |

---

## Safety / Invariants

- W1 fixes the dense **retrieval match** (tagging/threshold/query), never the mandatory-hybrid policy and never by marking empty as complete.
- W2 competency terms MUST trace to real `augmented_skills_graph` nodes; no fabricated capabilities.
- W3 changes only run-dir-pointer finalization / status classification — it does not change any X3 disposition.
- Model-backed judges stay model-backed (no mocks); the live external-Claude generation path is the target.
