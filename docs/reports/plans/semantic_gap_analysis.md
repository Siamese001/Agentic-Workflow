# Semantic Gap Analysis - Agentic Architecture Major Arteries

## Executive Summary

**Total Gaps Identified:** 12
**High Priority:** 5
**Medium Priority:** 4
**Low Priority:** 3
**Parse Failures:** 0

## Analysis Methodology

This analysis traces actual execution flows through L0-L6 layers using AST-based
code scanning to identify where architectural intent (lower latency, deterministic
lookups, cache-first patterns) diverges from implementation reality.

**Approach:**
1. Map critical hot paths across each layer
2. AST scan for import statements and cache usage patterns
3. Identify missing wirings between cache modules and consumers
4. Categorize gaps by layer, artery, and priority
5. Surface parse failures explicitly instead of silently dropping files from analysis

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
| L1 | 1 | 1 | 0 | 2 |
| L2 | 4 | 0 | 0 | 4 |
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
- `get_or_fetch` pattern is used consistently
- Replay mode tests pass with warm cache (no redundant fetches)
- Side-effect envelope tests confirm cache-first behavior
- Parse failure count is zero or intentionally documented
