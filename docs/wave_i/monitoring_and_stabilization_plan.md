# Wave I Monitoring and Stabilization Plan

## 1. Minimum Metrics and Alert Classes to Activate

Wave I activates only minimum proven monitoring surfaces already evidenced in-repo.

Scope boundary for Wave I monitoring:

- IN: semantic-cache telemetry/alerts where that surface is part of the active rollout unit, incident severity handling, and ADG health gate checks.
- OUT: any new monitoring classes not already evidenced in `docs/monitoring/*`, `docs/runbooks/*`, or `docs/guides/infrastructure_monitoring.md`.

### 1.1 Semantic cache event telemetry (where rollout touches this surface)

- Metric family: `agentic_workflow_l4_semantic_cache_events_total{event, namespace}`
- Source references:
  - `docs/monitoring/semantic_cache_observability.md`
  - `docs/monitoring/prometheus_rules_semantic_cache.yaml`
  - `ops_scripts/dev_tools/start_metrics_sidecar.py`

Required alert classes:
- `SemanticCacheMissRateAnomaly`
- `SemanticCacheEvictionSpike`
- `SemanticCacheInvalidationSpike`
- `SemanticCacheNoTraffic`

### 1.2 Incident severity handling baseline

- Source reference: `docs/runbooks/v15_incident_playbook.md`
- Severity classes active in Wave I operations:
  - SEV-1: immediate response
  - SEV-2: same-day response
  - SEV-3: next-business-day response

### 1.3 ADG health verification baseline

- Source references:
  - `docs/guides/infrastructure_monitoring.md`
  - H14 validation pattern in `docs/wave_h/H14_final_production_gate/final_gate_validation_report.md`
- Minimum checks:
  - ADG health check at rollout start
  - ADG health check at hypercare exit decision
  - ADG health check before any rollout widening decision

## 2. Observation Windows

- Window W1: T0 to T+60m (cutover integrity window)
- Window W2: T+60m to T+24h (early stabilization window)
- Window W3: T+24h to T+72h (hypercare confirmation window)
- Window W4: T+72h to T+7d (stabilization completion window)

## 3. Hypercare Cadence

- T+15m: first anomaly and availability checkpoint
- T+60m: first stability decision checkpoint
- T+24h: daily health and incident-pattern review
- T+48h: trend review and escalation-path quality check
- T+72h: hypercare continuation/exit recommendation
- T+7d: stabilization closure decision

## 4. Severity Thresholds and Escalation Rules

### 4.1 Threshold model

- Any SEV-1 event during W1/W2 blocks rollout widening.
- Repeating SEV-2 events on same surface trigger hold and containment review.
- SEV-3 events are tracked; trend escalation applies if recurrence indicates systemic instability.

### 4.2 Escalation rules (role-based)

1. Runtime Operator role receives first alert and executes first response.
2. Surface Technical Owner role evaluates technical containment path.
3. Governance Owner role confirms policy-safe decision on hold/rollback/widen.
4. Incident Commander role (designated operational authority) finalizes major go/no-go decisions.

Escalation action tie-ins:

- G1 hold condition: missing required monitoring activation for active rollout unit.
- G2 hold condition: unstable alert behavior with unresolved ownership response path in `docs/wave_i/owner_escalation_and_rollback_matrix.md`.
- G3 hold condition: unresolved SEV-1/SEV-2 containment outcomes during hypercare windows.

## 5. Stabilization Exit Conditions

All must be true:

- Observation windows completed with no unresolved SEV-1 conditions.
- Monitoring baseline remained active and reviewable throughout Wave I.
- Escalation path was exercised or proven ready without ambiguity.
- Rollback readiness remained valid throughout rollout windows.
- No contradiction found against H14 evidence baseline.

If any condition is unmet, Wave I remains open with explicit carry-forward actions.
