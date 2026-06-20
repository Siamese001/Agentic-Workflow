---
plan_id: typed-edge-role-facet-guardrails-a6f3d2
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: ["phase2-gtm-presales-remaining-f7a2c9"]
---

# Typed Edge Role Facet Guardrails

> **Superseded for active execution (2026-06-16):** use
> [`apps-rg-11-lane-closeout-5f8c2a.md`](apps-rg-11-lane-closeout-5f8c2a.md)
> as the active SSOT for finishing apps_rg. This file remains historical design
> context for role facets, typed edges, sliding-scale composition, and waterfall
> proof. Its embedded lane-board status is stale.

Make GraphDB the skills and metrics SSOT, remove legacy candidate-fact authority noise before baseline, certify graph behavior before typed edges, add role-family facets, then add typed proof edges and sliding-scale composition guardrails with mandatory E2E waterfall evidence.

> **plan_id discipline**: markers use `plan=typed-edge-role-facet-guardrails-a6f3d2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W2 (W2.3 — 2026-06-15: **8/11 lanes X3_ALLOW** [competencies, unify_bullets, ibm_bullets, insurtech_bullets, ey_bullets, insurtech_narrative, ey_narrative, **unify_narrative**]. 3 fixes delivered to main this session: (1) **parallel manifest RESTORED** `cab5caf0fa` (serial re-pin was a regression — wave-0 max_parallel:5, wave-1:4, PR#325 values; 1.96×); (2) **unify_narrative graph-era binding** `386179710b` (validators recognize `reb_unify_*`/`skill_*` bundle+skill ids, not just legacy `bul_unify_*` slot ids; offline-proven, FAIL→PASS); (3) **ibm_bullets KEYSTONE** `ffdf540f3b` (Gemini X1D `unsupported_metric` cleared by surfacing the approved+promotable "20%" metric_outcome into the judge `allowed_fact_packet` — `metric_cap=0` from missing `_CAPS_BY_BAND` entry had stripped it from judge evidence; live-validated factual_support 1.0→5.0, X3_ALLOW; **NO selection change** so W2/W3 diagnostics untouched). **ibm_narrative now UNBLOCKED** (was upstream cascade). 2 BLOCK remain: **executive_summary** (6 generation-quality issues: claims lacking source_fact_ids, "$22m" style-echo, JD-phrase copy, 148>140 words) + **headline** (3 graph-era binding gates [same family] + `xyz_literal_grounding` + `openai_chatgpt` X1D — two-front). ibm_narrative likely needs the same graph-era scope/binding fix as unify_narrative (`ibm_narrative_x2.py` is bul_ibm_*-only).)
LAST_COMPLETED_WAVE: W2.2 (competencies + ibm_bullets fixes; W1 + W2.0/W2.1 + FEC grounding-gate fix [c245b7be97] all merged)
LAST_UPDATED: 2026-06-15
REBASELINE_2026_06_13: Full waterfall rebaselined against merged main (HEAD 1495ffb548) — see "## Rebaselined Waterfall — Current Main" (the status SSOT). Parallel executor merged (11.7 min/E2E, 1.96×); W1/W2.0/W2.1/W2.2-competencies + replay harness merged; lane board 7 ALLOW / 4 BLOCK (ibm_bullets, headline, exec_summary, +ibm_narrative cascade); P3/P7 DONE, P2 not-a-blocker, P4/P5 open; live-API floor ~4 E2Es (~50-70 min). Prior "~8 min / P3-pending / conditional-on-merge" framing was stale (relied on memory + session-PR-state, both wrong); corrected by reading code.
E2E_GATE_POLICY: graph-% correctness proof rides the FREE selection diagnostic across 5 targets at stages A–D; LIVE E2E limited to 2 ship targets (Anthropic + Brown & Brown) — single-resume gates W1..W4 (default Anthropic), 2-resume live enforcement at W5. 2 of the 5 (Neo4j VP Product Management, Aveva Distinguished AI Tech Lead) are held-out, run cold on frozen config = generalization test. Supersedes the prior "3-resume / 33-lane at W5" model — see "### Graph-% + Waterfall Variance Evidence § Target roster".
PLAN_AMENDMENTS_2026_06_13: (1) W2.1/W2.3 Execution Details scope corrected to single-resume; (2) W3/W4 cross-role smoke-run implementation locus named (`tools/apps_rg/selection_diagnostic.py`, built in W3.1); (3) W5.0 phase added — Truist + B&B threshold-table authoring before W5.1; (4) W2.1 output-hash made conditional on Deterministic/Replay Rule mode; (5) Stage A canonical artifact path = `artifacts/w1/`; (6) Stage A prior-stage variance carve-out; (7) W2.2 `candidate_fact_id` search removed (P0.1 owns it).
PLAN_AMENDMENTS_2026_06_13B: TARGET-MODEL CHANGE (operator-approved). Graph-% correctness evidence widened 3→5 diagnostic targets (free, non-generation) for a stronger generalization proof; LIVE E2E narrowed 3→2 ship targets. Roster: tuned = Anthropic, Brown & Brown, Truist; **held-out** (frozen-config, run cold) = Neo4j VP Product Management (PM facet), Aveva Distinguished AI Tech Lead (distinguished-IC facet). 5-target diagnostic at stages A–D (target-agnostic mechanism stages); 2 live (Anthropic + Brown) end-to-end incl. W5 sliding-scale enforcement; Truist/Neo4j/Aveva are SELECTION-proven only (not generation-proven). **Wherever older text below says "3 targets / 3-resume / 33-lane", read per this model: 5 on the diagnostic, 2 live.** Defense + roster in "### Graph-% + Waterfall Variance Evidence".
STATUS_2026_06_14: **FEC grounding false-block FIXED** (fix `76f2461bb2`, on main `c245b7be97`) — graph-authority lanes now GENERATE (ibm_bullets `REAL_LLM`, **25/26 X2 gates PASS**), reversing the structural 0/11. **Remaining ibm_bullets blocker** = `x2_ibm_metric_anchor_bullet_ownership: bul_ibm_005_missing_metric_token`. Grounded cause: `bul_ibm_005` plan_fact = `fact_revenue_ops_001` carries a **HELD "$10M new ARR"** (`has_metric=True`, `metric_outcome_ids=None`) while the canonical anchor expects the **approved "20%"** (`metric_ibm_20pct_joint_revenue_growth`); the LLM correctly avoided $10M → metric-free bullet → anchor gate fails (slot marked has-metric but neither $10M nor 20% anchored). Also: Gemini Pro X1D `MODEL_BACKED_FAIL`. **Fix locus:** `build_ibm_phase2_graph_plan_fact` (`apps_rg/runtime/sections/ibm_bullets_graph_evidence.py`). **RESOLVED 2026-06-14 (fix `f8943f9698`)** — operator chose **drop-held-metric**: a raw ledger metric is claimable only when an approved `metric_outcome` is bound; the unbound held "$10M" → `has_metric=False` → the anchor gate's no-metric escape passes truthfully (regression test `tests/unit/apps_rg/test_ibm_held_metric_not_claimable.py`). **Validated live:** ibm_bullets now `x2_ibm_metric_anchor_bullet_ownership=PASS`, **ALL 26 X2 gates PASS**, `PRODUCT_QUALITY_STATUS=PASS`. **Last ibm_bullets blocker** = decisive **Gemini Pro X1D judge** `MODEL_BACKED_FAIL` (Anthropic Claude X1D passes 0.74; ALLOW requires every configured X1D judge model-backed-pass) — RESOLVED 2026-06-14 (fix `f678fb9103`). **Root:** the slot→candidate-fact ranking (stamped to `bul_ibm_*` by order) and the slot→bundle map used by generation (`IBM_BULLET_SLOT_BUNDLE_MAP`) were assigned independently, so the X1D grounding judge graded the bundle-generated bullet against an UNRELATED ranked candidate fact (bul_ibm_005 alliance bullet vs Salesforce $10M fact). **Fix:** `_rebind_ibm_slot_claim_text_to_bundle` (in `section_graph_skills_proof_pool.py`, after slot-id stamping) rebinds each slot's judge-facing `claim_text` to its bundle narrative + approved metric-outcome labels (surfaces the approved "20%" as grounding); generation unaffected; candidate_fact_id lineage preserved; held $30M/$22M phrases excluded. **Validated live:** ibm_bullets **X3_ALLOW** — Gemini X1D 1.0→**5.0 PASS**, Claude 0.75 PASS, all 26 X2 PASS, exit 0. **FIRST fully-green generated lane.** Likely SYSTEMIC (unify/insurtech/ey share the stamp-by-order pattern). **Next sub-wave:** full 11-lane baseline E2E to measure the post-fix board.
W1_RESET_NOTE: 2026-06-13 operator directive "assume nothing was done, start at beginning" — prior W1 blocking-baseline DONE markers retired; W1 re-passed under the amended current-substrate-passable bar with 6-lane W2 blocker ledger (see W1 Blocker Ledger below).
W1_CLOSE_OUT_2026_06_13: W1 marked DONE on the current-substrate-passable bar (operator decision 2026-06-13). 5 lanes X3_ALLOW on existing graph substrate (unify_bullets, insurtech_bullets, ey_bullets, insurtech_narrative, ey_narrative). 6 lanes deferred to W2 — see W1 Blocker Ledger. Durable config landed: (a) `apps_rg/runtime/section_model_limits.py` `SECTION_MODEL_MAX_MODEL_LEN` default 24576 → 32768; (b) `apps_rg/runtime/sections/executive_summary_context_limits.py` `DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS` / `DEFAULT_REGEN_MAX_OUTPUT_TOKENS` 2048 → 4096, `HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS` 4096 → 8192, `_DEFAULT_CONTEXT_WINDOW` 24576 → 32768; (c) `resolve_provider_context_window` precedence flipped — app-local `APPS_RG_SECTION_MAX_MODEL_LEN` wins, legacy `VLLM_MAX_MODEL_LEN` kept as fallback only. Tests passing (13/13). MAX_PATH lesson: every W2–W5 run MUST use a short `--artifact-dir` (e.g. `artifacts/w2`, `artifacts/w3`).

---

## Rebaselined Waterfall — Current Main (2026-06-13, HEAD 1495ffb548)

> ⛔ **SSOT for current status. Code-grounded (verified against merged `main`, not memory or the chat
> narrative). Supersedes any conflicting inline status below.** The North Star is unchanged: a finished
> resume = all 11 generated lanes `X3_ALLOW` → run assembles `final_resume.json` → DOCX built from it.

### What is MERGED in main (verified in code)

| Capability | Where (code) | Effect |
|---|---|---|
| **Parallel lane execution** | `section_lane_executor.py` lock-free (`_ENV_OVERLAY_LOCK` removed); manifest `default_max_parallel: 5`, wave-1 `max_parallel: 4` | **A full 11-lane E2E ≈ 11.7 min** (measured 704s vs 1383s serial = 1.96×), identical dispositions |
| **W1 Claude-era token config** | `section_model_limits.py` (ctx 32768), `executive_summary_context_limits.py` (output 4096 / cap 8192) | exec_summary parse-truncation fixed |
| **W2.0 metric_outcome materialization** | `metric_outcome_materializer.py` (92 nodes + 452 edges) | metrics are first-class GraphDB rows |
| **W2.2 alias layer** | `graph_era_aliases.py` (`source_fact_ids↔graph_evidence_ids`) | graph-era field foundation |
| **competencies lane fix** | required-family pack retention + bundle enrichment + prompt align + graph-bundle backfill | **competencies → X3_ALLOW** |
| **Offline gate-replay harness** | `tools/apps_rg/replay_section_gates.py` | post-gen fixes validate in ~11s, **zero API** |

### Current lane board — 10/11 X3_ALLOW (validated 2026-06-15, serial E2E; on `origin/main`)

> SSOT for Stage B status. 10 lanes validated via serial E2E (`artifacts/m2s` 9/11 + `artifacts/m4`
> headline ALLOW). Session fixes on `origin/main`: `cab5caf0fa` parallel · `386179710b` unify_narrative
> binding · `ffdf540f3b` ibm_bullets keystone · `a15cd3997d` unify_narrative scope · `6071614cc5` narrative
> opener · `7c93de856e` lane progress bar · `ccd8128363` ibm_narrative (slot→bundle + mechanism) ·
> `afed4e146e`+`48a153bd13` headline (binding + grounding skill-text + plan↔ledger subset).
> Validate serial — parallel is flaky (C0 race, backlog G58); the X1D failures seen on parallel runs
> were evidence contamination, disproven under serial.

| Status | Lanes |
|---|---|
| ✅ X3_ALLOW (10) | competencies, unify_bullets, **ibm_bullets**, insurtech_bullets, ey_bullets, **unify_narrative**, **ibm_narrative**, insurtech_narrative, ey_narrative, **headline** |
| ❌ X3_BLOCK (1) | **executive_summary** — last lane (see ledger; X2-only, 4 gates) |

> **executive_summary token-budget note (2026-06-15):** the migration commit `b5563e8d1c` (+9 lines)
> tipped the 211-line exec_summary prompt over the 95% input-token cap (`L2_BLOCK`, ~776 over) → no
> generation; reverted (`e2c930aaff`). The fix MUST be **net-negative** on tokens: trim the legacy
> hardcoded fact ids (`fact_engineering_platform_006`/`fact_governance_003`/`fact_quant_hpc_*`) + literal
> `$22M/20%/8→28` (repeat ~8× across lines 84-103) + condense the verbose S1-S6 rules to create headroom,
> THEN fold the 4 fixes (hardcoded-figure ban · allowlist-generic metric sourcing · JD-verbatim-copy ban ·
> S1 mechanism-list ban) in tersely. Budget-aware refactor + live serial validation = the genuine finish.

#### Remaining-lane blocker ledger (W2.3 — finish these 3 → 11/11 → first Anthropic DOCX)

> Plain-English cause first; the precise gate/term follows. These are the in-scope finish-line items
> for this wave — worked in sequence under one owner, validated by one batched E2E (not separate chips).

| Lane | What's wrong (plain) | Precise cause | Fix | Validation |
|---|---|---|---|---|
| **ibm_narrative** | The IBM paragraph is rejected on a bookkeeping mismatch, not its content: it credits facts with the *old* reference numbers while the approved-evidence list now uses the *new* ones — same facts, no translation step. Also reads too generic. | Cites `bul_ibm_*` slot ids; FEC holds graph-era `reb_ibm_*` bundle ids → `x2_claim_ledger_source_fact_ids_subset_of_fec` (no slot→bundle resolution at the shared gate). Plus `x2_narrative_technical_specificity_floor` (no named mechanism). | Resolve slot→bundle (`IBM_BULLET_SLOT_BUNDLE_MAP` exists) so a cited slot counts as its FEC bundle; require a mechanism token in the prompt. | one batched E2E |
| **executive_summary** | Written, but fails six writing-quality checks: some claims aren't tied to a verified fact, it repeats a "$22M" figure copied from a style example, it lifts a phrase from the job posting, and it runs 8 words over the 140-word cap. | 6 X2 gates: unsupported/orphan claims, `north_star_style_echo` ($22m), `jd_phrase_copy`, `paragraph_max_words` 148>140, allowed-fact utilization, mechanism-inventory. | Prompt-harden: ground every claim to a source fact, drop style-echo numbers, stay in budget. | one batched E2E |
| **headline** | The hardest — fails three ways at once: same old-vs-new reference-number mismatch as IBM; its phrases use words absent from the facts they cite; and one of two AI graders (OpenAI) rejects it. | Graph-era binding gates (`*_bundle_id_required` etc.) + `xyz_literal_grounding` (segment nouns ungrounded; `skill_*` claim_text unresolved) + decisive `openai_chatgpt` X1D. | Same binding-recognition fix as the narratives; ground segment nouns to bound facts; re-check X1D. | one batched E2E |

> Tracking decision (2026-06-15): these stay **rows in this plan**, not `spawn_task` chips — they are the
> Stage-B finish line (north star), share one validation run (narratives need their companions in the same
> build), and would collide on provider rate limits + overlapping checker/prompt files if split across
> sessions. WIP=1, one owner. No full rebaseline — the B→C→D→E waterfall structure is unchanged; only the
> Stage-B scoreboard advanced 7→8/11.

### The remaining waterfall (each stage = one ~12-min live E2E, run serial; offline build in between)

| Stage | Wave | Goal | Validation | Live E2E |
|---|---|---|---|---|
| **B** | W2.2 → **W2.3** | Fix the 4 blocked lanes → **11/11 X3_ALLOW → `final_resume.json` assembles → first finished Anthropic DOCX** | replay-offline per lane; 1 batched 11/11 confirm | **1 × ~12 min** |
| **C** | W3 | Role-family / facet targeting over the now-passing pool | replay + **5-target** diagnostic (non-gen, offline; incl. 2 held-out run cold) | 1 × ~12 min |
| **D** | W4 | Typed proof/traversal edges | replay + **5-target** diagnostic (offline) | 1 × ~12 min |
| **E0** | W5.0-W5.2 | Sliding-scale % **diagnostics** (Anthropic + B&B threshold tables; dry-run) | **replay of Stage D** (no-effect stage) | **0** |
| **E1** | W5.3-W5.4 | Sliding-scale % **active enforcement** + full waterfall report | **2 ship targets** (Anthropic + Brown) live under enforcement | 1 × ~12-24 min |

**Live-API floor ≈ 4 sequential E2Es (~50-70 min total)** — measured, parallel; not the pre-parallel ~4 h. The first **finished Anthropic resume** lands at the END of Stage B (W2.3). C/D/E refine targeting + composition on an already-shipping pipeline.

### Graph-% + Waterfall Variance Evidence — REQUIRED (proves the graph is correct)

> ⛔ **This is the original plan's whole reason for being and MUST NOT be dropped by the cost rebaseline.**
> The proof that the graph is implemented correctly is the **graph-skill % breakout × all 11 lanes** for a
> role-family-diverse target set, plus the **stage-to-stage variance** showing each waterfall step changed the
> selected-skill composition the way its one causal change predicts. **Operator amendment 2026-06-13B:** the
> correctness proof rides the FREE selection diagnostic across **5 targets** (stronger generalization), while
> the expensive LIVE E2E is limited to **2 ship targets**. See § Target roster + § Cost allocation below.

#### Target roster (5 diagnostic / 2 live) — all have a complete briefing + JD on disk (verified)

| # | Target (role) | JD + briefing stem (`apps_rg/config/targeting/`) | Role-facet × domain corner | Tuned? | Role in test |
|---|---|---|---|---|---|
| 1 | **Anthropic** — Mgr Applied AI Architecture, Partnerships | `anthropic_manager_applied_ai_architecture_partnerships_*` | partnerships / GTM applied-AI × AI-native | tuned | **LIVE + ship** |
| 2 | **Brown & Brown** — SVP IT Strategy & Innovation | `brown_brown_svp_it_strategy_innovation_*` | IT strategy / exec × insurance | tuned | **LIVE + ship** |
| 3 | **Truist** — Head Agentic AI Engineering | `truist_head_agentic_ai_engineering_*` | agentic-eng leadership × banking | tuned | diagnostic-only |
| 4 | **Neo4j** — VP Product Management, Agentic AI | `neo4j_vp_product_management_agentic_ai_*` | **product management** × AI-native | **HELD-OUT** | diagnostic-only (run cold) |
| 5 | **Aveva** — Distinguished AI Tech Lead | `aveva_distinguished_ai_tech_lead_initiatives_*` | **distinguished IC / tech-lead** × industrial SW | **HELD-OUT** | diagnostic-only (run cold) |

- **Why these 5:** they occupy five distinct (role-facet × domain) corners; #4 (PM) and #5 (distinguished-IC) hit role facets the W3 taxonomy was **not** tuned for. A graceful, role-appropriate result for them is a real **generalization** proof of the graph mechanisms *and* of W3 facet-taxonomy coverage; a generic fallback is a coverage gap to surface, not hide. (Runners-up with complete pairs — OpenAI Partner ADE, AIG VP Agentic AI, Citi Head of AI Strategy, Invesco Global Head Advanced Engineering — each overlap an existing corner; OpenAI is the best swap-in for a partnerships hold-out.)
- **The 2 live (Anthropic + Brown & Brown)** are the widest role-family gap of the shippable set, so they double as the cross-family generation-safety extremes. **Swappable** by the operator (e.g. Brown↔Truist) via the runner's `--target-*` args — changing the 2-live choice changes which band tables W5.0 authors, not the proof structure.

#### Hold-out discipline — what makes 5 worth more than 3 (mandatory for the generalization claim)

> 5 targets is a *generalization* proof only if ≥2 were **not** used to tune the graph. So: **freeze** the
> graph / facet / bundle config, then run #4 (Neo4j) + #5 (Aveva) **cold**. If their graph-% is role-appropriate
> and the variance is explainable **without any tuning**, the "you just overfit to 3 hand-picked targets"
> objection dies. If they need tuning to pass, **log it** — they become training points (not hold-outs) and the
> generalization claim weakens until 2 fresh cold targets are found. This freeze-and-run-cold step is a hard
> part of W3.1's spec (DoD-14).

#### Cost allocation — why 5 diagnostic / 2 live (the defense)

- The **selection diagnostic is ~free** (non-generation, seconds, zero LLM); a **live E2E is ~12 min + provider-rate-limited**. So the correctness proof rides the free surface at width 5; the expensive surface stays at width 2.
- **Stages A–D test target-agnostic mechanisms** (baseline, materialization, SSOT, facet weighting, typed-edge eligibility) — same code, different inputs → **run all 5 on the diagnostic** here; this is where the 5-way proof lives. No per-target artifacts needed.
- **Stages E0/E1 (sliding-scale) consume per-target hand-authored band tables + need generation** → only the **2 live** targets get band tables + live runs. The diagnostic carries band-table *selection correctness*; the live E2E proves *generation safety* — 2 (the extremes) cover it. (This **supersedes the earlier "3 live mandatory at sliding-scale"** — the free diagnostic now does the per-target band-correctness work for the targets that have tables.)
- **Infra cost of 5-vs-3 = zero:** the W3.1 `selection_diagnostic.py` runner (built regardless) is parameterized by target list; `[3]→[5]` is a config line.
- **Scoped claim (honest — do NOT overclaim the 3 diagnostic-only targets as "passing"):** *graph SELECTION correctness proven for 5 role families (2 held-out, run cold); 2 proven END-TO-END through generation + DOCX + sliding-scale enforcement.*
- **Safety valve:** if any held-out (or Truist) shows a **material, target-specific** anomaly (|Δ|≥3pp on a cell the others don't exhibit), promote it to a live run at that stage rather than trusting the diagnostic.

**Required at EVERY waterfall stage (A captured, B, C, D, E0, E1) — not deferred to W5:**
1. **graph-skill % × 11 lanes**, broken out by dimension: role family · role facet · pillar · source-fact-family · employer scope · metric type — for **5 targets at A–D**, **2 live targets at E0/E1**.
2. **Per-step variance**: each stage diffed against (a) the immediately-prior stage AND (b) immutable Stage A (`artifacts/w1/`), per target, per lane — top added / removed / promoted / demoted graph skills, each tagged expected/unexpected.

**Two-tier production (code-grounded):**
- **Authoritative (assembly-based):** `tools/apps_rg/graph_skill_utilization_report.py` — **requires `final_resume_assembly/final_resume.json` (verified: raises without it)**, so it yields a target's full graph-% only once that target reaches 11/11. Anthropic gets this at Stage B (W2.3); both live targets at Stage E1 (W5.4).
- **Cheap every-stage (selection-based) — the lever that keeps this affordable for 5 targets at every stage:** the **W3.1 `tools/apps_rg/selection_diagnostic.py` runner MUST emit the per-lane graph-skill % breakout (all 6 dimensions) for the in-scope targets directly from selection/traversal artifacts (proof-pool / selected-graph-evidence), WITHOUT full generation or assembly.** Non-generation (≈ seconds, zero LLM) → the matrix + variance is produced at every stage without N× full generation.

**Consequence for the build order:** the selection-based graph-% diagnostic is a hard W3.1 deliverable (not optional), and it is what makes the 5-target evidence requirement compatible with the 2-live cost rebaseline. The 2 live E2Es confirm X3 gates + DOCX for the ship targets; the **graph-% correctness evidence for all 5 targets comes from the cheap diagnostic at the same stage.** W5.4 then assembles the full A→E1 variance report.

#### Calculation intervals — compute at EVERY stage boundary (7 capture points)

Compute the matrix at **A, B0, B, C, D, E0, E1** — not a subset; the proof is the variance *pattern*, and two stages are **zero-variance controls** whose job is to show no movement. Skipping any stage breaks the causal chain. **Target coverage:** 5 diagnostic targets at A–D (the target-agnostic mechanism stages — where the 5-way generalization proof lives); 2 live targets at E0/E1 (the per-target band-table stages). The diagnostic is non-generation so 5-wide costs ≈ seconds.

| Stage (wave) | Causal change | Diagnostic targets | Expected variance vs prior |
|---|---|---|---|
| **A** (W1) | baseline | 5 (back-filled) | — (reference; `artifacts/w1/`) |
| **B0** (W2.0/1) | metric_outcome materialization | 5 | **~0 — CONTROL** (no-effect proof) |
| **B** (W2.3) | GraphDB SSOT + 4 lane fixes | 5 | only on fixed/blocked lanes (ibm_bullets, headline, exec_summary); neutral elsewhere |
| **C** (W3.2) | role-family / facet targeting | 5 (incl. 2 held-out, run cold) | **deliberate per-target re-weighting** — the key positive signal; held-outs prove generalization |
| **D** (W4.2) | typed proof/traversal edges | 5 | eligibility blocks/admits where typed edges bite |
| **E0** (W5.2) | sliding-scale dry-run | 2 live | **~0 — CONTROL** (diagnostics only) |
| **E1** (W5.4) | sliding-scale active enforcement | 2 live | rebalancing toward the per-target threshold bands |

#### Output format (canonical — emit per stage, markdown + JSON sidecar)

**Cell metric** = lane graph-skill coverage % = `selected graph-skill terms ÷ total selected terms` for that lane×target (the "is the graph driving this lane" number; per memory, most lanes were historically fact-only ≈ low %). Optional cell suffix = dominant graph-skill family. The full **6-dimension** breakout (role family · role facet · pillar · source-fact-family · employer scope · metric type) lives in the JSON sidecar per cell. Lane column keys (fixed order): `comp` competencies · `u_bul` unify_bullets · `ibm_bul` ibm_bullets · `it_bul` insurtech_bullets · `ey_bul` ey_bullets · `u_nar` unify_narrative · `ibm_nar` ibm_narrative · `it_nar` insurtech_narrative · `ey_nar` ey_narrative · `exec` executive_summary · `head` headline.

**(1) Per-stage matrix — 5 resume rows at A–D / 2 live rows at E0–E1 × 11 lane columns** (held-out rows flagged `†`):

```markdown
Stage <X> (<wave>) — graph-skill coverage % by lane × target
| Target | comp | u_bul | ibm_bul | it_bul | ey_bul | u_nar | ibm_nar | it_nar | ey_nar | exec | head |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Anthropic        |  |  |  |  |  |  |  |  |  |  |  |
| Brown & Brown    |  |  |  |  |  |  |  |  |  |  |  |
| Truist           |  |  |  |  |  |  |  |  |  |  |  |
| Neo4j (PM) †     |  |  |  |  |  |  |  |  |  |  |  |
| Aveva (dist-IC) †|  |  |  |  |  |  |  |  |  |  |  |
```
At **E0/E1** this collapses to the **2 live rows** (Anthropic, Brown & Brown) only — the other 3 are diagnostic-only and stop at Stage D.

**(2) Per-stage variance — Δ vs prior stage / Δ vs Stage A (percentage points), + expected verdict:**

```markdown
Variance Stage <X> vs <prior> (Δpp) / vs A (cum) — material = |Δ| ≥ 3pp
| Target | comp | u_bul | ibm_bul | it_bul | ey_bul | u_nar | ibm_nar | it_nar | ey_nar | exec | head |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Anthropic        | Δ/cum | … |  |  |  |  |  |  |  |  |  |
| Brown & Brown    |  |  |  |  |  |  |  |  |  |  |  |
| Truist           |  |  |  |  |  |  |  |  |  |  |  |
| Neo4j (PM) †     |  |  |  |  |  |  |  |  |  |  |  |
| Aveva (dist-IC) †|  |  |  |  |  |  |  |  |  |  |  |
| **Expected?**    | ✓/✗ + one-line reason for each material (|Δ|≥3pp) cell, tied to this stage's single causal change | … |
```
**Hold-out reading (C onward):** a held-out row (`†`) whose material deltas are role-appropriate and explainable *without tuning* = generalization confirmed; an unexplained held-out delta the tuned rows don't show = a graph defect the 3 tuned targets masked (high-value catch).

**Rules:** every **material** cell (|Δ| ≥ 3pp) needs an explicit expected/unexpected verdict in the `Expected?` row tied to *this stage's one causal change*; an unexplained material delta is a **regression until explained or reverted** (waterfall atomicity). Control stages (B0, E0) must show **all cells ≤ |3pp|** — any material movement there is a no-effect-violation. The `Expected?` row is per-target where targets diverge (split per-target — up to 5 sub-rows at A–D, 2 at E0/E1).

**(3) Illustrative (Stage A, from the retired W1 3-target run — aggregate family mix, shown to anchor the shape, not lane-level):** Anthropic partnerships-ecosystem 27.9% / enterprise-tech-delivery 24.8% / agentic-AI-governance 18.5%; Truist agentic-AI-governance 37.0% / enterprise-tech-delivery 30.4%; Brown & Brown cloud-data-platform 28.1% / enterprise-tech-delivery 24.9%. The W3.1 diagnostic produces this **per lane** (11 cells/target), not just aggregate.

### Prerequisites — corrected status (verified in code)

| ID | Prereq | Status |
|---|---|---|
| P1 | Replay harness | 🟡 **IN MAIN**, competencies-only; extend per-lane |
| P2 | Provider/judge concurrency + backoff | ⚠️ **NOT an apps_rg blocker** (elevated ceilings; lock was the real serializer, now removed). Real scope = **agent fan-out** throttle only |
| P3 | Intra-run lane concurrency | ✅ **DONE-IN-MAIN** (PR #325; lock removed) |
| P4 | Multi-target launcher (W5) | ❌ GAP — ~20-min W5 optimization, not a blocker |
| P5 | Agent fan-out for offline build | ❌ not started; stagger ≤2-3 (server-rate-limits concurrent agents) |
| P6 | Worktree runtime junctions + `.env` | ✅ done |
| P7 | Measured A/B speedup | ✅ **DONE** (1.96×) |

**Immediate next action:** one ~12-min baseline E2E on main → confirm the lane board + capture raw outputs → fix ibm_bullets / headline / exec_summary (validate offline via replay) → one 11/11 confirm E2E → build DOCX. That is the first finished resume.

---

## Context (SCQA)

- **Situation** - `apps_rg` already has an augmented skills graph with role-family inference, track weights, bridge edges, section projection, and senior-role fixtures. The Anthropic partner applied-AI fixture correctly identifies partner applied AI architecture, hyperscaler GTM, partnerships GTM, AI solutions architecture, and customer adoption signals.
- **Complication** - If traversal sources only approved partner skills and partner metrics, the selected skill pool becomes ATS-heavy and overfit before generation. Final text anti-overfit checks are too late when graph traversal has already created an over-concentrated proof pool.
- **Question** - How do we redesign traversal so role-family granularity improves targeting without replacing typed proof edges, without keeping `candidate_fact` or `fact_ledger` as competing skills or metrics authority, and without losing cross-role signal diversity?
- **Answer** - First run a P0 pre-flight that removes or fences `candidate_fact` as a runtime authority while preserving compatibility aliases for historical lineage. Then run the controlled waterfall: certify finalized graphs without typed edges, materialize first-class `metric_outcome` nodes as a pre-B GraphDB authority gate, remove `fact_ledger` authority in favor of GraphDB SSOT, add role-family facets, add typed edges, then add sliding-scale percent composition. Every material change must have its graph-% evidence (the free 5-target selection diagnostic, 2 of them held-out/run-cold, at stages A–D; the 2 live ship targets at E0/E1) plus a live E2E (single chosen resume x 11 generated lanes for W1–W4; the 2 live ship targets at W5), compare against immutable Stage A and the immediately prior stage, and explain whether variance is expected.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| P0 | P0.1, P0.2, P0.3 | Candidate-fact deprecation and test gate | ~12K | GraphDB can expose equivalent fact/proof/source identifiers or fail closed where missing | DONE | `candidate_fact` authority is deprecated and tested before W1 starts |
| W1 | W1.1, W1.2 | Finalized graph baseline without typed edges | ~14K | Current graph receipts, fixtures, and E2E command path are discoverable | DONE | Met current-substrate-passable bar 2026-06-13: 5 lanes X3_ALLOW (unify_bullets, insurtech_bullets, ey_bullets, insurtech_narrative, ey_narrative); 6 lanes deferred to W2 with blocker ledger; durable Claude-era ctx/output config landed in code defaults (32768 ctx / 4096 output / 8192 hard cap). Full 11/11 successful E2E is the W2 exit gate. |
| W2 | W2.0, W2.1, W2.2, W2.3 | Pre-B metric-outcome materialization, GraphDB SSOT, graph-era runtime field migration, and `fact_ledger` reference removal | ~24K | GraphDB can expose all skills, metrics, and metric outcomes needed by generation before Stage B E2E | IN_PROGRESS | W2.0 ✅ (metric_outcome merged in main) · W2.1 ✅ (B0 E2E ran) · W2.2 🟡 (competencies lane ✅ X3_ALLOW merged; ibm_bullets/headline/exec_summary open) · W2.3 ⏳ (11/11 exit gate → first finished resume) |
| W3 | W3.1, W3.2 | Role-family and role-facet targeting | ~18K | Role facets can be implemented as targeting weights over eligible graph paths | TODO | **DIAGNOSTIC-ONLY (tiered gate policy):** 5-target graph-% diagnostic (2 held-out, cold) shows role-family variance without partner-only overfit + offline replay on touched lanes. No full live E2E (single-lane spot-check only if a prompt/model input changed). |
| W4 | W4.1, W4.2 | Typed GraphDB proof/traversal edges | ~20K | Typed edges can be layered over the GraphDB SSOT without changing app/core boundaries | TODO | **DIAGNOSTIC-ONLY (tiered gate policy):** 5-target diagnostic shows typed edges explain eligibility + block unsupported paths + offline replay on touched lanes. No full live E2E. |
| W5 | W5.0, W5.1, W5.2, W5.3, W5.4 | Per-target threshold authoring, sliding-scale dry-run, active enforcement, anti-overfit guardrails, and waterfall closeout | ~31K | Composition metrics can be emitted before prompt assembly and enforcement can be toggled independently from diagnostics | TODO | Both live-target threshold tables (Anthropic + Brown & Brown) exist before W5.1; dry-run and active-enforcement E2E each cover the 2 live targets × 11 lanes (22-lane) and isolate sliding-scale behavior against W1 and prior stage |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| P0.1 | Inventory and classify `candidate_fact` usage before W1 | DONE |
| P0.2 | Deprecate or fence `candidate_fact` authority | DONE |
| P0.3 | Run candidate-fact deprecation tests and block W1 on failures | DONE |
| W1.1 | Resolve canonical E2E commands, target fixtures, and baseline graph receipts | DONE |
| W1.2 | Run single-resume successful E2E without typed edges (Stage A gate) | DONE (current-substrate-passable; 6 lanes deferred to W2 — see W1 Blocker Ledger) |
| W2.0 | Materialize first-class `metric_outcome` nodes only | DONE (merged in main) |
| W2.1 | Run pre-B metric-outcome E2E and prove behavior-neutral materialization | DONE (B0 E2E `artifacts/w2_b0/`; structural no-effect proof) |
| W2.2 | Migrate graph-era runtime fields and fence `fact_ledger` / proof-pool authority | IN_PROGRESS (alias layer + competencies lane DONE in main; ibm_bullets/headline/exec_summary open — see lane board) |
| W2.3 | Run GraphDB SSOT Stage B E2E and explain variance from B0 and W1 (= 11/11 exit gate → first finished resume) | TODO |
| W3.1 | Introduce reusable role-family facets and target alignment diagnostics | TODO |
| W3.2 | Run role-family E2E and explain variance from W2 | TODO |
| W4.1 | Implement typed GraphDB edge contracts for proof, traversal, and targeting | TODO |
| W4.2 | Run typed-edge E2E and explain variance from W3 | TODO |
| W5.0 | Author the live-target threshold table for Brown & Brown (Anthropic exists; Truist deferred unless swapped into the 2-live set) | TODO |
| W5.1 | Implement sliding-scale diagnostic calculations behind a dry-run flag | TODO |
| W5.2 | Run sliding-scale dry-run E2E and explain variance from W4 and W1 | TODO |
| W5.3 | Enable active sliding-scale enforcement and pre-prompt rebalancing | TODO |
| W5.4 | Run active sliding-scale E2E, produce waterfall analysis, and update Notion closeout | TODO |

### Rebaselined Effort Model (replay + parallelization, 2026-06-13)

> Status corrected against merged main (see "## Rebaselined Waterfall — Current Main"): **P3 + P7 are DONE-in-main** (parallel executor merged, 1.96× measured). Remaining open gaps: **P4** (W5 launcher) and **P5** (agent fan-out). **P2 is NOT an apps_rg blocker** (agent-layer only).

**Three forces reshape the remaining cost:**
1. **Deterministic replay** cuts the *number* of live API calls — post-generation work (binding, backfill, gate logic, typed-edge contracts, diagnostics, field-renames) validates offline via `tools/apps_rg/replay_section_gates.py` (zero API). Only pre-generation changes (prompt/evidence/selection) and the per-stage gate confirmation need a live call.
2. **Parallelization** cuts *wall-clock* of the calls that remain — intra-run lane concurrency (P3), GPU fp16 embedding, concurrent multi-target runs at W5 (P4), and agent fan-out for the offline build (P5).
3. **Serial waterfall (irreducible)** — stages B→C→D→E1 each compare against the prior stage, so the live confirmations cannot overlap each other; parallelism compresses work *inside* a stage and lanes *inside* a run only.

**Rebaselined remainder:**

| Block | Offline (agent-parallel, ~0 API) | Live API | Est. wall-clock (live, MEASURED parallel) |
|---|---|---|---|
| Stage B / W2.3 | ibm_bullets metric_outcome wiring · headline lineage · exec_summary alias · `fact_ledger` fence (replay-validated) | 1 batched 11/11 E2E | **~12 min** (measured 11.7 min, parallel executor in main) |
| Stage C / W3 | `role_facet_contract` · `selection_diagnostic` runner · neg-tests · **5-target** smoke (non-gen, 2 held-out cold) | 1 single-resume E2E | ~12 min |
| Stage D / W4 | 7 typed-edge contracts · traversal packet · tests · **5-target** smoke (non-gen) | 1 single-resume E2E | ~12 min |
| Stage E0 / W5.2 | dry-run diagnostic engine · 2 threshold tables (Anthropic + Brown) · **E0 = replay of Stage D** | 0 | replay |
| Stage E1 / W5.4 | active-enforcement engine · waterfall report | 1 × 22-lane (2 live targets) | ~12 min if P4 launcher (2 concurrent), else ~24 min (2 sequential) |

**Live-API floor = 4 sequential E2Es (~50-70 min total, measured-parallel)** — not the estimated ~8-min figure (corrected upward by the measured 11.7 min) and not the pre-parallel ~4 h. The dominant remaining work is the **offline build**, parallelizable across agents on local compute. Net: roughly **1–2 focused sessions**, gated by the 4 serial live confirmations, not by the API loop. **First finished Anthropic resume lands at the end of Stage B (W2.3).**

---

## Out Of Scope

- Manually editing generated resume text to hide graph behavior.
- Promoting DRAFT, INTERNAL_ONLY, LOW, or directional skills to external claims.
- Treating JD or briefing text as proof.
- Replacing typed edges with granular role families in the final architecture.
- Adding company-specific edge types such as `anthropic_partner_supports_skill`.
- Implementing `agentic_core` runtime `EdgeContract` handoffs between U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, or L6.
- Changing runtime handoff authority outside `apps_rg` resume generation.
- Changing `agentic_core`.
- Removing `master_skills_arsenal_ledger.json` as a serialization, export, bootstrap, or review artifact. This plan may fence it behind the `augmented_skills_graph` authority interface, but DB-only persistence migration is not part of W2 closure.
- Implementing ADG-style graph-skill materialized views, Redis hot projections, or GraphDB Lite/NetworkX projections as production runtime dependencies before W5 closeout. Read-only/offline analysis is allowed only under the Post-Waterfall Graph Projection Recommendation.
- Applying evidence-strength, metric-strength, recency, confidence, or capability-depth as active ranking multipliers before a separate post-Stage-B ranking waterfall gate. W2 may emit evidence-strength and metric-strength as diagnostics only; selection behavior changes require a later authorized stage with its own full E2E run.
- Using `capability_depth` as a proof substitute. It may be introduced only after W2 as a diagnostic or role-facet input in its own tested delta, and it cannot satisfy proof, provenance, or claim eligibility.
- Adding first-class `ResumeBullet` nodes to the core graph. Bullet scoring and generated-output history remain downstream of role-episode bundles and section outputs for this plan; any core-graph bullet-node scope belongs after this waterfall or in a separate downstream plan.
- Weakening final text anti-overfit, X2, X1D, or C0 evidence discipline.

---

## Architecture Position

The final hierarchy is:

1. GraphDB skills and metrics SSOT.
2. Typed proof, provenance, employer, capability, and section eligibility edges.
3. Role-family and role-facet targeting weights.
4. Sliding-scale percent composition policy.
5. Anti-overfit traversal guardrails.
6. Resume section generation.
7. Final text lint and judge checks.

Role family is a consumer of the graph, not the graph authority. Typed edges answer "is this allowed and why?" Role facets answer "how much should this eligible area matter for this JD?" Sliding-scale percentages answer "is the final selected pool balanced enough for this target without overfitting?"

The implementation order deliberately runs role-family E2E before typed-edge E2E to isolate its effect in the waterfall. That does not make role family the authority layer. The final architecture still requires typed edges to control proof and eligibility.

---

## Hardening Rules

### Typed Edge Scope Clarification

In this plan, "typed edges" means GraphDB proof/traversal edges used by `apps_rg` resume generation:
- proof edges
- provenance edges
- employer edges
- capability edges
- section eligibility edges
- targeting edges
- facet edges

This plan does not implement `agentic_core` runtime `EdgeContract` handoffs between U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, or L6. Runtime handoff authority remains out of scope.

### Authority Stack Invariant

```text
targeting_weight <= section_eligibility <= claim_eligibility <= proof <= provenance <= GraphDB SSOT
```

A lower layer may narrow, rank, demote, or block. A lower layer may not admit a skill, metric, or claim that the higher authority layer did not allow.

### Waterfall Atomicity And E2E Gate

The waterfall is valid only when every stage isolates one causal change. Do not batch materialization, authority migration, ranking behavior, role facets, typed edges, sliding-scale diagnostics, or active enforcement into the same untested delta.

Required atomic stages:
- **A** - immutable Post-P0 finalized graph baseline.
- **B0** - first-class `metric_outcome` materialization only; schema/materialization/resolver validation, no selection or ranking effect.
- **B** - GraphDB SSOT migration: graph-era field preference, proof-pool transport/cache boundary, and `fact_ledger` skills/metrics authority removal.
- **C** - role-family and role-facet targeting over already eligible graph paths.
- **D** - typed GraphDB proof/traversal edges.
- **E0** - sliding-scale diagnostics dry-run only.
- **E1** - active sliding-scale enforcement and pre-prompt rebalancing.

No stage may start until the previous stage has its accepted E2E artifact set — per the **E2E Resume-Count Gate Policy** (see "Mandatory E2E Matrix And Waterfall"): for stages A, B0, B, C, D this is ONE chosen resume completing a *successful* E2E (all 11 generated lanes `X3_ALLOW`, resume assembles) plus the non-generation 5-target graph-% diagnostic; for stages E0 and E1 it is the 2 live ship targets × 11 lanes (22-lane) — or an explicit blocker ledger for every unrun lane. Materialization-only or diagnostics-only stages must prove selected skill IDs, selected metric IDs, ranking order, prompt-input hashes, lane status, and generated-output hashes are unchanged wherever generation occurs (generated-output-hash parity is required only under the **Deterministic / Replay Rule For No-Effect Stages** below; otherwise prompt-input + selected-evidence + ranking + lane-status parity is the no-effect proof). Any unexpected difference is a regression until explained or reverted.

Every stage artifact must include a change manifest naming the exact runtime/config/schema changes under test. If a change is not named in that manifest, it cannot be claimed as closure evidence for that stage.

### Deterministic / Replay Rule For No-Effect Stages

`metric_outcome` materialization (B0) and sliding-scale dry-run (E0) claim "no selection/ranking/output effect." Because generated lanes call a non-deterministic LLM provider, identical prompt inputs can still yield different generated text, so a raw generated-output-hash diff would fail for the wrong reason. For B0 and E0 the no-effect proof MUST use exactly ONE of:
- **(a) Replay** — replay frozen provider responses captured from the comparison stage (Stage A for B0; Stage D for E0). With replay, generated-output-hash parity IS required.
- **(b) Deterministic / mock generation** — run B0/E0 with deterministic or mock generation so output is reproducible. Output-hash parity IS required.
- **(c) Input-parity fallback** — if neither replay nor deterministic generation is available, output-hash parity is NOT required; the binding no-effect proof is instead **prompt-input hash + selected-evidence (skill/metric ID set) hash + ranking order + lane status** all unchanged.

The change manifest MUST name which of (a)/(b)/(c) was used. A no-effect stage may NOT be failed on a generated-output-hash mismatch alone unless replay or deterministic mode (a)/(b) was in force.

### Proof Pool Runtime Boundary

`proof_pool`, `proof_pool_resolver`, and any allowed-pool metadata are not a second SSOT. They are runtime transport/cache surfaces for the selected GraphDB-approved evidence set. Their only valid job is to carry forward `selected_graph_evidence_plan`, `allowed_graph_evidence_ids`, selected graph node IDs, selected graph edge IDs, and selected graph metric IDs so validators and generation can enforce the allowed set.

During W2.2, keep proof-pool plumbing only as a compatibility surface while migrating consumers to graph-era names. It may narrow, deduplicate, group, or explain GraphDB-approved evidence. It may not create proof, repair missing graph paths, admit fact-era IDs as authority, or preserve `candidate_fact`, `fact_ledger`, `source_fact_ids`, or `allowed_fact_ids` as proof authority. If a proof-pool row cannot resolve to GraphDB-authorized evidence, traversal fails closed with `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict.

