# P1-W4 — Track-weighted graph expansion

**Generated:** 2026-05-19T15:54:27Z  
**Plan:** graph-skills-hardening-f3a8c1  
**Role family:** SVP_ENGINEERING_AI_PLATFORM

## Track weights

- `track_actuarial_risk_derivatives`: 0.1304
- `track_data_tech_cloud_ml`: 0.2609
- `track_genai_agentic`: 0.6087

## Selected facts by track

- `track_actuarial_risk_derivatives`: 3 facts
- `track_data_tech_cloud_ml`: 5 facts
- `track_genai_agentic`: 7 facts

## Graph hop sample (first skill)

```json
[
  {
    "edge_type": "career_track_contains_pillar",
    "from": "track_actuarial_risk_derivatives",
    "to": "pillar_actuarial_foundation",
    "note": "track-weighted pillar scope"
  },
  {
    "edge_type": "skill_row_pillar_projection",
    "from": "pillar_actuarial_foundation",
    "to": "skill_actuarial_fsa_fellowship",
    "note": "ACTIVE skill_row pillar match (not causal)"
  },
  {
    "edge_type": "skill_supported_by_fact",
    "from": "skill_actuarial_fsa_fellowship",
    "to": "fact_certs_001",
    "note": "graph edge skill_supported_by_fact"
  }
]
```

## C0.3 binding (track-weighted)

- c03_graph_bound_status: **BOUND**
- c03_binding_surface: `apps_rg/fact_inventory/track_weighted_graph_expansion`
- c03_graph_expansion_ref: `ref:graph:track_weighted_expansion:02be8ad784a61557`
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
