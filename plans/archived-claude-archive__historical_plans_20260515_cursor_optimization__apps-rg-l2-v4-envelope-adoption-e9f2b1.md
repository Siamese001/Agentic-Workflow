---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-l2-v4-envelope-adoption-e9f2b1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-l2-v4-envelope-adoption-e9f2b1.md'
source_sha256: fdf49622a598bff198f668a30418b54413109ee6f7baac3b1c9c725c48c6336a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: "Apps_RG L2 v4 Envelope Adoption"
slug: "apps-rg-l2-v4-envelope-adoption-e9f2b1"
plan_type: refactor
created: "2026-05-13"
status: "Completed"
tier: "T3"
dod_exempt: false
completed: "2026-05-13"
---

# Apps_RG L2 v4 Envelope Adoption

**Plan ID:** apps-rg-l2-v4-envelope-adoption-e9f2b1  
**Status:** Completed  
**Created:** 2026-05-13  
**Completed:** 2026-05-13  
**Classification:** apps_rg wiring/adoption (not generic core enabling)  
**Prerequisite:** Category A patch accepted (ProviderGateway public API, quarantine liquidation complete)

---

## Summary

Adopt the existing generic agentic_core L2 v4 envelope for apps_rg without contaminating agentic_core. This is **apps_rg wiring/adoption work**, not core enabling work, unless the audit proves a generic primitive is missing.

**Key Principle:** HOP execution remains in L2.3/E3. The missing work is the governed envelope around HOP: E1 Prep → E2 Validation → E3 Exec → E4 Heal → E5 Seal.

---

## Current State vs Target State

### Current State (Post-Category A)

```
CompiledPromptArtifact ──► l2_execute_apps_rg()
                              │
                              ├──► _execute_via_qwen_vllm() ──► ProviderGateway.invoke()
                              │
                              ├──► _call_external_ensemble() ──► ProviderGateway.invoke()
                              │
                              └──► SealedL2Artifact (partial fields)

Missing:
- L2ExecutionPacket wrapper
- E1 FrozenExecutionContext
- E2 validation gate
- Structured E4 heal
- Full E5 Seal with replay manifest
```

### Target State (Post-This Plan)

```
CompiledPromptArtifact ──► apps_rg L2 adapter
                              │
                              ▼
                    ┌─────────────────────┐
                    │  L2ExecutionPacket  │ ◄── wraps CPA + metadata
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  E1 PREP            │
                    │  FrozenExecutionContext
                    │  - policy_hash      │
                    │  - blueprint_hash   │
                    │  - registry_digest  │
                    │  - provider/model   │
                    │  - sandbox envelope │
                    │  - capability token   │
                    │  - budget           │
                    │  - replay_key       │
                    │  - idempotency_key  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  E2 VALIDATION      │
                    │  ApprovedWorkOrder  │
                    │  - provider registry│
                    │  - sandbox check    │
                    │  - capability check │
                    │  - route match      │
                    │  - prompt refs      │
                    │  - evidence refs    │
                    │  - budget check     │
                    │  - replay binding   │
                    │  - no L4 write      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  E3 HOP EXEC        │ ◄── L2.3
                    │  ProviderGateway    │
                    │     .invoke()       │
                    │  - preserve receipt │
                    │  - no direct calls  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  E4 HEAL            │
                    │  Same-authority only│
                    │  - JSON repair      │
                    │  - Schema reformat  │
                    │  - Deterministic    │
                    │  - No provider swap │
                    │  - No route change  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  E5 SEAL            │
                    │  SealedL2Artifact   │
                    │  - full fields      │
                    │  - provider receipts│
                    │  - attempt receipts │
                    │  - heal receipts    │
                    │  - replay manifest  │
                    │  - durable_commit   │
                    │       = false       │
                    │  - mutation_inert   │
                    └──────────┬──────────┘
                               │
                               ▼
                         Exit Gate
```

---

## Files to Inspect

### Core L2 v4 Contracts (Read-Only Reference)
| File | Purpose |
|------|---------|
| `agentic_core/L2_execution/types/l2_v4_contracts.py` | WorkOrderInputs, FrozenExecutionContext, PrepOutput, ValidationOutput, ApprovedWorkOrder, TelemetryBundle |
| `agentic_core/L2_execution/types/l2_v3_receipts.py` | PrepReceipt, ValidationReceipt, AttemptReceipt, HealReceipt, DispatchReceipt |
| `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` | E1→E2→E3→E4→E5 orchestration (adapter pattern) |
| `agentic_core/L2_execution/l2_package_driven_executor.py` | Package-driven L2 executor (reference implementation) |

