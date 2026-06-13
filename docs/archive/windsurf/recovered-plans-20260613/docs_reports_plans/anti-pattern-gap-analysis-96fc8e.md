# Anti-Pattern Governance Gap Analysis

Gap analysis of 10 high-signal anti-patterns against existing code governance enforcement mechanisms.

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


## Coverage Summary

| # | Anti-Pattern | Pre-Commit | Guardian Tests | Governance Tests | CI Workflow | Gap Level |
|---|---|---|---|---|---|---|
| 1 | Gateway Bypass | ✅ T3a | ✅ `test_guardian_gateway_bypass.py` | ✅ `test_req_p0_gateway_monopoly.py` | ✅ `layer-sovereignty-enforcement.yml` | **None** |
| 2 | Unauthorized Mutation Outside UWG | ✅ T3a (global_mutation) | ✅ `test_anti_patterns.py` (GlobalMutation) | ✅ `test_req_p0_runtime_write_interceptor.py`, `test_req071_stage8_uwg_routing.py`, `test_req417_runtime_mutation_guard.py` | ✅ `layer-sovereignty-enforcement.yml` | **Partial** |
| 3 | Upward Authority Leakage | ✅ T3f (module-collision-guard) | ✅ `test_guardian_cross_layer_mutation.py` | ✅ `test_layer_sovereignty_enforcer.py` | ✅ `layer-sovereignty-enforcement.yml` | **None** |
| 4 | C0/Telemetry as Hidden Control Plane | ❌ None | ✅ `test_guardian_c0_sovereignty.py` | ❌ No `tests/governance` test | ❌ None | **High Gap** |
| 5 | Split-Brain State | ❌ None | ❌ None | ⚠️ `test_routing_config_seal.py` (seal only) | ❌ None | **High Gap** |
| 6 | Config-With-Logic | ❌ None | ❌ None | ❌ None | ❌ None | **Critical Gap** |
| 7 | Direct Prompt Compilation Outside Assembly Stage | ❌ None | ❌ None | ⚠️ `test_req095_prompt_determinism.py` (output determinism only) | ❌ None | **High Gap** |
| 8 | Human Bypass / Trusted-Admin Shortcuts | ❌ None | ❌ None | ⚠️ `test_req085_086_hil.py` (HIL fields only, not bypass gate) | ❌ None | **High Gap** |
| 9 | Oscillation / Flapping Controllers | ❌ None | ❌ None | ✅ `test_oscillation_freeze.py` | ❌ None | **Partial** |
| 10 | Duplicate SSOTs | ❌ None | ⚠️ `test_ssot_alignment.py` (registry completeness) | ⚠️ `test_ssot_structure_validation_enforcer.py` (structure drift) | ✅ `ssot-enforcement.yml`, `ssot-kernel-guardrail.yml` | **Partial** |

---

## Detailed Findings

### 1. Gateway Bypass ✅ COVERED
- **Pre-commit T3a** (`check_anti_patterns.py`): `MagicConfigDetector` catches hardcoded model name literals (e.g., `"gpt-4"`).
- **Guardian**: `test_guardian_gateway_bypass.py` — AST-scans for `provider_sdk_import` (direct `import openai/anthropic/google.generativeai`) and `direct_model_call` (`OpenAI()`).
- **Governance**: `test_req_p0_gateway_monopoly.py` — AST scan of `L0–L5` for forbidden SDK imports outside `L2_execution` allowlist.
- **CI**: `layer-sovereignty-enforcement.yml` enforces this on every push to `agentic_core/**`.
- *No gaps identified.*

---

