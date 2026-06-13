<!-- V15_INCIDENT_PLACEHOLDER -->
# V15 Incident Bundle: V15-FINAL

## Incident ID

`V15-FINAL`

## Status

- [ ] Triage complete
- [ ] Root cause identified
- [ ] Remediation applied
- [ ] Validation passed
- [ ] Postmortem written

## Evidence Collection Commands

```bash
# P1 compliance gate
python -m pytest tests/guardian/test_v15_p1_compliance.py -q

# P6 refinement gate
python -m pytest tests/guardian/test_v15_p6_refinement.py -q

# Full guardian suite
python -m pytest tests/guardian/ -q

# Generate review summary
python ops_scripts/review/generate_v15_review_summary.py \
    --out artifacts/review_summary.md \
    --json-out artifacts/review_envelope.json

# Validate policy pack
python ops_scripts/policy/validate_v15_policy_pack.py \
    --path agentic_core/L0_maintenance/policy/v15_policy_pack.json \
    --json-out artifacts/policy_envelope.json
```

## Bundle Contents

- `inputs/` — Environment snapshot and command log
- `artifacts/` — Collected evidence (guardian report, review summary, policy pack)
- `analysis/` — Triage, root cause, and remediation notes

## Playbook

See `docs/runbooks/v15_incident_playbook.md` for the full incident response procedure.
