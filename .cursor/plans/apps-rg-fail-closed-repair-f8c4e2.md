---
plan_id: apps-rg-fail-closed-repair-f8c4e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg Product Fail-Closed + Counted Repair Policy (P0 / P1 / P2)

Stop “finish the resume over fidelity” on product runs: stale/mock lane evidence cannot win, failures stay visible, and bounded repairs are mechanical or counted regen with ledger proof.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: P2
LAST_UPDATED: 2026-05-22
NOTION_STATUS: Completed
DISK_SSOT: .cursor/plans/apps-rg-fail-closed-repair-f8c4e2.md

---

## Context (SCQA)

- **Situation** — `apps_rg` modular full-resume runs could roll up failed/mock/phase0 lane artifacts, skip narrative LLM when companion bullets were not finalized, and pass X2 after silent deterministic rewrites. Seven generated lanes each had local repair stacks with no shared product-quality authority.
- **Complication** — Product quality could read PASS while the scored attempt failed or while code rewrote display text to satisfy gates. Phase0 synthetic stubs could masquerade as lane evidence. Repairs were not counted or surfaced in package disposition.
- **Question** — How do we enforce fail-closed product assembly and document bounded repairs without hiding first-attempt failure?
- **Answer** — P0 pointer/status fail-closed; P1 `section_repair_ledger.json` per lane with PASS only when authoritative attempt + X2 align; P2 phase0 isolation and package-test harness alignment.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| P0 | P0.1–P0.4 | Pointer policy, product quality FAIL, phase-1 fail-fast, companion preflight | ~35K | `APPS_RG_WHOLE_RUN_ENVELOPE` / correlated CLI | ✅ DONE | No stale/mock rollup; narratives blocked without finalized bullets |
| P1 | P1.1–P1.3 | Repair ledger SSOT + all 7 lanes wired + product PASS rules | ~45K | Regen replaces L2 and re-runs X2 | ✅ DONE | Ledger blocks deterministic_rewrite pass without authoritative regen |
| P2 | P2.1–P2.3 | Phase0 product block, judge-safe off on product, contract fixtures | ~15K | Retrospective completion | ✅ DONE | Phase0 blocked on product; 44+ unit/contract tests green |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | Successful-pointer-only resolution | `modular_lane_adapter.py`, `runtime_proof_layout.py`, `companion_bullet_finalization.py` | `latest_real` / mock fallback | ~10K | ✅ DONE |
| P0.2 | Product quality FAIL not PARTIAL | `mock_runtime_proof_policy.py`, `product_output_policy.py`, `resume_package_disposition.py` | Mock/blocked counted as PASS | ~8K | ✅ DONE |
| P0.3 | Phase-1 fail-fast | `modular_resume_generation.py` | Phase-1 continued after lane FAIL | ~10K | ✅ DONE |
| P0.4 | Companion narrative preflight | `unify_narrative_lane.py`, `ibm_narrative_*`, contracts | LLM without finalized bullets | ~7K | ✅ DONE |
| P1.1 | Repair ledger + policy SSOT | `section_repair_ledger.py`, `section_repair_policy.py`, `section_repair_lane_integration.py` | No shared repair truth | ~12K | ✅ DONE |
| P1.2 | Wire all generated lanes | `executive_summary_lane.py`, `headline_lane.py`, bullets/narrative/competencies lanes, `section_authority_repairs.py` | Silent surgery | ~25K | ✅ DONE |
| P1.3 | Ledger unit tests | `test_section_repair_ledger_p1.py`, `test_product_fail_closed_p0.py` | No regression harness | ~8K | ✅ DONE |
| P2.1 | Phase0 isolation on product | `modular_resume_generation.py`, `product_output_policy.py` | Phase0 PASS on product path | ~5K | ✅ DONE |
| P2.2 | Judge-safe + package harness | `executive_summary_judge_remediation.py`, `test_resume_package_x3.py` | SRFS prefilter on product | ~5K | ✅ DONE |
| P2.3 | Proof bundle | pytest unit + contract slice | — | ~5K | ✅ DONE |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| P0 | Fail-closed pointers + phase-1 | ✅ DONE | 15 | companion + product_fail_closed_p0 |
| P1 | Counted repair ledger | ✅ DONE | 6 | 16 runtime + 2 test files |
| P2 | Phase0 isolation + harness | ✅ DONE | 2 | modular_resume + resume_package tests |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| P0.1 | Successful-pointer-only | ✅ DONE |
| P0.2 | Product quality FAIL | ✅ DONE |
| P0.3 | Phase-1 fail-fast | ✅ DONE |
| P0.4 | Companion preflight | ✅ DONE |
| P1.1 | Ledger SSOT | ✅ DONE |
| P1.2 | All lanes wired | ✅ DONE |
| P1.3 | Ledger tests | ✅ DONE |
| P2.1 | Phase0 block | ✅ DONE |
| P2.2 | Judge-safe + package | ✅ DONE |
| P2.3 | Proof | ✅ DONE |

