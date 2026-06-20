---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-l2-v4-envelope-adoption-e9f2b1-W2-REPORT.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-l2-v4-envelope-adoption-e9f2b1-W2-REPORT.md'
source_sha256: 2c400ba3d68991513e1aa5afbd62fbd6f2a55f89c654cf79ce79f8ae60d7e9bc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W2 Execution Report: E1 PREP Adapter

**Plan:** apps-rg-l2-v4-envelope-adoption-e9f2b1  
**Phase:** W2 — E1 PREP Adapter Only  
**Date:** 2026-05-13  
**Status:** COMPLETE — **PASS**

---

## 1. Files Changed

| File | Change Type | Lines | Purpose |
|------|-------------|-------|---------|
| `apps_rg/runtime/bindings/l2_envelope_adapter.py` | **NEW** | 275 | E1 PREP builder functions |
| `tests/_apps_contract/test_apps_rg_l2_envelope.py` | **NEW** | 396 | 22 E1-specific tests |

**Files NOT Changed (per W2 scope):**
- ❌ `agentic_core/` — no modifications
- ❌ `apps_rg/runtime/bindings/l2_binding.py` — no modifications
- ❌ `provider_gateway.py` — no modifications
- ❌ `sealed_l2_artifact.py` — no modifications
- ❌ `compiled_prompt_artifact.py` — no modifications
- ❌ `provider_profiles.yaml` — no modifications
- ❌ No YAML configs created

---

## 2. Exact E1 Builder Functions Implemented

### 2.1 `_build_work_order_inputs(cpa) -> WorkOrderInputs`

| Field | Source | Transform |
|-------|--------|-----------|
| `execution_form` | CPA posture | `ExecutionForm.SINGLE_STEP` |
| `task_spec.intent` | `cpa.system_preamble` | First 500 chars |
| `task_spec.expected_output_contract` | `cpa.schema_version` | Pass through |
| `task_spec.grounded` | `cpa.evidence_digest` | `bool()` |
| `model_spec.name` | `cpa.target_model` | CapabilitySpec wrapper |
| `tool_spec` | `cpa.allowed_tools` | First tool if present |
| `slo_slice_ms` | `cpa.max_tokens` | `max_tokens * 15` (15ms/token) |
| `retry_ceiling` | Default | 3 |
| `max_repair_count` | Default | 3 |

### 2.2 `_build_frozen_execution_context(cpa) -> FrozenExecutionContext`

| Field | Source | Default |
|-------|--------|---------|
| `model_runtime_version` | `cpa.target_model` | "unknown" |
| `provider_lane` | `cpa.target_provider` | "local_vllm" |
| `filesystem_view` | `cpa.allowed_file_roots` | "()" |
| `network_rules` | `cpa.allowed_networks` | "()" |
| `secrets_scope` | `cpa.egress_policy_ref` | "" |
| `allowed_file_roots` | `cpa.allowed_file_roots` | Pass through |
| `allowed_network_destinations` | `cpa.allowed_networks` | Pass through |
| `allowed_syscalls` | — | `()` (empty) |
| `locale` | — | "en-US" |

### 2.3 `_build_determinism_bundle(cpa) -> DeterminismBundle`

| Field | Source | Transform |
|-------|--------|-----------|
| `blueprint_hash` | `cpa.compilation_hash` | Pass through |
| `prompt_hash` | `cpa.compilation_hash` | Pass through |
| `policy_hash` | `cpa.l5_certification_ref` | Fallback: `cpa.signature` |
| `input_hash` | Stable CPA identity | SHA-256 of `req:run:app:trace:tenant` |
| `replay_key` | `cpa.replay_key` | Pass through |
| `attempt_seed` | UUID4 | Unique per call |

### 2.4 `_build_lineage_root(cpa) -> LineageRoot`

| Field | Source | Fallback |
|-------|--------|----------|
| `parent_route_id` | `cpa.trace_id` | `cpa.request_id` |
| `parent_plan_id` | `cpa.run_id` | `None` |
| `parent_step_id` | — | `None` |
| `ancestry_chain` | `(cpa.trace_id,)` | Empty tuple |
| `same_run_packet_family` | `cpa.run_id` | `""` |

### 2.5 `_build_prep_output(cpa) -> PrepOutput`

