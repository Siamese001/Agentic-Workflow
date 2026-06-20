---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-lic-ag9-prompt-authority-coverage-e5f2a8.md'
original_relative_path: '_archive\\2026-05\\apps-lic-ag9-prompt-authority-coverage-e5f2a8.md'
source_sha256: e31fcd698a0825148aeeb3e4efc95e4be72bf212c534916b5fdf4eec2e154133
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-lic-ag9-prompt-authority-coverage-e5f2a8
plan_type: hardening
dod_exempt: false
---

# AG-9 apps_lic Prompt Authority Coverage

Prompt authority hardening plan for `apps_lic` — inventories all prompt surfaces, classifies authority and stage consumption, resolves UNKNOWN_NEEDS_REVIEW rows, and enforces all invariants via a 21-test suite and a CI gate. Brings apps_lic to parity with apps_rg AG-8 prompt authority pattern while preserving apps_lic's outreach messaging domain specifics.

---

## Context (SCQA)

- **Situation** — `apps_lic` has a live prompt assembly pipeline (PA binding at `agentic_core/prompt_governance/apps_lic_pa_binding.py`) assembling prompts from `apps_lic/prompt_assembly/` templates. The pipeline has 8 canonical BOM slots (S0, I0, C0, U0, D0, E0, Y0, R0) across 8 templates, 13 eval rubric dimensions, 17 exit rubric dimensions, and 3 prompts.json templates. However, it lacks a formal audit of which prompt surfaces are runtime-reachable, which stages consume them, and whether authority boundaries are respected.

- **Complication** — Without a structured prompt authority inventory and stage consumption matrix, risks accumulate silently: U0/C0/evidence conflation, unresolved UNKNOWN_NEEDS_REVIEW surfaces, non-content-sensitive `compilation_hash`, and no CI enforcement of any of these invariants. The apps_lic domain (outreach messaging) has different requirements than apps_rg (resume generation), requiring domain-specific authority classes like `RECIPIENT_PROFILE_DATA_ONLY` and `BRIEFING_CONTEXT_DATA_ONLY`.

- **Question** — How do we harden `apps_lic` prompt authority so that all 103 surfaces are classified, all risks are resolved, and all invariants are continuously enforced?