### Current apps_rg L2 (Modify)
| File | Purpose |
|------|---------|
| `apps_rg/runtime/bindings/l2_binding.py` | Current l2_execute_apps_rg() implementation |
| `apps_rg/config/provider_profiles.yaml` | Provider registry configuration |

### SealedL2Artifact Contract (Read)
| File | Purpose |
|------|---------|
| `agentic_core/runtime/contracts/sealed_l2_artifact.py` | Target E5 output contract |
| `agentic_core/runtime/contracts/compiled_prompt_artifact.py` | E1 input source |

### Provider Infrastructure (Read)
| File | Purpose |
|------|---------|
| `agentic_core/runtime/providers/provider_gateway.py` | E3 HOP execution (already used) |
| `agentic_core/runtime/providers/provider_types.py` | ProviderRequest, ProviderInvocationReceipt |

---

## Category A Invariant Preservation (MUST VERIFY)

Implementation must continuously prove these invariants from Category A:

| Invariant | Verification Method | Gate |
|-----------|---------------------|------|
| No private ProviderGateway calls | `grep -r "_invoke_local_vllm\|_invoke_external_api" apps_rg/` | CI enforced |
| No direct urllib/requests/httpx/openai/anthropic | `grep -r "urllib\|requests\.\|httpx\.\|openai\.\|anthropic\." apps_rg/` | CI enforced |
| ProviderGateway.invoke() only HOP path | `grep -r "gateway\.invoke" apps_rg/` must be only call | Code review |
| pytest collect-only zero errors | `pytest tests/_apps_contract/ --collect-only` | CI enforced |
| Zero collection errors preserved | Pre-commit hook | `check_apps_rg_collection.py` |

**Blocking:** Any violation of these invariants → immediate rollback to Category A state.

---

## Explicit L2 Boundaries (MUST NOT)

L2 MUST NOT perform the following actions. Each is a hard boundary violation:

| Action | Why Blocked | Detection |
|--------|-------------|-----------|
| **Assemble prompts** | Belongs to PA (L1 output) | grep `prompt_assembly` in L2 |
| **Retrieve C0 evidence** | Belongs to C0/cross-app substrate | grep `c0_retrieval\|substrate_ingest` in L2 |
| **Choose route** | Belongs to L0/L1 routing | grep `route_select\|choose_route` in L2 |
| **Expand workflow** | Belongs to L3 orchestration | grep `workflow_expand\|step_expand` in L2 |
| **Judge final quality** | Belongs to Exit/L5 evaluation | grep `judge\|grade\|score` in L2 (except heal) |
| **Write L4** | Belongs to L5/UWG durability | grep `l4_write\|uwg_write\|durable_commit` in L2 |
| **Mutate durable state** | L2 produces proposed_diff only | Check for side-effect writes |
| **Widen authority during heal** | E4 must preserve frozen context | Authority proof comparison |

**W1 Audit Task:** Verify no boundary violations exist in current `l2_binding.py` before adding envelope.

---

## Files Proposed to Modify

### Primary Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `apps_rg/runtime/bindings/l2_binding.py` | Major refactor | Implement E1-E5 envelope around existing HOP calls |
| `apps_rg/runtime/bindings/l2_envelope_adapter.py` | New file | apps_rg-specific E1→E5 adapter implementing v4 contracts |
| `apps_rg/config/l2_validation_rules.yaml` | **Conditional** | E2 validation rules — only if W1 audit proves YAML needed vs inline |
| `apps_rg/config/l2_e4_heal_profile.yaml` | **Conditional** | E4 heal policies — only if W1 audit proves YAML needed vs inline |

### Supporting Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `apps_rg/__init__.py` | Minor | Export new L2 envelope types if needed |
| `tests/_apps_contract/test_apps_rg_l2_envelope.py` | New test file | E1-E5 phase contract tests |

---

## Generic Core Enabling Gaps

**Assessment:** After audit, the following generic primitives exist and do NOT require core modification:

| Primitive | Status | Location |
|-----------|--------|----------|
| L2ExecutionPacket | ✅ Exists | `l2_v4_contracts.py` - container contract |
| FrozenExecutionContext | ✅ Exists | `l2_v4_contracts.py` - E1 output |
| WorkOrderInputs | ✅ Exists | `l2_v4_contracts.py` - E1 input |
| ApprovedWorkOrder | ✅ Exists | `l2_v4_contracts.py` - E2 output |
| ValidationOutput | ✅ Exists | `l2_v4_contracts.py` - E2 output |
| PrepOutput | ✅ Exists | `l2_v4_contracts.py` - E1 output |
| TelemetryBundle | ✅ Exists | `l2_v4_contracts.py` - E3 output |
| l2_phase_pipeline | ✅ Exists | `orchestration/l2_phase_pipeline.py` - orchestrator |
| ProviderGateway.invoke() | ✅ Exists | Already used in Category A |
| SealedL2Artifact | ✅ Exists | `runtime/contracts/sealed_l2_artifact.py` - E5 output |

