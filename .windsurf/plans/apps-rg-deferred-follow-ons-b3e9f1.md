---
plan_id: apps-rg-deferred-follow-ons-b3e9f1
plan_type: governance
dod_exempt: false
parent_plan: apps-rg-quarantine-gap-remediation-8f405c
---

# apps_rg Deferred Follow-On Capability Plans

Tracks the three capability follow-on items explicitly deferred from
`apps-rg-quarantine-gap-remediation-8f405c` W6 (verdict
`PASS_WITH_DEFERRED_FOLLOW_ONS`). These are separate future capability
plans — not quarantine audit gaps. The parent plan is fully COMPLETE.

---

## Context

The quarantine gap remediation plan (`8f405c`) closed all four gaps
(GAP-1..4) and the bypass risk (BR-1). Three items were explicitly
deferred because they require separate capability implementations that
did not exist at the time of W5 wiring:

| # | Field | Reason for deferral | Parent receipt |
|---|---|---|---|
| DF-1 | `hitl_policy_ref` | HITL registry (AG-13.b) not yet implemented; field extracted as metadata-only at Exit | `artifacts/apps_rg/w5_gap3_field_consumers_receipt.json` |
| DF-2 | `output_requirements.fact_checked_required` (full enforcement) | Fact-check engine not implemented; W5 Exit binding carries as deferred metadata | `artifacts/apps_rg/w5_gap3_field_consumers_receipt.json` |
| DF-3 | `output_requirements.formats` (output renderer callbacks) | Formats extracted in `AppsRGExitGatePolicy` but renderer integration not wired | `artifacts/apps_rg/w5_gap3_field_consumers_receipt.json` |

---

## Wave Structure

| Wave | Scope | Checkpoint | Status |
|------|-------|------------|--------|
| W1 | DF-1: HITL policy registry — implement AG-13.b lookup and attach to Exit disposition | HITL registry callable | 🔲 NOT STARTED |
| W2 | DF-2: Fact-check engine — wire `fact_checked_required` enforcement at Exit gate | Fact-check gate enforcing | 🔲 NOT STARTED |
| W3 | DF-3: Output renderer callbacks — wire `formats` from `AppsRGExitGatePolicy` to renderer dispatch | Renderer dispatch wired | 🔲 NOT STARTED |
| W4 | Tests + field map final sweep — all 3 DF items promoted to FULLY_ENFORCED in field map | 0 metadata-only deferred | 🔲 NOT STARTED |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Implement HITL registry lookup (AG-13.b) | `agentic_core/runtime/exit/apps_rg_exit_binding.py`, `apps_rg/hitl/` | AG-13.b schema | ~10K | 🔲 TODO |
| W1.P2 | Wire hitl_policy_ref resolution to Exit disposition | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Disposition contract shape | ~5K | 🔲 TODO |
| W2.P1 | Implement fact-check gate engine stub | `agentic_core/L2_execution/` or `agentic_core/runtime/exit/` | Fact-check source | ~8K | 🔲 TODO |
| W2.P2 | Wire `fact_checked_required=true` to blocking Exit verdict | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Fail-closed semantics | ~4K | 🔲 TODO |
| W3.P1 | Wire `formats` field to output renderer dispatch | `agentic_core/runtime/exit/apps_rg_exit_binding.py`, `tools/apps_rg/resume_docx_renderer.py` | Renderer API contract | ~6K | 🔲 TODO |
| W4.P1 | Tests for all 3 DF items enforcing (not metadata-only) | `tests/_apps_contract/test_rg_deferred_followons.py` (new) | Test isolation | ~6K | 🔲 TODO |
| W4.P2 | Update field map: flip 3 remaining metadata-only entries to FULLY_ENFORCED | `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` | YAML SSOT | ~2K | 🔲 TODO |

---

## Deferred Item Details

### DF-1 — `profile_manifest.hitl_policy_ref` (HITL Registry AG-13.b)

**Current state** (W5 wiring):
- `extract_apps_rg_exit_gate_policy()` reads `hitl_policy_ref` from `app_payload`
- Stored in `AppsRGExitGatePolicy.hitl_policy_ref` (metadata-only; no lookup)
- `evaluate_apps_rg_exit_provenance_gate()` carries it in evaluation result as `hitl_policy_ref_deferred`

