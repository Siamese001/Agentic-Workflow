# Layer Gravity Violations Fix

**Date:** 2026-03-24  
**Issue:** 817 layer gravity violations from L0-L6 importing L_RUNTIME  
**Root Cause:** `lifecycle_trace_contract` placed in L_RUNTIME layer  
**Impact:** Violates layer gravity rule (LN can only import from L0..LN)

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 🔍 Root Cause Analysis

### Current State:
```
L0 modules (817) ──import──> L_RUNTIME/lifecycle_trace_contract ❌
```

### Layer Gravity Rule:
```
LN can only import from L0..LN
L0 should NOT import from L_RUNTIME (higher layer)
```

### Violation Pattern:
- **817 modules** across L0-L6 import `agentic_core.runtime.lifecycle_trace_contract`
- **All violations** are the same: importing trace contract functions
- **Legitimate need** - all layers need to emit lifecycle traces

---

## 🛠️ Recommended Solution: Create L_CONTRACTS Layer

### New Architecture:
```
L_CONTRACTS (new)
├── lifecycle_trace_contract.py
├── policy_contracts.py  
├── interface_contracts.py
└── shared_contracts.py

L0-L6 modules ──import──> L_CONTRACTS/lifecycle_trace_contract ✅
L_RUNTIME modules ──import──> L_CONTRACTS/lifecycle_trace_contract ✅
```

### Benefits:
1. **Fixes layer gravity** - L_CONTRACTS is lower than all layers
2. **Maintains functionality** - all layers can still import contracts
3. **Architectural clarity** - contracts are explicitly shared interfaces
4. **Future-proof** - other cross-layer contracts can use same pattern

---

## 📋 Implementation Plan

### Phase 1: Create L_CONTRACTS Layer
1. Create `agentic_core/L_CONTRACTS/` directory
2. Move `lifecycle_trace_contract.py` to `L_CONTRACTS/`
3. Update layer assignments in ADG scanner
4. Add `L_CONTRACTS` to layer hierarchy

### Phase 2: Update Import Paths
1. Find all imports: `from agentic_core.runtime.lifecycle_trace_contract import`
2. Replace with: `from agentic_core.L_CONTRACTS.lifecycle_trace_contract import`
3. Update 817 files across all layers

### Phase 3: Validate Fix
1. Regenerate ADG
2. Verify 0 layer gravity violations
3. Run CI to ensure no regressions

---

## 🔧 Alternative Solutions (Rejected)

### Option 1: Move to L0
- ❌ L0 shouldn't contain runtime contracts
- ❌ Still violates layer gravity for L1-L6

### Option 2: Add Layer Gravity Gate to CI
- ❌ Would block current development
- ❌ Doesn't fix architectural issue

### Option 3: Ignore Violations
- ❌ Violates layer gravity principles
- ❌ Technical debt accumulation

---

## 🎯 Expected Outcome

### Before Fix:
- **817 layer gravity violations**
- **L0-L6 importing from higher layer**
- **Architecture principle violation**

### After Fix:
- **0 layer gravity violations**
- **All layers importing from L_CONTRACTS**
- **Clean layer hierarchy**

### Validation:
```bash
# Check violations are fixed
python -c "
import sqlite3
conn = sqlite3.connect('artifacts/adg/adg_indexed_*.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type=\"violates\"')
print(f'Violations: {cursor.fetchone()[0]}')
conn.close()
"
# Expected: 0
```

---

## 📊 Impact Assessment

### Files to Modify: ~817
### Risk: Low (import path changes only)
### Effort: Medium (mass file update)
### Benefit: High (fixes architectural violation)

---

## 🚀 Next Steps

1. **Create L_CONTRACTS layer structure**
2. **Move lifecycle_trace_contract**
3. **Update all import statements**  
4. **Regenerate ADG and validate**
5. **Update CI to check layer violations**

This fix will eliminate all 817 violations while maintaining functionality and improving architectural integrity.

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

