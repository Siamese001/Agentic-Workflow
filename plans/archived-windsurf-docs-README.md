---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\README.md'
original_relative_path: 'README.md'
source_sha256: 839fd82795df13af6d465418961f19bbdf730e4e1cb4c401d97a850014b1d99d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
