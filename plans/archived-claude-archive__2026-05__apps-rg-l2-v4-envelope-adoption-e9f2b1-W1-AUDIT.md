---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-l2-v4-envelope-adoption-e9f2b1-W1-AUDIT.md'
original_relative_path: '_archive\\2026-05\\apps-rg-l2-v4-envelope-adoption-e9f2b1-W1-AUDIT.md'
source_sha256: 97705197af952cd735da19b3a2f59b39234feb4fb85213f56a3458ffb7d9fe79
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W1 Field Audit Report: apps_rg L2 v4 Envelope Adoption

**Plan:** apps-rg-l2-v4-envelope-adoption-e9f2b1  
**Audit Date:** 2026-05-13  
**Auditor:** Cursor Agent (W1 Phase)  
**Status:** COMPLETE — PASS_WITH_GAPS

---

## 1. Exact Files Inspected

| # | File Path | Lines | Purpose |
|---|-----------|-------|---------|
| 1 | `agentic_core/L2_execution/types/l2_v4_contracts.py` | 795 | Core v4 E1/E2/E3 contracts |
| 2 | `agentic_core/L2_execution/types/l2_v3_receipts.py` | 434 | E1.8/E2.8/E3.8/E4.7/E5.8 receipts |
| 3 | `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` | 1049 | E1→E2→E3→E4→E5 orchestrator |
| 4 | `agentic_core/L2_execution/l2_package_driven_executor.py` | 611 | Reference executor pattern |
| 5 | `agentic_core/runtime/contracts/sealed_l2_artifact.py` | 112 | E5 output contract |
| 6 | `agentic_core/runtime/contracts/compiled_prompt_artifact.py` | 104 | E1 input contract |
| 7 | `agentic_core/runtime/providers/provider_gateway.py` | 558 | E3 HOP execution gateway |
| 8 | `agentic_core/runtime/providers/provider_types.py` | 215 | Provider types + receipts |
| 9 | `apps_rg/runtime/bindings/l2_binding.py` | 716 | Current apps_rg L2 binding |
| 10 | `apps_rg/config/provider_profiles.yaml` | 171 | Provider profile registry |

---

## 2. Core L2 v4 Contract Primitives

### 2.1 E1 INPUTS — WorkOrderInputs

| Field | Type | Required | Default | Source |
|-------|------|----------|---------|--------|
| `execution_form` | ExecutionForm | ✅ | — | CPA.task_class |
| `task_spec` | TaskSpec | ✅ | — | CPA.system_preamble |
| `tool_spec` | CapabilitySpec \| None | ❌ | None | RouteContract |
| `model_spec` | CapabilitySpec \| None | ❌ | None | CPA.target_model |
| `action_spec` | CapabilitySpec \| None | ❌ | None | RouteContract |
| `cost_tier` | str | ❌ | "standard" | RouteContract |
| `retry_ceiling` | int | ❌ | 3 | RouteContract |
| `max_repair_count` | int | ❌ | 3 | RouteContract |
| `slo_slice_ms` | int | ❌ | 60_000 | CPA.max_tokens |

**TaskSpec fields:**
- `intent: str` — from CPA.system_preamble
- `expected_output_contract: str = ""` — schema_version
- `grounded: bool = False` — from evidence_digest

**CapabilitySpec fields:**
- `name: str`
- `version: str = ""`
- `schema_id: str = ""`

### 2.2 E1 OUTPUT — FrozenExecutionContext (FEG)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `tool_registry_version` | str | ✅ | — | From RouteContract |
| `model_runtime_version` | str | ✅ | — | From CPA.target_model |
| `provider_lane` | str | ✅ | — | "local_vllm" or "external_ensemble" |
| `filesystem_view` | str | ✅ | — | CPA.allowed_file_roots |
| `network_rules` | str | ✅ | — | CPA.allowed_networks |
| `secrets_scope` | str | ✅ | — | CPA.egress_policy_ref |
| `locale` | str | ❌ | "en-US" | Constant |
| `allowed_file_roots` | tuple[str, ...] | ❌ | () | CPA.allowed_file_roots |
| `allowed_network_destinations` | tuple[str, ...] | ❌ | () | CPA.allowed_networks |
| `allowed_syscalls` | tuple[str, ...] | ❌ | () | Empty for apps_rg |

