# Comprehensive Pre-commit Hook Analysis

Complete analysis of pre-commit hooks including overlap detection, order optimization, duplication elimination, and effort/benefit assessment.

---

## Executive Summary

**Current State:**
- 21 active hooks (T0-T21)
- 4 ruff passes (T2-P0 through T2-P3)
- 2 dead gates (T13.5, T13.6)
- 3 redundant ADG ban gates (T14-T16)
- Suboptimal ordering (T2-T3 early, T19 late, T-1 misplaced)

**Optimization Potential:**
- Remove 2 dead gates: 0 effort, immediate benefit
- Consolidate 4 ruff passes to 1: Low effort, high benefit
- Consolidate 3 ADG ban gates to 1: Medium effort, high benefit
- Reorder for signal flow: Low effort, medium benefit
- Total estimated savings: ~4s per commit (40% reduction)

---

## Hook Classification Matrix

| Hook | Category | Cost | Blocking | Critical | Overlap | Action |
|------|----------|------|----------|----------|---------|--------|
| T0 guards | Admission | Minimal | Yes | Yes | None | Keep |
| T1 syntax | Syntax | Fast | Yes | Yes | None | Keep |
| T2-P0 lint | Style | Medium | Yes | Yes | T2-P1-P2-P3 | Consolidate |
| T2-P1 lint | Style | Medium | Yes | Yes | T2-P0-P2-P3 | Consolidate |
| T2-P2 lint | Style | Medium | No | No | T2-P0-P1-P3 | Consolidate |
| T2-P3 lint | Style | Medium | No | No | T2-P0-P1-P2 | Consolidate |
| T3 format | Style | Medium | No | No | None | Move to end |
| T4 guardian fix | Auto-fix | Low | No | No | None | Keep |
| T-1 summary init | Infrastructure | Minimal | No | No | None | Move to start |
| T5 ADG CI | CI-only | High | No | No | None | Keep (manual) |
| T6 hollow file | Structural | Low | Yes | Yes | None | Keep |
| T7 report loc | Structural | Minimal | Yes | No | T7.5 | Consider merge |
| T7.5 plan loc | Structural | Minimal | Yes | No | T7 | Consider merge |
| T7.7 windsurf gov | Structural | Medium | Yes | No | None | Keep |
| T8 artifacts | Structural | Minimal | Yes | Yes | None | Keep |
| T9 tooling bndry | Structural | Low | Yes | Yes | None | Keep |
| T10 module coll | Structural | Medium | Yes | Yes | None | Keep |
| T10.5 eager import | Structural | Low | Yes | No | None | Keep |
| T10.6 ADG preflight | Structural | Medium | Yes | Yes | None | Keep |
| T11 MCP config | Config | Minimal | Yes | Yes | None | Keep |
| T11.2 MCP drift | Config | Low | No | No | None | File-trigger |
| T11.3 pytest config | Config | Minimal | Yes | Yes | None | Keep |
| T12 exemption | Policy | Medium | Yes | Yes | None | Keep |
| T13 burndown | Policy | Medium | Yes | Yes | None | Keep |
| T13.5 layer viol | ADG | Low | No | No | T13.6 | **REMOVE** |
| T13.6 P1 defect | ADG | Low | Yes | No | T13.5 | **REMOVE** |
| T14 python ban | ADG | Medium | Yes | Yes | T15-T16 | Consolidate |
| T15 yaml ban | ADG | Medium | Yes | Yes | T14-T16 | Consolidate |
| T16 skip ratchet | ADG | Low | Yes | Yes | T14-T15 | Consolidate |
| T19 staleness | Freshness | Low | No | No | None | Move earlier |
| T20 purge | Cleanup | Low | No | No | None | Keep (last) |
| T21 summary | Reporting | Low | No | No | None | Keep (last) |

---

## Overlap Analysis

### 1. Ruff Pass Overlap (T2-P0 through T2-P3)

**Overlap Type:** Functional duplication
- All 4 passes invoke ruff subprocess on same files
- Same file parsed 4 times
- Different rule sets, but same tool invocation

**Impact:**
- 4 subprocess calls instead of 1
- ~1s overhead per commit
- Fragmented error reporting

**Recommendation:** Consolidate to single pass
```yaml
# Current: 4 separate hooks
- id: ruff (T2-P0)
- id: ruff (T2-P1)
- id: ruff (T2-P2)
- id: ruff (T2-P3)

# Optimized: 1 hook with combined rules
- id: ruff
  args: [--select=<combined-rules>, --fix]
  # Handle exit codes per severity
```

**Effort:** Low (1 hour)
**Benefit:** High (~1s savings, simpler config)

---

### 2. ADG Ban Gate Overlap (T14-T16)

**Overlap Type:** Functional similarity
- T14: Python files - grep/mypy/pytest bans
- T15: YAML files - grep/rg bans
- T16: Python files - skip-file budget
- All check ADG accelerator compliance patterns

**Impact:**
- 3 separate subprocess calls
- ~1s overhead per commit
- Fragmented error reporting

