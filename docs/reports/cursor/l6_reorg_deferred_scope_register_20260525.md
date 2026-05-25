# L6 Reorg — Deferred Scope Register

**Date:** 2026-05-25  
**Parent plan (Completed):** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Follow-up plan:** [l6-reorg-deferred-followup-f3a9c2.md](../../.cursor/plans/l6-reorg-deferred-followup-f3a9c2.md)  
**E2E closeout:** [l6_plan_e2e_closeout_20260525.json](l6_plan_e2e_closeout_20260525.json)

---

## Executive summary

Parent L6 reorg **completed** `PATH_RENAME_CANONICAL` with fail-closed governance and documented gravity (86 L6→lower edges). This register captures **all deferred invasive work** so follow-up waves do not reopen the parent plan.

---

## Deferred items

| ID | Deferred from | Description | Blast / risk | Follow-up wave | P-Band hint |
|----|---------------|-------------|--------------|----------------|-------------|
| DS-1 | W4 §4 D1 | Move `L6_observability/promotion/` → active `L6_system_learning/…` (06.7) | Low — 1 prod importer (`apps_lic`) | W1.1 | P2 |
| DS-2 | W4 §4 D2 | Consolidate `utils/evaluation/*` (24) vs `shadow_eval/` (12) | **High** — eval pipeline | W1.3 ADR + future plan | P1 |
| DS-3 | W4 §4 D3 | Nest root OTEL modules under `runtime_trace/` | Medium — 8+ fan-in ingest | W1.2 | P2 |
| DS-4 | W6 / ADR-085 | Move to L_OPS: `async_eval_packet`, `governed_handoff`, `desk_d_governed_board` | Medium — eval coupling | W2.1 | P2 |
| DS-5 | W6 / 7c4e2a | Category A types → `agentic_core/_shared/types/` | **Blocked** — lifecycle instrumentation | W3.1 spike | P3 |
| DS-6 | Gap G4 | `engines/` flat bucket — chapter map vs physical split | Doc-low / move-high | W4.1 | P3 |
| DS-7 | 7c4e2a W3/W4 | Optional CI gate reading `architectural_exceptions.yaml` | Governance | W2.2 | P3 |
| DS-8 | E2E closeout | ADG regen after `span_contracts` / `snapshot/` markers | Ops (~13 min) | W2.2 | P3 |

---

## Completed in parent (not deferred)

| Item | Evidence |
|------|----------|
| Physical rename to `agentic_core/L6_system_learning/` | [l6_w5_post_rename_cert_20260525.json](l6_w5_post_rename_cert_20260525.json) |
| L6-TAG / L6-OBS fail-closed | [l6_plan_e2e_closeout_20260525.json](l6_plan_e2e_closeout_20260525.json) |
| Gravity documentation (86 edges) | [architectural_exceptions.yaml](../../config/architectural_exceptions.yaml), [ADR-085](../../architecture/adr/ADR-085-l6-observability-dependency-hygiene.md) |
| `integrity_report_generator_util` → `ops_scripts/reports/` | 7c4e2a W2.P2 (2026-05-01) |
| Doc folder rename 06_L6_Observability_and_System_Learning | W2 receipt |

---

## Chat / session capture (2026-05-25)

Deferred explicitly in assistant closeout summaries:

1. **W4 passive moves** — map-only; D1–D3 listed in [l6_w4_passive_drift_20260525.md](l6_w4_passive_drift_20260525.md).
2. **W6 gravity** — `documented_over_threshold`; physical L_OPS moves and `_shared` extraction deferred per [l6_w6_gravity_receipt_20260525.md](l6_w6_gravity_receipt_20260525.md).
3. **engines/** — remain flat; chapter map deferred to follow-up (G4).
4. **Eval consolidation** — requires dedicated ADR before any merge (D2).

---

## Proof commands (follow-up plan)

```bash
python tools/_oneoff/l6_w6_gravity_inventory.py
python tools/_oneoff/l6_e2e_closeout_verify.py
```
