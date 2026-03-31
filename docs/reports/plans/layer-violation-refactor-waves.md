# Layer Boundary Violation Refactoring Plan
**Generated**: 2026-03-30  
**ADG Digest**: 36fd527e4c4a9c99  
**Total Violations**: 6 critical layer boundary violations  

## Executive Summary

Six critical layer boundary violations detected by ADG hot cache analysis. These violations break architectural gravity rules and must be fixed in dependency-ordered waves to prevent cascading failures.

## Violation Inventory (ADG-Sourced)

| Wave | Edge ID | Violation | File | Line | Severity |
|------|---------|-----------|------|------|----------|
| 1 | 17190 | L0→L2 | `agentic_core/L0_routing/scripts/error_handler.py` | 86 | HIGH |
| 1 | 21485 | L0→L2 | `agentic_core/L0_routing/scripts/forward_rolling_facade.py` | 22 | HIGH |
| 2 | 18587 | L0→L_SL | `agentic_core/L0_routing/scripts/execute_ssot.py` | 838 | HIGH |
| 3 | 141554 | L5→L_TOOLS | `agentic_core/L5_safety/hitl/review_queue_api.py` | 27 | MEDIUM |
| 4 | 204009 | L_TOOLS→L_RUNTIME | `agentic_core/adg/schema_util.py` | 25 | MEDIUM |
| 5 | 210369 | L_SHARED→L_TOOLS | `agentic_core/evaluation/golden/eval_spine_integration.py` | 13 | MEDIUM |

---

## Wave 1: L0→L2 Violations (Foundation → Execution)

**Target**: Fix 2 violations where L0 imports `get_clock` from L2_execution.providers

### Root Cause
```python
# error_handler.py:86 AND forward_rolling_facade.py:22
from agentic_core.L2_execution.providers import get_clock
```

L0 (routing/foundation) cannot depend on L2 (execution). The `get_clock` provider is an execution-level primitive that L0 needs for timestamps.

### Solution Strategy
**Move `get_clock` from L2_execution.providers to L_SHARED.providers**

#### Files to Modify
1. **Create**: `agentic_core/utils/providers.py` (new L_SHARED location)
   - Move `get_clock` function
   - Move `ClockProvider` class if exists
   - Add docstring explaining this is L_SHARED cross-cutting utility

2. **Update**: `agentic_core/L2_execution/providers.py`
   - Add deprecation shim: `from agentic_core.utils.providers import get_clock`
   - Add deprecation warning for 1 release cycle

3. **Update**: `agentic_core/L0_routing/scripts/error_handler.py`
   - Change import from `agentic_core.L2_execution.providers` to `agentic_core.utils.providers`

4. **Update**: `agentic_core/L0_routing/scripts/forward_rolling_facade.py`
   - Change import from `agentic_core.L2_execution.providers` to `agentic_core.utils.providers`

#### Acceptance Criteria
- [ ] `get_clock` exists in `agentic_core/utils/providers.py`
- [ ] L2 providers.py has backward-compatible shim
- [ ] Both L0 files import from L_SHARED
- [ ] ADG violations 17190 and 21485 resolved
- [ ] All tests pass
- [ ] Git commit: "Wave 1: Move get_clock to L_SHARED, fix L0→L2 violations"

---

## Wave 2: L0→L_SL Violation (Foundation → System Learning)

**Target**: Fix 1 violation where L0 imports from system_learning

### Root Cause
```python
# execute_ssot.py:838
from system_learning...  # (exact import TBD from line 838)
```

L0 (routing/foundation) importing L_SL (system_learning) violates gravity. System learning is a feedback loop layer that sits above the core.

### Solution Strategy
**Option A**: Lazy runtime import (if only used in specific execution paths)  
**Option B**: Move system_learning integration to L3 orchestration layer  
**Option C**: Use dependency injection pattern

#### Investigation Required
1. Read `execute_ssot.py:838` to identify exact import
2. Trace usage of system_learning symbols in execute_ssot.py
3. Determine if usage is critical path or optional enhancement
4. Choose strategy based on usage pattern

#### Files to Modify (TBD after investigation)
- `agentic_core/L0_routing/scripts/execute_ssot.py` — remove or lazy-load import

#### Acceptance Criteria
- [ ] Investigation complete, strategy chosen
- [ ] L0 no longer statically imports system_learning
- [ ] ADG violation 18587 resolved
- [ ] All tests pass
- [ ] Git commit: "Wave 2: Remove L0→L_SL import from execute_ssot.py"

---

## Wave 3: L5→L_TOOLS Violation (Safety → ADG Tooling)

**Target**: Fix 1 violation where L5 imports hitl_graph from adg.runtime

### Root Cause
```python
# review_queue_api.py:27
from agentic_core.adg.runtime.hitl_graph import (
    HITLDecisionType, HITLGraph, HITLRuntimeRecorder,
)
```

L5 (safety/governance) importing L_TOOLS (adg tooling) creates circularity risk. HITL is a safety concern, not a tooling concern.

### Solution Strategy
**Move `hitl_graph.py` from `agentic_core/adg/runtime/` to `agentic_core/L5_safety/hitl/`**

#### Files to Modify
1. **Move**: `agentic_core/adg/runtime/hitl_graph.py` → `agentic_core/L5_safety/hitl/hitl_graph.py`

2. **Create**: `agentic_core/adg/runtime/hitl_graph.py` (backward-compatible shim)
   ```python
   # Deprecated: moved to L5_safety.hitl
   from agentic_core.L5_safety.hitl.hitl_graph import *
   import warnings
   warnings.warn("hitl_graph moved to L5_safety.hitl", DeprecationWarning)
   ```

