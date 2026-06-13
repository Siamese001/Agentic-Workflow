# Guardian Test Expansion — AST-Driven Plan
**Repository:** `c:\Git\Agentic-Workflow`
**Scope:** L5 safety plane + `agent_registry` + `SovereignLLMGateway`
**Analysis basis:** AST import graph over 3,162 Python files (scanned 2025)
**Evidence file:** `artifacts/_guardian_adg_result.json`

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


## 1. Recommendation Summary

Guardian is the highest fan-out enforcement layer in the repository.
A naive file-by-file test expansion would create redundant, low-signal coverage.
The AST dependency graph reveals that **two modules alone (`sovereign_kernel`, `structure_blueprint_pkg`) are transitively consumed by 102–105 files**, yet their behavioral enforcement contracts (boundary validation, immutability guarantees, fail-closed semantics) have **zero direct unit tests**.

The graph-driven insight is:
> Test the seam, not the consumer. Every high fan-in Guardian node should have
> a small, deterministic behavioral test that asserts the contract it publishes —
> then each consumer can be protected by a single transitive proof test rather
> than a deep fixture per consumer.

**Deliverables produced by this session:**

| File | Status |
|---|---|
| `tests/guardian/test_classification_kernel_hardened.py` | ✅ Created |
| `tests/guardian/test_agent_registry_hardened.py` | ✅ Created |
| `tests/guardian/test_structure_blueprint_hardened.py` | ✅ Created |
| `tests/guardian/test_sovereign_llm_gateway_hardened.py` | ✅ Created |
| `artifacts/_guardian_adg_result.json` | ✅ Created (raw graph data) |

---

## 2. AST Dependency Maps

### 2A. Import Dependency Graph (fan-in / fan-out)

Scanned 3,162 Python files across `agentic_core`, `apps_*`, `tests`, `ops_scripts`, `tools`, `system_learning`.

| Guardian Component | Path | fan_in | fan_out (to guard. targets) | test_cov files |
|---|---|---|---|---|
| `sovereign_kernel` | `L5_safety/config/structure_blueprint/sovereign_kernel.py` | **105** | 0 | 17 |
| `structure_blueprint_pkg` | `L5_safety/config/structure_blueprint/__init__.py` | **102** | 0 | 16 |
| `base_detector_validator` | `L5_safety/validators/base_detector_validator.py` | 11 | 0 | 4 |
| `agent_registry` | `agentic_core/agents/agent_registry.py` | 10 | 0 | **1** |
| `classification_kernel` | `L5_safety/core_kernel/classification_kernel.py` | 10 | 0 | **2** |
| `SovereignLLMGateway` | `L2_execution/enforcement/SovereignLLMGateway.py` | 9 | 1 | 3 |
| `type_erasure_validator` | `L5_safety/validators/type_erasure_validator.py` | 8 | 0 | 2 |
| `registry_verification_enforcer` | `L5_safety/enforcement/registry_verification_enforcer.py` | 7 | 0 | 3 |
| `gravity_validator` | `L5_safety/validators/gravity_validator.py` | 6 | 0 | **1** |
| `dependencygraph_validator` | `L5_safety/validators/dependencygraph_validator.py` | 6 | 0 | **1** |
| `layer_sovereignty_enforcer` | `L5_safety/enforcement/layer_sovereignty_enforcer.py` | 3 | 0 | 2 |
| `structure_blueprint_config` | `L5_safety/config/structure_blueprint_config.py` | 2 | 0 | 1 |
| `ssot_guardrail` | `L5_safety/enforcement/ssot_guardrail.py` | 2 | 0 | 1 |

> **fan_out (within guardian set):** `SovereignLLMGateway` → `agent_registry` (the only intra-guardian dependency found).

### 2B. Inheritance Graph

| Component | Key Classes | Inheritance |
|---|---|---|
| `SovereignLLMGateway` | `SovereigntyViolation` | `Exception` |
| `SovereignLLMGateway` | `SovereignLLMGateway` | (singleton, no base) |
| `base_detector_validator` | `AntiPatternDetector` | `ABC` |
| `base_detector_validator` | `EnforcementLevel`, `AntiPatternCategory` | `str, Enum` |
| `type_erasure_validator` | `TypeErasureDetector` | `AntiPatternDetector` |
| `layer_sovereignty_enforcer` | `LayerSovereigntyEnforcer` | (no base) |
| `registry_verification_enforcer` | `RegistryVerifier` | (no base) |
| `gravity_validator` | `UnifiedSSOTValidator` | (no base) |

