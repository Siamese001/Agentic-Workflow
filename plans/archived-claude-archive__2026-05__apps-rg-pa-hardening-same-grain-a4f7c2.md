---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-pa-hardening-same-grain-a4f7c2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-pa-hardening-same-grain-a4f7c2.md'
source_sha256: 5ce4dfccb35dabb793914728d4e697000c8e09f7db3eadf5f75322cf91754d17
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Prompt Assembly Hardening — Same-Grain Upgrade

> **Slug**: `apps-rg-pa-hardening-same-grain-a4f7c2`
> **Parent plan**: `apps-rg-pa-bom-compiled-artifact-final-b8e2d1` (Completed)
> **Pattern source**: `apps_lic` Prompt Assembly hardening grain
> **Status**: Live

## 1. Context

apps_rg has a prior PA integration (parent plan) that established:
- `contracts.py` with `AppsRgCompiledPromptArtifact` and 5-slot model (S0/I0/C0/U0/R0)
- `compiler.py` that loads a `prompt_bom.yaml` and loose `.md` templates
- `slot_mapper.py` with 5-slot mapping and untrusted-data fencing
- `provider_request.py` adapter
- `_PAGuard` in `steps.py` with compile-on-demand

**Problem**: The current implementation is still too abstract compared to `apps_lic`:
- Templates are loose Markdown files, not governed YAML artifacts
- Only 4 E3_EXEC templates exist; no E4_HEAL or E5_SEAL templates
- 5-slot model missing D0 (origin/injection fences), E0 (approved examples), Y0 (style prefs)
- No `prompt_registry.yaml`
- Compiler has no registry awareness, no manifest_hash, no canonical_slot_bytes_hash
- Contracts missing `template_version`, `prompt_registry_hash`, `manifest_hash`, `canonical_slot_bytes_hash`, `origin_label_map`, `local_evidence_contract_ref`, `audit_refs`

## 2. Target Architecture

