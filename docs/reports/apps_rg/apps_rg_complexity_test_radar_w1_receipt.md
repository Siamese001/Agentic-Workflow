# apps_rg Complexity Test Radar — W1 Receipt

```text
STATUS: PASS
PLAN_ID: apps-rg-complexity-test-radar-605dcc
WAVE_ID: W1
WAVE_TITLE: Meta-tests (complexity radar)
SCOPE_MATCH: yes — W1.0–W1.3 meta-tests, maps, baseline fixture, CI diff gate script
SCOPE_DRIFT: none
FILES_CHANGED:
- tests/unit/apps_rg/section_rigor/rigor_gate_maps.py
- tests/unit/apps_rg/section_rigor/repair_authority.py
- tests/unit/apps_rg/section_rigor/gate_coverage_registry.py
- tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py
- tests/unit/apps_rg/section_rigor/test_parallel_dispatch_quality_paths.py
- tests/unit/apps_rg/section_rigor/test_section_complexity_budget.py
- tests/unit/apps_rg/section_rigor/fixtures/complexity_baseline.json
- tests/unit/apps_rg/section_rigor/fixtures/complexity_allowlist.json
- ops_scripts/apps_rg/section_complexity_reduction_audit.py
- ops_scripts/ci/check_apps_rg_complexity_baseline.py
COMMANDS_RUN:
- python -m pytest tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py tests/unit/apps_rg/section_rigor/test_parallel_dispatch_quality_paths.py tests/unit/apps_rg/section_rigor/test_section_complexity_budget.py -q --tb=short -p pytest_timeout -> exit 0 (36 passed)
- python ops_scripts/apps_rg/section_complexity_reduction_audit.py -> exit 0
- python ops_scripts/ci/check_apps_rg_complexity_baseline.py -> exit 0 (STATUS PASS)
- git diff -- agentic_core -> pre-existing guardian comment diffs only (no edits by this wave)
TESTS_GATES:
- W1 meta-test slice -> 36 passed
- CI complexity baseline gate -> PASS
ARTIFACTS_WRITTEN:
- tests/unit/apps_rg/section_rigor/fixtures/complexity_baseline.json
- tests/unit/apps_rg/section_rigor/fixtures/complexity_allowlist.json
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF, STATIC_COMPLEXITY_PROOF
FORBIDDEN_FILES_TOUCHED:
- agentic_core: git diff shows pre-existing comment-only changes; this wave did not author agentic_core edits
- .cursor/rules: not touched
- .cursor/templates: not touched
EXPLICIT_NON_CLAIMS:
- Not release eligibility proof
- Not LIVE_RUNTIME_PROOF
- Does not certify product output quality
NEXT_BLOCKER: none
```
