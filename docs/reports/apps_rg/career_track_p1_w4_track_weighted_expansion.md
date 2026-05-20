# P1-W4 — Track-weighted graph expansion

**Generated:** 2026-05-20T12:40:42Z  
**Plan:** graph-skills-hardening-f3a8c1  
**Role family:** REGULATED_AI_GOVERNANCE

## Track weights

- `track_actuarial_risk_derivatives`: 0.3913
- `track_data_tech_cloud_ml`: 0.3043
- `track_genai_agentic`: 0.3043

## Selected facts by track

- `track_actuarial_risk_derivatives`: 5 facts
- `track_data_tech_cloud_ml`: 6 facts
- `track_genai_agentic`: 5 facts

## Graph hop sample (first skill)

```json
[
  {
    "edge_type": "career_track_contains_pillar",
    "from": "track_actuarial_risk_derivatives",
    "to": "pillar_banking_platform_responsible_ai",
    "note": "track-weighted pillar scope"
  },
  {
    "edge_type": "skill_row_pillar_projection",
    "from": "pillar_banking_platform_responsible_ai",
    "to": "skill_sr_basel_ccar_lineage_regulatory",
    "note": "ACTIVE skill_row pillar match (not causal)"
  },
  {
    "edge_type": "skill_supported_by_fact",
    "from": "skill_sr_basel_ccar_lineage_regulatory",
    "to": "fact_governance_003",
    "note": "graph edge skill_supported_by_fact"
  }
]
```

## C0.3 binding (track-weighted)

- c03_graph_bound_status: **BOUND**
- c03_binding_surface: `apps_rg/fact_inventory/track_weighted_graph_expansion`
- c03_graph_expansion_ref: `ref:graph:track_weighted_expansion:f07c04d6399ba244`
- c03_graph_hop_paths_count: **21**
- c03_selected_tracks: ['track_actuarial_risk_derivatives', 'track_data_tech_cloud_ml', 'track_genai_agentic']
- non_graph_evidence_items_count: **0**
- graph_expansion_mode: **TRACK_WEIGHTED_MULTI_HOP**

## Authority

- broad_skills_ledger_used_as_authority: **False**
- cross_track_causal_claims: **False**
- tracks_with_facts: **['track_actuarial_risk_derivatives', 'track_data_tech_cloud_ml', 'track_genai_agentic']**

## agentic_core isolation

- isolation_verdict: **ISOLATED_PREEXISTING_CHURN**
- touched_by_this_wave: **False**
- dirty_files: `['agentic_core/L0_routing/logs/guardian_report.json', 'agentic_core/L0_routing/reasoning/execution_orchestrator.py', 'agentic_core/L0_routing/reasoning/route_gates.py', 'agentic_core/L2_execution/apps_rg_l2_binding.py', 'agentic_core/L4_state/memory/runtime_adg/_trace_index.json', 'agentic_core/runtime/contracts/tests/test_contracts_smoke.py']`