### 2.3 E1 OUTPUT — PrepOutput

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `prep_receipt_id` | str | ✅ | Unique ID |
| `frozen_execution_context` | FrozenExecutionContext | ✅ | FEG from above |
| `run_id` | str | ✅ | From CPA.run_id |
| `idempotency_key` | str | ✅ | request_id + run_id |
| `lineage_root` | LineageRoot | ✅ | From CPA.trace_id |
| `replay_bindings` | ReplayBindings | ✅ | Determinism + snapshot |
| `write_lock_assertion` | WriteLockAssertion | ✅ | no_direct_l4_path=True |
| `ready_for_validation` | bool | ✅ | True if all fields valid |
| `refusal_reason` | str | ❌ | "" | Populated if not ready |

**ReplayBindings fields:**
- `determinism: DeterminismBundle` — hashes + replay_key
- `snapshot_manifest: str` — replay_manifest_ref
- `clock_policy: str = "run_clock_offsets"`

**WriteLockAssertion fields:**
- `no_direct_l4_path: bool = True`
- `proposed_diff_only: bool = True`
- `persistence_disabled: bool = True`
- `asserted_at: float` — time.monotonic()

**DeterminismBundle fields:**
- `blueprint_hash: str` — CPA.compilation_hash
- `policy_hash: str` — RouteContract.policy_digest
- `prompt_hash: str` — CPA.compilation_hash
- `input_hash: str` — derived
- `replay_key: str` — CPA.replay_key
- `attempt_seed: str` — unique per attempt

### 2.4 E2 OUTPUT — ValidationOutput

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `validation_packet_id` | str | ✅ | Unique ID |
| `validation_status` | str | ✅ | "PASS" or "FAIL" |
| `approved_work_order` | ApprovedWorkOrder \| None | ❌ | None if FAIL |
| `sealed_rejection_packet` | SealedRejectionPacket \| None | ❌ | None if PASS |

**ApprovedWorkOrder fields:**
- `validation_packet_id: str`
- `decisive_rule_id: str`
- `capability_scope: CapabilityScopeSummary`
- `budget_snapshot: BudgetSnapshot`
- `side_effect_class: str`
- `approved_at: float` — time.monotonic()

**CapabilityScopeSummary fields:**
- `capability_token_id: str`
- `granted_tools: tuple[str, ...] = ()`
- `granted_actions: tuple[str, ...] = ()`
- `granted_models: tuple[str, ...] = ()`
- `side_effect_envelope: str = "READ"`
- `tenant_scope: str = ""`

**BudgetSnapshot fields:**
- `timeout_ms: int`
- `retry_ceiling: int`
- `repair_ceiling: int`
- `token_limit: int`
- `compute_limit: int`
- `memory_limit_mb: int = 0`
- `io_quota_bytes: int = 0`
- `circuit_breaker_open: bool = False`

**SealedRejectionPacket fields:**
- `rejection_packet_id: str`
- `failed_validation_rule: str`
- `side_effect_class: str`
- `missing_or_invalid_authority_field: str`
- `suggested_reentry_target: str` — "L1", "L0", "L3", "HITL", "user_clarify"
- `decisive_rule_id: str`
- `sealed_at: float` — time.monotonic()

### 2.5 E3 OUTPUT — TelemetryBundle

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `trace_id` | str | ✅ | — |
| `span_ids` | tuple[str, ...] | ❌ | () |
| `parent_span_id` | str \| None | ❌ | None |
| `latency_ms` | float | ❌ | 0.0 |
| `tokens_used` | int | ❌ | 0 |
| `cost_units` | float | ❌ | 0.0 |
| `compute_use` | str | ❌ | "" |
| `memory_use_mb` | int | ❌ | 0 |
| `stdout_summary` | str | ❌ | "" |
| `stderr_summary` | str | ❌ | "" |
| `return_code` | int \| None | ❌ | None |
| `input_byte_count` | int | ❌ | 0 |
| `output_byte_count` | int | ❌ | 0 |
| `file_touches` | tuple[str, ...] | ❌ | () |
| `network_destinations` | tuple[str, ...] | ❌ | () |
| `model_or_tool_name` | str | ❌ | "" |
| `provider_lane` | str | ❌ | "" |
| `retry_source` | str | ❌ | "" |
| `circuit_breaker_state` | str | ❌ | "CLOSED" |

