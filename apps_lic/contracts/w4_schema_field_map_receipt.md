# W4 Schema and Field-Map Coverage Receipt

**Status**: COMPLETE  
**Date**: 2026-05-11  
**Tests**: 21/21 PASS (new) + 89/89 PASS (W3.5 regression check)  
**No new runtime behavior introduced.**

---

## Receipt Fields

### Schema identity

| Field | Value |
|---|---|
| `schema_regenerated` | `true` |
| `schema_generation_command` | `python tools/apps_lic/w4_schema_verify.py --generate-schema` |
| `schema_path` | `artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json` |
| `pydantic_model_source` | `apps_lic.contracts.apps_lic_ingress_contract_v1.AppsLicIngressContractV1` |
| `field_map_coverage_result` | `artifacts/apps_lic/w4_field_map_coverage_result.json` |

### Pointer counts — total

| Metric | Count |
|---|---|
| Total schema pointers | **233** |
| Total field-map entries (exact + pattern) | **159** (145 exact + 14 pattern-prefix) |
| Covered pointers | **233** |
| Coverage % | **100.0%** |
| `silently_dropped_fields` | **`[]`** |

### Pointer counts — `runtime_customization_package` scope only

| Metric | Count | Notes |
|---|---|---|
| Total schema pointers under `/runtime_customization_package` | **126** | |
| Explicitly MAPPED | **53** | Direct field-map entry with `status: MAPPED`; target `ValidatedRequest.app_payload.runtime_customization_package.*` |
| DERIVED | **1** | `/runtime_customization_package/package_digest` — caller-computed; explicit receipt below |
| DEFERRED | **0** | No rcp fields deferred; all preserved into `app_payload` |
| REJECTED | **0** | |
| Covered-by-parent | **72** | ProfileRef sub-fields (ref_id/ref_path/ref_digest per ref) travel with their MAPPED parent pointer; no separate entry required |
| Silently dropped | **0** | |

### Pointer counts — global scope (outside `runtime_customization_package`)

| Metric | Count | Notes |
|---|---|---|
| Total schema pointers outside rcp | **107** | |
| MAPPED | **60** | |
| DERIVED | **6** | |
| DEFERRED | **41** | All carry explicit `target` + `reason` referencing plan wave (W5/W6) — see §5 |
| REJECTED | **0** | |
| Covered-by-parent | **0** | |
| Silently dropped | **0** | |

### Derived field receipts

| Pointer | Status | Receipt |
|---|---|---|
| `/payload_digest` | DERIVED | Adapter re-computes SHA-256 of canonical JSON; caller-supplied value cross-checked; adapter value wins |
| `/runtime_customization_package/package_digest` | DERIVED | Caller-computed digest preserved verbatim in `app_payload` for audit trail |

### Tests

| Run | Count | Result |
|---|---|---|
| W4 new tests | 21 | PASS |
| W3.5 regression | 89 | PASS |
| **Total** | **110** | **PASS** |

---

## W4 Verification Summary

### 1. Schema regenerated from Pydantic

`AppsLicIngressContractV1.model_json_schema()` was called at test time; schema written to  
`artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json`.  
This is the canonical Pydantic-generated JSON Schema (draft 2020-12). It is the runtime shape
of the contract, not the hand-authored `ag8_apps_lic_payload_schema.json` (which is a
discovery-phase annotation artefact).

### 2. Schema matches AppsLicIngressContractV1 exactly

- Schema title: `AppsLicIngressContractV1`
- Root properties include: `transport`, `campaign`, `forbidden_send_modes`, `entity_refs`,
  `personalization`, `generation_hints`, `tone_constraints`, `output_format`,
  `research_requirements`, `routing_policy`, `validation_policy`, `gate_decision_policy`,
  `qa_report`, `integration_target`, `hitl_policy`, `pii_policy`, `governance_shield`,
  `antipattern_policy`, `source_lineage`, `ab_test`, `replay_audit`,
  `runtime_customization_package`, `payload_digest`.
- Total schema pointers enumerated: **233**

### 3. runtime_customization_package in schema

`/runtime_customization_package` is a top-level property in the schema.

### 4. All runtime_customization_package fields represented

126 pointers under `/runtime_customization_package` found in schema, including:
- All 17 `ProfileRef` sub-fields (ref_id, ref_path, ref_digest, required per ref)
- All 3 `RoutePolicy` fields
- All 3 `WritePolicy` fields
- All 5 `CacheBypassPolicy` fields
- All 3 `RuntimeGatePolicy` fields
- All 3 `ExitGatePolicy` fields
- All 4 `ConsentCompliancePolicy` fields (including nested compliance_profile_ref)
- All 7 `MetaFeedbackPolicy` fields
- `package_digest`

### 5. Field-map covers every JSON pointer

**233/233 pointers covered (100.0%).**  
`silently_dropped_fields: []`

Coverage breakdown:
| Status | Count | Notes |
|---|---|---|
| MAPPED | 113 | Direct field-map entry with MAPPED status |
| DERIVED | 7 | Computed/transformed fields with explicit receipts |
| DEFERRED | 41 | Recognized, not yet wired — explicit reason in field map |
| COVERED_BY_PARENT | 72 | Sub-fields of a MAPPED/DERIVED/DEFERRED parent |

### 6. runtime_customization_package pointers mapped to ValidatedRequest.app_payload.*

`/runtime_customization_package` → `ValidatedRequest.app_payload.runtime_customization_package`  
All 126 rcp sub-pointers are covered via exact match, parent coverage, or pattern prefix.

### 7. Derived fields have explicit receipts

| Field | Status | Receipt |
|---|---|---|
| `/payload_digest` | DERIVED | Adapter re-computes sha256; caller-supplied cross-checked; adapter value wins |
| `/runtime_customization_package/package_digest` | DERIVED | Caller-computed; preserved verbatim in app_payload for audit trail |

### 8. Fail closed on silently dropped fields

`tools/apps_lic/w4_schema_verify.py` returns exit code 1 if `silently_dropped_fields` is non-empty.  
Test `TestW4FieldMapCoverage::test_no_silently_dropped_fields` fails on any dropped pointer.

### 9–10. No new runtime behavior; W3.5 boundary not regressed

- `agentic_core` was not modified.
- W3.5 suite: 89/89 PASS (regression check confirmed same session).
- `_load_exit_profile` fail-closed behavior confirmed still active via W4 regression probe test.

---

## Files Created

| File | Purpose |
|---|---|
| `tools/apps_lic/w4_schema_verify.py` | Schema generation + field-map coverage verification tool |
| `tools/apps_lic/__init__.py` | Package marker |
| `tests/_apps_contract/test_w4_apps_lic_schema_field_map_coverage.py` | 21 W4 tests |
| `artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json` | Generated Pydantic JSON Schema |
| `artifacts/apps_lic/w4_field_map_coverage_result.json` | Machine-readable coverage result |
| `apps_lic/contracts/w4_schema_field_map_receipt.md` | This receipt |

## Files Modified

None. W4 is proof-only — no existing files were modified.
