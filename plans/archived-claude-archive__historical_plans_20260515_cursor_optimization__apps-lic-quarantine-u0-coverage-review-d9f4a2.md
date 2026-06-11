---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-quarantine-u0-coverage-review-d9f4a2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-quarantine-u0-coverage-review-d9f4a2.md'
source_sha256: 46fb23c7dd5b138cd65ec09b97d7d17a3c88bbd5b125b62e4cd03c21d313c6f0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-lic-quarantine-u0-coverage-review-d9f4a2
plan_type: audit
dod_exempt: false
---

# apps_lic Quarantine-to-U0 Packet Coverage Review

Exhaustive evidence-first review determining whether all legitimate apps_lic quarantined capabilities are incorporated into the apps_lic U0 input packet and downstream agentic_core contract chain.

---

## Context (SCQA)

- **Situation** — apps_lic rides the canonical agentic_core spine (U0→L1→L0→C0→PA→L2→Exit→UWG→L4→L6). A comprehensive `AppsLicIngressContractV1` (880-line Pydantic contract at `apps_lic/contracts/apps_lic_ingress_contract_v1.py`) defines the U0 shape. The app has ~50+ engine/reasoning/validator/service files, archived L1 cognition planners (`archives/apps_lic_L1_cognition_20260504/`), archived dead code (`archives/adg_dead_code/2026-04-23/apps_lic/`), and `apps_lic/migrations/` + `apps_lic/scripts/` containing legacy purge/migration utilities. No dedicated `_quarantine/` folder exists — quarantined state is implicit (deprecated/legacy/disabled markers in-tree).
- **Complication** — Without a dedicated quarantine folder, it is unclear whether all valid capabilities scattered across in-tree "quarantine-equivalent" locations (deprecated engines, disabled validators, migration scripts, legacy types, archived planners) have been represented in the U0 ingress contract or downstream contracts. Stranded capabilities could mean functional gaps or unsafe bypasses.
- **Question** — Are all valid apps_lic quarantined capabilities now represented in the U0 input packet and downstream agentic_core contract chain, or are there missing functions stranded in quarantine?
- **Answer** — This plan executed an 8-wave evidence-gathering audit (no code changes) producing structured JSON artifacts, a gap register, and a retirement-or-remediation decision packet. W0–W7 complete. Final audit execution status: PASS. Final coverage verdict: FAIL (7 HIGH gaps are auto-generated scaffold stubs with zero real logic — all recommended RETIRE_WITH_RECEIPT). 2 items require owner decision.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_lic/contracts/apps_lic_ingress_contract_v1.py` | Canonical U0 shape definition | ✅ read W3 |
| `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml` | Field-to-consumer mapping proof | ✅ read W3 |
| `apps_lic/__main__.py` | Entry path / spine handoff | ✅ read W0 |
| `apps_lic/spine_manifest.yaml` | Route declarations | ✅ read W0 |
| `apps_lic/engines/**` | All engine capabilities | ✅ scanned W1 |
| `apps_lic/reasoning/**` | Reasoning/orchestration agents | ✅ scanned W1 |
| `apps_lic/validators/**` | Validation capabilities | ✅ scanned W1 |
| `apps_lic/types/**` | Type definitions (deprecated markers) | ✅ scanned W1; 5 orphaned types found W4 |
| `apps_lic/migrations/**` | Migration/legacy scripts | ✅ scanned W1 |
| `apps_lic/scripts/**` | Utility scripts including purge_legacy_archive | ✅ scanned W1 |
| `apps_lic/services/**` | Service layer | ✅ scanned W1 |
| `apps_lic/policy/**` | Policy configs | ✅ scanned W1 |
| `apps_lic/prompt_assembly/**` | Prompt compilation | ✅ scanned W1 |
| `apps_lic/integrations/**` | Spine handoff / workflow dispatch | ✅ scanned W1 |
| `archives/apps_lic_L1_cognition_20260504/` | Archived L1 planners | ✅ confirmed relocated W3 |
| `archives/adg_dead_code/2026-04-23/apps_lic/` | ADG-identified dead code | ✅ 7 false-positive gaps found W3–W4 |
| `tests/_apps_contract/` tests for apps_lic | Test coverage proof | ✅ reference-only W3 |
| `agentic_core/L0_routing/apps_lic_l0_binding.py` | L0 binding existence | ✅ verified W3 |
| `agentic_core/L1_cognition/apps_lic_l1_binding.py` | L1 binding existence | ✅ verified W3 |
| `apps_lic/config/domain_contract/**` | Eval harness contracts | ✅ scanned W1 |

---

## Wave Structure

| Wave | Metric | Scope | Status | Key Outcome |
|------|--------|-------|--------|-------------|
| W0 | Environment baseline | Verify file tree, test harness, ADG health | ✅ PASS | 155 py files in apps_lic, 39 archived, test harness available |
| W1 | Quarantine inventory | Enumerate ALL quarantine-equivalent files | ✅ PASS | 109 items inventoried (103 reviewable + 6 generated/cache) |
| W2 | Capability classification | Classify each into A-L buckets + risk | ✅ PASS | 103 classified: 48 H_EXIT, 33 G_L2, 11 NON_RUNTIME, 6 C_L0, 5 B_L1 |
| W3 | U0 + downstream mapping | Cross-check against contracts + surfaces | ✅ PASS | 92 COVERED, 5 MISSING, 1 TEST_ONLY, 4 DOC_ONLY; 7 P0 false positives found |
| W4 | Gap identification + blocking | Severity-ranked gap register | ✅ PASS | 13 true gaps (7 HIGH, 6 LOW), 2 NEEDS_REVIEW, 23 not-gap |
| W5 | Test + proof review | Run tests, evaluate gap-relevant coverage | ✅ PASS | 722 apps_contract pass; 7 HIGH gaps have zero executable test proof |
| W6 | Deliverable emission | Final JSON receipt + markdown summary | ✅ PASS | audit_execution=PASS, coverage_verdict=FAIL, remediation=NOT_STARTED |
| W7 | Retirement-or-remediation decision | Evidence-first disposition for 9 unresolved items | ✅ PASS | 7 RETIRE_WITH_RECEIPT (all stubs), 2 OWNER_DECISION_REQUIRED |
| W8 | Retirement receipts + guard tests | Emit 7 retirement receipts; add quarantine guard tests | ✅ PASS | 7 receipts emitted, 5/5 guard tests green, golden_baseline.json excluded (config snapshot) |
| W9 | Owner decisions | Owner reviews w5_migration.py + network_ops.py; decides archive vs keep | ✅ PASS | W4-GAP-010: KEEP_AS_NON_RUNTIME_MIGRATION_UTILITY; W4-GAP-035: RETIRE_WITH_RECEIPT |
| W10 | Final coverage closure | Emit final coverage receipt with updated PASS verdict | ✅ PASS | coverage_verdict=PASS, 8 retired + 1 non-runtime, 0 unresolved, plan complete |

**Actual tokens W0–W10: ~135K. All waves complete.**

---

## Out Of Scope

- Unquarantining any files
- Restoring quarantined code to production paths
- Patching or fixing any discovered gaps (review only)
- Modifying `AppsLicIngressContractV1` or any downstream contracts
- Creating new tests (documenting missing tests only)
- Changes to `agentic_core/` bindings
- Other apps (`apps_rg`, `apps_qna`, etc.) — apps_lic only

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 0.1 | Pre-flight: tree + health | `apps_lic/**`, test harness | — | ~5K | ✅ DONE |
| 1.1 | In-tree quarantine scan | `apps_lic/engines/`, `reasoning/`, `types/` | deprecated/legacy markers | ~10K | ✅ DONE |
| 1.2 | Archives + migrations scan | `archives/apps_lic_*`, `migrations/`, `scripts/` | files outside main tree | ~8K | ✅ DONE |
| 1.3 | Config + validator + service scan | `validators/`, `services/`, `policy/` | disabled/legacy config | ~7K | ✅ DONE |
| 2.1 | Capability classification (A-F) | All inventoried files → U0/L1/L0/C0/PA/L3 | — | ~10K | ✅ DONE |
| 2.2 | Capability classification (G-L) | All inventoried files → L2/Exit/UWG/L4/L6/Gates/L5 | — | ~10K | ✅ DONE |
| 3.1 | U0 contract field mapping | `apps_lic_ingress_contract_v1.py` vs capabilities | field coverage gaps | ~12K | ✅ DONE |
| 3.2 | Downstream contract mapping | L1/L0/C0/PA/L2/Exit/UWG bindings vs capabilities | contract chain gaps | ~13K | ✅ DONE |
| 3.3 | P0 manual review | 28 P0_MUST_MAP items manual verification | false-positive coverage | ~5K | ✅ DONE |
| 4.1 | Gap identification + blocking | Gap register with severity + blocking level | 7 HIGH false-positive gaps | ~10K | ✅ DONE |
| 4.2 | Orphaned-type verification | 5 type files zero-import check via grep | orphaned stale types | ~2K | ✅ DONE |
| 5.1 | Test execution + coverage | `pytest -k apps_lic` + contract tests | missing test categories | ~8K | ✅ DONE |
| 5.2 | Gap-relevant test review | Tests for 13 true-gap capabilities | gap evidence quality | ~4K | ✅ DONE |
| 6.1 | Final JSON receipt emission | Consolidated receipt at `artifacts/apps_lic/` | — | ~3K | ✅ DONE |
| 6.2 | Final markdown summary | Markdown summary at `artifacts/apps_lic/` | — | ~2K | ✅ DONE |
| 7.1 | Archived source inspection | Read all 7 HIGH gap source files + 2 NEEDS_REVIEW | evidence-first | ~8K | ✅ DONE |
| 7.2 | Active substitute search | grep for active replacements in apps_lic + agentic_core | match specificity | ~3K | ✅ DONE |
| 7.3 | Decision packet emission | JSON decision packet with 9 item dispositions | — | ~5K | ✅ DONE |

---

## Gap Register (W4 Final — 2026-05-11)

### 7 HIGH — ACTIVE_RUNTIME_GAP — BLOCKS_FINAL_PASS

Archived ADG-dead tools with **no active replacement** for their specific capability. W3 automated matching was a false positive (generic terms only: Initialize, Process, configuration, tools).

| Gap ID | Inventory ID | Capability | Expected Home |
|--------|-------------|-----------|---------------|
| W4-GAP-021 | W1-QINV-0069 | Aggregate Campaign State | apps_lic active runtime engine |
| W4-GAP-023 | W1-QINV-0075 | Compute Personalization Match | apps_lic active runtime engine |
| W4-GAP-024 | W1-QINV-0076 | Diagnose Personalization Issues | apps_lic active runtime engine |
| W4-GAP-025 | W1-QINV-0084 | Log Campaign Metrics | apps_lic active runtime engine |
| W4-GAP-029 | W1-QINV-0090 | Search Similar Messages | apps_lic active runtime engine |
| W4-GAP-030 | W1-QINV-0091 | Snapshot Campaign State | apps_lic active runtime engine |
| W4-GAP-031 | W1-QINV-0092 | Update Recipient Profiles | apps_lic active runtime engine |

**Recommendation**: In a later remediation wave, either prove intentional retirement with an explicit retirement receipt, or map the capability into the active runtime / U0 / downstream contract chain.

### 6 LOW — DOCUMENTATION_ONLY_GAP / TEST_COVERAGE_GAP — DOES_NOT_BLOCK_W5

| Gap ID | Inventory ID | Capability | Type | Reason |
|--------|-------------|-----------|------|--------|
| W4-GAP-016 | W1-QINV-0053 | app content validator agent types | DOCUMENTATION_ONLY | Orphaned: 0 imports repo-wide (664 lines) |
| W4-GAP-017 | W1-QINV-0055 | lic vector memory types | DOCUMENTATION_ONLY | Orphaned: 0 imports repo-wide (563 lines) |
| W4-GAP-018 | W1-QINV-0058 | recipient archetype types | DOCUMENTATION_ONLY | Orphaned: 0 imports repo-wide (597 lines) |
| W4-GAP-019 | W1-QINV-0061 | state checkpoint types | DOCUMENTATION_ONLY | Orphaned: 0 imports repo-wide (444 lines) |
| W4-GAP-020 | W1-QINV-0062 | validation severity types | DOCUMENTATION_ONLY | Orphaned: 0 imports repo-wide (610 lines) |
| W4-GAP-008 | W1-QINV-0027 | migrations/__init__.py | TEST_COVERAGE | Test-only references; not contract-chain coverage |

### 2 NEEDS_REVIEW — NEEDS_OWNER_DECISION

| Gap ID | Inventory ID | Source | Reason |
|--------|-------------|--------|--------|
| W4-GAP-010 | W1-QINV-0033 | `apps_lic/migrations/w5_migration.py` | BLOCKER_REVIEW, 76 markers, write-like calls — unclear if stranded |
| W4-GAP-035 | W1-QINV-0102 | `archives/.../network_ops.py` | Unclear scope — infrastructure utility or stranded runtime? |

### 23 NOT_A_GAP (confirmed)

17 P0_CONFIRMED_COVERED (specific active replacements verified), 2 NON_RUNTIME, 4 INFO documentation-only scripts.

---

## W4 Key Findings

1. **7 archived tools are true ACTIVE_RUNTIME_GAPs** — W3 automated matching relied on generic terms; manual P0 review overrode to MISSING.
2. **5 type files are orphaned** — `grep_search` confirmed zero imports from any file across the entire repo.
3. **Both archived L1 planners confirmed relocated** — `message_planner.py` → `apps_lic/reasoning/message_planner.py` (score=67), `profile_planner.py` → `apps_lic/reasoning/profile_planner.py` (score=49).
4. **25% P0 false-positive rate** — automated term-matching over-counted coverage on archived tools.
5. **No BLOCKER-severity gaps** — 7 HIGH items block final pass but not W5.

---

## Artifacts Emitted

| Wave | Artifact | Path |
|------|----------|------|
| W1 | Quarantine inventory | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w1_inventory.json` |
| W1 | W1 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w1_receipt.json` |
| W2 | Capability classification | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w2_classification.json` |
| W2 | W2 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w2_receipt.json` |
| W3 | Search surfaces | `artifacts/apps_lic/apps_lic_w3_search_surfaces.json` |
| W3 | Mapping matrix | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w3_mapping_matrix.json` |
| W3 | P0 manual review | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w3_p0_manual_review.json` |
| W3 | W3 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w3_receipt.json` |
| W4 | Gap register | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w4_gap_register.json` |
| W4 | W4 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w4_receipt.json` |
| W5 | Test reference scan | `artifacts/apps_lic/apps_lic_w5_test_reference_scan.json` |
| W5 | Test proof matrix | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w5_test_proof_matrix.json` |
| W5 | Gap test manual review | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w5_gap_test_manual_review.json` |
| W5 | W5 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w5_receipt.json` |
| W6 | Final JSON receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review.json` |
| W6 | Final markdown summary | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review.md` |
| W6 | W6 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w6_receipt.json` |
| W7 | Decision packet | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w7_decision_packet.json` |
| W7 | W7 receipt | `artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w7_receipt.json` |

---

## Execution Plan

### Wave 0 — Pre-flight Baseline ✅ DONE

**Result**: 155 py files in apps_lic, 39 archived apps_lic files, test harness confirmed, ADG health green.

### Wave 1 — Quarantine Inventory ✅ DONE

**Result**: 109 items inventoried (103 reviewable + 6 generated/cache excluded). 4 location types: IN_TREE_ACTIVE (42), IN_TREE_QUARANTINE_EQUIVALENT (25), ARCHIVED_ADG_DEAD_CODE (37), ARCHIVED_L1_COGNITION (2), plus generated/cache. Builder script: `artifacts/apps_lic/build_w1_quarantine_inventory.py`.

### Wave 2 — Capability Classification ✅ DONE

**Result**: 103 items classified into A-L spine buckets. Distribution: H_EXIT_EVAL_CONTROL (48), G_L2_EXECUTE (33), NON_RUNTIME_UTILITY (11), C_L0_ROUTE (6), B_L1_INTERPRET_PLAN (5), J_L4_DURABLE_STATE (4), L_L5_00C_GOVERNANCE_GATES (1), E_PROMPT_ASSEMBLY (1). 28 items flagged P0_MUST_MAP. Builder: `artifacts/apps_lic/build_w2_capability_classification.py`.

### Wave 3 — U0 + Downstream Cross-Check ✅ DONE

**Result**: 10,004 searchable surfaces collected. 103 items mapped: 92 COVERED (17 U0, 9 field map, 44 downstream, 22 active runtime), 5 MISSING_CANDIDATE, 1 TEST_ONLY, 4 DOCUMENTED_ONLY, 1 NOT_RUNTIME. P0 manual review found 7 false positives (archived tools matched only on generic terms). Both archived L1 planners confirmed relocated to `apps_lic/reasoning/`. Builders: `build_w3_search_surfaces.py`, `build_w3_mapping_matrix.py`.

### Wave 4 — Gap Identification ✅ DONE

**Result**: 38 candidates assessed → 13 true gaps (7 HIGH archived-tool runtime gaps, 5 LOW orphaned types, 1 LOW test-only migration init), 23 not-gap, 2 NEEDS_REVIEW. 7 BLOCKS_FINAL_PASS. No BLOCKER-severity items. W5 is not blocked. Builder: `build_w4_gap_register.py`.

### Wave 5 — Test + Proof Review ✅ DONE

**Result**: 722 apps_contract tests pass; 19 fail (pre-existing fixture deps); 31 errors (pre-existing + 3 EXPECTED_GUARD_BEHAVIOR quarantine RuntimeErrors). All 14 coverage categories have TEST_REFERENCE_ONLY status. 3 governance quarantine guards pass. **7 HIGH gaps have ZERO executable test assertions** — references exist only in `tests/architecture/mirror_discovery_snapshot.json` (data file, not test). 2 NEEDS_REVIEW items have passing tests but only prove utility mechanics, not contract-chain coverage. Builder scripts: `build_w5_test_reference_scan.py`, `build_w5_test_proof_matrix.py`.

### Wave 6 — Deliverable Emission ✅ DONE

**Result**: Final JSON receipt and markdown summary emitted. 15 prior artifacts validated (0 missing, 0 invalid). **Audit execution status: PASS. Coverage verdict: FAIL. Remediation status: NOT_STARTED.** Final answer: 7 HIGH archived ADG-dead tool capabilities remain unresolved with zero executable test proof. 2 items need owner decision. Builder: `build_w6_final_deliverables.py`.

### Wave 7 — Retirement-or-Remediation Decision Packet ✅ DONE

**Result**: All 9 unresolved items assessed with evidence-first analysis. All 7 HIGH gap source files read via filesystem MCP — **all are auto-generated scaffold stubs with zero real implementation** (generic `process()` returning `{"status":"processed"}`, undefined imports, uppercase variable bugs). Active substitute search confirmed governed alternatives exist: HOP1ProfileAnalysisAgent + profile_planner (personalization), L4 contracts (state), OTEL + L6 (metrics), PersonaPlannerValidator (validation). **Decisions: 7 RETIRE_WITH_RECEIPT, 2 OWNER_DECISION_REQUIRED** (w5_migration.py is a real 469-line migration utility; network_ops.py is a consolidated MCP mock file). W8 can proceed for retirement receipts. Builder: `build_w7_decision_packet.py`.

---

## Rules

- No code changes — this is a read-only audit
- Evidence-first: every claim backed by file path + symbol + line reference
- No unquarantining: quarantined files stay quarantined
- No fake receipts: if evidence is missing, mark MISSING
- Distinction: "in docs" ≠ "in runtime" ≠ "proven by tests"
- Tests are reference evidence, NOT contract-chain coverage
- Active replacement must match specific capability, not generic terms
- Constitutional spine laws are the arbiter of correctness

---

## Success Criteria

- [x] All quarantine-equivalent locations identified (in-tree + archives) — W1
- [x] Every quarantined file inventoried with path, type, purpose — W1 (109 items)
- [x] Capability classification complete (A-L buckets) — W2 (103 classified)
- [x] U0 packet coverage proven or gaps documented — W3 (17 U0, 9 field map)
- [x] Downstream contract coverage proven or gaps documented — W3–W4 (13 true gaps identified)
- [x] Test coverage evaluated for gap-relevant capabilities — W5 (7 HIGH: zero proof; 6 LOW: reference-only)
- [x] Final consolidated JSON receipt emitted — W6 (audit_execution=PASS, coverage=FAIL)
- [x] Final verdict rendered with proof — W6 (FAIL: 7 HIGH gaps, 2 owner decisions)
- [x] Retirement-or-remediation decisions for all 9 unresolved items — W7 (7 RETIRE, 2 OWNER)

---

## Rollback Strategy

Not applicable — this is a read-only audit plan. No code changes are made. Artifacts can be deleted if review is invalidated.

---

## Acceptance Criteria

| Metric | Target | Verification | Status |
|---|---|---|---|
| Quarantine files reviewed | 100% of identified files | W1 inventory: 109 items | ✅ |
| Coverage status assigned | Every file has a coverage_status enum | W3 mapping matrix: 103 mapped | ✅ |
| Gaps documented | All MISSING items in gap register | W4 gap register: 13 true gaps | ✅ |
| Tests executed | apps_lic test suite runs | W5 receipt: 722 pass, 19 fail, 31 errors | ✅ |
| Deliverables present | Final receipt + gap register + decision packet | `artifacts/apps_lic/` (21 artifacts) | ✅ |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Quarantine inventory populated for all 109 items | `python -c "import json; d=json.load(open('artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review_w1_inventory.json')); print(len(d['inventory']))"` → 109 | ✅ |
| DoD-2 | Coverage cross-check maps each capability to contract or MISSING | W3 mapping matrix has `coverage_status` for all 103 reviewable items | ✅ |
| DoD-3 | Gap register with severity for all candidates | W4 gap register: 38 candidates, all have severity + blocking level | ✅ |
| DoD-4 | Tests run for gap-relevant capabilities | W5 receipt: 722 pass; 7 HIGH gaps confirmed zero test proof | ✅ |
| DoD-5 | Final consolidated receipt exists and is valid JSON | `python -c "import json; json.load(open('artifacts/apps_lic/apps_lic_quarantine_u0_packet_coverage_review.json'))"` exits 0 | ✅ |
| DoD-6 | Final verdict rendered with evidence | audit_execution=PASS, coverage=FAIL, backed by 7 HIGH gaps + 2 owner decisions | ✅ |
| DoD-7 | Retirement-or-remediation decision for each unresolved item | W7 decision packet: 9 items, all with decision + rationale + risk | ✅ |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| W8 retirement receipts for 7 RETIRE_WITH_RECEIPT items | W7 decided disposition; W8 emits receipts + guard tests | W7 decision packet recommended_next_plan |
| Owner decision on w5_migration.py (W4-GAP-010) | Real migration utility — owner decides archive vs keep | W7 decision packet OWNER_DECISION_REQUIRED |
| Owner decision on network_ops.py (W4-GAP-035) | Consolidated MCP mock — owner confirms zero imports → retire | W7 decision packet OWNER_DECISION_REQUIRED |
| Retirement receipts for 5 orphaned types (LOW) | Review-only; explicit retirement is remediation | W4 gap register LOW items |
| Quarantine guard tests for archived tools | W7 recommends; W8 implements | W7 decision packet expected_tests |
| Final coverage receipt with PASS verdict | Blocked on W8 completion + owner decisions | W7 final_verdict |
| Runtime OTel trace verification | Static audit only | Separate spine-cert plan |

---

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