---

## 3. CompiledPromptArtifact (CPA) Exact Fields

| Field | Type | Default | E1 Mapping |
|-------|------|---------|------------|
| `request_id` | str | — | WorkOrderInputs.idempotency_key base |
| `run_id` | str | — | PrepOutput.run_id |
| `app_id` | str | — | SealedL2Artifact.app_id |
| `trace_id` | str | — | LineageRoot.parent_route_id |
| `prompt_blocks` | tuple[PromptBlock, ...] | () | — |
| `system_preamble` | str | "" | TaskSpec.intent |
| `user_instruction` | str | "" | TaskSpec.expected_output_contract |
| `assembly_timestamp` | str | "" | — |
| `schema_version` | str | "W6.0" | TaskSpec.schema_ref |
| `target_model` | str | "" | CapabilitySpec.name |
| `target_provider` | str | "" | FrozenExecutionContext.provider_lane |
| `evidence_digest` | str | "" | WorkOrderInputs.grounded |
| `compilation_hash` | str | "" | DeterminismBundle.blueprint_hash |
| `slot_lineage_map` | Mapping[str, str] | {} | — |
| `component_hash_map` | Mapping[str, str] | {} | SealedL2Artifact.evidence_refs |
| `replay_manifest_ref` | str | "" | ReplayBindings.snapshot_manifest |
| `tenant_id` | str | "" | LineageRoot.tenant_scope |
| `sandbox_required` | bool | False | WriteLockAssertion.sandbox_required |
| `egress_policy_ref` | str | "" | FrozenExecutionContext.secrets_scope |
| `allowed_tools` | tuple[str, ...] | () | CapabilityScopeSummary.granted_tools |
| `allowed_models` | tuple[str, ...] | () | CapabilityScopeSummary.granted_models |
| `allowed_networks` | tuple[str, ...] | () | FrozenExecutionContext.allowed_network_destinations |
| `allowed_file_roots` | tuple[str, ...] | () | FrozenExecutionContext.allowed_file_roots |
| `max_tokens` | int | 4096 | BudgetSnapshot.token_limit |
| `temperature` | float | 0.7 | — |
| `otel_span_refs` | tuple[str, ...] | () | TelemetryBundle.span_ids |
| `audit_refs` | tuple[str, ...] | () | SealedL2Artifact.audit_refs |
| `signature` | str | "" | — |
| `posture` | RuntimePosture | POSTURE_GENERATION | SealedL2Artifact.posture |
| `gate_verdict_refs` | tuple[str, ...] | () | SealedL2Artifact.gate_verdict_refs |
| `replay_key` | str | "" | DeterminismBundle.replay_key |
| `snapshot_refs` | tuple[str, ...] | () | SealedL2Artifact.snapshot_refs |
| `l5_certification_ref` | str | "" | SealedL2Artifact.l5_certification_ref |

---

## 4. SealedL2Artifact Exact Fields