**Conclusion:** No generic core enabling gaps identified. This is purely apps_rg wiring/adoption work.

---

## Apps_RG Adapter/Wiring Changes

### 1. E1 PREP: Build FrozenExecutionContext

**Adapter Function:** `apps_rg_l2_e1_prep()`

**Inputs:**
- `CompiledPromptArtifact` (from PA)
- `RouteContract` (from L0)
- `apps_rg` profile/config

**Outputs:** `PrepOutput` containing:

| Field | Source | Mapping |
|-------|--------|---------|
| `frozen_execution_context.tool_registry_version` | `apps_rg/config/tool_registry.yaml` | Profile version hash |
| `frozen_execution_context.model_runtime_version` | Provider profile | `local_qwen_generator.model` |
| `frozen_execution_context.provider_lane` | Provider profile | `"local_vllm"` or `"external_ensemble"` |
| `frozen_execution_context.filesystem_view` | RouteContract sandbox | `sandbox.file_roots` |
| `frozen_execution_context.network_rules` | RouteContract egress | `egress.allowed_destinations` |
| `frozen_execution_context.secrets_scope` | RouteContract | `execution_form.secrets_scope` |
| `frozen_execution_context.allowed_file_roots` | RouteContract | `sandbox.file_roots` tuple |
| `frozen_execution_context.allowed_network_destinations` | RouteContract | `egress.allowed_destinations` tuple |
| `replay_bindings.determinism.blueprint_hash` | CompiledPromptArtifact | `prompt.compilation_hash` |
| `replay_bindings.determinism.policy_hash` | RouteContract | `route.policy_digest` |
| `replay_bindings.snapshot_manifest` | Runtime | Determinism bundle snapshot |
| `replay_bindings.clock_policy` | Config | `"run_clock_offsets"` |
| `write_lock_assertion.no_direct_l4_path` | Constant | `True` |
| `write_lock_assertion.proposed_diff_only` | Constant | `True` |
| `write_lock_assertion.persistence_disabled` | Constant | `True` |
| `idempotency_key` | Request | `request_id + run_id + attempt_seed` |
| `lineage_root` | Request | `trace_id + span_id` |

### 2. E2 VALIDATION: ApprovedWorkOrder Gate

**Adapter Function:** `apps_rg_l2_e2_validate()`

**Validation Checks (E2 Rules):**

| Check # | Rule | Implementation | On Fail |
|---------|------|----------------|---------|
| V1 | Provider registry check | Verify `local_qwen_generator` in registry | SealedRejectionPacket with decisive_reason |
| V2 | Sandbox envelope check | Verify `sandbox_required` matches route | SealedRejectionPacket with decisive_reason |
| V3 | Capability token check | Verify `allowed_models` contains target model | SealedRejectionPacket with decisive_reason |
| V4 | Route match check | Verify CPA `task_class` matches route | SealedRejectionPacket with decisive_reason |
| V5 | Prompt refs check | Verify `prompt_artifact_digest` non-empty | SealedRejectionPacket with decisive_reason |
| V6 | Evidence refs check | Verify `evidence_refs` non-empty if grounding required | SealedRejectionPacket with decisive_reason |
| V7 | Budget check | Verify `execution_budget_ms` > 0 | SealedRejectionPacket with decisive_reason |
| V8 | Replay binding check | Verify `replay_key` non-empty | SealedRejectionPacket (non-deterministic) |
| V9 | No direct L4 write check | Verify `write_lock_assertion.no_direct_l4_path` | SealedRejectionPacket (hard block) |

**E2 Failure Semantics (CRITICAL):**
- L2 MUST NOT: reroute, replan, reground, or call user/L0/L1/L3/C0/PA directly
- On validation FAIL: emit `ValidationOutput` with `sealed_rejection_packet`
- Include `decisive_reason` and `recommended_next_owner` (informational only)
- Downstream consumer (Exit, L5, or orchestrator) decides next action based on sealed packet

**Output:** `ValidationOutput` with `approved_work_order` or `sealed_rejection_packet`

### 3. E3 HOP EXEC: ProviderGateway.invoke()

**Adapter Function:** `apps_rg_l2_e3_execute()`

**Implementation:**
- Use existing `_execute_via_qwen_vllm()` from Category A
- Use existing `_call_external_ensemble()` from Category A
- Wrap results in `TelemetryBundle`
- Capture `ProviderInvocationReceipt` from gateway

**Key Constraint:** No changes to ProviderGateway usage (already correct from Category A)

