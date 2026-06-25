# C0.3 Actual Graph Full Zero-Loss Overwrite

This package is meant to be copied over the repo root.

## What it changes

- Adds deterministic metric/outcome heterogeneity policy.
- Adds C0.3 canonical graph overwrite materializer.
- Adds validation for C0.3 hardening nodes, edges, and skill rows.
- Adds tests proving append-only/idempotent behavior.
- Overwrites `apps_rg/fact_inventory/master_skills_arsenal_ledger.py` with a full replacement that validates the new C0.3 hardening layer when present.

## Critical graph target

The actual canonical graph is:

```text
apps_rg/fact_inventory/master_skills_arsenal_ledger.json
```

Because that file is very large, this artifact does not include a fabricated partial JSON. The included materializer rewrites the real local file in place after reading all existing content from your checkout.

## Apply

```bash
python apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py
python apps_rg/fact_inventory/validate_c03_graph_hardening.py
pytest tests/unit/apps_rg/fact_inventory/test_c03_graph_full_zero_loss_overwrite.py
```

## Zero-loss guarantee

The materializer is append-only by ID:

- existing `skill_rows` are retained
- existing `graph_nodes` are retained
- existing `graph_edges` are retained
- existing top-level keys are retained
- only missing C0.3 hardening rows/nodes/edges are added