- **Answer** — A 4-wave plan: W0 baseline verification, W1 prompt inventory, W2 authority classification, W3 stage consumption matrix, W4 prompt authority hardening. Each wave emits artifacts and verifies counts reconcile.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W0 | W0.P1–W0.P3 | Baseline verification — confirm spine wiring intact, identify prompt files, emit baseline report | ~8K | 🔲 TODO |
| W1 | W1.P1–W1.P3 | Prompt inventory — discover all 103 prompt surfaces, emit `ag9_prompt_authority_inventory.json` | ~15K | 🔲 TODO |
| W2 | W2.P1–W2.P3 | Authority classification — classify all 103 surfaces with `authority_class`, `runtime_reachable`, `canonical_prompt_slot` | ~20K | 🔲 TODO |
| W3 | W3.P1–W3.P3 | Stage consumption matrix — map all 103 surfaces to stage consumption statuses | ~18K | 🔲 TODO |
| W4 | W4.P1–W4.P5 | Prompt authority hardening — verify PA slot_lineage_map, resolve UNKNOWN rows, write 21 tests + CI gate | ~25K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Spine wiring verification | `tests/_apps_contract/test_ag8_apps_lic_golden_path.py` | Must pass before any changes | ~2K | 🔲 TODO |
| W0.P2 | Prompt file discovery | `apps_lic/prompt_assembly/`, `apps_lic/config/` | Identifying all touchpoints | ~3K | 🔲 TODO |
| W0.P3 | Baseline report | `artifacts/apps_lic/ag9_baseline_report.json` | Establishing foundation | ~3K | 🔲 TODO |
| W1.P1 | BOM slot discovery | `prompt_bom.yaml` | 8 canonical slots | ~3K | 🔲 TODO |
| W1.P2 | Template slot body discovery | 8 templates in `prompt_assembly/templates/` | 65 slot bodies across templates | ~6K | 🔲 TODO |
| W1.P3 | Rubric and prompts discovery | `eval_rubrics.yaml`, `exit_rubric.yaml`, `prompts.json` | 30 dimensions + 3 templates | ~6K | 🔲 TODO |
| W2.P1 | Authority class assignment | `ag9_prompt_authority_classification.json` | Domain-specific authority classes | ~7K | 🔲 TODO |
| W2.P2 | Runtime reachability scoring | `runtime_reachable` field for all 103 surfaces | Distinguish dead vs live code | ~6K | 🔲 TODO |
| W2.P3 | Canonical slot mapping | `canonical_prompt_slot` for all 103 surfaces | Map to BOM slots | ~7K | 🔲 TODO |
| W3.P1 | Stage consumption matrix | `ag9_prompt_stage_consumption_matrix.json` (103 rows) | U0/L1/L0/C0/PA/L2/Exit/L6 mapping | ~6K | 🔲 TODO |
| W3.P2 | Stage consumption report | `ag9_w3_stage_consumption_report.md` | Human-readable analysis | ~6K | 🔲 TODO |
| W3.P3 | UNKNOWN_NEEDS_REVIEW identification | Identify rows for W4 resolution | Gap analysis | ~6K | 🔲 TODO |
| W4.P1 | PA slot_lineage_map verification | `apps_lic_pa_binding.py` | Verify U0/C0/evidence separation | ~6K | 🔲 TODO |
| W4.P2 | UNKNOWN rows resolved | Update classification + matrix | Close all gaps | ~5K | 🔲 TODO |
| W4.P3 | compilation_hash verification | Content-hash (sha256) verification | Ensure content-sensitive | ~4K | 🔲 TODO |
| W4.P4 | 21-test suite | `tests/_apps_contract/test_apps_lic_prompt_authority_coverage.py` | All invariants tested | ~5K | 🔲 TODO |
| W4.P5 | CI gate | `ops_scripts/ci/check_apps_lic_prompt_authority_coverage.py` | Continuous enforcement | ~5K | 🔲 TODO |

---

## W4 Acceptance Criteria — Final State

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 3-way count consistent at 103 (inventory / classification / matrix) | 🔲 | All three JSON files: `total_items=103` |
| `discovered_not_yet_classified` bucket preserved + nonzero | 🔲 | `inventory_metadata.discovered_not_yet_classified_count` |
| No matrix prompt_id missing classification | 🔲 | test_3 green |
| Runtime prompts have `authority_class`, `contract_field_target`, `prompt_slot_target` | 🔲 | test_4 + test_5 green |
| U0 does not consume generation instruction slots | 🔲 | test_6 green (slot-based predicate) |
| L1 consumes only planning/domain projections (not raw generation slots) | 🔲 | test_7 green (slot-based predicate) |
| L0 consumes only structured L1PlanContract fields | 🔲 | test_8 + test_9 green |
| C0 does not assemble prompts | 🔲 | test_10 green |
| PA is the only generation prompt assembly authority | 🔲 | test_11 green |
| PA `slot_lineage_map` separates U0 task from C0 evidence from briefing data | 🔲 | test_12 green |
| PA `component_hash_map` includes all runtime-used components | 🔲 | test_13 green |
| `compilation_hash` changes with content (sha256, not len) | 🔲 | test_14 green |
| Briefing context remains C0-only (no instruction slot injection) | 🔲 | test_15 green |
| Eval rubrics map to Exit/X1, not generation stages | 🔲 | test_16 green |
| L2 does not load raw apps_lic prompts | 🔲 | test_17 green |
| Exit does not assemble generation prompts | 🔲 | test_18 green |
| No UNKNOWN_NEEDS_REVIEW without resolution | 🔲 | test_19 green — all resolved |
| No ChromaDB mutation | 🔲 | test_20 green |
| No external embedding generation | 🔲 | test_21 green |
| CI gate: 0 errors, 0 warnings | 🔲 | `PA-LIC-COV: PASS — 0 errors, 0 warnings` |