### 2C. Decorator Usage Graph

| Component | Decorators |
|---|---|
| `classification_kernel` | `lru_cache`, `contextmanager` |
| `SovereignLLMGateway` | `dataclass`, `classmethod`, `property` |
| `layer_sovereignty_enforcer` | `dataclass`, `staticmethod`, `property` |
| `base_detector_validator` | `dataclass`, `abstractmethod`, `property` |
| `type_erasure_validator` | `property` |
| `gravity_validator` | `dataclass`, `property` |
| `dependencygraph_validator` | `dataclass`, `wraps`, `property` |

### 2D. Test-to-Source Coverage Graph (current state)

| Guardian Node | Current Test Files |
|---|---|
| `classification_kernel` | `tests.unit…test_execution_mode`, `tests.unit…test_phase1_enforcer_seam` |
| `structure_blueprint_pkg` / `sovereign_kernel` | 16–17 files (all indirect — path constants, phantom dirs) |
| `agent_registry` | `tests.unit…test_commit_proof_invariant` (import-only) |
| `SovereignLLMGateway` | `tests.governance.test_generation_routing_enforcement`, `test_sovereignty_attack_suite`, `test_req414_egress_guard` |
| `layer_sovereignty_enforcer` | `tests.governance.test_layer_sovereignty_enforcer`, `test_stabilization_hardening_s1_s5` |
| `registry_verification_enforcer` | `tests.governance.test_ssot_structure_validation_enforcer`, `test_stabilization_hardening_s1_s5`, `tests.unit…test_registry_verification` |
| `base_detector_validator` | 4 guardian test files |
| `gravity_validator` | `test_path_setup` (import probe only) |
| `dependencygraph_validator` | `test_path_setup` (import probe only) |

---

## 3. Criticality Ranking

### Tier 0 — Hard-Stop Security/Governance Chokepoints

| Rank | Component | Justification |
|---|---|---|
| T0-1 | `sovereign_kernel` | fan_in=105; compile-time governance root; declaring what IS and IS NOT a kernel component; if `validate_boundary()` regresses, all 105 consumers silently receive wrong answers |
| T0-2 | `structure_blueprint_pkg` | fan_in=102; CI placement validators, phantom-dir tests, all depth checks — all read SOVEREIGN_TERRITORIES from this package |
| T0-3 | `SovereignLLMGateway` | Sole LLM choke point; enforces agent_id, model allowlist, DETERMINISTIC-mode block; fan_in=9; any bypass is a security regression |
| T0-4 | `classification_kernel` | fan_in=10; SSOT for file-type classification across L0–L6, runtime, ops_scripts; `lru_cache` makes error paths invisible unless directly tested |
| T0-5 | `agent_registry` | Compile-time agent allowlist; `get_profile()` is the authorization gate for every LLM call; fan_in=10; test_cov=1 (import only) |

### Tier 1 — Structural Correctness and Routing Dependencies

| Rank | Component | Justification |
|---|---|---|
| T1-1 | `base_detector_validator` | fan_in=11; ABC for all anti-pattern detectors; if abstract interface regresses, all concrete detectors silently break |
| T1-2 | `registry_verification_enforcer` | fan_in=7; scans filesystem vs registry; orphan/missing detection is a deployment correctness gate |
| T1-3 | `type_erasure_validator` | fan_in=8; inherits from `base_detector_validator`; type erasure detection is a critical governance check |
| T1-4 | `layer_sovereignty_enforcer` | fan_in=3; AST-based L0–L6 import hierarchy enforcement; directly consulted by CI |
| T1-5 | `gravity_validator` | fan_in=6; unified SSOT validator; test_cov=1 (import probe only) — severe gap |

### Tier 2 — Convenience / Reporting Utilities

| Rank | Component | Justification |
|---|---|---|
| T2-1 | `structure_blueprint_config` | fan_in=2; re-export shim only; low behavioral risk but backward-compat surface must not diverge from package |
| T2-2 | `ssot_guardrail` | fan_in=2; enforcement utility; low fan-in, low blast radius |
| T2-3 | `dependencygraph_validator` | fan_in=6; test_cov=1 — gap, but validator is internal to ops tooling |