### 4. E4 HEAL: Same-Authority Repair

**Adapter Function:** `apps_rg_l2_e4_heal()`

**Heal Policies (Same Authority Only):**

| Heal Type | Allowed | Implementation |
|-----------|---------|----------------|
| JSON trailing comma repair | ✅ Yes | Regex `r",\s*([}\]])"` → `r"\1"` |
| JSON truncation trim | ✅ Yes | Find rightmost `}` and parse prefix |
| Output reformat (markdown fences) | ✅ Yes | `_strip_json_fences()` already exists |
| Deterministic trim | ✅ Yes | Remove trailing content after valid JSON |
| Transient network retry | ✅ Yes | Only if same provider, same endpoint |

| Heal Type | Disallowed | Block |
|-----------|------------|-------|
| Provider substitution | ❌ **BLOCKED** | Cannot switch from Qwen to GPT |
| Route change | ❌ **BLOCKED** | Cannot change from R4 to R5 |
| Policy widening | ❌ **BLOCKED** | Cannot relax sandbox/capability |
| Sandbox escalation | ❌ **BLOCKED** | Cannot add file/network access |
| Budget increase | ❌ **BLOCKED** | Cannot exceed retry_ceiling |

**E4 Same-Authority Enforcement:**
- Heal receipts must prove same provider/model/sandbox/capability as original attempt
- Any authority change → heal blocked, attempt marked failed
- `HealReceipt` includes `authority_proof: dict` showing frozen context preserved

### 5. E5 SEAL: Full SealedL2Artifact

**Adapter Function:** `apps_rg_l2_e5_seal()`

**E5 Schema Strategy (CRITICAL):**

1. **Populate ONLY existing SealedL2Artifact fields** from `agentic_core/runtime/contracts/sealed_l2_artifact.py`
2. **If v4-required fields are absent** from the generic contract → **STOP and classify as generic core schema gap**
3. **Do NOT create apps_rg-only sealed fields** that should be generic
4. Author-Gate required before any SealedL2Artifact contract modification

**Field Mapping (from EXISTING contract only):**

| SealedL2Artifact Field | Source | Required | Status |
|------------------------|--------|----------|--------|
| `request_id`, `run_id`, `app_id`, `trace_id` | E1 context | ✅ Yes | Existing |
| `execution_status` | E3 result | ✅ Yes | Existing |
| `generated_content` | E3 output | ✅ Yes | Existing |
| `generated_content_origin` | Constant | `Origin.MODEL_GENERATION` | Existing |
| `proposed_state_diff` | E3 parsed JSON | ✅ Yes | Existing |
| `state_diff_authorized` | Constant | `False` (L5/Exit decides) | Existing |
| `execution_timestamp` | E3 timestamp | ✅ Yes | Existing |
| `execution_duration_ms` | E3 telemetry | ✅ Yes | Existing |
| `sovereign_execution_receipt` | E3 provider receipt | ✅ Yes | Existing |
| `tenant_id` | E1 context | ✅ Yes | Existing |
| `sandbox_required` | E1 FEG | ✅ Yes | Existing |
| `egress_policy_ref` | E1 FEG | ✅ Yes | Existing |
| `allowed_tools` | E1 FEG | ✅ Yes | Existing |
| `allowed_models` | E1 FEG | ✅ Yes | Existing |
| `allowed_networks` | E1 FEG | ✅ Yes | Existing |
| `allowed_file_roots` | E1 FEG | ✅ Yes | Existing |
| `prompt_artifact_digest` | CPA | ✅ Yes | Existing |
| `compilation_hash` | E1 determinism | ✅ Yes | Existing |
| `schema_version` | Constant | `"W6.0"` | Existing |
| `otel_span_refs` | E3 telemetry | ⚠️ **VERIFY EXISTS** | Audit W1 |
| `audit_refs` | E1-E4 receipts | ⚠️ **VERIFY EXISTS** | Audit W1 |
| `evidence_refs` | CPA | ✅ Yes | Existing |
| `prompt_refs` | CPA lineage | ⚠️ **VERIFY EXISTS** | Audit W1 |
| `provider_receipts` | E3 attempts | ⚠️ **VERIFY EXISTS** | Audit W1 |
| `replay_manifest` | E1 bindings | ⚠️ **VERIFY EXISTS** | Audit W1 |
| `durable_commit_occurred` | Constant | `False` | Existing |
| `mutation_candidate_inert` | Constant | `True` (if state_diff non-empty) | Existing |

**W1 Audit Task:** Verify exact field names and types in SealedL2Artifact before any implementation.

---

## Contract Field Mapping Table

### Input: CompiledPromptArtifact → L2ExecutionPacket