---

## apps_lic Domain-Specific Authority Classes

The following authority classes are specific to apps_lic's outreach messaging domain:

| Authority Class | Description | apps_lic Example |
|-----------------|-------------|------------------|
| `SYSTEM_OR_POLICY_INSTRUCTION` | Spine-level governance directives | S0 slot in all templates |
| `DOMAIN_TASK_INSTRUCTION` | Outreach-specific drafting rules | I0 slot with channel constraints |
| `USER_TASK_DATA` | User outreach request text | U0 slot content |
| `C0_EVIDENCE_DATA_ONLY` | Verified briefing context | C0 slot with recipient data |
| `BRIEFING_CONTEXT_DATA_ONLY` | PreloadedOutreachContextManifest data | Briefing research content |
| `RECIPIENT_PROFILE_DATA_ONLY` | Recipient profile/seniority data | Verified recipient attributes |
| `APPROVED_EXAMPLE_DATA` | Style reference examples | E0 slot content |
| `WRITING_PREFERENCE_DATA` | Sender voice/style preferences | Y0 slot with signature rules |
| `OUTPUT_SCHEMA_CONTRACT` | JSON schema and validation rules | R0 slot output contract |
| `NARRATIVE_ARC_GUIDANCE` | P2 optional arc structure | N0 slot (optional) |
| `ARCHETYPE_TONE_CALIBRATION` | P2 optional tone calibration | A0 slot (optional) |
| `COMPETITIVE_CONTEXT_DATA` | P2 optional differentiator data | L0 slot (optional) |
| `EVAL_RUBRIC_CRITERIA` | Exit evaluation dimensions | eval_rubrics.yaml dimensions |
| `EXIT_GUARD_RAILS` | Hard-fail boundary rules | exit_rubric.yaml notes |
| `JUDGE_PROMPT_TEMPLATE` | LLM-as-judge prompts | prompts.json templates |
| `LEGACY_COMPILER_SURFACE` | lic_pa_compiler.py surfaces | Dead code paths |
| `UNKNOWN_NEEDS_REVIEW` | Unclassified surfaces | To be resolved in W4 |

---

## Artifacts to Emit

| Artifact | Description |
|----------|-------------|
| `artifacts/apps_lic/ag9_baseline_report.json` | W0 baseline verification report |
| `artifacts/apps_lic/ag9_prompt_authority_inventory.json` | 103-surface prompt inventory |
| `artifacts/apps_lic/ag9_prompt_authority_classification.json` | Full authority classification |
| `artifacts/apps_lic/ag9_prompt_stage_consumption_matrix.json` | Stage consumption matrix |
| `artifacts/apps_lic/ag9_w3_stage_consumption_report.md` | W3 human-readable report |
| `artifacts/apps_lic/ag9_prompt_no_bypass_map.json` | W4 enforcement map (20 invariants) |
| `artifacts/apps_lic/ag9_prompt_contract_mapping.json` | Contract field → prompt slot mapping |
| `artifacts/apps_lic/ag9_prompt_authority_report.md` | W4 authority report |
| `artifacts/apps_lic/ag9_prompt_acceptance_evidence.json` | W4 acceptance evidence for all 21 criteria |

---

## Files to Create

| File | Purpose |
|------|---------|
| `.cursor/plans/apps-lic-ag9-prompt-authority-coverage-e5f2a8.md` | This plan |
| `tests/_apps_contract/test_apps_lic_prompt_authority_coverage.py` | 21 acceptance tests |
| `ops_scripts/ci/check_apps_lic_prompt_authority_coverage.py` | CI gate (advisory; bypass `PA_LIC_COV_BYPASS=1`) |
| `artifacts/apps_lic/ag9_*` | All JSON and MD artifacts |

---

