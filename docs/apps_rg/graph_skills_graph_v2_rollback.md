# Graph v2 quality migration — rollback (W3)

Plan: `graph-skills-quality-enhancement-c4e8a1`

## v1 SSOT (pre-W3)

- Ledger: [master_skills_arsenal_ledger.json](../../apps_rg/fact_inventory/master_skills_arsenal_ledger.json)
- Backup created by W3 emitter: `artifacts/apps_rg/fact_inventory/backups/master_skills_arsenal_ledger_pre_graph_v2_w3_<timestamp>.json`

## Rollback procedure

1. Identify backup path from [graph_v2_migration_receipt.json](../reports/apps_rg/graph_v2_migration_receipt.json) → `backup_v1_path`.
2. Copy backup over the live ledger:

```bash
cp artifacts/apps_rg/fact_inventory/backups/<backup_file>.json apps_rg/fact_inventory/master_skills_arsenal_ledger.json
```

3. Rematerialize SQLite (optional, for C0.3 lookup parity):

```bash
python -c "from apps_rg.fact_inventory.augmented_skills_graph_sqlite import materialize_augmented_skills_graph_sqlite; materialize_augmented_skills_graph_sqlite()"
```

4. Re-run W3 emitter to confirm `active_orphan_count_after` matches pre-migration baseline if needed.

## What W3 changed

- Removed legacy `early_career` from `allowed_sections` on four `ACTIVE_CONFIRMED` actuarial skills (not a generated lane).
- Added `graph_hop_path`, `link_class_by_fact`, and `source_ledger_ref` on remediated ACTIVE rows when missing.
- Pinned `graph_v2_digest` in migration receipt for W10 digest checks.

## Non-claims

- Rollback restores ledger JSON only; runtime proof dirs under `artifacts/apps_rg/runtime_proofs/` are not reverted.
- Graph v2 does not replace v1 schema version string in metadata; quality tag is `graph_metadata.graph_skills_quality_w3`.
