# C0.3 graph-skill granularity hardening — zero-loss overwrite package

## Actual graph target

The canonical graph is the JSON ledger:

`apps_rg/fact_inventory/master_skills_arsenal_ledger.json`

This package does not replace that file blindly. It includes an idempotent hardening script that opens the current main-branch graph JSON, preserves every existing node/edge/skill row, and adds granular C0.3 graph structure.

## What this adds

- Granular capability-domain nodes
- Metric-bucket nodes
- Metric-option nodes
- C0.3-specific skill rows
- Typed edges for:
  - track → capability domain
  - capability domain → skill
  - skill → metric bucket
  - metric bucket → metric
  - skill → metric option
  - section → selectable skill
  - skill → sibling/reinforcement skill
- Selection policy requiring:
  - distinct metric buckets
  - rejected sibling receipts
  - candidate nodes visited
  - frontier size by hop depth
  - reverse traversal support

## Why this is zero-loss

The apply script:

1. Reads the existing graph JSON.
2. Stores before-counts and digest.
3. Adds or merges rows by stable ids.
4. Preserves existing scalar fields on conflict.
5. Merges list fields without duplicates.
6. Validates that no previous ids disappeared.
7. Writes a backup before replacing the JSON.
8. Emits a receipt under `docs/reports/apps_rg/`.

## Apply

```bash
python apps_rg/fact_inventory/apply_c03_graph_skill_granularity_hardening.py --dry-run
python apps_rg/fact_inventory/apply_c03_graph_skill_granularity_hardening.py
python apps_rg/fact_inventory/validate_c03_graph_skill_granularity.py
pytest tests/unit/apps_rg/fact_inventory/test_c03_graph_skill_granularity_hardening.py
```
