# L6 Public Bootstrap Source Audit — W9b Report

**Report date:** 2026-05-18  
**Status:** PARTIAL  
**proof_eligible:** false

---

## Summary

License and PII eligibility audit for **5** registered public bootstrap sources. **0** approved, **4** pending, **1** blocked. Import allowlist is **empty** (expected). No datasets downloaded or ingested.

## Posture summary

| Source | import_posture | license_status_after |
|--------|----------------|----------------------|
| netsol/resume-score-details | pending | pending |
| CareerCorpus | pending | pending |
| Kaggle resume examples | pending | pending |
| O*NET | pending | pending |
| Academic small-n relevance | **blocked** | blocked |

**Blocked:** `academic_resume_job_relevance_small_n` — `license_status=unknown` with no operator license evidence in repo.

## Artifacts

- [source_eligibility_audit_w9b.json](../../artifacts/apps_rg/benchmarks/public_bootstrap/source_eligibility_audit_w9b.json)
- [import_allowlist_w9b.json](../../artifacts/apps_rg/benchmarks/public_bootstrap/import_allowlist_w9b.json)

## Required before any future import

Each pending source must populate `required_before_import` evidence fields (license URL, redistribution flag, PII scrub plan, attribution, local path, `operator_approval_ref`) before moving to `import_posture=approved`.

## Non-claims

- public_bootstrap is not calibration proof
- No public bytes ingested
- No human labels or calibration metrics

## Receipt

[l6_public_bootstrap_source_audit_w9b_manifest.json](l6_public_bootstrap_source_audit_w9b_manifest.json)