| CPA Field | L2ExecutionPacket Field | Transform |
|-----------|------------------------|-----------|
| `request_id` | `packet_id` | Pass through |
| `run_id` | `run_id` | Pass through |
| `app_id` | `app_id` | Pass through |
| `trace_id` | `trace_id` | Pass through |
| `tenant_id` | `tenant_id` | Pass through |
| `system_preamble` | `work_order_inputs.task_spec.intent` | Extract intent |
| `user_instruction` | `work_order_inputs.task_spec.expected_output_contract` | Contract reference |
| `max_tokens` | `work_order_inputs.slo_slice_ms` | Map to timeout |
| `temperature` | `work_order_inputs.action_spec.version` | Version hint |
| `compilation_hash` | `replay_bindings.determinism.blueprint_hash` | Pass through |
| `evidence_digest` | `evidence_refs` | Map to tuple |
| `slot_lineage_map` | `prompt_refs` | Map to tuple |

### Output: L2ExecutionPacket → SealedL2Artifact

| L2ExecutionPacket Field | SealedL2Artifact Field | Transform |
|------------------------|------------------------|-----------|
| `frozen_execution_context` | `sandbox_*`, `allowed_*` | Unpack context |
| `approved_work_order.capability_scope` | `allowed_models`, `allowed_tools` | Pass through |
| `approved_work_order.budget_snapshot` | `execution_duration_ms` (check) | Validate within budget |
| `telemetry_bundle.latency_ms` | `execution_duration_ms` | Pass through |
| `telemetry_bundle.tokens_used` | (new field) | Add to SealedL2Artifact |
| `attempt_receipts` | `provider_receipts` | Map receipts |
| `heal_receipts` | (new field) | Add to SealedL2Artifact |
| `replay_bindings` | `replay_manifest` | Serialize manifest |

---

## apps_rg L2 Envelope Validation Checks

### New Gates in `apps_rg/runtime/bindings/l2_envelope_adapter.py`

| Gate | Phase | Check | On Violation |
|------|-------|-------|--------------|
| `L2_E1_FEG_FROZEN` | E1 | FEG fields immutable after prep | Raise `L2EnvelopeError` |
| `L2_E2_PROVIDER_REG` | E2 | Provider in registry | SealedRejectionPacket |
| `L2_E2_SANDBOX_MATCH` | E2 | Sandbox matches route | SealedRejectionPacket |
| `L2_E2_CAPABILITY_SCOPE` | E2 | Model in allowed list | SealedRejectionPacket |
| `L2_E2_BUDGET_OK` | E2 | Budget > 0 | SealedRejectionPacket |
| `L2_E2_NO_L4_PATH` | E2 | Write lock assertion true | Hard block, L5 notify |
| `L2_E3_GATEWAY_ONLY` | E3 | Only ProviderGateway.invoke() | RuntimeError if direct call |
| `L2_E4_SAME_AUTHORITY` | E4 | Heal doesn't change provider | HealReceipt with authority proof |
| `L2_E4_NO_POLICY_WIDEN` | E4 | Sandbox/capability unchanged | Reject heal, fail attempt |
| `L2_E5_FULL_FIELDS` | E5 | All required fields present | ValidationError |
| `L2_E5_MUTATION_INERT` | E5 | `state_diff_authorized=False` | Ensure L5/Exit controls write |
| `L2_E5_NO_DURABLE_COMMIT` | E5 | `durable_commit_occurred=False` | Ensure no direct L4 write |

---

## CI/Tests to Add or Update

### New Test File: `tests/_apps_contract/test_apps_rg_l2_envelope.py`

| Test Class | Coverage |
|------------|----------|
| `TestL2E1Prep` | FrozenExecutionContext fields, replay bindings, write lock assertion |
| `TestL2E2Validation` | Each validation rule (V1-V9), PASS and FAIL paths |
| `TestL2E3Execution` | ProviderGateway.invoke() usage, receipt capture, telemetry bundle |
| `TestL2E4Heal` | Allowed repairs (JSON fix, trim), disallowed (provider swap, policy widen) |
| `TestL2E5Seal` | Full SealedL2Artifact fields, mutation_inert, no_durable_commit |
| `TestL2EndToEnd` | Full E1→E5 pipeline with stub provider |

### Updated Tests

| Test File | Change |
|-----------|--------|
| `test_apps_rg_l2_steps_only_via_core_recipe.py` | Verify envelope doesn't bypass core recipe |
| `test_apps_rg_no_ad_hoc_prompt_model_call.py` | Verify ProviderGateway is only call path |

### CI Gates to Register

| Gate | File | Tier |
|------|------|------|
| `APPS-RG-L2-ENVELOPE` | `ops_scripts/ci/check_apps_rg_l2_envelope.py` | T2 |

