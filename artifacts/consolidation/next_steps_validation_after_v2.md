# Next-Steps Validation — AFTER v2 (Final PR-Ready)

Generated: 2026-02-08T23:47Z

## Final Gate Outputs (CI order)

### Phase 1: SSOT enforcement + unit tests + governance coverage

```text
Manifest SSOT Check:
  scanned=2 dirs  legacy_names=['target_paths_v2.json', 'target_paths.json']
PASS: no legacy manifest references found

Active Set SSOT Check (AST-enforced):
  governed_scripts=2
    - ops_scripts/ci/agent_count_cap.py
    - ops_scripts/ci/discovery_registry_consistency_check.py
PASS: all governed scripts use active_set_helper exclusively

Active Set SSOT Check Unit Tests: 12 passed in 0.06s

Governance Coverage Audit:
  scanned=12  governed=0  violations=0
PASS: 100% governance coverage — no CI script bypasses SSOT
```

### Phase 2: Active-set gates

```text
Agent Count Cap (discovery-aligned):
  active=149  cap=149  delta=0
  fingerprint: a3d39ecce65c6dbb0abe6f164b6323fc471dff01bb0c7d049fa100ba2f6b62c3
PASS: 149 active agents within cap 149

Discovery Registry Consistency Check:
  checked=149  file_missing=0  class_missing=0  shim_ref=0
PASS: all active records consistent

Active Set Drift Snapshot Check:
  snapshot_count=149  current_count=149
  snapshot_fingerprint=a3d39ecce65c6dbb...
  current_fingerprint=a3d39ecce65c6dbb...
PASS: active set fingerprint matches snapshot
```

### Phase 3: Remaining gates

```text
MRO New Diamond Check (entry-level prevention):
  baseline_entries=82  current_entries=82
  new_diamonds=0
PASS: no new MRO diamonds introduced

MRO Diamond Contract Check (ratcheting):
  scanned=4 roots
  count=82  ceiling=82  delta=0
  allowlisted=0  non_allowlisted=82
PASS: 82 MRO diamonds == baseline ceiling 82

Init Contract Check (scan mode): checked 22 __init__.py files
PASS: 0 violations

Skip/Quarantine Enforcement Gate (non-bypassable):
  skip: count=10  ceiling=25  delta=-15
  quarantine: count=49  ceiling=49  delta=0
PASS: all skips documented, ceilings enforced, critical tests clean

Centrality Gate (baseline + new-node detection):
  baseline_known=6
  (all modules within ceilings)
PASS: all modules within ceilings, no new gravity nodes

CI Self-Consistency Gate:
  checks_run=5  errors=0
PASS: all cross-gate artifacts are internally consistent
```

### Phase 4: Full test suite

```text
python -m pytest -q
77 passed in 2.73s
```

## Final Counts

| Metric                     | Value                                                            |
|----------------------------|------------------------------------------------------------------|
| Active agent count         | 149                                                              |
| Active set fingerprint     | a3d39ecce65c6dbb0abe6f164b6323fc471dff01bb0c7d049fa100ba2f6b62c3 |
| MRO diamonds count         | 82                                                               |
| MRO diamonds ceiling       | 82                                                               |
| New diamonds               | 0                                                                |
| Snapshot fingerprint match | Yes                                                              |
| Governance violations      | 0                                                                |
| CI self-consistency errors | 0                                                                |
| Tests passed               | 77                                                               |
| Tests failed               | 0                                                                |
| Tests skipped              | 0                                                                |

## Changes Since v1

- **Skipped tests fixed**: 3 integration tests (`test_agentic_core_no_agents_in_types`, `_config`, `_validators`) had hardcoded double-nested path `c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core`. Fixed to `Path(__file__).resolve().parents[3] / "agentic_core"`. All 3 now pass.
- **baseline_io.py**: New atomic JSON I/O helper with CI write-safety guard. `write_json_atomic()` refuses writes if `CI=true` or `GITHUB_ACTIONS=true` unless `ALLOW_BASELINE_WRITES_IN_CI=1`.
- **mro_contract_check.py**: Auto-lower writes now use `baseline_io.write_json_atomic()`.
- **active_set_snapshot_check.py**: Bump-tag auto-update writes now use `baseline_io.write_json_atomic()`.
- **gate_consistency_check.py**: Added required-key validation for snapshot and MRO baseline JSON. Added actionable failure messages with exact regeneration commands.
- **Governance scan count**: 11 -> 12 (baseline_io.py added to exclusions).
- **Test count**: 74 passed + 3 skipped -> 77 passed + 0 skipped.
- **New test files**: `test_baseline_io.py` (13 tests), updated `test_active_set_snapshot_check.py` (tmpdir-only writes).

## Commands Run

```bash
# Phase 1
python ops_scripts/ci/manifest_ssot_check.py
python ops_scripts/ci/active_set_ssot_check.py
python -m pytest tests/core/test_active_set_ssot_check.py -xvv
python ops_scripts/ci/governance_coverage_check.py

# Phase 2
python ops_scripts/ci/agent_count_cap.py
python ops_scripts/ci/discovery_registry_consistency_check.py
python ops_scripts/ci/active_set_snapshot_check.py

# Phase 3
python ops_scripts/ci/mro_new_diamond_check.py
python ops_scripts/ci/mro_contract_check.py
python ops_scripts/ci/init_contract_check.py
python ops_scripts/ci/skip_quarantine_check.py
python ops_scripts/ci/centrality_gate.py
python ops_scripts/ci/gate_consistency_check.py

# Phase 4
python -m pytest -q
```

## Created/Modified Files (This Iteration)

### Created

- `ops_scripts/ci/baseline_io.py` — Atomic JSON I/O with CI write guard
- `tests/core/test_baseline_io.py` — 13 unit tests (read/write/CI guard regression)
- `docs/reports/plans/PR_SUMMARY_CONSOLIDATION_HARDENING.md` — Reviewer-facing PR summary
- `artifacts/consolidation/next_steps_validation_after_v2.md` — This file

### Modified

- `ops_scripts/ci/mro_contract_check.py` — Uses `baseline_io.write_json_atomic()`
- `ops_scripts/ci/active_set_snapshot_check.py` — Uses `baseline_io.write_json_atomic()`
- `ops_scripts/ci/active_set_ssot_check.py` — Added `baseline_io.py` to exclusions
- `ops_scripts/ci/gate_consistency_check.py` — Required-key checks + actionable messages
- `tests/core/test_active_set_snapshot_check.py` — Writes redirected to tmpdir
- `tests/integration/agentic_core/test_repo_scan_no_agents_outside_reasoning.py` — Fixed fixture path
