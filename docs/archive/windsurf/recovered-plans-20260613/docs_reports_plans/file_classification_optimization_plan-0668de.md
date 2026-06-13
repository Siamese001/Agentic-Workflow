# FileClassificationAgent Integration Optimization Plan

This plan optimizes the integration of FileClassificationAgent within execute_ssot.py by adding early detection capabilities, improving confidence calculation, and ensuring comprehensive coverage across all phases.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

FileClassificationAgent is currently integrated in execute_ssot.py at:
- **Line 2187**: Registered in agents dictionary as "file_classification"
- **Line 2351-2367**: Executed in Phase 2.5 as "Sovereignty Enforcement"
- **Limited scope**: Only triggered when `pascal_proceed` is true based on location violations

## Issues Identified

1. **Late Execution**: FileClassificationAgent runs after Phase 3, missing early naming violations
2. **Limited Input**: Only uses location violations (`p1_loc`) for confidence calculation
3. **No Early Detection**: Doesn't contribute to Phase 1 discovery results
4. **Separate Execution**: Runs independently instead of integrated with other phases

## Optimization Strategy

### Phase 1: Early Detection Integration
- Add FileClassificationAgent to Phase 1 discovery alongside LocationAgent
- Capture naming and classification violations early
- Feed results into confidence calculation for better decision making

### Phase 2: Enhanced Confidence Calculation
- Include FileClassificationAgent violations in confidence scoring
- Provide comprehensive violation analysis to decision engine
- Enable more informed healing decisions

### Phase 3: Integrated Validation
- Use FileClassificationAgent results in architectural validation
- Ensure naming compliance is checked alongside structural validation

### Phase 4: Comprehensive Healing
- Integrate FileClassificationAgent healing with Governor healing plan
- Coordinate file renames with other structural changes

## Implementation Phases

### Phase 1: Add Early Detection (Lines 1294-1317)
```python
# After LocationAgent setup, add FileClassificationAgent
state_mgr.update_agent("FileClassificationAgent", "L5 - Safety")
file_classifier = agents["file_classification"](project_root=Path.cwd())

# Run classification scan on territory
classification_result = file_classifier.run(target_territory=territory)
classification_violations = classification_result.get("violations", [])
```

### Phase 2: Update Confidence Calculation (Lines 2337-2341)
```python
# Include both location and classification violations
total_violations = len(p1_loc) + len(classification_violations) if p1_loc and classification_violations else len(p1_loc or classification_violations or [])
pascal_confidence = decision_engine.calculate_healing_confidence(
    violations_count=total_violations,
    violation_types=["SOVEREIGNTY", "NAMING", "HEADER", "CLASSIFICATION"],
    territory=territory,
)
```

### Phase 3: Integrated Reporting (Lines 1310-1314)
```python
# Combine location and classification violations
all_violations = violations + classification_violations
location_scan_result = {
    "location_violations": violations,
    "classification_violations": classification_violations,
    "total_violations": len(all_violations),
    "violations": all_violations
}
```

### Phase 4: Coordinated Healing (Lines 2350-2367)
```python
# Update to use comprehensive violation data
if hasattr(pascal, "heal_repository"):
    res = pascal.heal_repository(
        target_territory=territory,
        dry_run=dry_run,
        auto_approve=auto_approve,
        violation_types=["NAMING", "HEADER", "CLASSIFICATION"],  # Explicit types
    )
```

## Test Cases Required

### Test 1: Early Detection Integration
- Verify FileClassificationAgent runs in Phase 1
- Check classification violations are captured
- Ensure results are stored in state manager

### Test 2: Enhanced Confidence Calculation
- Test confidence calculation with combined violations
- Verify decision engine receives comprehensive data
- Check healing decisions are more accurate

### Test 3: Integrated Reporting
- Verify combined violation reports
- Check state manager stores all violation types
- Ensure reporting includes classification data

### Test 4: Coordinated Healing
- Test healing with explicit violation types
- Verify file renames coordinate with other changes
- Check healing results include all violation types

### Test 5: Backward Compatibility
- Ensure existing functionality remains intact
- Test with territories that have no classification violations
- Verify dry-run mode works correctly

## File Diffs Summary

1. **execute_ssot.py**: Add early detection, update confidence calculation, enhance reporting
2. **FileClassificationAgent.py**: Add violation_types parameter to heal_repository method
3. **Test files**: Create comprehensive test suite for all phases

## Benefits

1. **Earlier Detection**: Naming violations caught in Phase 1 instead of Phase 2.5
2. **Better Decisions**: Confidence calculation based on comprehensive violation data
3. **Integrated Healing**: File renames coordinated with other structural changes
4. **Improved Reporting**: Complete violation picture across all types
5. **Maintained Compatibility**: All existing functionality preserved

## Risk Mitigation

1. **Backward Compatibility**: All changes are additive, no breaking changes
2. **Gradual Rollout**: Can be enabled via feature flag if needed
3. **Comprehensive Testing**: Full test coverage for all scenarios
4. **Rollback Plan**: Changes can be easily reverted if issues arise

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

