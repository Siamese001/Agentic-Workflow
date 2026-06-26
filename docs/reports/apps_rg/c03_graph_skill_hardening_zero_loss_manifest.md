# C0.3 Graph Skills Hardening — Zero-Loss Overwrite Manifest

Source inspected: `Siamese001/Agentic-Workflow`, default branch `main`.

## Current main-branch gap addressed

The C0.3 graph expansion path currently builds selected skill/fact hop paths from track → pillar → skill → fact and binds those as graph evidence. The hardening overlay adds:

- multi-hop traversal to depth 4
- reverse fact → skill traversal receipts
- canonical precise edge roles and precision metadata
- frontier-size receipts by hop depth
- rejected sibling skills with rejection reasons
- metric heterogeneity buckets so résumé metrics do not collapse into repeated generic proof
- guardrail status for metric over-concentration

## Files in this overwrite kit

- `apps_rg/fact_inventory/c03_graph_skill_hardening.py`
- `apps_rg/config/c03_graph_skill_hardening_policy.json`
- `tests/unit/apps_rg/fact_inventory/test_c03_graph_skill_hardening.py`
- `docs/reports/apps_rg/c03_graph_skill_hardening_zero_loss_manifest.md`

## Integration point

Call `harden_c03_graph_expansion(meta, g, fact_claims=claims)` immediately after `bind_track_weighted_c03_graph_evidence(...)` in `apps_rg/fact_inventory/track_weighted_graph_expansion.py`, before closeout validation.

For graph materialization jobs, call `harden_augmented_skills_graph_payload(graph)` before writing `master_skills_arsenal_ledger.json` to add canonical edge metadata without removing existing fields.

## Zero-loss guarantee

The hardener only adds fields or canonical metadata. It does not delete, rename, or mutate existing skill rows, fact IDs, graph nodes, graph edges, role-family profiles, source refs, or existing proof-pool fields.
