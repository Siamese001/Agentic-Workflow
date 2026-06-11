---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\guardian-execute-ssot-overlap-reduction-fad400.md'
original_relative_path: 'guardian-execute-ssot-overlap-reduction-fad400.md'
source_sha256: e5afa284ee674bbf2d5caef290797f5960dc94d7af81775370d60fa5f8f60a7c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Guardian / execute_ssot.py Overlap Reduction Plan

Reduce redundancy between `tests/guardian/` (70+ test files) and `agentic_core/L0_routing/scripts/execute_ssot.py` (7,600-line monolith) by mapping every overlap, classifying it, and prescribing targeted deletions or consolidations.

---

## Context: execute_ssot.py Is Marked FROZEN

Line 2: `# FROZEN — superseded by l0_execute.py`. This means it is a legacy entry-point kept alive only for backward-compat. Several guardian tests still target it directly, creating tech debt.

---

## What execute_ssot.py Contains (Relevant to Tests)

| Concern | Lines |
|---|---|
| `resolve_repo_root()` — deterministic root resolver | 744–755 |
| `_optional_runtime_guard()` / `_apply_v15_enforcement_flag()` | 560–584, 758–762 |
| `_maybe_force_utf8_console()` / `_maybe_force_utf8_logging_handlers()` | 778–821 |
| `run_fence_self_check()` — write-gateway + immutable-roots probe (calls `sys.exit`) | 624–741 |
| `_preflight_import_check()` — `_legacy_main` symbol gate | 537–557 |
| `_v15_build_ssot_manifest()` / `_v15_ssot_gateway_audit()` | 829–899 |
| `FailureType` / `RoutingTier` / `RoutingInputs` / `RoutingDecision` / `compute_routing_decision()` | 956–1147 |
| `SovereignDecisionEngine` (flat class) | 1424+ |
| `ASTCodeQualityValidator` — scans for missing return-type hints | 1241–1289 |
| `ReconciliationViolation` / `ReconciliationManifest` | 1155–1238 |
| `HealContext` frozen dataclass | 1341–1416 |
| `_fire_meta_learning_intake()` — FAISS/corpus/version-store wiring | 120–508 |

---

## Overlaps Mapped

### Category A — Guardian Tests Exercising a FROZEN File

| Test file | What it tests | Issue |
|---|---|---|
| `test_execute_ssot_v15_contract.py` | `resolve_repo_root`, `_apply_v15_enforcement_flag`, `_optional_runtime_guard`, CLI `--help`, dry-run artifact guard | All targeted at a FROZEN module. If the live path is `l0_execute.py`, these tests have no regression value. |
| `test_ssot_heal_runner_preflight.py` | `_legacy_main` symbol presence; retry-restore logic via mocks | Mock-only tests; the three non-trivial cases test a retry pattern that never runs in production. The one real import (`_legacy_main`) is covered elsewhere. |
| `test_ssot_utf8_output.py` | `_maybe_force_utf8_console`, `_maybe_force_utf8_logging_handlers` | 10 cases for two stdlib-wrapping one-liners in a frozen file. Over-specified. |

### Category B — Dual Scanning (Both execute_ssot and Test Walk the Same Blueprint)

| Test file | execute_ssot equivalent | Redundancy |
|---|---|---|
| `test_ssot_alignment.py` — `TestSSOTAlignment.test_blueprint_reality_check` | `_legacy_main` calls `FilesystemSSOTReconcilerAgent.scan_territory()` against the same `structure_blueprint_config` | Two separate directory walks; test duplicates runtime scan rather than asserting on its result. |
| `test_structure_drift.py` | execute_ssot calls `generate_structure_manifest` indirectly via reconciler phases | 91-line file whose entire concern is a sub-function of SSOT alignment. |
| `test_guardian_hygiene.py` — temp/empty/init-only folder scans | execute_ssot healing phases call `HygieneAgent` which does the same three scans | Both scan for identical artefacts; test uses synthetic fixtures so overlap is acceptable in isolation, but the scan logic is defined twice. |

### Category C — Logic in execute_ssot That Belongs Only in Tests

