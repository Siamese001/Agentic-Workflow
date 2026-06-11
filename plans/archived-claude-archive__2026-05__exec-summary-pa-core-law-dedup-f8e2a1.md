---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-pa-core-law-dedup-f8e2a1.md'
original_relative_path: '_archive\\2026-05\\exec-summary-pa-core-law-dedup-f8e2a1.md'
source_sha256: 0cd5732a74dc5ccf224a72945c592e3c5e5571311a6886f04f198e36a88635b3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-pa-core-law-dedup-f8e2a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary PA Core-Law Dedup and Token Governance

Eliminate apps_rg executive-summary prompt restatement of full PA law; reference core contracts by name; keep only section-specific prose (voice, graph evidence, capped targeting, compact schema); enforce via drift tests and runtime token proof.

> **plan_id discipline**: `exec-summary-pa-core-law-dedup-f8e2a1` matches filename stem.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-24
PARENT_SPINE_PLAN: apps-rg-spine-only-unification-d8f4a2
LAST_UPDATED: 2026-05-24

---

## Context (SCQA)

- **Situation** — Executive summary compiles via `apps_rg` `PromptCompiler` with slot bodies from [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml). `pa_template_ref: strategic_tailor_v1` is slot-order shell only; **agentic_core jinja slots are not merged** at runtime. Dedup v2 (`EXEC_SUMMARY_PROMPT_DEDUP_V2`) and capsule/targeting-cap already brought Brown & Brown to `REAL_LLM` (~7.6k tokens vs 13.8k avail; [exec_summary_20260522_084114](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_084114/)).
- **Complication** — Static slots still **restate** RG-wide PA themes (NO FABRICATION, claim_ledger, JD-not-proof) inside `proof_law_v1` and S0. X2 gate catalogs appear in I0, `_EXEC_SUMMARY_X2_GATE_REFS`, R0 prose, PRODUCT_SHAPE, and SRFS oneshot (~+4k when SRFS path). Phrase echo on compiled prompts: `claim_ledger` ~10×, `x2_exec_summary_*` ~9×, `ALLOWED_SOURCE_FACT_IDS` ~8×.
- **Question** — How do we align apps_rg executive-summary slots with the mental model “core PA law by reference only; apps_rg owns writing behavior only” without weakening X2 or product evidence authority?
- **Answer** — Introduce shared `pa_core_law_v1` contract IDs; slim exec template to pointers + section blocks; make **PRODUCT_SHAPE** the sole in-prompt gate catalog; cap SRFS style replay when capsule is active; add drift tests and smoke proof.

---

## Mental Model (Governance)

| Layer | Allowed in apps_rg exec slots |
|-------|------------------------------|
| **Reference only** | `pa_truth_oath_v1`, `pa_proof_binding_v1`, `pa_targeting_only_v1`, `pa_untrusted_data_fence_v1` |
| **Section prose** | `north_star_synthesis_contract`, `credential_policy_v1`, `composition_heuristics`, E0 style, `graph_only_generation_quality` |
| **Runtime append** | `INPUT_AUTHORITY` (substrate pointer), `PRODUCT_SHAPE` (sole X2 gate/bounds list) |
| **Data (not law)** | C0 facts, evidence capsule, capped JD/briefing |

**Forbidden:** Full restatement of strategic_tailor S0 eight-point oath or generic I0 evidence-tier essay inside exec I0/S0.