---

## 4. Test Gap Analysis

### T0-1/T0-2: `sovereign_kernel` + `structure_blueprint_pkg`

**Current tests:** 17/16 files that _import_ these modules for path constants.

**Missing behavioral tests:**
- `is_kernel_component()` prefix-match semantics (exact vs. sub-module vs. partial overlap)
- `is_modular_extension()` prefix-match semantics
- `validate_boundary()` return contract: `(True, "kernel_component:…")`, `(True, "modular_extension:…")`, `(False, "unclassified_module:…")`
- **Fail-closed**: unclassified path returns `False`, not `True`
- Path normalization: forward-slash, backslash, mixed-slash all resolve correctly
- `SOVEREIGN_KERNEL_COMPONENTS` is a `frozenset` (immutable) — mutation attempt raises
- `MODULAR_EXTENSIONS` is a `frozenset` — no overlap with kernel
- `SovereignLLMGateway` declared as kernel component (critical choke point declared)
- `agent_registry` declared as kernel component
- `structure_blueprint_config` shim `__all__` mirrors package `__all__` exactly

**Missing failure-path tests:**
- Empty string passed to `validate_boundary()` → `False`
- Module with partial prefix overlap (e.g., `agentic_core.L5_safety_extra`) → `False`

**Missing transitive tests:**
- Shim backward-compat surface: all 163 names accessible via `from structure_blueprint_config import X`

**→ New file:** `tests/guardian/test_structure_blueprint_hardened.py` (44 tests)

---

### T0-3: `SovereignLLMGateway`

**Current tests (3 files):**
- `test_generation_routing_enforcement`: topology (exists, has `generate`, has `operation_stats`), AST file scanner subprocess tests
- `test_sovereignty_attack_suite`: import-only assertions
- `test_req414_egress_guard`: structure checks

**Missing behavioral tests:**
- `route_generation()` with `agent_id=""` → `SovereigntyViolation("agent_id is required")`
- `route_generation()` with unregistered agent → `SovereigntyViolation("not found in registry")`
- `route_generation()` with DETERMINISTIC agent → `SovereigntyViolation("DETERMINISTIC and cannot call")`
- `route_generation()` with LLM_API agent + disallowed model → `SovereigntyViolation("not in allowed_models")`
- `_audit()` appends entry with `provider`, `model`, `success`, `latency_ms`, `ts`
- `_audit()` FIFO rotation: oldest entries pruned when `max_audit_log_size` exceeded
- `_egress_audit_log.entries` appended before provider dispatch (egress audit order)
- `_injection_detector.scan()` called before `_call_provider()`
- Provider degraded after 5 consecutive failures
- Provider exits degraded mode after timeout
- All providers failed → `SovereigntyViolation("All LLM providers failed")`
- Fallback increments `operation_stats["fallbacks"]`
- Replay envelope contains `agent_id`, `model`; deterministic for same request
- `reset_instance()` clears singleton state for clean test isolation

**Missing failure-path tests:**
- None of the existing tests assert that rejection **raises rather than returns a result**

**→ New file:** `tests/guardian/test_sovereign_llm_gateway_hardened.py` (38 tests)

---

### T0-4: `classification_kernel`

**Current tests (2 files):**
- `test_execution_mode.py`: exhaustive coverage of `classify_execution_mode()` signals ✅
- `test_phase1_enforcer_seam.py`: import probe

**Missing behavioral tests:**
- `classify_file_standalone()` has **zero direct unit tests**
- Full FileType taxonomy coverage (AGENT, MIXIN, STRATEGY, ENFORCER, VALIDATOR, CONFIG, SCRIPT, UTILITY, ORCHESTRATOR, EXCEPTION, STUB, ADAPTER, TEST, IGNORE)
- Priority ordering: IGNORE > STUB > TEST > EXCEPTION > MIXIN > AGENT (first-match-wins)
- `lru_cache` semantics: hits increment on second call, `currsize==0` after `clear_classification_cache()`
- `classification_cache_context()`: clears on entry AND on exit (even on exception)
- `get_classification_conflicts()`: returns copy, not reference
- `clear_classification_conflicts()` resets state
- `CONFIG_WITH_LOGIC` conflict recording
- Error hardening: `UnicodeDecodeError`, `OSError`, `SyntaxError`, zero-byte file → IGNORE
- `is_agent_file()` predicate consistent with `classify_file_standalone()`
- `is_agent_or_orchestrator()` returns `True` for both AGENT and ORCHESTRATOR
- Consumer regression guard: canonical classification stable after cache clear

