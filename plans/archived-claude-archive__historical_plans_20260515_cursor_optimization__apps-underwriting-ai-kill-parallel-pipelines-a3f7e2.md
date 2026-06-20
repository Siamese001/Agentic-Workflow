---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-underwriting-ai-kill-parallel-pipelines-a3f7e2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-underwriting-ai-kill-parallel-pipelines-a3f7e2.md'
source_sha256: 73e8630448d6c05512e78d26b375401b13cecb651bf909e2d858b89718a9f1cb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Kill Parallel Pipelines in apps_underwriting_ai; Move Config to U0 Input

Deletes all parallel execution paths that bypass `agentic_core` and moves every
`apps_underwriting_ai/config/domain_contract/` file into a U0 `runtime_customization_package`
so that `agentic_core`'s dispatch chain is the ONLY execution path.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — `apps_underwriting_ai` has two fully-implemented execution paths:
  (1) the intended `agentic_core` dispatch chain (U0→L1→L0→C0→PA→L2→Exit) and
  (2) a legacy parallel path (`governed_underwriting_run.py` → `ExecutionAdapter` →
  `UnderwritingEngine`) that bypasses `agentic_core` entirely. A third bypass exists
  via `UnderwritingIngressRunner`, which reads files and dispatches directly to the
  parallel path. The `underwriting_capability_registry.py` is an app-side registry
  that duplicates `agentic_core` routing authority. The domain config (17 YAML files
  in `config/domain_contract/`) is read ad-hoc rather than flowing in through U0 as
  a `runtime_customization_package`.

- **Complication** — The parallel path means execution can succeed (or silently fail)
  without ever touching the governed spine. `_run_demo` and `_run_from_file` in
  `__main__.py` print `status=STUB_OK` and return 0 without running a single `agentic_core`
  layer. The app-side capability registry is a duplication of ownership that belongs
  exclusively to `agentic_core`. Config flowing outside U0 means the governance chain
  never sees the app's policy, threshold, and route constraints at intake time.

- **Question** — How do we make `agentic_core`'s dispatch chain the only execution
  path, surface the full domain config to U0, and delete every parallel bypass?

- **Answer** — Delete the parallel path files, collapse the app-side registry, wire
  `__main__.py` to call `agentic_core` dispatch directly, and build a U0 binding that
  consumes the domain contract as a `runtime_customization_package`.

---

## Parallel Path Inventory (what gets killed)

| File | Parallel role | Disposition |
|---|---|---|
| `integrations/governed_underwriting_run.py` | Convenience wrapper calling `ExecutionAdapter` directly | **DELETE** |
| `integrations/execution_adapter.py` | `ExecutionAdapter` → `UnderwritingEngine` bypass | **DELETE** |
| `integrations/underwriting_ingress_runner.py` | File-based ingress → `governed_underwriting_run` | **DELETE** |
| `integrations/spine_handoff.py` | Stale `SpineHandoffEnvelope` wrapping result for wrong route | **DELETE** |
| `integrations/underwriting_capability_registry.py` | App-side capability registry duplicating `agentic_core` authority | **DELETE** |
| `engines/underwriting_engine.py` | Imperative 5-stage driver — parallel to L2 step adapters | **RELOCATE** to `engines/_legacy/` (preserved as reference; not on any import path) |
| `__main__.py` `_run_demo` / `_run_from_file` | Print `STUB_OK` and return 0 — never enter `agentic_core` | **REPLACE** with `agentic_core` dispatch calls |
| `__main__.py` `_resolve_capability` / `_r5_terminal` | Wire to app-side registry | **REPLACE** with `agentic_core` direct route |

## Config to U0 Input

