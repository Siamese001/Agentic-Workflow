# Semantic Gap Analysis - Agentic Architecture Major Arteries

## Executive Summary

**Total Gaps Identified:** 37
**High Priority:** 13
**Medium Priority:** 12
**Low Priority:** 12
**Parse Failures:** 3

## Analysis Methodology

This analysis traces actual execution flows through L0-L6 layers using AST-based
code scanning to identify where architectural intent (lower latency, deterministic
lookups, cache-first patterns) diverges from implementation reality.

**Approach:**
1. Map critical hot paths across each layer
2. AST scan for import statements and cache usage patterns
3. Detect prompt assemblers and score canonical slot coverage for S0/D0/I0/C0/U0
4. Check for manifest-hash and boundary-snapshot evidence on prompt execution paths
5. Identify missing wirings between cache modules and consumers
6. Categorize gaps by layer, artery, and priority
7. Surface parse failures explicitly instead of silently dropping files from analysis

## Prompt Taxonomy Coverage

| File | Slot Coverage | Manifest Hash | Boundary Snapshot |
|------|---------------|---------------|-------------------|
| `agentic_core/L0_routing/engines/assembly_stage.py` | S0=present, D0=present, I0=present, C0=present, U0=present | yes | no |
| `agentic_core/L0_routing/engines/execution_orchestrator.py` | S0=missing, D0=present, I0=missing, C0=missing, U0=missing | no | no |
| `agentic_core/L0_routing/scripts/class_info.py` | S0=missing, D0=present, I0=missing, C0=present, U0=missing | no | no |
| `agentic_core/L1_cognition/engines/prompt_artifact_cache.py` | S0=present, D0=present, I0=present, C0=present, U0=missing | no | no |
| `agentic_core/L2_execution/enforcement/boundary_verifier.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/engines/execution_gateway.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/healers/qwen_vllm_inference.py` | S0=present, D0=missing, I0=missing, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/types/execution_trace_types.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/types/sandbox_envelope_types.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |

## Parse Failures

| File | Error Type | Message |
|------|------------|---------|
| `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py` | IndentationError | unexpected indent (SSOTFolderCleanupAgent.py, line 100) |
| `agentic_core/L0_routing/scripts/forensic_discovery_prep.py` | IndentationError | expected an indented block after 'try' statement on line 53 (forensic_discovery_prep.py, line 54) |
| `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py` | IndentationError | unexpected indent (run_guardian_hierarchy_compliance.py, line 72) |

## L0 Layer Gaps

### L0-GAP-002: Reasoning Policy Engine

**Priority:** MEDIUM

**Architectural Intent:**
Cache immutable policy configurations to avoid repeated L4 state lookups

**Implementation Reality:**
reasoning_policy_engine.py does not use policy_registry_cache.py

**Impact:**
Policy config fetched from L4 state on every request

**Evidence Files:
- `agentic_core/L0_routing/engines/reasoning_policy_engine.py`

**Recommended Fix:**
Wrap policy_config retrieval with PolicyRegistryCache.get_or_fetch()

---

## L1 Layer Gaps

### L1-GAP-001: Cognitive Engine Tool Resolution

**Priority:** HIGH

**Architectural Intent:**
Cache expensive tool embedding computations to avoid repeated API calls

**Implementation Reality:**
cognitive_engine.py does not use tool_embedding_cache.py

**Impact:**
Tool embeddings recomputed on every cognition cycle

**Evidence Files:
- `agentic_core/L1_cognition/engines/cognitive_engine.py`

**Recommended Fix:**
Import ToolEmbeddingCache and wrap embedding generation with cache.get_or_fetch()

---

### PROMPT-TAXONOMY-GAP-1f8d794d52: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_orchestrator.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=present, I0=missing, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, I0, C0, U0

---

### PROMPT-TAXONOMY-GAP-2fb9c2152f: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
prompt_artifact_cache.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=present, D0=present, I0=present, C0=present, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: U0

---

### PROMPT-TAXONOMY-GAP-455d7b7dca: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
sandbox_envelope_types.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-53e1b1633f: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_trace_types.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-8a6344918d: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
qwen_vllm_inference.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=present, D0=missing, I0=missing, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: D0, I0, C0, U0

---

### PROMPT-TAXONOMY-GAP-94ab5260b1: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_gateway.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-d23b3738f0: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
boundary_verifier.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-f88702ec50: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
class_info.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=present, I0=missing, C0=present, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, I0, U0

---

### L1-GAP-PROMPT-bd4796a6e6: Prompt Artifact Retrieval

