---
plan_id: apps-rg-lane-aggregation-gap-closure-b8c3d1
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: [apps-rg-lane-reasoning-optimization-7c4e9b, apps-rg-aig-remaining-lanes-closeout-d4e1f7]
---

# apps_rg Lane + Aggregation Gap Closure — The Consolidated Master Plan

One plan for every gap surfaced by the 2026-06 per-lane and aggregation analyses: Qwen-era over-compensation (gates, SC paths, floors, caps), the numeric/config drift family, the uncovered stochastic-content failure class, judge resilience, and the all-or-nothing aggregation layer — organized by *theme* so one fix closes a gap class across all lanes at once.

> **plan_id discipline**: `plan_id` matches the filename stem `apps-rg-lane-aggregation-gap-closure-b8c3d1`. Wave markers use `plan=apps-rg-lane-aggregation-gap-closure-b8c3d1`.

## Supersedes
| Predecessor slug | Reason |
|---|---|
| apps-rg-lane-reasoning-optimization-7c4e9b | Created hours earlier with the optimization subset (W1–W7); this plan absorbs its full scope verbatim and adds the per-lane gap inventory (headline/exec/bullets/narratives/role-episode), the stochastic-content repair wave, and hygiene debt into one master inventory. No content dropped — wave mapping preserved below. |
| apps-rg-aig-remaining-lanes-closeout-d4e1f7 | **Code-review-verified superseded 2026-06-10**: every deterministic wave is landed AND committed (merge `655fc41284`, PR #280) — W1 dense-filter fix, W2 floor=3, W3 canonical ids + summarizer truth, W5 caps=8000, W6 judge refresh=True, narrative em-dash/roster fixes. The only open remainder (W4 all-11 proof + residuals: ibm fact↔content quality, headline signal flap, ibm_narrative cascade) maps exactly to this plan's G13/G14/G15 (W4) and W9 proof. Best evidence at supersession: final11 = 8/11 ALLOW + 1 review. |

> **Relationship (not superseded):** `apps-rg-aig-e2e-remediation-e4b7c1` (parent) continues as the historical remediation record; `apps-rg-c02-bootstrap-gate-correctness-c02f1a` continues independently (evidence durability). d4e1f7's residuals — (a) ibm per-slot fact↔content grounding, (b) headline governance-signal stochastic miss, (c) ibm_narrative cascade — are **active scope here** (W4: G13/G14/G15; proof: W9) as of its 2026-06-10 supersession.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** — The AIG E2E bring-up (2026-06-09/10) healed the wiring layer completely: `final11` executed all 11 lanes (8 X3_ALLOW + 1 review + 2 content blocks). Along the way, a full per-lane + aggregation gap analysis was performed against measured configs (SC paths, selector floors, judge panels, repair ladders) and live run artifacts (X2 gate counts, fire evidence, closeout matrices).
- **Complication** — The analysis surfaced 43 gaps in seven recurring families, scattered across two new plans, two in-flight plans' residuals, and chat-only findings: (1) **Qwen-era over-compensation** never recalibrated after PR #256 — 59–91 X2 gates on bespoke lanes vs 9 on Claude-era lanes, 8 SC paths feeding a degenerate 8-choose-8 competencies selection (~10-min lane), an uncalibrated 0.72 floor, Qwen-sized token caps (two already caused outages); (2) **numeric/config drift between paired surfaces** — six separate 100%-failure incidents (preview≠canonical counters, prompt-floor vs gate-floor, release-constant vs gate requirement, static judge rosters, off-by-one budgets); (3) **the uncovered stochastic-content failure class** — every repair ladder targets Qwen's *form* failures while Claude's actual residual failures (headline governance-signal flaps, ibm fact-drift judge verdicts) have **no** repair path; (4) **judge fragility** — 9 lanes on quorum=1; (5) **all-or-nothing aggregation** — final11's 8-good-lane run shipped zero product, lane state is re-derived in ≥4 places, internal pointers are provenance-free, and the root speaks 4 X3 vocabularies.
- **Question** — How do we close all of it in one coordinated effort, evidence-first, without weakening a single content-law protection?
- **Answer** — Structural enforcement first, then theme-waves: **W0 Contract Matrix** (invariants × surfaces, computed coverage, mutation proof — converts gap *discovery* from endless manual archaeology into a one-time deterministic computation and makes future omissions CI failures) → instrument (W1) → kill the drift family structurally (W2) → recalibrate generation budgets (W3) → cover the stochastic-content class with repair machinery (W4) → judge failover (W5) → right-size gates in both directions (W6) → harden aggregation incl. patch-run (W7) → clear hygiene debt (W8) → before/after full-run proof (W9).

## Definition of ENDED (the answer to "does this ever stop?")

Gap discovery is unbounded only while enforcement is enumerated (N invariants × 11 lanes hand-written, omissions invisible). This plan **ends** the unbounded class, by construction:

1. **Contracts are finite and frozen at W0**: the matrix bounds the invariant set. "Done" = matrix fully bound + per-cell mutation suite green + E2E canary green — a checkable state, not "no gaps found lately."
2. **After the freeze, a new "gap" is a new contract row** — a deliberate, single-entry-point product decision (add row → CI shows every unbound surface → bind or waive). Never again an emergency discovered by archaeology.
3. **Tuning is explicitly NOT a gap** (SC counts, caps, judge economics, patch-run ROI): optimization is infinite by nature, so it is budgeted and telemetry-fed (W1 receipts emitted continuously, weekly drift report via the existing calibration cadence) — scheduled maintenance, not discovery sessions.
4. **Two structural guarantees make regressions impossible rather than detected**: one implementation per rule (W2 — drift cannot occur between copies that don't exist) and matrix inheritance (new lanes/invariants cannot ship unbound).

---

## Master Gap Inventory (consolidated from the 2026-06-10 analyses)

| # | Gap | Lane(s) | Family | Wave |
|---|---|---|---|---|
| G1 | X2 gate-depth asymmetry (59–91 vs 9) with zero yield data | all | Qwen-comp | W1→W6 |
| G2 | Degenerate 8-choose-8 selection; 8 Qwen-sized SC paths; ~10-min runtime | competencies | Qwen-comp | W3 |
| G3 | Bullets SC 4+regen sized for Qwen variance | unify/ibm/role-episode bullets | Qwen-comp | W3 |
| G4 | 0.72 selection floor uncalibrated for Claude score distributions | all selector lanes | Qwen-comp | W1→W3 |
| G5 | Remaining Qwen-sized token caps unaudited (2 already caused outages) | all | Qwen-comp | W3 |
| G6 | Positional bullet-id injection masks schema regressions | bullet lanes | Qwen-comp | W6 |
| G7 | Preview ≠ canonical word counter (observed phantom repair calls) | exec_summary | drift | W2 |
| G8 | In-lane preview duplicates gate logic (prefix/pipes/words) | headline | drift | W2 |
| G9 | Release-constant ↔ gate coherence unguarded (judge-refresh outage class) | exec_summary (class: all) | drift | W2 |
| G10 | JUDGE_REGEN_MAX_ATTEMPTS code/test SSOT conflict (1 vs 3) | exec_summary | drift | W2 |
| G11 | Static judge-roster fossils (sweep for any lane still hardcoding) | all | drift | W2 |
| G12 | Off-by-one/normalization budget drift class (3rd lane incident) | narratives | drift | W2 |
| G13 | Stochastic content gates have no repair rung (governance-signal flap) | headline | stochastic | W4 |
| G14 | No bullet judge-remediation: decisive judge fail = dead run; pool holds unused alternates — *downgraded 2026-06-10: d4e1f7 W5's `slot_fact_story` grading anchor fixed the generation-side cause (gemini 0.0→5.0); this remains the cheap salvage path for residual soft-fail rolls (final11: 3.5 vs 4.0 after two 5.0 rolls)* | unify/ibm bullets | stochastic | W4 |
| G15 | Per-slot fact↔content semantic alignment uninstrumented before judge ("$10M ARR" drift) — *downgraded 2026-06-10: root cause closed generation-side by d4e1f7 W5 (slot_fact_story anchor + plan-metric scrub + compliance floors); entailment-at-selection remains as the deterministic backstop, no longer the active blocker* | ibm/unify bullets | stochastic | W4 |
| G16 | Empty selection reaches X2 as 15-gate cascade (pre-X2 short-circuit deferred) | bullet lanes | stochastic | W4 |
| G17 | HOLD-metric cross-fact bleed during generation | ibm bullets | stochastic | W4 |
| G18 | Quorum=1 judge on 9 lanes — outage/stale-calibration stalls lane to HITL | 9 lanes | judges | W5 |
| G19 | Judge-regen full-panel rescore cost uncalibrated (RESCORE_SOFT_ONLY policy) | exec_summary | judges | W5 |
| G20 | Role-episode under-gating: quality floors + reverse leakage scans unported | insurtech/ey ×4 | gates | W6 |
| G21 | No cross-section coherence gates (global metric dedup, doc identity, style) | aggregation | gates | W6 |
| G22 | Zero-yield Qwen gates retire (advisory-first; content-law exempt) | bespoke lanes | gates | W6 |
| G23 | All-or-nothing assembly — no patch-run; 8-good-lane run ships zero product | aggregation | aggregation | W7 |
| G24 | Lane state re-derived in ≥4 places (every packaging/display bug this cycle) | aggregation | aggregation | W7 |
| G25 | Provenance-free pointers + mtime run-dir selection | aggregation | aggregation | W7 |
| G26 | Four root-X3 vocabularies + unreceipted exit-0 override | aggregation | aggregation | W7 |
| G27 | Lane criticality (required/optional/fatal) scattered across 3 modules | aggregation | aggregation | W7 |
| G28 | Process-global env plumbing in serial dispatch loop | aggregation | aggregation | W7 |
| G29 | Locked-identity verbatim guaranteed per-lane, not per-document | aggregation | aggregation | W7 |
| G30 | Cascade coupling: one bullet fail kills two lanes (design review, companion law) | narratives | aggregation | W7 |
| G31 | Merged-doc anchor fields (gap_notes/self_check) from a different path than bullets | bullet lanes | hygiene | W8 |
| G32 | Dead `qwen_vllm_health` imports (2 prod modules + 1 test import a PR#256-deleted module) | preflight | hygiene | W8 |
| G33 | 9 competencies unit tests red on clean main (lockstep/rigor/bundle drift) | competencies | hygiene | W8 |
| G34 | Static hand-authored role-episode bundles — no freshness/consistency pipeline | insurtech/ey | hygiene | W8 |
| G35 | Narrative `exactly_one_sentence` naive-counter migration verification (decimal false-fail) | role-episode narratives | hygiene | W8 |
| G36 | **C0.3 graph-binding X2 enforcement is UNEVEN** — measured: `executive_summary_x2` has no `graph_skill_node_ids` gate; the generic role_episode suite (insurtech/ey ×4) enforces fact scope but **no graph-binding gate** — the flagship contract is weakest on the newest lanes | exec_summary, insurtech/ey ×4 | **C0.3 (value spine)** | W6 |
| G37 | **No per-section C0.3 coverage metric** — nothing measures which graph skill nodes were *available* for a section vs *surfaced* in output, or JD-targeted nodes vs used; "the graph drove the content" is asserted, never quantified | all 11 | **C0.3 (value spine)** | W1→W6 |
| G38 | **`APPS_RG_C03_GRAPH_MANDATORY` fail-closed path untested per lane** — does each of the 11 lanes actually BLOCK (not silently degrade) when graph evidence is absent? Only 2 enforcement sites exist (`c0_mandatory_policy`, `native_c03_skills_graph`) | all 11 | **C0.3 (value spine)** | W6 |
| G39 | **C0.3 gates must be pre-classified CONTENT_LAW** in the W1 yield audit — explicit retirement immunity before any W6 cuts | all | **C0.3 (value spine)** | W1 |
| G40 | **Base-resume anti-hydration gates are UNEVEN** — n-gram overlap gates exist for competencies/headline/ibm/unify; coverage for exec_summary, narratives, and role_episode lanes unverified — the "base resume is NEVER a content source" law is enforced lane-by-lane, not universally | all 11 | **base-containment** | W6 |
| G41 | **No document-level base-resume containment gate at aggregation** — per-lane scans only; the assembled resume is never scanned as a whole against base-resume prose | aggregation | **base-containment** | W6→W7 |
| G42 | **Identity-copy whitelist not formalized as a deterministic contract** — the ONLY permissible base-resume reads for generated lanes are company / title / location / dates-of-service (locked-copy manifest + prompt "calibration_only" notes exist, but no contract test asserts generated-lane code paths cannot read base-resume prose fields) | all 11 | **base-containment** | W6 |
| G43 | **Selection→bindability omission class** (code-verified 2026-06-10: 11✓/2◐/0✗) — targeting correctly selects graph skills the bundle layer cannot bind, so they silently drop (103/166 nodes unbound; born-empty families; 6 unlinked HIGH facts; 4/7 IBM episodes with empty fact links; 7-vs-8 family vocabulary drift). **Delegated to sibling plan `apps-rg-skills-bindability-closure-a7e2f9`** (frozen, first post-ship increment); its W3 bindability/liveness gate becomes a **W0 Contract-Matrix row** here. Bonus defects from verification: lowercase `"active"` vs `"ACTIVE"` on `ccb_insurance_domain_erm`; 166-vs-177 ledger/SQLite node-count disagreement | competencies / C0.3 chain | **C0.3 (value spine)** | W0 + a7e2f9 |
| G44 | **ADG P2 ratchet regression from apps_rg runtime (2026-06-10 regen FAIL, 14 > ceiling 12)** — two new MEDIUM antipattern sites block every ADG regeneration: (1) `apps_rg/runtime/section_graph_skills_proof_pool.py:119-122` `return_none_swallow` (`except (json.JSONDecodeError, OSError): return None` in `_role_episode_bundle_plan`; needs `# guardian: allow-return-none-swallow -- <reason>` via Author-Gate, or explicit error surfacing); (2) `apps_rg/runtime/sections/executive_summary_qwen_regen_dispatch.py:15` `star_import_use` in the ADR-082 Qwen-rename compat shim (smallest fix: delete the redundant `import *` — lines 16–21 already re-export the public symbols explicitly) | competencies / executive_summary | hygiene (CI-gate) | now |
| G45 | **Headline authoritative-attempt gap for format-retry adoptions** (found during W4.2 implementation 2026-06-10, pre-existing): a format-retry regen adoption (`record_regen_llm replaced_l2=True`) followed by X2 pass is NOT covered by the lane's `set_authoritative_attempt` condition — `ledger_blocks_product_pass` flips product PASS→FAIL via `regen_replaced_l2_but_authoritative_attempt_still_1`. Fix = uniform ledger-based predicate (`counted_regen_x2_pass` idiom, `section_repair_lane_integration.py:118-122`) as a deliberate, separately-tested change — NOT an accidental widening of the condition | headline | drift-family | W8 |
| G46 | **Pre-existing red: `tests/_apps_contract/test_headline_pa_compiled_prompt.py::test_compiled_headline_production_prompt_markers`** fails at clean HEAD (compiled production prompt lost the "not the default answer"/"identity reference" marker) — prompt or test drifted; reconcile with the G33 red-test cleanup | headline | hygiene | W8 |
| G47 | **E2E run-artifact durability** (incident 2026-06-10): the final11/closeout run dirs were written inside an ephemeral worktree and REAPED with it — the authoritative 9/11 baseline survives only as plan text. Ad-hoc E2E runs must write `--artifact-dir` under a durable root (primary checkout `artifacts/` or `~`), and the lane matrix + x1d/x3 verdict JSONs should be archived per run (heartbeat.ps1 already does this; ad-hoc worktree runs are the exposure) | aggregation / ops | receipts | W7 |
| G48 | **Contract-harness fixtures blocked pre-provider** (stash-proven pre-existing 2026-06-10): `test_apps_rg_graph_story_authority_e2e` unify+ibm cases fail at clean HEAD blocking at `wire_spine_c0_fec_or_block` (fixture env lacks C0.2 evidence), +1 competencies red, +9 lane-importing unit reds (failure sets identical clean vs patched) — the lane harnesses can't exercise post-C0 seams until fixtures carry C0.2 evidence; reconcile with G33 | unify/ibm bullets, competencies | hygiene | W8 |
| G50 | **Headline judge-level fact drift has no deterministic backstop** (attempt4 2026-06-11: gemini decisive 1.0 — "'Retrieval Lifecycle Controls' not supported by cited fact_engineering_platform_004"; X2 all-pass, openai 4.4 pass). The W4.3 numeric entailment is bullets-only; headline segment phrases need a composition-time cited-fact entailment check (non-numeric: key noun phrases ⊆ cited fact text) or a reselection-style re-roll on decisive single-judge fail | headline | stochastic | W4-residual |
| G51 | **exec_summary one unsourced ledger row → 11-gate echo cascade** (attempt4: `claim_ledger[2] missing source_fact_ids` echoed through every coverage/accounting gate). Same single-cause-cascade class W4.4 fixed for bullets: a pre-X2 orphan-row short-circuit (or one bounded regen feeding the orphan row back) would collapse 11 fails to 1 honest fail + repair | executive_summary | stochastic | W4-residual |
| G52 | **ibm_bullets pool selection collapsed to 0 slots while lane X2 passed** (attempt4: synthetic selector row decisive "0 slots, min_score=0.00, gate_ok=False" yet 0 X2 fails — bullets present from somewhere). Anomaly: selection-state vs lane-output divergence; W4.1 correctly excluded synthetic rows but the 0-slot shape needs RCA if it recurs under patch-run | ibm/unify bullets | stochastic | W7 (RCA on recurrence) |
| G49 | **Headline content-gate family needs FULL rung coverage, not per-gate arms** (3 E2E attempts 2026-06-10/11, each 9/11 with a DIFFERENT headline content gate tripping: governance signal → specificity floor → narrowing labels). Arms were added reactively (PR #284/#286/+). Durable closure: enumerate every pure-text stochastic content gate in the headline X2 suite (governance, specificity, narrowing/demote pair, jd-only-phrase, e0-ngram, …) and either (a) generalize the rung to evaluate the WHOLE pure-text gate subset pre-X1D and feed all failures back in one bounded regen, or (b) prove the remaining gates can't flap (input-independent). Until then each new flap costs a full E2E cycle to discover | headline | stochastic | W4-residual |

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.3 | **CONTRACT MATRIX — structural enforcement (ends the endless-gap class)** | ~50K | Invariant set enumerable from existing gates + the two value-spine contracts | 🔲 TODO | Machine-readable matrix (invariants × 12 surfaces) with `enforced_by`/`tested_by`/waiver per cell; CI gate fails on ANY empty cell; per-cell mutation fixtures (known-bad BLOCKS, known-good passes) auto-enumerated; all remaining coverage holes surface ONCE, deterministically — manual gap-hunting retired |
| W1 | W1.1, W1.2 | **Instrumentation** — gate-yield audit, repair/regen fire rates, selector score histograms, cost baseline | ~45K | Archived run corpus (e2e_aig_verify/*, runtime_proofs) suffices | 🔲 TODO | `lane_reasoning_yield_audit.md` with per-gate fire counts (G1), 0.72 histograms (G4), per-lane call/latency baseline; every later cut cites it |
| W2 | W2.1–W2.4 | **Drift-family elimination** — shared counters, config↔gate coherence asserts, judge-regen SSOT, roster sweep | ~40K | Shared utils importable by lane + validator | 🔲 TODO | G7/G8: previews import canonical checks (zero phantom repairs on canary); G9: startup assert fails fast on contradictions; G10: one constant, tests agree; G11/G12: sweep clean |
| W3 | W3.1, W3.2 | **Generation budget recalibration** — competencies 8→4, bullets 4→3, floor + cap audit | ~40K | W1 histograms predict; canary proves | 🔲 TODO | G2: competencies ≤5 min; G3: bullets ≤4 paths happy-path; G4: floor re-set from histogram; G5: caps sized from measured p99+margin; all X3_ALLOW on canary; env-tunable rollback |
| W4 | W4.1–W4.4 | **Stochastic-content repair coverage** — bullet judge-feedback reselection, headline signal rung, selection-time fact-entailment, pre-X2 short-circuit | ~55K | Bullet pool retains alternates; entailment scoped to selection-time check (not the unbounded content dig) | ✅ DONE (2026-06-10, PR #284 merged `da80b2929b`; 7-agent recon + adversarial design verification; 217/217 combined tests post-merge with c0 spine; live-flap proof rides the post-W4 E2E + 5-canary watch) | G14: decisive judge fail triggers ONE reselection from existing pool (no new generation) before final verdict — DONE, extended to soft-fail arm with revert-on-worse (north-star decision); G13: content-signal miss gets a targeted rung or prompt emphasis (flap rate →0 over 5 canaries) — code DONE, canary watch open; G15/G17: selector verifies bullet claims entailed by cited facts (catches "$10M ARR" drift pre-judge) — DONE; G16: empty selection fails once pre-X2 with true reason — DONE |
| W5 | W5.1 | **Judge resilience** — failover judge for quorum=1 lanes; rescore policy calibration | ~20K | openai_chatgpt acceptable failover; calibration ledger covers it | 🔲 TODO | G18: simulated gemini outage → lanes complete via failover, zero happy-path cost; G19: rescore-soft-only policy set with W1 cost data; headline/exec 2-judge panels unchanged (defended) |
| W6 | W6.1, W6.2 | **Gate right-sizing, both directions** — retire zero-yield Qwen gates; port floors/scans to role-episode; cross-section gates | ~45K | W1 yield table is sole authority; content-law exempt | 🔲 TODO | G22: each retirement cites yield row + 1 advisory cycle; G20: role-episode gains floors + reverse leakage scans the data justifies; G21: 3–4 evidence-first cross-section gates; G6: positional-id injection retired or downgraded to receipted warning |
| W7 | W7.1–W7.4 | **Aggregation hardening** — patch-run, terminal lane-state receipt, pointer provenance, root-X3 unification + criticality matrix | ~55K | final11 evidence base | 🔲 TODO | G23: failed run re-completes by re-dispatching ONLY non-ALLOW lanes; G24: one `lane_state.json`, all consumers read it; G25: pointers carry run_id+x3+digest, verified; G26/G27: one mapping receipt, exit==disposition, override receipted, declarative criticality matrix; G28: env→explicit param; G29: doc-level verbatim-identity gate; G30: companion-law design review (Author-Gate if change proposed) |
| W8 | W8.1, W8.2 | **Hygiene & debt** — dead imports, anchor-field coherence, red tests, bundle freshness, counter-migration verify | ~30K | No behavior changes beyond fixes | 🔲 TODO | G32: no prod module imports a deleted module; G31: merged doc's anchor fields sourced coherently or receipted; G33: 9 competencies tests reconciled; G34: bundle load-time consistency check vs base resume + graph; G35: narrative counter verified sentence-aware |
| W9 | W9.1 | **Before/after full-run proof** | ~20K | W1–W8 landed | 🔲 TODO | Equal-or-better lane matrix vs final11 baseline; total calls + wall-clock reduced (competencies −50% time, bullets −25% calls, retry cost −80% via patch-run); closeout receipts archived |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Contract registry: enumerate the invariant set (from existing gates + value-spine contracts) into a machine-readable matrix (invariants × 11 lanes + aggregation), each cell `enforced_by` / `tested_by` / signed waiver | 🔲 TODO |
| W0.2 | Coverage CI gate: computes matrix fullness, FAILS on any empty cell; new lanes inherit all rows; new invariants enter only as new rows | 🔲 TODO |
| W0.3 | Per-cell mutation proof (Fort Knox pattern at lane level): auto-enumerated known-bad fixture must BLOCK + known-good must pass for every cell | 🔲 TODO |
| W1.1 | Gate-yield extractor over archived x2_gate_outputs (classify CONTENT_LAW / QWEN_COMP / FORM / WIRING) | 🔲 TODO |
| W1.2 | Repair/regen fire rates, selector score histograms, per-lane cost baseline | 🔲 TODO |
| W1.3 | **C0.3 + base-containment baseline**: per-lane graph-binding coverage matrix (which lanes gate it, which don't); per-section graph-node available-vs-surfaced metric over archived runs; base-resume n-gram scan of every archived generated output; CONTENT_LAW pre-classification of all C0.3/base gates | 🔲 TODO |
| W2.1 | Shared counting/check utils; exec + headline previews import canonical | 🔲 TODO |
| W2.2 | Startup config↔gate coherence asserts (gate-requires-X ⇒ X-path enabled) | 🔲 TODO |
| W2.3 | Judge-regen attempts SSOT reconcile (code+test+docstring) | 🔲 TODO |
| W2.4 | Roster + numeric-drift sweep (static rosters, off-by-one class) | 🔲 TODO |
| W3.1 | SC cuts behind env-tunable constants (competencies 8→4, bullets 4→3) + canaries | 🔲 TODO |
| W3.2 | 0.72 floor re-set from histograms; token-cap audit from measured p99 | 🔲 TODO |
| W4.1 | Bullet judge-feedback reselection (pool alternates, no new generation) | ✅ DONE (PR #284, merged `da80b2929b` 2026-06-10; decisive + soft-fail arms, revert-on-worse + revert-on-X2-regression, sidecar supersession, receipts; 28 new tests) |
| W4.2 | Headline content-signal repair rung / prompt emphasis | ✅ DONE (PR #284; shared gate-predicate trigger, 1 bounded regen fail-closed, governance_floor added to evidence pack; 25 new/extended tests) |
| W4.3 | Selection-time fact-entailment check (per-slot claim ⊆ cited fact) | ✅ DONE (PR #284; deterministic numeric-token entailment vs slot's own C0-pool corpus, exclusion-only, ibm shared-bundle metric leak closed; 17+ tests) |
| W4.4 | Pre-X2 empty-selection short-circuit | ✅ DONE (PR #284; EMPTY_SELECTION_PRE_X2 single honest block, X3_BLOCK + non-zero exit, truthful artifacts preserved; truth-table tested) |
| W5.1 | Failover judge config + quorum behavior + rescore policy | 🔲 TODO |
| W6.1 | Zero-yield Qwen-gate retirement (advisory cycle → removal, yield-cited) | 🔲 TODO |
| W6.2 | Port quality floors + reverse leakage scans to role-episode; cross-section gates | 🔲 TODO |
| W6.3 | **C0.3 + base-containment to PARITY across all 11 lanes**: graph-binding X2 gate added to exec_summary + role_episode suites; per-lane C0.3-mandatory fail-closed tests; uniform base-resume anti-hydration gate on every lane; document-level containment gate at assembly; identity-whitelist contract test (generated lanes can read ONLY company/title/location/dates) | 🔲 TODO |
| W7.1 | Patch-run mode (re-dispatch only non-ALLOW lanes, re-aggregate) | 🔲 TODO |
| W7.2 | Terminal `lane_state.json` receipt (single writer, all consumers) | 🔲 TODO |
| W7.3 | Pointer provenance (run_id+x3+digest, verified; mtime→pointer-follow) | 🔲 TODO |
| W7.4 | Root-X3 unification, criticality matrix, receipted override, env plumbing, doc-identity gate | 🔲 TODO |
| W8.1 | Dead qwen imports + anchor-field coherence + counter-migration verify | 🔲 TODO |
| W8.2 | 9 red competencies tests + bundle freshness check | 🔲 TODO |
| W9.1 | Before/after full AIG E2E with cost/latency receipts | 🔲 TODO |

---

## Out Of Scope

- Weakening any **content-law** gate (grounding, claim-ledger coverage, metric preservation, locked identity, leakage scans) — exempt from retirement regardless of yield.
- The **unbounded** bullet content-quality dig ("why do SC paths score what they score") — W4.3 scopes only the deterministic *entailment-at-selection* check; prompt/content tuning stays deferred in the parent plan.
- Headline/executive_summary judge **panel composition** — the 2-judge panels are defended and stay.
- `agentic_core` edits; other `apps_*`; receipt-schema renames (e.g. `qwen_health` fields) — separate schema-versioned change; qwen *naming* residue (separate, largely landed).
- d4e1f7's live W4 closeout execution — runs to completion independently; its residuals activate here afterward.

---

## Wave Detail (compact — each phase names its gaps; the inventory table is the SSOT)

**W1 Instrumentation.** Build the evidence layer everything else cites: walk every archived `x2_gate_outputs.json` + selection/regen receipts across all Claude-era runs → per-gate fire table with CONTENT_LAW/QWEN_COMP/FORM/WIRING classification (G1), selector score histograms vs 0.72 (G4), repair-ladder fire rates, per-lane provider-call + latency baseline (for W9). Output: `docs/reports/apps_rg/lane_reasoning_yield_audit.md`.

**W2 Drift-family elimination.** The six observed drift incidents share one shape: two implementations of one rule. Extract shared canonical utils (word/sentence counters, structure checks) and make every in-lane preview import them (G7, G8). Add startup coherence asserts: any gate that *requires* an artifact fails fast at import if the only producing path is disabled (G9 — the judge-refresh outage class). Reconcile `JUDGE_REGEN_MAX_ATTEMPTS` to one authority (G10). Sweep for static judge rosters and remaining off-by-one numeric drift (G11, G12).

**W3 Generation budget recalibration.** Competencies SC 8→4 (the 8-choose-8 selection is degenerate; paths only buy term variance — G2), bullets 4→3 with the regen round retained (G3), 0.72 floor re-set from W1 histograms (G4), token caps sized from measured Claude p99 + margin (G5). All env-tunable; canary X3_ALLOW is the floor.

**W4 Stochastic-content repair coverage.** The failure class Claude actually produces, currently uncovered: (W4.1) decisive bullet judge fail triggers **one reselection** from the existing candidate pool guided by the judge's per-slot findings — no new generation, near-zero cost (G14); (W4.2) headline content-signal gates get a targeted rung or prompt emphasis (G13); (W4.3) selection-time **entailment check** — a candidate bullet whose claim isn't supported by its cited fact is rejected before selection (catches the "$10M ARR" drift 5 stages before the judge; G15, G17); (W4.4) pre-X2 empty-selection short-circuit (G16).

**W5 Judge resilience.** Config-declared failover judge invoked only on primary unavailability/disqualification for the 9 quorum=1 lanes (G18); judge-regen rescore policy (full panel vs soft-only) set with W1 cost data (G19).

**W6 Gate right-sizing, both directions.** Retire QWEN_COMP-classified zero-yield gates via one advisory cycle each, yield-row cited (G22); port the proven quality floors and reverse cross-employer leakage scans to the 9-gate role-episode suites where data justifies (G20); add 3–4 cross-section coherence gates at assembly (global metric dedup, doc-level verbatim identity, style normalization — G21); retire or downgrade the positional-id injection to a receipted warning (G6).

**W6.3 — The two flagship contracts to parity (the value-spine wave).** The C0.3 skills graph is apps_rg's core value proposition; the gates that prove the graph drove the content must be **uniform, per-section, and untouchable**:
- **Graph-binding parity (G36)**: add the `graph_skill_node_ids`-required X2 gate to `executive_summary_x2` and the generic role_episode suite (measured holes); after this, all 11 lanes deterministically reject output whose claims don't bind graph nodes (and/or ledger facts per lane contract).
- **Coverage metric (G37)**: per-section receipt `c03_coverage_receipt.json` — graph nodes available (from the section's targeting capsule) vs surfaced in output vs JD-targeted; a floor (evidence-set from W1.3 baseline) becomes an X2 gate where the data supports one, an advisory metric elsewhere. This converts "graph-grounded" from narrative to number.
- **Fail-closed proof (G38)**: per-lane test matrix — with graph evidence artificially absent and `APPS_RG_C03_GRAPH_MANDATORY=1`, each of the 11 lanes must BLOCK with a named reason, never silently degrade to non-graph content.
- **Base-containment parity (G40–G42)**: one shared anti-hydration validator (base-resume prose n-gram overlap) applied to every generated lane uniformly; a document-level scan at assembly over the full merged resume; and a contract test pinning the **identity whitelist** — generated-lane code paths may read exactly four base-resume fields (company, title, location, dates-of-service) and nothing else; any new read site fails the contract test.

**W7 Aggregation hardening.** Patch-run mode: re-dispatch only non-ALLOW lanes into the same sections root, re-aggregate — accepted lanes keep sealed receipts (G23; converts a 1-lane flap from ~50-call rerun to ~2-min retry). Terminal `lane_state.json` written once by the dispatcher, consumed by packaging/product-bar/summarizer (G24). Pointer payloads carry run_id+x3+digest and are verified; mtime selection replaced (G25). One lane↔root X3 mapping receipt; exit==disposition; inspection override stamps a receipt (G26). Declarative required/optional/fatal lane matrix (G27). Env plumbing → explicit context param (G28). Document-level locked-identity verbatim gate (G29). Companion-law cascade design review — Author-Gate before any change (G30).

**W8 Hygiene & debt.** Fix dead `qwen_vllm_health` importers (G32); source merged-doc anchor fields coherently (G31); reconcile the 9 red competencies tests (G33); bundle load-time freshness/consistency check (G34); verify the narrative sentence-counter migration (G35).

**W9 Proof.** Full AIG E2E vs the final11 baseline: equal-or-better matrix, measured cost/latency reductions, patch-run demonstrated on an injected failure. Closeout receipts archived.

---

## Definition of Done

| # | Definition of Done | Verification |
|---|---|---|
| 1 | Yield audit exists; every retirement/recalibration cites it | report + diff citations |
| 2 | Zero drift-class incidents reproducible: previews==canonical, coherence asserts in place, one judge-regen constant | canary receipts + assert unit tests |
| 3 | Competencies ≤5 min, bullets ≤4 paths happy-path, floor/caps recalibrated, all X3_ALLOW on canary | standalone canaries + receipts |
| 4 | Stochastic tail covered: judge-fail reselection, signal rung, entailment-at-selection, single-block empty selection | fault-injection + 5-canary flap-rate check |
| 5 | Quorum=1 lanes survive primary-judge outage | fault-injection test green |
| 6 | Zero content-law gates weakened; role-episode gains data-justified floors | diff review vs yield classifications |
| 7 | **Smoke run:** injected single-lane failure re-completes via patch run without regenerating passing lanes | patch-run canary + `lane_state.json` receipts |
| 8 | Full-run proof: equal-or-better matrix at measurably lower cost (competencies −50% time, bullets −25% calls, retry −80%) | W9 closeout vs final11 baseline |
| 9 | Targeted regression slice green | `python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "x2 or judge or selector or regen or self_consistency or headline or executive_summary or competencies or bullet or narrative or lane_evidence or rollup or c03 or graph or base_resume"` |
| 10 | **C0.3 adherence proven per section**: all 11 lanes carry the graph-binding gate; coverage receipts emitted; all 11 fail-closed tests pass with graph absent | gate-parity diff + `c03_coverage_receipt.json` in every lane run dir + fail-closed matrix green |
| 11 | **Base-resume containment absolute**: uniform per-lane anti-hydration gate + document-level scan = zero prose hits; identity-whitelist contract test green (only company/title/location/dates readable) | W9 full run: doc-level scan clean; contract test in CI |

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| All 43 inventory gaps (G1–G43; G43 delegated to a7e2f9) | Yes — W1–W9 | — |
| Unbounded bullet content-quality dig | — | parent `apps-rg-aig-e2e-remediation-e4b7c1` deferred item |
| Receipt-schema renames (`qwen_health`, call-plan filenames) | — | separate schema-versioned change |
| Mock-provider test reconciliation (23 reds) + qwen naming residue | — | existing chips/efforts |

---

## Safety / Invariants

- **Evidence before cuts**: nothing retires or shrinks without a W1 yield-table citation; canary X3_ALLOW is the floor for every recalibration.
- **Content-law exemption is absolute** (grounding, claim-ledger, metric preservation, identity, leakage).
- **The C0.3 skills graph is the value spine.** Every C0.3 gate (graph-binding, allowlist coherence, mandatory fail-closed, coverage floors) is CONTENT_LAW by definition — pre-classified in W1.3, immune to W6 retirement forever. Optimization may touch *how much we sample*; it may never touch *whether the graph proves the content*.
- **The base resume is identity-only for generated lanes**: company, title, location, dates-of-service — nothing else, ever. All other base-resume content reaches the product exclusively through the locked-copy deterministic path. Enforced three ways: per-lane anti-hydration gates, the document-level scan, and the identity-whitelist contract test.
- All knobs env-tunable — rollback is configuration, not revert. Retired gates pass one advisory cycle first.
- Model-backed judges stay model-backed; failover adds availability, never replaces a verdict. Reselection (W4.1) chooses among *already-generated, already-receipted* candidates — it never fabricates.
- Patch-run reuses only lanes with sealed receipts + verified pointers; aggregation provenance rules apply to every reused artifact.