Do not remove or broadly rename proof-pool plumbing as a standalone pre-W2 cleanup. The controlled implementation point is W2.2, before W2.3 Stage B E2E, so any behavior change is captured in the GraphDB SSOT waterfall delta.

### No Silent Fallback Rule

If GraphDB lacks a required skill, metric, proof edge, employer edge, provenance edge, or section edge, traversal must emit `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict. It may not infer, synthesize, or backfill eligibility from JD text, briefing text, generated text, `candidate_fact`, `fact_ledger`, prompt context, or historical output.

### Canonical Traversal Verdicts

Allowed verdicts:
- `SELECTED`
- `DEMOTED`
- `BLOCKED_UNPROVEN`
- `BLOCKED_SECTION`
- `BLOCKED_EMPLOYER_SCOPE`
- `BLOCKED_PROVENANCE`
- `BLOCKED_CANDIDATE_FACT_AUTHORITY`
- `BLOCKED_FACT_LEDGER_AUTHORITY`
- `REBALANCE_REQUIRED`
- `MISSING_GRAPH_PATH`
- `DIAGNOSTIC_ONLY`

Unknown verdicts fail closed.

### Required Negative Tests

- `high_role_facet_weight_cannot_select_unproven_skill`
- `jd_keyword_cannot_create_proof_or_provenance`
- `section_block_overrides_high_facet_weight`
- `missing_supporting_fact_blocks_claim_eligibility`
- `missing_employer_binding_blocks_employer_scoped_claim`
- `candidate_fact_runtime_authority_read_fails_closed_before_W1`
- `fact_ledger_runtime_skill_read_fails_closed_after_W2`
- `linked_metric_outcome_id_must_resolve_to_graph_metric_outcome_after_W2`
- `metric_outcome_materialization_does_not_change_selection_before_B0`
- `stage_b0_e2e_artifacts_must_cover_all_target_lanes`
- `each_waterfall_stage_requires_prior_and_stage_a_diff`
- `diagnostic_only_stage_preserves_prompt_inputs_and_ranking`
- `strength_diagnostics_do_not_change_selection_before_ranking_stage`
- `typed_edge_missing_path_blocks_selected_skill_after_W4`
- `over_concentrated_pool_blocks_prompt_assembly_after_W5`
- `repeated_metric_family_triggers_rebalance`
- `target_company_name_cannot_be_claimed_as_experience`
- `capability_depth_cannot_satisfy_proof_or_claim_eligibility`
- `resume_bullet_nodes_cannot_enter_core_graph_before_waterfall_closeout`
- `facet_weight_changes_rank_only_within_graph_eligible_pool` (positive test — facet weights re-rank only inside the GraphDB-eligible pool, never admit a skill or import a JD term)

### Prompt-Hack Exclusion

Prompt-only fixes are not valid closure evidence. Changing prompt wording, examples, or anti-overfit text without changing traversal diagnostics and enforcement does not satisfy W3, W4, or W5.

---

## Candidate Fact P0 Recommendation

**Recommendation: move `candidate_fact` authority deprecation and testing to P0 before W1 starts.**

This should be a pre-flight deprecation and test gate, not a broad physical deletion. P0 should deprecate or fence `candidate_fact` as a runtime source of skills, metrics, proof, claim eligibility, section eligibility, or weighting. Historical identifiers may remain temporarily as compatibility aliases or lineage fields only when they point to GraphDB-backed fact nodes and cannot admit anything.

**Why P0 is the right timing**:
- W1 is supposed to be the clean finalized-graph baseline. If `candidate_fact` can still influence proof or eligibility, the baseline measures legacy substrate noise instead of graph behavior.
- Removing it after W1 would create avoidable waterfall variance that is not about role family, typed edges, or sliding-scale policy.
- P0 keeps W2 focused on `fact_ledger` storage/source cleanup instead of mixing two authority migrations in one E2E delta.
- GraphDB SSOT should be true before the first all-lane baseline; otherwise later graph-skill percentage breakouts can be contaminated by candidate-fact selection behavior.

**Why this is not a full destructive removal before W1**:
- Existing reports, validators, prompts, and legacy artifacts may still use `candidate_fact_id` as a lineage label.
- Deleting every field up front would expand blast radius and could block the plan on renaming churn rather than authority correctness.
- The needed P0 outcome is fail-closed authority behavior: any `candidate_fact` runtime read that would admit, prove, rank, or select must return `BLOCKED_CANDIDATE_FACT_AUTHORITY` or `MISSING_GRAPH_PATH` unless it resolves to a GraphDB-authorized path.

**Tradeoff accepted**:
- The plan loses a pre-P0 E2E comparison against legacy candidate-fact behavior. That is intentional. Legacy candidate-fact behavior is noise, not a useful waterfall stage. P0 should still emit a static inventory and targeted fail-closed test evidence so the removed noise is auditable.

---

## Fact Ledger Timing Decision

Remove `fact_ledger` authority only after the pre-B `metric_outcome` materialization E2E gate is accepted, and before role-family or typed-edge implementation.

**Why this timing is recommended**:
- W1 creates a clean control run against the current finalized graph, and B0 creates a narrow metric-outcome materialization control before the broader SSOT migration.
- Stage B prevents dual authority before role-family weighting or typed edges are introduced. Otherwise, a role-family or typed-edge regression could be masked by stale `fact_ledger` reads.
- GraphDB must be the only skills and metrics authority before traversal is made more powerful. Role facets and typed edges should operate on one source of truth, not arbitrate between GraphDB and ledger remnants.
- Any remaining claim-audit artifact must be renamed or fenced so it cannot be confused with skills or metrics authority. No runtime path may consult `fact_ledger` for skill eligibility, metric eligibility, weighting, proof, or traversal.

---

## Post-Waterfall Graph Projection Recommendation

**Recommendation: defer production implementation of ADG-style graph-skill materialized views, GraphDB Lite/NetworkX projections, Redis hot projections, and selector-manifest wiring until after W5 closes.**

During P0-W5, only read-only/offline exploratory artifacts are allowed. They may inspect copied waterfall outputs or graph snapshots, but they must not feed proof pools, C0/C0.3 receipts, traversal verdicts, packet generation, validators, prompt assembly, or waterfall pass/fail status.

**Defense**:
- P0-W5 is a causal waterfall. Each stage is supposed to isolate one source of variance: candidate-fact deprecation, GraphDB SSOT, role-family facets, typed edges, then sliding-scale composition. Adding a derived projection layer mid-waterfall would introduce a second variance source and weaken stage attribution.
- The authority boundary is already the core invariant: GraphDB / `augmented_skills_graph` is the skills and metrics SSOT; materialized views, GraphDB Lite projections, Redis keys, and manifests are derived receipts or projections. They may narrow, rank, explain, cache, or audit; they may not admit new skills, metrics, proof, or claims.
- Implementing the projection layer after W5 lets it reuse stable verdicts, breakout dimensions, artifact paths, row-count expectations, and variance categories proven by the waterfall instead of freezing intermediate contracts.
- The useful ADG pattern is the discipline, not the ADG schema: bounded materialized query surfaces, manifest row counts, fail-closed presence checks, and analyst artifacts. The `apps_rg` version should be purpose-built around section evidence candidates, allowed-pool closure, skill/fact support strength, hop paths, bundle skew, and utilization.

**Allowed before W5**:
- Design notes naming candidate `apps_rg` views and receipt fields.
- Offline reports that read existing graph snapshots or waterfall artifacts without changing runtime behavior.
- Static row-count or schema experiments that are clearly labeled non-authoritative and disposable.

**Not allowed before W5**:
- Runtime consumption of new graph-skill MVs, Redis projections, or NetworkX projections.
- Fallbacks from missing GraphDB proof into derived projections.
- Product proof, release claims, or pass/fail gates based on derived projection rows.

**Post-W5 candidate follow-up scope**:
- `mv_section_evidence_candidates`
- `mv_role_episode_bundle_rank`
- `mv_skill_fact_support_strength`
- `mv_allowed_pool_closure`
- `mv_hop_paths_by_fact`
- `mv_bundle_skew_diagnostics`
- A bounded graph-selection analyst artifact with selected/demoted/blocked/missing rows and row-count manifest.

---

## Mandatory E2E Matrix And Waterfall

> **E2E Gate Policy (operator amendment, 2026-06-15 — TIERED; supersedes the per-stage-live amendments of 2026-06-13 / 13B; governs this entire section).**
> Rationale: a full live 11-lane E2E at every stage (× targets) is wasteful (~12–25 min each + provider throttling + the Phase-1 concurrency race) AND the model-SSOT drift that cost days hid precisely because no *cheap per-stage* check ever compared intended-vs-actual. The fix is **cheaper per-stage gates + fewer full-live runs**, not fewer gates. Per-stage variance attribution is preserved via the $0 tiers below.
>
> **Four validation tiers — use the cheapest tier that proves the stage:**
> 1. **Offline replay** (`tools/apps_rg/replay_section_gates.py`, ~11s, zero API) — every post-gen / X2-gate / tail change; re-runs the deterministic tail + X2 gates on saved `raw_model_output.txt`.
> 2. **FREE 5-target selection diagnostic** (no LLM, zero API) — any stage whose effect is on *selection / traversal* (W3 role-family, W4 typed-edges); emits per-target/per-lane graph-% (6-dim) + selected/demoted/blocked/missing + per-step variance vs prior stage and immutable Stage A.
> 3. **Single-lane live run** (`python -m apps_rg --section <lane>`, ~1–2 min) — pre-gen / prompt / **model** changes; spot-checks one lane (e.g. `competencies`→Haiku, `unify_bullets`→Sonnet in `provider_request.json`).
> 4. **Full live 11-lane E2E** — reserved for exactly **TWO milestones**: **M1 = Stage B / W2.3** (first 11/11 `X3_ALLOW` once the graph substrate is fixed → first finished resume) and **M2 = W5 / E0+E1** (sliding-scale ship: the 2 live ship targets × 11 lanes). **No full live E2E at B0, C (W3), or D (W4).**
>
> **Per-stage gate map:**
> - **A (W1):** ONE current-substrate-passable live E2E (immutable baseline) + 5-target diagnostic. *(unchanged — A is the baseline anchor.)*
> - **B0 (W2.0/2.1):** offline replay + 5-target diagnostic + the no-effect parity proof (Deterministic/Replay rule). **No new full live E2E.**
> - **B (W2.3) = MILESTONE M1:** ONE full live 11-lane E2E reaching **11/11 `X3_ALLOW`** (single chosen target, default Anthropic) + 5-target diagnostic.
> - **C (W3) / D (W4): DIAGNOSTIC-ONLY** — gate = FREE 5-target selection diagnostic (graph-% + variance vs prior/A) + offline replay on any touched lane; a single-lane live spot-check is allowed only if a prompt/model input changed. **No full live E2E.**
> - **E0/E1 (W5) = MILESTONE M2:** the 2 live ship targets (Anthropic + Brown & Brown) × 11 lanes under sliding-scale enforcement.
>
> **Model-SSOT assertion (NEW gate — closes the drift that cost days):** the per-section generator model has ONE SSOT — `apps_rg/config/provider_profiles.yaml` (`external_claude_generator.default_model` Sonnet high-signal + `model_by_section` Haiku cost tier), resolved by `section_model_limits.resolve_section_generation_model(<lane>)`. Every live run's `provider_request.json` per lane MUST carry that resolved model; a mismatch is a stage FAIL. Enforced by `ops_scripts/ci/check_apps_rg_model_ssot.py` (static: no hardcoded `claude-*` model literal in apps_rg generation paths outside the SSOT) + the offline-replay model check.
>
> **Anti-loss / delivery discipline (NEW — the actual cause of the lost work):** each increment is committed + pushed and **auto-delivered to main** the same turn it passes its tier gate (`SCOPE_COMPLETE: branch=… tests=…` → `auto_deliver_on_scope_complete` → rebase→retest→push). Never park uncommitted work in a reap-prone worktree; pin the active worktree (`feat/*` + `.keep-worktree`) for the stage's duration.
>
> **Net:** full live E2E count drops from ~6–7 (per-stage) to **2 (M1 + M2)**; every other stage keeps a $0 gate so a regression surfaces in seconds with per-stage variance attribution intact.
> - **"Successful / 11-of-11 E2E"** = the integrated run assembles a complete resume with **all 11 generated lanes at `X3_ALLOW`** (no `X3_BLOCK`, no `PRE_RUN_BLOCKED` on a generated lane). A fail-closed *blocking* baseline does **not** satisfy a live gate.
> - **Progression gate:** a wave may not be marked complete, nor the next start, until its tier gate has passed with artifacts (A/B = live + diagnostic; B0/C/D = diagnostic + offline; W5 = both live ship resumes under enforcement).
> - **Default live target (A, M1):** `anthropic_partner_applied_ai` unless the operator selects another.
> - **W1 carve-out (operator decision, 2026-06-13).** At **W1 only**, "successful E2E" means **current-substrate-passable**: every lane that passes on the *existing* graph substrate reaches `X3_ALLOW` after the genuinely-W1 generation fixes (`executive_summary` schema/parse, narrative `forbidden_opener`). Lanes blocked **solely** on W2-scoped graph bindings (`bundle_id` / `graph_skill_node_ids` / `source_fact_or_graph_lineage`) or `metric_outcome` anchoring are **deferred to W2** with an explicit per-lane blocker ledger. The **full 11/11 all-lanes-`X3_ALLOW` successful E2E is the W2 / Stage B exit gate**, not W1. Rationale: 4 of 6 Anthropic W1 blockers (competencies-LLMOps, headline, unify-lineage, ibm_bullets metric-anchor) are exactly W2's graph-binding/`metric_outcome` work; requiring 11/11 at W1 would collapse W1↔W2 stage isolation. A fail-closed *blocking* baseline still does NOT satisfy W1.
> - **Reading the rest of this section:** wherever text below says "3 targets x 11 lanes" or "all 33 target-lane combinations" for stages **A, B0, B, C, D**, read it as **the single chosen resume's 11 lanes live (successful E2E) + the 5-target graph-% diagnostic (non-generation)**. For stages **E0 and E1**, read "3 targets / 33-lane" as **the 2 live ship targets × 11 lanes (22-lane)** — the 3-resume model is superseded by amendment 2026-06-13B.

The target roster (amended 2026-06-13B → **5 diagnostic / 2 live**; the cheap selection diagnostic runs all 5 at A–D, LIVE E2E runs only the 2 ship targets). Pre-W5 live gates run exactly ONE target (default Anthropic); W5 live = the 2 ship targets:

| Reader-facing target | JD + briefing stem (`apps_rg/config/targeting/`) | Tuned? | Role in test |
|---|---|---|---|
| Anthropic — Mgr Applied AI Architecture, Partnerships | `anthropic_manager_applied_ai_architecture_partnerships_*` | tuned | **LIVE + ship** |
| Brown & Brown — SVP IT Strategy & Innovation | `brown_brown_svp_it_strategy_innovation_*` | tuned | **LIVE + ship** |
| Truist — Head Agentic AI Engineering | `truist_head_agentic_ai_engineering_*` | tuned | diagnostic-only |
| Neo4j — VP Product Management, Agentic AI | `neo4j_vp_product_management_agentic_ai_*` | **held-out** | diagnostic-only (cold) |
| Aveva — Distinguished AI Tech Lead | `aveva_distinguished_ai_tech_lead_initiatives_*` | **held-out** | diagnostic-only (cold) |

Each target must run all 11 generated-content lanes from `apps_rg.runtime.section_execution_plan.GENERATED_CONTENT_LANES`:

| Order | Lane |
|---:|---|
| 1 | `competencies` |
| 2 | `unify_bullets` |
| 3 | `ibm_bullets` |
| 4 | `insurtech_bullets` |
| 5 | `ey_bullets` |
| 6 | `unify_narrative` |
| 7 | `ibm_narrative` |
| 8 | `insurtech_narrative` |
| 9 | `ey_narrative` |
| 10 | `executive_summary` |
| 11 | `headline` |

P0 is a prerequisite, not a waterfall stage. P0 must pass before W1 starts, and W1 Stage A is the first E2E run (single chosen resume x 11 generated lanes). This avoids spending baseline effort on known legacy candidate-fact authority noise.

Stage A is the immutable comparison baseline for this plan. Do not overwrite or reclassify Stage A artifacts after W1 is accepted. Every later E2E stage must compare against both the immediately prior stage and Stage A so the plan has one stable baseline plus stepwise causal attribution. B0 is a pre-B schema/materialization gate, not a ranking or selection stage.

The waterfall stages are (the **Validation Method** column is the 2026-06-13 rebaseline — replay/offline where the change is deterministic, live only for the stage-gate confirmation; see "## Parallelization & Replay Prerequisites" and "### Rebaselined Effort Model"):

| Stage | Required state | E2E requirement | Validation Method (rebaselined) |
|---|---|---|---|
| A | Post-P0 finalized graphs without typed edges | Run 1 chosen resume x 11 generated lanes (successful E2E — all lanes `X3_ALLOW`, resume assembles); typed edges disabled or absent; `candidate_fact` authority removed or fenced | ✅ DONE (live, `artifacts/w1/`) |
| B0 | First-class `metric_outcome` materialization only | Run 1 chosen resume x 11 generated lanes; compare to A; prove metric IDs resolve through GraphDB rows and prove no selection, ranking, prompt-input, generated-output, or lane-status effect except explicit fail-closed unresolved-metric blockers | ✅ DONE (live, `artifacts/w2_b0/`); structural no-effect proof |
| B | GraphDB SSOT with `fact_ledger` skills/metrics authority removed and graph-era runtime fields preferred | Run 1 chosen resume x 11 generated lanes; explain variance from B0 and A | **live-confirm ×1** — lane fixes replay-validated offline (`replay_section_gates.py`), then 1 batched 11/11 live E2E (lanes N-wide) |
| C | Role family and role facets enabled | Run 1 chosen resume x 11 generated lanes; explain variance from B and A (plus W3 cross-role non-generation diagnostic smoke run for all **5 targets**, incl. 2 held-out run cold) | **live-confirm ×1** (single resume) + **offline-smoke** (5-target diagnostic is non-generation) |
| D | Typed edges enabled | Run 1 chosen resume x 11 generated lanes; explain variance from C and A (plus W4 cross-role non-generation diagnostic smoke run for all **5 targets**) | **live-confirm ×1** (single resume) + **offline-smoke** (5-target diagnostic is non-generation) |
| E0 | Sliding-scale diagnostics dry-run enabled, enforcement disabled | Run the **2 live targets** x 11 lanes (22-lane); explain diagnostic-only variance from D and A; prove no pre-prompt blocking or ranking effect | **replay (Stage D)** — E0 is a declared no-effect stage; per the Deterministic/Replay Rule the 22-lane requirement is satisfied by replaying Stage D's frozen responses + computing diagnostics offline (input-parity proof). **0 live** |
| E1 | Sliding-scale active enforcement and pre-prompt rebalancing enabled | Run the **2 live targets** (Anthropic + Brown & Brown) x 11 lanes (22-lane); explain variance from E0, D, and A; prove concentration breaches produce `REBALANCE_REQUIRED` before prompt assembly | **live ×1** — the one genuinely-live 22-lane run; **2 ship targets** (concurrent via the multi-target launcher, prereq P4 — or serial) |

> **Rebaselined live-API floor = 4 sequential E2Es** (Stage B, C, D, E1). E0 is replay-validated; the W3/W4 5-target cross-role smokes are non-generation (offline); all post-generation lane fixes are validated offline via `tools/apps_rg/replay_section_gates.py` (zero API). Validation moving offline is a **cost reduction, not a rigor reduction** — the same X2 gates run, just without a live generation where the change is deterministic. The 4 live confirmations stay **serial** (waterfall atomicity: each compares against the prior stage).

Every run artifact must include:
- Target slug, briefing/resume input path, graph version, run id, stage id, lane id, and lane status.
- Change manifest naming exactly which schema, resolver, runtime, scoring, diagnostic, or enforcement changes were active.
- Feature flags or configuration proving which stage was active.
- `baseline_stage_id=A` plus immutable Stage A artifact references used for comparison. **Canonical Stage A artifact path = `artifacts/w1/`** (single-resume successful E2E captured with short `--artifact-dir` to avoid Windows MAX_PATH). All later stages reference this path verbatim.
- Graph skills percentage breakout by lane.
- Breakout dimensions for role family, role facet, pillar, source fact family, employer scope, and metric type.
- Selected, demoted, blocked, and missing skills with reasons.
- Selected skill IDs, selected metric IDs, ranking order, prompt-input hashes, lane status, and generated-output hashes for materialization-only and diagnostic-only no-effect proof.
- A variance rationalization versus both Stage A and the prior waterfall stage, including top added, removed, promoted, and demoted graph skills. **Carve-out: Stage A has no prior stage; for the Stage A artifact, the prior-stage variance section is N/A and the Stage-A-vs-prior-stage comparison is omitted.** Stage A's only required comparison is against P0 outcomes, which is qualitative (baseline creation) rather than a percentage delta.
- An expected/unexpected classification for each material variance.

A stage is not complete unless every required lane — the single chosen resume's 11 generated lanes (live) + the 5-target graph-% diagnostic for stages A, B0, B, C, D; the 2 live ship targets' 22 lanes for E0 and E1 — either passes or has an explicit blocker with blocker class, failed command, artifact path, and next action.

---

## Parallelization & Replay Prerequisites

> Added 2026-06-13, status corrected against merged main. **P3 + P7 are DONE-in-main** (parallel executor
> merged, 1.96× measured); **P2 is NOT an apps_rg blocker** (the lock was the serializer, now removed). The
> remaining **open gaps are P4** (W5 multi-target launcher) **and P5** (agent fan-out). The serial-waterfall
> constraint (B→C→D→E1 cannot overlap) is **irreducible** — no prerequisite removes it.

| ID | Prerequisite | Why required | Owner | Status |
|---|---|---|---|---|
| **P1** | Replay harness for all 11 lanes (`tools/apps_rg/replay_section_gates.py`) | each lane's post-gen fix validates offline (zero API) instead of a live regen | orchestration | 🟡 **IN MAIN**, competencies-only (1/11); extend per-lane |
| **P2** | Provider + judge concurrency + 429 backoff in `section_provider_call.py` / `section_judge_policy.py` | concurrent provider/judge calls | apps_rg runtime | ✅ **NOT an apps_rg blocker** — code-verified: the serializer was `_ENV_OVERLAY_LOCK` (now removed), provider ceilings are elevated (Claude 5000 RPM). Real scope = **agent fan-out (P5)** throttle only (6 concurrent agents were server-rate-limited) |
| **P3** | Intra-run lane concurrency (lock-free executor + manifest caps) | makes one E2E fast | apps_rg runtime | ✅ **DONE-IN-MAIN** (PR #325 / commit `06502b57f8`; `_ENV_OVERLAY_LOCK` removed, `default_max_parallel: 5`, wave-1 `max_parallel: 4`) |
| **P4** | Multi-target launcher (run the 2 live ship targets concurrently) | W5 E1 22-lane runs ~1× wall-clock instead of 2× | apps_rg runtime / ops | ❌ GAP (verified: no launcher in code) — ~20-min W5 optimization, not a blocker |
| **P5** | Agent fan-out (Workflow over the offline build) | parallelize the 3 W2.2 lanes + W3/W4 contracts + W5 tables; **server-rate-limits concurrent agents — stagger ≤2-3** | orchestration | ❌ not started (first attempt server-rate-limited) |
| **P6** | Worktree runtime junctions + `.env` (`data/cache/sparse` + `chromadb`) | any E2E fails closed without them | operator | ✅ done |
| **P7** | Measured A/B lane-parallel speedup | replaces the estimated ~8-min figure with the real number | sibling chat | ✅ **DONE — 1.96× (704s vs 1383s); use 11.7 min/E2E** |

**Dependency note:** P2 underpins P3/P4/P5 — concurrency without backoff is throttled, not faster. Close P2
before trusting any parallel speedup (including the A/B in P7 and the agent fan-out in P5).

---

## P0 - Candidate-Fact Deprecation And Test Gate

P0_STATUS: DONE
P0_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: P0

**Authorization**: REQUIRED - Candidate-fact authority deprecation can touch proof, selection, validators, prompts, and legacy artifact compatibility.

**Phases**:
- **P0.1** - Inventory and classify `candidate_fact` usage before W1 | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **P0.2** - Deprecate or fence `candidate_fact` authority | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **P0.3** - Run candidate-fact deprecation tests and block W1 on failures | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Allowed after P0**:
- `candidate_fact_id` as a compatibility alias or lineage identifier in historical artifacts.
- Adapters that translate legacy candidate-fact identifiers to GraphDB fact/proof nodes.
- Diagnostic output showing a legacy identifier and its GraphDB-backed path.

**Not allowed after P0**:
- Any `candidate_fact` runtime read that admits, proves, ranks, weights, or selects a skill, metric, claim, or section.
- Any fallback where missing GraphDB proof is filled from candidate facts.
- Any prompt context that treats candidate facts as proof independent of GraphDB provenance.

**Acceptance**:
- Static inventory classifies each live `candidate_fact` reference as allowed lineage/compatibility or disallowed authority.
- Disallowed authority paths are removed, renamed, or fail closed behind GraphDB lookup.
- `candidate_fact_runtime_authority_read_fails_closed_before_W1` passes.
- Missing GraphDB translation for a legacy candidate-fact identifier emits `MISSING_GRAPH_PATH` or `BLOCKED_CANDIDATE_FACT_AUTHORITY`.
- W1 cannot start until P0 deprecation and test evidence exists.

---

## Wave 1 - Finalized Graph Baseline Without Typed Edges

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES (current-substrate-passable bar; full 11/11 deferred to W2)
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - Command discovery, fixture resolution, and single-resume successful-E2E evidence collection only.

**Phases**:
- **W1.1** - Resolve canonical E2E commands, target fixtures, and baseline graph receipts | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Run single-resume successful E2E without typed edges (Stage A gate) | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES (current-substrate-passable; 6 lanes deferred to W2)

**Acceptance** (amended 2026-06-13 — single-resume successful-E2E gate; supersedes the prior blocking-baseline acceptance):
- P0 has passed, so `candidate_fact` cannot act as skills, metrics, proof, eligibility, selection, or weighting authority.
- Canonical fixture/input paths are resolved for the chosen single target (default `anthropic_partner_applied_ai`).
- W1 success = **current-substrate-passable** (operator decision 2026-06-13): every lane that passes on the existing graph substrate reaches `X3_ALLOW` after the genuinely-W1 generation fixes (`executive_summary` schema/parse + narrative `forbidden_opener`). Lanes blocked solely on W2-scoped graph bindings (`bundle_id` / `graph_skill_node_ids` / `source_fact_or_graph_lineage`) or `metric_outcome` anchoring are **deferred to W2** with a per-lane blocker ledger. The full 11/11 all-lanes-`X3_ALLOW` successful E2E is the **W2 / Stage B exit gate**, not W1. A fail-closed blocking baseline still does NOT satisfy W1.
- Typed edges are disabled, absent, or explicitly no-op in the baseline configuration.
- Artifacts show graph-skill percentage breakouts per lane for the chosen resume.
- The multi-target *live* matrix is NOT required at W1; live runs only the single chosen resume pre-W5 and the 2 ship targets at W5 (sliding-scale). The 5-target graph-% evidence is the non-generation diagnostic.
- (Reference only) The prior blocking-baseline run at `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/` is retained as historical context, not as W1 completion evidence.

**W1 baseline enablement rules** (what repairs are allowed before Stage A exists):
- **Allowed (does not taint the baseline):** command discovery, fixture path fixes, stale config correction, artifact plumbing / output-dir wiring, graph receipt discovery.
- **Conditionally allowed:** graph CONTENT fixes (missing graph paths, fixtures, validators) only if separately logged as **pre-A baseline-enabling debt** in the change manifest, each named so the captured Stage A is reproducible.
- **Not allowed:** selection / ranking / eligibility BEHAVIOR changes — unless Stage A is restarted from scratch and the change manifest names them. Any behavior change silently applied before capture invalidates the immutable baseline.

**W1 close-out artifacts** (full detail in the Cross-Wave Deferral Ledger section below): 5 lanes `X3_ALLOW` on current substrate, 6 lanes deferred to next-wave work, Stage A canonical artifact at `artifacts/w1/`, durable Claude-era ctx/output code defaults landed.

---

## Cross-Wave Deferral Ledger (W1 close → next-wave handoff)

W1 closes 2026-06-13 on the current-substrate-passable bar (operator decision). 5 of 11 lanes reach `X3_ALLOW` on the existing graph substrate; the remaining 6 are deferred to next-wave work because their blockers are squarely in the metric_outcome materialization + graph-era field migration scope. Each row records the *exact* failed X2 gate(s) and the next-wave phase that addresses it.

| Lane | Status | Failed X2 gate(s) | Root cause | Next-wave phase that resolves |
|---|---|---|---|---|
| `competencies` | X3_BLOCK | `competency_bundle_binding_missing`, `bundle_id_resolves`, `graph_skill_node_ids_present`, `generic_category_allowed`, `min_items_satisfied`, `colon_format_valid` | "LLMOps & Reliability" category has no graph bundle binding in the current `augmented_skills_graph`. Selection emits competencies that have no graph lineage. | Graph-era field migration phase (graph-era bundle binding + augmented_skills_graph authority resolution) |
| `unify_narrative` | X3_BLOCK | `source_fact_or_graph_lineage_present`, `bundle_id_resolves`, `graph_skill_node_ids_present` | Unify lane missing graph lineage / bundle binding for several selected skills. | Graph-era field migration phase (lineage resolver) |
| `headline` | X3_BLOCK | `source_fact_or_graph_lineage_present`, `positioning_bundle_id`, `graph_skill_node_ids_present`, `xyz_literal_grounded_in_briefing` | Headline missing source-fact/graph-lineage + positioning bundle. XYZ literal grounding fails because briefing-grounded fact attribution flows through fact-era IDs. | Graph-era field migration phase (headline lineage path) |
| `ibm_bullets` | X3_BLOCK | `ibm_metric_anchor_bullet_ownership` | No `metric_outcome` node bound to bullet — selected metric IDs are side-field references on role_episode bundles, not first-class graph rows. | Metric-outcome materialization phase (first-class `metric_outcome` materialization) |
| `ibm_narrative` | upstream_not_finalized | (cascade) | Cascade from `ibm_bullets` block — no lane-local failure. | Metric-outcome materialization phase (resolves automatically when `ibm_bullets` is unblocked) |
| `executive_summary` | X3_BLOCK | `source_fact_coverage_100`, `unsupported_claim_zero`, `claim_ledger_orphan_zero`, `material_clause_coverage_100`, `allowed_fact_utilization`, `metric_fact_id_granularity`, `sentence_coverage_pass`, `self_check_claim_ledger_consistent`, `section_claims_supported_by_base_resume`, `no_mechanism_inventory`, `north_star_style_echo_unsupported_zero`, `claim_coverage_accounting_consistent`, `input_usage_accounting_consistent` (13 gates) | All 13 are claim-grounding / evidence-coverage gates hung off `source_fact_ids`. The graph-era field migration renames `source_fact_ids` → `graph_evidence_ids` and re-anchors metric grounding on first-class `metric_outcome` graph rows. Iterating these gates at W1 against the fact-era substrate is rework — the next wave replaces the substrate. | Metric-outcome materialization + graph-era field migration phases. Generation-discipline residue (unsupported-claim avoidance) may carry into the Stage B E2E as a separate sub-blocker; assess after the field migration lands. |

**5 lanes that did pass on current substrate** (recorded for next-wave variance comparison):
- `unify_bullets` — X3_ALLOW
- `insurtech_bullets` — X3_ALLOW
- `ey_bullets` — X3_ALLOW
- `insurtech_narrative` — X3_ALLOW
- `ey_narrative` — X3_ALLOW

(InsurTech and EY are locked-deterministic per `apps_rg/AGENTS.md` § Locked deterministic copy; their `X3_ALLOW` reflects the locked path executing cleanly, not graph-skill exercise.)

**Stage A canonical artifact path**: `artifacts/w1/` (single-resume run for `anthropic_partner_applied_ai`, short `--artifact-dir` to dodge Windows MAX_PATH 260). All later stages reference this path verbatim.

**Stage A change manifest** (durable config fixes applied before W1 close; named per the W1 baseline enablement rules):
- `apps_rg/runtime/section_model_limits.py`: `SECTION_MODEL_MAX_MODEL_LEN` default `24576` → `32768` (Claude-era ctx SSOT; legacy Qwen value retained on `VLLM_MAX_MODEL_LEN` for apps_lic / agentic_core healers).
- `apps_rg/runtime/sections/executive_summary_context_limits.py`: `DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS` `2048` → `4096`; `DEFAULT_REGEN_MAX_OUTPUT_TOKENS` `2048` → `4096`; `HARD_CAP_SCRATCH_MAX_OUTPUT_TOKENS` `4096` → `8192`; `_DEFAULT_CONTEXT_WINDOW` `24576` → `32768`.
- `apps_rg/runtime/sections/executive_summary_context_limits.py:resolve_provider_context_window`: precedence flipped — `APPS_RG_SECTION_MAX_MODEL_LEN` (app-local) wins, `VLLM_MAX_MODEL_LEN` kept only as legacy fallback for backward compat.
- Test updates: `test_executive_summary_context_limits.py` + `test_executive_summary_token_budget_regen.py` reflect Claude-era defaults (13 tests pass).

These are env/budgeting/resolver fixes only — NO selection/ranking/eligibility behavior change. Stage A captured under these fixes remains the immutable baseline.

---

## Wave 2 - Metric Outcome Pre-B Gate And GraphDB SSOT

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Authorization**: REQUIRED - Any schema, traversal, validator, or runtime authority change must be explicitly reviewed before execution.

**Phases**:
- **W2.0** - Materialize first-class `metric_outcome` nodes only | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES (92 metric_outcome nodes + 452 edges materialized 2026-06-13)
- **W2.1** - Run pre-B metric-outcome E2E and prove behavior-neutral materialization | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES (first valid full-substrate B0 E2E 2026-06-13: 6 X3_ALLOW / 4 X3_BLOCK / 1 cascade; W2.0 no-effect proven structurally — see W2.1 note below)
- **W2.2** - Migrate fact-era runtime fields behind graph-era aliases and fence `fact_ledger` / proof-pool authority | ~8K tokens | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO (alias layer + competencies lane DONE; ibm_bullets/headline/exec_summary remaining)
  - **W2.2 lane-fix progress (authorized 11/11 sub-scope):**
    - ✅ **competencies** — X3_ALLOW live (2026-06-13). Fixes: required-family pack retention (`competency_capability_evidence._filter_packet_by_selected_graph_plan`), llmops bundle enrichment (4 graph skills + 5 anchors), prompt term-floor 2→3 + bundle-label pin (`competencies_pa.py`), graph-bundle min-term backfill with keyword-budget (`competencies_lane_runtime.backfill_graph_bundle_min_terms` + wired in `competencies_lane_execution`). Commits `5d1e814c3a` + unlock chain.
    - ⏳ **ibm_bullets** — root cause located: `ibm_bullets_graph_evidence.py:213` `has_metric=bool(metric_raw)` marks HELD metrics claimable; fix = approved-metric_outcome-only + graph-aware anchor gate.
    - ⏳ **headline** — positioning bundle + graph lineage + grounded XYZ literal.
    - ⏳ **executive_summary** — claim grounding via `graph_era_aliases` + generation discipline.
  - **#1 unlock built**: `tools/apps_rg/replay_section_gates.py` validates post-gen fixes offline in ~11s, ZERO API (harness verdict confirmed == live X3_ALLOW for competencies). Remaining lanes use: offline iterate → 1 confirming regen each.
  - Alias layer landed 2026-06-13: `apps_rg/runtime/graph_era_aliases.py` + 13 tests. Full 158-file fact-era surface migration deferred to follow-up wave.
- **W2.3** - Run GraphDB SSOT Stage B E2E and explain variance from B0 and W1 | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Pre-W2 cleanup status**:

| Cleanup | Status | Timing decision | Rationale |
|---|---|---|---|
| Metric SSOT derivation from graph JSON | DONE before W2 | Pre-waterfall baseline hardening complete | Low-disruption removal of hardcoded metric allowlists; W2 can assume metric approval comes from graph JSON `metric_outcome_nodes`. |
| First-class `metric_outcome` nodes in materialized GraphDB | OPEN | Execute in W2.0, then prove with B0 E2E in W2.1 before Stage B | W2 claims GraphDB is the skills and metrics SSOT. Metric outcomes may originate from graph JSON and role-episode bundle references, but Stage B should verify them as graph nodes/edges rather than side fields only. This is schema/materialization/validation only and must not change ranking or selection. |
| Generic employer bundle registry behind existing wrappers | DONE before W2 | Pre-waterfall baseline hardening complete | Existing imports keep working while all employer graph wrappers share loader/access/validation primitives. |
| Normalize graph JSON bundle schema | DONE before W2 | Pre-waterfall baseline hardening complete | All employer bundles share the common graph shape before W2 changes runtime contracts. |
| Rename fact-era runtime fields to graph-era fields | OPEN | Execute in W2.2 before Stage B E2E in W2.3 | Highest blast radius because `selected_fact_plan`, `allowed_fact_ids`, `source_fact_ids`, `fact_id`, and `candidate_fact_id` still cross validators, lanes, proof pools, prompt artifacts, and output schemas. Do not perform as an untracked cleanup or mix it with B0; make it a controlled Stage B compatibility migration with variance evidence. |
| Proof-pool authority boundary | OPEN | Execute in W2.2 before Stage B E2E in W2.3 | Keep proof-pool plumbing only as selected graph evidence transport/cache while consumers migrate. Do not delete or rename it as a standalone cleanup; prove it cannot admit, repair, or preserve proof outside GraphDB-approved IDs. |

**W2 SCOPE EXPANSION (operator-authorized 2026-06-13)**:

```text
DISCOVERED_SCOPE: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=W2 phase=W2.2 gap="W2.3 11/11 X3_ALLOW exit gate not reachable by graph-era field rename alone; 4 blocked lanes need graph-content authoring + ibm_bullets selection-correctness (held-metric mis-mark), the latter colliding with the W2 'B0/B no selection behavior change' invariant" impact="blocks W2.3 exit gate"
AUTHORIZATION_DECISION: plan=typed-edge-role-facet-guardrails-a6f3d2 decision=ACCEPTED authorized_by=user decisive_reason="operator chose 'Authorize lane fixes — pursue real 11/11' 2026-06-13; 11/11 Anthropic resume is the genuine goal, worth expanding W2 into graph-content authoring + selection-correctness"
SCOPE_EXPANSION: plan=typed-edge-role-facet-guardrails-a6f3d2 reason="W2 now includes the 4-lane unblock: competencies+headline graph bundle authoring, ibm_bullets selection held-metric correctness + graph-aware anchor gate, exec_summary claim-grounding via graph-era aliases" added="W2.2 lane-fix sub-scope" authorized="yes"
```

**Lane-fix sub-scope (authorized 2026-06-13, pursue 11/11):**
- `competencies` — author graph bundle binding for "LLMOps & Reliability" category (graph content).
- `headline` — author positioning bundle + graph_skill_node_ids lineage for selected content (graph content).
- `ibm_bullets` — selection must not mark HELD metrics (e.g. "$10M new ARR") as `has_metric=True`; anchor gate validates against approved `metric_outcome` graph rows (W2.0) rather than stale `IBM_METRIC_ANCHOR_RULES` tokens. This is the one fix that touches the selection layer — explicitly authorized despite the B0/B invariant; Stage B re-baselines to capture it.
- `executive_summary` — claim grounding via the W2.2 `graph_era_aliases` layer (`source_fact_ids`→`graph_evidence_ids`) + residual generation discipline.

**W2 causal split and implementation order**:

**W2.0 - Metric-outcome materialization only**:
1. Materialize first-class metric outcome graph rows before any Stage B authority migration:
   - `metric_outcome` node type or equivalent canonical graph row
   - edges from supporting facts, skills, role episodes, employers, and sections where available
   - resolver validation for every `linked_metric_outcome_ids` / `metric_outcome_nodes` reference emitted by role-episode bundles
   - fail-closed `MISSING_GRAPH_PATH` or `BLOCKED_*` verdict for unresolved metric outcome IDs
2. Keep this stage schema/materialization/validation only. Do not change skill selection, metric selection, ranking order, prompt assembly, generated text, role-family behavior, typed-edge behavior, sliding-scale behavior, `capability_depth`, or ResumeBullet modeling.
3. Emit evidence-strength and metric-strength only as report-only diagnostics where the existing data supports them. They may expose weak or missing paths, but they may not alter selection, ranking, prompt assembly, waterfall percentages, lane pass/fail, or generated text.

**W2.1 - B0 metric-outcome E2E**:
1. Run the single chosen resume's 11 generated lanes with only W2.0 changes active (multi-target *live* matrix is the 2 ship targets at W5; the 5-target graph-% diagnostic is non-generation).
2. Compare B0 to immutable Stage A and prove selected skill IDs, selected metric IDs, ranking order, prompt-input hashes, generated-output hashes, and lane status are unchanged wherever generation occurs.
3. Classify any new blocker as unresolved metric-outcome materialization debt, not as ranking or targeting variance.
4. B0 is not accepted until every `linked_metric_outcome_ids` / `metric_outcome_nodes` reference either resolves to a first-class GraphDB metric outcome row or fails closed with an explicit blocker artifact.

**W2.2 implementation strategy (operator-amended 2026-06-13)**:

Discovery: a worktree grep of `selected_fact_plan|allowed_fact_ids|source_fact_ids` across `apps_rg/runtime/**` returned **158 files** with 234 total occurrences — far beyond the plan's ~8K token estimate. A full simultaneous migration is impractical; the realistic path is a **two-layer cut**:

1. **Alias layer (foundational, all-or-nothing):** a new module `apps_rg/runtime/graph_era_aliases.py` defines the canonical fact-era ↔ graph-era field name mapping plus helpers to (a) emit both names side-by-side on a dict, (b) read either name with graph-era preferred. This is producer-side only — no semantic change.
2. **Targeted consumer migration (scope-cut to the W1 blocker ledger):** migrate only the consumers blocking the 6 W1-deferred lanes:
   - **exec_summary** — 13 fact-era gates depend on `source_fact_ids`; aliasing to `graph_evidence_ids` and updating the lane's `_claim_grounding_check` is the highest-leverage single change.
   - **ibm_bullets** — `_ibm_metric_anchors_on_assigned_bullets` to consult `metric_outcome` graph rows (via W2.0 `resolve_metric_outcome_graph_node`) when the canonical hardcoded anchor rules don't match.
   - **competencies** — LLMOps & Reliability category needs a graph bundle binding; either add bundle JSON or migrate the bundle resolver to accept the materialized graph row directly.
   - **unify_narrative + headline** — graph-lineage resolution via the alias layer.
3. **All other 158 - 5 = ~153 consumer files** stay on fact-era field names; the alias layer makes them functionally graph-era-aware because producers now emit both names. These files migrate in subsequent waves (W3+) as they become relevant, without blocking W2.3.

The full-migration end-state (all 158 files renamed to graph-era only, fact-era removed) is **deferred to a follow-up wave** — labeling it explicitly here so the W2.3 exit gate doesn't expand to require it.

**W2.2 - Graph-era runtime fields, proof-pool boundary, and `fact_ledger` fence** (original plan text below; the implementation strategy above scope-cuts step 2):
1. Introduce graph-era output names while preserving fact-era read aliases for compatibility:
   - `selected_graph_evidence_plan` beside `selected_fact_plan`
   - `allowed_graph_evidence_ids` beside `allowed_fact_ids`
   - `graph_evidence_ids` beside `source_fact_ids`
   - `graph_evidence_id` beside `fact_id`
   - `legacy_candidate_fact_id` only as lineage, never authority
2. Update validators, proof-pool metadata, and section packets to prefer graph-era names.
3. Treat proof-pool outputs as internal selected-graph-evidence transport/cache only; every retained row must resolve to GraphDB-approved node, edge, or metric IDs.
4. Keep fact-era fields as compatibility aliases until all generated lanes and X2/X1D gates read graph-era fields.
5. Remove or hard-fail any fact-era field or `fact_ledger` read that can still admit, rank, prove, or select a skill, metric, claim, or section.
6. Continue emitting evidence-strength and metric-strength as diagnostics only. They may explain selected, weak, blocked, or missing paths, but they may not alter W2.3 skill selection, metric selection, ranking, prompt assembly, waterfall percentages, lane status, or generated text.

**W2.3 - Stage B GraphDB SSOT E2E**:
1. Run the single chosen resume's 11 generated lanes with W2.0 and W2.2 changes active.
2. Compare B to B0 and immutable Stage A.
3. Attribute variance only to graph-era contract migration, proof-pool authority fencing, `fact_ledger` authority removal, or fail-closed missing GraphDB paths.
4. Any variance caused by evidence-strength, metric-strength, capability-depth, role facets, typed edges, ResumeBullet nodes, prompt changes, or active ranking behavior is out of stage and must be reverted or split into a later authorized waterfall stage.

**Authority rule**:

GraphDB is the SSOT for skills, metrics, skill eligibility, metric eligibility, graph traversal, and skill weighting. `fact_ledger` references must be removed, renamed, or fenced so they cannot act as a skills or metrics source of truth.

Selected skill references, including `selection_plan_skill_ref` values and lane-selected `skill_id` values, must resolve through the `augmented_skills_graph` authority interface. The current `master_skills_arsenal_ledger.json` file may remain as the backing serialization/export/bootstrap artifact for that authority, but it must not be named, queried, or reported as an independent skills authority.

Metric outcome references, including `linked_metric_outcome_ids` and bundle `metric_outcome_nodes`, must resolve to first-class GraphDB metric outcome rows before B0 is accepted. Role-episode bundle fields may carry references and summaries, but they are not the metric authority once B0 closes.

Allowed after W2:
- A clearly named claim-audit or generation-audit artifact that records what was emitted.
- Backward-compatible adapters that fail closed and delegate to GraphDB.
- JSON ledger artifacts only when labeled as non-authoritative serialization/export/bootstrap/review artifacts or hidden behind the `augmented_skills_graph` resolver boundary.
- Proof-pool plumbing only as an internal allowed-graph-evidence transport/cache whose rows are derived from GraphDB-approved selected graph evidence and fail closed on unresolved IDs.
- Evidence-strength and metric-strength diagnostics only when labeled report-only and excluded from ranking, selection, prompt assembly, lane status, generated text, and waterfall percentages until a later authorized stage.
- Historical documentation describing the migration.

Not allowed after W2:
- Any runtime read from `fact_ledger` to admit, weight, prove, or select a skill or metric.
- Any fallback path where missing GraphDB data is silently filled from `fact_ledger`.
- Any diagnostic that reports `fact_ledger` as an authoritative source for skills or metrics.
- Any runtime, report, or diagnostic contract that tells consumers to look up selected skills against "master skills" as an authority instead of the `augmented_skills_graph` authority interface.
- Any proof-pool or allowed-pool path that creates proof, repairs missing GraphDB evidence, accepts fact-era IDs as authority, or reports itself as the source of claim truth.
- Any metric claim, metric eligibility decision, or metric-strength diagnostic that depends only on side-field bundle references without resolving the metric outcome through GraphDB.
- Any evidence-strength, metric-strength, recency, confidence, or capability-depth score that changes W2.3 / Stage B ranking or selected evidence before a distinct ranking waterfall stage is authorized.
- Any DB-vs-JSON arbitration path during generation; if the GraphDB authority cannot resolve a required skill, metric, proof, employer, provenance, or section path, traversal fails closed.

**Acceptance**:
- B0 materialization E2E covers the single chosen resume's 11 generated lanes before any Stage B authority migration begins.
- Materialized GraphDB exposes first-class metric outcome rows and resolver checks for role-episode `linked_metric_outcome_ids` / `metric_outcome_nodes`.
- B0 proves `metric_outcome` materialization does not alter selected skill IDs, selected metric IDs, ranking order, prompt-input hashes, generated-output hashes, lane status, or waterfall percentages wherever generation occurs.
- Any unresolved metric-outcome reference emits `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict with an explicit blocker artifact.
- Static search and runtime tracing show no skills or metrics authority depends on `fact_ledger` by Stage B.
- Per-lane diagnostics resolve `selection_plan_skill_ref` and selected `skill_id` values through the `augmented_skills_graph` authority interface; any `lookup_backend` detail is explicitly non-authoritative.
- Per-lane diagnostics include evidence-strength and metric-strength as report-only fields, and a regression check proves they do not alter W2.3 selected skill IDs, selected metric IDs, ranking order, prompt inputs, lane status, generated text, or waterfall percentages.
- Proof-pool metadata carries graph-era selected evidence IDs and is documented as transport/cache only, not authority.
- Non-GraphDB-resolvable proof-pool rows fail closed before validators or generation can use them.
- Missing GraphDB skill, metric, proof, employer, provenance, or section paths emit `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict; no runtime path silently backfills from `fact_ledger`.
- `fact_ledger_runtime_skill_read_fails_closed_after_W2` passes.
- GraphDB SSOT Stage B E2E covers the single chosen resume's 11 generated lanes.
- Variance from B0 and W1 is rationalized as expected migration variance or flagged as regression.
- The W2 run preserves or improves graph-skill breakout visibility versus W1.
- **W2 carries the full 11/11 successful-E2E exit gate deferred from W1** (operator decision 2026-06-13): after metric_outcome materialization (W2.0) and graph-era/SSOT binding work (W2.2), the chosen resume's Stage B E2E reaches **all 11 generated lanes `X3_ALLOW` and the resume assembles**. The W1-deferred binding lanes (competencies-LLMOps bundle, headline + unify graph-lineage, ibm_bullets metric-anchor, ibm_narrative cascade) clear here, where the binding work lives.

---

## Wave 3 - Role Family And Role Facet Targeting

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED - Role-family granularity changes can affect every generated lane and must be reviewed before execution.

**Phases**:
- **W3.1** - Introduce reusable role-family facets and target alignment diagnostics | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Run role-family E2E and explain variance from W2 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Facet model**:

| Role family | Candidate reusable facets |
|---|---|
| `PARTNER_APPLIED_AI_ARCHITECTURE` | `applied_ai_architecture`, `partner_gtm`, `hyperscaler_cosell`, `technical_presales`, `customer_adoption_derisking`, `enterprise_platform_credibility` |
| `AGENTIC_ENGINEERING_LEADERSHIP` | `agentic_platform_architecture`, `engineering_leadership`, `ai_governance`, `delivery_operating_model`, `platform_reliability`, `stakeholder_alignment` |
| `IT_STRATEGY_AND_INNOVATION` | `it_strategy`, `innovation_portfolio`, `operating_model_transformation`, `enterprise_architecture`, `vendor_partner_leverage`, `business_outcome_delivery` |

**`role_facet_contract`** (facets are a real contract, not JD-keyword matching — defines the SSOT, default, and untagged behavior so no implementation can smuggle JD keywords in under "facet matching"):

```text
facet_id
role_family_id
eligible_pillar_ids          # facet may weight ONLY these graph pillars
skill_weight_range           # min..max multiplier applied within the eligible pool
default_weight
untagged_skill_behavior = neutral | demote | block   # behavior for skills with no facet tag
source_of_truth = graph_config | graph_row | static_taxonomy   # where facet assignments live
```

- A facet weights rank ONLY within the GraphDB-eligible pool; it can never admit a skill, create proof, or import a JD/briefing term as eligibility.
- `untagged_skill_behavior` defaults to `neutral` — untagged skills are not demoted or blocked merely for lacking a facet tag.
- `source_of_truth` MUST be declared; facet assignments may not be inferred at runtime from JD text.

**Acceptance**:
- Facets are reusable across role families and cannot directly admit a claim.
- Role-family granularity does not replace typed proof edges.
- A facet can boost only skills that already pass GraphDB SSOT eligibility.
- `high_role_facet_weight_cannot_select_unproven_skill` passes.
- `jd_keyword_cannot_create_proof_or_provenance` passes.
- `section_block_overrides_high_facet_weight` passes.
- `facet_weight_changes_rank_only_within_graph_eligible_pool` passes (positive test: facet weights re-rank only inside the graph-eligible pool, never admit).
- Role-family E2E covers the single chosen resume's 11 generated lanes; the cross-role diagnostic smoke run (below) covers all **5 targets** without full generation.
- Variance from W2 explains how the 5 targets move differently by role-family and lane — including the 2 held-outs (Neo4j PM, Aveva distinguished-IC) run cold.

**Cross-role diagnostic smoke run (required, non-generation)**:
- After the single-resume successful E2E, run a **non-generation selection/traversal diagnostic for all 5 targets** (Anthropic, Brown & Brown, Truist, Neo4j, Aveva — see "### Graph-% + Waterfall Variance Evidence § Target roster"). Per target and lane it must emit the selected / demoted / blocked / missing rows and the role-family / facet / pillar breakouts **without full generated output or X3 disposition**.
- **Hold-out discipline (mandatory):** before running #4 Neo4j + #5 Aveva, **freeze** the graph / facet / bundle config and run them **cold**. Role-appropriate, tuning-free results = generalization proof; if they need tuning to pass, log it (they become training points, claim weakens). This is the step that makes 5 worth more than 3.
- Purpose: surface role-family regressions for the non-live targets at W3, so they are not first observed at W5 where sliding-scale is also active and attribution is harder; and prove the graph generalizes to facets it was not tuned for.
- Cheap (selection/traversal only) and a W3 completion requirement; it does NOT replace the single-resume successful-E2E gate.
- **Implementation locus (built in W3.1, reused by W4):** `tools/apps_rg/selection_diagnostic.py` (or equivalent CLI mode such as `python -m apps_rg --selection-diagnostic --target-company ... --target-role ... --jd ...`) that drives the same selection/traversal path used by full generation but short-circuits before LLM dispatch and emits, **per target and per lane, to a JSON artifact**: (a) selected / demoted / blocked / missing rows, AND (b) **the graph-skill % breakout across all 6 dimensions — role family · role facet · pillar · source-fact-family · employer scope · metric type** (this is the every-stage, all-5-targets correctness evidence required by "### Graph-% + Waterfall Variance Evidence"). It must accept a **target list** (default the 5-target roster at A–D; the 2 live targets at E0/E1) and a `--frozen-config` mode for the cold hold-out runs. It must also emit a **per-step variance** block diffing the current stage's graph-% against the prior stage AND immutable Stage A (`artifacts/w1/`) per target/lane. This runner does NOT yet exist in `python -m apps_rg`; **W3.1 includes building it, and the graph-% + variance output (plus the freeze-and-run-cold hold-out path) is a hard part of its spec (not just selected/demoted rows).** W3.2 (and the W4 smoke run) invoke it; W3 cannot be marked complete without this runner existing and producing the graph-% + variance artifacts for all 5 targets × 11 lanes.
- **Back-fill for already-passed stages:** because this runner is built at W3.1, run it retroactively against Stage A/B0/B selection artifacts (deterministic — they re-derive from the merged graph) so the A→B→C variance chain has the 5-target graph-% at every prior step, not just from C onward.

---

## Wave 4 - Typed GraphDB Edge Contracts

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization**: REQUIRED - Typed edge changes alter proof, traversal, targeting, and eligibility semantics across `apps_rg` graph traversal.

**Phases**:
- **W4.1** - Implement typed GraphDB edge contracts for proof, traversal, and targeting | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Run typed-edge E2E and explain variance from W3 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Typed edge categories**:

| Category | Purpose | Example edge types |
|---|---|---|
| Proof | Shows a skill or claim is evidence-backed | `skill_supported_by_fact`, `fact_claim_eligible` |
| Provenance | Shows where proof came from | `fact_source_provenance`, `fact_source_trace` |
| Employer | Constrains facts to IBM, Unify, EY, InsurTech, or other employers | `employment_hosts_fact`, `fact_bound_to_employer` |
| Capability | Connects tracks, pillars, skills, and facts | `career_track_contains_pillar`, `pillar_contains_skill` |
| Section eligibility | Decides where a claim may appear | `skill_allowed_in_section`, `skill_blocked_for_section` |
| Targeting | Lets JD/briefing influence rank only | `target_context_suggests_role_family` |
| Facet | Applies reusable role intent over eligible paths | `role_family_contains_facet`, `facet_prioritizes_pillar` |

**Traversal explanation packet**:
- `role_family`
- `role_facet`
- `pillar_id`
- `skill_id`
- `supporting_fact_ids`
- `source_fact_family`
- `metric_type`
- `employer_scope`
- `section_eligibility`
- `claim_eligibility`
- `targeting_only_terms`
- `blocked_or_demoted_reason`

**Acceptance**:
- Every selected skill can emit a path with role family, facet, pillar, supporting fact, employer, section eligibility, and blocking notes.
- JD/briefing signals never appear in proof or provenance fields.
- Section lanes can reject a skill even when its role facet weight is high.
- Unknown traversal verdicts fail closed.
- `missing_supporting_fact_blocks_claim_eligibility` passes.
- `missing_employer_binding_blocks_employer_scoped_claim` passes.
- `typed_edge_missing_path_blocks_selected_skill_after_W4` passes.
- Typed-edge E2E covers the single chosen resume's 11 generated lanes; the cross-role diagnostic smoke run (below) covers all **5 targets** without full generation.
- Variance from W3 explains whether typed edges changed selection by proof, provenance, employer, or section eligibility.

**Cross-role diagnostic smoke run (required, non-generation)**:
- After the single-resume successful E2E, run the **non-generation typed-edge traversal diagnostic for all 5 targets** (incl. the 2 held-out, Neo4j + Aveva). Per target and lane it must emit the selected / demoted / blocked / missing rows plus the typed-edge category breakout (proof / provenance / employer / capability / section eligibility / targeting / facet) **without full generated output**.
- Purpose: catch typed-edge eligibility regressions for the non-live targets (Truist, Neo4j, Aveva) at W4, before W5 mixes in sliding-scale behavior — and confirm typed-edge eligibility generalizes to the held-out facets (PM, distinguished-IC).
- Cheap selection/traversal only; a W4 completion requirement that does NOT replace the single-resume successful-E2E gate.
- **Implementation locus:** reuse the `tools/apps_rg/selection_diagnostic.py` runner built in W3.1. W4.1 extends it to emit the typed-edge category breakout (proof / provenance / employer / capability / section eligibility / targeting / facet) per selected/demoted/blocked/missing row; no new runner is built at W4.

---

## Wave 5 - Sliding-Scale Percent Policy And Waterfall

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Authorization**: REQUIRED - Sliding-scale thresholds and blocking behavior affect generation eligibility.

**Phases**:
- **W5.0** - Author the live-target threshold table IT_STRATEGY_AND_INNOVATION (Brown & Brown) matching the existing PARTNER_APPLIED_AI_ARCHITECTURE (Anthropic) structure; **both live-target tables (Anthropic + Brown & Brown) MUST exist before W5.1 starts.** Truist's AGENTIC_ENGINEERING_LEADERSHIP table is **deferred** (Truist is a diagnostic-only target, no band table needed at A–D) unless the operator swaps it into the 2-live ship set (amendment 2026-06-13B). | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.1** - Implement sliding-scale diagnostic calculations behind a dry-run flag | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - Run sliding-scale dry-run E2E and explain variance from W4 and W1 | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** - Enable active sliding-scale enforcement and pre-prompt rebalancing | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.4** - Run active sliding-scale E2E, produce waterfall analysis, and update Notion closeout | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Sliding-scale rollout gates**:

| Stage | Mode | Required proof |
|---|---|---|
| E0 | Dry-run diagnostics only | Computes facet, source, metric, section, and repeated-concept mix for every target/lane; emits would-be `REBALANCE_REQUIRED` without changing ranking, selection order, prompt inputs, or lane pass/fail status |
| E1 | Active enforcement | Applies caps, floors, penalties, and rebalancing before prompt assembly; concentration breaches block or rebalance with `REBALANCE_REQUIRED`; all variance is compared to E0, D, and A |

> **Rebaselined validation (2026-06-13, targets amended 2026-06-13B → 2 live):** **E0 is replay-validated, 0 live calls** — it is a declared no-effect stage (diagnostics only), so the 22-lane requirement is met by replaying Stage D's frozen provider responses and computing the dry-run diagnostics offline, proving input-parity (selected evidence + ranking + lane status unchanged) per the Deterministic/Replay Rule. **E1 is the one genuinely-live 22-lane run** (active enforcement changes pre-prompt selection ⇒ generation changes ⇒ must run live), with the **2 live ship targets** (Anthropic + Brown & Brown) run concurrently via the multi-target launcher (prereq **P4**) or serially. So W5's live cost rebaselines to **1×22-lane (2 live targets)**.
- Use ranges, caps, floors, and penalties rather than fixed one-size percentages.
- Compute percentages from eligible graph skills, not JD keyword counts.
- Use section-specific thresholds so headline, executive summary, competencies, bullets, and narratives can differ.
- Preserve durable candidate strengths even when a target role is highly specialized.
- Require a rebalancing verdict before prompt assembly when concentration breaches caps or floors.

**Illustrative Anthropic partner applied-AI target ranges**:

| Facet | Target range |
|---|---:|
| Applied AI / solution architecture | 25-30% |
| Partner / alliance GTM | 20-25% |
| Hyperscaler / co-sell | 15-20% |
| Technical presales / adoption | 15-20% |
| Enterprise platform credibility | 10-15% |
| Legacy quant/risk credibility | 0-5% |

**Per-target threshold config (required before W5 — not just Anthropic):**

The Anthropic ranges above are illustrative. Before E0/E1, a binding threshold config MUST exist for **every target role family and section-lane type**, so enforcement is mechanical (not operator judgment):

```text
role_family            # PARTNER_APPLIED_AI_ARCHITECTURE | AGENTIC_ENGINEERING_LEADERSHIP | IT_STRATEGY_AND_INNOVATION
section_lane_type      # headline | executive_summary | competencies | bullets | narrative
facet_caps             # per-facet max %
facet_floors           # per-facet min %
source_family_caps     # per source-fact-family max %
metric_family_caps     # per metric-family max %
core_candidate_preservation_floor   # reserved % for durable candidate strengths
```

W5 is BLOCKED until both **live** targets — Anthropic (`PARTNER_APPLIED_AI_ARCHITECTURE`) and Brown & Brown (`IT_STRATEGY_AND_INNOVATION`) — each have their own threshold table. Truist's (`AGENTIC_ENGINEERING_LEADERSHIP`) table is deferred unless it is swapped into the 2-live set (amendment 2026-06-13B).

**Guardrails**:

| Guardrail | Purpose |
|---|---|
| Facet concentration caps | Prevent generic partner GTM from dominating the pool |
| Facet floors | Preserve applied AI architecture, technical presales, platform credibility, engineering leadership, and IT strategy signals where relevant |
| Source diversity | Prevent all selected skills from coming from one fact family such as `fact_partnerships_gtm_*` |
| Section-specific caps | Keep headline, summary, bullets, narratives, and competencies from using the same density rules |
| Repeated concept penalty | Demote repeated co-sell, alliance, marketplace, partner enablement, agentic, innovation, and transformation concepts |
| Metric diversity | Balance revenue/GTM, platform delivery, adoption, operational scale, governance/reliability, and transformation metrics |
| Core candidate preservation | Reserve space for durable candidate strengths independent of target JD wording |
| Proof-targeting firewall | Keep JD/briefing terms out of proof and claim eligibility |

**Canonical taxonomies (binding enums — so two implementers cannot diverge):**
- **`metric_family`** = `revenue_gtm` | `platform_delivery` | `adoption` | `operational_scale` | `governance_reliability` | `transformation` | `risk_quant`. Drives the metric-diversity guardrail and `repeated_metric_family_triggers_rebalance`.
- **`repeated_concept_family`** = `co_sell` | `alliance` | `marketplace` | `partner_enablement` | `agentic` | `innovation` | `transformation` | `governance` | `platform_reliability`. Drives the repeated-concept penalty.
- Both enums are the SSOT; adding a bucket requires a plan amendment.

**Diagnostic shape**:

```text
target: anthropic_partner_applied_ai
stage: sliding_scale_percent
lane: executive_summary
role_family: PARTNER_APPLIED_AI_ARCHITECTURE
facet_mix:
  partner_gtm: 32% WARN cap 30%
  applied_ai_architecture: 18% WARN floor 20%
  enterprise_platform_credibility: 7% WARN floor 10%
source_mix:
  partnerships_gtm facts: 65% WARN
  platform facts: 20%
  adoption facts: 15%
verdict: REBALANCE_REQUIRED
```

**Waterfall report requirements**:
- Compare A to B0, B0 to B, B to C, C to D, D to E0, E0 to E1, and A to every post-baseline stage for every target and lane.
- Show graph-skill percent change by role family, facet, pillar, source fact family, employer scope, and metric type.
- Show sliding-scale dry-run versus active-enforcement deltas, including which lanes had no text/output change in dry-run and which lanes blocked, rebalanced, promoted, or demoted evidence after active enforcement.
- Call out top variance drivers and whether each was expected.
- Explain why Anthropic, Truist, and Brown & Brown diverge from one another after each stage.
- Include a compact summary table suitable for Notion closeout.

**Acceptance**:
- Sliding-scale dry-run E2E covers the 2 live targets × 11 lanes (22-lane) and proves diagnostics do not alter ranking, selected evidence, prompt inputs, generated text, or lane pass/fail status.
- Active sliding-scale E2E covers the 2 live targets × 11 lanes (22-lane) after enforcement is enabled.
- A full waterfall report exists for Stage A plus B0, B, C, D, E0, and E1.
- Over-concentrated selected pools return `REBALANCE_REQUIRED` before prompt assembly.
- `over_concentrated_pool_blocks_prompt_assembly_after_W5` passes.
- `repeated_metric_family_triggers_rebalance` passes.
- `target_company_name_cannot_be_claimed_as_experience`
- `capability_depth_cannot_satisfy_proof_or_claim_eligibility`
- `resume_bullet_nodes_cannot_enter_core_graph_before_waterfall_closeout` passes.
- Prompt-only wording, example, or anti-overfit text changes are rejected as W5 closure evidence unless traversal diagnostics and enforcement changed.
- Final text anti-overfit remains in place for copied JD phrasing, keyword stuffing, unsupported target-company claims, repeated buzzwords, and target role as past experience.
- Notion row links the disk plan and final evidence.

---

## Execution Details

### P0.1 - Candidate-Fact Authority Inventory

**Scope**: Classify `candidate_fact` usage before W1 as either allowed lineage/compatibility or disallowed runtime authority.

**Required searches**:
```bash
rg -n "candidate_fact|candidate facts|CandidateFact" apps_rg tests docs plans .codex
```

**Classification rule**:
- Allowed: lineage identifier, historical artifact reference, or compatibility alias that resolves to a GraphDB-backed path.
- Disallowed: any use that admits, proves, ranks, weights, selects, or backfills a skill, metric, claim, proof path, or section.

**Completion evidence**: `docs/reports/apps_rg/candidate_fact_p0_authority_inventory_20260612.md` classifies remaining references as lineage/compatibility, fact-vector substrate labels pending W2, tombstones, or historical prompt/test artifacts. The post-patch static search found no remaining `candidate_facts_as_proof: true` declarations or tests expecting candidate facts to prove claims.

### P0.2 - Candidate-Fact Authority Deprecation

**Scope**: Deprecate, rename, or fence disallowed `candidate_fact` authority before any W1 E2E baseline run.

**Completion evidence**: `apps_rg/runtime/validators/graph_skills_proof_common.py` now emits `BLOCKED_CANDIDATE_FACT_AUTHORITY` for candidate-fact/SRFS authority flags, authority source fields, selection methods, and candidate-fact claim substrate without GraphDB claim authority. `apps_rg/runtime/sections/section_spec.py` forces deprecated `candidate_facts_as_proof` input closed and preserves `candidate_fact_lineage_allowed` as lineage-only configuration.

### P0.3 - Candidate-Fact Deprecation Tests

**Scope**: Run the fail-closed test gate before W1.

**Required evidence**:
- Static inventory artifact.
- Runtime fail-closed evidence for at least one disallowed candidate-fact authority read.
- Passing `candidate_fact_runtime_authority_read_fails_closed_before_W1`.
- A compatibility map for any remaining `candidate_fact_id` fields.
- Explicit W1 block if the test fails or if any disallowed authority read remains.

**Completion evidence**: Focused P0 gate passed: `tests/unit/apps_rg/runtime/sections/test_section_spec_wave6.py`, `tests/unit/apps_rg/test_candidate_fact_deprecation_p0.py`, `tests/unit/apps_rg/test_graph_skills_authority_separation.py`, `tests/unit/apps_rg/test_selected_role_fact_set_retirement_guard.py`, and `tests/_apps_contract/test_apps_rg_augmented_skills_graph_source_authority.py` reported 47 passed, 3 warnings with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and local `addopts` override for the unavailable timeout plugin.

### W1.1 - Resolve Commands And Fixtures

**Scope**: Identify the canonical E2E command, target fixtures, graph receipt paths, and generated-content lane list before changing behavior.

**Required searches**:
```bash
rg -n "anthropic_partner_applied_ai|truist_head_of_agentic_engineering|brown_brown_svp_it_strategy_innovation" apps_rg tests docs/reports/apps_rg plans
rg -n "GENERATED_CONTENT_LANES|section_execution_plan|e2e|end to end" apps_rg tests docs/reports/apps_rg plans
```

**Completion evidence**:
- Canonical generated lane matrix resolved from `apps_rg.runtime.section_execution_plan.GENERATED_CONTENT_LANES`: 11 generated lanes per target.
- Canonical target fixtures resolved:
  - Anthropic AI Partner: `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt` and `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md`.
  - Truist Head of Agentic Engineering: `apps_rg/config/targeting/truist_head_agentic_ai_engineering_jd.txt` and `apps_rg/config/targeting/truist_head_agentic_ai_engineering_briefing.md`.
  - Brown & Brown SVP IT Strategy & Innovation: `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt` and `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md`.
- `python -m apps_rg doctor --strict --json` passed before W1 runs.

### W1.2 - Single-Resume Successful E2E (Stage A gate)

**Scope**: Run the Post-P0 finalized graph / no-typed-edge baseline for ONE chosen target (default `anthropic_partner_applied_ai`) across all 11 generated lanes to a **successful E2E** (all lanes `X3_ALLOW`, resume assembles), capturing per-lane graph-skill breakouts.

> ⛔ **Retired Historical Evidence (non-advancing).** The "Prior three-target blocking run" block below is from the superseded 2026-06-12 blocking baseline. **This evidence is non-advancing and cannot satisfy DoD-1.** It is retained only for historical graph-skill-mix context; W1 is satisfied solely by a fresh single-resume successful E2E.

**Prior three-target blocking run — RETIRED, historical context only:**
- W1 report: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.md`.
- Machine-readable W1 report: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.json`.
- Anthropic baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/anthropic_partner_applied_ai`; patch receipt `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/anthropic_partner_applied_ai/patch_run_receipt.json`.
- Truist baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/truist_head_of_agentic_engineering`; patch receipt `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/truist_head_of_agentic_engineering/patch_run_receipt.json`.
- Brown & Brown baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/brown_brown_svp_it_strategy_innovation`.

**Waterfall outcome**:
- Coverage: 33 explicit target-lane rows captured: 13 executed-and-blocked rows, 15 pre-run blocked rows, and 5 selected/authorized rows.
- Anthropic target graph-skill mix: partnerships ecosystem 27.9%, enterprise technology delivery 24.8%, agentic AI governance platform 18.5%, cloud data platform 15.2%, actuarial/capital/risk 7.1%, insurance/insurtech 5.4%, product commercialization 1.2%.
- Truist target graph-skill mix: agentic AI governance platform 37.0%, enterprise technology delivery 30.4%, partnerships ecosystem 18.5%, cloud data platform 9.8%, actuarial/capital/risk 2.2%, product commercialization 2.2%.
- Brown & Brown target graph-skill mix: cloud data platform 28.1%, enterprise technology delivery 24.9%, agentic AI governance platform 16.1%, insurance/insurtech 10.4%, partnerships ecosystem 10.0%, actuarial/capital/risk 9.2%, product commercialization 1.2%.
- `tools/apps_rg/graph_skill_utilization_report.py` could not run because W1 did not reach `final_resume_assembly/final_resume.json`; this is expected for the W1 blocking baseline. The W1-specific report uses lane receipts, X3 dispositions, provider responses, and patch receipts instead.
- Variance against P0 is classified as baseline creation and fail-closed behavior, not a percentage delta, because P0 was a candidate-fact authority deprecation/test gate rather than an all-lane E2E composition stage.
- RETIRED RATIONALE (no longer valid): the prior run was accepted as a blocking baseline with no final resume assembly. Under the amended single-resume successful-E2E gate this run is **non-advancing and cannot satisfy DoD-1**; a fresh successful E2E (all 11 generated lanes `X3_ALLOW`, resume assembles) is required.

### W2.0 - First-Class Metric Outcome Materialization

**Scope**: Materialize metric outcomes as GraphDB-resolvable rows before any Stage B authority migration. This is schema/materialization/resolver-validation only.

**Required searches**:
```bash
rg -n "linked_metric_outcome_ids|metric_outcome_nodes|metric_outcome|metric outcome" apps_rg/runtime apps_rg/fact_inventory apps_rg/config tests docs plans .codex
rg -n "evidence_strength|metric_strength|capability_depth|ResumeBullet|resume_bullet" apps_rg tests docs plans .codex
```

**Review rule**: metric outcome references must resolve to GraphDB rows before they can support metrics authority. Evidence-strength and metric-strength may be emitted only as diagnostics. Capability depth and ResumeBullet nodes are not W2 core-graph inputs. No ranking, selection, prompt, role-facet, typed-edge, sliding-scale, capability-depth, or ResumeBullet behavior may be introduced in W2.0.

**Completion evidence**:
- Materialized GraphDB schema or export contains first-class metric outcome rows.
- Resolver evidence shows role-episode `linked_metric_outcome_ids` and `metric_outcome_nodes` resolve or fail closed.
- Runtime check for `linked_metric_outcome_id_must_resolve_to_graph_metric_outcome_after_W2`.
- Static check proving W2.0 did not introduce active ranking multipliers, capability-depth behavior, or ResumeBullet core-graph nodes.

### W2.1 - Pre-B Metric Outcome E2E

> **W2.1 RESULT (2026-06-13).** First valid full-substrate B0 E2E for `anthropic_partner_applied_ai` at `artifacts/w2_b0/` (run_id in `terminal_ret_packet.json`). **6 X3_ALLOW** (unify_bullets, unify_narrative, insurtech_bullets, insurtech_narrative, ey_bullets, ey_narrative) · **4 X3_BLOCK** (competencies, executive_summary, headline, ibm_bullets) · **1 cascade** (ibm_narrative ← ibm_bullets). The 4 blocked lanes are exactly the W2.2 consumer-migration targets.
>
> **Prerequisite discovered + fixed (not in original plan):** every prior W1/W2 E2E silently fail-closed at C0.2 because the per-chat **worktree lacked the gitignored runtime data** (`data/cache/sparse/fact_vectors.db` BM25 + `data/cache/chromadb/` dense) and `.env`. Fix = Windows directory junctions from worktree → primary checkout + copied `.env`. This is the real reason the retired W1 baseline showed only 5 ALLOW with all-lanes-BM25-unavailable. Memory: `worktree-runtime-data-junctions`.
>
> **Stage A baseline integrity:** the designated Stage A path `artifacts/w1/` exists only in the **primary checkout** and is a **pre-junction broken run** (all lanes BM25-unavailable) — NOT a valid baseline. Consequence: there is no clean empirical Stage A → B0 diff. **W2.0 no-effect is proven STRUCTURALLY instead** (input-parity fallback (c) at the materialization level): the materializer (`metric_outcome_materializer.metric_outcome_node_and_edge_rows`) raises on any node-ID collision with an existing graph node and emits ONLY `metric_outcome`-typed nodes + `metric_outcome_`-prefixed edges, so no pre-existing `node_type`/`edge_type` query result changes. Verified live: 92 metric_outcome nodes + 452 edges added, existing skill/edge counts unchanged. This is a stronger guarantee than an LLM output-hash diff (which the Deterministic/Replay Rule already exempts under fallback (c)).
>
> **ibm_bullets block root cause (W2.2 target):** single failed gate `x2_ibm_metric_anchor_bullet_ownership`, observed `['bul_ibm_005_missing_metric_token']`. The gate's `IBM_METRIC_ANCHOR_RULES` hardcodes a stale fact-era requirement that `bul_ibm_005` carry the literal token "20%", but the graph-selected plan legitimately assigned that bullet `has_metric: None`. W2.2 fix = make metric ownership graph-determined (a bound `metric_outcome` row satisfies it) rather than literal-token-determined; the existing `_ibm_metric_anchors_on_assigned_bullets` no-metric escape is not firing for bul_ibm_005, indicating the runtime `selected_plan` shape differs from on-disk `selected_fact_plan.json` — needs a per-lane runtime trace.

**Scope**: Run Stage B0 for the single chosen resume (default `anthropic_partner_applied_ai`) across all 11 generated lanes with only W2.0 changes active. The multi-target *live* matrix is the 2 ship targets at W5 per the E2E Resume-Count Gate Policy (the 5-target graph-% diagnostic is non-generation).

**Required evidence**:
- The single chosen resume's 11 generated lanes with Stage B0 run ids, artifact paths, lane status, and blocker details where applicable.
- Comparison against immutable Stage A for selected skill IDs, selected metric IDs, ranking order, prompt-input hashes, lane status, and waterfall percentages. Generated-output hash parity is required ONLY when B0 runs in replay mode (a) or deterministic/mock mode (b) per the Deterministic / Replay Rule For No-Effect Stages; under input-parity fallback (c), output-hash parity is NOT a B0 gate (an LLM-nondeterminism output diff alone does NOT fail B0 — the binding no-effect proof in mode (c) is prompt-input + selected-evidence + ranking + lane-status parity).
- Proof that evidence-strength and metric-strength diagnostics are report-only and do not alter ranking, selected evidence, prompt inputs, generated text, or lane pass/fail status.
- Explicit blocker ledger for any unresolved metric outcome IDs.
- `metric_outcome_materialization_does_not_change_selection_before_B0` passes.
- `stage_b0_e2e_artifacts_must_cover_all_target_lanes` passes.

### W2.2 - Graph-Era Runtime Field Migration, Proof-Pool Boundary, And GraphDB SSOT

**Scope**: After B0 is accepted, migrate fact-era runtime field names to graph-era contracts behind compatibility aliases, fence proof-pool plumbing as transport/cache only, replace or fence every `fact_ledger` skills/metrics authority reference, and ensure selected skill references resolve through the `augmented_skills_graph` authority interface rather than any separately named "master skills" authority.

**Required searches**:
```bash
rg -n "selected_fact_plan|allowed_fact_ids|source_fact_ids|fact_id" apps_rg/runtime apps_rg/config tests docs plans .codex
rg -n "proof_pool|proof pool|proof_pool_resolver|allowed_pool|proof metadata" apps_rg/runtime apps_rg/config tests docs plans .codex
rg -n "fact_ledger|fact ledger|FactLedger" apps_rg tests docs plans .codex
rg -n "master_skills|master skills|master_skills_arsenal_ledger|selection_plan_skill_ref" apps_rg tests docs plans .codex
rg -n "evidence_strength|metric_strength|capability_depth|ResumeBullet|resume_bullet" apps_rg tests docs plans .codex
```

> Note: `candidate_fact_id` was inventoried and classified in P0.1 and fenced in P0.2; W2.2 reuses that classification (lineage/compatibility allowed; authority disallowed) rather than re-searching. Adding `candidate_fact_id` back into this search would re-surface the P0.1-allowed lineage aliases as if they were new W2.2 scope.

**Review rule**: fact-era names may remain only as explicit compatibility aliases while W2.2 migrates consumers to graph-era names. Proof-pool names may remain only for runtime compatibility when they carry GraphDB-approved selected evidence IDs and fail closed on unresolved IDs. References that only describe historical migration may remain in docs. Runtime, fixture, traversal, validator, and generator paths may not use `fact_ledger` as skills or metrics authority after Stage B. References to `master_skills_arsenal_ledger.json` may remain only as non-authoritative serialization/export/bootstrap/review labels or as resolver implementation detail behind `augmented_skills_graph`; user-facing diagnostics must not present it as a separate skills SSOT.

**Completion evidence**:
- Compatibility map from every fact-era runtime field to its graph-era replacement.
- Static audit showing graph-era fields are the preferred read path in validators, proof-pool metadata, and section packets.
- Static and runtime audit showing proof-pool plumbing is transport/cache only and all usable rows resolve to GraphDB-approved graph evidence IDs.
- Runtime proof that fact-era aliases do not admit, rank, prove, or select skills, metrics, claims, or sections.
- Runtime proof that evidence-strength and metric-strength diagnostics do not alter W2.3 selected skill IDs, selected metric IDs, ranking order, prompt inputs, lane status, generated text, or waterfall percentages.

### W2.3 - GraphDB SSOT Stage B E2E

**Scope**: Run Stage B for the single chosen resume (default `anthropic_partner_applied_ai`) across all 11 generated lanes after W2.2 and compare against both Stage B0 and immutable Stage A. The multi-target *live* matrix is the 2 ship targets at W5 per the E2E Resume-Count Gate Policy (the 5-target graph-% diagnostic is non-generation). **Stage B is the 11/11-all-lanes-`X3_ALLOW` exit gate** for the W1-deferred binding lanes (operator decision 2026-06-13).

**Required evidence**:
- The single chosen resume's 11 generated lanes with Stage B run ids, artifact paths, lane status, and blocker details where applicable.
- Variance rationalization versus B0 and Stage A, with every material delta classified as expected migration variance, fail-closed GraphDB path debt, or regression.
- Static and runtime evidence showing no skills or metrics authority depends on `fact_ledger`.
- `fact_ledger_runtime_skill_read_fails_closed_after_W2` passes.
- `strength_diagnostics_do_not_change_selection_before_ranking_stage` passes.
- `each_waterfall_stage_requires_prior_and_stage_a_diff` passes.
- W2.3 E2E artifact includes both graph-era contract proof and compatibility-alias deprecation status.

### W4.2 - Traversal Explanation Packet

**Scope**: Emit the packet contract before final selection is passed into section generation.

**Expected packet fields** are listed in Wave 4 and must be present in artifacts for selected, demoted, and blocked skills.

**Verdict rule**: selected, demoted, blocked, missing, rebalance, and diagnostic-only outcomes must use the canonical verdict enum from Hardening Rules. Unknown verdicts fail closed.

### W5.1 - Sliding-Scale Dry-Run Implementation

**Scope**: Implement sliding-scale calculations behind a dry-run flag. Dry-run may compute caps, floors, repeated-concept penalties, source diversity, metric diversity, and core-candidate-preservation diagnostics, but it may not alter selected evidence, ranking order, prompt inputs, or lane pass/fail status.

**Required evidence**:
- Feature flag or configuration showing dry-run mode.
- Diagnostic packet emitted for every generated lane.
- Unit or runtime regression proving dry-run output is observational only.

### W5.2 - Sliding-Scale Dry-Run E2E

**Scope**: Run Stage E0 across the full target/lane matrix and compare dry-run diagnostics against Stage D and immutable Stage A.

**Required evidence**:
- 22 target-lane rows (2 live targets × 11 lanes) with sliding-scale diagnostic packets.
- Per-lane would-be cap/floor/rebalance verdicts.
- Proof that dry-run diagnostics did not change selected skill IDs, selected metric IDs, ranking order, prompt inputs, generated text, or lane status.
- Variance explanation versus Stage D and Stage A.

### W5.3 - Active Sliding-Scale Enforcement

**Scope**: Enable pre-prompt enforcement. Active mode may demote, rebalance, or block over-concentrated pools before prompt assembly using the sliding-scale policy proven in dry-run.

**Required evidence**:
- Feature flag or configuration showing active enforcement mode.
- `REBALANCE_REQUIRED` emitted before prompt assembly for concentration breaches.
- No JD/briefing term can become proof or claim eligibility through the sliding-scale layer.
- Unit or runtime regression for repeated metric family and over-concentrated pool behavior.

### W5.4 - Active Sliding-Scale E2E And Waterfall Analysis

**Scope**: Run Stage E1 across the full target/lane matrix and produce a single waterfall artifact that joins Stage A plus B, C, D, E0, and E1.

**Minimum output tables**:
- `run_matrix`: target x stage x lane status.
- `skill_percent_breakout`: target x stage x lane x breakout dimension.
- `sliding_scale_diagnostics`: target x stage x lane x facet/source/metric/section/repeated-concept guardrail result.
- `variance_drivers`: target x stage_transition x lane x driver.
- `waterfall_summary`: target x lane x A-to-E1 net change.

---

## Gap Register

**GAP-1: Role family too close to skill selection**
- Impact: A granular role family can behave like a keyword bucket.
- Closure: Role facets weight only GraphDB-eligible paths and typed edges control final proof.

**GAP-2: Final anti-overfit too late**
- Impact: A partner-heavy proof pool naturally generates partner-heavy text.
- Closure: Add traversal diagnostics and rebalance before generation.

**GAP-3: Source concentration invisible**
- Impact: IBM sections can overuse partnership facts while underusing platform/cloud/architecture proof.
- Closure: Source diversity diagnostics and section-specific caps.

**GAP-4: Proof and targeting can blur**
- Impact: JD/briefing terms can influence output as if they proved experience.
- Closure: Proof-targeting firewall and typed traversal packet.

**GAP-5: `fact_ledger` competes with GraphDB**
- Impact: Skills and metrics authority can drift between sources.
- Closure: Remove or fence `fact_ledger` skills/metrics authority before role-family or typed-edge changes.

**GAP-5A: `master_skills` wording creates a second-SSOT impression**
- Impact: Reports or diagnostics can appear to require a separate "master skills" authority even when the intended authority is GraphDB / `augmented_skills_graph`.
- Closure: Resolve selected skill refs through the `augmented_skills_graph` authority interface and label any JSON ledger usage as non-authoritative serialization/backend detail.

**GAP-5B: Metric outcomes are referenced but not first-class GraphDB authority**
- Impact: Role-episode bundles can carry `linked_metric_outcome_ids` / `metric_outcome_nodes` while the materialized graph treats metrics as side fields, weakening the W2 claim that GraphDB is the skills and metrics SSOT.
- Closure: Materialize metric outcomes as GraphDB-resolvable rows in W2.0, run B0 single-resume x 11-lane E2E before Stage B, prove no selection/ranking effect, and fail closed on unresolved metric outcome IDs.

**GAP-5C: Strength scores can blur diagnostics with selection**
- Impact: Evidence-strength or metric-strength multipliers may improve ranking quality, but adding them before Stage B closes would make the GraphDB SSOT delta impossible to attribute cleanly.
- Closure: Emit strength fields as diagnostics only in W2; if ranking multipliers are later accepted, insert a separate post-B ranking gate with the full 5-target graph-% diagnostic + a single-resume live E2E before role-family or typed-edge behavior is mixed in.

**GAP-5D: `proof_pool` wording creates a second-SSOT impression**
- Impact: Reports, validators, or generation code can appear to treat the proof pool as claim truth instead of a selected-evidence transport surface derived from GraphDB.
- Closure: Keep proof-pool plumbing only as a runtime cache for GraphDB-approved selected evidence IDs, prefer graph-era names in user-facing contracts, and fail closed on any row that cannot resolve to GraphDB authority.

**GAP-6: No waterfall means no causal attribution**
- Impact: E2E differences cannot be attributed to SSOT migration, role family, typed edges, or sliding-scale policy.
- Closure: Require the same target roster (5 diagnostic at A–D / 2 live at E0–E1) and 11 lanes at every stage with variance rationalization against both the prior stage and immutable Stage A.

**GAP-6A: Sliding-scale behavior is under-proven if only final closeout runs it**
- Impact: The key feature can be hidden inside final E2E variance, making it unclear whether diagnostics, enforcement, or unrelated generation changes caused the result.
- Closure: Split sliding scale into E0 dry-run diagnostics and E1 active enforcement, each with full 3 x 11 E2E and explicit comparisons to prior stage and Stage A.

**GAP-6B: Bundled changes can destroy causal attribution**
- Impact: If schema materialization, authority migration, diagnostics, ranking multipliers, capability-depth behavior, role facets, typed edges, or prompt changes land together, the waterfall cannot explain which change caused output variance.
- Closure: Require a named change manifest and a full E2E gate for every stage; B0 is metric-outcome materialization only, B is SSOT migration only, C is role facets, D is typed edges, E0 is diagnostic-only sliding scale, and E1 is active enforcement.

**GAP-7: Missing graph paths can be silently backfilled**
- Impact: Traversal can appear to pass while sourcing eligibility from JD, briefing, prompt context, historical output, generated text, or `fact_ledger`.
- Closure: Enforce `MISSING_GRAPH_PATH` or `BLOCKED_*` verdicts and fail closed on unknown verdicts.

**GAP-8: Prompt-only closure can mask traversal defects**
- Impact: Rewording prompts can reduce visible overfit without fixing selection, proof, or composition enforcement.
- Closure: Disallow prompt-only fixes as W3, W4, or W5 closure evidence.

**GAP-9: Candidate-fact authority pollutes the first graph baseline**
- Impact: W1 can measure legacy candidate-fact behavior instead of GraphDB traversal behavior.
- Closure: Move `candidate_fact` authority removal/fencing to P0, before the first E2E baseline.

---

## Definition of Done

> **Validation-method note (2026-06-13 rebaseline):** DoD evidence is unchanged, but *how* it is produced
> is rebaselined per "### Rebaselined Effort Model" + the waterfall "Validation Method" column. Deterministic
> evidence (DoD-2B/4/6/13 — gates, contracts, fences, hardening) is **replay/offline-validated** via
> `tools/apps_rg/replay_section_gates.py` + unit tests (zero API). E2E DoDs (DoD-3/5/7/9/10/10A) take their
> **one live-confirm** per stage (DoD-9/E0 by replay). The 5-target smokes (DoD-5/7) are non-generation/offline.
> Replay reduces validation COST, not rigor — the same gates run.

DoD-0: Candidate-fact authority is deprecated and tested before W1.
- Evidence: P0 inventory classifies all live `candidate_fact` references, disallowed authority paths fail closed, `candidate_fact_runtime_authority_read_fails_closed_before_W1` passes, W1 is blocked on failure, and remaining `candidate_fact_id` fields are lineage/compatibility only.
- Status: DONE

DoD-1: Finalized graph baseline without typed edges is captured via a single-resume successful E2E.
- Evidence: Post-P0 W1 E2E run for ONE chosen target (default `anthropic_partner_applied_ai`) reaches **current-substrate-passable** (all lanes that pass on the existing graph substrate are `X3_ALLOW` after the W1 gen-fixes: exec_summary schema/parse + narrative `forbidden_opener`), with per-lane graph-skill percent breakouts and an explicit blocker ledger for lanes deferred to W2 (graph-binding / `metric_outcome` anchoring). The full 11/11 successful E2E is the W2 / Stage B gate; the multi-target *live* matrix is the 2 ship targets at W5 (the 5-target graph-% diagnostic is non-generation) per the E2E Resume-Count Gate Policy.
- Status: TODO

DoD-2A: First-class metric-outcome materialization is complete before Stage B.
- Evidence: First-class `metric_outcome` rows exist in materialized GraphDB; role-episode metric IDs resolve or fail closed; B0 E2E covers the single chosen resume's 11 generated lanes; B0 proves metric-outcome materialization has no ranking, selection, prompt-input, lane-status, generated-output, or waterfall-percentage effect except explicit unresolved-metric blockers.
- Status: TODO

DoD-2B: GraphDB is the skills and metrics SSOT.
- Evidence: Static and runtime evidence shows `fact_ledger` is not used for skill eligibility, metric eligibility, weighting, proof, or traversal; proof-pool plumbing is transport/cache only and cannot admit proof outside GraphDB-approved selected evidence IDs; per-lane selected skill refs resolve through the `augmented_skills_graph` authority interface, with any JSON ledger usage labeled as non-authoritative backend detail.
- Status: TODO

DoD-3: GraphDB SSOT migration has E2E parity or explained variance.
- Evidence: W2.3 Stage B E2E run covers the single chosen resume's 11 generated lanes and rationalizes variance from both B0 and W1; evidence-strength and metric-strength are present only as diagnostics and have no Stage B ranking, selection, prompt-input, lane-status, generated-output, or waterfall-percentage effect.
- Status: TODO

DoD-4: Role facets exist as reusable targeting weights, not direct skill selectors.
- Evidence: `high_role_facet_weight_cannot_select_unproven_skill`, `jd_keyword_cannot_create_proof_or_provenance`, and `section_block_overrides_high_facet_weight` pass.
- Status: TODO

DoD-5: Role-family E2E is complete.
- Evidence: W3 E2E run covers the single chosen resume's 11 generated lanes with per-lane graph-skill percent breakouts and variance from W2; W3 cross-role diagnostic smoke run covers all 5 targets (non-generation), with the 2 held-out (Neo4j, Aveva) run cold on frozen config.
- Status: TODO

DoD-6: Typed edge hierarchy is documented and implemented without replacing proof edges with role-family buckets.
- Evidence: Design/spec artifact plus code diff showing `apps_rg` GraphDB proof, provenance, employer, capability, section eligibility, targeting, and facet edges remain authoritative within resume generation.
- Status: TODO

DoD-7: Typed-edge E2E is complete.
- Evidence: W4 E2E run covers the single chosen resume's 11 generated lanes, explains variance from W3 by edge category (plus W4 cross-role diagnostic smoke run across all 5 targets, non-generation), and `missing_supporting_fact_blocks_claim_eligibility`, `missing_employer_binding_blocks_employer_scoped_claim`, and `typed_edge_missing_path_blocks_selected_skill_after_W4` pass.
- Status: TODO

DoD-8: Sliding-scale percentage policy is reviewed and implemented.
- Evidence: Caps, floors, penalties, and section-specific thresholds are documented and exercised first in E0 dry-run diagnostics, then in E1 active enforcement.
- Status: TODO

DoD-9: Sliding-scale dry-run E2E proves diagnostics without behavior change.
- Evidence: E0 dry-run E2E covers the 2 live targets × 11 lanes (22-lane) and proves sliding-scale diagnostics do not alter selected skill IDs, selected metric IDs, ranking order, prompt inputs, generated text, or lane status.
- Status: TODO

DoD-10: Active anti-overfit enforcement runs before generation.
- Evidence: E1 active E2E covers the 2 live targets × 11 lanes (22-lane); concentrated candidate pools return `REBALANCE_REQUIRED` before prompt assembly; `over_concentrated_pool_blocks_prompt_assembly_after_W5` and `repeated_metric_family_triggers_rebalance` pass.
- Status: TODO

DoD-10A: Full waterfall is complete against one immutable baseline.
- Evidence: Report compares immutable Stage A to B0 metric-outcome materialization, Stage B GraphDB SSOT, role family, typed edges, sliding-scale dry-run, and active sliding-scale enforcement; it also compares each adjacent stage transition for all targets and lanes.
- Status: TODO

DoD-11: Final text anti-overfit remains active.
- Evidence: Existing or updated tests cover copied JD phrasing, keyword stuffing, unsupported target-company claims, target role as past experience, repeated buzzwords, and `target_company_name_cannot_be_claimed_as_experience`.
- Status: TODO

DoD-12: Notion and disk status are synchronized.
- Evidence: Plans DB row exists with **`Status` matching the disk plan's `PLAN_STATUS`** (currently `IN_PROGRESS` — not a hardcoded `Not Started`), `Exists On Disk=true`, and `Plan File Path=plans/typed-edge-role-facet-guardrails-a6f3d2.md`; predecessor comment notes scoped supersession. Notion status tracks disk state across waves, not a fixed value.
- Status: TODO

DoD-13: Hardening contract is enforced.
- Evidence: The authority stack invariant, waterfall atomicity and E2E gate, no-silent-fallback rule, canonical traversal verdict enum, candidate-fact authority fence, diagnostic-only no-effect rule, and prompt-hack exclusion are covered by tests or runtime validators. Prompt-only changes are not accepted as closure evidence for W3, W4, or W5.
- Status: TODO

DoD-14: Graph correctness is proven by the **5-target × 11-lane graph-% breakout (2 held-out, run cold) + per-step waterfall variance**, plus **2 targets proven end-to-end** (generation + DOCX + sliding-scale enforcement). **(The original plan's core proof — must not be dropped by the cost rebaseline; see "### Graph-% + Waterfall Variance Evidence".)**
- Evidence: For the **5-target roster** (Anthropic, Brown & Brown, Truist tuned; Neo4j VP Product Management + Aveva Distinguished AI Tech Lead **held-out, frozen-config, run cold**) × all 11 generated lanes, the **graph-skill % breakout across 6 dimensions** (role family, role facet, pillar, source-fact-family, employer scope, metric type) is produced via `tools/apps_rg/selection_diagnostic.py` (selection-based, non-generation, cheap) at **every stage A–D for all 5 targets** and **E0/E1 for the 2 live targets**; and via `tools/apps_rg/graph_skill_utilization_report.py` (assembly-based, authoritative) for each **live** target once it reaches 11/11. Each stage carries a **per-step variance** vs the immediately-prior stage AND immutable Stage A, per target/lane, with every material (|Δ|≥3pp) delta tagged expected/unexpected; control stages (B0, E0) show all cells ≤|3pp|. The held-out rows pass **without tuning** (or are logged as training points if not). **Scoped claim:** selection correctness proven for 5 role families (2 cold); generation/DOCX/enforcement proven for 2. The W5.4 waterfall report joins the full A→B0→B→C→D→E0→E1 chain (5 targets A–D, 2 live E0/E1; subsumes DoD-10A).
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=typed-edge-role-facet-guardrails-a6f3d2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=typed-edge-role-facet-guardrails-a6f3d2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

**Self-authorization limit (AUTHORIZATION_STATUS: REQUIRED phases).** For any phase marked `AUTHORIZATION_STATUS: REQUIRED` (W2–W5), `authorized_by=self` may ONLY produce `decision=REJECTED`, `DEFERRED`, or `SPLIT_TO_NEW_PLAN`. A `decision=ACCEPTED` scope expansion on a REQUIRED phase requires `authorized_by=user` or `authorized_by=author_gate` — self may never absorb new scope into a required-authorization wave.

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| `phase2-gtm-presales-remaining-f7a2c9` | Scoped supersession only: replaces the completed typed bridge-edge / role-family design posture for future traversal work. The predecessor remains historical and terminal for completed Phase 2 graph scope. |

---

## Marker Quick Reference

Wave lifecycle markers must be at start of line and use exact plan id:

```text
WAVE_START: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N>
WAVE_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 phase=<W1.1>
PLAN_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 note="<final outcome>"
```
