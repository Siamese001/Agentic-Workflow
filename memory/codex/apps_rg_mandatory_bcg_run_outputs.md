# apps_rg Mandatory BCG and Run-Ledger Outputs

Protected memory type: ProceduralPattern

- name: `ProceduralPattern:AppsRgMandatoryBcgRunOutputs`
- entityType: `ProceduralPattern`

Observations:

- apps_rg closeout must not report only success/failure; every run must emit `BCG_EXECUTIVE_OUTPUT.md`, `APPS_RG_MANDATORY_RUN_OUTPUT.md`, and `APPS_RG_MANDATORY_RUN_OUTPUT.json`.
- Runtime emitter: `apps_rg/runtime/mandatory_run_outputs.py`; regenerate for an existing run with `python -m apps_rg.runtime.mandatory_run_outputs <run_dir>`.
- Whole-run orchestration emits mandatory outputs before `review_bundle.zip`, so the review bundle contains the BCG RCA and the section/judge ledger even for failed runs.
- CLI closeout prints the mandatory BCG and run ledger after whole-run or section execution, so the initial run output answers what ran, what did not, which judges ran, and why.
- `tools/apps_rg/render_run_summary.py` surfaces mandatory output presence and top RCA findings; missing mandatory output is an operator-readiness gap.
- Do not weaken X2/X3 gates to make a BCG output; failed runs should produce RCA and remediation, not product authorization.
- Discovered: 2026-06-28; validated: 2026-06-28 with `python -m pytest tests/unit/apps_rg/test_mandatory_run_outputs.py tests/unit/apps_rg/test_run_summary_bcg_competencies.py tests/unit/apps_rg/test_r3r4_whole_run_reachability.py`.
