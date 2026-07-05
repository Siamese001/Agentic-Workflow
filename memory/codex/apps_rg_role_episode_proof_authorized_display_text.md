# ProceduralPattern:AppsRgRoleEpisodeProofAuthorizedDisplayText

```json
{
  "entities": [{
    "name": "ProceduralPattern:AppsRgRoleEpisodeProofAuthorizedDisplayText",
    "entityType": "ProceduralPattern",
    "observations": [
      "Fixes apps_rg InsurTech/EY role-episode overwrite risk where model display text can import JD/briefing/target-role wording while citing valid source_fact_ids.",
      "For `apps_rg/runtime/sections/role_episode_lane.py`, keep LLM output as allowed source_fact_id selection/order only; render visible bullets and narratives from selected proof fact `claim_text` via `display_text_authority=selected_fact_plan_claim_text`.",
      "Advertise and enforce `x2_<section>_display_text_proof_authorized` in `apps_rg/runtime/sections/section_product_shape_ssot.py`; runtime `text_claim_coverage.json` should record display_text_authority and proof_authorized_rows.",
      "Regression pattern: a model bullet like `partner-led deployments of frontier AI at scale` with a valid EY source_fact_id must be discarded before display and replaced by the selected proof fact claim_text.",
      "Validate with `python -m pytest tests/unit/apps_rg/test_role_episode_x2_gates.py tests/unit/apps_rg/test_role_episode_jd_tailoring.py tests/unit/apps_rg/section_rigor/lanes/test_role_episode_sections.py tests/unit/apps_rg/test_causal_rca_regression_fixtures.py tests/unit/apps_rg/test_insurtech_ey_base_resume_grounding.py tests/unit/apps_rg/test_insurtech_ey_role_episode_wiring.py tests/unit/apps_rg/test_insurtech_ey_role_episode_bundles.py tests/unit/apps_rg/test_role_episode_graph_no_base_bullet_artifacts.py -q`.",
      "Guard against the next-session misread: valid source_fact_ids are not enough; visible material phrases must match selected proof fact claim_text after sentence normalization, and graph-skill phrases are selection hints rather than approved display wording.",
      "discovered: 2026-07-05, validated: 2026-07-05"
    ]
  }]
}
```
