# Apps RG Contract Harness — Failure Register (W0)

**Plan:** [apps-rg-contract-harness-modernization-f4e8b2](../../.cursor/plans/apps-rg-contract-harness-modernization-f4e8b2.md)  
**Generated:** 2026-05-26T13:02:51.598768+00:00  
**Filter:** `pytest tests/_apps_contract/ -k "competencies or prompt_judge or product_shape or executive_summary_x2 or unify_bullets or ibm_bullets or unify_narrative or ibm_narrative"`  

## Summary

| Metric | Count |
|--------|------:|
| Failed | 190 |
| Errors | 4 |
| Passed | 320 |
| Skipped | 15 |
| Classified rows | 194 |
| Pytest exit | 1 |

## Bucket totals

| ID | Wave | Count | Description |
|----|------|------:|-------------|
| B1 | W1 | 31 | CLI subprocess uses removed ``--provider mock`` (product allows qwen_vllm only) |
| B2 | W2 | 6 | Legacy ``claim_evidence_source_type`` / proof_source enums omit ``augmented_skills_graph`` |
| B3 | W2 | 6 | Tests pass wrong ``proof_pool_type`` vs ``evidence_authority='augmented_skills_graph'`` |
| B4 | W3 | 4 | ``SectionFrontSpinePreconditionError`` — proof pool before front spine bridge |
| B5 | W4 | 147 | Other contract drift (competencies, product_shape, PA tiering, pipeline mocks) |

## Sub-bucket (B5 tail)

| Sub-bucket | Count |
|------------|------:|
| other | 64 |
| pa_tiering | 34 |
| competencies | 32 |
| ibm_lane | 22 |
| unify_lane | 22 |
| graph_skills_authority | 16 |
| commercial_medium | 4 |

## B1 — CLI subprocess uses removed ``--provider mock`` (product allows qwen_vllm only)

| Test module | Failures |
|-------------|----------:|
| `tests._apps_contract.test_ibm_bullets_runtime_slice` | 12 |
| `tests._apps_contract.test_apps_rg_augmented_skills_graph_all_sections_runtime_receipts` | 5 |
| `tests._apps_contract.test_apps_rg_section_input_usage_ledgers` | 5 |
| `tests._apps_contract.test_unify_narrative_section_pipeline` | 5 |
| `tests._apps_contract.test_unify_narrative_l6_shadow_learning` | 2 |
| `tests._apps_contract.test_unify_bullets_section_pipeline` | 1 |
| `tests._apps_contract.test_unify_narrative_runtime_slice` | 1 |

## B2 — Legacy ``claim_evidence_source_type`` / proof_source enums omit ``augmented_skills_graph``

| Test module | Failures |
|-------------|----------:|
| `tests._apps_contract.test_apps_rg_augmented_skills_graph_dual_source_all_sections` | 6 |

## B3 — Tests pass wrong ``proof_pool_type`` vs ``evidence_authority='augmented_skills_graph'``

| Test module | Failures |
|-------------|----------:|
| `tests._apps_contract.test_apps_rg_augmented_skills_graph_source_authority` | 5 |
| `tests._apps_contract.test_unify_bullets_section_pipeline` | 1 |

## B4 — ``SectionFrontSpinePreconditionError`` — proof pool before front spine bridge

| Test module | Failures |
|-------------|----------:|
| `tests._apps_contract.test_commercial_medium_claim_output_containment` | 4 |

## B5 — Other contract drift (competencies, product_shape, PA tiering, pipeline mocks)

| Test module | Failures |
|-------------|----------:|
| `tests._apps_contract.test_apps_rg_pa_tiered_prompt.TestCompetenciesSection` | 10 |
| `tests._apps_contract.test_apps_rg_srfs_w4_x2_slice_gates` | 10 |
| `tests._apps_contract.test_ibm_bullets_section_pipeline` | 10 |
| `tests._apps_contract.test_apps_rg_resume_exit_checks.TestCompetenciesCheck` | 9 |
| `tests._apps_contract.test_resume_section_treatment_profile.TestUnifyBulletOrdinalTiers` | 9 |
| `tests._apps_contract.test_unify_bullets_section_pipeline` | 8 |
| `tests._apps_contract.test_pa_binding_role_tiering.TestUnifyBulletTiering` | 7 |
| `tests._apps_contract.test_apps_rg_competencies_x2_source_facts` | 6 |
| `tests._apps_contract.test_apps_rg_no_inline_prompt_authority` | 6 |
| `tests._apps_contract.test_apps_rg_pa_tiered_prompt.TestVerbatimSections` | 6 |
| `tests._apps_contract.test_apps_rg_srfs_w2_canonical_threading` | 6 |
| `tests._apps_contract.test_resume_section_treatment_profile.TestIbmBulletOrdinalTiers` | 6 |
| `tests._apps_contract.test_apps_rg_srfs_w3_lane_adoption` | 5 |
| `tests._apps_contract.test_c0_evidence_room_generated_lanes_e2e` | 5 |
| `tests._apps_contract.test_pa_binding_role_tiering.TestIBMBulletTiering` | 5 |
| `tests._apps_contract.test_c0_fec_single_reality_e2e` | 4 |
| `tests._apps_contract.test_resume_section_treatment_profile.TestVerbatimNarratives` | 4 |
| `tests._apps_contract.test_resume_section_treatment_profile.TestCompetencies` | 4 |
| `tests._apps_contract.test_apps_rg_pre_dispatch_preflight` | 3 |
| `tests._apps_contract.test_apps_rg_srfs_w5_prompt_hierarchy` | 3 |
| `tests._apps_contract.test_unify_narrative_runtime_slice` | 3 |
| `tests._apps_contract.test_apps_rg_graph_story_authority_e2e` | 2 |
| `tests._apps_contract.test_apps_rg_srfs_w7_broader_fixtures` | 2 |
| `tests._apps_contract.test_pa_binding_role_tiering.TestNarrativeSectionsAreVerbatim` | 2 |
| `tests._apps_contract.test_apps_rg_manual_section_review.TestSectionCoverage` | 1 |
| … | 11 more modules |

