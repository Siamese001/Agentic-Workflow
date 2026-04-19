# Wave I Execution Run 001

## Chosen Rollout Unit

- Rollout unit: **Semantic-cache-enabled single canary unit (no widening in this run record set)**.
- Scope intent: establish the first bounded Wave I execution packet for canary-only operationalization.

## Why this is the smallest valid first rollout unit

1. Monitoring and alert evidence for this surface is explicit and already in-repo:
   - `docs/monitoring/semantic_cache_observability.md`
   - `docs/monitoring/prometheus_rules_semantic_cache.yaml`
   - `ops_scripts/dev_tools/start_metrics_sidecar.py`
2. Canary/soak and rollback procedures are explicit and already in-repo:
   - `docs/runbooks/d2_canary_soak_operator_sheet.md`
   - `docs/runbooks/d2_anomaly_gate_playbook.md`
   - `docs/runbooks/d2_rollback_drill_evidence.md`
3. Ownership and rollback authority are already mapped in Wave I matrix rows for this surface and shared Wave I controls:
   - `docs/wave_i/owner_escalation_and_rollback_matrix.md`
4. This unit stays bounded to canary execution and avoids broad rollout assumptions.

## Pre-Filled from Repo Evidence

- H14 baseline references and baseline snapshot lineage (`04182026_2044`).
- In-scope rollout-unit label and explicit out-of-scope boundaries.
- Matrix-linked surface clusters and role labels.
- Known monitoring/runbook references.
- Known rollback evidence references and authority alignment language.
- Exit criteria row mapping (EC-01 through EC-07) and evidence-source pointers.

## Execution-Time Fill-In Only

- UTC timestamps and record IDs.
- Live ADG health result and live command/evidence logs.
- Approval outcomes (`APPROVE`/`DENY`/`HOLD`) and sign-offs.
- Readiness states per row (`PENDING`, `READY`, `HOLD`, `NOT_READY`) at runtime.
- Operational observations, incident facts, containment actions, and any rollback execution details.
- Final exit pass/fail outcomes and closure status.

## Operator Execution Order

1. `pre_rollout_readiness_record.md`
2. `cutover_go_no_go_record.md` (G1 then subsequent approved checkpoints)
3. `hypercare_run_log.md`
4. `incident_and_rollback_decision_log.md` (as incidents occur)
5. `wave_i_exit_decision_record.md`
6. `carry_forward_register.md` (only unresolved later-wave items)
