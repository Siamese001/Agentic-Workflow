---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pa-bom-compiled-artifact-final-b8e2d1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pa-bom-compiled-artifact-final-b8e2d1.md'
source_sha256: e4c3a1c91c8161cee3b2c7f9baf2629622b1c178b00b7f3f4b05590b5ba380ac
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg PA BOM → CompiledPromptArtifact Integration

> Turn the PA guard stub into the real PromptBOM → CompiledPromptArtifact → governed model call path.

## Context

The prior apps_rg core-bound execution refactor is complete (plan `apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2`):
- `apps_rg/__main__.py` is a pure shim.
- `agentic_core` owns R4 execution and L2 recipe resolution.
- `apps_rg/l2_recipe/steps.py` has `GenerateResumeStep` with a stub `_PAGuard`.
- Missing recipe and `l2_callable` injection both fail closed.

**Gap**: The PA guard is a stub that checks for `pa_compatible` / `prompt_bom_dir` context flags.
It does NOT compile a real `CompiledPromptArtifact`. Model calls can still bypass PA if
the context flag is set without actually compiling prompts.

## Target Architecture

```
apps_rg/prompts/prompt_bom.yaml          # Prompt Bill of Materials
apps_rg/prompts/resume_generation/*.md    # Domain prompt templates (4 flows)
apps_rg/prompt_assembly/contracts.py      # PA contract types
apps_rg/prompt_assembly/compiler.py       # BOM → CompiledPromptArtifact compiler
apps_rg/prompt_assembly/slot_mapper.py    # Slot mapping (S0/I0/C0/U0/R0)
apps_rg/prompt_assembly/provider_request.py # Artifact → provider request adapter
apps_rg/l2_recipe/steps.py               # Updated: compile before model call
```

Flow:
1. `GenerateResumeStep` receives L2 context with JD, resume, brief, flow route
2. Loads `prompt_bom.yaml`, selects prompt_id by flow route
3. PA compiler loads template, computes hashes, maps slots, validates
4. Emits `CompiledPromptArtifact`-compatible dict with all required fields
5. `provider_request.py` renders artifact into provider-specific messages
6. Model call uses ONLY artifact-rendered request
7. Step result references compiled artifact hashes/replay metadata

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | P1-P3 | Prompt inventory + PA contracts + compiler | ~25K | Existing pa_local.py shape is compatible | ✅ DONE | BOM exists, contracts defined, compiler emits artifact |
| W2 | P4-P6 | Wire into L2 step + model call path + sealing | ~20K | GenerateResumeStep can call compiler in-step | ✅ DONE | Step requires artifact, provider uses artifact only |
| W3 | P7-P8 | Docs/manifests + tests | ~15K | Existing 137 tests remain green | ✅ DONE | 8 new test files pass, spine docs updated |
| W4 | P9-P10 | Acceptance + plan completion | ~5K | — | ✅ DONE | 232 passed, 0 failed |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Prompt inventory (BOM + templates) | 5 new files | None | ~5K | ✅ DONE |
| P2 | PA contracts | 1 new file | Type shape alignment | ~5K | ✅ DONE |
| P3 | PA compiler + slot mapper + provider adapter | 3 new files | Hash computation | ~15K | ✅ DONE |
| P4 | Wire compile into L2 step | 1 edit | Guard→compile transition | ~8K | ✅ DONE |
| P5 | Provider request adapter | 1 new file | Provider format | ~5K | ✅ DONE |
| P6 | Sealing / artifact output | 1 edit | Artifact ref in step result | ~5K | ✅ DONE |
| P7 | Update AGENTIC_SPINE.md + spine_manifest.yaml | 2 edits | Prose accuracy | ~3K | ✅ DONE |
| P8 | Tests (8 new test files) | 8 new files | Mock boundaries | ~12K | ✅ DONE |
| P9 | Acceptance commands | — | — | ~3K | ✅ DONE |
| P10 | Mark plan complete + Notion | 1 edit | — | ~2K | ✅ DONE |

