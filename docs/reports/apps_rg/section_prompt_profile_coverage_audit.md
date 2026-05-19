# Section prompt profile coverage audit (Wave 1)

**Generated:** 2026-05-18  
**Scope:** `apps_rg` section prompt profile coverage only (no SRFS/X2/X3, no `agentic_core`, no live LLM).

## Executive summary

Two prompt surfaces coexist in `apps_rg`:

| Surface | SSOT path | Runtime consumer |
|---------|-----------|------------------|
| Managed workflow BOM nodes | `apps_rg/config/section_prompts/<node_id>.yaml` | `ManagedWorkflowPAResolver` (W7/W9 managed workflow, domain-config tests) |
| Canonical Qwen section lanes | `apps_rg/prompt_assembly/section_prompt_contracts/*.contract.yaml` + `templates/*.yaml` | `section_prompt_adapter` + section lanes / dispatch PA |

**Pre-closeout gap:** Only `skills_block.yaml` existed under `config/section_prompts/`; seven managed-workflow profiles were absent on disk but still referenced by PA resolver, domain-config tests, and W9 E2E entry.

**Canonical lanes** (headline, executive_summary, competencies, unify_*, ibm_*, education, certifications, early_career) do **not** use `config/section_prompts/`; their contracts and templates are present and exercised by runtime lanes.

## Wave 1 commands

| Command | Result |
|---------|--------|
| `git diff -- agentic_core` | No diff |
| `python -m compileall apps_rg tests -q` | Exit 0 |
| `pytest tests/_apps_contract -k "section_prompt or prompt_profile or bom_slots or output_schema_ref"` | 34 passed, 57 failed (pre-restore) |

## Managed workflow matrix (`config/section_prompts/`)

| profile_name | file_exists (audit) | verdict (audit) | active_runtime_path |
|--------------|---------------------|-----------------|---------------------|
| header_block | false | MISSING_ACTIVE | true |
| professional_summary | false | MISSING_ACTIVE | true |
| experience_block | false | MISSING_ACTIVE | true |
| skills_block | true | PASS | true |
| education_block | false | MISSING_ACTIVE | true |
| certifications_block | false | MISSING_ACTIVE | true |
| selected_projects_block | false | MISSING_ACTIVE | true |
| final_render | false | MISSING_ACTIVE | true |

## Canonical lane matrix (contracts + templates)

All ten lane contracts exist under `section_prompt_contracts/` with matching `apps_rg_prompt_template_ref` templates. These are **not** gaps in `config/section_prompts/` — intentionally separate SSOT.

## Out-of-scope failures in pytest filter

`test_apps_rg_pa_tiered_prompt.py` (11 tests) expects `apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json` and `SectionPromptArtifact.prompt_directive` — a **tiered-treatment profile**, not a `section_prompts/*.yaml` file. Not restored in this wave.

## Machine-readable SSOT

- [section_prompt_profile_coverage_audit.json](section_prompt_profile_coverage_audit.json)
