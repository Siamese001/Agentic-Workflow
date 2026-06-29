# Generate Full ADG Gate Rationalization

```json
{
  "entities": [{
    "name": "ProceduralPattern:GenerateFullAdgGateRationalizationInvariant",
    "entityType": "ProceduralPattern",
    "observations": [
      "INVARIANT: Keep generate_full_adg gates decision-linked; do not report work that is not expected to be burned down or that would force core-to-app imports.",
      "scope: tools/reports/adg_bcg_executive_synthesis.py, ops_scripts/ci/check_graph_reach.py, ops_scripts/ci/baselines/wiring_graph_reach_ratchet.json, agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py",
      "enforcement: G_REACH_l0_reachability is core-layer L0 reachability only; L_APP is excluded and app reachability belongs to app-specific gates/tests.",
      "violation_examples: mixing stale gate_results from another snapshot into adg_bcg_executive_summary_latest; importing apps_* from agentic_core to satisfy G_REACH; restoring agentic_core/L5_safety/reasoning/hierarchy_healer.py.",
      "canonical_pattern: report consistency first via artifact snapshot/certification checks, route hierarchy root-file scans through StructureEnforcerAgent, and treat hierarchy_healer.py as deleted legacy artifact.",
      "doctrine_ref: AGENTS.md Core vs apps summary; memory/MEMORY.md Architectural invariants; tests/unit/ops_scripts/ci/test_check_graph_reach.py"
    ]
  }]
}
```
