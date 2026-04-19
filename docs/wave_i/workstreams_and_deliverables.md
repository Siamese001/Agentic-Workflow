# Wave I Workstreams and Deliverables

Wave I uses four tightly bounded workstreams only.

## WS1 — Rollout Readiness and Cutover Control

- Purpose: Turn H14 pass status into a controlled, stepwise rollout path with explicit go/no-go points.
- Outputs:
  - Consolidated pre-rollout and cutover checklist.
  - Cutover decision checkpoints bound to H14 evidence baseline.
  - Role-based cutover authority table sourced from `docs/wave_i/owner_escalation_and_rollback_matrix.md`.
- Dependencies:
  - `docs/wave_h/H14_final_production_gate/*`
  - `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`
- Done criteria:
  - Rollout sequence is operator-usable and unambiguous.
  - Every cutover checkpoint has an explicit pass/fail criterion.
  - No checklist item contradicts H14 gate evidence.

## WS2 — Monitoring Activation and Alert Baseline

- Purpose: Activate minimum live observability required to safely run immediate post-gate operations.
- Outputs:
  - Minimum metric/alert class baseline for Wave I limited to already-proven in-scope surfaces.
  - Observation windows and alert review expectations.
  - Monitoring activation checks tied to existing metrics surfaces.
- Dependencies:
  - `docs/monitoring/semantic_cache_observability.md`
  - `docs/monitoring/prometheus_rules_semantic_cache.yaml`
  - `ops_scripts/dev_tools/start_metrics_sidecar.py`
  - `docs/guides/infrastructure_monitoring.md`
- Done criteria:
  - Required metric streams and alert classes are explicitly listed.
  - Observation windows and threshold handling are documented.
  - Monitoring checks are integrated into rollout go/no-go control.

## WS3 — Stabilization and Hypercare Operations

- Purpose: Define immediate post-cutover operating rhythm for anomaly detection, triage, containment, and review.
- Outputs:
  - Hypercare cadence (first 24h, first 72h, first 7d).
  - Severity thresholds and incident response triggers.
  - Early-run review rhythm and stabilization exit conditions.
- Dependencies:
  - `docs/runbooks/v15_incident_playbook.md`
  - `docs/runbooks/d2_anomaly_gate_playbook.md`
- Done criteria:
  - Severity handling and escalation path are role-bound.
  - Hypercare timing and review events are measurable.
  - Stabilization exit conditions are explicit and testable.

## WS4 — Ownership, Escalation, and Rollback Readiness

- Purpose: Ensure operators can safely contain failures and recover with role-based accountability.
- Outputs:
  - Role-based ownership and escalation matrix (`docs/wave_i/owner_escalation_and_rollback_matrix.md`).
  - Rollback readiness checks and validation expectations.
  - Rollback trigger table linked to observed conditions.
- Dependencies:
  - `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`
  - `docs/runbooks/d2_rollback_drill_evidence.md`
  - `docs/runbooks/v15_incident_playbook.md`
- Done criteria:
  - Every in-scope surface has a role-assigned primary and escalation path.
  - Rollback readiness criteria are complete before rollout widening.
  - Rollback triggers are explicit and operator-actionable.
