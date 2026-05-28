# Competencies Graph-Skill Rigor Wiring

**Generated:** 2026-05-28 · **Scope:** competencies only · **Status:** PASS (runtime proof deferred)

Final competencies output is generated from graph-backed **competency capability bundles**. Base
resume competencies are a rigor / seniority / technical-density / coverage **calibration baseline
only** — never source prose. Archive resumes are provenance inventory only. JD/briefing are targeting
only. E0 examples are style only.

## Authority model

| Source | Role |
|--------|------|
| Graph skills + linked source facts | content/proof authority |
| Base resume competencies | calibration baseline only |
| Archive resumes | candidate signal / provenance only |
| JD / briefing | targeting only |
| E0 examples | style only |
| Generic taxonomy labels | display wrappers only, never proof |

## Competency capability bundles

Data file: [competency_capability_bundles.json](../../../apps_rg/fact_inventory/competency_capability_bundles.json)

Required families (8) + optional supporting families (2 activated). Each bundle binds
`competency_bundle_id`, `capability_family`, `graph_skill_node_ids`, `linked_source_fact_ids`,
`employer_bindings`, `role_episode_bindings`, `allowed_sections`, `evidence_strength`,
`external_claim_policy`, `activation_status`, `base_rigor_family_match`, `seniority_signal`,
`technical_density_signal`, `commercial_or_operating_scope_signal`, and `target_relevance_rationale`.

| bundle_id | family | graph skill nodes | source facts |
|-----------|--------|-------------------|--------------|
| ccb_agentic_platforms | agentic_platforms | 3 | fact_engineering_platform_001 |
| ccb_runtime_governance | runtime_governance | 4 | fact_engineering_platform_001 |
| ccb_retrieval_context_engineering | retrieval_context_engineering | 4 | fact_engineering_platform_003 |
| ccb_llmops_reliability | llmops_reliability | 4 | fact_engineering_platform_003/004 |
| ccb_distributed_systems_engineering | distributed_systems_engineering | 3 | fact_engineering_platform_002 |
| ccb_platform_productization | platform_productization | 3 | fact_engineering_platform_006 |
| ccb_partnerships_ecosystem_execution | partnerships_ecosystem_execution | 4 | fact_partnerships_gtm_002 |
| ccb_engineering_leadership | engineering_leadership | 2 | fact_exec_001 |
| ccb_data_governance_security (optional) | data_governance_security | 2 | fact_solutions_002 |
| ccb_devsecops_delivery_governance (optional) | devsecops_delivery_governance | 2 | fact_engineering_platform_002 |

## Registry + guards

Module: [competency_capability_registry.py](../../../apps_rg/runtime/sections/competency_capability_registry.py)

`assert_competency_bundle_id_present`, `validate_competency_bundle`, `get_bundles_for_section`,
`reject_flat_taxonomy_only_bundle`, `reject_default_fid_only_support`, `reject_jd_only_skill`,
`reject_archive_prose_hydration`, `reject_base_resume_prose_hydration`, `classify_support`
(distinguishes graph-backed / generic taxonomy / JD-only / archive-base calibration / fallback).

## C0 / proof pool / PA

Evidence module: [competency_capability_evidence.py](../../../apps_rg/runtime/sections/competency_capability_evidence.py)

- `COMPETENCY_CAPABILITY_EVIDENCE_PACK` emitted into competencies C0 with proof_authority,
  base_resume_usage=calibration_only, archive_usage=provenance_inventory_only, jd_usage=targeting_only,
  examples_usage=style_only, competency_bundle_ids, graph_skill_node_ids by category, source_fact_ids
  by category, employer/role bindings, activation status, external claim policy, and seniority/rigor
  baseline signals.
- Proof pool attach: [proof_pool_resolver.py](../../../apps_rg/runtime/proof_pool_resolver.py) →
  `attach_competency_bundles_to_proof_pool_metadata`.
- PA injection: [competencies_pa.py](../../../apps_rg/runtime/sections/competencies_pa.py) renders
  bundles as evidence data only with the organic-generation instruction.
- Runtime stamping: [competencies_lane_execution.py](../../../apps_rg/runtime/sections/competencies_lane_execution.py)
  stamps `competency_bundle_id` + `graph_skill_node_ids` onto categories by taxonomy mapping.

## X2 gates (HARD only in bundle mode)

[competencies_quality_x2.py](../../../apps_rg/runtime/validators/competencies_quality_x2.py) +
[competencies_x2.py](../../../apps_rg/runtime/validators/competencies_x2.py):

`x2_competencies_capability_bundles_in_proof_pool`, `x2_competency_bundle_id_required_per_category`,
`x2_graph_skill_node_ids_required_per_category`, `x2_source_fact_ids_or_graph_lineage_required_per_category`,
`x2_default_fid_only_support_forbidden`, `x2_generic_taxonomy_only_category_forbidden`,
`x2_jd_only_skill_forbidden`, `x2_base_archive_ngram_overlap_forbidden_or_warn`,
`x2_competency_rigor_floor_met`, `x2_technical_density_floor_met`,
`x2_required_capability_families_covered` (>=7 of 7).

Gates are only emitted when `proof_pool_metadata.competency_capability_bundle_consumption` is true,
so no existing gate is weakened.

## Config decision

[section_retrieval_profile.yaml](../../../apps_rg/config/domain_contract/section_retrieval_profile.yaml)
`competencies`: `graph_expansion_allowed: true`, `competency_bundle_consumption: required`,
`graph_expansion_mode: competency_bundle_only`. Enabled because bundle consumption is wired and
flat taxonomy/flat skill consumption is blocked.

## Tests

[test_competencies_capability_bundle_wiring.py](../../../tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py)
— 24 passed.

## Runtime proof

NOT CLAIMED. Canonical CLI runtime proof for the competencies lane is deferred to the user per scope.
