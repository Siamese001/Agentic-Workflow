---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\sections-pa-core-law-rollout-c3a8f1.md'
original_relative_path: '_archive\\2026-05\\sections-pa-core-law-rollout-c3a8f1.md'
source_sha256: d0eb64be73b3f85318c3e42e309e56a9968b87f9c95897d24e4afdba0e484b7d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: sections-pa-core-law-rollout-c3a8f1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Sections PA Core-Law Rollout (Headline, Unify/IBM, Competencies)

Roll out the executive-summary PA dedup and token-governance pattern to **headline**, **competencies**, and **Unify/IBM** lanes (bullets + position narratives). Reuse [pa_core_law_v1.yaml](apps_rg/prompt_assembly/pa_core_law_v1.yaml); keep section-specific prose only; make **PRODUCT_SHAPE** the sole in-prompt X2 gate catalog; add drift ratchets and per-lane runtime proof.

> **plan_id discipline**: `sections-pa-core-law-rollout-c3a8f1` matches filename stem.  
> **Predecessor (complete):** [exec-summary-pa-core-law-dedup-f8e2a1.md](exec-summary-pa-core-law-dedup-f8e2a1.md) · [closeout receipt](docs/reports/apps_rg/exec_summary_pa_core_law_dedup_closeout_receipt.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Complete
CURRENT_WAVE: W6
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-05-22

---

## Review — Executive Summary Work Completed (Reference)

### What was fixed (exec lane)

| Theme | Before | After |
|-------|--------|--------|
| Core PA law | Full NO FABRICATION + proof essays in S0/I0/`proof_law_v1` | Reference `pa_truth_oath_v1`, `pa_proof_binding_v1`, `pa_targeting_only_v1`, `pa_untrusted_data_fence_v1` in [pa_core_law_v1.yaml](apps_rg/prompt_assembly/pa_core_law_v1.yaml) |
| X2 gate catalog | Triplicated in I0, R0, `_EXEC_SUMMARY_X2_GATE_REFS`, PRODUCT_SHAPE, SRFS oneshot | **PRODUCT_SHAPE append only** ([executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)) |
| SRFS replay | Re-embedded E0 + gate lists | Compact oneshot when [evidence capsule](apps_rg/runtime/sections/executive_summary_evidence_capsule.py) active |
| Token path | Risk of TOKEN_BUDGET block | Brown proof: 7003 / 13824 tokens, `dispatch_allowed: true`, `capsule_applied: true` ([exec_summary_20260522_090529](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_090529)) |
| Enforcement | Ad hoc | [test_exec_summary_prompt_drift_ratchet.py](tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py), dedup v2 / CORE_LAW_V3 markers |

### Mental model — scope boundaries (platform vs apps_rg)

| Layer | Owns | Does **not** own |
|-------|------|------------------|
| **agentic_core** | Generic L2 `PromptAssembler`, jinja slot packs, cross-app PA shells (when a lane uses them) | apps_rg section display rules, employment-scoped fact IDs, RG X2 gate implementations |
| **apps_rg PA compile** | Section templates (`*_v1.yaml`), `PromptAssemblyInput`, runtime append blocks | Duplicating full strategic_tailor eight-point oath in every section |
| **Runtime append (all GENERATED_LANES)** | [INPUT_AUTHORITY](apps_rg/runtime/dispatch/input_authority_prompt_block.py) + [PRODUCT_SHAPE](apps_rg/runtime/sections/section_product_shape_ssot.py) | Re-listing the same X2 IDs inside static I0/R0 |
| **Section prose (allowed)** | North-star task, slice hygiene (bul_unify_*), rewrite distribution, JSON shape, E0 style calibration | Generic claim_ledger tutorial repeated per slot |

**Compile-path truth (today):** No executive-summary lane merges agentic_core jinja at runtime. Unify/IBM bullets compile via `strategic_tailor_v1` **slot order** + [w7_strategic_tailor_shell_slots.yaml](apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml) + large `_legacy_i0()` strings in `*_pa.py` — **not** by loading `unify_bullet_tailor_v1.yaml` / `ibm_bullet_tailor_v1.yaml` bodies into the compiler (those YAML files are spec/SSOT drift risk until wired or trimmed).

**Forbidden after rollout:** Restating `pa_core_law_v1` contract bodies in S0/I0 when PRODUCT_SHAPE + INPUT_AUTHORITY already carry proof/X2 authority.

---

## Context (SCQA)

- **Situation** — Exec summary rollout is **COMPLETE** (marker `EXEC_SUMMARY_PROMPT_CORE_LAW_V3`, 50 pytest, Brown REAL_LLM). Other generated lanes already receive PRODUCT_SHAPE via `finalize_section_compiled_with_proof_pool` / `augment_section_compiled_with_input_authority`, but **static slots still restate governance** and inflate tokens.
- **Complication (measured static template / I0 bulk):**

| Lane | Primary prompt SSOT | ~chars | `NO FABRICATION` / oath | `claim_ledger` echoes | PRODUCT_SHAPE at runtime |
|------|---------------------|--------|-------------------------|----------------------|---------------------------|
| headline | [headline_tailor_v1.yaml](apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml) | ~18.8k | 1× full task_contract + evidence_hierarchy essay | ~10× in YAML | Yes (via INPUT_AUTHORITY path) |
| competencies | [competency_selector_v2.pa_slots.yaml](apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml) | ~3.8k | Full S0 oath block | 1× (+ I0 rules) | Yes (`finalize_section_compiled_with_proof_pool`) |
| unify_bullets | `_legacy_i0()` in [unify_bullets_pa.py](apps_rg/runtime/sections/unify_bullets_pa.py) + w7 shell | ~4k+ I0 inline | w7 S0 + inline “Source Authority” essay | 6+ in I0 | Yes |
| unify_narrative | [unify_position_narrative_v1.yaml](apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml) + PA | ~17k YAML spec | `sovereign_oath` block | 6× | Yes |
| ibm_bullets | `_legacy_i0()` in [ibm_bullets_pa.py](apps_rg/runtime/sections/ibm_bullets_pa.py) + w7 shell | ~3k+ I0 inline | w7 S0 + forbidden-terms essay | 7+ in I0 | Yes |
| ibm_narrative | [ibm_position_narrative_v1.yaml](apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml) + PA | ~19.5k YAML | `sovereign_oath` + x2 mention | 16× | Yes |

- **Question** — How do we apply the exec-summary dedup playbook without weakening X2, SRFS slice rules, or deterministic locked content (Unify/IBM facts)?
- **Answer** — Per-section waves: pointer S0/D0/I0 → single gate catalog in PRODUCT_SHAPE only → diet runtime I0 / YAML spec → shared drift ratchet tests → Brown (or lane-default) smoke with token receipts where budget gates exist.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success criteria |
|------|-----------|-------|-------------|--------|------------------|
| W0 | W0.1 | Baseline inventory + compiled-prompt fingerprints | ~12K | ✅ DONE | [w0_baseline.md](docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.md) |
| W1 | W1.1–W1.2 | Shared contracts + compile conventions | ~15K | ✅ DONE | w7 shell + template headers reference `pa_core_law_v1` |
| W2 | W2.1 | Headline slim | ~25K | ✅ DONE | ~7.2k YAML chars (~66% vs W0); static slots ~1.8k tokens; drift ratchet green |
| W3 | W3.1 | Competencies slim | ~15K | ✅ DONE | pa_slots ~3.8k chars, ~1.1k static tokens; X2 in PRODUCT_SHAPE only; drift ratchet green |
| W4 | W4.1–W4.4 | Unify/IBM bullets + narratives | ~45K | ✅ DONE | I0 pa_core_law slim; YAML oath trimmed; drift ratchet + contract tests green |
| W5 | W5.1 | Drift ratchets + pytest | ~20K | ✅ DONE | 63 pytest PASS; [w5_pytest_gate.md](docs/reports/apps_rg/sections_pa_core_law_rollout_w5_pytest_gate.md); rollup asserts single PRODUCT_SHAPE |
| W6 | W6.1–W6.3 | Runtime proof + closeout | ~25K | ✅ DONE (PARTIAL) | 4/6 REAL_LLM; all lanes PRODUCT_SHAPE×1 + pa_core_law; [closeout](docs/reports/apps_rg/sections_pa_core_law_rollout_closeout_receipt.md) |

---

## Phase-Level Summary

| Phase | Title | Scope | Status |
|-------|-------|-------|--------|
| W0.1 | Baseline compile fingerprints | Brown JD + briefing; `core_law_rollout_w0_20260522_093143` | ✅ DONE |
| W1.1 | Extend w7 shell to pa_core_law refs | [w7_strategic_tailor_shell_slots.yaml](apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml) v1.1 | ✅ DONE |
| W1.2 | Section marker + validator hints | HEADLINE/COMPETENCIES/UNIFY_IBM markers; [pa_core_law.py](apps_rg/prompt_assembly/pa_core_law.py) helpers | ✅ DONE |
| W2.1 | Headline template dedup | [headline_tailor_v1.yaml](apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml), drift ratchet tests | ✅ DONE |
| W3.1 | Competencies template dedup | [competency_selector_v2.pa_slots.yaml](apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml), drift ratchet | ✅ DONE |
| W4.1 | Unify bullets I0 diet | [unify_bullets_pa.py](apps_rg/runtime/sections/unify_bullets_pa.py) | ✅ DONE |
| W4.2 | Unify narrative diet | [unify_narrative_pa.py](apps_rg/runtime/sections/unify_narrative_pa.py), YAML spec trim | ✅ DONE |
| W4.3 | IBM bullets I0 diet | [ibm_bullets_pa.py](apps_rg/runtime/sections/ibm_bullets_pa.py) | ✅ DONE |
| W4.4 | IBM narrative diet | [ibm_narrative_pa.py](apps_rg/runtime/sections/ibm_narrative_pa.py), YAML spec trim | ✅ DONE |
| W5.1 | Drift + contract tests | [test_sections_pa_core_law_w5_rollup.py](tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py), [sections_pa_core_law_w5_pytest_gate.py](ops_scripts/apps_rg/sections_pa_core_law_w5_pytest_gate.py) | ✅ DONE |
| W6.1 | Headline smoke | [headline_20260522_101600](artifacts/apps_rg/runtime_proofs/headline/real/headline_20260522_101600) | ✅ REAL_LLM |
| W6.2 | Competencies smoke | [competencies_20260522_101716](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260522_101716) | ✅ REAL_LLM |
| W6.3 | Unify/IBM smoke | [w6_smoke.md](docs/reports/apps_rg/sections_pa_core_law_rollout_w6_smoke.md) + closeout | ✅ PARTIAL (narratives upstream-blocked isolated) |

---

## Wave 0 — Baseline

WAVE_ID: W0  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  

**W0.1** — For each lane, compile with representative Brown payload (or existing contract fixtures); record:

- `compiled_prompt_tokens` (same estimator as exec: chars/3 × 1.12)
- Counts: `NO FABRICATION`, `claim_ledger`, `x2_<section>_` in static slots vs PRODUCT_SHAPE block
- Save under `artifacts/apps_rg/runtime_proofs/<lane>/baseline/core_law_rollout_w0_<ts>/`

**Acceptance:** Table in closeout draft; identifies headline + IBM narrative as P0 token debt.

---

## Wave 1 — Shared Core Law (Reuse Exec SSOT)

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  

**W1.1** — Replace w7 shell S0/D0 one-liners with `pa_core_law_v1` references (keep employment-scoped rules in lane I0 only).

**W1.2** — Add template markers:

- `HEADLINE_PROMPT_CORE_LAW_V3`
- `COMPETENCIES_PROMPT_CORE_LAW_V3`
- `UNIFY_IBM_PROMPT_CORE_LAW_V3`

Document in each template header: `forbidden_slot_body_source: strategic_tailor_v1` (full bodies).

**Acceptance:** [test_pa_core_law_v1.py](tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py) still passes; no new `agentic_core` edits.

---

## Wave 2 — Headline

WAVE_ID: W2  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
W2_CLOSEOUT: 2026-05-22 — headline_tailor_v1 pa_core_law slim (~7.2k chars); drift + contract tests green

**Target files:** [headline_tailor_v1.yaml](apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml), [headline_pa.py](apps_rg/runtime/sections/headline_pa.py), [test_headline_pa_compiled_prompt.py](tests/_apps_contract/test_headline_pa_compiled_prompt.py)

**W2.1 actions:**

1. S0: `NO FABRICATION: governed by pa_truth_oath_v1` + north_star_task + task_contract **section-only** (pipe format, word count, no metrics).
2. Collapse `<evidence_hierarchy>` to `Implements pa_proof_binding_v1 + pa_targeting_only_v1`; SRFS slice rule = one short bullet (not multi-page essay).
3. I0: JSON/claim_ledger shape only; **no** X2 gate ID literals (gates live in PRODUCT_SHAPE from [section_product_shape_ssot.py](apps_rg/runtime/sections/section_product_shape_ssot.py) `_headline_shape`).
4. R0: schema comment pointer only (mirror exec R0 pattern).
5. Keep E0/Y0; U0 in PA stays task-specific.

**Tests:** Update [test_headline_tailor_v15_prompt_quality.py](tests/unit/apps_rg/test_headline_tailor_v15_prompt_quality.py) for slimmed contracts; add `test_headline_prompt_drift_ratchet.py`.

**Risk:** Headline is highest static YAML bulk (~18k chars) — expect largest token win.

---

## Wave 3 — Competencies

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
W3_CLOSEOUT: 2026-05-22 — competency_selector_v2.pa_slots pa_core_law slim; drift + contract tests green

**Target files:** [competency_selector_v2.pa_slots.yaml](apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml), [competencies_pa.py](apps_rg/runtime/sections/competencies_pa.py)

**W3.1 actions:**

1. S0/D0: pa_core_law references; keep **category/term display** rules (6–8 categories, noun phrases, no metrics).
2. I0: construction checklist only; jd_alignment booleans pointer to `pa_targeting_only_v1`.
3. Confirm PRODUCT_SHAPE lists all [competencies X2 gates](apps_rg/runtime/sections/section_product_shape_ssot.py) `_competencies_shape` — remove any duplicate gate prose from slots.

**Tests:** Extend competencies contract tests; drift ratchet (no `x2_competencies_` in static YAML).

---

## Wave 4 — Unify / IBM (Bullets + Narratives)

WAVE_ID: W4  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
W4_CLOSEOUT: 2026-05-22 — four-lane I0 pa_core_law slim; YAML sovereign_oath trimmed; drift ratchet green

Four lanes: `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`.

**W4.1 Unify bullets** — Diet [unify_bullets_pa.py](apps_rg/runtime/sections/unify_bullets_pa.py) `_legacy_i0`:

- Move generic proof/JD-not-proof lines to pa_core_law refs.
- Keep: bul_unify_* hygiene, distribution table, protected bullet metrics, mechanism-inventory cap, fact-scope gate **names** only in PRODUCT_SHAPE.
- Align [unify_bullet_tailor_v1.yaml](apps_rg/prompt_assembly/templates/unify_bullet_tailor_v1.yaml) header with runtime SSOT (document “compile uses PA `_legacy_i0`” or wire YAML — **Author-Gate if wiring changes blast radius**).

**W4.2 Unify narrative** — Trim [unify_position_narrative_v1.yaml](apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml) `sovereign_oath` to contract refs + Unify-only scope; narrative sentence bounds stay section-specific.

**W4.3 IBM bullets** — Same pattern as W4.1 for [ibm_bullets_pa.py](apps_rg/runtime/sections/ibm_bullets_pa.py) (forbidden Unify/runtime vocab list stays — section-specific).

**W4.4 IBM narrative** — Trim [ibm_position_narrative_v1.yaml](apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml); remove inline `x2_` prose where PRODUCT_SHAPE covers it.

**Invariant:** Do not weaken locked IBM/Unify facts, rewrite distributions, or SRFS slice gates.

---

## Wave 5 — Drift Enforcement

WAVE_ID: W5  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
W5_CLOSEOUT: 2026-05-22 — drift rollup + pytest gate 63 passed; [sections_pa_core_law_rollout_w5_pytest_gate.md](docs/reports/apps_rg/sections_pa_core_law_rollout_w5_pytest_gate.md)

**W5.1** — Add ratchet tests (pattern from [test_exec_summary_prompt_drift_ratchet.py](tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py)):

| Test module | Fails when |
|-------------|------------|
| `test_headline_prompt_drift_ratchet.py` | `x2_headline_` in headline_tailor S0/I0/R0 |
| `test_competencies_prompt_drift_ratchet.py` | `x2_competencies_` in pa_slots |
| `test_unify_ibm_prompt_drift_ratchet.py` | `x2_unify_` / `x2_ibm_` in static I0 or sovereign_oath blocks |

Shared assertion: compiled prompt contains exactly one PRODUCT_SHAPE block with gate IDs for that `section_id`.

**Gate (SSOT):**

```bash
python ops_scripts/apps_rg/sections_pa_core_law_w5_pytest_gate.py
```

Rollup: [test_sections_pa_core_law_w5_rollup.py](tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py) parametrizes six lanes — exactly one `PRODUCT_SHAPE (deterministic X2 authority` block per compile; I0 free of `x2_*` gate catalogs.

---

## Wave 6 — Runtime Proof

WAVE_ID: W6  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES (PARTIAL rollup — 4/6 REAL_LLM)  
W6_CLOSEOUT: 2026-05-22 — [sections_pa_core_law_rollout_closeout_receipt.md](docs/reports/apps_rg/sections_pa_core_law_rollout_closeout_receipt.md)

**Commands (Brown & Brown targeting — adjust per lane CLI surface):**

```bash
# Headline
python -m apps_rg --section headline ^
  --target-company "Brown & Brown" ^
  --target-role "SVP IT Strategy & Innovation" ^
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt ^
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md ^
  --provider qwen_vllm --allow-non-allow-exit-zero

# Competencies (same targeting paths)

# Unify/IBM: use existing modular section CLI flags / whole-run lane order from apps_rg CLI help
```

**Acceptance per lane:**

- `runtime_generation_status: REAL_LLM` where provider available
- `dispatch_allowed: true` on token-budget-gated lanes (add headline budget gate in W2 if missing — **gap register**)
- PRODUCT_SHAPE present; static slots cite `pa_core_law_v1`
- Closeout: [sections_pa_core_law_rollout_closeout_receipt.md](docs/reports/apps_rg/sections_pa_core_law_rollout_closeout_receipt.md)

---

## Gap Register

**GAP-1: Headline lacks exec-grade token_budget module**  
Exec has [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py). Headline may rely on context window only. **Open for W6** — add budget gate or document exemption in closeout receipt.

**GAP-2: Unify/IBM YAML vs PA `_legacy_i0` drift**  
Bullet YAML marked spec-only (W4 headers). **Partial:** [ibm_narrative_pa.py](apps_rg/runtime/sections/ibm_narrative_pa.py) still injects full spec layers (~11k I0). Follow-on before/ during W6.3.

**GAP-3: X2 product quality vs token PASS**  
Exec Brown run: token PASS + X2 content FAIL is acceptable for governance DoD. Same semantics for W6.

**GAP-4: agentic_core jinja unification**  
Deferred — same as exec plan. apps_rg-only rollout.

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | W0 baseline table for 6 lane compile paths | PASS |
| DoD-2 | headline + competencies static slots use pa_core_law refs; no full oath restate | PASS (W2–W3) |
| DoD-3 | Unify/IBM four lanes: w7 shell + I0/YAML diet; no duplicate oath stacks | PASS (W4; ibm_narrative compile bulk remains GAP-2) |
| DoD-4 | Drift ratchet tests fail on `x2_` in static slots | PASS (W5 gate 63 tests) |
| DoD-5 | Contract pytest 0 fail for touched lanes | PASS (W5 gate) |
| DoD-6 | W6 REAL_LLM smoke + artifacts under `artifacts/apps_rg/runtime_proofs/` | PARTIAL (4/6 REAL_LLM) |
| DoD-7 | Notion Plans row + closeout receipt | PASS |

---

## Out Of Scope

- `agentic_core/**` prompt jinja / L2 `PromptAssembler` changes
- Weakening X2 gates, fixtures, or locked Unify/IBM canonical facts
- Executive summary re-work (complete — reference only)
- Premium model tiering, whole-run PHASE1 lane wiring
- Other sections (early_career, insurtech, certifications, education) — follow-on burndown

---

## Scope Expansion Authorization

Emit `DISCOVERED_SCOPE` / `AUTHORIZATION_DECISION` / `SCOPE_EXPANSION` per [plan-governance](.cursor/skills/plan-governance/SKILL.md) if wiring YAML into compiler or adding headline token budget crosses blast-radius threshold.

---

PLAN_CREATED: slug=sections-pa-core-law-rollout-c3a8f1 path=.cursor/plans/sections-pa-core-law-rollout-c3a8f1.md status=Not Started
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
