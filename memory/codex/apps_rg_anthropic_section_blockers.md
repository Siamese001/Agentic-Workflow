# ProceduralPattern:AppsRgAnthropicSectionBlockers

```json
{
  "entities": [{
    "name": "ProceduralPattern:AppsRgAnthropicSectionBlockers",
    "entityType": "ProceduralPattern",
    "observations": [
      "Fixes apps_rg Anthropic full-section blockers where InsurTech bullets empty-select after truncated self-consistency JSON and headline passes X2 despite redundant partner/alliance/channel segments.",
      "For InsurTech/EY role-episode bullets, inspect `apps_rg/runtime/sections/role_episode_lane.py`; bullet lanes need lane-aware `max_tokens` large enough for 3 bullets plus claim-ledger JSON, while narratives may keep the smaller default.",
      "For headline X1D semantic-redundancy failures, inspect `apps_rg/runtime/validators/headline_x2.py`; repeated partner ecosystem language such as Hyperscaler Alliance Co-Sell plus Partner Channel Alliance must fail `x2_headline_segments_quality` before X1D.",
      "Keep the producer contract aligned in `apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml`; prompt hardening should teach mutual X/Y/Z capability-family distinctness rather than relaxing judge thresholds.",
      "Validate with `python -m pytest tests/unit/apps_rg/test_role_episode_x2_gates.py tests/unit/apps_rg/validators/test_headline_x2_fixed_prefix_contract.py tests/unit/apps_rg/test_headline_tailor_v15_prompt_quality.py -q` plus headline/product-shape drift guards.",
      "Guard against the next-session misread: do not treat empty bullet output as a content-quality failure when all SC paths show REAL_LLM truncated JSON; fix the producer token budget and keep parser/gates fail-closed.",
      "discovered: 2026-07-05, validated: 2026-07-05"
    ]
  }]
}
```
