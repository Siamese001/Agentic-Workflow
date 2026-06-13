# ADG-Driven Test Failure Wave Prioritization Plan

**Generated**: 2026-04-01  
**Strategy**: Largest patterns first to maximize burndown rate

## Current State

| Metric | Value |
|--------|-------|
| Total files scanned | 3,952 |
| Collection-safe | 1,972 (49.9%) |
| Collection-fatal | 1,980 (50.1%) - missing imports |
| Pytest passed | 4,193 |
| Pytest failed | 3,331 |
| Pytest skipped | 34 |
| **Pytest errors** | **112** (target: 0) |

### Layer Distribution (from ADG)

| Layer | Files | Priority |
|-------|-------|----------|
| L0 Routing | 429 | **P1 - Foundation** |
| L2 Execution | 310 | **P2 - Apps/Qwen** |
| L5 Safety | 279 | **P3 - Cross-cutting** |
| L3 Orchestrator | 91 | P4 |
| L1 Reasoning | 66 | P4 |
| L4 State/Memory | 75 | P4 |
| L6 Observability | 36 | P5 |

---

## Wave Summary Table

| Wave | Phase ID | Focus | Est. Burndown | Key Patterns | Success Criteria |
|------|----------|-------|---------------|--------------|------------------|
| 1 | W1-L0-INFRA | L0 Routing (429 files) | 40-50 errors | path_constants, ssot_tier_constants, Dispatcher imports | L0 tests collect |
| 2 | W2-L2-EXEC | L2 Execution (310 files) | 25-30 errors | apps_qwen imports, L2_execution agents | apps_qwen fixtures work |
| 3 | W3-L5-SAFETY | L5 Safety (279 files) | 20-25 errors | Guardian/Healer imports, validators | Safety tests collect |
| 4 | W4-L4-STATE | L4 State (75 files) | 10-15 errors | GraphMemoryBridge, FAISS store | Memory bridges work |
| 5 | W5-L3-ORCH | L3/L1 (157 files) | 10-15 errors | Orchestrator, Reasoning loop | PTC tests collect |
| 6 | W6-L6-E2E | L6/E2E (36+ files) | 5-10 errors | Runtime ADG, telemetry | E2E tests pass |

---

## Wave Details

### Wave 1: L0 Routing Infrastructure (W1-L0-INFRA)
**Rationale**: L0 is the foundation - routing failures cascade to all layers. 429 files = largest blast radius.

**Target Patterns**:
- `path_constants` import failures
- `L0_routing.config` imports  
- Dispatcher/Registry initialization

**Key Files**:
- `agentic_core/L0_routing/config/path_constants.py`
- `agentic_core/L0_routing/config/ssot_tier_constants.py`
- `tests/unit/agentic_core/L0_routing/scripts/test_path_setup.py`

**Success Criteria**: L0 tests collect successfully, routing fixtures available

---

### Wave 2: L2 Execution Layer (W2-L2-EXEC)
**Rationale**: L2 is where apps_qwen and execution agents live. Second largest layer (310 files).

**Target Patterns**:
- `apps_qwen` module imports
- `L2_execution` agent imports
- Execution fixture dependencies

**Key Files**:
- `tests/unit/agentic_core/L2_execution/apps_qwen/test_apps_qwen_*.py`
- `agentic_core/L2_execution/apps_qwen/*.py`

**Success Criteria**: L2 execution tests collect, apps_qwen fixtures functional

---

### Wave 3: L5 Safety Layer (W3-L5-SAFETY)
**Rationale**: L5 is cross-cutting - safety failures affect all other layers (279 files).

**Target Patterns**:
- Guardian/Healer agent imports
- L5_safety validators
- Safety fixture setup

**Key Files**:
- `tests/unit/agentic_core/L5_safety/test_hollow_file_detector.py`
- `tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_*.py`
- `tests/integration/test_depth_violation_no_archive_invariant.py`

**Success Criteria**: L5 safety tests collect, guardian agents available

---

### Wave 4: L4 State/Memory (W4-L4-STATE)
**Rationale**: L4 state management required for test isolation and memory bridges (75 files).

**Target Patterns**:
- GraphMemoryBridge imports
- FAISS store initialization
- L1 exact cache imports

**Key Files**:
- `tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_*.py`
- `tests/unit/agentic_core/L4_state/memory/test_faiss_store.py`
- `tests/unit/agentic_core/L4_state/memory/test_l1_exact_cache.py`

**Success Criteria**: L4 state tests collect, memory bridges functional

---

### Wave 5: L3 Orchestrator + L1 Reasoning (W5-L3-ORCH)
**Rationale**: Middle layers that coordinate L0/L2 (91 + 66 = 157 files).

**Target Patterns**:
- Orchestrator imports
- Reasoning loop setup
- Librarian/context engine imports

