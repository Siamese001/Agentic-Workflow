# L6 Follow-Up Plan E2E Closeout

**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.cursor/plans/l6-reorg-deferred-followup-f3a9c2.md)  
**Verifier:** [l6_followup_e2e_closeout_verify.py](../../tools/_oneoff/l6_followup_e2e_closeout_verify.py)  
**Machine receipt:** [l6_followup_plan_e2e_closeout_20260525.json](l6_followup_plan_e2e_closeout_20260525.json)

## Bundles executed

| Bundle | Command | Role |
|--------|---------|------|
| Parent structural | `python tools/_oneoff/l6_e2e_closeout_verify.py` | 21-check parent reorg invariants + L6 gates |
| W0 reconcile | `python tools/_oneoff/l6_followup_w0_reconcile.py` | Inventory ↔ YAML (43 pairs) |
| Arch exceptions | `L6_ARCH_EXCEPTIONS_FAIL_CLOSED=1 python ops_scripts/ci/check_l6_architectural_exceptions.py` | Documented gravity SSOT |
| Follow-up surface | `python tools/_oneoff/l6_followup_e2e_closeout_verify.py` | W0–W4 artifacts, moves, imports, OTEL pytest |

## Definition of Done mapping

| DoD | Evidence |
|-----|----------|
| DoD-0 | Deferred register on disk |
| DoD-1 | W0 reconcile JSON `reconcile_status: PASS` |
| DoD-2 | ADR-087 + promotion/OTEL paths + batch receipt |
| DoD-3 | 43 pairs documented (amended; ≤24 deferred) |
| DoD-4 | Parent + follow-up E2E verifiers PASS |
| DoD-5 | Category A spike report filed |
