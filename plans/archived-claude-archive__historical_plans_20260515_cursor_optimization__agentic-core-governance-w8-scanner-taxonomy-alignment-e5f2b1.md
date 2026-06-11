---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\agentic-core-governance-w8-scanner-taxonomy-alignment-e5f2b1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\agentic-core-governance-w8-scanner-taxonomy-alignment-e5f2b1.md'
source_sha256: c56da31eca650a7a304624210c27ea9fdc5e33c61fdb319860716cf1eefe9e4a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: agentic-core-governance-w8-scanner-taxonomy-alignment-e5f2b1
plan_type: governance    # governance | gates, schemas, CI, rule changes
# plan_type governs §22 ADG graph-layer-evidence gate:
#   governance → SKIPPED (gates, schemas, CI, rule changes)
# See: .windsurf/rules/adg-graph-layer-enforcement.md § "Plan Scope via Frontmatter"
#
# NOTION STATUS DISCIPLINE (§plan-location.md):
#   - Plans MUST be created with Status="Not Started" (never "In Progress")
#   - Use: from tools.notion.plan_creation_helper import create_plan_in_notion
#   - See: .windsurf/rules/plan-location.md § "Notion Status Discipline"
---

# W8: Align Governance Scanner Taxonomy with W7 Phase 0 Classification

Align `core_leakage_scan.py` strict mode with W7 Phase 0 semantic classification so strict mode reflects governance risk (runtime policy leakage) instead of raw literal matches.

---

## Context (SCQA)

**Situation:** W7 Phase 0 classified 297 violations into 5 semantic categories. Only RUNTIME_POLICY_LEAKAGE (2 files) required migration. The remaining ~295 violations are acceptable: STATIC_REGISTRY_METADATA (~140), OFFLINE_TOOLING_REFERENCE (~60), and FALSE_POSITIVE (~90).

**Complication:** The current strict scan treats all app literals equally, exiting 1 for any match. This creates noise and misrepresents actual governance risk. A scan showing 304 "violations" when only 2 are actual runtime leaks undermines trust in the governance system.

**Question:** How do we reconfigure the scanner to distinguish runtime policy leakage from approved non-runtime metadata and tooling references?

**Answer:** Update scan taxonomy to implement W7 Phase 0 classification: CRITICAL/HIGH only for runtime-coupled leakage; STATIC_REGISTRY and OFFLINE_TOOLING reported as INFO; FALSE_POSITIVE patterns excluded.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| W7 Phase 0 Classification Report | Taxonomy source of truth | ✅ Available at `artifacts/governance/w7_phase0_classification.md` |
| `tools/governance/core_leakage_scan.py` | Scanner implementation | 🔲 TODO - analyze current rule set |
| `agentic_core/adg/analysis/ModuleOwnership.py` | STATIC_REGISTRY example | ✅ Verified non-runtime in W7 |
| `agentic_core/adg/applications/placement_advisor.py` | RUNTIME_LEAKAGE (now fixed) | ✅ Fixed in W7 P1 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W8 | P1 | Scanner taxonomy update | ~400 | W7 classification finalized | ✅ DONE | Scanner distinguishes 5 categories |
| W8 | P2 | Strict mode redefinition | ~200 | P1 taxonomy implemented | ✅ DONE | strict exits 0 when runtime=0 |
| W8 | P3 | CI integration verification | ~200 | P2 strict mode working | ✅ DONE | CI remains green, reports meaningful counts |
| W8 | P4 | Documentation update | ~100 | P3 verified | ✅ DONE | AGENTS.md references new taxonomy |
| W8 | P5 | Classification reconciliation | ~600 | Taxonomy engine installed | ✅ DONE | UNKNOWN=0, RUNTIME=0 or moved to remediation |
| W8 | P6 | W9 Remediation Handoff | ~0 | P5 complete | ✅ DONE | W9 plan created for 55 RUNTIME findings |

**Overall Plan Status**: **PARTIAL / CLASSIFICATION COMPLETE / REMEDIATION BLOCKED BY W9**

**W8 Deliverables (PASS)**:
- ✅ Taxonomy engine installed and functioning
- ✅ UNKNOWN = 0 (all 154 reclassified with rationale)
- ✅ Classification rationale present for all findings
- ✅ Strict mode behavior correct (blocks on runtime/unknown)

