---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-provider-authenticity-gate-c4f8b2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-provider-authenticity-gate-c4f8b2.md'
source_sha256: 941674ee64c416473c0e0b39f6a7822fad5ae71cca174f48c04c0779951019ee
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-provider-authenticity-gate-c4f8b2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg: Provider authenticity fast-fail for normal full résumé CLI

Add an **apps_rg-local** provider authenticity and artifact gate so normal CLI full résumé runs never silently use stub output, never authorize full success without real artifacts, and never treat stub receipts as `REAL_RESUME` / X3D full success — while preserving **explicit** stub/dry-run/test paths.

> **plan_id discipline**: filename stem `apps-rg-provider-authenticity-gate-c4f8b2` matches `plan_id` above. Markers: `plan=apps-rg-provider-authenticity-gate-c4f8b2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-16

---

## Context (SCQA)

- **Situation** — `apps_rg` L2 envelope resolves providers via `apps_rg/runtime/bindings/l2_envelope_adapter.py` (`_resolve_l2_envelope_provider_mode`, `_provider_profile_for_cpa`). When `ProviderMode` is `LOCAL_ONLY` / `LIVE_ALLOWED` but CPA `target_provider` does not match a known live lane, resolution **falls through** to `ProviderProfile` with `profile_id="apps_rg_envelope_stub"` and `ProviderKind.STUB` — a **silent** substitution. vLLM or HTTP failures can combine with stub/no-output paths so CLI may exit `0` with `outcome_authorized=True` without `outputs/generated_resume.json` or `outputs/resume.docx`.
- **Complication** — Operators interpret exit `0` and X3 as “full résumé succeeded” when only a stub receipt or empty manifest was produced. This violates honest runtime proof and the apps_rg résumé contract (`resume_generation_contract.py`, `resume_output_shape.py`, `l2_recipe/steps.py`).
- **Question** — How do we classify provider intent, fast-fail **normal** full résumé runs before generation when the effective provider is stub-only without explicit permission, propagate `FAILED_PROVIDER` without stub fallback, and bind artifacts + `generation_status` so X3D full success requires `REAL_RESUME` and required files?
- **Answer** — Introduce a **provider mode classifier** (`LIVE_REQUIRED` | `EXPLICIT_STUB` | `TEST_STUB` | `UNKNOWN`), enforce a **pre-generation authenticity gate** and **post-generation artifact gate** in `apps_rg` (profile/runtime/recipe/validators/package), extend receipts/manifests with `generation_status` and `provider_error` vectors, and add contract/unit tests; **no** `agentic_core` weakening; reuse generic hooks only if already present (otherwise stay app-local).

---

## Status Tables

### Wave Progress (plan-location columns)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Classifier + pre-gen fast-fail + FAILED_PROVIDER (no stub fallback) | ~18K | Sovereign/gateway surfaces stable; stub env semantics unchanged for tests | 🔲 TODO | Normal full path never resolves to stub without explicit mode; provider HTTP/timeout → `FAILED_PROVIDER`, non-zero / not authorized |
| W2 | W2.1–W2.2 | Artifact gate + REAL_RESUME sections + manifest/docx_verified | ~14K | Existing manifest and docx verify hooks identifiable | 🔲 TODO | Missing JSON/DOCX/manifest or section gaps block “full success”; `docx_verified=true` required |
| W3 | W3.1 | Exit/X3 binding + integration verification (Brown & Brown CLI) | ~10K | Live vLLM optional for CI; contract tests mock provider | 🔲 TODO | X3D full success iff `REAL_RESUME` + artifacts; explicit stub → `STUB_RECEIPT`, `full_resume_generated=false` |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Provider mode classifier module (`apps_rg`) + unit tests | 🔲 TODO |
| W1.2 | Pre-generation gate: block `apps_rg_envelope_stub` / stub gateway unless `EXPLICIT_STUB` or `TEST_STUB` | 🔲 TODO |
| W1.3 | Provider errors: map 400/500/timeout → `FAILED_PROVIDER`, carry `provider_error`, no stub downgrade | 🔲 TODO |
| W2.1 | Required artifact gate: paths + `docx_verified` + `apps_rg_output_manifest.json` | 🔲 TODO |
| W2.2 | REAL_RESUME section lint: headline, executive_summary, competencies, professional_experience, education, certifications | 🔲 TODO |
| W3.1 | Wire `generation_status` / authenticity into deterministic path before X3 (`resume_package_x3.py` or apps_rg gate consumed by Exit) | 🔲 TODO |

---

## Out Of Scope

- Removing or rewriting stub provider implementation used by CI.
- Changing global Exit/X3 **contracts** in `agentic_core` (only consume/bind **existing** fields or add **apps_rg-local** gate inputs already allowed by U0/package).
- Faking or synthesizing `generated_resume.json` / `resume.docx` for success.
- Broad refactors of vLLM client or recipe steps beyond failure classification and gating.

---

## Root cause pointer (implementation seed)

Silent stub fallback today — final branch in `_provider_profile_for_cpa` returns `apps_rg_envelope_stub` when target provider is not classified as local vLLM and external profile is not selected:

```445:450:apps_rg/runtime/bindings/l2_envelope_adapter.py
    return ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
        model_id=mid,
        capabilities=("text_generation", "structured_json_generation"),
        sandbox_safe=True,
        requires_network=False,
    )
