# CRO projection — broad contract failure closeout

**Generated:** 2026-05-18 (post-fix verification)

## Summary

Eight failures under `-k "skills or arsenal or srfs or role_family"` were reproduced. All eight are **in scope** for this seam: six trace to a missing `skills_block.yaml`, two to proof-pool IBM company-hint min-fact gating. **None were regressions from CRO composite projection hardening.**

| Classification | Count |
|----------------|-------|
| Fixed | 8 |
| Quarantined (pre-existing, unrelated) | 0 |
| CRO regression | 0 |

## Failure matrix

| # | Test | Root cause | Fix |
|---|------|------------|-----|
| 1 | `test_section_prompt_file_exists[skills_block.yaml]` | `section_prompts/` never restored after slim consolidation | Restored `skills_block.yaml` from `0b49b51f53` |
| 2 | `test_section_prompt_structure[skills_block.yaml-skills_block]` | Same | Same |
| 3 | `test_no_quarantine_module_import_in_section_prompt[skills_block.yaml]` | Same | Same |
| 4 | `test_apps_rg_pa_resolves_section_prompt_profiles[skills_block]` | PA fail-closed without template | Same |
| 5 | `test_output_schema_ref_non_empty_for_all_nodes[skills_block]` | Invalid artifact (missing template) | Same |
| 6 | `test_section_prompt_slots_are_valid_bom_slots[skills_block.yaml]` | Same | Same |
| 7 | `test_default_resolves_broad_skills_ledger_when_srfs_absent[ibm_bullets]` | 3 IBM ledger rows < `min_section_facts` 6 → base resume fallback | Partial company-hint accepts ledger when `fact_count > 0` |
| 8 | `test_default_resolves_broad_skills_ledger_when_srfs_absent[ibm_narrative]` | Same | Same |

## Fixes applied

1. **[skills_block.yaml](apps_rg/config/section_prompts/skills_block.yaml)** — Restored declarative PA profile (deterministic skills extraction; no new LLM claims).
2. **[proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py)** — When company-hint slice has fewer facts than `min_section_facts` but at least one ledger row, still return `broad_skills_ledger` instead of `base_resume_fallback`.

## Quarantined gaps

None for this filter. Other missing `section_prompts/*.yaml` files (e.g. `header_block.yaml`) are **not** exercised by this `-k` expression; they remain a separate pre-existing gap if the full domain-config suite is run without filter.

## CRO profile invariants (unchanged)

- No standalone `CRO` role family in [master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml)
- Composite profile `CHIEF_REVENUE_OFFICER_COMPOSITE` only in [composite_projection_profiles.yaml](apps_rg/config/domain_contract/composite_projection_profiles.yaml) and arsenal ledger
- `fact_customer_success_001` (LOW) and `fact_sales_accounts_004/005` (NEEDS_VERIFICATION) not promoted to authoritative skills

## Explicit non-claims

- Restoring `skills_block.yaml` does not add skills to the candidate profile or arsenal graph.
- Partial IBM ledger slices (3 facts) do not satisfy production `min_section_facts=6` for full bullet lanes; they only satisfy contract default-resolution when SRFS is absent.
- JD/briefing remain targeting-only per proof-pool metadata.

Machine-readable: [cro_projection_contract_failure_closeout.json](cro_projection_contract_failure_closeout.json)