| File | U0 field name |
|---|---|
| `config/domain_contract/app_domain_manifest.yaml` | `app_domain_manifest` |
| `config/domain_contract/route_profiles.yaml` | `route_profiles` |
| `config/domain_contract/threshold_profiles.yaml` | `threshold_profiles` |
| `config/domain_contract/input_contract.yaml` | `input_contract` |
| `config/domain_contract/eval_rubrics.yaml` | `eval_rubrics` |
| `config/domain_contract/grader_roster.yaml` | `grader_roster` |
| `config/domain_contract/fixtures.yaml` | `fixtures` |
| `config/domain_contract/negative_controls.yaml` | `negative_controls` |
| `config/domain_contract/prompt_profiles.yaml` | `prompt_profiles` |
| `config/domain_contract/retrieval_profiles.yaml` | `retrieval_profiles` |
| `config/domain_contract/capability_profiles.yaml` | `capability_profiles` |
| `config/domain_contract/orchestration_profiles.yaml` | `orchestration_profiles` |
| `config/domain_contract/cache_profiles.yaml` | `cache_profiles` |
| `config/domain_contract/learning_profiles.yaml` | `learning_profiles` |
| `config/domain_contract/output_schema.yaml` | `output_schema` |
| `config/domain_contract/repair_profiles.yaml` | `repair_profiles` |
| `config/domain_contract/task_classes.yaml` | `task_classes` |

---

## Wave Overview

**Waves**: 4 total (W1–W4)
**Total Estimate**: ~30K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Delete parallel path files + relocate `UnderwritingEngine` | ~6K tokens | Checkpoint A | STATUS: TODO
- **W2** — Build `apps_underwriting_ai/runtime/bindings/u0_binding.py` consuming domain_contract as `runtime_customization_package` | ~10K tokens | Checkpoint B | STATUS: TODO
- **W3** — Wire `__main__.py` to `agentic_core` dispatch; stub remaining 6 bindings (L1/L0/C0/PA/L2/Exit) with TODO stubs | ~8K tokens | Checkpoint C | STATUS: TODO
- **W4** — Tests + CI gates | ~6K tokens | Checkpoint D | STATUS: TODO

---

## Wave 1 — Delete Parallel Path Files

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Files In Scope**:
- `apps_underwriting_ai/integrations/governed_underwriting_run.py` → **DELETE**
- `apps_underwriting_ai/integrations/execution_adapter.py` → **DELETE**
- `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` → **DELETE**
- `apps_underwriting_ai/integrations/spine_handoff.py` → **DELETE**
- `apps_underwriting_ai/integrations/underwriting_capability_registry.py` → **DELETE**
- `apps_underwriting_ai/engines/underwriting_engine.py` → **MOVE** to `apps_underwriting_ai/engines/_legacy/underwriting_engine.py`

**Pre-flight checklist**:
1. Grep for any import of the deleted files outside `apps_underwriting_ai/` — confirm zero callers.
2. Confirm `engines/underwriting_engine.py` is only referenced from `execution_adapter.py` (which is also being deleted) and from tests.
3. Any tests importing the deleted files get updated in W4.

---

## Wave 2 — U0 Binding with runtime_customization_package

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Files In Scope** (new):
- `apps_underwriting_ai/runtime/__init__.py`
- `apps_underwriting_ai/runtime/bindings/__init__.py`
- `apps_underwriting_ai/runtime/bindings/u0_binding.py`
- `apps_underwriting_ai/runtime/contracts/__init__.py`
- `apps_underwriting_ai/runtime/contracts/underwriting_ingress_payload.py`

**U0 binding shape** (mirrors `apps_rg/runtime/bindings/u0_binding.py`):
```python
def u0_validate_underwriting(envelope: UnderwritingIngressEnvelope) -> ValidatedUnderwritingRequest:
    """
    1. Load all 17 domain_contract YAMLs from config/domain_contract/.
    2. Package them as runtime_customization_package fields on the ValidatedRequest.
    3. Validate required fields: request_id, applicant_id, product_class.
    4. Enforce input_contract.yaml forbidden_inputs rules.
    5. Enforce negative_controls.yaml (protected_attribute_direct_input etc).
    6. Return ValidatedUnderwritingRequest — fail-closed on any violation.
    """
```

**`UnderwritingIngressEnvelope` fields** (new dataclass):
```
request_id: str
applicant_id: str
product_class: str
documents: tuple[dict, ...] = ()
metadata: dict = {}
trace_id: str = ""
submitted_at: str = ""
```