**Not in scope:** Changing `agentic_core` jinja or L2 W6 `PromptAssembler` (exec lane does not use them today).

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.2 | Core law SSOT + contract registry | ~25K | strategic_tailor S0 remains canonical full oath until extracted | ✅ DONE | `pa_core_law_v1.yaml` exists; exec template references by ID |
| W2 | W2.1–W2.3 | Exec slot slim + compile path | ~35K | `PromptAssemblyInput` still requires `NO FABRICATION` literal in S0 | ✅ DONE | Gate triplication removed; tests green |
| W3 | W3.1–W3.2 | SRFS/capsule + drift enforcement | ~20K | Capsule default on product path | ✅ DONE | SRFS oneshot skips gates; drift tests fail on regression |
| W4 | W4.1 | Runtime proof + receipt | ~15K | Qwen available for Brown & Brown | ✅ DONE | `REAL_LLM` + `dispatch_allowed: true` receipt |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W1.1 | Define `pa_core_law_v1` contracts | `apps_rg/prompt_assembly/pa_core_law_v1.yaml`, `strategic_tailor_v1` header | No shared SSOT for “core law” name | ~12K | ✅ DONE |
| W1.2 | Validator: reference-not-restate | `tests/unit/apps_rg/prompt_assembly/`, `contracts.py` | S0 oath validator blocks one-liner-only | ~13K | ✅ DONE |
| W2.1 | Slim I0/S0 to pointers | `executive_summary.generate_scratch_v1.yaml` | `proof_law_v1` still full prose | ~10K | ✅ DONE |
| W2.2 | Single gate catalog (PRODUCT_SHAPE only) | `executive_summary_pa.py`, `section_product_shape_ssot.py` | `_EXEC_SUMMARY_X2_GATE_REFS`, R0 gate list duplicate | ~12K | ✅ DONE |
| W2.2b | Allowlist dedup | deferred | Duplicate JSON allowlist | ~5K | DEFERRED |
| W2.3 | Contract tests update | `test_exec_summary_pa_compiled_prompt.py`, `test_executive_summary_prompt_dedup_v2.py` | Hash stability | ~8K | ✅ DONE |
| W3.1 | SRFS oneshot diet | `executive_summary_pa.py` SRFS formatters | Reinlines E0 + PRODUCT_SHAPE | ~10K | ✅ DONE |
| W3.2 | Prompt drift ratchet | `test_exec_summary_prompt_drift_ratchet.py` | No CI guard on `x2_` in I0 | ~10K | ✅ DONE |
| W4.1 | Brown smoke + token receipt | [exec_summary_20260522_090529](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_090529) | Regression to TOKEN_BUDGET block | ~15K | ✅ DONE |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Core law SSOT | ✅ DONE | test_pa_core_law_v1 | pa_core_law_v1.yaml, contracts.py |
| W2 | Exec slot slim | ✅ DONE | dedup_v2, drift ratchet, contract tests | executive_summary.generate_scratch_v1.yaml, executive_summary_pa.py |
| W3 | SRFS + drift | ✅ DONE | test_exec_summary_prompt_drift_ratchet | executive_summary_pa.py SRFS diet |
| W4 | Runtime proof | ✅ DONE | 50 pytest + Brown smoke | exec_summary_20260522_090529, closeout receipt |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | pa_core_law_v1 contracts | ✅ DONE |
| W1.2 | Reference-not-restate validator | ✅ DONE |
| W2.1 | Slim S0/I0 pointers | ✅ DONE |
| W2.2 | PRODUCT_SHAPE-only gates | ✅ DONE |
| W2.3 | Contract tests | ✅ DONE |
| W3.1 | SRFS oneshot diet | ✅ DONE |
| W3.2 | Drift ratchet tests | ✅ DONE |
| W4.1 | Brown smoke proof | ✅ DONE |

---

## Out Of Scope

- Editing `agentic_core/**` generic prompt jinja or L2 `PromptAssembler` (unless later unified PA program).
- Weakening X2 gates, fixtures, or `section_product_shape_ssot` numeric bounds.
- Removing E0 many-shot from L2 execute path (style calibration stays).
- Premium-model escalation / L2 tiering (separate plan).
- Whole-run `PHASE1_NO_RUN_DIR` lane wiring (separate plan).

---

## Wave 1 — Core Law SSOT and Contract Names

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Add `apps_rg/prompt_assembly/contracts/pa_core_law_v1.yaml` with stable blocks: `pa_truth_oath_v1`, `pa_proof_binding_v1`, `pa_targeting_only_v1`, `pa_untrusted_data_fence_v1` (content sourced from [strategic_tailor_v1.yaml](apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml) S0/D0, not duplicated in exec template). | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Document in template header: exec loads scratch yaml only; `strategic_tailor_v1` is **forbidden** as slot body source for executive_summary. Optional: relax `PromptAssemblyInput` S0 check to accept `pa_truth_oath_v1` token + one-line bound. | ~13K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Contract file validates (YAML schema or unit test).
- Grep docs: no instruction to load strategic_tailor bodies for exec.

---

## Wave 2 — Executive Summary Slot Slim and Compile Path

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Replace I0 `<proof_law_v1>` body with: `Implements pa_proof_binding_v1 + pa_targeting_only_v1 (see pa_core_law_v1).` Keep section-only: `credential_policy_v1`, `north_star_synthesis_contract`, `composition_heuristics`, `internal_deliberation_controls`, compact `output_contract` / `self_check_requirements`. S0: `NO FABRICATION: governed by pa_truth_oath_v1; bound: C0 + ALLOWED_SOURCE_FACT_IDS.` | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Remove `_EXEC_SUMMARY_X2_GATE_REFS` from PA; remove R0 “Gate refs:” prose; I0 says “X2 gates: see appended PRODUCT_SHAPE only.” Ensure `format_product_shape_prompt_block` is complete for all proof/style/bounds gates. | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Update contract tests; add assertion: compiled prompt has exactly one block listing `x2_exec_summary_sentence_count_4_5` gate ID in PRODUCT_SHAPE (not in I0 body). | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Static slot token estimate (minimal JD/briefing, no SRFS) &lt; ~6.5k (down from ~4.5k law+style baseline + gate echo).
- All exec-summary pytest selectors pass.

---

