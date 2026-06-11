---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-ag8-prompt-authority-coverage-d9f4c2.md'
original_relative_path: 'apps-rg-ag8-prompt-authority-coverage-d9f4c2.md'
source_sha256: bb944c5fded7f24957ceb29b4bd0e2d0762fc4e1d9a30b698bfed10ca7d5ed8a
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-ag8-prompt-authority-coverage-d9f4c2
plan_type: hardening
dod_exempt: false
---

# AG-8 apps_rg Prompt Authority Coverage

Prompt authority hardening plan for `apps_rg` — inventories all prompt surfaces, classifies authority and stage consumption, resolves UNKNOWN_NEEDS_REVIEW rows, fixes PAB-003 U0/C0 conflation, and enforces all invariants via a 21-test suite and a CI gate.

---

## Context (SCQA)

- **Situation** — `apps_rg` has a live prompt assembly pipeline (PA binding at `agentic_core/prompt_governance/apps_rg_pa_binding.py`) assembling prompts from `rg_prompt_profile.yaml`. The pipeline lacks a formal audit of which prompt surfaces are runtime-reachable, which stages consume them, and whether authority boundaries are respected.
- **Complication** — Without a structured prompt authority inventory and stage consumption matrix, risks accumulate silently: U0/C0 conflation (PAB-003), unresolved UNKNOWN_NEEDS_REVIEW surfaces, non-content-sensitive `compilation_hash`, and no CI enforcement of any of these invariants.
- **Question** — How do we harden `apps_rg` prompt authority so that all surfaces are classified, all risks are resolved, and all invariants are continuously enforced?
- **Answer** — A 5-wave plan: W0 baseline gates, W1 prompt inventory, W2 authority classification, W3 stage consumption matrix, W4 prompt authority hardening. All waves now DONE.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W0 | W0.P1 | Baseline gates — confirm CI gate infrastructure and test harness | ~5K | ✅ DONE |
| W1 | W1.P1–W1.P3 | Prompt inventory — discover all 86 prompt surfaces, emit `ag8_prompt_authority_inventory.json` | ~20K | ✅ DONE |
| W2 | W2.P1–W2.P3 | Authority classification — classify all 86 surfaces with `authority_class`, `runtime_reachable`, `canonical_prompt_slot` | ~30K | ✅ DONE |
| W2.1 | W2.1.P1 | Blocker resolution — resolve 8 missing classifications, reconcile count to 86 | ~10K | ✅ DONE |
| W3 | W3.P1–W3.P3 | Stage consumption matrix — map all 86 surfaces to stage consumption statuses | ~25K | ✅ DONE |
| W3.1 | W3.1.P1 | Count reconciliation — explain and resolve 86 SOT count, emit reconciliation artifact | ~8K | ✅ DONE |
| W4 | W4.P1–W4.P5 | Prompt authority hardening — fix PAB-003, resolve 11 UNKNOWN rows, write 21 tests + CI gate | ~40K | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Status |
|----------|-------|---------------|--------|
| W0.P1 | Baseline gates | Existing CI gate infrastructure | ✅ DONE |
| W1.P1 | Prompt surface discovery | `rg_prompt_profile.yaml`, `apps_rg_pa_binding.py` | ✅ DONE |
| W1.P2 | Inventory artifact emit | `ag8_prompt_authority_inventory.json` | ✅ DONE |
| W1.P3 | Discovered-not-yet-classified bucket | `inventory_metadata.discovered_not_yet_classified_count=13` | ✅ DONE |
| W2.P1 | Authority class assignment | `ag8_prompt_authority_classification.json` | ✅ DONE |
| W2.P2 | Runtime reachability scoring | `runtime_reachable` field for all 86 surfaces | ✅ DONE |
| W2.P3 | Canonical slot mapping | `canonical_prompt_slot` for all 86 surfaces | ✅ DONE |
| W2.1.P1 | Count reconciliation + missing entries | `ag8_w3_1_count_reconciliation.json`, total_classified=86 | ✅ DONE |
| W3.P1 | Stage consumption matrix | `ag8_prompt_stage_consumption_matrix.json` (86 rows) | ✅ DONE |
| W3.P2 | W3 report | `ag8_w3_stage_consumption_report.md` | ✅ DONE |
| W3.P3 | UNKNOWN_NEEDS_REVIEW identification | 11 rows identified for W4 resolution | ✅ DONE |
| W3.1.P1 | Count reconciliation report | `ag8_w3_1_count_reconciliation.json` | ✅ DONE |
| W4.P1 | PAB-003 fix | `apps_rg_pa_binding.py` — split `_build_user_instruction` → `_build_u0_task_block` + `_build_c0_evidence_block` | ✅ DONE |
| W4.P2 | 11 UNKNOWN rows resolved | `ag8_prompt_authority_classification.json` + `ag8_prompt_stage_consumption_matrix.json` | ✅ DONE |
| W4.P3 | `compilation_hash` fix | Content-hash (sha256) instead of `len(content)` | ✅ DONE |
| W4.P4 | 21-test suite | `tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py` | ✅ DONE |
| W4.P5 | CI gate | `ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py` | ✅ DONE |

---

