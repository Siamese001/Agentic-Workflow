---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-deferred-follow-ons-b3e9f1.md'
original_relative_path: 'apps-rg-deferred-follow-ons-b3e9f1.md'
source_sha256: a8bd2177b33cda54f9d47f64e078b46eab1484dc0be7cc72f8aef3dba57752d5
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
| W1 | DF-1: HITL policy registry — implement AG-13.b lookup and attach to Exit disposition | HITL registry callable | ✅ COMPLETE |
| W2 | DF-2: Fact-check engine — wire `fact_checked_required` enforcement at Exit gate | Fact-check gate enforcing | ✅ COMPLETE |
| W3 | DF-3: Output renderer callbacks — wire `formats` from `AppsRGExitGatePolicy` to renderer dispatch | Renderer dispatch wired | ✅ COMPLETE |
| W4 | Tests + field map final sweep — all 3 DF items promoted to FULLY_ENFORCED in field map | 0 metadata-only deferred | ✅ COMPLETE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Implement HITL registry lookup (AG-13.b) | `agentic_core/runtime/exit/hitl_policy_registry.py` (new) | AG-13.b schema | ~10K | ✅ DONE |
| W1.P2 | Wire hitl_policy_ref resolution to Exit disposition | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Disposition contract shape | ~5K | ✅ DONE |
| W2.P1 | Implement fact-check gate engine stub | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Fail-closed semantics | ~8K | ✅ DONE |
| W2.P2 | Wire `fact_checked_required=true` to blocking Exit verdict | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Fail-closed semantics | ~4K | ✅ DONE |
| W3.P1 | Wire `formats` field to output renderer dispatch | `agentic_core/runtime/exit/apps_rg_exit_binding.py`, `tools/apps_rg/resume_docx_renderer.py` | Renderer API contract | ~6K | ✅ DONE |
| W4.P1 | Tests for all 3 DF items enforcing (not metadata-only) | `tests/_apps_contract/test_rg_deferred_followons.py` (new) | Test isolation | ~6K | ✅ DONE |
| W4.P2 | Update field map: flip 3 remaining metadata-only entries to FULLY_ENFORCED | `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` | YAML SSOT | ~2K | ✅ DONE |

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
| DoD-1 | HITL policy ref resolves to structured spec at Exit (not metadata string passthrough) | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestHitlPolicyResolution` → pass | ✅ DONE (15/15 pass) |
| DoD-2 | `fact_checked_required=True` with no fact-check receipt produces Exit FAIL (not WARN/deferred) | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestFactCheckEnforcement` → pass | ✅ DONE (10/10 pass) |
| DoD-3 | `formats=["docx"]` in U0 packet → DOCX renderer invoked; artifact emitted | `pytest tests/_apps_contract/test_rg_deferred_followons.py::TestOutputRendererDispatch` → pass | ✅ DONE (12/12 pass) |
| DoD-4 | Field map shows 0 `status: DEFERRED` or `status: METADATA_ONLY` entries for DF-1..3 | `grep -c "DEFERRED\|METADATA_ONLY" apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` = 0 for these 3 fields | ✅ DONE (all 3 → MAPPED) |
| DoD-5 | `python -m apps_rg --help` exits 0 (spine entry point unaffected) | Exit 0 | ✅ DONE |

**Verification-vs-Deferral table**:

| Item | Why deferred from THIS plan | Tracked in |
|---|---|---|
| PDF renderer for `formats=["pdf"]` | PDF renderer requires separate toolchain (wkhtmltopdf or headless browser) | Separate output-renderer plan |
| Real LLM judge calibration | Requires holdout corpus and Spearman ≥ 0.80 calibration | `apps-eval-harness-deferred-e4a1b7` |
| C0 FEC producer binding | Requires separate FEC producer plan | Separate FEC plan |

PLAN_CREATED: plan=apps-rg-deferred-follow-ons-b3e9f1

---

## Closure Record

**Final status**: ✅ COMPLETE  
**Commit**: `f419d2bc4c` — `feat(apps-rg): wire DF-1/2/3 deferred follow-ons (HITL registry, fact-check gate, DOCX renderer)`  
**Closed**: 2026-05-11

### Deferred items closed

