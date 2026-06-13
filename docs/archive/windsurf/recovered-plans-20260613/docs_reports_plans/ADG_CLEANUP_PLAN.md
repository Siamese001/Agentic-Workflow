# ADG Violation Cleanup Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 🎯 Objective
Systematically reduce ADG violations from 1798 to below 1000 ceiling through targeted waves.

## 📊 Current Status
- **Total violations**: 1798 (798 excess over 1000 ceiling)
- **Consolidation work**: ✅ COMMITTED (Phase 1 complete)
- **Syntax errors**: Partially resolved (4/6 files fixed)
- **Next target**: <1000 violations

## 🌊 Wave-Based Cleanup Strategy

### Wave 1: Syntax Error Resolution (Priority: HIGH)
**Target**: Fix remaining syntax errors preventing proper ADG analysis

**Files to Fix**:
1. `tools/wave7b_multi_environment_hardener.py` - Multiple YAML syntax errors
2. `system_learning/pipelines/pipeline_factory.py` - Line 294 syntax error

**Expected Impact**: 
- Proper ADG scanning functionality
- Accurate violation counting
- Estimated reduction: 50-100 violations

### Wave 2: High-ROI Guardian Exemptions (Priority: HIGH)
**Target**: Add justified guardian exemptions to highest-ROI files

**Top 10 Files by Violations**:
1. `agentic_core/L0_routing/scripts/execute_ssot.py` (61 violations) - Already exempted
2. `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` (25 violations)
3. `agentic_core/L4_state/lifecycle/lifecycle_policy_applier.py` (11 violations)
4. `agentic_core/L5_safety/reasoning/GovernanceAgent.py` (14 violations)
5. `agentic_core/L4_state/enforcement/graph_memory_bridge.py` (10 violations)

**Expected Impact**: ~60 violations reduction

### Wave 3: Regression Failure Resolution (Priority: MEDIUM)
**Target**: Fix 7 regression failures in silent_degradation category

**Failed Files**:
- `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` (+1 excess)
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py` (+1 excess)
- `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` (+1 excess)
- `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` (+4 excess)
- `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` (+1 excess)
- `agentic_core/mixins/tracing_mixin.py` (+1 excess)
- `agentic_core/runtime/config/security_level_config.py` (+1 excess)

**Expected Impact**: ~10 violations reduction

### Wave 4: Medium-ROI File Cleanup (Priority: MEDIUM)
**Target**: Address violations in files with 5-10 violations

**Target Files**:
- `apps_rg/engines/base_rg_engine.py` (6 violations)
- `system_learning/pipelines/meta_learning_pipeline.py` (4 violations)
- `agentic_core/L5_safety/reasoning/hierarchy_healer.py` (6 violations)
- `system_learning/engines/prompt_provenance_builder.py` (9 violations)
- `agentic_core/L1_cognition/planning/plan_creator.py` (5 violations)

**Expected Impact**: ~30 violations reduction

### Wave 5: Bulk Pattern Resolution (Priority: LOW)
**Target**: Address common patterns across many files

**Violation Categories**:
- `path_fragility`: 398 violations
- `magic_configuration`: 303 violations
- `silent_swallower`: 468 violations
- `silent_degradation`: 513 violations

**Strategy**: Pattern-based fixes and additional guardian exemptions

## 🚀 Implementation Steps

### Step 1: Syntax Error Resolution
```bash
# Fix wave7b YAML syntax errors
# Fix pipeline_factory.py syntax error
# Test with python syntax validation
```

### Step 2: Guardian Exemption Strategy
```bash
# Add justified exemptions to high-ROI files
# Follow format: # guardian: allow-<pattern> -- <specific justification>
# Get HITL approval for new exemptions
```

### Step 3: Regression Fixes
```bash
# Fix silent_degradation regressions
# Focus on files exceeding ceilings
# Test fixes individually
```

### Step 4: Medium-ROI Cleanup
```bash
# Target files with 5-10 violations
# Use pattern-based fixes
# Add exemptions where appropriate
```

### Step 5: Final Push
```bash
# Address remaining bulk violations
# Use systematic approach
# Target <1000 total violations
```

## 📈 Success Metrics

### Phase Targets:
- **Wave 1**: 1798 → ~1700 violations
- **Wave 2**: ~1700 → ~1640 violations  
- **Wave 3**: ~1640 → ~1630 violations
- **Wave 4**: ~1630 → ~1600 violations
- **Wave 5**: ~1600 → <1000 violations

### Final Success Criteria:
- ✅ Total violations < 1000
- ✅ ADG burndown gate passes
- ✅ No regression failures
- ✅ All syntax errors resolved
- ✅ Guardian exemptions justified

## 🔄 Continuous Process

### Daily Monitoring:
```bash
# Run ADG burndown check
python ops_scripts/ci/adg_burndown_gate.py

# Track progress
# Update this plan
# Adjust strategy as needed
```

### Quality Assurance:
- All fixes must pass syntax validation
- Guardian exemptions must have specific justifications
- No new regressions introduced
- Maintain code quality standards

## 📋 Next Actions

1. **IMMEDIATE**: Fix remaining syntax errors (Wave 1)
2. **TODAY**: Add guardian exemptions to high-ROI files (Wave 2)
3. **THIS WEEK**: Address regression failures (Wave 3)
4. **NEXT WEEK**: Medium-ROI cleanup (Wave 4)
5. **FOLLOWING WEEK**: Bulk pattern resolution (Wave 5)

## 🎁 Expected Outcome

After completing all 5 waves:
- **ADG violations**: <1000 (below ceiling)
- **Code quality**: Maintained or improved
- **System stability**: No regressions
- **Documentation**: Complete cleanup record
- **Future maintenance**: Easier with reduced violations

This systematic approach ensures we reduce violations while maintaining code quality and system stability.

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

