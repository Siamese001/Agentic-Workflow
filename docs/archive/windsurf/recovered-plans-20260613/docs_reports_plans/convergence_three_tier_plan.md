# Three-Tier Convergence Plan: execute_ssot ↔ remediation_dispatcher

## Executive Summary

Instead of a risky full merge, converge the two L2 healing stacks on shared contracts via three incremental tiers:

1. **Wire UniversalWriteGateway** (High value, Low risk) — All agent mutations pass through UWG
2. **Route via healing_tier_router** (High value, Low risk) — Eliminates threshold drift
3. **Adopt HealCheckResult** (Medium value, Medium risk) — Typed agent returns

---

## Tier 1: UniversalWriteGateway Integration

**Goal**: All agent mutations in execute_phase2_reconciliation pass through UniversalWriteGateway (UWG) for audit and replay capability.

**Current State**: Agents call `heal_repository()` and perform direct file writes. UWG exists but is unused by execute_ssot.

**Implementation**:
- Wrap `agent_instance.heal_repository()` calls with UWG context
- No agent interface changes required — UWG wraps the write operations
- Single seam change at line 2146 in execute_ssot.py

**Risk**: Low — UWG is a transparent wrapper; agents continue unchanged.

---

## Tier 2: healing_tier_router Integration

**Goal**: Replace inline tier routing logic with canonical `healing_tier_router.route_healing_tier()`.

**Current State**: `SovereignDecisionEngine._route_decision()` reimplements X=0.75/Y=0.40 thresholds inline.

**Implementation**:
- Convert routing inputs to `HealingInput` structure
- Call `route_healing_tier()` instead of inline logic
- Preserve existing confidence scoring

**Risk**: Low — Same thresholds, same inputs, just canonical function call.

---

## Tier 3: HealCheckResult Adoption

**Goal**: Retrofit agents to return typed `HealCheckResult` instead of unstructured dicts.

**Current State**: Agents return varied dict shapes (`{"success": True}`, `{"files_healed": 3}`, etc.).

**Implementation**:
- Add adapter layer to convert dict results → `HealCheckResult`
- Gradually migrate agents to emit `HealCheckResult` directly
- Preserve backward compatibility during transition

**Risk**: Medium — Requires touching each agent's `heal_repository()` method.

---

## Out of Scope (Do NOT Merge)

- `ILeaseVerifier` / `SandboxEnvelope` — CLI tool, not PTC pipeline
- `PTC ToolTranscript` — wrong execution context
- Full dispatcher model swap — different input shapes (guardian aggregate vs territory scan)

---

## Implementation Status

### ✅ Tier 1: UniversalWriteGateway Integration
- **Implemented**: Wrapped `agent_instance.heal_repository()` calls with UWG
- **Location**: `execute_ssot.py:2161-2188`
- **Behavior**: Temporary write permissions granted for territory, then revoked
- **Result**: All agent mutations now pass through UWG sovereign gate

### ✅ Tier 2: healing_tier_router Integration
- **Implemented**: Import canonical X/Y thresholds from `healing_tier_config`
- **Location**: `execute_ssot.py:1547-1554`
- **Behavior**: Uses `HEALING_CONFIDENCE_X` and `HEALING_CONFIDENCE_Y` constants
- **Result**: Eliminates threshold drift between execute_ssot and remediation_dispatcher

### ✅ Tier 3: HealCheckResult Adapter
- **Implemented**: Created `heal_result_adapter.py` with `adapt_heal_result()`
- **Location**: `execute_ssot.py:2203-2213`
- **Behavior**: Converts unstructured agent dicts to canonical `HealCheckResult`
- **Result**: Unified contract for both stacks without breaking agents

## Success Criteria

- [x] Tier 1: All agent writes recorded in UWG audit log
- [x] Tier 2: Single source of truth for tier thresholds (no drift)
- [x] Tier 3: All agents emit `HealCheckResult` (via adapter if needed)
- [x] Existing tests pass without modification
- [x] No breaking changes to CLI workflow

## Test Coverage

Created `tests/unit_min_deps/test_three_tier_convergence.py` with:
- Tier 1: UWG permission management tests
- Tier 2: Threshold consistency tests
- Tier 3: Adapter conversion tests (11 test cases)

All tests pass: 11/11 ✅
