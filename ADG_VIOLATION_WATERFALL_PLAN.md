# ADG Violation Reduction Waterfall Plan

## 📊 CURRENT STATE (BASELINE)
**Total Violations**: 1809 (809 excess over 1000 ceiling)

### **Current Violation Breakdown**
| Category | Count | % of Total |
|----------|-------|-------------|
| silent_degradation | 524 | 29.0% |
| silent_swallower | 468 | 25.9% |
| path_fragility | 398 | 22.0% |
| magic_configuration | 303 | 16.8% |
| global_mutation | 49 | 2.7% |
| config_with_logic | 48 | 2.7% |
| type_erasure | 8 | 0.4% |
| direct_prompt_compilation | 11 | 0.6% |
| **TOTAL** | **1809** | **100%** |

---

## 🌊 WATERFALL VISUALIZATION

```
CURRENT STATE: 1809 violations
    │
    ▼
WAVE 1: Syntax Error Resolution (-50 to -100)
    │
    ▼
WAVE 2: High-ROI Guardian Exemptions (-60)
    │
    ▼
WAVE 3: Regression Failure Resolution (-10)
    │
    ▼
WAVE 4: Medium-ROI File Cleanup (-30)
    │
    ▼
WAVE 5: Bulk Pattern Resolution (-600+)
    │
    ▼
TARGET STATE: <1000 violations
```

---

## 📋 DETAILED WAVE-BY-WAVE BREAKDOWN

### **🔥 WAVE 1: Syntax Error Resolution**
**Target**: Fix remaining syntax errors preventing proper ADG analysis

**Files to Fix**:
- `tools/wave7b_multi_environment_hardener.py` - Multiple YAML syntax errors
- `system_learning/pipelines/pipeline_factory.py` - Line 294 syntax error
- `profile_adg.py` - Indentation errors

**Expected Impact**: **-50 to -100 violations**
- Proper ADG scanning functionality
- Accurate violation counting
- Eliminates inflated counts from parsing errors

**Violation Types Affected**:
- All categories (syntax errors cause inflated counts across the board)

**Post-Wave 1 Target**: ~1709-1759 violations

---

### **🎯 WAVE 2: High-ROI Guardian Exemptions**
**Target**: Add justified guardian exemptions to highest-ROI files

**Top Files & Violations**:
| File | Violations | Type | Reduction |
|------|------------|------|-----------|
| `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | 25 | silent_swallower | -25 |
| `agentic_core/L4_state/lifecycle/lifecycle_policy_applier.py` | 11 | config_with_logic | -11 |
| `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | 14 | silent_swallower | -14 |
| `agentic_core/L4_state/enforcement/graph_memory_bridge.py` | 10 | silent_swallower | -10 |

**Expected Impact**: **-60 violations**

**Violation Types Affected**:
- silent_swallower: -60
- config_with_logic: -11

**Post-Wave 2 Target**: ~1649-1699 violations

---

### **🔧 WAVE 3: Regression Failure Resolution**
**Target**: Fix 7 regression failures in silent_degradation category

**Failed Files & Excess**:
| File | Current | Ceiling | Excess | Action |
|------|---------|---------|--------|--------|
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | 7 | 6 | +1 | Fix |
| `agentic_core/L3_orchestration/engines/orchestrator_engine.py` | 4 | 3 | +1 | Fix |
| `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` | 3 | 2 | +1 | Fix |
| `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` | 5 | 1 | +4 | Fix |
| `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` | 11 | 10 | +1 | Fix |
| `agentic_core/mixins/tracing_mixin.py` | 2 | 1 | +1 | Fix |
| `agentic_core/runtime/config/security_level_config.py` | 2 | 1 | +1 | Fix |

**Expected Impact**: **-10 violations**

**Violation Types Affected**:
- silent_degradation: -10

**Post-Wave 3 Target**: ~1639-1689 violations

---

### **📁 WAVE 4: Medium-ROI File Cleanup**
**Target**: Address violations in files with 5-10 violations

