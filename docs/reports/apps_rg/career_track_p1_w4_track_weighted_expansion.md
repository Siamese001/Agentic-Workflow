# P1-W4 — Track-weighted graph expansion

**Generated:** 2026-06-17T23:04:01Z  
**Plan:** graph-skills-hardening-f3a8c1  
**Role family:** SVP_ENGINEERING_AI_PLATFORM

## Track weights

- `track_actuarial_risk_derivatives`: 0.1304
- `track_data_tech_cloud_ml`: 0.2609
- `track_genai_agentic`: 0.6087

## Selected facts by track

- `track_actuarial_risk_derivatives`: 4 facts
- `track_data_tech_cloud_ml`: 3 facts
- `track_genai_agentic`: 6 facts

## Graph hop sample (first skill)

```json
[
  {
    "edge_type": "career_track_contains_pillar",
    "from": "track_actuarial_risk_derivatives",
    "to": "pillar_regulatory_governance",
    "note": "track-weighted pillar scope"
  },
  {
    "edge_type": "skill_row_pillar_projection",
    "from": "pillar_regulatory_governance",
    "to": "skill_finra_sec_regulatory_compliance",
    "note": "ACTIVE skill_row pillar match (not causal)"
  },
  {
    "edge_type": "skill_row_fact_id_links",
    "from": "skill_finra_sec_regulatory_compliance",
    "to": "fact_consulting_001",
    "note": "fact_id_links on skill_row (no separate fact node)"
  }
]
```

## C0.3 binding (track-weighted)

- c03_graph_bound_status: **BOUND**
- c03_binding_surface: `apps_rg/fact_inventory/track_weighted_graph_expansion`
- c03_graph_expansion_ref: `ref:graph:track_weighted_expansion:71434de8331de06e`
- c03_graph_hop_paths_count: **22**
- c03_selected_tracks: ['track_actuarial_risk_derivatives', 'track_data_tech_cloud_ml', 'track_genai_agentic']
- non_graph_evidence_items_count: **0**
- graph_expansion_mode: **TRACK_WEIGHTED_MULTI_HOP**

## Authority

- broad_skills_ledger_used_as_authority: **False**
- cross_track_causal_claims: **False**
- tracks_with_facts: **['track_actuarial_risk_derivatives', 'track_data_tech_cloud_ml', 'track_genai_agentic']**

## agentic_core isolation

- isolation_verdict: **CLEAN**
- touched_by_this_wave: **False**
- dirty_files: `[]`
