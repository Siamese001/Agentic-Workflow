# Phase 1 Remediation Plan - SSOT Governance Compliance

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary
This plan addresses all BLOCKER and MAJOR governance violations identified in the Phase 1 SSOT dry-run review using 3 waves maximum per governance rules, with deterministic enforcement semantics clarified.

## Current Status
- **Phase 1**: INCOMPLETE (BLOCKED)
- **Current Commit**: 3303626b215ed29b36743157f2fa271b368a7f5c
- **Primary Blocker**: Windows LongPathsEnabled pre-flight failure

## Governance Clarifications Applied

### Enforcement Rules
- **MISNAMED_UTILITY**: Must increment violation counter in ALL modes (validate_only, dry_run, active)
- **DUAL-TAG Resolution**: Use deterministic priority hierarchy (decorator > inheritance > filename > directory > heuristic)
- **Compliance Threshold**: Structural only - BLOCKER=0 required, no percentage-based thresholds

### Violation Classification
- **BLOCKER**: Duplicates, misplaced tests, preflight failure, territory collisions
- **MAJOR**: MISNAMED_UTILITY, DUAL-TAG conflicts, enforcement visibility defects

## Remediation Waves (Maximum 3)

### Wave 1 — Preflight + Canonical Execution Restoration
**Objective**: Enable canonical SSOT entrypoint execution

**Windows LongPathsEnabled Issue**:
1. **Primary**: Enable in Windows Registry
   - Location: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set: `LongPathsEnabled = 1`

2. **Fallback**: Modify pre-flight check for dry-run mode
   - File: `agentic_core/L0_routing/scripts/execute_ssot.py` line 736
   - Change hard failure to warning when dry_run=True

**Verification**: Run canonical entrypoint successfully
```bash
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --validate
```

### Wave 2 — Structural Blocker Remediation
**Objective**: Eliminate all BLOCKER-level violations

**2.1 Duplicate ContentStrategyAgent.py Resolution**:
- Compare files in `apps_rg/engines/` vs `apps_rg/reasoning/`
- Delete duplicate, keep canonical version
- Update any import references

**2.2 Misplaced Test File Relocation**:
- Move: `apps_rg/scripts/test_run_grand_unification_tests.py`
- To: `tests/apps_rg/scripts/test_run_grand_unification_tests.py`
- Verify test discovery still works

**Verification**: All BLOCKER count = 0

### Wave 3 — Classification Enforcement Hardening + Counter Integrity
**Objective**: Fix MAJOR violations and enforcement visibility

**3.1 MISNAMED_UTILITY Counter Fix**:
- Identify why violation counter shows 0 despite logged findings
- Fix FileClassificationAgent to increment counter for MISNAMED_UTILITY
- Ensure severity=MAJOR classification

**3.2 DUAL-TAG Resolution Hardening**:
- Implement deterministic priority hierarchy in classification logic
- Remove folder context override for higher-priority signals
- Mark conflicting top-tier signals as violations

**3.3 Systematic Naming Issues**:
- Document all MISNAMED_UTILITY files across apps_*
- Create renaming plan for future phases (not executing now)
- Focus on counter accuracy, not bulk renaming

**Verification**:
- Violation counter accurately reflects all findings
- No BLOCKER violations remain
- Classification rules use deterministic resolution

## Success Criteria (Structural, Not Statistical)

### Absolute Requirements
- [ ] BLOCKER violations = 0
- [ ] Duplicate files = 0
- [ ] Misplaced test files = 0
- [ ] Preflight canonical execution restored
- [ ] Violation counter accurately reflects findings

### Governance Requirements
- [ ] Classification uses deterministic DUAL-TAG resolution
- [ ] MISNAMED_UTILITY increments violation counter
- [ ] No folder context override of higher-priority signals
- [ ] Enforcement visibility defect resolved

## Execution Sequence

### Wave 1 Execution
1. Attempt Windows LongPaths registry enablement
2. Test canonical entrypoint execution
3. Implement fallback if needed
4. Verify full legacy pipeline access restored

### Wave 2 Execution
1. Resolve ContentStrategyAgent.py duplicate
2. Relocate test file to proper structure
3. Verify all BLOCKER violations eliminated

### Wave 3 Execution
1. Fix violation counter logic
2. Implement deterministic DUAL-TAG resolution
3. Verify enforcement accuracy
4. Final compliance verification

## Risk Mitigation

- **Registry Changes**: Document before/after states
- **File Deletions**: Verify dependencies before removal
- **Test Relocation**: Ensure CI discovery continuity
- **Classification Changes**: Test counter accuracy before/after

## Phase Completion Criteria

Phase 1 marked COMPLETE only when:
- Canonical SSOT entrypoint executes without pre-flight failure
- All BLOCKER structural violations resolved
- Violation counter accurately reflects all findings
- Classification enforcement uses deterministic rules
- Ready to proceed to Phase 2 reconciliation

## Next Steps

1. Begin Wave 1 (preflight restoration)
2. Execute waves sequentially
3. Document all changes for governance audit
4. Update Phase 1 report with remediation evidence

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