```

**Plan**: For **normal full résumé** mode, replace this silent return with **BLOCKED** / explicit error (or never return stub unless mode is `STUB_ONLY` / test harness). Keep stub return only inside `ProviderMode.STUB_ONLY` branch and explicit test entrypoints.

---

## Wave 1 — Classifier, fast-fail, provider failure

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

### W1.1 — Provider mode classifier

**Deliverable**: New module under `apps_rg/runtime/providers/` or `apps_rg/runtime/gates/` (TBD during execution) exporting:

| Enum / value | Meaning |
|----------------|---------|
| `LIVE_REQUIRED` | Normal full résumé CLI / production-like run; stub forbidden unless overridden by explicit receipt mode |
| `EXPLICIT_STUB` | User/request flagged `stub_receipt` / dry-run / CLI flag / env clearly requesting receipt-only |
| `TEST_STUB` | Pytest/CI `APPS_RG_L2_PROVIDER_MODE=stub_only`, `APPS_RG_L2_FORCE_STUB=1`, or `conftest` contract fixtures |
| `UNKNOWN` | Cannot classify; **fail-closed** for `LIVE_REQUIRED` contexts |

**Inputs**: `APPS_RG_L2_PROVIDER_MODE`, `APPS_RG_L2_FORCE_STUB`, resume artifact contract mode (`resume_generation_contract.normalize_resume_artifact_contract_mode`), optional CLIargv flags, `ProviderProfile.profile_id`, `ProviderKind`, gateway class name / registry id if available.

### W1.2 — Fast-fail rule (normal full résumé)

Before L2 generation batch (earliest stable seam — likely `canonical_dispatch`, `integrated_r4_deterministic_pipeline_run` app overlay, or `apps_rg` CLI after profile resolution):

Fail with **`generation_status=BLOCKED_STUB_PROVIDER`**, **`full_resume_generated=false`**, **`terminal_class=FAILURE` or `BLOCKED`**, when **any** of:

- `profile_id` contains `"stub"` (case-normalized) **and** mode is not `EXPLICIT_STUB` / `TEST_STUB`
- Resolved mode is stub-only **without** explicit/test exemption
- `APPS_RG_L2_FORCE_STUB=1` **and** run is classified `LIVE_REQUIRED`
- Gateway resolves to Stub provider class in live context

**Explicit stub exception**: When `EXPLICIT_STUB` or `TEST_STUB`, allow stub execution but downstream must set **`generation_status=STUB_RECEIPT`** (or existing aligned constant), **`full_resume_generated=false`**, and must **not** claim full résumé success or X3D full allow for full package.

### W1.3 — Provider failure (no fallback)

On live provider 400/500/timeout/connection failure:

- **`generation_status=FAILED_PROVIDER`**
- **`full_resume_generated=false`**
- Propagate structured **`provider_error`** into attempt receipts, run manifest, terminal packet
- **Do not** call stub path
- CLI: non-zero exit and/or **`outcome_authorized=false`** consistent with existing spine enums

---

## Wave 2 — Artifacts and REAL_RESUME

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

### W2.1 — Required artifact gate

Full résumé success requires (paths relative to run dir, align with existing artifacts layout):

- `outputs/generated_resume.json` exists (non-empty JSON object)
- `outputs/resume.docx` exists
- `apps_rg_output_manifest.json` exists
- `docx_verified=true` in manifest or parallel receipt (match existing field names in codebase)

### W2.2 — REAL_RESUME classification

Extend or reuse shape contract in `resume_output_shape.py` / orchestration:

- `generated_resume` must classify as **`REAL_RESUME`** (new enum or string constant set: `REAL_RESUME` vs `STUB_RECEIPT` vs failure states)
- Required top-level/section keys present: **headline**, **executive_summary**, **competencies**, **professional_experience**, **education**, **certifications** (exact schema paths to mirror `resume_output_shape` / sealed extract)

---

## Wave 3 — Exit binding and smoke

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

### W3.1 — X3 / Exit visibility

- Surface `provider_authenticity` / `generation_status` / `full_resume_generated` on objects already read by **`apps_rg/runtime/internal/resume_package_disposition.py`** (or add an apps_rg deterministic pre-X3 gate that sets blocking facts consumed by X3 aggregation).
- **Invariant**: X3D “full success” path requires **`REAL_RESUME`** and forbids **`STUB_RECEIPT`**, **`FAILED_PROVIDER`**, **`BLOCKED_STUB_PROVIDER`**.
- Do not weaken core X3; add inputs or lane block reasons only.

**Smoke (human)**: After implementation — normal Brown & Brown CLI with live vLLM; expect honest failure when vLLM down.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Classifier | New `apps_rg/runtime/.../provider_run_mode.py` (or similar), unit tests | Env matrix + conftest interaction | ~6K | 🔲 TODO |
| W1.2 | Pre-gen gate | `l2_envelope_adapter.py`, `canonical_dispatch.py`, CLI (`__main__.py`) | Single early seam vs duplicate checks | ~8K | 🔲 TODO |
| W1.3 | Failed provider | `qwen_vllm_provider.py`, envelope execute path, manifest writers | Error payload shape | ~6K | 🔲 TODO |
| W2.1 | Artifacts | Manifest builder, post-run verifier | Path drift across run ids | ~5K | 🔲 TODO |
| W2.2 | REAL_RESUME | `resume_output_shape.py`, `orchestrate_full_resume.py` | Locked deterministic sections vs generated | ~5K | 🔲 TODO |
| W3.1 | X3 wire | `resume_package_x3.py`, possibly exit profile YAML | Avoid core edits | ~4K | 🔲 TODO |

---

## Gap Register

**GAP-1: Earliest stable seam for fast-fail**
- **Details**: Profile resolution may occur inside envelope adapter; CLI may need duplicated check vs single helper called from adapter + dispatch.
- **Impact**: Medium — avoid double maintenance; prefer one `assert_provider_authentic_for_full_resume()` used from one orchestration entry.

**GAP-2: TEST_STUB vs EXPLICIT_STUB detection**
- **Details**: `tests/conftest.py` sets stub env globally; classifier must treat pytest as `TEST_STUB` without labeling developer CLI as test.
- **Impact**: High if wrong — false positives block CI or allow bad CLI.

---

## Definition of Done

| DoD | Outcome | Evidence | Status |
|-----|---------|----------|--------|
| DoD-1 | Normal full résumé never uses stub without explicit/test mode | Contract test: profile `apps_rg_envelope_stub` + `LIVE_REQUIRED` → fast-fail / `BLOCKED_STUB_PROVIDER` | TODO |
| DoD-2 | Live provider 400 does not stub-fallback | Mocked HTTP 400 test → `FAILED_PROVIDER`, not authorized | TODO |
| DoD-3 | Explicit stub = receipt only | `full_resume_generated=false`, `STUB_RECEIPT`, DOCX may exist as receipt | TODO |
| DoD-4 | Missing JSON or DOCX blocks success | Tests assert manifest/X3 outcome | TODO |
| DoD-5 | REAL_RESUME requires six sections | Unit test on shape classifier | TODO |
| DoD-6 | X3D full success requires REAL_RESUME + artifacts | Contract test on `resume_package_x3` or integrated packet | TODO |
| DoD-7 | Smoke-run Brown & Brown CLI | `python -m apps_rg ...` with real profile; vLLM down → honest fail | TODO |

### Smoke-run (executable surface)

```bash
# New focused tests (path TBD, e.g. tests/unit/apps_rg/test_provider_authenticity_gate.py)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_provider_authenticity_gate.py -q --tb=short -p pytest_timeout

