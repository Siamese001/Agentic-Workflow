# apps_rg Graph Skills SQLite Runtime Invariant

Entity shape:

```json
{
  "entities": [
    {
      "name": "ProceduralPattern:AppsRgGraphSkillsSqliteRuntimeInvariant",
      "entityType": "ProceduralPattern",
      "observations": [
        "INVARIANT: Keep apps_rg/fact_inventory/master_skills_arsenal_ledger.json as the canonical graph source; use the generated SQLite file only as the C0.3 graph-skills runtime query projection.",
        "scope: apps_rg/fact_inventory/augmented_skills_graph_sqlite.py; apps_rg/runtime/c03_graph_sqlite_context.py; apps_rg/runtime/c0/c03_graph_expansion.py; apps_rg/runtime/c0/c03_sqlite_graph_selection.py; artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite.",
        "enforcement: apps_rg/fact_inventory/validate_c03_graph_hardening.py plus focused pytest selectors in plans/graph-skills-sqlite-runtime-redesign-a4c9e2.md.",
        "violation_examples: treating the generated .sqlite binary as canonical; hand-editing SQLite to change skills; appending duplicate C0.3 graph concepts instead of consuming JSON ledger rows; using graph rows as claim proof.",
        "canonical_pattern: materialize deterministic c03_skill_selection_features from JSON; verify ledger_hash freshness through ensure_c03_graph_sqlite; rank and receipt C0.3 selected/rejected siblings through select_c03_sqlite_graph_candidates.",
        "doctrine_ref: plans/graph-skills-sqlite-runtime-redesign-a4c9e2.md; docs/reports/apps_rg/graph_skills_sqlite_runtime_redesign_a4c9e2_receipt.json."
      ]
    }
  ]
}
```

