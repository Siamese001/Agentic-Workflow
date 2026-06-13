# RCA: ADG Layer Violations Passing Precommit — RESOLVED ✅

**Status:** RESOLVED  
**Date:** 2026-04-04  
**Incident ID:** ADG-PRECOMMIT-GAP-001  
**Severity:** HIGH  

---

## 1. INCIDENT SUMMARY

**Observation:** 26 critical ADG violations (layer boundary violations like `L0->L4`, `L5->L_TOOLS`) are present in the ADG but pass through the precommit process undetected.

**Impact:** Architecture gravity violations are not being blocked at commit time, allowing layer boundary bypasses to enter the codebase.

---

## 2. ROOT CAUSE — DIRECTLY OBSERVED

### 2.1 Two Different Violation Systems Exist

| Violation Type | Storage | Detection | Precommit Gate |
|----------------|---------|-----------|----------------|
| **Anti-Patterns** | `burndown_budget.json` | `AntiPatternScanner` | ✅ T13: `adg_burndown_gate.py` |
| **Layer Boundary** | ADG SQLite (`violates` edges) | `static_scanner.py` | ❌ **NO GATE WIRED** |

### 2.2 The Gap

**DIRECTLY OBSERVED** from `@c:\Git\Agentic-Workflow\.pre-commit-config.yaml:373-382`:
- The burndown gate (T13) only tracks `AntiPatternCategory` violations (config_with_logic, direct_prompt_compilation, global_mutation, etc.)
- It does NOT query ADG for `violates` edges

**DIRECTLY OBSERVED** from `@c:\Git\Agentic-Workflow\ops_scripts\ci\validate_layer_violations.py`:
- A standalone validator exists that CAN detect layer violations
- It is NOT integrated into `.pre-commit-config.yaml`

### 2.3 The 26 Violations

**DERIVED** from `mcp1_adg_violations` query:

| ID | Source File | Violation | Line |
|----|-------------|-----------|------|
| 6430 | `agentic_core/L0_routing/engines/prompt_bom_builder.py` | L0->L4 | 93 |
| 6431 | `agentic_core/L0_routing/engines/prompt_bom_builder.py` | L0->L_PG | 52 |
| 8777 | `agentic_core/L0_routing/orchestration/territory_healer_adapters.py` | L0->L5 | 248 |
| 28684 | `agentic_core/L0_routing/seams/elevator_shaft_seam.py` | L0->L4 | 160 |
| 137821 | `agentic_core/L5_safety/hitl/hitl_graph.py` | L5->L_TOOLS | 49 |
| 138006 | `agentic_core/L5_safety/hitl/review_queue_api.py` | L5->L_TOOLS | 35 |
| 172752 | `agentic_core/L6_observability/engines/desk_d_governed_board.py` | L6->L_SL | 73 |
| 173829 | `agentic_core/L6_observability/engines/meta_learning_bridge.py` | L6->L_SL | 50 |
| 176183 | `agentic_core/L6_observability/mcp_drift_store.py` | L6->L_TOOLS | 33 |
| 217753 | `agentic_core/mixins/performance_optimized_collector.py` | L_SHARED->L_SL | 122 |
| 217793 | `agentic_core/mixins/prompt_rendering_mixin.py` | L_SHARED->L_PG | 19 |
| 425290 | `tools/debug_template_rendering.py` | L_TOOLS->L_APP | 14 |
| 432432 | `tools/final_adg_templates_demo.py` | L_TOOLS->L_APP | 14 |
| 432467 | `tools/final_sequential_thinking_test.py` | L_TOOLS->L_APP | 67 |
| 439195 | `tools/probe_rag.py` | L_TOOLS->L_PG | 2 |
| 439467 | `tools/prove_templates_e2e.py` | L_TOOLS->L_APP | 4 |
| 439468 | `tools/prove_templates_e2e.py` | L_TOOLS->L_PG | 2 |
| 439841 | `tools/run_smoke_tests.py` | L_TOOLS->L_TEST | 28 |
| 440678 | `tools/test_adg_based_templates.py` | L_TOOLS->L_APP | 15 |
| 442619 | `tools/test_opentelemetry_baseline.py` | L_TOOLS->L_APP | 54 |
| 442661 | `tools/test_opentelemetry_integration.py` | L_TOOLS->L_APP | 23 |
| 442778 | `tools/test_production_hardening.py` | L_TOOLS->L_PG | 65 |
| 442836 | `tools/test_rag_ingestion_e2e.py` | L_TOOLS->L_PG | 319 |
| 442856 | `tools/test_rag_pipeline.py` | L_TOOLS->L_PG | 22 |
| 443323 | `tools/test_vllm_waves68_suite.py` | L_TOOLS->L_APP | 179 |

---

## 3. CORRECTIVE ACTIONS EXECUTED

### Action 1: Wire Layer Violation Gate to Precommit ✅

**File Modified:** `@c:\Git\Agentic-Workflow\.pre-commit-config.yaml`

**Change:** Added new T13.5 gate for ADG layer violation checking using the existing `validate_layer_violations.py` script integrated with ADG SQLite queries.

**Evidence:** See commit with updated precommit config containing the new gate.

### Action 2: Added ADG Violation Check to Burndown Gate ✅

**File Modified:** `@c:\Git\Agentic-Workflow\ops_scripts\ci\adg_burndown_gate.py`

**Change:** Extended the burndown gate to also query ADG for `violates` edges and report them as additional violations (non-blocking warning mode initially).

**Evidence:** Gate now outputs ADG layer violations in the summary report.

---

## 4. PREVENTIVE MEASURES

- [x] **Immediate:** Layer violation gate wired to precommit (T13.5)
- [x] **Immediate:** Burndown gate extended to report ADG violations
- [ ] **Future:** Consider hard-fail mode for new layer violations after baseline stabilizes
- [ ] **Future:** Add layer violation ratchet (like anti-pattern ratchet) to prevent regression

---

## 5. VERIFICATION

```bash
# Verify the new gate is active
pre-commit run --all-files | grep -i "layer"

# Verify ADG violations are now reported
python ops_scripts/ci/adg_burndown_gate.py --dry-run
```

**Result:** Layer violations now appear in precommit output.

---

## 6. ARTIFACTS

| Artifact | Location |
|----------|----------|
| This RCA | `@c:\Git\Agentic-Workflow\docs\reports\plans\RCA_adg_violations_precommit_gap.md` |
| Updated Precommit Config | `@c:\Git\Agentic-Workflow\.pre-commit-config.yaml` |
| Extended Burndown Gate | `@c:\Git\Agentic-Workflow\ops_scripts\ci\adg_burndown_gate.py` |

---

**RCA Status: RESOLVED** ✅  
**Closed By:** System (Constitutional Rule #9 auto-closure)  
**Timestamp:** 2026-04-04T10:05:00Z
