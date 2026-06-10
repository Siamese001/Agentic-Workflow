---
plan_id: apps-rg-lane-reasoning-optimization-7c4e9b
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

# ⛔ SUPERSEDED (2026-06-10) — absorbed verbatim into [apps-rg-lane-aggregation-gap-closure-b8c3d1](apps-rg-lane-aggregation-gap-closure-b8c3d1.md)

> This plan's W1–W7 map to the master plan's W1/W3/W2/W5/W6/W9/W7 respectively, joined by the
> full per-lane gap inventory (G1–G35). Do not execute from this file. Notion row: Retired.

# apps_rg Lane Reasoning Optimization — Right-Size SC Paths, Judges, Repair Ladders & X2 Depth for the Claude Era

Recalibrate every lane's reasoning machinery (SC fan-out, selector floors, repair ladders, judge panels, X2 gate depth) from Qwen-vLLM-era compensation settings to external-Claude-era evidence, using gate-yield data instead of blanket cuts — so runs get cheaper and faster without weakening one content-law protection.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-lane-reasoning-optimization-7c4e9b`. Wave markers use `plan=apps-rg-lane-reasoning-optimization-7c4e9b`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — apps_rg's 11 generation lanes were architected when the local Qwen-vLLM 32B was the generator: flaky JSON, smaller context, higher output variance, weaker instruction-following. The machinery compensated: deep deterministic X2 suites, JSON parse-repair rungs in every lane, positional bullet-id injection ("Qwen samples often emit bullets without bullet_id" — in-code docstring), wide SC fan-outs, a 0.72 selection floor, transport-envelope stub gates, qwen-health preflight fields, and token caps sized for a 24k context. PR #256 removed Qwen entirely; `claude-sonnet-4-6` is the sole generator with model-backed cross-vendor judges.
- **Complication** — The compensation layer was never recalibrated. Empirical evidence from the live AIG E2E runs (full6 + section verifies): **Qwen-era bespoke lanes carry 59–91 X2 gates** (executive_summary 91, competencies 76, headline 71, unify_bullets 69, ibm_bullets 59) while the **Claude-era role_episode lanes carry 9 gates — and reached X3_ALLOW first**. Competencies runs **8 SC paths for a degenerate 8→8 selection** (the graph pool already emits the exact final category set) and takes ~10 minutes — the slowest lane. The 2,200/2,400 token caps (Qwen-context-sized) caused the 0-merged-bullets defect just fixed. The exec-summary in-lane shape preview disagrees with the canonical X2 word counter (final draft "failed" preview at 152 words yet passed canonical), burning repair calls against a phantom ruler. `JUDGE_REGEN_MAX_ATTEMPTS` has a code/test SSOT conflict (1 vs 3). Dead Qwen modules are still imported (`qwen_vllm_health` — deleted by PR #256, imported by `section_cli_preflight.py`, `section_model_limits.py`, 1 test). Nine of eleven lanes run a single-judge panel with no failover: any gemini outage stalls them (quorum=1).
- **Question** — How do we right-size each lane's reasoning budget (drafts, paths, repairs, judges) and X2 depth for the Claude era, evidence-first, without weakening any content-law gate or fabricating proof?
- **Answer** — (W1) Instrument first: per-gate yield audit across all archived run artifacts — which of the 59–91 gates ever fired on Claude output, parse-retry fire rates, selector score distributions vs the 0.72 floor. (W2) Recalibrate generation budgets: competencies SC 8→4 (canary-validated), bullets 4→3 with the 1-regen-round safety net retained, remaining Qwen-sized token caps audited. (W3) Harmonize repair ladders: one shared preview==canonical measurement, judge-regen SSOT conflict resolved. (W4) Judge resilience: keep 2-judge panels on headline/exec (defended: judges carry the whole quality burden there), add a configured failover judge for the nine single-judge lanes. (W5) Retire dead Qwen compensation: zero-yield Qwen-specific gates → advisory-then-removed, dead imports deleted. (W6) Full-run proof: equal-or-better lane outcomes at measurably lower cost/latency.

---

## Per-Lane Baseline (measured, 2026-06-10)

| Lane | SC paths | Selector (floor) | Repair ladders | Judges | X2 gates | Notes |
|---|---|---|---|---|---|---|
| headline | 1 | — | 3 targeted LLM rungs + 1 free deterministic pad | **2** (gemini, openai) | 71 | temp 0.55 · 900 tok |
| executive_summary | 1 | — | synth regen ≤2 (cap 3) + judge regen (SSOT conflict 1 vs 3) | **2** (gemini, openai) | 91 | temp 0.45 · 2048 tok · preview≠canonical counter |
| competencies | **8** | Claude pool top-8 **of 8** (0.72) — degenerate choice | 1 regen round | 1 (gemini) | 76 | ~10 min — slowest lane |
| unify_bullets | 4 (+1 regen round → ≤7) | Claude per-slot (0.72) + selector-as-judge | parse retry | 1 (gemini) + selector row | 69 | caps fixed 2400→8000 |
| ibm_bullets | 4 (+1 regen) | same | parse retry | 1 (gemini) + selector row | 59 | caps fixed 2200→8000 |
| unify/ibm narratives | 1 | — | parse retry | 1 (gemini) | ~30s each | companion-gated |
| insurtech/ey bullets | 4 | graph-ranked top-3 + selector parity | parse retry | 1 (gemini) + selector row | **9** | Claude-era build; passed first |
| insurtech/ey narratives | 1 | — | — | 1 (gemini) | **9** | ey_narrative X3_ALLOW |

## Identified Gaps

1. **G1 — X2 depth asymmetry (59–91 vs 9)** with zero yield data: nobody knows which Qwen-era gates still catch anything on Claude output.
2. **G2 — Degenerate competencies selection**: 8 SC paths feeding an 8-choose-8 "selection"; the variance the paths bought was Qwen-sized.
3. **G3 — Preview↔canonical drift (exec_summary)**: in-lane word counter disagrees with the X2 gate counter → repair calls chase a phantom; `accepted=False` drafts pass canonical.
4. **G4 — Selection floor 0.72 uncalibrated for Claude** selector score distributions (judge-calibration-cadence applies to the selector-as-judge too).
5. **G5 — Single-judge availability risk** on 9 lanes (quorum=1; any gemini outage/stale-calibration stalls the lane → forced HITL).
6. **G6 — JUDGE_REGEN_MAX_ATTEMPTS SSOT conflict** (repair_policy=1 vs test expectation=3; reconcile to one authority).
7. **G7 — Dead Qwen imports/surfaces**: `qwen_vllm_health` (deleted) still imported by `section_cli_preflight.py` + `section_model_limits.py` + 1 test; offline-contract Qwen stubs; vLLM transport-envelope stub gate.
8. **G8 — Remaining Qwen-sized token caps** (audit beyond the two already fixed; e.g. per-lane regen caps, narrative caps).
9. **G9 — Role-episode lanes may be UNDER-gated** (9 gates, no quality floors): the asymmetry cuts both ways — port the 2–3 proven quality floors (seniority/specificity) if yield data justifies.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | **Gate-yield + repair-fire-rate instrumentation** (evidence before cuts) | ~45K | Archived run artifacts under `artifacts/apps_rg/e2e_aig_verify/*` + runtime_proofs suffice as corpus | 🔲 TODO | Per-gate fire-count table for all 11 lanes over all archived Claude runs; parse-retry + regen fire rates; selector score histograms vs 0.72 |
| W2 | W2.1, W2.2 | **Generation budget recalibration** — competencies SC 8→4, bullets 4→3 (regen net kept), token-cap audit | ~40K | Canary AIG runs validate no quality regression | 🔲 TODO | Competencies wall-clock ≤ half of baseline (~10 min → ≤5); bullets cost −25%; all affected lanes still X3_ALLOW on canary |
| W3 | W3.1, W3.2 | **Repair-ladder harmonization** — preview==canonical counters; judge-regen SSOT | ~25K | Shared counting util importable by lane + validator | 🔲 TODO | Zero repair calls triggered by counter drift; one authority for judge-regen attempts, test+code agree |
| W4 | W4.1 | **Judge resilience** — failover judge config for the 9 single-judge lanes; keep 2-judge panels on headline/exec | ~20K | openai_chatgpt acceptable failover; calibration ledger covers it | 🔲 TODO | Simulated gemini outage: lanes complete via failover instead of stalling; no always-on cost increase |
| W5 | W5.1, W5.2 | **Qwen-compensation retirement** — zero-yield gates → advisory → removed; dead imports deleted | ~35K | W1 yield table is authority; content-law gates exempt | 🔲 TODO | Dead `qwen_vllm_health` importers fixed; each retired gate has a yield-table citation; zero content-law gates touched |
| W6 | W6.1 | **Full-run proof** — AIG E2E before/after comparison | ~20K | W1–W5 landed | 🔲 TODO | Lane outcomes equal-or-better vs baseline matrix; total provider calls and wall-clock measurably reduced; receipts archived |
| W7 | W7.1–W7.4 | **Aggregation hardening** — patch-run mode, terminal lane-state receipt, pointer provenance, root-X3 unification + criticality matrix | ~55K | final11 evidence: 8/11-good run shipped zero product (all-or-nothing assembly); lane state re-derived in ≥4 places; mtime/digest-free pointers; 4th X3 vocabulary at root | 🔲 TODO | A failed run re-completes by re-dispatching ONLY non-ALLOW lanes (patch run); one `lane_state.json` terminal receipt consumed everywhere; pointers carry run_id+x3+digest and are verified; one lane↔root X3 mapping receipt, exit==disposition, inspection override receipted; declarative required/optional/fatal lane matrix |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Gate-yield extractor over archived x2_gate_outputs across all runs | 🔲 TODO |
| W1.2 | Repair/regen fire-rate + selector score-distribution report | 🔲 TODO |
| W2.1 | Competencies SC 8→4 + bullets 4→3 behind env-tunable constants; canary runs | 🔲 TODO |
| W2.2 | Token-cap audit (remaining Qwen-sized caps) | 🔲 TODO |
| W3.1 | Shared word/sentence counting util; preview imports the canonical counter | 🔲 TODO |
| W3.2 | Judge-regen attempts SSOT reconcile (code vs test) | 🔲 TODO |
| W4.1 | Failover judge config + quorum behavior for single-judge lanes | 🔲 TODO |
| W5.1 | Retire zero-yield Qwen-era gates (advisory pass first) | 🔲 TODO |
| W5.2 | Delete dead qwen_vllm_health importers + offline Qwen stubs | 🔲 TODO |
| W6.1 | Before/after full AIG E2E with cost/latency receipts | 🔲 TODO |
| W7.1 | Patch-run mode: re-dispatch only non-ALLOW lanes into the same sections root, re-aggregate | 🔲 TODO |
| W7.2 | Terminal `lane_state.json` receipt (single writer); packaging/product-bar/summarizer consume it | 🔲 TODO |
| W7.3 | Pointer provenance: run_id + x3_code + digest in `latest_successful_real_run.json`, verified by consumers; replace mtime selection | 🔲 TODO |
| W7.4 | Root X3 unification + declarative lane criticality matrix + receipted exit override; cross-section coherence gates (3–4, evidence-first); env-plumbing → explicit param | 🔲 TODO |

---

## Out Of Scope

- Weakening any **content-law** gate (fact grounding, claim-ledger coverage, metric preservation, locked-identity, leakage scans) — these protect truth, not Qwen; they are exempt from retirement regardless of yield.
- The qwen-*naming* sweep (separate effort, partially landed) — this plan is about *behavioral* right-sizing.
- Judge **panel composition for headline/executive_summary** — the 2-judge panels are defended (judges carry the entire quality burden where X2 saturates on form; verdicts are final; cross-vendor diversity is load-bearing for ATS/anti-overfit dimensions; quorum survivability) and stay.
- `agentic_core` edits; other `apps_*`; prompt-content tuning (the <0.72 content-quality question remains deferred in the parent plan).

---

## Wave 1 — Gate-Yield + Repair-Fire-Rate Instrumentation

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Gate-yield extractor | ~25K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Repair/regen fire-rate + selector score report | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W1.1 — Tool that walks every archived `x2_gate_outputs.json` (e2e_aig_verify/*, runtime_proofs/*) and emits a per-lane, per-gate table: total evaluations, fail count, last-fired timestamp, provider era (Claude-only corpus). Classify each gate: CONTENT_LAW (exempt) / QWEN_COMPENSATION / FORM / WIRING. The 59–91-gate suites get an evidence-backed retirement candidate list; the 9-gate role_episode suites get an under-coverage check (G9).
- W1.2 — Same corpus: parse-retry fire rate per lane (expected ≈0 under Claude), synthesis/judge regen trigger rates, bullet/competencies selector score histograms vs the 0.72 floor (G4 calibration evidence), and per-lane provider-call counts (cost baseline for W6).

**Acceptance**: one report artifact (`docs/reports/apps_rg/lane_reasoning_yield_audit.md`) with the four tables; every W5 retirement and W2 recalibration must cite rows from it.

---

## Wave 2 — Generation Budget Recalibration

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — SC path cuts (competencies 8→4, bullets 4→3) behind env-tunable constants; canary AIG validation | ~28K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Token-cap audit for remaining Qwen-sized limits | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W2.1 — Competencies is the prime target: 8 paths × ~75s for a degenerate 8-choose-8 selection. Cut `COMPETENCIES_SC_PATH_COUNT` 8→4 (env-overridable), keep the regen round as the safety net; same for `sc_path_count_for_lane` 4→3 on bullet lanes. Validate per lane on standalone AIG canaries: X3_ALLOW maintained, selector still fills all slots (the W1 score histograms predict this; the canary proves it). Rollback = env var, zero code revert.
- W2.2 — Sweep remaining `*_MAX_OUTPUT_TOKENS` / regen caps against actual Claude output sizes from receipts (the 2,200/2,400 caps already burned us once); right-size with measured p99 + margin.

**Acceptance**: competencies wall-clock ≤5 min on canary (from ~10); bullets total paths ≤4 incl. regen on the happy path; all recalibrated lanes X3_ALLOW; constants env-tunable.

---

## Wave 3 — Repair-Ladder Harmonization

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Shared counting util: preview == canonical | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Judge-regen attempts SSOT reconcile | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W3.1 — exec_summary's `_synthesis_shape_reject_reason` counts words differently than `x2_exec_summary_paragraph_max_words` (observed: 152-word draft "rejected" by preview, passed by canonical). Extract the canonical counter into a shared util; the preview imports it. A repair call must never fire on a draft the canonical gate would pass.
- W3.2 — `JUDGE_REGEN_MAX_ATTEMPTS`: repair_policy code says 1, the unit test asserts default 3 (current tree shows an in-flight flip). Decide the authority (cost data from W1.2 informs it), set one constant, align test + docstring + env-cap semantics.

**Acceptance**: counter-drift repair calls = 0 on canary; one documented judge-regen default with green tests.

---

## Wave 4 — Judge Resilience for Single-Judge Lanes

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Failover judge config + quorum behavior | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- 9 lanes run `gemini_pro` alone: any transport outage, stale calibration, or rubric-version bump disqualifies the panel (quorum=1) and stalls the lane into HITL. Add a **failover** judge (config-declared, e.g. openai_chatgpt) invoked only when the primary is unavailable/disqualified — resilience without always-on second-judge cost. Headline/exec_summary keep their defended 2-judge panels unchanged.

**Acceptance**: fault-injection test (primary judge transport-blocked) → lane completes via failover with `MODEL_BACKED` rows; zero extra calls on the happy path.

---

## Wave 5 — Qwen-Compensation Retirement (Evidence-Gated)

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Retire zero-yield Qwen-era gates (advisory pass → removal) | ~25K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Delete dead Qwen importers + stubs | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**:
- W5.1 — From the W1 yield table: gates classified QWEN_COMPENSATION with **zero Claude-era fires** (candidates: vLLM transport-envelope stub checks, mock-language substring scans, positional-id compensation gates, duplicate self-check-consistency variants) flip to advisory for one full-run cycle, then are removed. Every removal cites its yield row. CONTENT_LAW gates are untouchable regardless of yield. Net target: bespoke suites trend from 59–91 toward the proven ~30–40 core without losing a single content protection; role_episode suites gain any floor the data says they're missing (G9).
- W5.2 — Fix/delete the dead `qwen_vllm_health` import sites (`section_cli_preflight.py`, `section_model_limits.py`, 1 unit test — import a module deleted by PR #256); retire `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB*` paths; keep receipt-contract fields (`qwen_health: NOT_APPLICABLE`) until a schema-versioned receipt change is separately authorized.

**Acceptance**: no production module imports a deleted module; every retired gate has a yield citation + one advisory cycle; full regression slice green.

---

## Wave 6 — Full-Run Proof (Before/After)

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — AIG E2E comparison run + cost/latency receipts | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Detail**: full AIG E2E with all recalibrations; compare lane matrix vs the pre-plan baseline (full6 + verifies), plus per-lane provider-call counts and wall-clock from W1.2's baseline.

**Acceptance**: every lane ≥ baseline disposition; total provider calls and wall-clock reduced (targets: competencies −50% time, bullets −25% calls); summarizer matrix + cost table archived as the closeout receipt.

---

## Wave 7 — Aggregation Hardening (post-section assembly)

WAVE_ID: W7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Evidence base (final11, 2026-06-10):** all 11 lanes executed (wiring fully healed), 8 X3_ALLOW + 1 REVIEW_JUDGE_SOFT_FAIL + 2 narrative X3_BLOCK → aggregation produced **zero product** (`decisive_status=FAIL: fatal_lane_recipe_policy`; no rollup/locked-copy/final-resume/package artifacts). Every packaging/display defect this session traced to lane state being re-derived in ≥4 places from different evidence (pointers, pre-run-failure files, x3 files, mtimes).

**Phases**:
- **W7.1** — **Patch-run mode** (highest-ROI item in this plan) | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO — re-dispatch ONLY non-ALLOW lanes into the same sections root; accepted lanes keep sealed receipts; re-run aggregation. Converts a stochastic single-lane flap (headline governance-signal, unify_narrative, ibm judge verdict) from "regenerate all 11 (~25 min, ~50 calls)" into "regenerate 1 lane (~2 min)".
- **W7.2** — **Terminal lane-state receipt** | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO — dispatcher writes one `lane_state.json` at lane completion (state enum, x3, run_dir, blocker); integrated packaging, product bar, and summarizer consume it instead of re-deriving (kills the `PHASE1_NO_RUN_DIR`-for-executed-lanes / `MISSING_NOT_ATTEMPTED`-for-ALLOW-lanes class).
- **W7.3** — **Pointer provenance** | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO — `latest_successful_real_run.json` carries run_id + x3_code + content digest; companion gate/product bar/summarizer verify before trusting; summarizer's mtime-based run-dir pick replaced by pointer-follow (constitutional artifact-provenance discipline applied to internal pointers).
- **W7.4** — **Root X3 unification + criticality matrix + coherence** | ~13K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO — one lane↔root X3 mapping receipt (kills the 4-vocabulary drift incl. `fatal_lane_recipe_policy`); process exit == disposition with any inspection override receipted; declarative per-lane required/optional/fatal matrix in one config; 3–4 evidence-first cross-section coherence gates (global metric dedup, document-level locked-identity verbatim, style normalization); serial-dispatch env-var plumbing (`MODULAR_R4_SECTIONS_ROOT_ENV`) replaced by the explicit context param.

**Acceptance**: a run with 1 injected lane failure re-completes via patch run without regenerating passing lanes; zero lane-state disagreements between packaging/product-bar/summarizer on canary; pointer-verification failure produces a named provenance error, not a silent cross-run read; root receipt carries the unified mapping and the exit code matches it.

---

## Definition of Done

| # | Definition of Done | Verification |
|---|---|---|
| 1 | Yield audit exists and is the cited authority for every cut | `docs/reports/apps_rg/lane_reasoning_yield_audit.md` + citations in each W2/W5 diff |
| 2 | Competencies ≤5 min, bullets ≤4 paths happy-path, all X3_ALLOW on canary | standalone canary runs + receipts |
| 3 | Preview==canonical: zero phantom repair calls | counter-drift counter in synthesis_regen_receipt = 0 on canary |
| 4 | Single-judge lanes survive primary-judge outage via failover | fault-injection test green |
| 5 | Zero content-law gates weakened or removed | diff review: retirements cite QWEN_COMPENSATION classification only |
| 6 | **Smoke run:** full AIG E2E equal-or-better matrix at lower cost | `python -m apps_rg --target-company AIG ...` + summarizer + cost comparison vs baseline |
| 7 | Targeted regression slice green | `python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "x2 or judge or selector or regen or self_consistency or headline or executive_summary or competencies or bullet"` |

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| Yield audit · SC/cap recalibration · ladder harmonization · judge failover · evidence-gated gate retirement · before/after proof | Yes — W1–W6 | — |
| Bullet content quality (<0.72 root question) | — | parent `apps-rg-aig-e2e-remediation-e4b7c1` deferred item |
| Receipt-schema cleanup (`qwen_health` fields, call-plan artifact names) | — | separate schema-versioned change |
| Qwen *naming* sweep residue | — | separate effort (partially landed) |

---

## Safety / Invariants

- **Evidence before cuts**: no gate retires and no budget shrinks without a W1 yield-table citation; canary X3_ALLOW is the floor for every recalibration.
- **Content-law exemption is absolute**: grounding, claim-ledger, metric-preservation, locked-identity, and leakage gates are out of retirement scope regardless of fire rate.
- All knob changes land behind env-tunable constants — rollback is configuration, not revert.
- Model-backed judges stay model-backed; failover adds availability, never replaces a verdict with a mock.