## Wave 3 — SRFS / Capsule Discipline and Drift Ratchet

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — When `evidence_capsule_active`: skip SRFS oneshot entirely (already partial). When SRFS required: strip `srfs_product_shape` X2 lists; point to PRODUCT_SHAPE; do not re-embed E0 exemplar paragraphs (reference example IDs only). | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Add `tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py`: fail if I0/R0 contain `x2_` gate ID literals; fail if `proof_law_v1` body &gt; N lines; fail if `&lt;proof_law_v1&gt;` count &gt; 1 in template. | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- SRFS compile delta vs non-SRFS &lt; ~2k tokens when capsule on.
- Drift tests fail on intentional regression fixture.

---

## Wave 4 — Runtime Proof

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Run Brown & Brown exec summary; capture [token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/) + `REAL_LLM`; write closeout receipt under `docs/reports/apps_rg/`. | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/test_executive_summary_prompt_dedup_v2.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py tests/unit/apps_rg/runtime/sections/test_executive_summary_evidence_capsule.py tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py -o addopts= -q

python -m apps_rg --section executive_summary ^
  --target-company "Brown & Brown" ^
  --target-role "SVP IT Strategy & Innovation" ^
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt ^
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md ^
  --provider qwen_vllm --allow-non-allow-exit-zero
```

**Acceptance**:
- `dispatch_allowed: true`, `capsule_applied: true`, `runtime_generation_status: REAL_LLM`.

---

## Gap Register

**GAP-1: apps_rg vs agentic_core “core PA” boundary**
- Full eight-point oath today lives in **apps_rg** `strategic_tailor_v1`, not agentic_core jinja. Extracting `pa_core_law_v1` is apps_rg-local unless a later platform program moves oath to `agentic_core/prompt_governance`.
- Impact: W1 scope stays in `apps_rg/prompt_assembly/` only.

**GAP-2: S0 validator requires `NO FABRICATION` literal**
- [contracts.py](apps_rg/prompt_assembly/contracts.py) blocks pure pointer S0 until W1.2 relaxes or dual-checks `pa_truth_oath_v1`.

**GAP-3: SRFS path still ~+4k tokens without capsule**
- Product path should prefer capsule; SRFS-only dev runs may still need SRFS diet (W3.1).

---

## Definition of Done

DoD-1: `pa_core_law_v1` contract file exists and exec template references it by name (no full oath prose in I0).
- Evidence: `tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py` pass
- Status: PASS

DoD-2: Compiled exec prompt has single X2 gate catalog (PRODUCT_SHAPE append only).
- Evidence: drift ratchet test pass; grep compiled fixture `x2_exec_summary` gate lines only under PRODUCT_SHAPE
- Status: PASS

DoD-3: Executive summary contract pytest suite green (zero regressions).
- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_prompt_dedup_v2.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py tests/unit/apps_rg/runtime/sections/test_executive_summary_evidence_capsule.py tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py` → 0 fail
- Status: PASS

DoD-4: Brown & Brown smoke — REAL_LLM with token budget PASS.
- Evidence: `python -m apps_rg --section executive_summary` (Brown paths) exit 0; [token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_090529/token_budget_receipt.json) status PASS, `dispatch_allowed: true`
- Status: PASS

DoD-5: Plan registered in Notion Plans DB with `Exists On Disk=true`, closeout receipt linked.
- Evidence: Notion row slug `exec-summary-pa-core-law-dedup-f8e2a1`; `docs/reports/apps_rg/exec_summary_pa_core_law_dedup_closeout_receipt.md`
- Status: PASS

### Verification vs Deferral

| Item | Verify in this plan | Deferred |
|------|---------------------|----------|
| Exec slot dedup + gate single-catalog | W2–W4 | — |
| Unified core/agentic_core PA package | — | Platform PA unification |
| Premium L2 tiering | — | Separate plan |
| Whole-run lane PHASE1 pointer | — | fix-whole-run-exec plan |
| Other sections (headline, competencies) same pattern | — | Follow-on burndown |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers per template.

---

## Marker Quick Reference

```
PLAN_CREATED: slug=exec-summary-pa-core-law-dedup-f8e2a1 path=.cursor/plans/exec-summary-pa-core-law-dedup-f8e2a1.md status=Not Started
WAVE_START: plan=exec-summary-pa-core-law-dedup-f8e2a1 wave=1
WAVE_COMPLETE: plan=exec-summary-pa-core-law-dedup-f8e2a1 wave=1 note="+N tests, N files, scope=pa-core-law"
PLAN_COMPLETE: plan=exec-summary-pa-core-law-dedup-f8e2a1 note="exec PA dedup shipped; Brown REAL_LLM"
```

---

## Related Artifacts

- Prior dedup work: `EXEC_SUMMARY_PROMPT_DEDUP_V2` in [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml)
- Overlap analysis: chat session 2026-05-22 (exec summary prompt slots vs core PA)
- Proof run: [exec_summary_20260522_084114](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_084114/)
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