| Item | Status | Enforcement path |
|---|---|---|
| DF-1 `hitl_policy_ref` | **FULLY_ENFORCED** | `hitl_policy_registry.resolve_hitl_policy()` → `HitlPolicySpec`; `hitl_required` flag in gate result; unknown refs → WARN (fail-soft); `APPS_RG_HITL_REGISTRY_FAIL_CLOSED=1` for strict |
| DF-2 `fact_checked_required` | **FULLY_ENFORCED** | `run_context.fact_check_receipt` checked at Exit; absent → FAIL (fail-closed default `APPS_RG_FACT_CHECK_FAIL_CLOSED=1`); `=0` softens to WARN |
| DF-3 `formats` | **FULLY_ENFORCED** (json + docx) | `_dispatch_docx_renderer()` dispatched post-Exit for `"docx"`; `"json"` natively produced; other formats logged as skipped metadata; renderer is fail-soft (error → skipped, not gate FAIL) |

### Test results (commit `f419d2bc4c`)

```
pytest tests/_apps_contract/test_rg_deferred_followons.py -q  → 40 passed
pytest tests/_apps_contract/test_w5_gap3_gate_consumers.py -q → 32 passed
Combined: 72/72 passed
```

### Files changed in commit

| File | Change |
|---|---|
| `agentic_core/runtime/exit/hitl_policy_registry.py` | NEW — `HitlPolicySpec` + `resolve_hitl_policy()` + 6 built-in policies |
| `agentic_core/runtime/exit/apps_rg_exit_binding.py` | UPDATED — DF-1/2/3 wired into `extract_*` + `evaluate_*` + `_dispatch_docx_renderer()` helper |
| `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` | UPDATED — 3 DEFERRED → MAPPED |
| `tests/_apps_contract/test_rg_deferred_followons.py` | NEW — 40 tests (15+10+12+4) |
| `tests/_apps_contract/test_w5_gap3_gate_consumers.py` | UPDATED — 3 tests updated from "still deferred" → "now wired" assertions |

No quarantine stubs modified. No schema changes. No changes to `apps_rg/` capability code.

---

## Renderer Boundary Note — Architectural Constraint

The DOCX renderer dispatch wired in DF-3 is a **bounded post-Exit return-format materialization callback**, not general execution. The following constraints are architectural invariants and MUST NOT be relaxed without a new Author-Gate decision:

1. **Renderer dispatch must be allowlisted** — only formats present in `_ALLOWED_RENDERER_FORMATS` (currently `{"json", "docx"}`) may be dispatched. Unknown formats are skipped with metadata; they never trigger arbitrary code execution.

2. **Format dispatch must be allowlisted** — `_dispatch_docx_renderer()` is the only renderer callable wired at this layer. New renderers (PDF, HTML, etc.) require a new DF plan and Author-Gate.

3. **Run directory must be sandboxed** — the renderer resolves its output path from `sealed_artifact.run_id` (or most-recent run fallback) within `artifacts/apps_rg/runs/<run_id>/`. It MUST NOT write outside that directory.

4. **Renderer must emit an artifact receipt** — successful render returns `{"status": "ok", "path": <docx_path>}` written into `policy_metadata.docx_artifact_path` in the gate result. Absence of this receipt indicates renderer was not invoked or failed.

5. **Renderer must assert no L4 write** — `_dispatch_docx_renderer()` reads from `generated_resume.json` and writes `generated_resume.docx` only. It MUST NOT call any L4 state writer, cache, or database. This is enforced by code review; a future gate may verify via static analysis.

6. **Renderer must not expand tools, providers, routes, capabilities, or authority** — the callback operates on already-sealed artifact data. It MUST NOT make LLM calls, invoke external HTTP endpoints, create new run artifacts beyond the docx file, or alter the `X3Disposition` or `SealedL2Artifact`.

7. **Failure policy must be explicit** — renderer failures are currently fail-soft (`status: error` → format skipped, no gate FAIL). This is correct because format materialization is a post-gate concern. If a specific deployment requires DOCX as a hard output requirement, set `APPS_RG_DOCX_RENDERER_FAIL_CLOSED=1` (not yet wired; future DF item).

**Exit remains the checkout/control layer.** It evaluates gate policies (provenance, HITL, fact-check) and then — only after those gates clear — may trigger bounded return-format materialization. Exit MUST NOT become a place where arbitrary post-processing happens. The renderer callback is the only permitted side effect, and it is scoped to format conversion of the already-sealed artifact.
