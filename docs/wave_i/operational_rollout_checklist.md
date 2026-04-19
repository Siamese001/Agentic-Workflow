# Wave I Operational Rollout Checklist

Use this checklist as the operator execution sheet for immediate post-H14 rollout.

## A. Pre-Rollout Checks

- [ ] Confirm H14 baseline artifacts are present and unchanged:
  - `docs/wave_h/H14_final_production_gate/production_gate_decision.md`
  - `docs/wave_h/H14_final_production_gate/final_gate_validation_report.md`
  - `docs/wave_h/H14_final_production_gate/evidence_manifest.md`
- [ ] Confirm gate status remains aligned with baseline (`PASS`, Wave H `COMPLETE`).
- [ ] Confirm current ADG health is green and snapshot is recorded for rollout event.
- [ ] Confirm ownership classes for in-scope surfaces from `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`.
- [ ] Confirm Wave I execution authority matrix is present and usable: `docs/wave_i/owner_escalation_and_rollback_matrix.md`.
- [ ] Confirm no new scope items that reopen H-wave blockers.

## B. Cutover Checks

- [ ] Define rollout unit order (canary -> constrained widening -> full approved scope).
- [ ] Assign role-based cutover authority:
  - [ ] Runtime Operator (execution)
  - [ ] Core Runtime Owner (technical sign-off)
  - [ ] Governance Owner (policy/escalation posture)
- [ ] Validate cutover go/no-go packet contains:
  - [ ] baseline snapshot ID
  - [ ] active monitoring confirmation
  - [ ] rollback readiness confirmation
- [ ] Execute cutover only if all packet checks are complete.

## C. Rollback Readiness Checks

- [ ] Confirm rollback drill evidence exists: `docs/runbooks/d2_rollback_drill_evidence.md`.
- [ ] Confirm rollback authority per surface cluster is populated in `docs/wave_i/owner_escalation_and_rollback_matrix.md`.
- [ ] Confirm rollback trigger table is available to operators in active runbooks.
- [ ] Confirm rollback target time is defined and accepted by Runtime Operator Role.
- [ ] Confirm fail-closed verification steps are executable for active rollout unit.
- [ ] Confirm rollback escalation role chain is explicit (primary -> secondary -> incident commander role) in the Wave I matrix.

## D. Monitoring Live Checks

- [ ] For rollout units that include the semantic-cache surface, confirm metrics exposure path is active (`ops_scripts/dev_tools/start_metrics_sidecar.py`).
- [ ] For rollout units that include the semantic-cache surface, confirm required alert classes are enabled from `docs/monitoring/prometheus_rules_semantic_cache.yaml`.
- [ ] Confirm no blind spots in first-run observation window.
- [ ] Confirm dashboard/query commands for live checks are available to operators.

## E. Owner and Escalation Confirmation

- [ ] Map each in-scope surface to role-based primary owner and escalation owner in `docs/wave_i/owner_escalation_and_rollback_matrix.md`.
- [ ] Confirm severity handling model is available to operators (`docs/runbooks/v15_incident_playbook.md`).
- [ ] Confirm escalation SLA expectations:
  - [ ] SEV-1 immediate
  - [ ] SEV-2 same day
  - [ ] SEV-3 next business day
- [ ] Confirm incident communication path and decision authority are documented.

## F. First-Run Observation Checks

- [ ] Record T0 start timestamp for rollout observation period.
- [ ] Execute first observation checkpoint at T+15m.
- [ ] Execute stability checkpoint at T+60m.
- [ ] Execute early hypercare checkpoint at T+24h.
- [ ] Record anomalies, interventions, and rollback decisions in one run log.

## G. Go/No-Go Decision Points

### G1 — Pre-cutover Go/No-Go

- GO only if sections A-D are complete with no blocking gaps.
- NO-GO if any baseline contradiction, missing matrix role assignment, or missing rollback readiness exists.

### G2 — Canary-to-Widening Go/No-Go

- GO only if no SEV-1 events, no unresolved SEV-2 safety issues, and monitoring is stable.
- NO-GO if (a) alert behavior is unstable on enabled monitoring surfaces, (b) ADG health check fails, or (c) owner/escalation path is unclear in the Wave I matrix.

### G3 — Hypercare Exit Go/No-Go

- GO (exit Wave I) only if Wave I exit criteria in `exit_criteria_and_gate.md` are met.
- NO-GO if stabilization conditions remain unmet, matrix readiness statuses are unresolved, or rollback confidence is incomplete.