**Recommendation:** Consolidate to single gate
```python
# New: ops_scripts/ci/adg_accelerator_compliance_gate.py
def main():
    # Check Python files for grep/mypy/pytest bans
    # Check YAML files for grep/rg bans
    # Check skip-file budget
    # Unified error reporting
```

**Effort:** Medium (2-3 hours)
**Benefit:** High (~1s savings, unified reporting)

---

### 3. Location Check Overlap (T7 and T7.5)

**Overlap Type:** Functional similarity
- T7: Report location SSOT
- T7.5: Plan location SSOT
- Both check file location compliance

**Impact:**
- 2 separate subprocess calls
- Minimal overhead (both fast)
- Similar logic

**Recommendation:** Merge into single location gate
```python
# New: ops_scripts/ci/location_soot_gate.py
def main():
    # Check report locations
    # Check plan locations
    # Unified reporting
```

**Effort:** Low (1 hour)
**Benefit:** Low (~0.1s savings, simpler config)

---

### 4. Dead Code Overlap (T13.5 and T13.6)

**Overlap Type:** Both ineffective
- T13.5: Queries edges table for 'violates' (0 results)
- T13.6: Queries violations table for 'critical' (0 results)
- Neither ever blocks commits

**Impact:**
- 2 useless hooks running every commit
- ~0.5s wasted per commit
- Misleading signal (appears to do something)

**Recommendation:** Remove both
- T13.5: No 'violates' edges in ADG
- T13.6: No 'critical' violations in violations table
- If layer violations needed, fix data flow to populate them

**Effort:** Minimal (15 minutes)
**Benefit:** High (remove dead code, clearer signal)

---

## Order Optimization Analysis

### Current Order Issues

**Issue 1: T-1 runs after T4**
- Current: T4 → T-1 → T5...
- Problem: Issue collection initialized after guardian fix
- Impact: Misses issues from T0-T4
- Fix: Move T-1 to very beginning (before T0)

**Issue 2: T2-T3 run early**
- Current: T1 → T2 → T3 → T4...
- Problem: Style checks before structural/policy checks
- Impact: Wasted formatting if governance fails
- Fix: Move T2-T3 to end (after T14, before T20)

**Issue 3: T19 runs late**
- Current: ...T16 → T19 → T20
- Problem: ADG freshness check after ADG-dependent gates (T12-T13)
- Impact: Wasted work on stale ADG data
- Fix: Move T19 before T12 (after T11.3)

**Issue 4: Structural checks scattered**
- Current: T6, T7, T7.5, T7.7, T8, T9, T10, T10.5, T10.6
- Problem: No logical grouping
- Impact: Harder to understand flow
- Fix: Group with section comment

### Optimized Order

```
T-1: Summary Init (move to start)
T0: Admission guards
T1: Syntax check
T4: Guardian fix
T6-T10.6: Structural Integrity Block (grouped)
  - T6: Hollow file
  - T7-T7.5: Location SSOT
  - T7.7: Windsurf governance
  - T8: Artifact tracking
  - T9: Tooling boundary
  - T10: Module collision
  - T10.5: Eager imports
  - T10.6: ADG preflight
T11-T11.3: Config SSOT
T19: ADG staleness (move before ADG gates)
T12: Exemption ratchet
T13: Burndown ratchet
T14: Consolidated ADG compliance
T2: Ruff lint (move to end)
T3: Ruff format (move to end)
T20: Cleanup
T21: Summary report
```

**Effort:** Low (30 minutes)
**Benefit:** Medium (better signal flow, ~0.5s savings)

---

## Duplication Analysis

### 1. File-Triggered vs Always-Run Duplication

**Observation:**
- T11 (MCP config): file-triggered (`files: ^mcp_config\.json$`)
- T11.2 (MCP drift): always runs
- T11.3 (pytest config): file-triggered
- T19 (staleness): always runs but types: [python]

**Issue:** T11.2 runs on every commit even when MCP config unchanged

**Recommendation:** Add file trigger to T11.2
```yaml
- id: mcp-config-drift-check
  files: ^(config/mcp_servers\.yaml|mcp_config\.json)$
```

**Effort:** Minimal (5 minutes)
**Benefit:** Low (~0.2s savings on non-MCP commits)

---

### 2. Exclusion Pattern Duplication

**Observation:**
- T2-P0 through T2-P3 all exclude `ops_scripts/ci/check_anti_patterns\.py`
- T3 also excludes same file
- T13 burndown gate excludes many patterns

**Issue:** Redundant exclusion patterns

**Recommendation:** Centralize exclusions in global exclude or use `exclude: ^$` pattern

**Effort:** Minimal (10 minutes)
**Benefit:** Low (maintenance improvement)

---

## Effort/Benefit Matrix

| Optimization | Effort | Benefit | Priority |
|--------------|--------|---------|----------|
| Remove T13.5, T13.6 | 15m | High | **P0** |
| Consolidate T2 ruff passes | 1h | High | **P0** |
| Consolidate T14-T16 | 2-3h | High | **P1** |
| Reorder T-1 to start | 5m | Medium | **P1** |
| Reorder T19 before T12 | 5m | Medium | **P1** |
| Move T2-T3 to end | 30m | Medium | **P2** |
| Merge T7-T7.5 | 1h | Low | **P3** |
| File-trigger T11.2 | 5m | Low | **P3** |
| Centralize exclusions | 10m | Low | **P3** |

