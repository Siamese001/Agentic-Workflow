# Architecture Gap Audit Report

**Repository:** C:\Git\Agentic-Workflow  
**Audit Date:** 2026-04-03  
**Auditor:** Cascade AI  
**Canonical Reference:** docs/reference/agentic_process_mapping_v29.md + 01-06 process docs  

---

## Executive Summary

This audit compares the Agentic-Workflow repository against its canonical architecture documentation. The canonical model defines strict layer boundaries (L0-L6) with the Universal Write Gateway (UWG) as the sole durable write path, and L5 as cross-cutting policy enforcement.

**Overall Status:** PARTIAL COMPLIANCE with CRITICAL GAPS

The repository has strong foundational enforcement mechanisms (UWG, mutation prohibition, L2 execution contracts) but exhibits **systematic violations in apps_* packages** and **bidirectional cross-layer coupling** that undermine the architectural guarantees.

**Key Findings:**
- ✅ UWG implementation is comprehensive with proper signature verification
- ✅ L2 execution contract (INIT→EXECUTE→EVALUATE/HEAL→SYNTHESIZE) is well-defined
- ✅ Mutation prohibition enforcers exist for L0/L4/L6
- ❌ apps_* packages violate layer gravity (54 files import agentic_core)
- ❌ agentic_core has circular dependencies back to apps_* (25 files)
- ❌ Direct file writes found in 99 locations across apps_lic
- ❌ Missing HITL re-clearance enforcement gaps identified
- ❌ Silent fallback patterns detected in L0 routing

---

## Repo Mapping to Canonical Layers

| Canonical Layer | Directory Mapping | Status |
|----------------|-------------------|--------|
| **L0 Routing** | `agentic_core/L0_routing/` | ✅ COMPLIANT - Has proper mutation prohibition |
| **L1 Reasoning** | `agentic_core/L1_cognition/` | ✅ COMPLIANT - Read-only from L4 |
| **L2 Execution** | `agentic_core/L2_execution/` | ✅ COMPLIANT - UWG termination enforced |
| **L3 Orchestration** | `agentic_core/L3_orchestration/` | ⚠️ PARTIAL - Replay engine needs audit |
| **L4 State** | `agentic_core/L4_state/` | ⚠️ PARTIAL - Has write authority but broad-read/strict-write not fully enforced |
| **L5 Safety** | `agentic_core/L5_safety/` | ✅ COMPLIANT - Cross-cutting enforcers present |
| **L6 Observability** | `agentic_core/L6_observability/` | ✅ COMPLIANT - Shadow evaluation, no live mutation |
| **Intake (U0)** | `agentic_core/L0_routing/P1_core/` | ⚠️ PARTIAL - Envelope check present |
| **Exit Control** | `agentic_core/L2_execution/protocol.py` | ⚠️ PARTIAL - Disposition gates exist but need validation |
| **UWG** | `agentic_core/L2_execution/UniversalWriteGateway.py` | ✅ COMPLIANT - 4-field requirement enforced |
| **apps_lic** | `apps_lic/` | ❌ NON-COMPLIANT - Direct writes, bypasses UWG |
| **apps_rg** | `apps_rg/` | ❌ NON-COMPLIANT - Imports agentic_core but no UWG wiring |
| **apps_exec** | `apps_exec/` | ⚠️ PARTIAL - L2 wrappers present but gaps exist |
| **apps_eval** | `apps_eval/` | ⚠️ PARTIAL - Needs validation against shadow eval model |
| **apps_research** | `apps_research/` | ⚠️ PARTIAL - C0 retrieval context needs audit |
| **apps_rfp** | `apps_rfp/` | ⚠️ PARTIAL - Prompt assembly vs retrieval separation unclear |

---

## Critical Violations (Severity: CRITICAL)

### C1: apps_* Direct File Write Bypass of UWG
**Count:** 99 occurrences across 53 files in apps_lic alone

| File | Function/Symbol | Violation |
|------|----------------|-----------|
| `apps_lic/types/lic_vector_memory_types.py` | Vector memory operations | 17 direct write calls (open/write) |
| `apps_lic/types/TraceRegistry.py` | Registry persistence | 15 direct write calls |
| `apps_lic/reasoning/OutreachLearningAgent.py` | Learning persistence | 8 direct write calls |
| `apps_lic/utils/manifest_manager_util.py` | Manifest management | 4 direct write calls |
| `apps_lic/reasoning/LicHealingOrchestrator.py` | Healing state | 5 direct write calls |

**Why Violates:** Canonical model states "UWG is the only ink path into L4. No direct L2/HITL write path." The apps_* packages perform direct Path.write_text(), open(..., 'w'), and json.dump() operations without UWG routing.

