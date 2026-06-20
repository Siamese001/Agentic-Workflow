---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-section-judge-policy-f60c6c.md'
original_relative_path: '_archive\\2026-05\\apps-rg-section-judge-policy-f60c6c.md'
source_sha256: 2c619508623925476ec1b529ca6799173b2b9faaee5f796f1bde7cbb264f9919
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-section-judge-policy-f60c6c
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg section-specific judge policy hardening

Enforce per-resume-section judge tiers, JudgePacket GRADE_ONLY contracts, fail-closed model resolution, and proof eligibility rules across all generated `apps_rg` lanes — without touching `agentic_core` or weakening X2/X3.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CLOSURE_STATUS: CLOSED
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-18

---

## Context (SCQA)

- **Situation** — `executive_summary` already has enhanced judge profile + GRADE_ONLY JudgePacket; other lanes reuse `executive_summary_x1d` providers but use loose rubric prompts, default flash/mini fallbacks, and shared `compute_lane_proof_bundle` that treats all judges as proof-decisive.
- **Complication** — Section matrix requires ENHANCED vs STANDARD vs BULLET_REWRITE vs OPTIONAL_ADVISORY tiers; competencies must not require X1D for proof; mini/flash/mock must never count toward proof eligibility.
- **Question** — How do we centralize section judge policy and wire every lane to fail-closed proof judges + JudgePacket grading?
- **Answer** — Add `section_judge_policy.py` SSOT, shared `section_judge_profile` + `grade_only_judge_packet`, section-aware proof bundle + X3, then migrate lane X1D runners and tests.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Policy SSOT + profile + proof bundle + competencies X2/X3 | ✅ DONE | test_section_judge_policy.py | section_judge_policy, section_judge_profile, grade_only_judge_packet, mock_runtime_proof_policy, competencies_x2, executive_summary_x3 |
| W2 | JudgePacket + policy-backed X1D for headline, unify, IBM lanes | ✅ DONE | policy-backed section judges | *_x1d.py, policy_backed_section_judges.py, lane/dispatch section_id |
| W3 | Contract tests + scoped pytest + exec_summary live proof | ✅ DONE | _apps_contract judge policy + live run | tests/_apps_contract, tests/unit/apps_rg |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Canonical section_judge_policy matrix | ✅ DONE |
| W1.2 | section_judge_profile + grade_only_judge_packet | ✅ DONE |
| W1.3 | compute_lane_proof_bundle + aggregate_x3 section flags | ✅ DONE |
| W2.1 | Wire standard-tier lanes to policy-backed judges | ✅ DONE |
| W2.2 | executive_summary uses policy SSOT (re-export compat) | ✅ DONE |
| W3.1 | Policy + JudgePacket contract tests | ✅ DONE |
| W3.2 | Scoped pytest + git diff agentic_core | ✅ DONE |
| W3.3 | Live executive_summary SRFS proof (companion arsenal plan) | ✅ DONE |

---

## Out Of Scope

- `agentic_core` changes
- Generation prompt changes (except section metadata alignment if required)
- `final_aggregate_resume` live lane (policy row reserved; wire when assembler lane exists)
- Full resume orchestration proof
- Weakening X2/X3 gates

---

## Wave 3 — Verification (completed)

**Commands run**:
```bash
python -m pytest tests/unit/apps_rg/test_section_judge_policy.py -q --tb=short
python -m pytest tests/_apps_contract -q --tb=short -k "judge or x1d or competencies or executive_summary or headline or unify or ibm"
git diff HEAD -- agentic_core
```

Live executive_summary (SRFS):
```bash
python -m apps_rg --section executive_summary --selected-role-fact-set artifacts/apps_rg/fact_inventory/selected_role_fact_set_20260518T181200Z_exec_summary_srfs_cli_proof.json
```

**Live result**: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_205434` — REAL_LLM, X2 all PASS, X3_ALLOW, all three X1D judges MODEL_BACKED_PASS.

---

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|--------------|
| D1 | Canonical `section_judge_policy` matrix matches user spec | unit test `test_section_judge_policy_matrix` |
| D2 | competencies proof does not require X1D pass | unit + competencies x2 gate |
| D3 | enhanced sections use ENHANCED tier models fail-closed | profile resolver tests |
| D4 | JudgePacket GRADE_ONLY on executive_summary + headline minimum | packet builder tests |
| D5 | `git diff HEAD -- agentic_core` empty | shell |
| D6 | Scoped pytest green | pytest commands above |
| D7 | Live exec_summary proof X3_ALLOW | exec_summary_20260518_205434 |

### Verification vs deferral

| Item | Status |
|------|--------|
| final_aggregate_resume lane wiring | Deferred until assembler section exists |
| Live exec_summary proof | ✅ DONE (2026-05-18) |