| Component | Builder Used |
|-----------|--------------|
| `frozen_execution_context` | `_build_frozen_execution_context` |
| `replay_bindings.determinism` | `_build_determinism_bundle` |
| `replay_bindings.snapshot_manifest` | `cpa.replay_manifest_ref` |
| `lineage_root` | `_build_lineage_root` |
| `write_lock_assertion` | `WriteLockAssertion(...)` |
| `ready_for_validation` | `bool(compilation_hash and replay_key)` |
| `refusal_reason` | List of missing required fields |
| `prep_receipt_id` | `f"prep-{uuid4().hex}"` |
| `idempotency_key` | `f"{request_id}:{run_id}"` |
| `run_id` | `cpa.run_id` |

**WriteLockAssertion values:**
- `no_direct_l4_path=True`
- `proposed_diff_only=True`
- `persistence_disabled=True`

---

## 3. Tests Added and Results

### 3.1 Test Inventory (22 tests)

| Test Class | # Tests | Focus |
|------------|---------|-------|
| `TestE1WorkOrderInputs` | 4 | WorkOrderInputs builder |
| `TestE1FrozenExecutionContext` | 2 | FrozenExecutionContext builder |
| `TestE1DeterminismBundle` | 4 | DeterminismBundle builder |
| `TestE1LineageRoot` | 2 | LineageRoot builder |
| `TestE1PrepOutput` | 4 | PrepOutput builder |
| `TestE1Invariants` | 6 | Boundary/invariant checks |

### 3.2 Required Tests Implemented

| # | Test Name | Status |
|---|-----------|--------|
| 1 | `test_e1_builds_work_order_inputs_from_cpa` | ✅ PASS |
| 2 | `test_e1_builds_frozen_execution_context_from_cpa` | ✅ PASS |
| 3 | `test_e1_builds_determinism_bundle_from_cpa` | ✅ PASS |
| 4 | `test_e1_builds_lineage_root_from_cpa` | ✅ PASS |
| 5 | `test_e1_builds_prep_output_ready_for_validation` | ✅ PASS |
| 6 | `test_e1_missing_replay_key_marks_not_ready_or_refusal_reason` | ✅ PASS |
| 7 | `test_e1_write_lock_assertion_blocks_direct_l4_path` | ✅ PASS |
| 8 | `test_e1_does_not_call_provider_gateway` | ✅ PASS |
| 9 | `test_e1_does_not_import_or_call_prompt_assembly` | ✅ PASS |
| 10 | `test_e1_does_not_retrieve_c0_or_write_l4` | ✅ PASS |

**Bonus tests added (12 additional):**
- `test_e1_work_order_inputs_derives_slo_from_max_tokens`
- `test_e1_work_order_inputs_grounded_false_without_evidence`
- `test_e1_work_order_inputs_populates_tool_spec_when_allowed_tools_present`
- `test_e1_fec_uses_safe_defaults_for_missing_fields`
- `test_e1_input_hash_is_deterministic`
- `test_e1_input_hash_differs_for_different_identity`
- `test_e1_policy_hash_falls_back_to_signature`
- `test_e1_lineage_uses_request_id_when_trace_id_missing`
- `test_e1_missing_compilation_hash_marks_not_ready`
- `test_e1_both_missing_fields_in_refusal_reason`
- `test_e1_prep_receipt_id_is_unique`
- `test_e1_idempotency_key_derived_from_request_and_run`

### 3.3 Test Execution Results

```bash
$ python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -v
======================= 22 passed, 3 warnings in 0.82s ========================
```

**Exit code: 0** — all tests pass.

---

## 4. Category A Invariant Verification

### 4.1 Commands Run

| # | Command | Result |
|---|---------|--------|
| 1 | `grep -r "_invoke_local_vllm\|_invoke_external_api" apps_rg/` | No matches |
| 2 | `grep -r "urllib\|requests\.\|httpx\.\|openai\.\|anthropic\." apps_rg/runtime/bindings/l2_envelope_adapter.py` | No matches |
| 3 | `grep -r "gateway\.invoke" apps_rg/` | 2 matches (l2_binding.py only) |
| 4 | `pytest tests/_apps_contract/ --collect-only` | 4094 tests, exit 0 |

### 4.2 Verification Summary

| Invariant | Status |
|-----------|--------|
| No `_invoke_local_vllm` | ✅ PASS |
| No `_invoke_external_api` | ✅ PASS |
| No `urllib` in new code | ✅ PASS |
| No `requests.` in new code | ✅ PASS |
| No `httpx.` in new code | ✅ PASS |
| No `openai.` in new code | ✅ PASS |
| No `anthropic.` in new code | ✅ PASS |
| `gateway.invoke()` only in l2_binding.py (pre-existing) | ✅ PASS |
| Collect-only zero errors | ✅ PASS (4094 tests) |