**Priority:** MEDIUM

**Architectural Intent:**
Cache parsed prompt templates to avoid repeated file I/O and parsing

**Implementation Reality:**
prompts_util.py does not use prompt_artifact_cache

**Impact:**
Prompt templates re-read and re-parsed on every request

**Evidence Files:
- `agentic_core/L1_cognition/utils/prompts_util.py`

**Recommended Fix:**
Wrap prompt loading with prompt_artifact_cache.get_or_fetch()

---

### PROMPT-MANIFEST-GAP-1f8d794d52: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_orchestrator.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-2fb9c2152f: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
prompt_artifact_cache.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-455d7b7dca: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
sandbox_envelope_types.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-53e1b1633f: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_trace_types.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-8a6344918d: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
qwen_vllm_inference.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-94ab5260b1: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_gateway.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-d23b3738f0: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
boundary_verifier.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-f88702ec50: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
class_info.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

## L2 Layer Gaps

### L2-GAP-VALIDATOR-2a5a3a48e6: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
qwen_gpu_validator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_gpu_validator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-462f37c35b: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
signature_invalidator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/healers/signature_invalidator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-5de3900449: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
vllm_replay_validator_types.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_replay_validator_types.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-83850aa0d5: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
manifest_hash_validator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/enforcement/manifest_hash_validator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### PROMPT-VALIDATOR-GAP-04f677f1e8: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
assembly_stage.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/engines/assembly_stage.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-1f8d794d52: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_orchestrator.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-2fb9c2152f: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
prompt_artifact_cache.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-455d7b7dca: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
sandbox_envelope_types.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-53e1b1633f: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_trace_types.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-8a6344918d: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
qwen_vllm_inference.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-94ab5260b1: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_gateway.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-d23b3738f0: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
boundary_verifier.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-f88702ec50: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
class_info.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

## L3 Layer Gaps

### L3-GAP-001: Orchestration Plan Construction

**Priority:** MEDIUM

**Architectural Intent:**
Cache orchestration plans to avoid repeated planning for identical requests

**Implementation Reality:**
orchestrator_engine.py does not use orchestration_plan_cache

**Impact:**
Orchestration plans recomputed on every request

**Evidence Files:
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py`

**Recommended Fix:**
Wrap plan construction with orchestration_plan_cache.get_or_fetch()

---

## L5 Layer Gaps

### L5-GAP-POLICY-8b7f6e8070: Safety Policy Enforcement

**Priority:** MEDIUM

**Architectural Intent:**
Cache immutable safety policies to avoid repeated L4 lookups

**Implementation Reality:**
sovereign_policy_registry_enforcer.py does not use policy_registry_cache

**Impact:**
Safety policies fetched from L4 on every enforcement check

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py`

**Recommended Fix:**
Wrap policy retrieval with policy_registry_cache.get_or_fetch()

---

## L6 Layer Gaps

### L6-GAP-CONFIG-3eed2e9d41: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
system_telemetry_util.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/utils/system_telemetry_util.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

### L6-GAP-CONFIG-8baab37ffc: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
entropy_telemetry_engine.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/engines/entropy_telemetry_engine.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

### L6-GAP-CONFIG-aeb60076fa: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
rag_telemetry_collector.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/enforcement/rag_telemetry_collector.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

## Priority Matrix

| Layer | High | Medium | Low | Total |
|-------|------|--------|-----|-------|
| L0 | 0 | 1 | 0 | 1 |
| L1 | 9 | 9 | 0 | 18 |
| L2 | 4 | 0 | 9 | 13 |
| L3 | 0 | 1 | 0 | 1 |
| L5 | 0 | 1 | 0 | 1 |
| L6 | 0 | 0 | 3 | 3 |

## Next Steps

1. **High Priority Gaps:** Address immediately - these cause repeated expensive operations
2. **Medium Priority Gaps:** Schedule for next sprint - moderate latency impact
3. **Low Priority Gaps:** Backlog - minor optimizations
4. **Parse Failures:** Fix or explicitly waive broken files so analysis coverage is auditable

## Validation

After implementing fixes, rerun semantic gap analysis to verify:
- Cache modules are imported in hot path files
- Prompt assemblers explicitly cover S0, D0, I0, C0, and U0
- Governed prompt assembly emits a manifest hash
- Validator paths emit boundary_snapshot.json for prompt-package inspection
- `get_or_fetch` pattern is used consistently
- Replay mode tests pass with warm cache (no redundant fetches)
- Side-effect envelope tests confirm cache-first behavior
- Parse failure count is zero or intentionally documented