**W8 Blockers (EXPECTED - HANDED OFF TO W9)**:
- ❌ Strict mode exit 0: BLOCKED - 55 true RUNTIME_POLICY_LEAKAGE remain
- ❌ Final remediation: BLOCKED BY W9 - requires runtime migration

**Final Counts**:
- RUNTIME_POLICY_LEAKAGE = 55 (W9 scope)
- STATIC_REGISTRY = 165 (non-blocking)
- OFFLINE_TOOLING = 24 (non-blocking)
- FALSE_POSITIVE = 11 (non-blocking)
- UNKNOWN = 0 ✅

**Strict Mode**: Exits 2 (correct behavior - will pass after W9)

**Total: ~900 tokens across 4 phases**

---

## Out Of Scope

- Fixing the remaining ~295 non-runtime violations (they are approved per W7 Phase 0)
- Migrating any additional files (only scanner configuration changes)
- Changes to ModuleOwnership, ADG adapters, or schema enums (proven non-runtime in W7)
- New test creation (existing tests should continue passing)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Taxonomy rule implementation | `core_leakage_scan.py` rule engine | PP-1: Current rules don't distinguish categories | ~200 | ✅ DONE |
| P1.2 | Category mapping definitions | Config/spec files | PP-2: Need canonical category definitions | ~200 | ✅ DONE |
| P2.1 | Strict mode severity logic | `core_leakage_scan.py` --strict flag | PP-3: Strict mode treats all violations equally | ~100 | ✅ DONE |
| P2.2 | Non-blocking category handling | Exit code logic | PP-4: Exit code logic needs category awareness | ~100 | ✅ DONE |
| P3.1 | CI gate verification | `run_contract_gates.py` integration | PP-5: Gate must accept new taxonomy | ~100 | ✅ DONE |
| P3.2 | Baseline scan run | Full repo scan | PP-6: Establish new baseline counts | ~100 | ✅ DONE |
| P4.1 | AGENTS.md update | Documentation | GAP-1: Need taxonomy reference | ~50 | ✅ DONE |
| P4.2 | Scan output format docs | README/help text | GAP-2: Users need category legend | ~50 | ✅ DONE |
| P5.1 | UNKNOWN findings reconciliation | Scan output analysis | PP-7: 154 UNKNOWN need classification | ~300 | ✅ DONE |
| P5.2 | RUNTIME_LEAKAGE reconciliation | Per-file runtime coupling verification | PP-8: 54 RUNTIME may be over-classified | ~200 | ✅ DONE |
| P5.3 | Classification rule refinement | `core_leakage_scan.py` | PP-9: Improve heuristics based on P5.1-P5.2 | ~100 | ✅ DONE |
| P6 | W9 Remediation Handoff | Create W9 plan for runtime leakage | BLOCKER: 55 RUNTIME findings require migration | ~0 | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

| ID | Gap | Risk | Mitigation |
|----|-----|------|------------|
| G1 | Category detection heuristics may have false negatives | Medium | Validate against W7 classification ground truth |
| G2 | Teams may rely on current scan behavior | Low | Document migration path; provide verbose mode showing all findings |
| G3 | Strict mode change is breaking for CI that expects exit 1 | Low | Coordinate with ops; new taxonomy is more accurate |

---

## P5: Classification Reconciliation (IN PROGRESS)

**Goal**: Reconcile 54 RUNTIME_POLICY_LEAKAGE + 154 UNKNOWN findings against W7 Phase 0 classification.

**Current State** (post-P1-P3):
```
[SUMMARY] Total detections: 255
[SUMMARY] Blocking: 208 (RUNTIME_POLICY_LEAKAGE: 54, UNKNOWN: 154)
[SUMMARY] Non-blocking: 47 (STATIC_REGISTRY: 31, OFFLINE_TOOLING: 4, FALSE_POSITIVE: 12)
```

**W7 Phase 0 Ground Truth**:
- W7 classified 297 violations total
- Only 2 RUNTIME_POLICY_LEAKAGE files required migration (placement_advisor.py, placement_advisor_types.py) — **DONE in W7 P1**
- Remaining ~295 approved as STATIC_REGISTRY_METADATA, OFFLINE_TOOLING_REFERENCE, or FALSE_POSITIVE

