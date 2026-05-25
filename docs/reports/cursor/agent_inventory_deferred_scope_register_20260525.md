# Agent Inventory — Deferred Scope Register

**Date:** 2026-05-25  
**Parent plan (Completed):** [agent-inventory-spine-taxonomy-b4e9f2.md](../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**Follow-up plan:** [agent-inventory-deferred-followup-c2a8f1.md](../../.cursor/plans/agent-inventory-deferred-followup-c2a8f1.md)  
**Closeout receipt:** [agent_inventory_spine_taxonomy_closeout_receipt.md](agent_inventory_spine_taxonomy_closeout_receipt.md)

---

## Executive summary

Parent plan **completed** W0–W3: ADR-088 spine/taxonomy separation, four-axis taxonomy on 118 `agentic_core` rows, CI A1/A2, RootCustoms orphan archive, W3 live spine path with **0** `*Agent` artifact strings. This register owns **all deferred work** so follow-up does not reopen parent waves.

---

## Deferred items

| ID | Deferred from | Description | Blast / risk | Follow-up wave | P-Band hint |
|----|---------------|-------------|--------------|----------------|-------------|
| DS-1 | W3 / GAP-3 | Full green integrated R4 product proof (`python -m apps_rg` no `--section`, or `PYTEST_APPS_RG_INTEGRATED_LIVE=1`) | High — live provider, lane chain, runtime | W1 | P1 |
| DS-2 | W3 Decision 1 | Optional class identity on HOW/spine JSON (`invoked_class`, `executor_module`) | **High** — proof contract + ADR-088 | W2 (ADR only unless approved) | P1 |
| DS-3 | W2 / GAP-4 | Physical layer moves per [misplacement ledger](agent_inventory_layer_misplacement_ledger_20260525.md) | Medium — import fan-in | W3 | P2 |
| DS-4 | W2.0 | Delete thin `RootCustomsAgent` shim after consumer burndown | Low — compat tests | W4 | P3 |
| DS-5 | Ongoing | Set any `*Agent` to `ARTIFACT_PROVEN` only with live/replay/test proof + `spine_proof_ref` | Governance — A2 | CI maintenance | P2 |

---

## Completed in parent (not deferred)

| Item | Evidence |
|------|----------|
| ADR-088 spine vs taxonomy separation | [ADR-088-product-spine-function-truth.md](../../docs/architecture/adr/ADR-088-product-spine-function-truth.md) |
| Four taxonomy axes + 118-row merge | [agent_inventory_spine_taxonomy_w1_receipt.md](agent_inventory_spine_taxonomy_w1_receipt.md) |
| CI `ARTIFACT_PROVEN=0` invariant | `ops_scripts/ci/check_agent_taxonomy_spine_invariants.py` |
| RootCustoms orphan archived | [agent_inventory_spine_taxonomy_w2_receipt.md](agent_inventory_spine_taxonomy_w2_receipt.md) |
| W3 live path (no mock backfill) | [agent_inventory_spine_taxonomy_w3_receipt.md](agent_inventory_spine_taxonomy_w3_receipt.md) |
| Mock harness path-shape only | [\_spine_proof_run/](../../artifacts/reports/agent_inventory/_spine_proof_run/) — **not** product proof |

---

## Non-goals (carry forward)

- Bulk `NOT_AGENT` on L5/healing classes — inventory uses four axes, not binary purge.
- Taxonomy registration as spine invocation — A2 remains fail-closed.
- L6 `snapshot/__init__.py` shim deletion in misplacement bucket — harness-only per ADR-088.

---

## Proof commands (follow-up plan)

```bash
python tools/governance/run_w3_live_spine_proof.py
PYTEST_APPS_RG_INTEGRATED_LIVE=1 python -m pytest tests/_apps_contract/test_integrated_spine_live_provider_e2e.py -q -o addopts=
python ops_scripts/ci/check_agent_taxonomy_spine_invariants.py
```