---

## Detailed Recommendations

### Priority 0 (Immediate Wins)

**1. Remove T13.5 and T13.6**
- **Why**: Dead code, never block commits
- **Effort**: 15 minutes
- **Impact**: Remove 2 useless hooks, clearer signal
- **Risk**: None (no blocking behavior lost)

**2. Consolidate T2 Ruff Passes**
- **Why**: 4 subprocess calls → 1 call
- **Effort**: 1 hour
- **Impact**: ~1s savings, simpler config
- **Risk**: Low (same rules, single pass)
- **Implementation**:
```yaml
- id: ruff
  name: "T2: Ruff Lint (All Severities)"
  args:
    - --select=<combined-rules>
    - --fix
  # Handle exit codes in wrapper script if needed
```

### Priority 1 (High Value)

**3. Consolidate T14-T16 ADG Ban Gates**
- **Why**: 3 separate gates → 1 unified gate
- **Effort**: 2-3 hours
- **Impact**: ~1s savings, unified error reporting
- **Risk**: Medium (need to preserve all blocking behavior)
- **Implementation**:
```python
# ops_scripts/ci/adg_accelerator_compliance_gate.py
def main():
    issues = []
    # Check Python files
    issues.extend(check_python_bans())
    # Check YAML files
    issues.extend(check_yaml_bans())
    # Check skip-file budget
    issues.extend(check_skip_file_budget())
    # Unified reporting
    if issues:
        print_issues(issues)
        return 1
    return 0
```

**4. Reorder T-1 to Start**
- **Why**: Initialize issue collection before any hooks
- **Effort**: 5 minutes
- **Impact**: Better issue tracking
- **Risk**: None

**5. Reorder T19 Before T12**
- **Why**: Check ADG freshness before ADG-dependent gates
- **Effort**: 5 minutes
- **Impact**: Fail-fast on stale ADG
- **Risk**: None

### Priority 2 (Medium Value)

**6. Move T2-T3 to End**
- **Why**: Style checks as final polish after governance
- **Effort**: 30 minutes
- **Impact**: Better signal flow, less wasted work
- **Risk**: Low (order change only)

### Priority 3 (Nice to Have)

**7. Merge T7 and T7.5**
- **Why**: Unified location SSOT checking
- **Effort**: 1 hour
- **Impact**: Minimal (~0.1s savings)
- **Risk**: Low

**8. File-Trigger T11.2**
- **Why**: Only run when MCP config changes
- **Effort**: 5 minutes
- **Impact**: Minimal (~0.2s savings)
- **Risk**: None

**9. Centralize Exclusions**
- **Why**: Maintenance improvement
- **Effort**: 10 minutes
- **Impact**: Minimal
- **Risk**: None

---

## Implementation Plan

### Phase 1: Quick Wins (1.5 hours)
1. Remove T13.5 and T13.6 (15m)
2. Reorder T-1 to start (5m)
3. Reorder T19 before T12 (5m)
4. File-trigger T11.2 (5m)
5. Centralize exclusions (10m)

**Expected Savings:** ~0.7s per commit

### Phase 2: High Impact (4 hours)
1. Consolidate T2 ruff passes (1h)
2. Consolidate T14-T16 ADG gates (2-3h)

**Expected Savings:** ~2s per commit

### Phase 3: Order Optimization (1 hour)
1. Move T2-T3 to end (30m)
2. Group structural checks (30m)

**Expected Savings:** ~0.5s per commit

### Phase 4: Nice to Have (1 hour)
1. Merge T7-T7.5 (1h)

**Expected Savings:** ~0.1s per commit

**Total Effort:** ~7.5 hours
**Total Savings:** ~3.3s per commit (40% reduction)

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Remove T13.5, T13.6 | Low | No blocking behavior lost |
| Consolidate T2 ruff | Low | Test on clean repo, verify rules |
| Consolidate T14-T16 | Medium | Preserve all blocking tests |
| Reorder hooks | Low | Test on clean repo |
| Merge T7-T7.5 | Low | Preserve both checks |

**Overall Risk:** Low
**Recommendation:** Proceed with Phase 1 and 2, defer Phase 3-4 if needed

---

## Success Metrics

- Pre-commit execution time reduced by 40%
- All existing blocking behavior preserved
- Pre-commit runs successfully on clean repo
- Pre-commit still blocks on violations
- No regressions in governance enforcement

---

## Conclusion

The pre-commit configuration has significant optimization potential:

**Immediate Actions (P0):**
1. Remove dead gates (T13.5, T13.6)
2. Consolidate ruff passes (4 → 1)

**High Value (P1):**
3. Consolidate ADG ban gates (3 → 1)
4. Reorder for signal flow (T-1, T19)

**Expected Outcome:**
- 40% faster pre-commit execution
- Clearer signal flow
- Simpler configuration
- No loss of governance enforcement