```
prompt_bom.yaml (8-slot, 8-template refs)
  → prompt_registry.yaml (template path, required_slots, output_contract, allowed_stage)
    → templates/*.yaml (governed YAML with slot_bodies, forbidden_behaviors, validation_rules)
      → rg_pa_compiler.py (registry-aware, hash-bound, deterministic)
        → CompiledPromptArtifact (all required fields)
          → artifact_to_provider_request (hash-validated)
            → L2 step (artifact-only model call)
              → sealed L2 output with artifact refs
```

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1-P4 | BOM + Registry + 8 YAML Templates | ~15k | Template bodies from user spec | 🔲 TODO | All 8 templates exist, YAML-governed, real bodies |
| W2 | P5-P8 | Contracts + Compiler + SlotMapper + Provider | ~12k | Backward-compatible upgrade | 🔲 TODO | 8-slot model, registry-aware compiler, all hashes |
| W3 | P9-P10 | L2 Steps + Spine Docs | ~5k | steps.py already has _PAGuard | 🔲 TODO | Steps use upgraded compiler, docs updated |
| W4 | P11 | 25 Hard Governance Tests | ~20k | Tests cover all 25 specified cases | 🔲 TODO | All 25 tests pass |
| W5 | P12 | Acceptance + Regression | ~3k | Run all test suites | 🔲 TODO | All pass, no regressions |

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | New prompt_bom.yaml (8-slot) | apps_rg/prompt_assembly/prompt_bom.yaml | Replace old BOM at apps_rg/prompts/ | ~1k | 🔲 TODO |
| P2 | New prompt_registry.yaml | apps_rg/prompt_assembly/prompt_registry.yaml | New file | ~2k | 🔲 TODO |
| P3 | 4 E3_EXEC YAML templates | apps_rg/prompt_assembly/templates/*.yaml | Replace loose .md templates | ~8k | 🔲 TODO |
| P4 | 4 E4/E5 YAML templates | apps_rg/prompt_assembly/templates/*.yaml | New templates | ~4k | 🔲 TODO |
| P5 | Upgrade contracts.py | apps_rg/prompt_assembly/contracts.py | Add missing fields, 8-slot | ~2k | 🔲 TODO |
| P6 | Upgrade rg_pa_compiler.py | apps_rg/prompt_assembly/rg_pa_compiler.py + compiler.py | Registry-aware, all hashes | ~4k | 🔲 TODO |
| P7 | Upgrade slot_mapper.py | apps_rg/prompt_assembly/slot_mapper.py | 8-slot model | ~2k | 🔲 TODO |
| P8 | Upgrade provider_request.py | apps_rg/prompt_assembly/provider_request.py | Validate new fields | ~1k | 🔲 TODO |
| P9 | Update steps.py | apps_rg/l2_recipe/steps.py | Use upgraded compiler | ~2k | 🔲 TODO |
| P10 | Update spine docs | apps_rg/AGENTIC_SPINE.md, spine_manifest.yaml | Remove PA=False | ~1k | 🔲 TODO |
| P11 | 25 governance tests | tests/_apps_contract/test_apps_rg_*.py | 25 new test files | ~20k | 🔲 TODO |
| P12 | Acceptance + regression | Run all suites | Fix any failures | ~3k | 🔲 TODO |

## 5. Files to Create

- `apps_rg/prompt_assembly/prompt_bom.yaml` (replace old at apps_rg/prompts/)
- `apps_rg/prompt_assembly/prompt_registry.yaml`
- `apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml`
- `apps_rg/prompt_assembly/templates/tailor_existing_v1.yaml`
- `apps_rg/prompt_assembly/templates/generate_scratch_v1.yaml`
- `apps_rg/prompt_assembly/templates/enhance_current_v1.yaml`
- `apps_rg/prompt_assembly/templates/resume_fact_check_v1.yaml`
- `apps_rg/prompt_assembly/templates/unsupported_claim_omission_v1.yaml`
- `apps_rg/prompt_assembly/templates/bullet_diversity_repair_v1.yaml`
- `apps_rg/prompt_assembly/templates/docx_manifest_v1.yaml`
- 25 test files under `tests/_apps_contract/`

## 6. Files to Modify

- `apps_rg/prompt_assembly/contracts.py` — add missing fields, 8-slot
- `apps_rg/prompt_assembly/compiler.py` — registry-aware, all hashes
- `apps_rg/prompt_assembly/rg_pa_compiler.py` — real compiler (not just re-export)
- `apps_rg/prompt_assembly/slot_mapper.py` — 8-slot model
- `apps_rg/prompt_assembly/provider_request.py` — validate new fields
- `apps_rg/prompt_assembly/__init__.py` — re-exports
- `apps_rg/l2_recipe/steps.py` — use upgraded compiler
- `apps_rg/AGENTIC_SPINE.md` — PA = CANONICAL_PA
- `apps_rg/spine_manifest.yaml` — prompt_bom_ref, registry, compiled_artifact_required_for

## 7. Rollback Plan

All changes are additive or in-place upgrades to existing PA files. Old .md templates are superseded but not deleted (compiler no longer references them). Revert commit to restore prior state.

## 8. Non-Goals (Deferred)

- Wiring compiled artifact into `apps_rg/scripts/generate_resume.py` runtime model call path (requires RgResumeOrchestrator refactor)
- Wiring compiled artifact into `apps_rg/reasoning/RgResumeOrchestrator.py` (legacy orchestrator)
- Real E4_HEAL runtime integration (fact_check, claim_omission, bullet_diversity steps)
- Real E5_SEAL runtime integration (docx_manifest step)
- Removal of legacy `apps_rg/prompts/` loose .md files
- Provider gateway integration testing

## 9. Acceptance Commands

```bash
pytest tests/_apps_contract -k apps_rg -q
pytest tests/_apps_contract -q
```

## 10. Success Criteria

- [ ] PromptBOM exists with 8 required slots and 8 template_registry_refs
- [ ] Prompt registry exists with all 8 templates registered
- [ ] All 8 YAML templates contain real implementation-grade body content
- [ ] Every template has template_id, version, owner, purpose, allowed_stage, input_contract, required_slots, forbidden_behaviors, slot_bodies, output_contract, validation_rules, hash_fields
- [ ] rg_pa_compiler emits CompiledPromptArtifact with all required fields
- [ ] GenerateResumeStep requires compiled artifact or compiles from governed context
- [ ] Provider request path requires compiled artifact
- [ ] No ad hoc prompt strings in active generation paths
- [ ] Missing template fails closed
- [ ] Placeholder templates fail tests
- [ ] Prompt hash determinism verified
- [ ] Sealed L2 artifact references compiled prompt artifact
- [ ] AGENTIC_SPINE.md and spine_manifest.yaml say CANONICAL_PA
- [ ] All 25 new governance tests pass
- [ ] All prior apps_rg tests pass (no regressions)

**Final acceptance**: apps_rg is not spine-complete until its resume prompts are registry-defined, PromptBOM-bound, implemented as real template bodies, compiled by rg_pa_compiler into CompiledPromptArtifact-compatible artifacts, consumed by L2, enforced by the provider request path, sealed into L2 artifacts, and covered by hard governance tests.