---

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| A1 | `pytest tests/_apps_contract/ --collect-only` returns zero errors | Command run, exit 0 |
| A2 | E1 Prep produces valid `FrozenExecutionContext` | Unit test passes |
| A3 | E2 Validation produces `ApprovedWorkOrder` or `SealedRejectionPacket` | Unit test passes |
| A4 | E3 HOP uses only `ProviderGateway.invoke()` | Grep verification |
| A5 | E4 Heal only same-authority repairs | Unit test with mock failures |
| A6 | E5 Seal produces full `SealedL2Artifact` | Field coverage test |
| A7 | `mutation_candidate_inert=True` when state_diff present | Assertion in seal test |
| A8 | `durable_commit_occurred=False` in all cases | Assertion in seal test |
| A9 | No agentic_core modifications (unless proven gap) | Git diff check |
| A10 | No prompt assembly moved into L2 | Code review |
| A11 | No C0 retrieval in L2 | Code review |
| A12 | No L4 write in L2 | Code review, gate check |

### Negative Control Tests (MUST FAIL CORRECTLY)

| Test | Scenario | Expected Result |
|------|----------|-----------------|
| N1 | Missing provider registry | E2 validation fails before E3 with SealedRejectionPacket |
| N2 | Missing replay key | E2 validation fails before E3 (non-deterministic) |
| N3 | Missing prompt artifact digest | E2 validation fails before E3 |
| N4 | Direct provider call attempted | Grep-blocked or RuntimeError raised |
| N5 | E4 provider substitution attempted | Blocked, heal fails, authority proof shows mismatch |
| N6 | E5 durable_commit_occurred check | Always `False` in every test case |
| N7 | state_diff_authorized check | Always `False` until Exit/L5 sets it |
| N8 | Boundary violation - prompt assembly in L2 | Grep detection fails, code review blocks |
| N9 | Boundary violation - C0 retrieval in L2 | Grep detection fails, code review blocks |
| N10 | Boundary violation - L4 write in L2 | Gate fails, code review blocks |

---

## Rollback Plan

| Scenario | Action |
|----------|--------|
| E1-E5 envelope breaks live resume generation | Revert to Category A state: `git checkout HEAD -- apps_rg/runtime/bindings/l2_binding.py` |
| ProviderGateway.invoke() fails after changes | Emergency bypass: set `APPS_RG_L2_FORCE_STUB=1` |
| Core primitive missing (unexpected) | Document gap, pause plan, Author-Gate decision on core modification |
| Performance regression (>30s inference) | Profile E2 validation overhead, optimize or disable non-critical checks |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1-P3 | **SCHEMA/FIELD AUDIT** - Inspect exact fields in l2_v4_contracts.py, l2_v3_receipts.py, l2_phase_pipeline.py, SealedL2Artifact, CompiledPromptArtifact, l2_binding.py. Update contract mapping table to EXACT field names. No code changes. | ~600 | ✅ DONE | Exact field audit report with verified mappings |
| W2 | P1-P4 | E1 PREP adapter: FrozenExecutionContext | ~600 | ✅ DONE | Unit test: E1 produces valid PrepOutput |
| W3 | P1-P4 | E2 VALIDATION adapter: ApprovedWorkOrder | ~600 | ✅ DONE | Unit tests: PASS and FAIL paths |
| W4 | P1-P3 | E3 HOP integration: TelemetryBundle | ~400 | ✅ DONE | Receipt capture verified |
| W5 | P1-P4 | E4 HEAL adapter: Same-authority repair | ~500 | ✅ DONE | JSON repair tests pass, provider swap blocked |
| W6 | P1-P3 | E5 SEAL adapter: Full SealedL2Artifact | ~500 | ✅ DONE | All fields present, inert flags set |
| W7 | P1-P3 | End-to-end integration, CI gates | ~400 | ✅ DONE | Full pipeline test passes |
| W8 | P1-P3 | CI Hardening, AST-based scanning, zero failures | ~400 | ✅ DONE | 143 tests pass, 7/7 CI gate checks |

---

## Explicit HOP Ownership Statement

**HOP (High-Order Processing / Model Execution) remains in L2.3 / E3 phase.**

This plan does NOT:
- Move HOP to another layer
- Change ProviderGateway ownership
- Modify how models are invoked
- Change the HOP execution interface

This plan ADDS:
- Envelope around HOP (E1-E2 before, E4-E5 after)
- Validation before HOP execution
- Structured repair after HOP failures
- Complete sealing after HOP success