**Category A invariants remain fully intact.**

---

## 5. Boundary Confirmations

| Boundary | Status | Evidence |
|----------|--------|----------|
| No agentic_core changes | ✅ CONFIRMED | `git status` shows only apps_rg changes |
| No YAML configs added | ✅ CONFIRMED | No new YAML files |
| No E2 implementation | ✅ CONFIRMED | No ValidationOutput production in adapter |
| No E3 implementation | ✅ CONFIRMED | No HOP calls in adapter |
| No E4 implementation | ✅ CONFIRMED | No heal logic in adapter |
| No E5 implementation | ✅ CONFIRMED | No SealedL2Artifact sealing in adapter |
| HOP remains L2.3/E3 | ✅ CONFIRMED | No changes to l2_binding.py |

---

## 6. W2_STATUS: **PASS**

### Decisive Factors

1. **All 5 E1 builder functions implemented** with exact field mappings per W1 audit
2. **All 22 tests pass** (including 10 required negative controls)
3. **Category A invariants intact** — no private gateway calls, no direct HTTP
4. **No agentic_core modifications** — pure apps_rg adapter code
5. **No YAML configs** — deferred per W1 recommendation
6. **No E2/E3/E4/E5 code** — scope strictly limited to E1 PREP

### Gaps Remaining (Expected)

| Gap | Type | Resolution |
|-----|------|------------|
| E2 validation adapter | Wiring | W3 |
| E3 executor callback | Wiring | W4 |
| E4 heal callback | Wiring | W5 |
| E5 seal logic | Wiring | W6 |
| YAML configs (if needed) | Config | W4+ |
| CI gates | Testing | W6 |

---

## 7. Exact Recommendation for W3

### W3 Scope: E2 Validation Adapter Only

**Goal:** Implement `_validate_work_order` function for E2 phase.

**Files to change:**
- `apps_rg/runtime/bindings/l2_envelope_adapter.py` — add validator function
- `tests/_apps_contract/test_apps_rg_l2_envelope.py` — add E2 tests

**Required behavior:**

```python
def _validate_work_order(
    work_order_inputs: WorkOrderInputs,
    prep_receipt: PrepReceipt,
) -> ValidationOutput:
    """E2 validation — validate provider registry, sandbox, capability, budget.

    Returns:
        ValidationOutput with either:
        - approved_work_order populated (PASS)
        - sealed_rejection_packet populated (FAIL)

    Must NOT:
        - Call ProviderGateway (E3 only)
        - Reroute/replan/reground/clarify
        - Call L0, L1, L3, C0, PA, or user directly
    """
```

**Validation checks (V1-V9):**
1. Provider registry entry exists
2. Sandbox envelope matches task class
3. Capability token valid for model
4. Budget sufficient for tokens requested
5. Replay key present and valid format
6. Prompt artifact digest present
7. No direct L4 write path
8. Route match (CPA.target_model in allowed_models)
9. Evidence refs present if grounded=True

**On failure:**
- Emit `ValidationOutput` with `sealed_rejection_packet`
- Include `decisive_rule_id` (which V check failed)
- Include `suggested_reentry_target` (informational only)
- Do NOT call other layers

**Tests required (minimum 8):**
1. `test_e2_passes_valid_work_order`
2. `test_e2_fails_missing_provider_registry`
3. `test_e2_fails_missing_replay_key`
4. `test_e2_fails_missing_prompt_digest`
5. `test_e2_fails_sandbox_mismatch`
6. `test_e2_fails_budget_exceeded`
7. `test_e2_does_not_call_provider_gateway`
8. `test_e2_does_not_reroute_or_clarify`

---

## 8. Semantic Equivalents Note (for Future W6)

Per W1 audit finding: `SealedL2Artifact` does not have named fields `durable_commit_occurred` or `mutation_candidate_inert`, but semantic equivalents exist:

| v4 Spec Field | Semantic Equivalent | Test Assertion |
|---------------|---------------------|----------------|
| `durable_commit_occurred=False` | `is_uwg_write_authority=False` AND `state_diff_authorized=False` | Assert both False |
| `mutation_candidate_inert=True` | `bool(proposed_state_diff) == True` (non-empty) | Assert non-empty |

**W6 tests must use these semantic equivalents**, not expect new fields.

---

*End of W2 Execution Report*