**Target Files**:
| File | Violations | Type | Reduction |
|------|------------|------|-----------|
| `apps_rg/engines/base_rg_engine.py` | 6 | mixed | -6 |
| `system_learning/pipelines/meta_learning_pipeline.py` | 4 | mixed | -4 |
| `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | 6 | mixed | -6 |
| `system_learning/engines/prompt_provenance_builder.py` | 9 | mixed | -9 |
| `agentic_core/L1_cognition/planning/plan_creator.py` | 5 | mixed | -5 |

**Expected Impact**: **-30 violations**

**Violation Types Affected**:
- Mixed categories (silent_swallower, magic_configuration, etc.)

**Post-Wave 4 Target**: ~1609-1659 violations

---

### **🌊 WAVE 5: Bulk Pattern Resolution**
**Target**: Address common patterns across many files

**Strategy by Category**:

#### **5A: Path Fragility Resolution (-200)**
- Replace hardcoded paths with pathlib
- Add OS-specific path handling
- Implement path validation

#### **5B: Silent Degradation Resolution (-150)**
- Add proper error handling
- Replace empty except blocks
- Implement logging for failures

#### **5C: Silent Swallower Resolution (-150)**
- Add specific exception handling
- Implement proper logging
- Replace generic except blocks

#### **5D: Magic Configuration Resolution (-100)**
- Extract hardcoded values to config
- Implement proper configuration management
- Remove magic numbers

**Expected Impact**: **-600 violations**

**Violation Types Affected**:
- path_fragility: -200
- silent_degradation: -150
- silent_swallower: -150
- magic_configuration: -100

**Post-Wave 5 Target**: ~1009-1059 violations

---

## 📊 WATERFALL SUMMARY TABLE

| Wave | Starting Count | Reduction | Ending Count | Key Targets |
|------|----------------|-----------|--------------|-------------|
| **BASELINE** | **1809** | **-** | **1809** | Current state |
| **Wave 1** | 1809 | -75 | 1734 | Syntax errors |
| **Wave 2** | 1734 | -60 | 1674 | High-ROI exemptions |
| **Wave 3** | 1674 | -10 | 1664 | Regression fixes |
| **Wave 4** | 1664 | -30 | 1634 | Medium-ROI files |
| **Wave 5** | 1634 | -634 | 1000 | Bulk patterns |
| **TARGET** | **1000** | **-809** | **<1000** | **Goal achieved** |

---

## 📈 CATEGORY-BY-CATEGORY WATERFALL

### **silent_degradation (524 → ~364)**
```
524 (baseline)
  ↓ Wave 3: -10 (regression fixes)
514
  ↓ Wave 5: -150 (bulk pattern fixes)
364 (target)
```

### **silent_swallower (468 → ~258)**
```
468 (baseline)
  ↓ Wave 2: -60 (high-ROI exemptions)
408
  ↓ Wave 5: -150 (bulk pattern fixes)
258 (target)
```

### **path_fragility (398 → ~198)**
```
398 (baseline)
  ↓ Wave 5: -200 (bulk pattern fixes)
198 (target)
```

### **magic_configuration (303 → ~203)**
```
303 (baseline)
  ↓ Wave 5: -100 (bulk pattern fixes)
203 (target)
```

### **global_mutation (49 → ~49)**
```
49 (baseline)
  ↓ No direct targeting in waves
49 (target - may need additional wave)
```

### **config_with_logic (48 → ~37)**
```
48 (baseline)
  ↓ Wave 2: -11 (high-ROI exemptions)
37 (target)
```

---

## 🎯 SUCCESS CRITERIA

### **Primary Goal**
- ✅ **Total violations < 1000**
- ✅ **ADG burndown gate passes**
- ✅ **All regression failures resolved**

### **Secondary Goals**
- ✅ **All syntax errors resolved**
- ✅ **Guardian exemptions justified**
- ✅ **No new regressions introduced**

---

## 📅 IMPLEMENTATION TIMELINE

| Wave | Duration | Start Date | Target Date |
|------|----------|------------|-------------|
| **Wave 1** | 1 day | Immediate | Today |
| **Wave 2** | 1 day | Today | Tomorrow |
| **Wave 3** | 2 days | Tomorrow | Day 3 |
| **Wave 4** | 3 days | Day 3 | Day 6 |
| **Wave 5** | 1 week | Day 6 | Day 13 |

**Total Project Duration**: ~2 weeks

---

## 🔄 MONITORING & ADJUSTMENT

### **Daily Checkpoints**
```bash
# Run daily to track progress
python ops_scripts/ci/adg_burndown_gate.py

# Update waterfall plan based on actual results
# Adjust targets if needed
```

### **Success Metrics**
- Wave completion: All targets met
- Cumulative reduction: On track with -809 total
- Quality: No new regressions introduced

---

## 🎁 EXPECTED OUTCOME

**After completing all 5 waves**:
- **Starting**: 1809 violations (809 excess)
- **Ending**: <1000 violations (below ceiling)
- **Net Reduction**: 809+ violations
- **Status**: ADG burndown gate passes
- **System Health**: Significantly improved

This systematic waterfall approach ensures predictable, measurable progress toward the ADG violation reduction goal.