**`ValidatedUnderwritingRequest` fields** (new dataclass):
```
request_id, applicant_id, product_class, documents, metadata, trace_id
runtime_customization_package: dict   # ← all 17 YAML blobs keyed by config field names
input_contract: dict                   # from input_contract.yaml
route_profiles: dict                   # from route_profiles.yaml
threshold_profiles: dict               # from threshold_profiles.yaml
policy_hash: str                       # from app_domain_manifest.yaml
blueprint_hash: str                    # from app_domain_manifest.yaml
app_domain_manifest: dict              # from app_domain_manifest.yaml
```

---

## Wave 3 — Wire __main__.py + Stub Remaining Bindings

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**`__main__.py` changes**:
- Remove `_resolve_capability`, `_r5_terminal`, `_run_demo`, `_run_from_file`
- Remove import of `underwriting_capability_registry`
- Replace `_run_demo` with call to `u0_validate_underwriting` + print the `ValidatedUnderwritingRequest.runtime_customization_package` summary
- Replace `_run_from_file` with: parse file → build `UnderwritingIngressEnvelope` → `u0_validate_underwriting` → (stub) dispatch
- `_run_live_cert` keeps `apps_shared.spine_emission.governed_run` — it is the cert harness, not a parallel pipeline

**Stub bindings** (TODO stubs, no logic, just wire the dispatch shape):
- `apps_underwriting_ai/runtime/bindings/l1_binding.py`
- `apps_underwriting_ai/runtime/bindings/l0_binding.py`
- `apps_underwriting_ai/runtime/bindings/c0_binding.py` (wraps `UnderwritingC0Adapter.run()`)
- `apps_underwriting_ai/runtime/bindings/pa_binding.py`
- `apps_underwriting_ai/runtime/bindings/l2_binding.py` (wraps L2 step adapters)
- `apps_underwriting_ai/runtime/bindings/exit_binding.py`
- `apps_underwriting_ai/runtime/dispatch/underwriting_dispatch.py`

---

## Wave 4 — Tests + CI Gates

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Tests**:
- Update any tests that imported deleted parallel path files
- `tests/_apps_contract/test_apps_underwriting_ai_u0_binding.py` — covers:
  - valid envelope → `ValidatedUnderwritingRequest` with all 17 config fields populated
  - missing `request_id` → raises fail-closed
  - forbidden input (`protected_attribute_direct_input`) → raises fail-closed
  - `runtime_customization_package` contains `policy_hash` from manifest
- `tests/_apps_contract/test_apps_underwriting_ai_import.py` — `python -m apps_underwriting_ai --help` exits 0

**CI gates**:
- `ops_scripts/ci/check_apps_underwriting_ai_import.py` — import gate
- `ops_scripts/ci/check_apps_underwriting_ai_no_parallel_path.py` — asserts none of the deleted files exist at their old paths; asserts `__main__.py` does NOT import `underwriting_capability_registry` or `governed_underwriting_run`

---

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| DoD-1 | `python -m apps_underwriting_ai --help` exits 0 | CI import gate |
| DoD-2 | `governed_underwriting_run.py`, `execution_adapter.py`, `underwriting_ingress_runner.py`, `spine_handoff.py`, `underwriting_capability_registry.py` do NOT exist at their original paths | `check_apps_underwriting_ai_no_parallel_path.py` |
| DoD-3 | `__main__.py` does NOT import `underwriting_capability_registry` or `governed_underwriting_run` | `grep` assertion in CI gate |
| DoD-4 | `ValidatedUnderwritingRequest.runtime_customization_package` contains all 17 domain_contract YAML blobs when U0 runs | `test_apps_underwriting_ai_u0_binding.py` |
| DoD-5 | `python -m apps_underwriting_ai --demo` prints `U0 validated` banner (not `STUB_OK`) and exits 0 | Manual smoke + test |

### Verification-vs-Deferral

| Item | Verification method | Deferred? |
|---|---|---|
| Full `agentic_core` dispatch chain (L1–Exit) | Deferred to follow-on plan | ✅ Deferred — W3 stubs are explicit TODO |
| Real LLM call on L2 | Deferred | ✅ Deferred |
| `check_apps_underwriting_ai_no_parallel_path.py` CI registration | W4 | In scope |