The core primitive `ProviderGateway.invoke()` remains the sole HOP execution path.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| E2 validation adds latency | Medium | Medium | Budget check is O(1), async if needed |
| E4 heal over-repairs | Low | High | Strict same-authority enforcement |
| SealedL2Artifact field explosion | Medium | Low | Use dataclass safe defaults |
| Core primitive missing | Low | High | Early audit phase (W1.P1) to verify |

---

## Definition of Done

| ID | DoD Item | Verification |
|----|----------|--------------|
| DoD-1 | E1-E5 envelope implemented in apps_rg | Unit tests for each phase |
| DoD-2 | Zero collect-only errors | `pytest tests/_apps_contract/ --collect-only` |
| DoD-3 | No agentic_core contamination | `git diff --name-only agentic_core/` empty |
| DoD-4 | HOP still uses ProviderGateway.invoke() | `grep gateway.invoke apps_rg/` |
| DoD-5 | Full SealedL2Artifact fields | Field coverage test passes |
| DoD-6 | Mutation inert, no durable commit | Assertions in E5 seal test |

---

## Related

- Parent: Category A patch `apps-rg-l2-critical-corrections-e7c4a1`
- Core contracts: `agentic_core/L2_execution/types/l2_v4_contracts.py`
- Core pipeline: `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py`
- SealedL2Artifact: `agentic_core/runtime/contracts/sealed_l2_artifact.py`

---

*End of Plan*

---

## CLOSEOUT RECEIPT

**Plan Status:** COMPLETED  
**Closeout Date:** 2026-05-13  
**Closeout Basis:** ACCEPTED

### Final W8 Gate Result

**APPS-RG-L2-V4-ENVELOPE CI Gate: PASS** ✅

| Check | Status |
|-------|--------|
| A. Full Envelope Tests | PASS (143 passed, 0 failed) |
| B. Collect-Only Proof | PASS (zero collection errors) |
| C. Provider Governance (AST-based) | PASS |
| D. Boundary Check (AST-based) | PASS |
| E. Mutation Law | PASS |
| F. Core Purity | PASS |
| G. Feature Flag Bridge | PASS |

### Validation Commands and Results

```bash
# Full envelope test suite
pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q
# Result: 143 passed, 0 failed, 0 errors

# Collect-only verification
pytest tests/_apps_contract/test_apps_rg_l2_envelope.py --collect-only
# Result: 143 tests discovered, zero collection errors

# CI gate execution
python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py
# Result: 7/7 checks passed, FINAL: PASS

# Grep checks for forbidden calls (PowerShell)
Select-String -Path apps_rg/runtime/bindings/l2_binding.py,apps_rg/runtime/bindings/l2_envelope_adapter.py `
  -Pattern '_invoke_local_vllm|_invoke_external_api|urllib|requests\.|httpx\.|openai\.|anthropic\.'
# Result: Only comment references, no executable forbidden calls