**What is needed**:
- Implement `apps_rg/hitl/` HITL registry lookup (AG-13.b): resolve `hitl_policy_ref` string → `HitlPolicySpec` object
- Wire resolved spec into Exit `DispositionRecord` so downstream HITL routing agent can branch on it
- Update `evaluate_apps_rg_exit_provenance_gate()` to call registry and return fully resolved spec

**Acceptance**: `hitl_policy_ref` resolves to a structured policy spec at Exit; HITL routing agent reads policy from disposition.

---

### DF-2 — `output_requirements.fact_checked_required` (Fact-Check Engine)

**Current state** (W5 wiring):
- `extract_apps_rg_exit_gate_policy()` reads `fact_checked_required` from `app_payload`
- Stored in `AppsRGExitGatePolicy.fact_checked_required`
- `evaluate_apps_rg_exit_provenance_gate()` returns `fact_check_deferred=True` when `fact_checked_required=True` (no actual gate)

**What is needed**:
- Implement a fact-check gate engine (new module or stub escalation)
- When `fact_checked_required=True`, Exit gate MUST verify `run_context.fact_check_receipt` is non-null
- If absent → FAIL (blocking, not metadata-only)
- Env-var: `APPS_RG_FACT_CHECK_FAIL_CLOSED` (default: True when `fact_checked_required=True`)

**Acceptance**: `fact_checked_required=True` with missing fact-check receipt causes Exit gate FAIL, not WARN/metadata.

---

### DF-3 — `output_requirements.formats` (Output Renderer Callbacks)

**Current state** (W5 wiring):
- `extract_apps_rg_exit_gate_policy()` reads `formats` list from `app_payload`
- Stored in `AppsRGExitGatePolicy.formats`
- NOT evaluated or dispatched anywhere in Exit gate

**What is needed**:
- Wire `AppsRGExitGatePolicy.formats` to renderer dispatch in `tools/apps_rg/resume_docx_renderer.py`
- When `formats` includes `"docx"` → dispatch DOCX renderer after Exit gate pass
- When `formats` includes `"json"` → already produced natively
- When `formats` includes `"pdf"` → dispatch PDF renderer (separate capability, may need another deferred item)

**Acceptance**: `formats=["docx"]` in U0 packet → DOCX renderer invoked post-Exit; artifact present in run directory.

---

## Out of Scope

- Restoring real LLM judges (tracked in `apps-eval-harness-deferred-e4a1b7`)
- C0 FEC producer binding (tracked separately)
- Any changes to quarantine stubs
- Any schema changes to `apps_rg/contracts/apps_rg_ingress_contract_v1.py`

---

## Rules

- All capability implementations MUST live in `agentic_core/` (never in `apps_rg/`)
- Field map updates are the authoritative record of wiring status
- No plan wave may claim COMPLETE without a passing test that exercises the full enforcement path (not metadata-only)
- `APPS_RG_PROVENANCE_GATE_FAIL_CLOSED` and `APPS_RG_QUALITY_GATE_FAIL_CLOSED` precedent applies

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | HITL policy ref resolves to structured spec at Exit (not metadata string passthrough) | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestHitlPolicyResolution` → pass | 🔲 |
| DoD-2 | `fact_checked_required=True` with no fact-check receipt produces Exit FAIL (not WARN/deferred) | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestFactCheckEnforcement` → pass | 🔲 |
| DoD-3 | `formats=["docx"]` in U0 packet → DOCX renderer invoked; artifact emitted | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestOutputRendererDispatch` → pass | 🔲 |
| DoD-4 | Field map shows 0 `status: DEFERRED` or `status: METADATA_ONLY` entries for DF-1..3 | `grep -c "DEFERRED\|METADATA_ONLY" apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` = 0 for these 3 fields | 🔲 |
| DoD-5 | `python -m apps_rg --help` exits 0 (spine entry point unaffected) | Exit 0 | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred from THIS plan | Tracked in |
|---|---|---|
| PDF renderer for `formats=["pdf"]` | PDF renderer requires separate toolchain (wkhtmltopdf or headless browser) | Separate output-renderer plan |
| Real LLM judge calibration | Requires holdout corpus and Spearman ≥ 0.80 calibration | `apps-eval-harness-deferred-e4a1b7` |
| C0 FEC producer binding | Requires separate FEC producer plan | Separate FEC plan |

PLAN_CREATED: plan=apps-rg-deferred-follow-ons-b3e9f1