## Files to Read (Not Modify)

| File | Why Needed |
|------|------------|
| `agentic_core/prompt_governance/apps_lic_pa_binding.py` | PA binding verification |
| `apps_lic/prompt_assembly/lic_pa_compiler.py` | Legacy compiler surfaces |
| `apps_lic/prompt_assembly/prompt_bom.yaml` | BOM slot definitions |
| `apps_lic/config/prompt_registry.yaml` | Template registry |
| `apps_lic/config/domain_contract/prompt_profiles.yaml` | Profile boundary rules |
| `apps_lic/config/domain_contract/eval_rubrics.yaml` | Eval dimensions |
| `apps_lic/config/exit_rubric.yaml` | Exit guard rails |
| `apps_lic/config/prompts.json` | Judge prompt templates |
| `apps_lic/prompt_assembly/templates/*.yaml` (8 files) | Template slot bodies |

---

## Key Risks to Resolve

| Risk ID | Description | Resolution Target |
|---------|-------------|-------------------|
| LIC-PAB-001 | U0/C0/briefing conflation in legacy templates | W4.P1 verification |
| LIC-PAB-002 | `compilation_hash` not content-sensitive in legacy compiler | W4.P3 verification |
| LIC-PROF-001 | Legacy compiler surfaces still reachable | W2 classification |
| UNKNOWN | Unclassified surfaces from prompts.json and rubrics | W4.P2 resolution |

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | All 103 surfaces classified with `authority_class` + `runtime_reachable` + `canonical_prompt_slot` | 🔲 |
| DoD-2 | `python -m pytest tests/_apps_contract/test_apps_lic_prompt_authority_coverage.py -q` → 21 passed | 🔲 |
| DoD-3 | `python ops_scripts/ci/check_apps_lic_prompt_authority_coverage.py` → exit 0, 0 errors | 🔲 |
| DoD-4 | PA `slot_lineage_map` has separate U0 + C0 + briefing entries | 🔲 |
| DoD-5 | All canonical alias artifacts exist on disk | 🔲 |
| DoD-6 | apps_lic AG-8 spine-wiring tests still pass (109 tests) | 🔲 |

### Verification-vs-Deferral

| Item | Verified | Deferred |
|------|----------|----------|
| 21 unit tests | 🔲 Session verification planned | — |
| CI gate 0 errors | 🔲 Session verification planned | — |
| 3-way count 103 | 🔲 Session verification planned | — |
| Real LLM E2E with new `compilation_hash` | — | Future plan (hash determinism test sufficient) |
| `discovered_not_yet_classified` full classification | — | Future wave (surfaces may remain unclassified if non-runtime) |

---

## Rollback Strategy

1. W0 gates protect against regressions — do not proceed if AG-8 tests fail.
2. New AG-9 files are isolated — removal does not touch AG-8 spine wiring.
3. If any test breaks existing apps_lic functionality, revert the offending AG-9 artifact.
4. `git stash` is safe at any wave boundary (no migrations, no schema changes, no L4 writes).

---

## Acceptance Invariant

AG-9 is complete only when apps_lic has **complete prompt authority coverage** with:
- All 103 surfaces discovered and classified
- Authority boundaries enforced (system > domain > user > evidence > briefing)
- PA slot_lineage_map proves separation of concerns
- content-sensitive prompt hashing
- component_hash_map covers runtime-used components
- No UNKNOWN_NEEDS_REVIEW remains unresolved
- No ChromaDB mutation
- No external embedding generation
- All AG-8 spine-wiring tests still pass

---

## Parent Plan Reference

- **AG-8 spine wiring (apps_lic)**: `.cursor/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md` — COMPLETED
- **AG-8 prompt authority (apps_rg)**: `.cursor/plans/apps-rg-ag8-prompt-authority-coverage-d9f4c2.md` — PATTERN REFERENCE

This plan follows the apps_rg AG-8 pattern but adapts for apps_lic's outreach messaging domain with appropriate authority classes and surface types.