### 2. Unauthorized Mutation Outside UWG ⚠️ PARTIALLY COVERED
- **Pre-commit T3a**: `GlobalMutationDetector` catches `sys.path.insert/append`, `os.environ[x]=y` — but **does not catch arbitrary file-write calls** (`open(..., "w")`, `Path.write_text()`) outside `L2_execution`.
- **Governance tests**: `test_req_p0_runtime_write_interceptor.py` tests the write interceptor contract but is a **self-contained mock** (doesn't scan the live codebase for naked writes).
- **Gap**: No AST scan at pre-commit or in guardian confirming that production source files outside `L2_execution` contain zero `open(…, "w")` / `.write_text()` / `.write_bytes()` calls. `test_req_p0_gateway_monopoly.py` lists these as `_FORBIDDEN_IO_SYMBOLS` but only enforces SDK imports in the current implementation.

#### Recommendation
- **Pre-commit T3a** — Add `WriteGatewayBypassDetector` to `AntiPatternScanner` (new `AntiPatternCategory.WRITE_GATEWAY_BYPASS`) scanning `L0–L5` source for unguarded write calls outside the UWG allowlist.
- **`tests/guardian/`** — Add `test_guardian_uwg_mutation_fence.py` mirroring the gateway-bypass guardian pattern: fixture with a naked `file.write_text(...)` in a non-L2 path → FAIL.
- **`tests/governance/`** — Extend `test_req_p0_gateway_monopoly.py` to activate the already-declared `_FORBIDDEN_IO_SYMBOLS` write-call check.

---

### 3. Upward Authority Leakage ✅ COVERED
- **Guardian**: `test_guardian_cross_layer_mutation.py` — checks `L6_mutates_L4`, `L4_invokes_L2`, `upward_layer_mutation`, `C0_mutates_control_plane`.
- **Governance**: `test_layer_sovereignty_enforcer.py` (24 KB) and `test_layer_sovereignty_guard.py`.
- **CI**: `layer-sovereignty-enforcement.yml` runs cross-layer import checks inline and runs `tests/guardian/test_l4_state_write_sovereignty.py` and `test_l1_cognition_purity_contract.py` on every push.
- *No gaps identified.*

---

### 4. C0/Telemetry as Hidden Control Plane 🔴 HIGH GAP
- **Guardian**: `test_guardian_c0_sovereignty.py` — detects `embedding_drives_routing`, `embedding_drives_tier_selection`, `embedding_mutates_threshold` via AST pattern match.
- **Gap A**: No pre-commit hook calls `run_c0_sovereignty_guardian` — the check only runs when guardian tests are explicitly executed, not on every commit.
- **Gap B**: Coverage is regex/name-pattern matching (`embedding_score`, `embedding_result`). RAG retrieval outputs, completeness signals, or evaluation scores stored under other variable names (e.g., `rag_score`, `retrieval_confidence`, `completeness_pct`) are **not caught**.
- **Gap C**: No `tests/governance/` test validates that telemetry emission paths (L6 observability) cannot write back to L4 state or L5 safety config.

#### Recommendation
- **Pre-commit T3a** — Wire `run_c0_sovereignty_guardian` (or an equivalent `C0ControlPlaneDetector`) into `check_anti_patterns.py`, or add a dedicated T3a-style hook `check-c0-sovereignty`.
- **`tests/governance/`** — Add `test_c0_telemetry_cannot_mutate_routing.py`: AST-scan L6 observability modules for assignments into L5 safety or L4 state objects.
- **`tests/governance/`** — Expand variable-name vocabulary in `scan_embedding_control_flow` beyond `embedding_*` to cover `rag_*`, `retrieval_*`, `completeness_*`, `eval_score`.

---

### 5. Split-Brain State 🔴 HIGH GAP
- **Governance**: `test_routing_config_seal.py` validates that the routing config is sealed (hash-locked), and `test_time_shifted_influence.py` checks time-shifted influence. Neither test verifies that **L0 routing reads and L5 verification reads are JIT-coupled to the same config snapshot**.
- **Gap**: No test asserts that config objects read at routing time are the identical instance/snapshot used at L5 verification time. A test that mocks stale config at one layer while the other reads fresh config, and asserts the system detects/rejects this, does not exist.

#### Recommendation
- **`tests/governance/`** — Add `test_split_brain_config_invariant.py`: simulate scenario where L0 routes against config version N while L5 verifies against version N+1; assert the system raises or rejects.
- **`tests/integration/`** — Add an integration test that exercises the Elevator Shaft JIT read contract end-to-end: a single routing round must read config exactly once (monkeypatched to count reads), and the same handle must be passed to L5 verification.
- **Pre-commit**: Consider a static check that `routing_config` is never stored in a module-level cache (global variable) in L0 or L5 files, as cached config is the root cause of split-brain.

---

### 6. Config-With-Logic 🔴 CRITICAL GAP (zero coverage)
- No pre-commit hook, no guardian test, no governance test, no CI workflow checks for business logic embedded inside config files or config-typed objects.
- The `MagicConfigDetector` catches *magic values* (hardcoded model names, thresholds) but does not detect *callable logic*, lambda expressions, conditionals, or `if`/`match` branches embedded in config dicts/JSON/YAML structures parsed at runtime.
- The `AntiPatternCategory` enum has no `CONFIG_WITH_LOGIC` entry.
- **Note**: The Classification Kernel (`classification_kernel.py`) does flag `CONFIG_WITH_LOGIC` as a governance violation pattern for *file classification* purposes, but this is not wired into the pre-commit scanner or any guardian/governance test.

#### Recommendation
- **Pre-commit T3a** — Add `ConfigWithLogicDetector` (new `AntiPatternCategory.CONFIG_WITH_LOGIC`) that AST-scans for: `lambda` expressions in module-level assignments, `if`/`match` inside config factory functions, callable values in dict literals assigned to `*_config` / `*_spec` / `*_policy` variables.
- **`tests/guardian/`** — Add `test_guardian_config_with_logic.py` with positive/negative fixtures: a dict containing a `lambda` → FAIL; a plain data dict → PASS.
- **`tests/governance/`** — Add `test_config_with_logic_invariant.py`: AST scan all `config/` subdirectories and `*_config.py` files across `agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/` for callable literals.

---

### 7. Direct Prompt Compilation Outside Assembly Stage 🔴 HIGH GAP
- **Governance**: `test_req095_prompt_determinism.py` only tests that a simulated assembly function produces stable output — it does **not** scan the codebase for locations where prompt strings are directly concatenated or f-string-built outside the `AirlockAssembler`.
- **Unit**: `test_assembly_stage.py` validates `AirlockAssembler` correctness but does not enforce exclusivity (that nothing else is allowed to produce final prompt strings).
- **Gap**: No AST scan confirms that `s0_system`/`i0_instructional`/`c0_context`/`u0_user_prompt` slot strings are never assembled via f-string, `str.join()`, `+` concatenation, or `format()` calls outside `assembly_stage.py`.

#### Recommendation
- **Pre-commit T3a** — Add `DirectPromptCompilationDetector` (new `AntiPatternCategory.DIRECT_PROMPT_COMPILATION`) scanning for f-strings or string concatenation that reference any of the known prompt slot names (`s0_`, `i0_`, `c0_`, `u0_`) outside the allowlisted assembly module.
- **`tests/guardian/`** — Add `test_guardian_prompt_assembly_exclusivity.py`: fixture with `prompt = f"{system_text}\n{user_text}"` outside assembly module → FAIL; same pattern inside `assembly_stage.py` → PASS (allowlisted).
- **`tests/governance/`** — Add `test_prompt_compilation_outside_assembly.py`: AST scan `L1_cognition`, `apps_rg/reasoning/`, `apps_lic/reasoning/` for string operations that look like prompt building.

---

### 8. Human Bypass / Trusted-Admin Shortcuts 🔴 HIGH GAP
- **Governance**: `test_req085_086_hil.py` only asserts that `HILReviewOutcome` has `reviewer_sig`/`reviewer_id` fields and that `MODIFY_DIFF` sets `requires_l5_reclear=True`. It does **not** assert the L5 re-clear actually happens before execution proceeds.
- **Gap A**: No test verifies that a `HILReviewOutcome` with `decision="APPROVE"` but without a valid `reviewer_sig` is rejected at the gate.
- **Gap B**: No test verifies that a human patch submitted via Path D cannot bypass L5 clearance — i.e., that the execution pipeline checks `requires_l5_reclear` and blocks if L5 has not signed off.
- **Gap C**: No pre-commit hook or guardian test scans for admin-shortcut patterns (e.g., `if admin:`, `bypass_l5=True`, `skip_gateway=True` flags in source).

#### Recommendation
- **`tests/governance/`** — Add `test_hil_bypass_rejection.py`: assert that `HILReviewOutcome(decision="APPROVE", reviewer_sig="", ...)` raises/rejects at the HIL gate.
- **`tests/governance/`** — Add `test_path_d_l5_reclear_enforcement.py`: mock `requires_l5_reclear=True` and assert execution is blocked until L5 clearance is obtained.
- **Pre-commit T3a** — Add `AdminBypassDetector`: scan for boolean flag names matching `*_bypass`, `*_skip_*`, `admin_override`, `force_approve` in production source files.
- **`tests/guardian/`** — Add `test_guardian_human_bypass.py` following the existing guardian pattern.

---

### 9. Oscillation / Flapping Controllers ⚠️ PARTIALLY COVERED
- **Governance**: `test_oscillation_freeze.py` — comprehensive unit tests for `OscillationDetector` with `ParameterFrozenError`, cooldown windows, freeze cycles, independent parameter tracking. **Well-covered at unit level.**
- **Gap A**: No governance or integration test verifies that the `OscillationDetector` is actually **wired** into the healer/tier-flip control path — only the detector in isolation is tested.
- **Gap B**: No test asserts that repeated tier flips (`Tier1 → Tier2 → Tier1 → ...`) in the routing engine trigger the circuit breaker, not just that the detector can detect them.
- **Gap C**: No pre-commit hook prevents code that disables or reconfigures the `OscillationDetector` with a trivially large `cooldown_window`.

#### Recommendation
- **`tests/integration/`** — Add `test_oscillation_circuit_breaker_wired.py`: drive a mock healing loop through N alternating tier assignments and assert `ParameterFrozenError` propagates to the healer control plane.
- **`tests/governance/`** — Add `test_oscillation_detector_wiring_invariant.py`: assert via import inspection that the healer/control-plane classes instantiate `OscillationDetector` with `cooldown_window` ≤ configured maximum.
- **Pre-commit**: Add a comment-guard check that `OscillationDetector` construction sites cannot use `cooldown_window` > threshold without a `# guardian: allow-oscillation-override` annotation.

---

### 10. Duplicate SSOTs ⚠️ PARTIALLY COVERED
- **CI**: `ssot-enforcement.yml` and `ssot-kernel-guardrail.yml` enforce SSOT structure.
- **Guardian**: `test_ssot_alignment.py` and `test_registry_completeness.py` check registry completeness and SSOT cross-references.
- **Governance**: `test_ssot_structure_validation_enforcer.py` (25 KB) checks structure drift.
- **Gap A**: No test specifically hunts for *duplicate prompt templates* — the same prompt text or fragment defined in more than one module (e.g., `apps_rg/reasoning/X.py` and `apps_lic/reasoning/Y.py` both defining the same system prompt string).
- **Gap B**: No test checks for duplicate agent profile/metadata across `apps_rg/config/agent_spec_config.py` and `apps_lic/config/agent_specs.json`.
- **Gap C**: No pre-commit hook detects string-level duplication of policy constants or thresholds across config files.

#### Recommendation
- **`tests/guardian/`** — Add `test_guardian_duplicate_ssot_prompts.py`: hash all module-level string constants > N chars across `apps_*/reasoning/` and `apps_*/config/` and assert no two are identical.
- **`tests/governance/`** — Add `test_no_duplicate_agent_specs.py`: load all `agent_spec*.json` / `agent_spec*_config.py` files and assert agent IDs are unique globally.
- **Pre-commit T3b (report-location) or new T3x** — Extend `validate_report_location.py` or add a dedicated hook to detect duplicate string constants > 80 chars shared across config files on staged files.

---

## Prioritized Action List

| Priority | Gap | Recommended Location | Effort |
|---|---|---|---|
| 🔴 P0 | Config-With-Logic — zero coverage | New `ConfigWithLogicDetector` in pre-commit T3a + `tests/guardian/` | Medium |
| 🔴 P0 | Direct Prompt Compilation — zero AST enforcement | New `DirectPromptCompilationDetector` in pre-commit T3a + `tests/guardian/` | Medium |
| 🔴 P1 | C0 Telemetry → Control Plane — no pre-commit hook | Wire `run_c0_sovereignty_guardian` into T3a pre-commit | Low |
| 🔴 P1 | Split-Brain State — no JIT coupling test | New `test_split_brain_config_invariant.py` in `tests/governance/` | Medium |
| 🔴 P1 | Human Bypass — gate enforcement not tested | `test_hil_bypass_rejection.py` + `test_path_d_l5_reclear_enforcement.py` in `tests/governance/` | Low |
| 🟡 P2 | UWG Mutation — write-call AST scan missing | Activate `_FORBIDDEN_IO_SYMBOLS` write checks in `test_req_p0_gateway_monopoly.py` | Low |
| 🟡 P2 | Oscillation — wiring not integration-tested | `test_oscillation_circuit_breaker_wired.py` in `tests/integration/` | Medium |
| 🟡 P2 | Duplicate SSOTs — prompt/spec dedup missing | `test_guardian_duplicate_ssot_prompts.py` in `tests/guardian/` | Medium |

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