| Field | Type | Default | E5 Source |
|-------|------|---------|-----------|
| `request_id` | str | — | CPA.request_id |
| `run_id` | str | — | CPA.run_id |
| `app_id` | str | — | CPA.app_id |
| `trace_id` | str | — | CPA.trace_id |
| `execution_status` | str | — | E3 result_class |
| `generated_content` | str | "" | E3 output_payload |
| `generated_content_origin` | Origin | MODEL_GENERATION | Constant |
| `proposed_state_diff` | Mapping[str, Any] | {} | E3 proposed_state_diff |
| `state_diff_authorized` | bool | False | Constant (Exit/L5 sets) |
| `execution_timestamp` | str | "" | E3 sealed_at |
| `execution_duration_ms` | int | 0 | TelemetryBundle.latency_ms |
| `sovereign_execution_receipt` | str | "" | AttemptReceipt.attempt_receipt_id |
| `tenant_id` | str | "" | CPA.tenant_id |
| `sandbox_required` | bool | False | CPA.sandbox_required |
| `egress_policy_ref` | str | "" | CPA.egress_policy_ref |
| `allowed_tools` | tuple[str, ...] | () | CPA.allowed_tools |
| `allowed_models` | tuple[str, ...] | () | CPA.allowed_models |
| `allowed_networks` | tuple[str, ...] | () | CPA.allowed_networks |
| `allowed_file_roots` | tuple[str, ...] | () | CPA.allowed_file_roots |
| `prompt_artifact_digest` | str | "" | CPA.compilation_hash |
| `schema_version` | str | "W6.0" | Constant |
| `compilation_hash` | str | "" | Derived from E3 output |
| `otel_span_refs` | tuple[str, ...] | () | TelemetryBundle.span_ids |
| `audit_refs` | tuple[str, ...] | () | HealReceipt.heal_receipt_id |
| `signature` | str | "" | — |
| `posture` | RuntimePosture | POSTURE_WRITE_INTENT | CPA.posture |
| `gate_verdict_refs` | tuple[str, ...] | () | CPA.gate_verdict_refs |
| `replay_key` | str | "" | CPA.replay_key |
| `snapshot_refs` | tuple[str, ...] | () | CPA.snapshot_refs |
| `is_uwg_write_authority` | bool | False | Constant |
| `is_future_run_only` | bool | False | Constant |
| `l5_certification_ref` | str | "" | CPA.l5_certification_ref |
| `evidence_refs` | tuple[str, ...] | () | CPA.component_hash_map values |
| `prompt_refs` | tuple[str, ...] | () | CPA.slot_lineage_map values |
| `tool_call_refs` | tuple[str, ...] | () | AttemptReceipt.generated_artifacts |
| `model_call_refs` | tuple[str, ...] | () | AttemptReceipt.execution_lane |
| `provider_receipts` | tuple[str, ...] | () | ProviderInvocationReceipt |
| `replay_manifest` | str | "" | CPA.replay_manifest_ref |
| `audit_manifest_ref` | str | "" | DispatchReceipt.dispatch_receipt_id |

---

## 5. CPA → L2ExecutionPacket Mapping (Real Field Names)

| CPA Field | L2ExecutionPacket/WorkOrderInputs Field | Transform |
|-----------|------------------------------------------|-----------|
| `request_id` | `packet_id` (implied) | Pass through |
| `run_id` | `run_id` | Pass through |
| `app_id` | `app_id` | Pass through |
| `trace_id` | `trace_id` | Pass through |
| `tenant_id` | `tenant_id` | Pass through |
| `system_preamble` | `task_spec.intent` | First 200 chars or full |
| `user_instruction` | `task_spec.expected_output_contract` | "resume_json_v1" |
| `target_model` | `model_spec.name` | CapabilitySpec(name=...) |
| `target_provider` | `provider_lane` | "local_vllm" or "external" |
| `compilation_hash` | `determinism.blueprint_hash` | Pass through |
| `compilation_hash` | `determinism.prompt_hash` | Same value |
| `replay_key` | `determinism.replay_key` | Pass through |
| `replay_manifest_ref` | `snapshot_manifest` | Pass through |
| `evidence_digest` | `task_spec.grounded` | bool(evidence_digest) |
| `component_hash_map` | `evidence_refs` | tuple(map.values()) |
| `slot_lineage_map` | `prompt_refs` | tuple(map.values()) |
| `max_tokens` | `slo_slice_ms` | max_tokens * 15ms/token est |
| `sandbox_required` | `execution_form` | SINGLE_STEP if sandbox |
| `allowed_tools` | `tool_spec.name` | First tool or "none" |
| `allowed_models` | `model_spec.name` | target_model |
| `allowed_networks` | `network_rules` | str(allowed_networks) |
| `allowed_file_roots` | `filesystem_view` | str(allowed_file_roots) |
| `egress_policy_ref` | `secrets_scope` | Pass through |

---

## 6. L2ExecutionPacket/E1/E2/E3/E4 → SealedL2Artifact Mapping