| Function in execute_ssot.py | Issue |
|---|---|
| `run_fence_self_check()` (L624–741) — validates write-gateway, protected-root policy, calls `sys.exit()` | Test/probe logic embedded in production runtime. Has no caller in `_legacy_main`. Already structurally tested by `test_circuit_breaker_gate.py` and `test_guardian_gateway_bypass.py`. |
| `ASTCodeQualityValidator` (L1241–1289) — scans files for missing return-type hints | Fully duplicated by `test_code_quality_metrics.py`. Unreferenced from the main execution path. |

### Category D — No Overlap (Keep As-Is)

- `test_guardian_contract.py`, `test_registry_completeness.py` — test contract types / registry; no execute_ssot overlap
- `test_v15_p2/3/4/5/6/7/8_compliance.py` — test determinism contract types independently
- `compute_routing_decision()` and its types — correctly targeted by compliance tests; do not move until `l0_execute.py` migration confirmed

---

## Proposed Steps

### Step 1 — Delete `test_ssot_heal_runner_preflight.py` *(~101 lines)*
All three non-trivial tests are mock-only with no production path. The one real assertion (`_legacy_main` is callable) is a free side-effect of any other execute_ssot import test.
- **Verify first:** confirm no CI job references this file explicitly.

### Step 2 — Shrink `test_ssot_utf8_output.py` to 2 cases *(saves ~150 lines)*
Keep: one happy-path reconfigure test (Windows) + one swallowed-exception test.
Drop: the 8 redundant platform/handler variants that test identical stdlib behavior.

### Step 3 — Merge `test_structure_drift.py` into `test_ssot_alignment.py` *(removes 1 file, ~91 lines)*
Add the 4 drift tests as `TestStructureDrift` inside `test_ssot_alignment.py`. Delete `test_structure_drift.py`.

### Step 4 — Remove `TestDefaultOutputsGitignored` from `test_execute_ssot_v15_contract.py` *(~22 lines)*
These two gitignore assertions (`test_logs_dir_gitignored`, `test_evidence_json_gitignored`) are setup invariants that cannot regress. Fold into a single parametrized check in `test_conftest_ignore_policy.py` which already handles gitignore policy.

### Step 5 — Extract `run_fence_self_check()` from execute_ssot.py *(removes ~118 lines from production file)*
Move its assertions into `test_guardian_gateway_bypass.py` as a new `TestFenceSelfCheck` class. Remove the function from execute_ssot (it calls `sys.exit` and has zero callers in `_legacy_main`).

### Step 6 — Delete `ASTCodeQualityValidator` from execute_ssot.py *(removes ~50 lines)*
It is unreachable from `_legacy_main` and fully covered by `test_code_quality_metrics.py`. Confirm no import in any other module before deleting.

### Step 7 — Refactor `test_ssot_alignment.py::test_blueprint_reality_check` *(~80-line targeted rewrite)*
Replace the duplicated `os.walk` loop with a call to `FilesystemSSOTReconcilerAgent`'s scan result, so the test asserts on the runtime agent's output rather than independently re-walking the tree.

---

## Net Effect

| Action | Files affected | ~Lines |
|---|---|---|
| Delete files | `test_ssot_heal_runner_preflight.py`, `test_structure_drift.py` | −192 |
| Shrink tests | `test_ssot_utf8_output.py`, `test_execute_ssot_v15_contract.py` | −172 |
| Remove dead code from execute_ssot.py | `run_fence_self_check`, `ASTCodeQualityValidator` | −168 |
| Refactor (no net delete) | `test_ssot_alignment.py` | ~80 rewrite |
| **Total reduction** | | **~530 lines** |

---

## Open Question for User

> The file header says `# FROZEN — superseded by l0_execute.py`.

Before executing Steps 5–6 (removing functions from execute_ssot.py), confirm:
1. Is `l0_execute.py` the live replacement with equivalent contract test coverage?
2. Should `test_execute_ssot_v15_contract.py` be deleted wholesale once `l0_execute.py` has its own contract tests (rather than just trimmed in Step 4)?

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

