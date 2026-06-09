# apps_lic Prompt Slot and X1-X3 W0 Inventory

Generated UTC: 2026-06-09T14:57:51+00:00
Apps LIC root: `C:\Git\Agentic-Workflow-apps_lic`
Plan: `plans/apps-lic-prompt-slot-x1x3-ssot-drift-4a9f2c.md`

## Method

- Read-only filesystem inventory of prompt, template, schema, recipient policy, runtime PA, and Exit policy sources.
- SHA-256 hashes are computed from current file bytes.
- YAML/JSON files are parsed for declared slots, templates, contracts, and Exit dispositions when available.
- ADG status: adg_sqlite.adg_health attempted on 2026-06-09; unavailable in Codex session with Transport closed; filesystem hash inventory used as W0 fallback.

## Classification Counts

| Classification | Files |
|---|---:|
| core_reference | 3 |
| exit_or_validation_contract | 8 |
| legacy_fence_candidate | 2 |
| output_contract | 4 |
| profile_or_rubric | 14 |
| recipient_or_message_policy | 7 |
| registry_or_bom | 2 |
| renderable_prompt_template | 8 |
| runtime_prompt_assembly | 2 |
| supporting_contract | 16 |

## Drift Observations

- Active template files missing from prompt_registry.yaml: compact_recruiter_arc, exec_positioning, outreach_draft_v2
- Template slot terms not declared in prompt_bom.yaml: A0, H0, L0, M0, N0
- X1/X2/X3 terms are present in Exit/runtime files and must remain non-prompt glossary terms: X1, X2, X3
- Legacy prompt sources requiring fence decision: apps_lic/config/prompts.json, apps_lic/types/PromptTemplate.py

## Inventory

