# FileClassificationAgent Fixes Implementation Plan

This plan fixes critical inconsistencies in the FileClassificationAgent through a phased approach that ensures system stability while addressing architectural violations between detection and healing logic.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Critical Runtime Fixes (Immediate)

**Objective:** Prevent crashes and restore basic functionality

### 1.1 Fix Undefined Logger
- **Issue:** `Logger.info()` called but Logger not defined (Line 657)
- **Impact:** Runtime crash when healing invoked
- **Fix:** Add proper logging import after line 44
- **Risk:** Low - simple import addition
- **Testing:** Verify agent can be instantiated and heal() called without crash

### 1.2 Remove Redundant Import
- **Issue:** `standard_heal` imported inside method (Line 649) but already imported at line 35
- **Impact:** Potential circular import, inconsistent usage
- **Fix:** Remove redundant import statement
- **Risk:** Low - import cleanup
- **Testing:** Verify heal() method still works

### 1.3 Update File Header Documentation
- **Issue:** Header references wrong filename (PascalSovereigntyAgent.py)
- **Impact:** Developer confusion, maintenance issues
- **Fix:** Update header to reference FileClassificationAgent.py
- **Risk:** None - documentation only
- **Testing:** N/A

## Phase 2: Core Logic Unification (High Priority)

**Objective:** Fix fundamental detection vs healing inconsistency

### 2.1 Unify Detection/Healing Logic
- **Issue:** Classification uses sophisticated AST analysis, healing uses crude string matching
- **Impact:** Files detected as AGENT may not be healed correctly
- **Fix:** Replace healing logic (Lines 674-728) with call to classify_file() and get_compliant_name()
- **Risk:** Medium - core logic change
- **Testing:** Test with prompt_governance files to ensure consistent behavior

### 2.2 Remove Dead Code Blocks
- **Issue:** Duplicate TEST handling logic (Lines 575-587 unreachable)
- **Issue:** Redundant UTILITY check (Lines 572-573 unreachable)
- **Impact:** Code maintenance nightmare, confusion
- **Fix:** Remove unreachable code blocks
- **Risk:** Low - dead code removal
- **Testing:** Verify existing functionality preserved

## Phase 3: Validation and Testing (Medium Priority)

**Objective:** Ensure fixes work correctly and don't break existing functionality

### 3.1 Update Test Cases
- **File:** `tests/guardian/test_pascal_edge_cases.py`
- **Issue:** Test may need updates for new logic
- **Fix:** Review and update test expectations
- **Risk:** Low - test updates only
- **Testing:** Run full test suite

### 3.2 Integration Testing with Prompt Governance
- **Target:** `agentic_core/prompt_governance/agents/` files
- **Test:** Verify files are correctly classified and healed
- **Expected:** Files should be renamed to *Agent.py pattern
- **Risk:** Medium - integration testing
- **Testing:** Dry-run execution on prompt_governance territory

### 3.3 Performance Validation
- **Test:** Ensure no performance degradation from changes
- **Metrics:** File processing time, memory usage
- **Risk:** Low - monitoring only
- **Testing:** Benchmark before/after

## Phase 4: Code Quality Polish (Low Priority)

**Objective:** Improve maintainability and consistency

### 4.1 Standardize Comment Styles
- **Issue:** Inconsistent comment formatting throughout file
- **Fix:** Adopt consistent comment style (prefer `# [CATEGORY] Description`)
- **Risk:** None - cosmetic only
- **Testing:** N/A

### 4.2 Code Organization Review
- **Issue:** Methods could be better organized
- **Fix:** Group related methods, add section comments
- **Risk:** None - structural organization
- **Testing:** N/A

## Implementation Dependencies

### Required Files
- `agentic_core/L5_safety/validators/FileClassificationAgent.py` (primary)
- `tests/guardian/test_pascal_edge_cases.py` (test updates)
- `agentic_core/L5_safety/validators/decorators.py` (dependency verification)

### System Integration Points
- `execute_ssot.py` - calls FileClassificationAgent.heal_repository()
- Prompt governance files - test targets for validation
- Test suite - must pass after changes

## Risk Mitigation

### Backup Strategy
- Git branch created before any changes
- Original file backed up to `.bak` file
- Rollback plan documented

### Testing Strategy
- Unit tests for each fix
- Integration tests with prompt_governance
- Regression tests for existing functionality
- Performance benchmarks

### Rollback Criteria
- Any test failure in existing test suite
- Performance degradation >10%
- Integration failures with execute_ssot.py

## Success Metrics

### Functional Metrics
- [ ] Logger undefined error eliminated
- [ ] Detection/healing logic unified
- [ ] All dead code removed
- [ ] Prompt governance files correctly processed

### Quality Metrics
- [ ] Zero lint errors
- [ ] Test suite passes 100%
- [ ] No performance degradation
- [ ] Documentation accurate

### Integration Metrics
- [ ] execute_ssot.py integration works
- [ ] Prompt governance violations resolved
- [ ] No breaking changes to dependent systems

## Timeline Estimation

- **Phase 1:**  (critical fixes)
- **Phase 2:**  (core logic changes)
- **Phase 3:**  (testing and validation)
- **Phase 4:**  (polish)
- **Total:** 

## Next Steps

1. Create git branch for changes
2. Execute Phase 1 fixes
3. Test basic functionality
4. Execute Phase 2 core changes
5. Comprehensive testing
6. Execute Phase 3 validation
7. Execute Phase 4 polish
8. Final integration testing
9. Merge to main branch

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