# Core purity check
git diff --stat agentic_core/
# Result: 1 file changed (pre-existing allowlisted file)
```

### Feature Flag Documentation

**APPS_RG_L2_USE_V4_ENVELOPE** environment variable controls envelope path:

- `APPS_RG_L2_USE_V4_ENVELOPE=1` → Enables governed E1→E2→E3→E4→E5 envelope path
- Default (unset/disabled) → Legacy path remains available

The v4 envelope is **feature-flagged and disabled by default**. Rollout/default enablement is a separate decision.

### Architecture Verification

| Requirement | Status |
|-------------|--------|
| E1→E2→E3→E4→E5 envelope exists | ✅ Verified |
| l2_execute_apps_rg enters v4 envelope through feature flag | ✅ Verified |
| Legacy path preserved when flag disabled | ✅ Verified |
| E3 uses ProviderGateway.invoke() | ✅ Verified |
| No private ProviderGateway calls | ✅ Verified |
| No direct urllib/requests/httpx/openai/anthropic calls | ✅ Verified |
| Boundary checks are AST-based (ignore comments/docstrings) | ✅ Verified |
| state_diff_authorized=False | ✅ Verified |
| is_uwg_write_authority=False | ✅ Verified |
| proposed_state_diff remains candidate-only | ✅ Verified |
| L2 does not write L4/UWG | ✅ Verified |
| No new agentic_core changes | ✅ Verified |

### Files Modified

**Implementation:**
- `apps_rg/runtime/bindings/l2_envelope_adapter.py` - E1-E5 envelope implementation
- `apps_rg/runtime/bindings/l2_binding.py` - W1 cleanup (ProviderGateway refactor)

**Tests:**
- `tests/_apps_contract/test_apps_rg_l2_envelope.py` - 143 contract tests

**CI Gate:**
- `ops_scripts/ci/check_apps_rg_l2_v4_envelope.py` - Hardened AST-based checks

### Core Purity Statement

No agentic_core modifications were made by this plan. The only `agentic_core/` diff is a pre-existing allowlisted file (`agentic_core/L6_learning/future_run_proposal_builder.py`) that was not touched by this plan.

### Final Statement

**apps_rg L2 v4 envelope adoption is complete as a feature-flagged governed runtime path.**

The governed envelope (E1 PREP → E2 VALIDATION → E3 HOP EXEC → E4 HEAL → E5 SEAL) is implemented and fully tested. The legacy execution path remains the default. Rollout and default enablement decisions are deferred to a separate operational decision.

---

*Closeout Receipt Version: 1.0*  
*Generated: 2026-05-13*
</thinking>



The comprehensive L2 v4 envelope adoption plan has been created.

## Summary

**Plan created:** `.windsurf/plans/apps-rg-l2-v4-envelope-adoption-e9f2b1.md`

### Key Elements

1. **Current vs Target State:** Detailed flow diagrams showing E1→E2→E3→E4→E5 envelope around existing HOP execution

2. **Core Enabling Gaps Assessment:**
   - ✅ **No core gaps identified**
   - All primitives exist in agentic_core
   - This is pure apps_rg wiring/adoption work

3. **Proposed New Files:**
   - `apps_rg/runtime/bindings/l2_envelope_adapter.py` - E1-E5 adapter
   - `apps_rg/config/l2_validation_rules.yaml` - E2 validation rules
   - `apps_rg/config/l2_e4_heal_profile.yaml` - E4 heal policies
   - `tests/_apps_contract/test_apps_rg_l2_envelope.py` - Contract tests

4. **Field Mapping Tables:**
   - CompiledPromptArtifact → L2ExecutionPacket
   - L2ExecutionPacket → SealedL2Artifact
   - Detailed contract field mappings

5. **Explicit HOP Ownership Statement:**
   - HOP remains in L2.3/E3
   - ProviderGateway.invoke() unchanged
   - Envelope adds governance around HOP, doesn't move it

6. **Wave Structure:**
   - W1: Audit (400 tokens)
   - W2-W6: E1-E5 adapters (2500 tokens total)
   - W7: Integration + CI (400 tokens)

7. **Acceptance Criteria:**
   - Zero collect-only errors
   - No agentic_core contamination
   - Full SealedL2Artifact fields
   - Mutation inert, no durable commit

8. **Rollback Plan:**
   - Git revert to Category A state
   - Emergency stub bypass
   - Core gap Author-Gate if needed

The plan is ready for review and potential wave-by-wave implementation.

---

## ADG_HOTSPOT_REPORT

> RETROACTIVE_EVIDENCE_PATCH — added 2026-05-14 per GAP-C7 remediation batch 2.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05122026_1828.sqlite

| Rank | File | Archetype | Layer | Fan-In | Surfaces | Wave |
|------|------|-----------|-------|--------|----------|------|
| 1 | `agentic_core/L2_execution/l2_package_driven_executor.py` | ORCHESTRATOR | L2 | high | Execution Surface, State Surface | W1-W5 (read-only reference) |
| 2 | `apps_rg/runtime/bindings/l2_binding.py` | CENTRAL_DEPENDENCY | L2/app | medium | Execution Surface, Write Surface | W3-W5 |
| 3 | `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` | ORCHESTRATOR | L2 | medium | Execution Surface | W1 (reference adapter pattern) |

---

## ADG_GRAPH_LAYER_EVIDENCE

> RETROACTIVE_EVIDENCE_PATCH — added 2026-05-14 per GAP-C7 remediation batch 2.

- **MV**: `mv_hotspot_centrality` — `agentic_core/L2_execution/l2_package_driven_executor.py` is high-fan-in ORCHESTRATOR; this plan adopts its E1→E5 envelope pattern for apps_rg wiring
- **MV**: `mv_dependency_cone_risk` — `apps_rg/runtime/bindings/l2_binding.py` sits at the apps_rg/core boundary; cone risk from L2 contract adoption propagates to all downstream plan phases
- **MV**: `mv_graph_reverse_dependency_hotspots` — `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` is a reverse-dependency hotspot; the adapter pattern (E1 Prep → E5 Seal) used here fans out to multiple app binding consumers
- **Semantic edge**: `apps_rg/runtime/bindings/l2_binding.py` →`reads_from`→ `agentic_core.L2_execution.types.l2_v4_contracts` (WorkOrderInputs, FrozenExecutionContext); `l2_binding` →`writes_to`→ `SealedL2Artifact` (E5 seal output)
- **Surface references**: Execution Surface (E1→E5 phase pipeline, HOP execution at E3), Write Surface (SealedL2Artifact output, mutation-inert commit discipline), State Surface (FrozenExecutionContext immutability contract)
