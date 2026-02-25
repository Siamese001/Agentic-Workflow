# V15 Guardian Incident Playbook

## 1. Scope

This playbook covers incidents triggered by the V15 Guardian enforcement
subsystem. It applies to all three enforcement modes (LOG_ONLY, SOFT_FAIL,
HARD_FAIL) and covers pipe-order violations, policy-config mutations,
hash-mismatch escalations, and clock anomalies.

## 2. Severity Levels

| Level | Mode | Behavior | Response SLA |
|-------|------|----------|--------------|
| SEV-3 (Low) | LOG_ONLY | Violation logged, execution continues | Next business day |
| SEV-2 (Medium) | SOFT_FAIL | Execution aborted with structured failure | Same day |
| SEV-1 (High) | HARD_FAIL | Exception raised, execution halted | Immediate |

### Classification Rules

- **SEV-1**: Any `V15HardFailAbort` raised in production; any rollback hash
  mismatch with escalation threshold breached; any pipe-order violation in
  HARD_FAIL mode.
- **SEV-2**: `V15SoftFailAbort` returned; policy-config mutation detected;
  repeated LOG_ONLY violations on same manifest (>3 occurrences).
- **SEV-3**: Single LOG_ONLY violation; ordering warnings; non-blocking
  evidence gaps.

## 3. Triage Steps

1. **Identify the mode**: Check `V15_ENFORCEMENT` environment variable value.
2. **Locate the trace**: Find the `trace_id` / `correlation_id` in logs.
3. **Classify violation type**: PIPE, POLICY, HASH, or CLOCK.
4. **Check gateway state**: Inspect `_pipe_violations`, `_policy_violations`,
   `_seen_signals` size, `_mismatch_tracker` escalation status.
5. **Determine blast radius**: How many manifests affected? Single agent or
   cross-agent?

## 4. Evidence Collection Commands

Run these commands from the repository root to collect evidence:

```bash
# P1 compliance gate
python -m pytest tests/guardian/test_v15_p1_compliance.py -q

# P6 refinement gate
python -m pytest tests/guardian/test_v15_p6_refinement.py -q

# Full guardian suite
python -m pytest tests/guardian/ -q

# Generate review summary with JSON envelope
python ops_scripts/review/generate_v15_review_summary.py \
    --out docs/reports/plans/v15_review_summary.md \
    --json-out incident_review.json

# Validate policy pack
python ops_scripts/policy/validate_v15_policy_pack.py \
    --path agentic_core/L0_maintenance/policy/v15_policy_pack.json \
    --json-out incident_policy.json

# Create incident bundle
python ops_scripts/incident/create_v15_incident_bundle.py \
    --out-dir incident_<ID> --incident-id <ID>
```

## 5. Decision Tree

### LOG_ONLY Violations

```
Is it a known pre-existing violation?
├── YES → Document in triage.md, monitor frequency, no action
└── NO → Is it a pipe-order violation?
    ├── YES → Check if pipe step sequence changed; review recent commits
    └── NO → Is it a policy-config mutation?
        ├── YES → Identify mutating code path; add guard
        └── NO → Log for postmortem, continue monitoring
```

### SOFT_FAIL Violations

```
Did the gateway return structured failure?
├── YES → Was rollback verified?
│   ├── YES → Safe state confirmed; investigate root cause
│   └── NO → ESCALATE to SEV-1; hash mismatch possible
└── NO (unexpected) → ESCALATE to SEV-1; gateway contract broken
```

### HARD_FAIL Violations

```
Was V15HardFailAbort raised?
├── YES → Execution halted cleanly
│   ├── Check rollback integrity
│   ├── Capture pre/post snapshots
│   └── Proceed to remediation
└── NO (unhandled exception) → ESCALATE; possible gateway bug
```

## 6. Immediate Containment

### HARD_FAIL

1. **Do NOT restart** the affected agent until root cause is identified.
2. Capture the full stack trace and `trace_id`.
3. Check `_mismatch_tracker.escalated` — if true, hash integrity is compromised.
4. If rollback failed, manually verify filesystem/git/memory state hashes.
5. Consider temporarily switching to SOFT_FAIL mode:
   `export V15_ENFORCEMENT=soft`

### SOFT_FAIL

1. Review the `GatewayResult.error` field for structured failure details.
2. Check if the manifest can be safely retried.
3. If repeated failures on same manifest, check for determinism issues.

### LOG_ONLY

1. No immediate containment required.
2. Monitor log volume — sudden spike may indicate systemic issue.
3. If violation count exceeds threshold, consider escalating to SOFT_FAIL.

## 7. Remediation + Validation

### Fix Workflow

1. Identify root cause in `analysis/root_cause.md`.
2. Implement fix in a feature branch.
3. Run full guardian suite: `python -m pytest tests/guardian/ -q`
4. Run P1 + P6 regression gates.
5. Generate fresh review summary and verify approval status.
6. Commit with reference to incident ID.

### Validation Checklist

- [ ] P1 compliance gate passes (76/76)
- [ ] P6 refinement gate passes (12/12)
- [ ] No new violations in LOG_ONLY mode
- [ ] Review summary shows "Ready for human approval: YES"
- [ ] Policy pack validates clean

## 8. Postmortem Template

```markdown
# Postmortem: INC-<ID>

## Summary
<!-- One-line description -->

## Impact
<!-- Severity, duration, affected components -->

## Root Cause
<!-- Technical root cause -->

## Detection
<!-- How was the incident detected? Which mode/gate? -->

## Resolution
<!-- What was done to fix it? -->

## Lessons Learned
<!-- What can be improved? -->

## Action Items
- [ ] Action 1
- [ ] Action 2
```