## Files to Create

- `apps_rg/prompts/prompt_bom.yaml`
- `apps_rg/prompts/resume_generation/strategic_tailor.md`
- `apps_rg/prompts/resume_generation/tailor_existing.md`
- `apps_rg/prompts/resume_generation/generate_scratch.md`
- `apps_rg/prompts/resume_generation/enhance_current.md`
- `apps_rg/prompt_assembly/contracts.py`
- `apps_rg/prompt_assembly/compiler.py`
- `apps_rg/prompt_assembly/slot_mapper.py`
- `apps_rg/prompt_assembly/provider_request.py`
- `tests/_apps_contract/test_apps_rg_prompt_bom_exists.py`
- `tests/_apps_contract/test_apps_rg_pa_compiles_prompt_artifact.py`
- `tests/_apps_contract/test_apps_rg_prompt_slots_fence_untrusted_data.py`
- `tests/_apps_contract/test_apps_rg_generate_step_requires_compiled_prompt_artifact.py`
- `tests/_apps_contract/test_apps_rg_generate_step_uses_compiled_artifact_only.py`
- `tests/_apps_contract/test_apps_rg_no_ad_hoc_prompt_model_call.py`
- `tests/_apps_contract/test_apps_rg_prompt_artifact_in_sealed_l2_output.py`
- `tests/_apps_contract/test_apps_rg_pa_failure_blocks_model_call.py`

## Files to Modify

- `apps_rg/l2_recipe/steps.py` — Replace stub guard with real compile-then-call
- `apps_rg/AGENTIC_SPINE.md` — Update PA property
- `apps_rg/spine_manifest.yaml` — Remove template_ids: [] placeholder if present
- `apps_rg/prompt_assembly/__init__.py` — Re-exports

## Rollback Plan

All new files can be deleted. `steps.py` edit is revertible — the stub guard still works.
`AGENTIC_SPINE.md` and `spine_manifest.yaml` are documentation-only changes.

## Acceptance Commands

```bash
pytest tests/_apps_contract/test_apps_rg_prompt_bom_exists.py -q
pytest tests/_apps_contract/test_apps_rg_pa_compiles_prompt_artifact.py -q
pytest tests/_apps_contract/test_apps_rg_prompt_slots_fence_untrusted_data.py -q
pytest tests/_apps_contract/test_apps_rg_generate_step_requires_compiled_prompt_artifact.py -q
pytest tests/_apps_contract/test_apps_rg_generate_step_uses_compiled_artifact_only.py -q
pytest tests/_apps_contract/test_apps_rg_no_ad_hoc_prompt_model_call.py -q
pytest tests/_apps_contract/test_apps_rg_prompt_artifact_in_sealed_l2_output.py -q
pytest tests/_apps_contract/test_apps_rg_pa_failure_blocks_model_call.py -q
pytest tests/_apps_contract -k apps_rg -q
pytest tests/_apps_contract -q
```

## Success Criteria

- [x] `apps_rg/prompts/prompt_bom.yaml` exists with 4 prompt entries
- [x] 4 prompt templates exist under `apps_rg/prompts/resume_generation/`
- [x] PA contracts define `AppsRgCompiledPromptArtifact` with all required fields
- [x] PA compiler loads BOM, selects template, computes hashes, emits artifact
- [x] `GenerateResumeStep` compiles artifact before model call
- [x] PA failure blocks model call (fail-closed)
- [x] No ad-hoc prompt-provider path remains
- [x] Sealed L2 output references compiled prompt artifact
- [x] `AGENTIC_SPINE.md` no longer says `APP_LOCAL_PA_COMPATIBLE` — says `CANONICAL_PA`
- [x] `spine_manifest.yaml` references prompt_bom
- [x] 8 new test files pass (95 new tests)
- [x] All existing apps_rg tests pass (232 total, 0 regressions)
