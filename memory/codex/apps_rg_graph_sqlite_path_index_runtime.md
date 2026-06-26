# apps_rg Graph SQLite Path Index Runtime

Entity shape:

```json
{
  "entities": [
    {
      "name": "ProceduralPattern:AppsRgGraphSqlitePathIndexRuntimeInvariant",
      "entityType": "ProceduralPattern",
      "observations": [
        "INVARIANT: Keep apps_rg graph intelligence source-authored in JSON, then deterministically materialize SQLite graph-index objects for C0.3 runtime traversal, ranking, and receipts.",
        "scope: apps_rg/fact_inventory/augmented_skills_graph_sqlite.py; apps_rg/fact_inventory/graph_sqlite_path_index.py; apps_rg/runtime/c0/c03_sqlite_graph_selection.py; apps_rg/runtime/c0/c03_graph_expansion.py.",
        "enforcement: materializer validation must count graph_paths, graph_neighborhoods, graph_sibling_links, section_evidence_budget, and validated_edges_missing_rationale_count.",
        "violation_examples: dropping edge rationale during projection; querying JSON directly from C0.3 for sibling/path traversal; treating resume_metric_usage or graph_selection_rejections as canonical graph facts; creating fact-to-metric paths not present in materialized graph edges.",
        "canonical_pattern: preserve graph_edges rationale/projection/policy/status; build graph_edges_reverse, graph_paths, graph_neighborhoods, graph_sibling_links, section_evidence_budget, resume_metric_usage, and graph_selection_rejections in generated SQLite; selector returns path_signature, sibling_alternatives, and rejection_receipts.",
        "validation_recipe: run `python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py` and `python -m pytest tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py -q` after path-index helper, validator, or C0.3 context changes.",
        "doctrine_ref: plans/graph-sqlite-path-index-runtime-b7e2c4.md; plans/sqlite-graph-engine-incremental-refinement-c4f91a.md; docs/reports/apps_rg/graph_sqlite_path_index_runtime_b7e2c4_receipt.json; docs/reports/apps_rg/sqlite_graph_engine_incremental_refinement.md."
      ]
    }
  ]
}
```
