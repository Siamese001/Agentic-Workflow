# IBM Role Episode Consumption Wiring

**Generated:** 2026-05-28T14:00:00Z

## Config Decision

- **Status:** `ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS`
- `ibm_bullets.graph_expansion_allowed` = `True`
- `ibm_narrative.graph_expansion_allowed` = `True`
- `role_episode_bundle_consumption` = `required`

## Role Episode Consumption

| Field | Value |
|-------|-------|
| c0_marker | IBM_ROLE_EPISODE_EVIDENCE_PACK |
| proof_authority | graph_role_episode_bundles_plus_linked_source_facts |
| base_resume_usage | calibration_only |
| jd_usage | targeting_only |
| archive_usage | provenance_only |
| examples_usage | style_only |
| promotable_metric_outcome_ids | ['metric_ibm_20pct_joint_revenue_growth', 'metric_ibm_10m_arr', 'metric_ibm_10pct_finops_savings_gated'] |

## X2 Gates Added

- `x2_ibm_role_episode_bundles_in_proof_pool`
- `x2_ibm_bullet_role_episode_bundle_id_required`
- `x2_ibm_metric_outcome_id_required_when_has_metric`
- `x2_ibm_hold_metric_forbidden_in_output`
- `x2_ibm_watson_studio_no_metric_bearing_claim`
- `x2_ibm_narrative_role_episode_bundles_in_proof_pool`
- `x2_ibm_narrative_role_episode_bundle_id_required`
- `x2_ibm_narrative_hold_metric_forbidden`

## Acceptance

| Gate | Result |
|------|--------|
| compileall apps_rg | run in closeout |
| test_ibm_role_episode_consumption_wiring | run in closeout |
| agentic_core diff | empty |