**Reconciliation Required**:

The scanner's heuristics are over-classifying. P5 validates each of the 208 blocking findings:

### P5.1: UNKNOWN Findings (154)

For each UNKNOWN finding:
1. Examine file path and content
2. Compare against W7 Phase 0 classification report
3. Determine correct category:
   - STATIC_REGISTRY_METADATA (registry entries, ownership tables, schemas)
   - OFFLINE_TOOLING_REFERENCE (ADG adapters, analysis tools)
   - FALSE_POSITIVE (docstrings, comments, examples)
   - RUNTIME_POLICY_LEAKAGE (true runtime branching — unlikely given W7)
4. Add content/file pattern to scanner for auto-classification
5. Or mark as GENERIC_ALLOWED with rationale if legitimate

**Deliverable**: UNKNOWN count = 0

### P5.2: RUNTIME_POLICY_LEAKAGE Findings (54)

For each RUNTIME finding:
1. Verify if true runtime policy leakage:
   - Does it branch on app_id/tenant_id at runtime?
   - Does it affect governed paths (U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L6)?
2. If false positive (over-classified):
   - Reclassify to STATIC_REGISTRY_METADATA (type definitions, constants)
   - Reclassify to OFFLINE_TOOLING_REFERENCE (tooling, analysis)
   - Reclassify to FALSE_POSITIVE (docstrings, examples)
3. If true runtime leakage:
   - Confirm not already fixed in W7
   - Document in P5.3 for potential W9 remediation plan

**Deliverable**: RUNTIME_POLICY_LEAKAGE = 0 (or documented true leaks for W9)

### P5.3: Classification Rule Refinement

Based on P5.1-P5.2 findings:
1. Update `classify_violation()` heuristics in `core_leakage_scan.py`
2. Add patterns for newly discovered categories
3. Re-run scan and verify UNKNOWN=0, RUNTIME=0
4. Document classification rationale for edge cases

**Deliverable**: Updated scanner with refined classification

---

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|--------------|
| DoD-1 | **strict scan exits 0 only when runtime policy leakage = 0** | `python tools/governance/core_leakage_scan.py --strict` exits 0 with current codebase (post-W7) |
| DoD-2 | **Static registry metadata is reported but non-blocking** | Scan output shows STATIC_REGISTRY count as INFO, not ERROR |
| DoD-3 | **Offline tooling references are reported but non-blocking** | Scan output shows OFFLINE_TOOLING count as INFO, not ERROR |
| DoD-4 | **False positives are excluded or separately reported** | Scan output shows FALSE_POSITIVE count as DEBUG or excludes entirely |
| DoD-5 | **CI remains green** | `python ops_scripts/ci/run_contract_gates.py` exits 0 |
| DoD-6 | **W6 delegation tests still pass** | `pytest tests/_apps_contract/test_w6_generic_delegation.py` passes (regression guard) |
| DoD-7 | **Documentation updated** | AGENTS.md references new scan taxonomy |
| DoD-8 | **W8 receipt generated** | Receipt exists at `artifacts/governance/agentic-core-governance-remediation-c4e8a2_w8_receipt.json` |
| DoD-9 | **0 UNKNOWN / UNCLASSIFIED findings in strict scan** | All findings classified; unknown count = 0 |

---

## Verification vs Deferral

| Item | Verify Now | Defer | Rationale |
|------|-----------|-------|-----------|
| Scanner taxonomy update | ✅ | | Core deliverable |
| Strict mode redefinition | ✅ | | Core deliverable |
| CI integration | ✅ | | Must not break existing gates |
| Full scan rule overhaul | | ✅ | W7 classification is sufficient scope |
| Additional test coverage | | ✅ | Existing tests validate behavior |

---

## Scanner Taxonomy Mapping (W7 Phase 0 → Scan Categories)