**→ New file:** `tests/guardian/test_classification_kernel_hardened.py` (48 tests)

---

### T0-5: `agent_registry`

**Current tests (1 file):**
- `test_commit_proof_invariant`: imports `AGENT_REGISTRY`, asserts it's a dict with `>0` entries

**Missing behavioral tests:**
- `get_profile("__nonexistent__")` raises `KeyError` (not silent `None`)
- `KeyError` message contains `"not found in registry"` and `"Available"` list
- `get_execution_profile()` delegates to `get_profile()` — same hard fail
- Empty string and whitespace `agent_id` raise `KeyError`
- `AGENT_REGISTRY` keys match `profile.agent_id` for every entry
- All DETERMINISTIC agents have `allowed_models == ()`
- All LLM_API agents have `len(allowed_models) > 0`
- `registry_digest()` is deterministic across repeated calls
- `registry_digest()` format: colon-delimited 3-part string `agent_id:intensity:mode`
- Transitive: `SovereignLLMGateway` raises `SovereigntyViolation` for unregistered agent
- Transitive: DETERMINISTIC agent blocked with message containing agent name
- Transitive: LLM_API agent with disallowed model blocked with model name in message
- Transitive: rejection raises, not returns `None`

**→ New file:** `tests/guardian/test_agent_registry_hardened.py` (28 tests)

---

### T1-1: `base_detector_validator`

**Current tests (4 files):** `test_anti_patterns`, `test_guardian_config_with_logic`, `test_guardian_prompt_assembly_exclusivity`, `test_path_setup`

**Gaps:**
- `AntiPatternDetector` ABC: attempting to instantiate it directly raises `TypeError`
- `CompositeDetector.detect()` aggregates results from child detectors
- `EnforcementLevel` ordering: `ERROR > WARNING > INFO`
- `DetectionResult` fields present and typed correctly

**→ No new file needed (fan_in=11 but existing coverage is reasonable); add to existing `test_anti_patterns.py`**

---

### T1-5: `gravity_validator`

**Current tests (1 file):** `test_path_setup` — import probe only

**Gaps:**
- `UnifiedSSOTValidator` raises on import violation
- `GravityViolation`, `ImportViolation`, `HierarchyViolation` contain violation message
- Clean repo produces no violations
- Fail-closed: empty root raises not silently passes

**→ To be addressed in a follow-up session (Tier 1, lower urgency than Tier 0)**

---

## 5. Proposed Test Files and Assertions

### File A: `tests/guardian/test_classification_kernel_hardened.py`

```
TestFileTypeTaxonomy         (18 tests) — every FileType literal reachable
TestPriorityOrdering          (5 tests) — first-match-wins contract
TestDualTagConflictDetection  (5 tests) — get/clear conflicts, CONFIG_WITH_LOGIC
TestCacheSemantics            (6 tests) — hits, currsize, clear, context manager
TestErrorHardening            (6 tests) — unicode, OS, syntax, zero-byte
TestPredicates                (7 tests) — is_agent_file, is_agent_or_orchestrator
TestConsumerContractRegression (2 tests) — parametrized stability + context manager
```

**Key assertions:**
- `classify_file_standalone(path) == "IGNORE"` for `__init__.py`, empty, syntax-error
- `classify_file_standalone(path) == "AGENT"` for class ending with `Agent`
- `classification_cache_info().currsize == 0` after context manager exit
- `get_classification_conflicts()` returns a copy
- Every error path → `"IGNORE"`, never raises

---

### File B: `tests/guardian/test_agent_registry_hardened.py`

```
TestGetProfileHardFail          (7 tests) — KeyError contract
TestRegisteredAgentContracts    (8 tests) — field invariants
TestRegistryDigest              (5 tests) — determinism, format
TestGatewayTransitiveEnforcement (8 tests) — SovereigntyViolation propagation
```

