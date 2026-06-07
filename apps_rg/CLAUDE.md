# apps_rg Runtime Seam Discipline

> Nested memory: auto-loads when working under `apps_rg/`. Migrated from the Cursor glob-scoped
> rule `010-apps-rg-runtime-seams` (globs `apps_rg/**`, `tests/**/apps_rg/**`, `artifacts/apps_rg/**`).
> Applies when editing or verifying resume-generator runtime seams.

## Current golden path focus

Build and verify section-specific runtime seams before broad integration:

- headline
- executive_summary
- Unify bullets
- Unify narrative
- IBM bullets
- IBM narrative
- competencies

## Locked deterministic copy

Do not rewrite locked deterministic sections unless explicitly authorized:

- InsurTech
- EY
- Early Career
- Education
- Certifications
- company names
- titles
- locations
- dates

## Gates and judges

- X1D judges belong after L2 section output for semantic quality.
- X2 deterministic gates enforce hard correctness.
- X3 aggregates X1D and X2 into ALLOW, REVIEW, or BLOCK.
- L6 is offline shadow calibration only. It never approves runtime output and never mutates the current run.

## Runtime evidence

For any apps_rg implementation claim, show:

- exact section generated
- prompt/profile used
- provider/model status, including mocked or blocked state
- output artifact path
- X1D judge result if applicable
- X2 deterministic gate result
- X3 disposition if wired