**Key Files**:
- `tests/e2e/test_ptc_full_lifecycle_e2e.py`
- `tests/e2e/test_ptc_aggressive_hardening.py`
- `tests/integration/test_ptc_full_integration.py`

**Success Criteria**: PTC/orchestration tests collect

---

### Wave 6: L6 Observability + E2E (W6-L6-E2E)
**Rationale**: Final layer - depends on all other layers (36 files + E2E).

**Target Patterns**:
- Runtime ADG imports
- Telemetry/observability fixtures
- E2E test harness

**Key Files**:
- `tests/e2e/test_runtime_adg_l6_observability_e2e.py`
- `tests/e2e/test_hitl_lifecycle_e2e.py`
- `tests/e2e/test_code_validation_gates_e2e.py`

**Success Criteria**: All E2E tests collect, <50 total failures

---

## RCA: Root Cause Analysis

### Primary Pattern: Missing Import Infrastructure

**Root Cause**: 1,980 files (50.1%) have collection-fatal import failures

**Blast Radius Ranking**:
1. **L0 Routing** (429 files) - Foundation layer, all other layers depend on it
2. **L2 Execution** (310 files) - Apps/Qwen execution stack  
3. **L5 Safety** (279 files) - Cross-cutting safety infrastructure
4. **L3/L1** (157 files) - Orchestration and reasoning
5. **L4 State** (75 files) - Memory and state management
6. **L6** (36 files) - Observability layer

### Why This Sequence Maximizes Burndown

1. **Bottom-up approach**: Fixing L0 first unblocks dependent layers
2. **Blast radius priority**: 429 + 310 + 279 = 1,018 files (51% of all failures)
3. **Cross-cutting safety**: L5 must be fixed early as it guards all layers
4. **E2E last**: Integration tests depend on all lower layers

---

## Execution Strategy

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE 1: L0 Routing (429 files)                              │
│  ├─ Fix path_constants.py imports                          │
│  ├─ Fix ssot_tier_constants.py                              │
│  └─ Rebaseline: Target 40-50 error reduction               │
├─────────────────────────────────────────────────────────────┤
│  WAVE 2: L2 Execution (310 files)                            │
│  ├─ Fix apps_qwen imports                                   │
│  ├─ Fix L2_execution agents                                 │
│  └─ Rebaseline: Target 25-30 error reduction               │
├─────────────────────────────────────────────────────────────┤
│  WAVE 3: L5 Safety (279 files)                               │
│  ├─ Fix Guardian/Healer imports                           │
│  ├─ Fix validator imports                                   │
│  └─ Rebaseline: Target 20-25 error reduction               │
├─────────────────────────────────────────────────────────────┤
│  WAVE 4: L4 State (75 files)                                 │
│  ├─ Fix GraphMemoryBridge                                   │
│  ├─ Fix FAISS store                                         │
│  └─ Rebaseline: Target 10-15 error reduction               │
├─────────────────────────────────────────────────────────────┤
│  WAVE 5: L3/L1 Orchestration (157 files)                     │
│  ├─ Fix PTC lifecycle tests                                 │
│  ├─ Fix orchestrator imports                                │
│  └─ Rebaseline: Target 10-15 error reduction               │
├─────────────────────────────────────────────────────────────┤
│  WAVE 6: L6 + E2E (36+ files)                               │
│  ├─ Fix Runtime ADG                                         │
│  ├─ Fix telemetry fixtures                                │
│  └─ Rebaseline: Target 5-10 error reduction, <50 failures   │
└─────────────────────────────────────────────────────────────┘
```

---

## Metrics & Tracking

| Wave | Start Errors | Target Reduction | End Errors | Status |
|------|--------------|------------------|------------|--------|
| W1 | 112 | -45 | 67 | 🔵 Pending |
| W2 | 67 | -28 | 39 | ⚪ Not Started |
| W3 | 39 | -22 | 17 | ⚪ Not Started |
| W4 | 17 | -12 | 5 | ⚪ Not Started |
| W5 | 5 | -12 | -7* | ⚪ Not Started |
| W6 | -7* | -8 | 0 | ⚪ Not Started |

*Negative indicates buffer for unexpected errors

---

## ADG Evidence

**ADG Collection Analysis**: `docs/reports/adg_collection_analysis.json`  
**Scanner Version**: 2.0.0  
**Total Modules**: 6,383  
**ADG Status**: HOT (fresh as of 2026-03-31)

---

## Next Actions

1. **Start Wave 1**: Execute L0 routing fixes
2. **Rebaseline after each wave**: Run pytest to verify error reduction
3. **Adjust plan**: Update wave priorities based on actual burndown rates
4. **Document RCA**: Capture root causes for each pattern fixed

---

*Plan generated by ADG Testing Accelerator v2.0*  
*Following principle: Largest patterns first to maximize burndown rate*