3. **Update**: `agentic_core/L5_safety/hitl/review_queue_api.py`
   - Change import to local: `from agentic_core.L5_safety.hitl.hitl_graph import ...`

4. **Search & Update**: All other files importing `agentic_core.adg.runtime.hitl_graph`
   - Use ADG to find all importers
   - Update to new location

#### Acceptance Criteria
- [ ] hitl_graph.py moved to L5_safety/hitl/
- [ ] Backward-compatible shim in place
- [ ] All importers updated
- [ ] ADG violation 141554 resolved
- [ ] All tests pass
- [ ] Git commit: "Wave 3: Move hitl_graph to L5_safety, fix L5→L_TOOLS violation"

---

## Wave 4: L_TOOLS→L_RUNTIME Violation (Tooling → Runtime)

**Target**: Fix 1 violation where schema_util.py imports from runtime

### Root Cause
```python
# schema_util.py:25
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through
```

L_TOOLS (adg/schema_util) importing L_RUNTIME creates cycle — runtime bootstrap imports tools concepts.

### Solution Strategy
**Remove the emitter import from schema_util.py**

The `_emit_reads_through` call in schema_util.py is likely for testing/instrumentation. Schema utilities should not emit runtime traces.

#### Files to Modify
1. **Update**: `agentic_core/adg/schema_util.py`
   - Remove line 25: `from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through`
   - Remove any calls to `_emit_reads_through()` in the file
   - If needed for tests, duplicate the constant or use a protocol

#### Acceptance Criteria
- [ ] schema_util.py no longer imports from runtime
- [ ] ADG violation 204009 resolved
- [ ] All tests pass (or tests updated if emitter was used)
- [ ] Git commit: "Wave 4: Remove L_TOOLS→L_RUNTIME import from schema_util.py"

---

## Wave 5: L_SHARED→L_TOOLS Violation (Shared → Tooling)

**Target**: Fix 1 violation where eval_spine_integration.py imports from adg.runtime

### Root Cause
```python
# eval_spine_integration.py:13
from agentic_core.adg.runtime.eval_spine import EvalSpine, EvalSpineReport
```

L_SHARED (evaluation/golden) importing L_TOOLS (adg runtime) — shared utilities should not depend on tooling.

### Solution Strategy
**Option A**: Move eval_spine to L_RUNTIME (if it's runtime infrastructure)  
**Option B**: Move eval_spine to L_SHARED (if it's cross-cutting evaluation)  
**Option C**: Use lazy import with TYPE_CHECKING only

#### Investigation Required
1. Determine if EvalSpine is runtime infrastructure or evaluation utility
2. Check if eval_spine has dependencies that would prevent moving to L_SHARED
3. Verify if eval_spine_integration.py is truly L_SHARED or should be in L_TOOLS

#### Files to Modify (TBD after investigation)
- Likely: Move `agentic_core/adg/runtime/eval_spine.py` to appropriate layer
- Update: `agentic_core/evaluation/golden/eval_spine_integration.py` import

#### Acceptance Criteria
- [ ] Investigation complete, strategy chosen
- [ ] eval_spine moved to appropriate layer OR lazy import implemented
- [ ] ADG violation 210369 resolved
- [ ] All tests pass
- [ ] Git commit: "Wave 5: Fix L_SHARED→L_TOOLS eval_spine import violation"

---

## Wave 6: Validation & Verification

**Target**: Confirm all violations resolved

### Validation Steps
1. **Regenerate ADG**: `python tools/adg/adg_redis_ingest.py --force`
2. **Query violations**: Use `mcp1_adg_violations` to verify count = 0 for `category: "violates"`
3. **Run layer validation**: `python ops_scripts/ci/validate_layer_violations.py agentic_core`
4. **Run full test suite**: Ensure no regressions
5. **Update documentation**: Update Import Flow.md if needed

#### Acceptance Criteria
- [ ] ADG shows 0 layer boundary violations
- [ ] validate_layer_violations.py passes
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Git commit: "Wave 6: Validation complete - all layer violations resolved"

---

## Git Workflow

After each wave:
```bash
# Stage changes
git add <modified_files>

# Commit with descriptive message
git commit -m "Wave N: <description>"

# Push to GitHub
git push origin main
```

---

## Rollback Strategy

If any wave fails:
1. **Immediate rollback**: `git reset --hard HEAD~1`
2. **Investigate failure**: Review test output, ADG violations
3. **Revise strategy**: Update this plan with lessons learned
4. **Retry wave**: Execute revised approach

---

## Dependencies & Prerequisites

- ADG hot cache must be fresh (run `adg_redis_ingest.py --force` before starting)
- All tests must pass before Wave 1
- No uncommitted changes in working directory
- Branch: `main` (or create feature branch `fix/layer-violations`)

---

## Success Metrics

- **Before**: 6 layer boundary violations (GV_violates=6)
- **After**: 0 layer boundary violations (GV_violates=0)
- **Test Coverage**: No regressions (all tests pass)
- **Commits**: 6 clean commits (1 per wave)
- **Documentation**: Import Flow.md updated with resolved violations

---

## Notes

- Wave order is dependency-driven: fix foundation violations first (L0), then work upward
- Each wave is atomic: can be rolled back independently
- Backward-compatible shims ensure no breaking changes for 1 release cycle
- ADG is source of truth for validation
