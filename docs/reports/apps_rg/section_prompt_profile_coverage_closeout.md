# Section prompt profile coverage closeout (Wave 2)

**Status:** PARTIAL  
**Generated:** 2026-05-18

## What changed

Restored seven managed-workflow section prompt profiles from commit `0b49b51f53` into [apps_rg/config/section_prompts/](apps_rg/config/section_prompts/). [skills_block.yaml](apps_rg/config/section_prompts/skills_block.yaml) was already present and left unchanged.

## Verification

| Gate | Result |
|------|--------|
| `ManagedWorkflowPAResolver` (8 nodes) | All resolve; `output_schema_ref` + BOM slots valid |
| `pytest -k "section_prompt or prompt_profile or bom_slots or output_schema_ref"` | 80 passed, **11 failed**, 1 skipped |
| `pytest -k "skills or arsenal or srfs or role_family"` | 197 passed, 1 skipped |
| `pytest tests/unit/apps_rg/fact_inventory` | 60 passed |
| Augmented skills graph + CRO hardening (scoped) | 60 passed |
| `git diff -- agentic_core` | Empty |

## Qwen X2 hardening readiness

**Ready for canonical section lane work:** headline, executive_summary, competencies, unify_*, ibm_*, education, certifications, early_career compile through `section_prompt_adapter` + `section_prompt_contracts/` + `prompt_assembly/templates/` — unchanged by this wave.

**Ready for managed-workflow PA:** all eight `config/section_prompts/*.yaml` profiles exist and resolve through `ManagedWorkflowPAResolver`.

**Not ready (out of scope):** `test_apps_rg_pa_tiered_prompt.py` still fails — missing `resume_pa_prompt_profile.v1.json` and `SectionPromptArtifact.prompt_directive` API drift. This is tiered-treatment config, not section prompt YAML coverage.

## Open gaps

See [section_prompt_profile_coverage_closeout.json](section_prompt_profile_coverage_closeout.json) `open_gaps`.

## Artifacts

- Wave 1 audit: [section_prompt_profile_coverage_audit.md](section_prompt_profile_coverage_audit.md), [section_prompt_profile_coverage_audit.json](section_prompt_profile_coverage_audit.json)
- Wave 2 closeout: this file + [section_prompt_profile_coverage_closeout.json](section_prompt_profile_coverage_closeout.json)