| W7 Phase 0 Category | Scan Severity | Exit Impact | Example Locations |
|-------------------|---------------|-------------|-------------------|
| **RUNTIME_POLICY_LEAKAGE** | CRITICAL/HIGH | ❌ Blocks strict mode | Runtime routing, policy checks |
| **STATIC_REGISTRY_METADATA** | INFO | ✅ Non-blocking | ModuleOwnership, schema enums |
| **OFFLINE_TOOLING_REFERENCE** | INFO | ✅ Non-blocking | ADG adapters, analysis tools |
| **FALSE_POSITIVE** | DEBUG or excluded | ✅ Non-blocking | Comments, test fixtures |
| **TRUE_CI_BREAKAGE** | WARN (if not fixed) | ✅ Non-blocking | Skill frontmatter (already fixed in W7) |
| **UNKNOWN / UNCLASSIFIED** | HIGH | ❌ Blocks strict mode | Unmapped detections requiring classification |

## Exit Logic Matrix

| Finding Mix | Strict Exit | Rationale |
|-------------|-------------|-----------|
| RUNTIME_POLICY_LEAKAGE > 0 | ❌ Nonzero | Actual governance risk detected |
| UNKNOWN / UNCLASSIFIED > 0 | ❌ Nonzero | Classification gap must be resolved |
| STATIC_REGISTRY_METADATA only | ✅ 0 | Approved non-runtime metadata |
| OFFLINE_TOOLING_REFERENCE only | ✅ 0 | Approved offline tooling |
| FALSE_POSITIVE only | ✅ 0 | No actual governance issue |
| No findings | ✅ 0 | Clean scan |

---

## Acceptance Criteria

1. `python tools/governance/core_leakage_scan.py --strict` exits 0 when runtime policy leakage = 0 AND unknown/unclassified = 0
2. Static registry metadata violations are reported as INFO (visible but non-blocking)
3. Offline tooling references are reported as INFO (visible but non-blocking)
4. False positives are excluded from strict mode or reported separately as DEBUG
5. `python ops_scripts/ci/run_contract_gates.py` exits 0 (CI remains green)
6. All W6 delegation tests pass (regression guard)
7. Scan output clearly distinguishes blocking vs non-blocking findings
8. W8 receipt generated with `remediation_complete=true`
9. **0 UNKNOWN / UNCLASSIFIED findings** — all detections have classification with source/rationale

---

## Related Artifacts

- W7 receipt: `artifacts/governance/agentic-core-governance-remediation-c4e8a2_w7_receipt.json`
- W7 classification: `artifacts/governance/w7_phase0_classification.md`
- Parent plan: `.windsurf/plans/agentic-core-governance-remediation-c4e8a2.md`
- W7 plan: `.windsurf/plans/agentic-core-governance-w7-non-delegation-violations-d4e8a2.md`
- Scanner: `tools/governance/core_leakage_scan.py`

---

## Notes

**Key implementation insight:** The scanner needs two-pass classification:
1. **Detection pass**: Find all app literal matches (current behavior)
2. **Classification pass**: Apply W7 taxonomy to categorize each match
3. **Severity assignment**: Map categories to severities per taxonomy table
4. **Exit logic**: RUNTIME_POLICY_LEAKAGE > 0 OR UNKNOWN/UNCLASSIFIED > 0 causes strict mode failure

**Strict Mode Transparency Requirement:**
Strict mode must NOT hide findings. It must emit:
- Total detections (all categories)
- Blocking findings (RUNTIME_POLICY_LEAKAGE + UNKNOWN/UNCLASSIFIED)
- Non-blocking classified findings (STATIC_REGISTRY, OFFLINE_TOOLING, FALSE_POSITIVE)
- Classification source/rationale (W7 Phase 0 classification)
- Unknown/unclassified findings count (must be 0 for strict pass)

**Backward compatibility:** Non-strict mode (--default) should maintain current behavior showing all violations. Only strict mode (--strict) implements the new taxonomy-based severity.

**Transparency Requirement (Per Constraint):**
Strict mode output must include:
```
[SUMMARY] Total detections: 304
[SUMMARY] Blocking: 0 (RUNTIME_POLICY_LEAKAGE: 0, UNKNOWN: 0)
[SUMMARY] Non-blocking: 304 (STATIC_REGISTRY: 140, OFFLINE_TOOLING: 60, FALSE_POSITIVE: 90, TRUE_CI_BREAKAGE: 5)
[CLASSIFICATION] Source: W7 Phase 0 classification report
[CLASSIFICATION] Rationale: Per-file runtime coupling analysis
[EXIT] Code: 0 (strict mode pass)
```
