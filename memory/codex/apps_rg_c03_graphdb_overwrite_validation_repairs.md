# apps_rg C0.3 GraphDB Overwrite Validation Repairs

Type: ProceduralPattern
Name: ProceduralPattern:AppsRgC03GraphdbOverwriteValidationRepairs

Observations:

- C0.3 graphDB/graph-skill overwrite zips must be applied through their materializers; do not blindly replace `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`.
- When `apply_graphdb_capability_sqlite_hardening.py` or `validate_graph_sqlite_path_index.py` calls `ensure_graphdb_capability_schema()`, open `augmented_skills_graph.sqlite` with `open_graph_sqlite(..., read_only=False)` because schema/view/index creation writes to SQLite.
- After granularity hardening, run the broader `python apps_rg/fact_inventory/validate_c03_graph_hardening.py`; the narrower granularity validator can pass while W4A graph nodes/edges or `skill_rows` still miss required master-ledger shape fields.
- C0.3 granularity nodes need W4A node fields (`description`, `support_level`, `visibility_rule`, `activation_status`, `evidence_risk`, `source_refs`, `projection_behavior`, `external_claim_policy`), edges need `projection_behavior`, `external_claim_policy`, `validation_status`, and C0.3 skill rows must use valid ledger enums such as `support_level=INTERNAL_ONLY` and `activation_status=ACTIVE_CONFIRMED`.
- Validate final state with `python apps_rg/fact_inventory/validate_c03_graph_hardening.py`, `python apps_rg/fact_inventory/validate_c03_graph_skill_granularity.py`, `python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py`, and scoped pytest for `tests/unit/apps_rg/fact_inventory/test_*graph*`.
- Discovered: 2026-06-26; validated: 2026-06-26.