# Regression slice
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_docx_export_recipe.py tests/unit/apps_rg/test_json_resume_docx.py -q --tb=short -p pytest_timeout
```

### Verification vs deferral

| Item | Verify now | Defer |
|------|------------|-------|
| Provider classifier unit tests | Yes | — |
| Live vLLM integration | Manual smoke only | CI uses mocks |
| Core Exit refactor | No | Forbidden unless pre-approved core charter |

---

## Scope Expansion Authorization

Uses standard markers from `.cursor/templates/execution-plan-template.md` if scope grows (e.g. new spine field in core).

---

## Execution output template (fill after implementation)

Copy to run summary / terminal packet:

```
STATUS:
FAST_FAIL_ADDED: yes/no
PROVIDER_MODE:
PROVIDER_PROFILE:
GENERATION_STATUS:
FULL_RESUME_GENERATED:
REQUIRED_ARTIFACTS:
- generated_resume_json:
- resume_docx:
- output_manifest:
- docx_verified:
EXIT_STATE:
- terminal_class:
- x3_disposition:
- outcome_authorized:
FILES_CHANGED:
COMMANDS_RUN:
TESTS_GATES:
ARTIFACT_DIR:
REMAINING_BLOCKER:
```

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-provider-authenticity-gate-c4f8b2 wave=1
WAVE_COMPLETE: plan=apps-rg-provider-authenticity-gate-c4f8b2 wave=1 note="+N tests, N files, scope=provider-gate"
```
