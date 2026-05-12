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
| W8 | P1 | Scanner taxonomy update | ~400 | W7 classification finalized | 🔲 TODO | Scanner distinguishes 5 categories |
| W8 | P2 | Strict mode redefinition | ~200 | P1 taxonomy implemented | 🔲 TODO | strict exits 0 when runtime=0 |
| W8 | P3 | CI integration verification | ~200 | P2 strict mode working | 🔲 TODO | CI remains green, reports meaningful counts |
| W8 | P4 | Documentation update | ~100 | P3 verified | 🔲 TODO | AGENTS.md references new taxonomy |

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
| P1.1 | Taxonomy rule implementation | `core_leakage_scan.py` rule engine | PP-1: Current rules don't distinguish categories | ~200 | 🔲 TODO |
| P1.2 | Category mapping definitions | Config/spec files | PP-2: Need canonical category definitions | ~200 | 🔲 TODO |
| P2.1 | Strict mode severity logic | `core_leakage_scan.py` --strict flag | PP-3: Strict mode treats all violations equally | ~100 | 🔲 TODO |
| P2.2 | Non-blocking category handling | Exit code logic | PP-4: Exit code logic needs category awareness | ~100 | 🔲 TODO |
| P3.1 | CI gate verification | `run_contract_gates.py` integration | PP-5: Gate must accept new taxonomy | ~100 | 🔲 TODO |
| P3.2 | Baseline scan run | Full repo scan | PP-6: Establish new baseline counts | ~100 | 🔲 TODO |
| P4.1 | AGENTS.md update | Documentation | GAP-1: Need taxonomy reference | ~50 | 🔲 TODO |
| P4.2 | Scan output format docs | README/help text | GAP-2: Users need category legend | ~50 | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

| ID | Gap | Risk | Mitigation |
|----|-----|------|------------|
| G1 | Category detection heuristics may have false negatives | Medium | Validate against W7 classification ground truth |
| G2 | Teams may rely on current scan behavior | Low | Document migration path; provide verbose mode showing all findings |
| G3 | Strict mode change is breaking for CI that expects exit 1 | Low | Coordinate with ops; new taxonomy is more accurate |

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

---

## Acceptance Criteria

1. `python tools/governance/core_leakage_scan.py --strict` exits 0 when runtime policy leakage = 0
2. Static registry metadata violations are reported as INFO (visible but non-blocking)
3. Offline tooling references are reported as INFO (visible but non-blocking)
4. False positives are excluded from strict mode or reported separately as DEBUG
5. `python ops_scripts/ci/run_contract_gates.py` exits 0 (CI remains green)
6. All W6 delegation tests pass (regression guard)
7. Scan output clearly distinguishes blocking vs non-blocking findings
8. W8 receipt generated with `remediation_complete=true`

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
4. **Exit logic**: Only RUNTIME_POLICY_LEAKAGE causes strict mode failure

**Backward compatibility:** Non-strict mode (--default) should maintain current behavior showing all violations. Only strict mode (--strict) implements the new taxonomy-based severity.
