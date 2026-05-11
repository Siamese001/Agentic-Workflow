# W3.5 Boundary Refactor Receipt

**Plan**: `apps-lic-u0-runtime-package-complete-f8e2a1.md`
**Date**: 2026-05-11
**Status**: COMPLETE — all blocking corrections applied, 89/89 tests green

---

## Receipt Fields

| Field | Value |
|---|---|
| `hardcoded_exit_profile_fallback_removed` | `true` |
| `exit_profile_failure_mode` | `fail_closed` |
| `exit_profile_source` | `apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json` |
| `exact_exit_gate_ids_proven` | `true` |
| `required_exit_gates` | `G21, G22, G23, G24, G26, G28` (from config SSOT) |
| `conditional_exit_gates` | `G25, G27` (from config SSOT) |
| `payload_digest_status` | `DERIVED` — adapter is canonical digest authority |
| `cache_bypass_receipt_source` | `runtime_customization_package.cache_bypass_policy` + `final_draft_cache_policy.outreach_message.v1.json` |
| `forbidden_send_modes_source` | `contract.forbidden_send_modes.modes` (Pydantic-validated, post-validation check) |
| `field_map_runtime_customization_package` | `MAPPED` — data preserved verbatim in `ValidatedRequest.app_payload` |

---

## Correction Detail

### 1. Field map: `runtime_customization_package` → `MAPPED`

All 50+ sub-fields under `runtime_customization_package` changed from blanket `DEFERRED`
to `MAPPED` with `target: ValidatedRequest.app_payload.runtime_customization_package.*`.

`package_digest` remains `DERIVED` (validator transforms the field).
`payload_digest` at root is `DERIVED` (adapter-computed SHA-256 receipt).

**File**: `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml`

### 2. Cache bypass receipt: data-driven

`_build_runtime_exhaust_bundle` now reads actual `CacheBypassPolicy` field values:
- `r1a_exact_cache_bypassed_for_final_drafts`
- `r1b_semantic_cache_bypassed_for_final_drafts`
- `cache_allowed_for_support_artifacts`
- `final_draft_cache_ttl_seconds`
- `support_artifact_cache_ttl_seconds`

Plus config path + SHA-256 digest of `final_draft_cache_policy.outreach_message.v1.json`
for self-auditable receipts. No static bypass strings used as proof.

**File**: `agentic_core/runtime/exit/apps_lic_exit_binding.py`

### 3. Forbidden send modes: contract is policy source

Removed pre-Pydantic `_check_forbidden_send_modes(fsm_raw)` hardcoded check.
Post-validation (step 2b) now calls `_check_forbidden_send_modes_from_contract(contract.forbidden_send_modes.modes)`.

Pydantic's `ForbiddenSendModesSection._must_contain_hardcoded_seven` fires during
`model_validate`; the `except ValidationError` handler re-raises `forbidden_send_modes`
errors as `AppsLicForbiddenSendModeError` (E2) instead of the generic E1.

`_CONTRACT_REQUIRED_SEND_MODES` constant is informational reference only —
enforcement is the validated contract, not the constant.

**File**: `agentic_core/runtime/u0/apps_lic_u0_adapter.py`

### 4. Exit gate IDs: exact, from config, no hardcoded fallback

`_load_exit_profile` now:
- Raises `AppsLicExitProfileError` (fail-closed) on `FileNotFoundError`, `OSError`, or `json.JSONDecodeError`
- Raises on missing `required_exit_gates` / `conditional_exit_gates` keys
- Raises on `ref_digest` mismatch when `package.exit_profile_ref.ref_digest` is provided
- Returns `profile_id`, `config_path`, `config_digest` so callers can prove data came from config
- **No hardcoded `["G21", "G22", ...]` fallback in `agentic_core`**

**File**: `agentic_core/runtime/exit/apps_lic_exit_binding.py`

### 5. payload_digest: `DERIVED`

`payload_digest` is recorded as `DERIVED` in the field map with receipt:
> "adapter's value wins: sha256-hex of all other ingress fields"

**File**: `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml`

---

## Test Evidence

| Test | Result |
|---|---|
| `TestW35ExitProfileFailClosed::test_apps_lic_exit_profile_loaded_from_config_exact_gate_ids` | PASS |
| `TestW35ExitProfileFailClosed::test_apps_lic_exit_profile_missing_fails_closed` | PASS |
| `TestW35ExitProfileFailClosed::test_apps_lic_exit_profile_malformed_fails_closed` | PASS |
| `TestW35ExitProfileFailClosed::test_apps_lic_exit_profile_missing_keys_fails_closed` | PASS |
| `TestW35ExitProfileFailClosed::test_apps_lic_exit_profile_digest_mismatch_fails_closed` | PASS |
| Full W3/W3.5 suite (89 tests) | 89/89 PASS |

---

## Files Modified

| File | Change |
|---|---|
| `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml` | `runtime_customization_package` DEFERRED→MAPPED; `payload_digest` DERIVED |
| `agentic_core/runtime/exit/apps_lic_exit_binding.py` | `_load_exit_profile` fail-closed; `AppsLicExitProfileError`; data-driven cache receipt |
| `agentic_core/runtime/u0/apps_lic_u0_adapter.py` | Post-validation forbidden_send_modes check; re-raise as E2 |
| `tests/_apps_contract/test_w3_apps_lic_exit_l6_package_consumption.py` | +5 tests in `TestW35ExitProfileFailClosed` |
