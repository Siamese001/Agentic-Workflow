# W7: Resolve Remaining Non-Delegation Core Governance Violations

## Plan Metadata

- **Plan ID**: agentic-core-governance-remediation-c4e8a2
- **Wave**: W7
- **Parent Remediation**: agentic-core-governance-remediation-c4e8a2
- **Created**: 2026-05-11
- **Status**: Not Started → In Progress
- **Dependencies**: W6 Complete (delegation scope clean)

## Problem Statement

W6 successfully cleaned `agentic_core/runtime/delegation` (zero app-specific literals, profile-driven implementation). However, the parent remediation c4e8a2 remains **PARTIAL / ENFORCEMENT ACTIVE** because:

1. `core_leakage_scan.py --strict` exits 1 (295 HIGH violations outside delegation scope)
2. `run_contract_gates.py` exits 1 (skill frontmatter failures unrelated to delegation)
3. 2 CRITICAL violations remain in other `agentic_core` modules

**Current violation distribution:**
- CRITICAL: 2 (app branching logic in non-delegation modules)
- HIGH: 295 (app-specific constants in adg/, applications/, contracts/)
- MEDIUM: 0
- Locations: `agentic_core/adg/`, `agentic_core/applications/`, `agentic_core/contracts/`

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W7 | P1-P3 | CRITICAL violations | ~800 | No breaking changes to TEMPORARY_THIN_ADAPTER | 🔲 TODO | 0 CRITICAL, core_leakage_scan critical-only exits 0 |
| W7 | P4-P7 | HIGH violations (adg/) | ~1200 | ADG analysis still functional post-migration | 🔲 TODO | adg/ folder has 0 HIGH violations |
| W7 | P8-P10 | HIGH violations (applications/) | ~600 | Placement advisor logic preserved | 🔲 TODO | applications/ folder has 0 HIGH violations |
| W7 | P11-P13 | HIGH violations (contracts/) | ~400 | Contract schema integrity maintained | 🔲 TODO | contracts/ folder has 0 HIGH violations |
| W7 | P14 | CI/skill fixes | ~200 | Frontmatter issues are auto-fixable | 🔲 TODO | run_contract_gates.py exits 0 |
| W7 | P15 | Final verification | ~100 | All gates pass sequentially | 🔲 TODO | ALL gates exit 0, remediation_complete=true |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| P1 | ADG MemoryAdapter fix | 1 file | Hardcoded app prefixes in tuple | ~300 | 🔲 TODO |
| P2 | ADG ModuleOwnership fix | 1 file | Literal app strings in enum/ownership table | ~300 | 🔲 TODO |
| P3 | Placement Advisor fix | 2 files | path.startswith() app checks | ~200 | 🔲 TODO |
| P4-P7 | ADG adapters/analysis | ~15 files | App-specific constants → profile refs | ~1200 | 🔲 TODO |
| P8-P10 | Applications folder | ~5 files | Generic resolver for placement logic | ~600 | 🔲 TODO |
| P11-P13 | Contracts schema | ~3 files | App enum → generic app registry lookup | ~400 | 🔲 TODO |
| P14 | Skill frontmatter | ~7 files | Add name/when-trigger per Anthropic spec | ~200 | 🔲 TODO |
| P15 | Verification & receipt | 1 receipt | Final strict scan + CI pass | ~100 | 🔲 TODO |

## Gap Register