---

## Design — Repair policy (locked)

| Kind | Allowed on product | Ledger | Product PASS |
|------|-------------------|--------|--------------|
| **Scored attempt 1** | First LLM → X2 snapshot | `attempt_1_x2_failed` recorded | Only if no blocking repairs |
| **Mechanical** | Parse JSON retry, fact-id typo, tail sanitize, pre-X2 coerce | `kind=mechanical` | Does not bump authoritative attempt |
| **Regen LLM** | Bounded same-authority regen | `kind=regen_llm`, `replaced_l2=true` | Requires `authoritative_attempt_number≥2` + X2 pass |
| **Deterministic rewrite** | **Blocked** (graph-only, display fallback, metric restore, capability projection) | `kind=deterministic_rewrite` | **FAIL** unless followed by counted regen |

Artifact per lane run: `section_repair_ledger.json` + `l2_output` fields `authoritative_attempt_number`, `authoritative_l2_source`.

---

## Out Of Scope

- Live qwen proof receipt (W4 SRFS skip-PASS burndown plan)
- Deleting competencies capability_projection module (simplification burndown)
- `agentic_core` spine changes
- Weakening X2/X3 gates

---

## Definition of Done

| ID | Criterion | Verification | Status |
|----|-----------|--------------|--------|
| D1 | Product runs resolve only `latest_successful_real_run.json` + product bar | `test_product_fail_closed_p0.py` | ✅ |
| D2 | Non-REAL_LLM → product_quality FAIL on product path | `infer_product_quality_blocked_or_mock` + envelope tests | ✅ |
| D3 | All 7 lanes emit repair ledger | `test_all_generated_lanes_have_repair_ledger_wiring` | ✅ |
| D4 | Deterministic rewrite cannot PASS without regen | `test_ledger_blocks_pass_after_deterministic_rewrite` | ✅ |
| D5 | Phase0 synthetic blocked when `product_fail_closed_runtime()` | `test_modular_phase0_blocked_on_product_fail_closed` | ✅ |
| D6 | Resume package synthetic fixtures use test harness | `test_resume_package_x3.py` 22 passed | ✅ |

### Verification vs Deferral

| Item | Verified in this plan | Deferred |
|------|----------------------|----------|
| Ledger on all lanes | D3 + code review | — |
| Live full-resume qwen run | — | W4 live proof (separate plan) |
| SRFS gate emission removal | — | `apps-rg-x2-dead-gates-burndown-c4e8f2` W4 |

---

## Proof commands (executed 2026-05-22)

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/runtime/test_section_repair_ledger_p1.py \
  tests/unit/apps_rg/runtime/test_product_fail_closed_p0.py \
  tests/unit/apps_rg/runtime/validators/test_companion_bullet_fail_closed.py \
  tests/_apps_contract/test_resume_package_x3.py \
  tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py \
  -o addopts= -q
# Result: 44 passed
```

---

## FILES_CHANGED (chat scope)

- [section_repair_ledger.py](apps_rg/runtime/section_repair_ledger.py)
- [section_repair_policy.py](apps_rg/runtime/section_repair_policy.py)
- [section_repair_lane_integration.py](apps_rg/runtime/section_repair_lane_integration.py)
- [product_output_policy.py](apps_rg/runtime/product_output_policy.py)
- [modular_resume_generation.py](apps_rg/l2_recipe/modular_resume_generation.py)
- [section_authority_repairs.py](apps_rg/runtime/sections/section_authority_repairs.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_judge_remediation.py](apps_rg/runtime/sections/executive_summary_judge_remediation.py)
- [headline_lane.py](apps_rg/runtime/sections/headline_lane.py)
- [unify_narrative_lane.py](apps_rg/runtime/sections/unify_narrative_lane.py)
- [ibm_narrative_lane_execution.py](apps_rg/runtime/sections/ibm_narrative_lane_execution.py)
- [ibm_narrative_lane_runtime.py](apps_rg/runtime/sections/ibm_narrative_lane_runtime.py)
- [competencies_lane_execution.py](apps_rg/runtime/sections/competencies_lane_execution.py)
- [competencies_lane_runtime.py](apps_rg/runtime/sections/competencies_lane_runtime.py)
- [unify_bullets_lane.py](apps_rg/runtime/sections/unify_bullets_lane.py)
- [ibm_bullets_lane.py](apps_rg/runtime/sections/ibm_bullets_lane.py)
- [test_section_repair_ledger_p1.py](tests/unit/apps_rg/runtime/test_section_repair_ledger_p1.py)
- [test_product_fail_closed_p0.py](tests/unit/apps_rg/runtime/test_product_fail_closed_p0.py)
- [test_resume_package_x3.py](tests/_apps_contract/test_resume_package_x3.py)

---

PLAN_COMPLETE: plan=apps-rg-fail-closed-repair-f8c4e2 status=Completed waves=P0,P1,P2
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