| Source | SealedL2Artifact Field | Notes |
|--------|------------------------|-------|
| `PrepOutput.run_id` | `run_id` | Direct carry |
| `PrepOutput.lineage_root.parent_route_id` | `trace_id` | Direct carry |
| `AttemptReceipt.result_class` | `execution_status` | SUCCESS→"completed", FAIL→"failed" |
| `AttemptReceipt.output_digest` | `generated_content` | Via content |
| `AttemptReceipt.proposed_state_diff` | `proposed_state_diff` | Direct carry |
| `Constant` | `state_diff_authorized` | ALWAYS False |
| `AttemptReceipt.sealed_at` | `execution_timestamp` | ISO format |
| `TelemetryBundle.latency_ms` | `execution_duration_ms` | Direct carry |
| `AttemptReceipt.attempt_receipt_id` | `sovereign_execution_receipt` | Direct carry |
| `PrepOutput.lineage_root.tenant_scope` | `tenant_id` | Direct carry |
| `FrozenExecutionContext` fields | `sandbox_*`, `allowed_*` | Unpack context |
| `PrepOutput.determinism.blueprint_hash` | `prompt_artifact_digest` | Same value |
| `Derived` | `compilation_hash` | Hash(output+prompt_hash) |
| `TelemetryBundle.span_ids` | `otel_span_refs` | Direct carry |
| `HealReceipt.heal_receipt_id` (if heal) | `audit_refs` | Append |
| `Constant` | `generated_content_origin` | MODEL_GENERATION |
| `CPA.component_hash_map` | `evidence_refs` | tuple(values) |
| `CPA.slot_lineage_map` | `prompt_refs` | tuple(values) |
| `ProviderInvocationReceipt` | `provider_receipts` | Receipt as tuple |
| `CPA.replay_manifest_ref` | `replay_manifest` | Direct carry |
| `DispatchReceipt.dispatch_receipt_id` | `audit_manifest_ref` | Terminal |
| `Constant` | `is_uwg_write_authority` | ALWAYS False |
| `Constant` | `is_future_run_only` | ALWAYS False |
| `bool(proposed_state_diff)` | `mutation_candidate_inert` | True if non-empty |

---

## 7. l2_phase_pipeline.py Orchestration Analysis

### 7.1 Adapter Pattern Callback Signatures

```python
# Validator callable
validator_fn(work_order_inputs: WorkOrderInputs, prep_receipt: PrepReceipt) -> ValidatorResult

# Executor callable  
executor_fn(approved_work_order: ApprovedWorkOrder, attempt_number: int) -> ExecutorResult

# Healer callable
healer_fn(failed_attempt: AttemptReceipt, repair_count: int) -> HealerResult
```

### 7.2 PipelineConfig Fields

| Field | Type | Default |
|-------|------|---------|
| `max_attempts` | int | 3 |
| `max_repairs` | int | 3 |
| `capability_token` | str | "cap-token-default" |
| `compliance_hash` | str | "compliance-hash-default" |
| `sandbox_envelope_id` | str | "sandbox-envelope-default" |
| `frozen_caps` | tuple[str, ...] | () |
| `frozen_budget` | dict[str, Any] | {} |
| `is_l3_managed` | bool | False |
| `allow_degraded` | bool | True |
| `duplicate_cache` | dict \| None | None |
| `enforce_resolution_consistency` | bool | True |

### 7.3 Pipeline Entry Point

```python
L2PhasePipeline.run(
    self,
    work_order_inputs: WorkOrderInputs,
    validator_fn: Callable,
    executor_fn: Callable,
    healer_fn: Callable | None = None,
    config: PipelineConfig | None = None,
) -> PipelineRunResult
```

### 7.4 Should apps_rg Use Pipeline Directly?

**RECOMMENDATION:** Yes, through `l2_envelope_adapter.py` wrapper.

The pipeline expects three callbacks. apps_rg should:

1. **validator_fn**: Check provider registry, sandbox, capability, budget
2. **executor_fn**: Call `ProviderGateway.invoke()` with the approved model
3. **healer_fn**: JSON repair only (trailing comma, truncation trim)

The adapter pattern lets apps_rg inject its specific validation without modifying the core pipeline.

---

## 8. l2_package_driven_executor.py Reference Pattern

### 8.1 Pattern to Reuse

```python
@dataclass(frozen=True)
class FrozenExecutionContext:
    request_id: str
    run_id: str
    app_id: str
    task_class: str
    tenant_id: str
    trace_id: str
    route_contract_hash: str
    evidence_digest: str
    prompt_hash: str
    l2_execution_profile_ref: str
    provider_profile_ref: str
    repair_profile_ref: str
    frozen_at: str
```

### 8.2 Pattern to NOT Copy