| ID | Gap | Risk | Mitigation |
|----|-----|------|------------|
| G1 | ADG app prefixes may be load-bearing for analysis | High | Create ADG profile registry before removal |
| G2 | ModuleOwnership table drives actual ownership decisions | High | Ensure migrated to external registry |
| G3 | Placement advisor app checks may route real traffic | Medium | Feature-flag migration, verify with tests |
| G4 | Contract schema app enum may be serialized | Low | Version bump if schema changes |
| G5 | Skill frontmatter fixes may be extensive | Low | Template-based auto-fix acceptable |

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|-------------- |
| DoD-1 | 0 CORE_APP_SPECIFIC_LEAKAGE across all agentic_core | `grep -c CORE_APP_SPECIFIC_LEAKAGE artifacts/governance/scans/core_leakage_scan_*.json` returns 0 |
| DoD-2 | core_leakage_scan.py --strict exits 0 | Run command, verify exit code 0 |
| DoD-3 | run_contract_gates.py exits 0 | Run command, verify exit code 0 |
| DoD-4 | No unrelated CI failures | Only scheduled/long-term items remain |
| DoD-5 | W7 receipt generated with remediation_complete=true | Receipt exists and field is true |
| DoD-6 | All W6 delegation tests still pass | `pytest tests/_apps_contract/test_w6_generic_delegation.py` passes |
| DoD-7 | Parent remediation can be marked COMPLETE | Update parent receipt final_status to REMEDIATION_COMPLETE |

## Verification vs Deferral

| Item | Verify Now | Defer | Rationale |
|------|-----------|-------|-----------|
| CRITICAL violations fixed | ✅ | | Must be resolved for strict mode pass |
| HIGH violations in adg/ | ✅ | | Block strict mode, must resolve |
| HIGH violations in applications/ | ✅ | | Block strict mode, must resolve |
| HIGH violations in contracts/ | ✅ | | Block strict mode, must resolve |
| Skill frontmatter | ✅ | | Blocks CI pass, quick fix |
| TEMPORARY_THIN_ADAPTER receipts | | ✅ | Already verified valid in W6 |
| Full ADG re-architecture | | ✅ | Out of scope; migration to profiles is W7 scope |

## Files In Scope

**CRITICAL fixes:**
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` (line 469: hardcoded prefixes)
- `agentic_core/adg/adapters/memory_mcp_adapter.py` (line 412: hardcoded prefixes)
- `agentic_core/adg/analysis/ModuleOwnership.py` (lines 165, 197-198: app literals)
- `agentic_core/adg/analysis/ownership.py` (lines 165, 197-198: app literals)
- `agentic_core/adg/applications/placement_advisor.py` (lines 582, 584: path checks)
- `agentic_core/adg/applications/placement_advisor_types.py` (lines 582, 584: path checks)
- `agentic_core/adg/contracts/schema.py` (lines 567-572: app enum)

**Skill frontmatter fixes:**
- `.windsurf/skills/app-leakage-refactor/SKILL.md`
- `.windsurf/skills/core-boundary-audit/SKILL.md`
- `.windsurf/skills/ledger-consulter-ask-user-question/SKILL.md`
- `.windsurf/skills/receipt-auditor/SKILL.md`
- `.windsurf/skills/runtime-package-verifier/SKILL.md`
- `.windsurf/skills/scope-containment/SKILL.md`
- `.windsurf/skills/u0-app-customization/SKILL.md`

## Acceptance Criteria

1. `python tools/governance/core_leakage_scan.py --strict` exits 0
2. `python ops_scripts/ci/run_contract_gates.py` exits 0
3. 0 CORE_APP_SPECIFIC_LEAKAGE across all agentic_core
4. 0 CRITICAL violations remaining
5. W7 receipt generated with `remediation_complete=true`
6. Parent remediation c4e8a2 can be marked COMPLETE
7. All W6 delegation tests still pass (regression guard)

## Related Artifacts

- W6 receipt: `artifacts/governance/agentic-core-governance-remediation-c4e8a2_w6_receipt.json`
- Parent plan: `.windsurf/plans/agentic-core-governance-remediation-c4e8a2.md`
- W6 plan: `.windsurf/plans/agentic-core-governance-w6-core-migration-d4e8a2.md`
- Scan reports: `artifacts/governance/scans/core_leakage_scan_*.json`

## Notes

- W6 proved the profile-driven pattern works for delegation
- W7 applies same pattern to remaining core modules
- True full completion requires ALL gates passing
- No new TEMPORARY_THIN_ADAPTER receipts needed (W6 covered migration receipts)