**Key assertions:**
- `get_profile("__x__")` raises `KeyError` matching `"not found in registry"`
- `profile.agent_id == key` for every registry entry
- DETERMINISTIC agents have `allowed_models == ()`
- `registry_digest()` format: 3-part colon-delimited string
- `SovereigntyViolation` raised (not `None` returned) for unregistered, DETERMINISTIC, disallowed-model

---

### File C: `tests/guardian/test_structure_blueprint_hardened.py`

```
TestIsKernelComponent         (14 tests) — exact, prefix, no-match, path normalization
TestIsModularExtension        (10 tests) — exact, prefix, no-match
TestValidateBoundary           (8 tests) — return type, kernel/ext/unclassified/empty
TestRegistryImmutability       (6 tests) — frozenset, no mutation, no overlap
TestCriticalDeclarations       (9+5 parametrized) — critical paths are kernel, extensions are not
TestStructureBlueprintConfigShim (6 tests) — shim importable, __all__ match, no class defs
```

**Key assertions:**
- `is_kernel_component("agentic_core.L5_safety.core_kernel.classification_kernel") is True`
- `is_kernel_component("agentic_core.L5_safety_extra") is False` (partial overlap rejected)
- `validate_boundary("unknown") == (False, "unclassified_module: unknown")`
- `SOVEREIGN_KERNEL_COMPONENTS.add(...)` raises `AttributeError`/`TypeError`
- `set(shim.__all__) == set(pkg.__all__)`

---

### File D: `tests/guardian/test_sovereign_llm_gateway_hardened.py`

```
TestPolicyEnforcementHardFails      (10 tests) — missing id, unregistered, deterministic, disallowed model
TestAuditLogContract                 (8 tests) — append, fields, FIFO rotation, operation_stats
TestEgressAuditAndInjectionDetection (5 tests) — egress append, prompt_hash, injection scan order
TestProviderDegradedMode             (7 tests) — degraded after 5 failures, exit after timeout, fallback stat
TestSingletonContract                (4 tests) — two instances same, reset allows fresh
TestReplayEnvelopeContract           (5 tests) — present, dict, contains agent_id+model, deterministic
```

**Key assertions:**
- `SovereigntyViolation("agent_id is required")` on empty `agent_id`
- `SovereigntyViolation` message contains agent name on unregistered
- `SovereigntyViolation` message contains `"DETERMINISTIC"` on mode block
- `_injection_detector.scan` called BEFORE `_call_provider` (call order verified)
- `replay_envelope` is a `dict` containing `agent_id` and `model`
- `replay_envelope` is identical for two identical requests

---

## 6. Rationale for AST Graphing

### Why the graph improves efficiency here

**Problem without graphs:**
Guardian is consulted horizontally by 100+ consumers. Naive test expansion would produce:
- Tests for every consumer file that happens to import `sovereign_kernel` (102+ files)
- Duplicate assertions of the same contract from different angles
- Brittle integration tests requiring real filesystem structures

**How the graph helps:**

| Graph insight | Test design decision |
|---|---|
| `sovereign_kernel` fan_in=105 with test_cov=17 | All 17 test files test path constants, not `validate_boundary()`. One seam test replaces the need for 102 consumer-level regression tests. |
| `classification_kernel` fan_in=10 with `lru_cache` decorator | Cache semantics must be explicitly tested — cache bugs are invisible to callers who always see a cached result. |
| `SovereignLLMGateway` is the only node with fan_out=1 (to `agent_registry`) | The gateway-registry enforcement chain can be tested end-to-end without involving any other Guardian node. |
| `agent_registry` test_cov=1 with fan_in=10 | Single most under-tested critical node. One behavioral test file provides 10x the value of import probes. |
| `base_detector_validator` fan_in=11, `type_erasure_validator` inherits from it | If ABC is broken, all 11 concrete detectors break silently. One inheritance test protects the hierarchy. |

### Fixture minimization decisions driven by the graph

- `SovereignLLMGateway` tests use `AsyncMock` for `_call_provider` only — the graph shows the enforcement gates all fire **before** the provider call.
- `sovereign_kernel` tests require **zero filesystem fixtures** — all contracts are pure function calls on string module paths.
- `classification_kernel` tests use `tmp_path` with minimal synthetic files — the graph shows the kernel reads only the file it's given.
- `agent_registry` tests require **no fixtures at all** for hard-fail tests — `AGENT_REGISTRY` is a compile-time dict.