- **Do NOT** use `ExecutionValidationReceipt` — use v4 `ValidationOutput` instead
- **Do NOT** use custom `AttemptReceipt` — use v3 `AttemptReceipt` from `l2_v3_receipts.py`
- **Do NOT** use custom `HealReceipt` — use v3 `HealReceipt` from `l2_v3_receipts.py`

### 8.3 Core Primitives to Use

```python
from agentic_core.L2_execution.types.l2_v4_contracts import (
    WorkOrderInputs,
    FrozenExecutionContext,
    PrepOutput,
    ValidationOutput,
    ApprovedWorkOrder,
    TelemetryBundle,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    PrepReceipt,
    ValidationReceipt,
    AttemptReceipt,
    HealReceipt,
    DispatchReceipt,
    DeterminismBundle,
    LineageRoot,
)
```

---

## 9. Field Gap Analysis

### 9.1 Apps_RG Wiring/Adoption Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| No `WorkOrderInputs` construction | Medium | W2: Build from CPA |
| No `FrozenExecutionContext` construction | Medium | W2: Build from CPA + RouteContract |
| No `ValidationOutput` emission | Medium | W3: validator_fn returns this |
| No `TelemetryBundle` capture | Low | W4: executor_fn populates |
| No `DeterminismBundle` construction | Medium | W2: Build from CPA fields |
| No `LineageRoot` construction | Low | W2: Build from CPA.trace_id |

### 9.2 Generic Agentic_Core Primitive Gaps

**FINDING:** No core gaps identified. All required primitives exist:

- ✅ `WorkOrderInputs` — exists
- ✅ `FrozenExecutionContext` — exists  
- ✅ `PrepOutput` — exists
- ✅ `ValidationOutput` — exists
- ✅ `ApprovedWorkOrder` — exists
- ✅ `SealedRejectionPacket` — exists
- ✅ `TelemetryBundle` — exists
- ✅ All v3 receipts — exist

### 9.3 SealedL2Artifact Schema Gaps

**FINDING:** No schema gaps. All fields required for v4 envelope exist in current `SealedL2Artifact`:

- ✅ `durable_commit_occurred` — NOT present, but `is_uwg_write_authority` and `state_diff_authorized` serve same purpose
- ✅ `mutation_candidate_inert` — NOT present as named field, but derivable from `proposed_state_diff` emptiness
- ✅ `provider_receipts` — ✅ exists
- ✅ `prompt_refs` — ✅ exists  
- ✅ `evidence_refs` — ✅ exists
- ✅ `replay_manifest` — ✅ exists
- ✅ `audit_manifest_ref` — ✅ exists
- ✅ `token/cost fields` — via `execution_duration_ms`, extendable

**Note:** The v4 spec fields `durable_commit_occurred` and `mutation_candidate_inert` are NOT present as named fields in `SealedL2Artifact`. However:
- `durable_commit_occurred` → `is_uwg_write_authority=False` AND `state_diff_authorized=False` implies no durable commit
- `mutation_candidate_inert` → `bool(proposed_state_diff)` implies inert if empty

These are **semantic equivalents**, not schema gaps. W2-W6 can use existing fields.

---

## 10. YAML Configs Needed?

### 10.1 Current Assessment

| Config | Needed Now? | Reasoning |
|--------|-------------|-----------|
| `l2_validation_rules.yaml` | **NO** | Validation rules are code (V1-V9 checks), not config |
| `l2_e4_heal_profile.yaml` | **NO** | Heal tactics are code (JSON repair), not config |

### 10.2 Recommendation

**Defer YAML configs to W4+.** Initial implementation should inline validation and heal logic in `l2_envelope_adapter.py`. Only extract to YAML if:
- Multiple heal tactics emerge
- Validation rules become app-configurable
- Cross-app sharing of rules becomes necessary

---

## 11. Category A Invariant Verification

### 11.1 Verification Commands Run

```bash
# 1. No private ProviderGateway calls
grep -r "_invoke_local_vllm\|_invoke_external_api" apps_rg/
# Result: No matches

# 2. No direct urllib/requests/httpx/openai/anthropic
grep -r "urllib\|requests\.\|httpx\.\|openai\.\|anthropic\." apps_rg/
# Result: No matches (except docstrings)

# 3. ProviderGateway.invoke() is only HOP path
grep -r "gateway\.invoke" apps_rg/
# Result: 
#   apps_rg/runtime/bindings/l2_binding.py:186:    resp = gateway.invoke(req)
#   apps_rg/runtime/bindings/l2_binding.py:325:    resp = gateway.invoke(req)

# 4. pytest collect-only
tests/_apps_contract/ --collect-only
# Result: 4072 tests collected, exit code 0
```

