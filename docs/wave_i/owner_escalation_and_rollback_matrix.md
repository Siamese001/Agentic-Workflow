# Wave I Owner, Escalation, and Rollback Matrix

This matrix is the role-based authority sheet for Wave I execution.

| Surface Cluster | Ownership Class | Primary Role | Secondary / Escalation Role | Incident Commander Role | Rollback Authority | Required Runbook / Evidence Reference | Monitoring Coverage Reference | Readiness Status (Execution Fill-In) |
|---|---|---|---|---|---|---|---|---|
| Wave I rollout control packet and cutover decisions | repo-managed | Runtime Operator Role | Core Runtime Owner Role | Incident Commander Role | Runtime Operator Role (with Governance Owner Role concurrence for widening hold/resume) | `docs/wave_i/operational_rollout_checklist.md`, `docs/wave_h/H14_final_production_gate/production_gate_decision.md` | `docs/wave_i/monitoring_and_stabilization_plan.md` §2-4 | PENDING |
| H14-validated runtime control surfaces (`memory_db_canonical_policy`, `graph_memory_bridge`, `execution_trace` shim alignment) | mixed-control | Core Runtime Owner Role | Governance Owner Role | Incident Commander Role | Core Runtime Owner Role | `docs/wave_h/H14_final_production_gate/evidence_manifest.md`, `docs/wave_h/H14_final_production_gate/final_gate_validation_report.md` | ADG health checkpoints in `docs/wave_i/monitoring_and_stabilization_plan.md` §1.3 | PENDING |
| Semantic cache canary/soak/rollback operating surface (where enabled in rollout unit) | mixed-control | Runtime Operator Role | Retrieval/Vector Owner Role | Incident Commander Role | Runtime Operator Role | `docs/runbooks/d2_anomaly_gate_playbook.md`, `docs/runbooks/d2_rollback_drill_evidence.md` | `docs/monitoring/semantic_cache_observability.md`, `docs/monitoring/prometheus_rules_semantic_cache.yaml`, `ops_scripts/dev_tools/start_metrics_sidecar.py` | PENDING |
| Incident triage and containment path for Wave I windows | mixed-control | Governance Owner Role | Core Runtime Owner Role | Incident Commander Role | Incident Commander Role | `docs/runbooks/v15_incident_playbook.md` | Severity and escalation model in `docs/wave_i/monitoring_and_stabilization_plan.md` §4 | PENDING |
| ADG health gate verification surface used at rollout start/exit | repo-managed | ADG/Tooling Owner Role | Runtime Operator Role | Incident Commander Role | ADG/Tooling Owner Role (for gate hold decision support) | `docs/guides/infrastructure_monitoring.md`, `docs/wave_h/H14_final_production_gate/final_gate_validation_report.md` | ADG health baseline in `docs/wave_i/monitoring_and_stabilization_plan.md` §1.3 | PENDING |

## Usage Rule

- Populate `Readiness Status (Execution Fill-In)` during rollout execution only (`PENDING`, `READY`, `HOLD`, `NOT_READY`).
- Wave I exit gate cannot close while any row remains `PENDING`, `HOLD`, or `NOT_READY`.