| Classification | Path | Slots / Exit Terms | SHA-256 |
|---|---|---|---|
| core_reference | `agentic_core/L2_execution/reasoning/authority_validator.py` | C0, D0, E0, H0, I0, M0, S0, U0 | `f52aaaddcabad2acda9ba3c01dafa22fc5650fd356b606c4535ec823b694c963` |
| core_reference | `agentic_core/L2_execution/reasoning/compiled_artifact.py` | C0, D0, E0, H0, I0, L0, M0, R0, S0, U0, Y0 | `d42e9597ef71a769a2555daa1db9db42f4d3b5445159591e24cc5e970ad5fbd1` |
| core_reference | `agentic_core/L2_execution/reasoning/prompt_messages.py` | C0, D0, E0, H0, I0, M0, S0, U0 | `d394799caff8a85497ce19b8d77a1171c2582f185b8cf69137519999efc429fa` |
| recipient_or_message_policy | `apps_lic/config/archetype_tone_policy.yaml` | - | `6e4b3170a46f4bc1c4706606c722e3d956ca1c35f147d9bd3de420da566de735` |
| recipient_or_message_policy | `apps_lic/config/archetype_tone_table.yaml` | - | `1f73c0e81d9e4d877cf2690894ec9010b6a8c62383e396a367476461ec0c8199` |
| supporting_contract | `apps_lic/config/domain_contract/app_domain_manifest.yaml` | - | `919b43efb09d5673e52d53a5cf55cbfa4162adb1ed4621df450747063f7d2e5e` |
| supporting_contract | `apps_lic/config/domain_contract/apps_lic_redesign_w0_contracts.yaml` | C0, L0, SC, X2 | `2868c8ddb9b785d6ac9e036f90e0a9bcab6e5d216e51f65245b50dc01ce03fcc` |
| profile_or_rubric | `apps_lic/config/domain_contract/cache_profiles.yaml` | C0 | `55021c24c9d4550c1a033e15c13d0580414ef6ee3c8e80c7ba7a6c049e44ee87` |
| profile_or_rubric | `apps_lic/config/domain_contract/capability_profiles.yaml` | - | `d751d864bdd5573444d550c22673271bb4d6272b9f0cd80c14fc22cf3891ef41` |
| profile_or_rubric | `apps_lic/config/domain_contract/delegation_profile.yaml` | - | `c742dd0cc73069d8b117e51238306e72dde3d6b1e7b94a6217ee4b21d839a228` |
| profile_or_rubric | `apps_lic/config/domain_contract/eval_rubrics.yaml` | - | `8a0609a5195b3f287a63cff26839de2e5eeff8decb114555e523da17d110c642` |
| exit_or_validation_contract | `apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json` | G21, G22, G23, G24, G25, G26, G27, G28 | `f9369a1714ad63ec838523810b3aef222beec05c287b10bd44d907cc8d7dcf40` |
| supporting_contract | `apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json` | - | `1ed3148c78c15ba3e46ad324226a2956f128a20bf7896c31e5857ddbd31abc82` |
| supporting_contract | `apps_lic/config/domain_contract/fixtures.yaml` | - | `d60816af230d3efdbfa5b3e21c8fc628e5503b2778edfce996690e20317d3bc2` |
| supporting_contract | `apps_lic/config/domain_contract/grader_roster.yaml` | - | `50c5f19dd4b3affb5fe613803121285fcb90ad85744290c0b75236cc19cced74` |
| supporting_contract | `apps_lic/config/domain_contract/input_contract.yaml` | - | `678e57327b17ba8754a9fdb3853133e21a31cc719544976ef03dfc5e73da83ea` |
| profile_or_rubric | `apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json` | C0, L0, U0 | `e55c8ece5d56b9b5cada55ad7582b7a6bc5136fc3dbbc2fe0eb8e03812e39390` |
| profile_or_rubric | `apps_lic/config/domain_contract/learning_profiles.yaml` | - | `e46279a95428ca85465e2ff9a01746f36b39e0e14ca768abf7afd791fd14df0b` |
| recipient_or_message_policy | `apps_lic/config/domain_contract/message_type_requirements.v1.yaml` | C0, SC, U0 | `bfa2dfc628cea5bce2a40a9926dc69097602cfd616b07482870c70ec7d212b26` |
| profile_or_rubric | `apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json` | - | `0044e320f77d99e608187be097055ea4ef6e63918160ab977b65061670d3230e` |
| supporting_contract | `apps_lic/config/domain_contract/negative_controls.yaml` | X3 | `20806554ba800f947565455f05658c95fc3d0546a48eef6ca7eaa2439517bc16` |
| supporting_contract | `apps_lic/config/domain_contract/opportunity_ingestion.v1.yaml` | - | `949fbec7696455281bedd8f531ca0503dc1d7b169a1d3932122c360e73ecff8f` |
| profile_or_rubric | `apps_lic/config/domain_contract/orchestration_profiles.yaml` | - | `f52402ece4cb79c0286ad18c28de9b8bde6b7700d55b6a1b25feba37a13b283b` |
| output_contract | `apps_lic/config/domain_contract/output_schema.yaml` | - | `5e737bf6c803d96f047110ef04674252110b0a546c9963c3a9829887c1262da8` |
| profile_or_rubric | `apps_lic/config/domain_contract/prompt_profiles.yaml` | - | `2996829c472aa7f64d4be1013de25cc8b0b843587297f70eb3b599ee0acd3d26` |
| recipient_or_message_policy | `apps_lic/config/domain_contract/recipient_classification.v1.yaml` | C0, U0 | `a9a3aeeeaabd4572b1bec7031ddd9d7e7389b2f0ef85b9b25bea4d0afacc848e` |
| profile_or_rubric | `apps_lic/config/domain_contract/repair_profiles.yaml` | - | `d761aba9faa81831d2f129fcf4a100437e609c681f96ecef79b109d1b70e6a7e` |
| profile_or_rubric | `apps_lic/config/domain_contract/research_delegation_profile.yaml` | U0 | `1c971dc98960d9ade119ac9c950d6f39c6adfd23c6f540f9105671eb3291b5d3` |
| profile_or_rubric | `apps_lic/config/domain_contract/retrieval_profiles.yaml` | - | `4bc3ce10e3bda7ffa0bdd538803d2c0bf447003449b9b1ff94936e68226476db` |
| profile_or_rubric | `apps_lic/config/domain_contract/route_profiles.yaml` | C0 | `25b7737a94509f9a22243cddefc75274d68642f6342b1edc4bd1d96cb1ec8cfa` |
| output_contract | `apps_lic/config/domain_contract/rubric_output_map.yaml` | - | `027d00aa2d99cb5004e4d167a8ac1e3fa5bba8b8876d376c54a0bad1036fda67` |
| supporting_contract | `apps_lic/config/domain_contract/runtime_customization_package.outreach_message.v1.json` | L0 | `d9db445084fd59d286a5d369d2fa6278b1ce0b68016580a691111b7adb20f11b` |
| exit_or_validation_contract | `apps_lic/config/domain_contract/runtime_gate_profile.outreach_message.v1.json` | - | `a010d52f69b1b8b667ab8b94aaeb36c7419da27a4e22f6f84c52545cbc329b53` |
| supporting_contract | `apps_lic/config/domain_contract/sender_proof_graph.v1.yaml` | C0, X2 | `21a9d309e95e83fea2b3e2912148851116c7dc3f3c8cd629489deee84fc181a5` |
| supporting_contract | `apps_lic/config/domain_contract/standing_sender_knowledge.v1.yaml` | - | `43f278243c612d3783e1957392af2ac5d203858e6bdc6de3d74a1acc7edee7a2` |
| supporting_contract | `apps_lic/config/domain_contract/task_classes.yaml` | - | `b29c04915ea621e7c59cc278e1935785a9d3f6acbeb0903f502c7f5ea742614d` |
| profile_or_rubric | `apps_lic/config/domain_contract/threshold_profiles.yaml` | - | `f8086124e6834004be2fed688db00a3f8de5cc47909635d3e8f5fc133be3c4e7` |
| exit_or_validation_contract | `apps_lic/config/domain_contract/validation_exit.v1.yaml` | C0, SC, X1, X2 | `3cb0923cb5b7cbd7223dc64c3d534ce76e7993e4721203a7ac1eb520e21d43ec` |
| exit_or_validation_contract | `apps_lic/config/domain_contract/validation_profiles.v1.json` | - | `380cf2ed0503b5e4fafbc38dbf6d2c943258462767ec0931c007bc1db8ae2f3e` |
| output_contract | `apps_lic/config/domain_contract/whole_message_generation.v1.yaml` | C0, SC | `b4a36110179292a330ef49d40287f5261a19d0b95c506ee5c953ae66c90fe39a` |
| exit_or_validation_contract | `apps_lic/config/exit_rubric.yaml` | L0, U0, X3 | `1d49b87363e1cf53624ce681d6f4c668bd743c0ceef741d6f3dbc1d031c138f9` |
| output_contract | `apps_lic/config/outreach_schema.json` | U0 | `7769d49ee42c180df0972091beaec3b9f184cf1f42e9ed9a88f43bcf44d10934` |
| registry_or_bom | `apps_lic/config/prompt_registry.yaml` | C0, D0, E0, I0, R0, S0, U0, Y0 | `27d29e8be33687ed74b2f5fad3b4b05c1c078f274d3d6b1d343df077ef7fa03a` |
| legacy_fence_candidate | `apps_lic/config/prompts.json` | - | `2c5466a83184f41ae7806110c9bd9237cedaf836af866e0841d706889744e205` |
| supporting_contract | `apps_lic/engines/generation_engine.py` | C0, SC, X1 | `2d831f339c02257a505df85c438c7213ef28d86d543baaf2effece9665c804b0` |
| supporting_contract | `apps_lic/engines/generation_subject_policy.py` | - | `d27b35a0669f61a1b76bde1e27ee09e1483f46f5ab53173e6a1c3933e0e8f54c` |
| exit_or_validation_contract | `apps_lic/engines/validation_exit.py` | X1, X2 | `f498e0bf8a3566feb34230407f72ef9a0c70a197c549dce0710758af41460c34` |
| supporting_contract | `apps_lic/engines/x1d_judge_feedback_regeneration.py` | X1 | `72bacbf5cbc90129eda0bbe30cf8e54b3a03dd00cd23c446eb1e4429c2f5ef5c` |
| supporting_contract | `apps_lic/engines/x1d_judge_policy.py` | X1 | `73e723fb6363aee3dcf18b02ad53a5e35494f12fc897e957dd8024a879dffbc3` |
| runtime_prompt_assembly | `apps_lic/prompt_assembly/lic_pa_compiler.py` | - | `0db8727b38f6ce592da0d27ae1b96b1be5fc03b9877c48cbd48f86c3e73f71e1` |
| registry_or_bom | `apps_lic/prompt_assembly/prompt_bom.yaml` | C0, D0, E0, I0, R0, S0, U0, Y0 | `adefaa001b394458aa8a42865f02db39b0b63044c1920bb6d3054bf6cb68392c` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/briefing_to_manifest_v1.yaml` | C0, D0, R0, S0 | `4f39d58ba359208271b2e627c12deb1f163f3b51dd7b2e01d4d4d71b8cfdb7ba` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/channel_length_repair_v1.yaml` | C0, D0, I0, R0, S0, Y0 | `a1f7ac57edd5320a31b39e67e12a73b205112e19cfed5893291549e2bd34f850` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/compact_recruiter_arc.yaml` | A0, C0, D0, E0, H0, I0, L0, M0, N0, R0, S0, U0 | `cf3c558a8bca109201b796dc16dce6c989e6749db0ce32598f7ac46eeb856811` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/exec_positioning.yaml` | A0, C0, D0, E0, I0, L0, N0, R0, S0, U0, Y0 | `c420c516cbebbf0280e90062768713e8c0dbfaf72cb48a7f4f9ea3ce3380c73d` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml` | A0, C0, D0, E0, I0, L0, N0, R0, S0, U0, Y0 | `eae754865332ca90fa0749027e12023c26a1a5c6c71d8d60bca2800946624248` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/outreach_draft_v2.yaml` | A0, C0, D0, E0, I0, L0, N0, R0, S0, U0, Y0 | `e34df2bd4fcc569470c686dcf065f4dfb325975d568169e0219bfee73ae9ed08` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/repair_antipattern_v1.yaml` | C0, D0, I0, R0, S0, Y0 | `6cbcf2e515361a8ae0f2615df8c416b376b89a0b427fb18bab8aa613aeb73fd8` |
| renderable_prompt_template | `apps_lic/prompt_assembly/templates/unsupported_claim_omission_v1.yaml` | C0, D0, I0, R0, S0 | `3224189892bb28999fa8af7de3e5e0da7aca736e8d8bd974f66f5c5c3234668f` |
| exit_or_validation_contract | `apps_lic/runtime/bindings/exit_binding.py` | G27, X1, X2, X3 | `e6fe886ff0e0da296827aec69e8d8494279e7f83cbd40ef2f3cc05079ba55a3d` |
| runtime_prompt_assembly | `apps_lic/runtime/bindings/pa_binding.py` | A0, C0, C03, D0, E0, H0, I0, L0, M0, R0, RI, S0, SC, U0 | `29a6f75914d27a7c97d3436eebcf73f64ddfd8d7de4a5b9768420438e18321f7` |
| exit_or_validation_contract | `apps_lic/runtime/bindings/w5_validation_exit_binding.py` | X1, X2 | `0256b5117ef3934af12c22edf66c95147d2ae73222e206cfd385ac7a946882a7` |
| legacy_fence_candidate | `apps_lic/types/PromptTemplate.py` | C0, D0, E0, H0, I0, M0, R0, S0, U0, Y0 | `aef54ac12391d6f516f17c200c61b6ee50b7e2102d96ef8abd281e02e3ede6c6` |
| recipient_or_message_policy | `apps_lic/types/recipient_archetype_mapping.py` | C0 | `ffcb46a51317b58e677ff3c67b26233beebda3119fd7f10a82e2a4ea7adcea22` |
| recipient_or_message_policy | `apps_lic/types/recipient_archetype_types.py` | - | `c86f662e18e78c144e753bbab6f0ed965b1f37b4de668200ea617c45140e694f` |
| recipient_or_message_policy | `apps_lic/types/recipient_policy_profile.py` | - | `65239ae70b78a19bb58a66452114d0c54fc61fa0d5c655af73c38834a5778aef` |

## Structured Details

### apps_lic/config/archetype_tone_policy.yaml

```json
{
  "top_keys": [
    "schema_version",
    "tone_matrix",
    "valid_archetypes"
  ]
}
```

### apps_lic/config/archetype_tone_table.yaml

```json
{
  "top_keys": [
    "archetypes",
    "recipient_class_fallback",
    "tone_violation_thresholds"
  ]
}
```

### apps_lic/config/domain_contract/app_domain_manifest.yaml

```json
{
  "top_keys": [
    "app_domain_contract_id",
    "app_id",
    "app_version",
    "blueprint_hash",
    "capability_profile_refs",
    "created_at",
    "domain",
    "eval_rubric_refs",
    "fixture_refs",
    "grader_roster_refs",
    "input_contract_ref",
    "negative_control_refs",
    "orchestration_profile_refs",
    "output_schema_ref",
    "owner_surface",
    "policy_hash",
    "prompt_profile_refs",
    "retrieval_profile_refs",
    "route_profile_refs",
    "source_app_config_ref",
    "status",
    "threshold_profile_refs"
  ]
}
```

### apps_lic/config/domain_contract/apps_lic_redesign_w0_contracts.yaml

```json
{
  "top_keys": [
    "c03_sender_proof_packet_contract",
    "c0_evidence_packet_contract",
    "canonical_message_types",
    "current_gap_map",
    "e2e_acceptance_modes",
    "exit_contract",
    "fail_closed_matrix",
    "jd_facts_contract",
    "length_budgets",
    "message_type_requirement_matrix",
    "negative_fixture_manifest",
    "no_weakening_invariants",
    "outreach_modes",
    "proof_bundle_contract",
    "reasoning_policy",
    "recipient_class_derivation",
    "recipient_classes",
    "rollout_switches",
    "runtime_boundary",
    "schema_version",
    "send_modes",
    "source_plan",
    "u0_seed_contract",
    "w0_status",
    "x1d_judge_contract",
    "x2_gate_contract"
  ]
}
```

### apps_lic/config/domain_contract/cache_profiles.yaml

```json
{
  "top_keys": [
    "app_id",
    "cache_profile_id",
    "cache_scope",
    "created_at",
    "grounded_only",
    "invalidation_triggers",
    "semantic_cache",
    "source_app_config_ref",
    "status",
    "ttl_seconds",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/delegation_profile.yaml

```json
{
  "top_keys": [
    "app_id",
    "delegation_routing",
    "metadata",
    "payload_validation",
    "profile_version",
    "reuse_validation",
    "terminal_cache"
  ]
}
```

### apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json

```json
{
  "allowed_exit_dispositions": [
    "APPROVED",
    "APPROVED_WITH_NOTES",
    "REJECTED",
    "HITL_REQUIRED",
    "ABSTAIN"
  ],
  "top_keys": [
    "allowed_exit_dispositions",
    "app_id",
    "conditional_exit_gates",
    "default_disposition",
    "fail_closed_on_exit_failure",
    "metadata",
    "profile_id",
    "required_exit_gates",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json

```json
{
  "top_keys": [
    "app_id",
    "cache_categories",
    "cache_invalidation_triggers",
    "cache_policy",
    "enforcement",
    "metadata",
    "profile_id",
    "r1a_exact_cache",
    "r1b_semantic_cache",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/input_contract.yaml

```json
{
  "top_keys": [
    "ambiguity_behavior",
    "app_id",
    "created_at",
    "data_boundary_rules",
    "forbidden_inputs",
    "input_contract_id",
    "input_normalization_rules",
    "missing_input_behavior",
    "optional_inputs",
    "origin_trust_requirements",
    "required_inputs",
    "source_app_config_ref",
    "status",
    "task_class",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json

```json
{
  "top_keys": [
    "allowed_route_families",
    "app_id",
    "briefing_only_policy",
    "cache_bypass_policy_ref",
    "default_route_family",
    "deprecated_route_families",
    "execution_form_mapping",
    "forbidden_route_families",
    "l3_required_for_families",
    "metadata",
    "profile_id",
    "route_selection_conditions",
    "route_selection_rules",
    "routing_model",
    "task_class",
    "terminal_execution_families",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/learning_profiles.yaml

```json
{
  "top_keys": [
    "app_id",
    "created_at",
    "holdout_required",
    "judge_calibration_cadence_days",
    "learning_profile_id",
    "min_n_each_arm",
    "notes",
    "promotion_threshold",
    "regret_budget",
    "source_app_config_ref",
    "status",
    "uplift_required",
    "version",
    "z_score"
  ]
}
```

### apps_lic/config/domain_contract/message_type_requirements.v1.yaml

```json
{
  "top_keys": [
    "authority",
    "canonical_message_types",
    "class_specific_requirements",
    "decision_rules",
    "gate_statuses",
    "message_type_policy",
    "missing_field_statuses",
    "modifiers",
    "purpose",
    "schema_version",
    "wave"
  ]
}
```

### apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json

```json
{
  "top_keys": [
    "app_id",
    "feedback_collection_points",
    "learning_policy",
    "learning_target",
    "meta_feedback_dimensions",
    "metadata",
    "profile_id",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/opportunity_ingestion.v1.yaml

```json
{
  "top_keys": [
    "baseline_vector_collections",
    "governance",
    "jd_normalization",
    "namespaces",
    "profile_evidence_input",
    "profile_readiness_receipt",
    "purpose",
    "readiness_statuses",
    "schema_version",
    "wave",
    "write_receipt"
  ]
}
```

### apps_lic/config/domain_contract/output_schema.yaml

```json
{
  "top_keys": [
    "app_id",
    "created_at",
    "field_constraints",
    "formatting_constraints",
    "optional_sections",
    "output_schema_id",
    "output_type",
    "prohibited_outputs",
    "required_sections",
    "schema_validation_rules",
    "source_app_config_ref",
    "status",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/recipient_classification.v1.yaml

```json
{
  "output_contract": {
    "required_fields": [
      "derived_recipient_class",
      "recipient_class_confidence",
      "class_reason_codes",
      "source_snapshot_ids",
      "supporting_facts",
      "contradicted_facts",
      "contradiction_status",
      "hitl_required",
      "u0_hint_used_as_authority"
    ]
  },
  "top_keys": [
    "authority",
    "canonical_classes",
    "confidence_thresholds",
    "evidence_sources",
    "fail_closed",
    "output_contract",
    "purpose",
    "schema_version",
    "signal_examples",
    "target_eligibility",
    "u0_policy",
    "wave"
  ]
}
```

### apps_lic/config/domain_contract/repair_profiles.yaml

```json
{
  "top_keys": [
    "app_id",
    "created_at",
    "repair_profile_id",
    "repair_scenarios",
    "source_app_config_ref",
    "status",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/research_delegation_profile.yaml

```json
{
  "top_keys": [
    "caller_app_id",
    "description",
    "expected_return",
    "policy_refs",
    "profile_id",
    "substrate_consumption",
    "target_app_id",
    "task_classes",
    "u0_package_requirements",
    "uploaded_briefings",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/rubric_output_map.yaml

```json
{
  "top_keys": [
    "app_id",
    "dimensions",
    "mapper_id",
    "rubric_id",
    "status",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/runtime_customization_package.outreach_message.v1.json

```json
{
  "top_keys": [
    "app_id",
    "metadata",
    "package_digest_required",
    "policies",
    "profile_id",
    "profile_refs",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/runtime_gate_profile.outreach_message.v1.json

```json
{
  "top_keys": [
    "app_id",
    "conditional_runtime_gates",
    "gate_execution_order",
    "halt_on_gate_failure",
    "max_parallel_gates",
    "metadata",
    "profile_id",
    "required_runtime_gates",
    "task_class",
    "version"
  ]
}
```

### apps_lic/config/domain_contract/sender_proof_graph.v1.yaml

```json
{
  "top_keys": [
    "acceptance",
    "authority",
    "inputs",
    "pa_envelope",
    "permission_decisions",
    "purpose",
    "relevance_scoring",
    "schema_version",
    "standing_corpus",
    "wave"
  ]
}
```

### apps_lic/config/domain_contract/standing_sender_knowledge.v1.yaml

```json
{
  "top_keys": [
    "approved_sender_proof_points",
    "claim_permission_map",
    "collection",
    "graph_skill_links",
    "namespace",
    "no_send_policy",
    "resume_project_facts",
    "schema_version",
    "sender_profile",
    "writing_preferences"
  ]
}
```

### apps_lic/config/domain_contract/validation_exit.v1.yaml

```json
{
  "allowed_exit_dispositions": [
    "clear_draft",
    "review_required",
    "blocked",
    "abstain"
  ],
  "top_keys": [
    "acceptance",
    "authority",
    "exit",
    "governance",
    "purpose",
    "risk_matrix",
    "schema_version",
    "wave",
    "x1d",
    "x2_gates"
  ]
}
```

### apps_lic/config/domain_contract/validation_profiles.v1.json

```json
{
  "top_keys": [
    "default_profile_id",
    "profiles",
    "schema_version"
  ]
}
```

### apps_lic/config/domain_contract/whole_message_generation.v1.yaml

```json
{
  "top_keys": [
    "acceptance",
    "authority",
    "candidate_contract",
    "governance",
    "length_budgets",
    "length_control_policy",
    "provider_backed_generation",
    "purpose",
    "reasoning_policy",
    "recipient_archetype_policy",
    "request_contract",
    "required_inputs",
    "schema_version",
    "wave"
  ]
}
```

### apps_lic/config/exit_rubric.yaml

```json
{
  "top_keys": [
    "antipattern_extension_patterns",
    "app",
    "dimensions",
    "hitl_policy",
    "schema_version",
    "x3_dispositions"
  ]
}
```

### apps_lic/config/outreach_schema.json

```json
{
  "top_keys": [
    "$schema",
    "additionalProperties",
    "description",
    "not",
    "properties",
    "required",
    "title",
    "type"
  ]
}
```

### apps_lic/config/prompt_registry.yaml

```json
{
  "declared_templates": [
    "briefing_to_manifest_v1",
    "channel_length_repair_v1",
    "outreach_draft_v1",
    "repair_antipattern_v1",
    "unsupported_claim_omission_v1"
  ],
  "top_keys": [
    "app",
    "hash_fields",
    "owner",
    "registry_id",
    "schema_version",
    "templates"
  ]
}
```

### apps_lic/config/prompts.json

```json
{
  "top_keys": [
    "judge_narrative_coherence",
    "judge_tone_register_fit",
    "profile_analysis_reasoning"
  ]
}
```

### apps_lic/prompt_assembly/prompt_bom.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "U0",
    "D0",
    "E0",
    "Y0",
    "R0"
  ],
  "top_keys": [
    "app",
    "bom_id",
    "hash_fields",
    "owner",
    "purpose",
    "required_slots",
    "schema_version",
    "slot_definitions",
    "template_registry_refs"
  ]
}
```

### apps_lic/prompt_assembly/templates/briefing_to_manifest_v1.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "C0",
    "D0",
    "R0"
  ],
  "output_contract": {
    "format": "json",
    "type": "PreloadedOutreachContextManifestContext"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/channel_length_repair_v1.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "D0",
    "Y0",
    "R0"
  ],
  "output_contract": {
    "format": "json",
    "type": "ChannelLengthRepair"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/compact_recruiter_arc.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "D0",
    "I0",
    "E0",
    "C0",
    "M0",
    "U0",
    "H0",
    "R0"
  ],
  "output_contract": {
    "format": "json",
    "type": "LinkedInRecruiterOutreachDraft"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/exec_positioning.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "U0",
    "D0",
    "E0",
    "Y0",
    "R0",
    "N0",
    "A0",
    "L0"
  ],
  "output_contract": {
    "format": "json",
    "type": "OutreachDraft"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "U0",
    "D0",
    "E0",
    "Y0",
    "R0",
    "N0",
    "A0",
    "L0"
  ],
  "output_contract": {
    "format": "json",
    "type": "OutreachDraft"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/outreach_draft_v2.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "U0",
    "D0",
    "E0",
    "Y0",
    "R0",
    "N0",
    "A0",
    "L0"
  ],
  "output_contract": {
    "format": "json",
    "type": "OutreachDraft"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/repair_antipattern_v1.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "D0",
    "Y0",
    "R0"
  ],
  "output_contract": {
    "format": "json",
    "type": "AntiPatternRepair"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```

### apps_lic/prompt_assembly/templates/unsupported_claim_omission_v1.yaml

```json
{
  "declared_required_slots": [
    "S0",
    "I0",
    "C0",
    "D0",
    "R0"
  ],
  "output_contract": {
    "format": "json",
    "type": "ClaimOmissionRepair"
  },
  "top_keys": [
    "allowed_stage",
    "forbidden_behaviors",
    "hash_fields",
    "input_contract",
    "output_contract",
    "owner",
    "purpose",
    "required_slots",
    "slot_bodies",
    "template_id",
    "validation_rules",
    "version"
  ]
}
```
