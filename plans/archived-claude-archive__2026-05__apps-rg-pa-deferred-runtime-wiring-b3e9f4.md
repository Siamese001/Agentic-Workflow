---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-pa-deferred-runtime-wiring-b3e9f4.md'
original_relative_path: '_archive\\2026-05\\apps-rg-pa-deferred-runtime-wiring-b3e9f4.md'
source_sha256: 6f3820aef92dad3b48f9fe7aa521945e334e6b40709bcffe9663b1fdd7158c67
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg PA Deferred — Runtime Wiring & Legacy Cleanup

> **Slug**: `apps-rg-pa-deferred-runtime-wiring-b3e9f4`
> **Parent plan**: `apps-rg-pa-hardening-same-grain-a4f7c2` (Completed)
> **Pattern source**: `apps_lic` PA runtime wiring
> **Status**: Not Started

## 1. Context

The parent plan delivered the full PA governance surface for apps_rg:
- 8-slot BOM, prompt registry, 8 governed YAML templates
- Registry-aware compiler with 7 hash fields
- Provider request validation, L2 _PAGuard, sealed artifact refs
- 81 governance tests, 313 apps_rg tests passing

**What remains**: the compiled artifact is produced and validated at the L2 step boundary, but the **runtime model call path** inside `apps_rg/scripts/generate_resume.py` and `apps_rg/reasoning/RgResumeOrchestrator.py` still constructs its own prompts internally. The compiled artifact must be threaded into these runtime paths so that actual model calls use the governed artifact — not ad hoc strings.

Additionally, the E4_HEAL templates (fact_check, claim_omission, bullet_diversity) and E5_SEAL template (docx_manifest) are defined but not wired into runtime steps. Legacy `.md` templates under `apps_rg/prompts/` are superseded but not removed.

## 2. Non-Goals (explicitly out of scope)

- Re-implementing the PA governance surface (done in parent plan)
- Modifying BOM, registry, or template YAML content (stable)
- Changing the compiler, contracts, or slot_mapper (stable)
- Provider gateway integration testing beyond apps_rg

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1-P2 | Thread artifact into generate_resume.py + RgResumeOrchestrator | ~8k | Orchestrator accepts compiled artifact dict | 🔲 TODO | Model calls use artifact messages, not ad hoc strings |
| W2 | P3-P5 | Wire E4_HEAL + E5_SEAL templates into runtime steps | ~6k | Steps exist in steps.py or need creation | 🔲 TODO | fact_check, claim_omission, bullet_diversity, docx_manifest steps compile and use artifacts |
| W3 | P6-P7 | Legacy cleanup + provider gateway smoke test | ~4k | .md templates no longer referenced | 🔲 TODO | Old prompts/ dir cleaned, provider request round-trip verified |

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Thread artifact into generate_resume.py | apps_rg/scripts/generate_resume.py | Internal prompt construction must yield to compiled artifact | ~4k | 🔲 TODO |
| P2 | Thread artifact into RgResumeOrchestrator | apps_rg/reasoning/RgResumeOrchestrator.py | Legacy orchestrator builds its own prompts | ~4k | 🔲 TODO |
| P3 | Wire fact_check + claim_omission steps | apps_rg/l2_recipe/steps.py | New L2 steps or integration into existing pipeline | ~3k | 🔲 TODO |
| P4 | Wire bullet_diversity_repair step | apps_rg/l2_recipe/steps.py | Same pattern as P3 | ~1.5k | 🔲 TODO |
| P5 | Wire docx_manifest step | apps_rg/l2_recipe/steps.py | E5_SEAL template integration | ~1.5k | 🔲 TODO |
| P6 | Remove legacy .md templates | apps_rg/prompts/*.md | Confirm no remaining references | ~1k | 🔲 TODO |
| P7 | Provider gateway smoke test | Integration test | Verify end-to-end artifact → provider request | ~2k | 🔲 TODO |

## 5. Files to Modify

- `apps_rg/scripts/generate_resume.py` — accept and use compiled artifact for model calls
- `apps_rg/reasoning/RgResumeOrchestrator.py` — accept compiled artifact, replace ad hoc prompt construction
- `apps_rg/l2_recipe/steps.py` — add FactCheckStep, ClaimOmissionStep, BulletDiversityRepairStep, DocxManifestStep (or wire templates into existing steps)

## 6. Files to Delete

- `apps_rg/prompts/*.md` — legacy loose Markdown templates (superseded by `apps_rg/prompt_assembly/templates/*.yaml`)

## 7. Tests to Add

- `tests/_apps_contract/test_apps_rg_runtime_artifact_threading.py` — verify generate_resume.py uses compiled artifact
- `tests/_apps_contract/test_apps_rg_e4_heal_steps.py` — fact_check, claim_omission, bullet_diversity step tests
- `tests/_apps_contract/test_apps_rg_e5_seal_step.py` — docx_manifest step test
- `tests/_apps_contract/test_apps_rg_legacy_cleanup.py` — no remaining references to old .md templates

## 8. Rollback Plan

Each wave is independently revertable. W3 (cleanup) should only execute after W1+W2 are verified. Legacy .md files can be restored from git history if needed.

## 9. Acceptance Commands

```bash
pytest tests/_apps_contract -k apps_rg -q
pytest tests/_apps_contract -q
# Verify no references to old .md templates:
# rg "apps_rg/prompts/" --include="*.py" --include="*.yaml"
```

## 10. Success Criteria

- [ ] generate_resume.py model calls use compiled artifact messages
- [ ] RgResumeOrchestrator uses compiled artifact, not ad hoc strings
- [ ] E4_HEAL templates (fact_check, claim_omission, bullet_diversity) wired into runtime steps
- [ ] E5_SEAL template (docx_manifest) wired into runtime step
- [ ] Legacy `apps_rg/prompts/*.md` files removed with zero remaining references
- [ ] Provider request round-trip verified via integration test
- [ ] All new tests pass, all existing tests pass (no regressions)