---

## 7. Risks and Limitations

| Risk | Mitigation |
|---|---|
| **Import edge ≠ runtime execution.** 105 files import `sovereign_kernel` but not all call `validate_boundary()` at runtime. | Tests assert behavioral contracts, not import topology. |
| **Graph does not capture dynamic imports.** `SovereignLLMGateway` uses `try/except ImportError` for `agent_registry`. | Tested via direct mock of `get_profile` to cover the fallback path. |
| **Cache invalidation race.** `lru_cache` in `classification_kernel` is module-global; tests using `tmp_path` files share the same cache. | Every test class uses `setup_method`/`teardown_method` to call `clear_classification_cache()`. |
| **Singleton state leakage.** `SovereignLLMGateway._instance` persists across tests. | All gateway tests call `SovereignLLMGateway.reset_instance()` in `setup_method`. |
| **Graph fan_in may overcount.** Package-level imports via `__init__.py` inflate consumer counts. | Fan_in is used for prioritization only, not as a correctness metric. |
| **AST-derived module paths may not match runtime import paths** in edge cases (namespace packages, conditional imports). | Rule 7 from non-negotiable rules: every AST-discovered dependency validated against actual import before structural claims. |

---

## 8. Final Prioritized Execution Order

| Priority | Action | File | Tests | Effort |
|---|---|---|---|---|
| **P0-A** | Implement `classification_kernel` hardened tests | `test_classification_kernel_hardened.py` | 48 | ✅ Done |
| **P0-B** | Implement `agent_registry` hardened tests + transitive gateway contract | `test_agent_registry_hardened.py` | 28 | ✅ Done |
| **P0-C** | Implement `structure_blueprint` hardened tests | `test_structure_blueprint_hardened.py` | 44 | ✅ Done |
| **P0-D** | Implement `SovereignLLMGateway` hardened tests | `test_sovereign_llm_gateway_hardened.py` | 38 | ✅ Done |
| **P1-A** | Add `base_detector_validator` ABC contract tests | `tests/guardian/test_anti_patterns.py` (extend) | ~8 | Pending |
| **P1-B** | Add `gravity_validator` behavioral tests | `tests/guardian/test_gravity_validator_hardened.py` | ~12 | Pending |
| **P1-C** | Add `registry_verification_enforcer` hard-fail path tests | extend `test_registry_verification.py` | ~6 | Pending |
| **P2-A** | Verify `structure_blueprint_config` shim `__all__` contract in CI | `test_structure_blueprint_config.py` (extend) | ~4 | Pending |

### Total new behavioral tests added this session: **158**

### Minimum high-signal regression suite (for when a Guardian file changes)

When `classification_kernel.py` changes:
→ Run `test_classification_kernel_hardened.py` + `test_agent_registry_hardened.py::TestGatewayTransitiveEnforcement`

When `agent_registry.py` changes:
→ Run `test_agent_registry_hardened.py` + `test_sovereign_llm_gateway_hardened.py::TestPolicyEnforcementHardFails`

When `sovereign_kernel.py` or `structure_blueprint/` changes:
→ Run `test_structure_blueprint_hardened.py` + `tests/architecture/test_contracts_fixture_placement.py`

When `SovereignLLMGateway.py` changes:
→ Run `test_sovereign_llm_gateway_hardened.py` (all) + `test_agent_registry_hardened.py::TestGatewayTransitiveEnforcement`

---

## Appendix: Graph Evidence

Raw graph data: `artifacts/_guardian_adg_result.json`
Analysis script: `artifacts/_guardian_adg_analysis.py`

Key graph properties confirmed:
- `sovereign_kernel` and `structure_blueprint_pkg` are the only nodes with fan_in > 100
- `SovereignLLMGateway` is the only Guardian node with internal fan_out (→ `agent_registry`)
- `classification_kernel` uses `lru_cache` + `contextmanager` decorators — both require explicit cache lifecycle tests
- `base_detector_validator` uses `abstractmethod` — abstract instantiation test needed
- `type_erasure_validator` is the only concrete subclass of `AntiPatternDetector` in scope
- `SOVEREIGN_KERNEL_COMPONENTS` and `MODULAR_EXTENSIONS` are `frozenset` — zero overlap confirmed programmatically

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

