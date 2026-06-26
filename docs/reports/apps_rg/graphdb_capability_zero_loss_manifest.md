# C0.3 graphDB-capability zero-loss overwrite manifest

This zip is a cumulative apps_rg graph-skills overwrite package.

It includes the prior C0.3 graph-skill hardening files and adds incremental
SQLite graph-engine capability files so the existing SQLite projection can
support graphDB-like traversal patterns.

## Canonical authority

`apps_rg/fact_inventory/master_skills_arsenal_ledger.json` remains canonical.

## SQLite projection

`artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite` remains a
generated runtime projection.

## Important note

The committed canonical JSON graph is very large. This package does not fake
a partial JSON replacement. It includes materializers that rewrite/enrich the
local canonical graph from the checked-out source while preserving all
existing nodes, edges, skill rows, role-family profiles, and metadata.
