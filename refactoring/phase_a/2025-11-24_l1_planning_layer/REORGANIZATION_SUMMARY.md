# L1 Planning Layer Reorganization

## Summary of Changes

The L1 planning layer has been reorganized for clarity and consistency.

---

## What Changed

### Before (Confusing Structure)
```
├── l1.py                    # Workflow planning (WorkflowPlanBundle)
├── l1_planning/             # Agent planning (strategy, RAG, QA, safety)
│   ├── __init__.py
│   ├── strategy_planning.py
│   ├── rag_planning.py
│   ├── qa_planning.py
│   └── safety_planning.py
├── l2/                      # Tool execution protocols
│   └── __init__.py
└── core/
    └── l1.py                # Re-export wrapper
```

**Problems:**
- Two different "L1" concepts (workflow planning vs agent planning)
- `l1.py` file and `l1_planning/` folder both claim to be "L1"
- `l2/` package conflicted with `l2.py` module
- Confusing for developers and imports

### After (Clear Structure)
```
├── workflow_planning.py     # Workflow planning (WorkflowPlanBundle) - L0 layer
├── l1/                      # Agent planning (strategy, RAG, QA, safety) - L1 layer
│   ├── __init__.py
│   ├── strategy_planning.py
│   ├── rag_planning.py
│   ├── qa_planning.py
│   └── safety_planning.py
├── l2.py                    # Execution layer (no conflicts)
├── l2_tools/                # Tool execution protocols (renamed from l2/)
│   └── __init__.py
└── core/
    ├── l1.py                # Re-exports from l1/ package
    └── workflow_planning.py # Re-exports from workflow_planning.py
```

**Benefits:**
- Clear separation: `workflow_planning.py` (L0) vs `l1/` (L1)
- No naming conflicts
- Consistent with other layers (l2.py, l3.py, l4.py, l5.py)
- Easier to understand and maintain

---

## Layer Definitions

### L0: Workflow Planning (`workflow_planning.py`)
**Purpose:** Build the overall `WorkflowPlanBundle` that defines the high-level workflow structure.

**Key Function:**
- `build_workflow_plan_bundle()` - Creates strategy, RAG, drafting, QA, and safety plans

**Imports:**
```python
from workflow_planning import build_workflow_plan_bundle
# or
from core.workflow_planning import build_workflow_plan_bundle
```

### L1: Agent Planning (`l1/` package)
**Purpose:** Pure planning for individual agents (strategy, RAG, QA, safety).

**Key Functions:**
- `plan_strategy()` - Generate strategy execution plan
- `plan_draft()` - Generate drafting execution plan
- `plan_rag_reasoning()` - Generate RAG reasoning plan
- `plan_hyde_query()` - Generate HYDE query plan
- `plan_semantic_qa()` - Generate semantic QA plan
- `plan_council_review()` - Generate council review plan
- `plan_safety_review()` - Generate safety review plan

**Imports:**
```python
import l1
from l1 import plan_strategy, plan_draft
# or
from core import l1
```

### L2: Execution (`l2.py`)
**Purpose:** Execute the plans created by L1 (no reasoning, pure execution).

**Key Functions:**
- `run_l2()` - Main execution pipeline
- `execute_workflow_plans()` - Sync wrapper

**Imports:**
```python
import l2
from l2 import run_l2
# or
from core import l2
```

---

## Files Modified

### Renamed
1. `l1.py` → `workflow_planning.py`
2. `l1_planning/` → `l1/`
3. `l2/` → `l2_tools/` (already done in Phase A)

### Created
1. `core/workflow_planning.py` - Re-export wrapper for workflow planning

### Updated Imports
1. `tests/test_runtime_core_v10_10.py` - Updated to use `core.workflow_planning`
2. `tests/test_end_to_end_v10_10.py` - Updated to use `core.workflow_planning`

### Verified (No Changes)
1. `core/l1.py` - Already correctly re-exports from `l1/` package
2. All L1 planning modules - No changes needed
3. `cognitive_agents.py` - Already imports `l1` correctly
4. `l2.py` - Already imports `l1` correctly

---

## Verification

All Phase A tests still pass after reorganization:

```bash
python tests/test_l1_phase_a.py  # 9/9 PASSED ✅
python verify_phase_a.py         # 6/6 PASSED ✅
```

---

## Migration Guide

### If you were importing workflow planning:
```python
# OLD
from l1 import build_workflow_plan_bundle

# NEW
from workflow_planning import build_workflow_plan_bundle
# or
from core.workflow_planning import build_workflow_plan_bundle
```

### If you were importing agent planning:
```python
# OLD (if you were using l1_planning)
from l1_planning import plan_strategy

# NEW
from l1 import plan_strategy
# or
import l1
l1.plan_strategy(...)
```

### If you were importing from core:
```python
# Workflow planning
from core.workflow_planning import build_workflow_plan_bundle

# Agent planning
from core.l1 import plan_strategy, plan_draft
# or
from core import l1
```

---

## Why This Matters

### Before
- **Confusing:** Two different things both called "L1"
- **Error-prone:** Easy to import the wrong module
- **Inconsistent:** `l1.py` file vs `l1_planning/` folder

### After
- **Clear:** `workflow_planning.py` (L0) vs `l1/` (L1)
- **Consistent:** Follows pattern of `l2.py`, `l3.py`, `l4.py`, `l5.py`
- **Maintainable:** Easy to understand which layer does what

---

## Architecture Clarity

```
┌─────────────────────────────────────────────────────┐
│  L0: Workflow Planning (workflow_planning.py)      │
│  Builds WorkflowPlanBundle                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  L1: Agent Planning (l1/ package)                   │
│  Pure planning for strategy, RAG, QA, safety        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Cognitive Agents (cognitive_agents.py)             │
│  Call L1 planners, execute via L2                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  L2: Execution (l2.py)                              │
│  Pure execution, no reasoning                       │
└─────────────────────────────────────────────────────┘
```

---

## Conclusion

The reorganization provides:
- ✅ Clear separation between workflow planning (L0) and agent planning (L1)
- ✅ No naming conflicts
- ✅ Consistent with other layers
- ✅ All tests passing
- ✅ Backward compatibility via `core/` re-exports

**Status:** Complete and verified ✅