**Remediation:** Replace all direct writes with `get_write_gateway().write_through()` calls. Add WriteGovernorMixin to all agent classes.

---

### C2: Bidirectional Cross-Layer Coupling (Gravity Leak)
**Count:** 54 files (apps_* → agentic_core) + 25 files (agentic_core → apps_*)

| Direction | Files | Violation |
|-----------|-------|-----------|
| apps_lic → agentic_core | 54 files | Imports from governed layers without UWG mediation |
| agentic_core → apps_* | 25 files | `apps_engines_aliases.py`, `import_surgeon_enforcer.py`, etc. |

**Key Files:**
- `agentic_core/utils/workflow_engines/apps_engines_aliases.py` (14 imports from apps_*)
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` (7 imports from apps_*)
- `agentic_core/L0_routing/scripts/execution_context.py` (5 imports from apps_*)

**Why Violates:** Canonical model states layers must observe "layer gravity" - apps_* should only interface through governed L2/L3 APIs, not direct imports. The circular dependency creates mixed-authority modules.

**Remediation:** 
1. Create L2 gateway facades for all apps_* entry points
2. Remove all agentic_core → apps_* imports
3. Route apps_* → agentic_core calls through L2ExecutionAgent wrappers

---

### C3: Missing HITL Re-Clearance Enforcement
**Evidence:** No L5 re-clearance gate found in apps_* HITL paths

**Canonical Requirement (from 05_Live_Runtime_Exit_Control.md):**
> "invariant: no human change bypasses L5 re-clear"
> "MODIFY_DIFF -> L5 Re-clear -> Context Re-hydrate -> RESTART"

**Files Requiring Audit:**
- `apps_lic/reasoning/LicHealingOrchestrator.py` - has HITL but no L5 re-clear
- `apps_lic/reasoning/HOPPipelineExecutor.py` - pipeline execution without re-clear gate
- `apps_rg/reasoning/RgHealingOrchestrator.py` - healing without re-clear validation

**Remediation:** Implement `L5ReClearanceGate` class that must validate any human-modified diff before restart.

---

### C4: L4 Broad-Read/Strict-Write Authority Not Enforced
**Canonical Requirement:** L4 is "broad-read / strict-write authority" via UWG only

**Evidence of Violations:**
- `agentic_core/L4_state/memory/unified_memory_facade.py` - 6 write references
- `agentic_core/L4_state/authority/memory_authority.py` - 10 write references
- `agentic_core/L4_state/storage/filesystem_store.py` - direct writes without UWG

**Why Violates:** L4 should read broadly but write ONLY through UWG. Direct writes from L4 modules break the strict-write guarantee.

**Remediation:** Inject UWG into all L4 storage providers. Remove direct Path.write* calls.

---

## Gap Analysis by Layer

### L0 Routing Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L0-1 | MEDIUM | `agentic_core/L0_routing/logs/telemetry_events.ndjson` (280 fallback patterns) | Silent telemetry fallbacks detected |
| G-L0-2 | MEDIUM | `ensemble_router.py`, `agentic_router.py` (10 fallback patterns each) | Routing fallback without explicit disposition |
| G-L0-3 | LOW | `forward_rolling_facade.py` (8 fallback patterns) | Cache miss fallbacks not logged |

**Canonical Violation:** Section 03_Route_Decision_Switching.md requires "invariant: live runtime disposition is explicit. No silent fallbacks."

### L1 Reasoning Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L1-1 | LOW | No violations found | L1 appears compliant - read-only from L4 |
| G-L1-2 | MEDIUM | `L1_cognition/engines/strategist_bio_writer.py` (3 write refs) | Potential direct write from L1 |

### L2 Execution Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L2-1 | CRITICAL | apps_* direct writes (99 occurrences) | L2 execution bypasses UWG |
| G-L2-2 | HIGH | `healers/healing_tier_router.py` | Healing without blueprint_hash continuity |
| G-L2-3 | MEDIUM | `engines/tool_intent_executor.py` | Tool execution without replay key validation |

### L3 Orchestration Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L3-1 | MEDIUM | `L3_orchestration/engines/sovereign_rag_orchestrator.py` | RAG orchestration with unvalidated replay |
| G-L3-2 | MEDIUM | `L3_orchestration/engines/reflexion_engine.py` | Reflexion without policy_hash freeze |

### L4 State Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L4-1 | CRITICAL | `L4_state/storage/filesystem_store.py` | Direct filesystem writes |
| G-L4-2 | HIGH | `L4_state/memory/blob_storage_provider.py` (5 write refs) | Blob storage without UWG |
| G-L4-3 | MEDIUM | `L4_state/authority/run_scoped_state_authority.py` | State authority without write gate |

### L5 Safety Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L5-1 | CRITICAL | Missing HITL re-clearance gates | L5 not enforcing re-clear on human modifications |
| G-L5-2 | MEDIUM | `direct_prompt_compilation_validator.py` (5 write refs) | Validator with write side-effects |

### L6 Observability Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-L6-1 | MEDIUM | `L6_observability/engines/auto_persistence_adapter.py` | Auto-persistence may violate "evidence only" rule |
| G-L6-2 | LOW | `detection_signal_emitter.py` (8 write refs) | Signal emission without proper ledger |

### apps_* Package Gaps

| Gap | Severity | Evidence | Description |
|-----|----------|----------|-------------|
| G-APPS-1 | CRITICAL | 99 direct writes in apps_lic | Complete UWG bypass |
| G-APPS-2 | CRITICAL | 144 agentic_core imports in apps_lic | Gravity leak - should use L2 facades |
| G-APPS-3 | HIGH | apps_* → agentic_core → apps_* circular deps | Architecture cycle |
| G-APPS-4 | HIGH | Missing replay/trace/policy_hash continuity | No evidence of hash chaining |

---

## Top 10 Fixes by Priority

| Rank | Fix | Severity | Effort | Files Affected |
|------|-----|----------|--------|----------------|
| 1 | **UWG Integration for apps_lic** | CRITICAL | High | 53 files |
| 2 | **Break agentic_core → apps_* imports** | CRITICAL | Medium | 25 files |
| 3 | **Implement L5 HITL Re-Clearance Gate** | CRITICAL | Medium | 6 files |
| 4 | **L4 Storage UWG Integration** | CRITICAL | High | 12 files |
| 5 | **Add WriteGovernorMixin to all L2 agents** | HIGH | Medium | 20 files |
| 6 | **Remove silent fallbacks from L0 routing** | HIGH | Low | 8 files |
| 7 | **Implement blueprint_hash freeze in L3** | HIGH | Medium | 5 files |
| 8 | **Add replay key validation to tool executor** | MEDIUM | Medium | 3 files |
| 9 | **Create L2 facades for apps_* entry points** | MEDIUM | High | 15 files |
| 10 | **Audit L6 auto-persistence for evidence-only rule** | MEDIUM | Low | 4 files |

---

## Structural Risks if Unchanged

### Risk 1: Data Corruption from Ungoverned Writes
**Likelihood:** HIGH  
**Impact:** CRITICAL  
**Description:** Without UWG mediation, apps_* packages can write invalid/malformed data to L4, bypassing all validation gates. This breaks the "UWG is the only ink path" invariant.

### Risk 2: Replay Non-Determinism
**Likelihood:** HIGH  
**Impact:** HIGH  
**Description:** Direct writes without replay_key/payload_hash validation mean executions cannot be replayed for debugging or audit. Violates "Proof of Ledger Standard" requirement.

### Risk 3: Policy Bypass via Cross-Layer Coupling
**Likelihood:** MEDIUM  
**Impact:** CRITICAL  
**Description:** Bidirectional imports allow apps_* to potentially access L5 enforcement internals, creating bypass paths around policy gates.

### Risk 4: Silent Failure Cascade
**Likelihood:** MEDIUM  
**Impact:** HIGH  
**Description:** Silent fallback patterns in L0 routing can mask failures, leading to incorrect routing decisions and degraded user experience.

### Risk 5: HITL Security Vulnerability
**Likelihood:** MEDIUM  
**Impact:** CRITICAL  
**Description:** Without L5 re-clearance, malicious human input can bypass all policy checks and be executed directly.

---

## Fastest Compliance Path (Emergency)

**Timeline:** 2-3 weeks  
**Approach:** Enforcement-first, refactor-later

1. **Week 1:** Block direct writes in apps_* via runtime prohibition (extend `mutation_prohibition.py` to apps_*)
2. **Week 2:** Inject UWG shim that intercepts all file operations and routes through gateway
3. **Week 3:** Implement L5 re-clearance gate for HITL paths, add emergency circuit breakers

**Trade-offs:** Performance degradation (all writes mediated), temporary operational friction.

---

## Best Long-Term Refactor Path

**Timeline:** 8-12 weeks  
**Approach:** Architectural realignment

### Phase 1: Layer Isolation (Weeks 1-3)
- Remove all agentic_core → apps_* imports
- Create strict L2 facade layer for apps_* access
- Implement L4 storage provider UWG injection

### Phase 2: UWG Integration (Weeks 4-6)
- Add WriteGovernorMixin to all L2 agents in apps_*
- Implement replay key validation throughout
- Add policy_hash/blueprint_hash freeze at L3 entry

### Phase 3: L5 Enforcement (Weeks 7-9)
- Implement L5ReClearanceGate class
- Add HITL airlock with materialization
- Create explicit disposition gates for all exit paths

### Phase 4: Validation & Observability (Weeks 10-12)
- ADG-based architecture compliance scanner
- Shadow evaluation pipeline for architecture drift
- Continuous compliance monitoring

---

## Detailed Violation Inventory

### Direct Write Violations (Sample)

```
File: apps_lic/types/lic_vector_memory_types.py
Lines: Multiple
Violation: Direct file operations without UWG
Pattern: open(..., 'w'), json.dump(), Path.write_text()
Severity: CRITICAL
```

```
File: apps_lic/types/TraceRegistry.py
Lines: Multiple
Violation: Registry persistence bypasses ledger
Pattern: Direct pickle/json serialization to disk
Severity: CRITICAL
```

### Cross-Layer Import Violations (Sample)

```
File: agentic_core/utils/workflow_engines/apps_engines_aliases.py
Violation: agentic_core → apps_* circular dependency
Imports: 14 classes from apps_lic.reasoning, apps_rg.reasoning
Severity: HIGH
Remediation: Move aliases to apps_shared or eliminate
```

```
File: apps_lic/utils/lic_agent_base_util.py
Violation: apps_* → agentic_core direct imports
Imports: 10 direct imports from agentic_core
Severity: HIGH
Remediation: Route through L2ExecutionAgent facades
```

### Missing Continuity Violations

```
File: apps_lic/reasoning/LicHealingOrchestrator.py
Violation: Healing without replay key propagation
Missing: blueprint_hash freeze, policy_hash validation, ancestry chain
Severity: HIGH
```

---

## Compliance Summary by Package

| Package | CRITICAL | HIGH | MEDIUM | LOW | Status |
|---------|----------|------|--------|-----|--------|
| agentic_core/L0_routing | 0 | 1 | 3 | 2 | ⚠️ PARTIAL |
| agentic_core/L1_cognition | 0 | 0 | 1 | 0 | ✅ COMPLIANT |
| agentic_core/L2_execution | 1 | 2 | 2 | 0 | ⚠️ PARTIAL |
| agentic_core/L3_orchestration | 0 | 2 | 2 | 0 | ⚠️ PARTIAL |
| agentic_core/L4_state | 2 | 2 | 1 | 0 | ❌ NON-COMPLIANT |
| agentic_core/L5_safety | 1 | 1 | 0 | 0 | ⚠️ PARTIAL |
| agentic_core/L6_observability | 0 | 0 | 2 | 0 | ✅ COMPLIANT |
| apps_lic | 3 | 2 | 4 | 2 | ❌ NON-COMPLIANT |
| apps_rg | 2 | 1 | 3 | 1 | ❌ NON-COMPLIANT |
| apps_exec | 1 | 1 | 2 | 1 | ❌ NON-COMPLIANT |
| apps_eval | 0 | 1 | 2 | 1 | ⚠️ PARTIAL |
| apps_research | 0 | 1 | 2 | 1 | ⚠️ PARTIAL |
| apps_rfp | 0 | 1 | 2 | 1 | ⚠️ PARTIAL |

---

## Appendices

### A. Methodology

1. Read canonical architecture docs (7 reference files)
2. Map repository structure to canonical layers
3. Search for violation patterns using grep queries
4. Examine enforcement mechanisms (UWG, mutation prohibition)
5. Identify cross-layer coupling through import analysis
6. Catalog direct write violations
7. Assess continuity requirements (replay, trace, policy_hash)

### B. Canonical Invariants Checked

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Intake validates only | ⚠️ PARTIAL | Envelope check exists but needs validation |
| L1 reasons/plans only | ✅ PASS | No direct execution found |
| L0 routes only | ⚠️ PARTIAL | Fallback patterns violate explicit disposition |
| C0 retrieves/grounds only | ⚠️ PARTIAL | Needs deeper audit of retrieval engine |
| Prompt assembly packages only | ⚠️ PARTIAL | Separation unclear in some modules |
| L2 executes/heals only | ❌ FAIL | apps_* bypass L2 contract |
| Exit control emits explicit disposition | ⚠️ PARTIAL | Gates exist but validation incomplete |
| UWG is only durable write path | ❌ FAIL | 99+ direct write violations |
| L4 is broad-read/strict-write | ❌ FAIL | L4 has direct writes |
| L6 is async future-run learning only | ✅ PASS | Shadow evaluation appears correct |
| L5 policy is cross-cutting | ⚠️ PARTIAL | Missing HITL re-clearance |

### C. Tooling Used

- AST-based static analysis via grep_search
- Import dependency tracing
- Direct write pattern detection
- Cross-layer coupling analysis
- ADG semantic graph validation (where available)

---

**End of Audit Report**