## W4 Acceptance Criteria — Final State

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 3-way count consistent at 86 (inventory / classification / matrix) | ✅ | All three JSON files: `total_items=86`, `total_classified=86`, `len(matrix)=86` |
| `discovered_not_yet_classified` bucket preserved + nonzero | ✅ | `inventory_metadata.discovered_not_yet_classified_count=13` |
| No matrix prompt_id missing classification | ✅ | test_3 green |
| Runtime prompts have `authority_class`, `contract_field_target`, `prompt_slot_target` | ✅ | test_4 + test_5 green |
| U0 does not consume generation instruction slots | ✅ | test_6 green (slot-based predicate) |
| L1 consumes only planning/domain projections (not raw generation slots) | ✅ | test_7 green (slot-based predicate) |
| L0 consumes only structured L1PlanContract fields | ✅ | test_8 + test_9 green |
| C0 does not assemble prompts | ✅ | test_10 green |
| PA is the only generation prompt assembly authority | ✅ | test_11 green |
| PA `slot_lineage_map` separates U0 task from C0 evidence (PAB-003 fixed) | ✅ | test_12 green |
| PA `component_hash_map` includes all runtime-used components | ✅ | test_13 green |
| `compilation_hash` changes with content (sha256, not len) | ✅ | test_14 green |
| Retrieved evidence remains C0-only (no instruction slot injection) | ✅ | test_15 green |
| Eval rubrics map to Exit/X1, not generation stages | ✅ | test_16 green |
| L2 does not load raw apps_rg prompts | ✅ | test_17 green |
| Exit does not assemble generation prompts | ✅ | test_18 green |
| No UNKNOWN_NEEDS_REVIEW without resolution | ✅ | test_19 green — all 11 resolved |
| No ChromaDB mutation | ✅ | test_20 green |
| No external embedding generation | ✅ | test_21 green |
| CI gate: 0 errors, 0 warnings | ✅ | `PA-COV: PASS — 0 errors, 0 warnings` |

---

## Artifacts Emitted

| Artifact | Description |
|----------|-------------|
| `artifacts/apps_rg/ag8_prompt_authority_inventory.json` | 86-surface prompt inventory with `discovered_not_yet_classified` bucket |
| `artifacts/apps_rg/ag8_prompt_authority_classification.json` | Full authority classification for all 86 surfaces |
| `artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json` | Stage consumption matrix for all 86 surfaces |
| `artifacts/apps_rg/ag8_w3_stage_consumption_report.md` | W3 human-readable stage consumption report |
| `artifacts/apps_rg/ag8_w3_1_count_reconciliation.json` | W3.1 count reconciliation detail |
| `artifacts/apps_rg/ag8_w4_no_bypass_map.json` | W4 enforcement map (14 invariants, no bypasses) |
| `artifacts/apps_rg/ag8_w4_contract_mapping.json` | Contract field → prompt slot mapping |
| `artifacts/apps_rg/ag8_w4_authority_report.md` | W4 authority report with resolution details |
| `artifacts/apps_rg/ag8_w4_acceptance_evidence.json` | W4 acceptance evidence for all 21 criteria |
| `artifacts/apps_rg/ag8_prompt_no_bypass_map.json` | Canonical alias for `ag8_w4_no_bypass_map.json` |
| `artifacts/apps_rg/ag8_prompt_contract_mapping.json` | Canonical alias for `ag8_w4_contract_mapping.json` |
| `artifacts/apps_rg/ag8_prompt_authority_report.md` | Canonical alias for `ag8_w4_authority_report.md` |
| `artifacts/apps_rg/ag8_prompt_acceptance_evidence.json` | Canonical alias for `ag8_w4_acceptance_evidence.json` |

---

## Files Modified (W4)

| File | Change |
|------|--------|
| `agentic_core/prompt_governance/apps_rg_pa_binding.py` | PAB-003 fix, `slot_lineage_map` expansion, `compilation_hash` fix |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | Cross-ref comment for `allowed_models` vs PA target model |
| `artifacts/apps_rg/ag8_prompt_authority_classification.json` | 11 UNKNOWN resolved, PROF-003 annotated |
| `artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json` | 11 UNKNOWN rows resolved |

## Files Created (W4)

| File | Purpose |
|------|---------|
| `tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py` | 21 acceptance tests |
| `ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py` | CI gate (advisory; bypass `PA_COV_BYPASS=1`) |
| `artifacts/apps_rg/ag8_w4_*` + canonical alias artifacts | Acceptance evidence bundle |

---

## Key Risks Resolved

| Risk ID | Description | Resolution |
|---------|-------------|------------|
| PAB-003 | U0/C0 conflation in `_build_user_instruction` | Split into `_build_u0_task_block` + `_build_c0_evidence_block` |
| PAB-004 | `compilation_hash` not content-sensitive | Switched to `sha256(content.encode())` per block |
| PROF-003 | Duplicate `forbidden_phrases` (duplicate of PROF-001) | Annotated as `DUPLICATE`, `runtime_reachable: false` |
| UNKNOWN ×11 | 11 UNKNOWN_NEEDS_REVIEW rows in matrix | All resolved with `w4_resolution` + stage consumption values |

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | All 86 surfaces classified with `authority_class` + `runtime_reachable` + `canonical_prompt_slot` | ✅ |
| DoD-2 | `python -m pytest tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py -q` → 21 passed | ✅ |
| DoD-3 | `python ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py` → exit 0, 0 errors | ✅ |
| DoD-4 | PAB-003 fixed: `slot_lineage_map` has separate U0 + C0 entries | ✅ |
| DoD-5 | All canonical alias artifacts exist on disk | ✅ |

### Verification-vs-Deferral

| Item | Verified | Deferred |
|------|----------|---------|
| 21 unit tests | ✅ Session verified | — |
| CI gate 0 errors | ✅ Session verified | — |
| 3-way count 86 | ✅ Session verified | — |
| Real LLM E2E re-run with new `compilation_hash` | — | Future plan (hash determinism test is sufficient for W4) |
| `discovered_not_yet_classified` full classification (13 surfaces) | — | Future wave |