## Remediation waves (Track B)

| Wave | Bucket | Exit criteria |
|------|--------|---------------|
| W1 | B1 | No contract test expects CLI `--provider mock` exit 0 |
| W2 | B2, B3 | Graph authority contracts assert `augmented_skills_graph` |
| W3 | B4 | Front-spine bridge before `resolve_section_proof_pool` |
| W4 | B5 | Competencies / product_shape / PA tiering green |
| W5 | all | Filtered `_apps_contract` gate 0 failed |

## Pytest tail (excerpt)

```text
bm_bullets_policy_evidence_required
FAILED tests/_apps_contract/test_resume_section_treatment_profile.py::TestCompetencies::test_competencies_treatment_is_jd_ranked
FAILED tests/_apps_contract/test_resume_section_treatment_profile.py::TestCompetencies::test_competencies_rewrite_allowed
FAILED tests/_apps_contract/test_resume_section_treatment_profile.py::TestCompetencies::test_competencies_evidence_required
FAILED tests/_apps_contract/test_resume_section_treatment_profile.py::TestCompetencies::test_competencies_phrase_word_bounds
FAILED tests/_apps_contract/test_source_resume_schema_v2.py::TestRequiredSectionsPresent::test_missing_competencies_fails_validation
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_canonical_cli_emits_required_unify_bullets_artifacts
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_unify_section_flag_alias
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_compiled_unify_prompt_contains_allowed_source_fact_ids_and_claim_text_contract
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_x2_contains_claim_text_gate_and_passes_on_mock
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_x2_text_claim_coverage_integrity_gate_present_and_passes_on_mock
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_canonical_claim_ledger_ids_use_unify_bullets_prefix_on_mock
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_text_claim_coverage_structural_schema_on_mock
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_l6_learning_shadow_written_after_x3_par_key_fields
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_compiled_unify_prompt_documents_bul_un_ify_typo_guard
FAILED tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_section_lane_main_calls_canonical_primitives
FAILED tests/_apps_contract/test_unify_narrative_l6_shadow_learning.py::test_canonical_run_emits_l6_shadow_learning_after_x3
FAILED tests/_apps_contract/test_unify_narrative_l6_shadow_learning.py::test_l6_learning_recommendations_are_future_run_only
FAILED tests/_apps_contract/test_unify_narrative_runtime_slice.py::test_mock_dispatch_runs
FAILED tests/_apps_contract/test_unify_narrative_runtime_slice.py::test_mock_one_sentence
FAILED tests/_apps_contract/test_unify_narrative_runtime_slice.py::test_x2_gate_count
FAILED tests/_apps_contract/test_unify_narrative_runtime_slice.py::test_mock_x3_review_plumbing
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_canonical_cli_emits_required_unify_narrative_artifacts
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_unify_narrative_section_flag_alias
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_compiled_unify_narrative_prompt_contains_allowed_source_fact_ids_and_claim_text_contract
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_x2_contains_claim_text_gate_and_passes_on_mock
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_x2_claim_text_gate_fails_empty_ledger
FAILED tests/_apps_contract/test_unify_narrative_section_pipeline.py::test_cli_stdout_mentions_unify_narrative_lane
ERROR tests/_apps_contract/test_commercial_medium_claim_output_containment.py::test_section_proof_pool_fixture_output[unify_bullets]
ERROR tests/_apps_contract/test_commercial_medium_claim_output_containment.py::test_section_proof_pool_fixture_output[unify_narrative]
ERROR tests/_apps_contract/test_commercial_medium_claim_output_containment.py::test_section_proof_pool_fixture_output[ibm_bullets]
ERROR tests/_apps_contract/test_commercial_medium_claim_output_containment.py::test_section_proof_pool_fixture_output[ibm_narrative]
190 failed, 320 passed, 15 skipped, 7188 deselected, 26 warnings, 4 errors in 368.26s (0:06:08)
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute
```