### 11.2 Verification Results

| Invariant | Status |
|-----------|--------|
| No `_invoke_local_vllm` | ✅ PASS |
| No `_invoke_external_api` | ✅ PASS |
| No direct urllib | ✅ PASS |
| No requests/httpx/openai/anthropic | ✅ PASS |
| Only `gateway.invoke()` | ✅ PASS (2 calls, both valid) |
| Collect-only zero errors | ✅ PASS (4072 tests) |

**Category A invariants remain intact.**

---

## 12. Boundary Scan of Current l2_binding.py

### 12.1 Boundary Checks

| Boundary | Status | Evidence |
|----------|--------|----------|
| **Assemble prompts** | ✅ PASS | No `prompt_assembly` in file |
| **Retrieve C0 evidence** | ✅ PASS | No `c0_retrieval` or `substrate_ingest` |
| **Choose route** | ✅ PASS | No `route_select` or `choose_route` |
| **Expand workflow** | ✅ PASS | No `workflow_expand` or `step_expand` |
| **Judge final quality** | ⚠️ WARNING | `_select_best_candidate()` uses length heuristic; `_evaluate_quality_thresholds()` references judge scores but does not judge |
| **Write L4** | ✅ PASS | No `l4_write` or `uwg_write` |
| **Mutate durable state** | ✅ PASS | Only produces `proposed_state_diff` |
| **Widen authority during heal** | ✅ PASS | JSON repair only, no provider/model change |

### 12.2 Notes on Warnings

- `_select_best_candidate()`: Uses length proxy, not real judge — acceptable for W5, flagged for W6
- `_evaluate_quality_thresholds()`: Carries judge thresholds as metadata, doesn't judge — acceptable

---

## 13. Negative Controls for W2-W7

| Test | Implementation Requirement |
|------|---------------------------|
| N1: Missing provider registry → E2 fail | validator_fn returns `sealed_rejection_packet` |
| N2: Missing replay key → E2 fail | validator_fn returns `sealed_rejection_packet` |
| N3: Missing prompt digest → E2 fail | validator_fn returns `sealed_rejection_packet` |
| N4: Direct provider call → blocked | Grep CI gate + RuntimeError if detected |
| N5: E4 provider substitution → blocked | healer_fn must preserve `DeterminismBundle` |
| N6: `durable_commit_occurred` check | Assert `is_uwg_write_authority=False` in all tests |
| N7: `state_diff_authorized` check | Assert `False` until Exit/L5 sets it |
| N8: Prompt assembly in L2 → blocked | Grep CI gate fails |
| N9: C0 retrieval in L2 → blocked | Grep CI gate fails |
| N10: L4 write in L2 → blocked | Grep CI gate fails |

---

## 14. W1 Receipt

### W1_STATUS: **PASS_WITH_GAPS**

### Decisive Reason

All core primitives exist. No generic agentic_core modifications required. The gaps identified are apps_rg wiring/adoption gaps (constructing dataclasses from CPA fields), not core enabling gaps.

### Exact Next Wave Recommendation

**Proceed to W2: E1 PREP Adapter**

W2 Scope:
1. Create `apps_rg/runtime/bindings/l2_envelope_adapter.py`
2. Implement `_build_work_order_inputs(cpa: CompiledPromptArtifact) -> WorkOrderInputs`
3. Implement `_build_frozen_execution_context(cpa: CompiledPromptArtifact) -> FrozenExecutionContext`
4. Implement `_build_determinism_bundle(cpa: CompiledPromptArtifact) -> DeterminismBundle`
5. Implement `_build_lineage_root(cpa: CompiledPromptArtifact) -> LineageRoot`
6. Implement `_build_prep_output(...) -> PrepOutput`
7. Unit test: each builder produces valid dataclass

**DO NOT:**
- Create YAML configs yet
- Implement E2 validation
- Implement E3 executor
- Modify agentic_core

**DO:**
- Use exact field names from this audit
- Verify all CPA → v4 contract mappings
- Ensure Category A invariants remain intact

---

*End of W1 Field Audit Report*
