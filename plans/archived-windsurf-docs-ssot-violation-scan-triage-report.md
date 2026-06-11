---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ssot-violation-scan-triage-report.md'
original_relative_path: 'ssot-violation-scan-triage-report.md'
source_sha256: 455e1c323131134d44bc13f58dbe6a8c910dbca21f884febb380b0405cd99044
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Violation Scan — Triage Report

**Scanner:** `ops_scripts/ci/ssot_violation_scanner.py`
**Report:** `artifacts/ssot_violation_scan.json`
**Files scanned:** 3,088 across 10 SOVEREIGN_TERRITORIES
**Targets:** 46 SSOT string constants + 2 import path patterns

---

## Summary

| Category | Count | Action |
|---|---|---|
| `REPLACE` — hardcoded path in path-construction context | 1,865 | Fix: swap literal for SSOT constant |
| `WRONG_IMPORT` — `structure_blueprint_config` instead of canonical | 298 | Fix: update import path |
| `SKIP_DYNAMIC` — comparison / dict-key, manual review | 1,329 | Review |
| `SKIP_COMMENT` — in docstring/comment only | 739 | None |
| `SKIP_TEST_DATA` — test fixture assertion | 105 | None |
| **Actionable total** | **2,163** | |

---

## REPLACE — Non-Test Breakdown

| Category | Non-test count | Test count |
|---|---|---|
| `root_dir` (e.g. `"agentic_core"`, `"archives"`) | ~480 | ~820 |
| `layer_root` (e.g. `"L0_routing"`, `"L5_safety"`) | ~210 | ~370 |
| `layer_path` (e.g. `"agentic_core/L5_safety"`) | ~55 | ~30 |
| `filename` (e.g. `"runtime_state.json"`) | ~28 | ~25 |
| `compound_path` (e.g. `"docs/reports/plans"`) | ~15 | ~10 |
| `test_path` (e.g. `"tests/unit"`) | ~12 | ~18 |

**Primary action target: ~800 non-test REPLACE hits.**

---

## WRONG_IMPORT — Top Offenders (non-test, 246 hits in 101 files)

All import `agentic_core.L5_safety.config.structure_blueprint_config` instead of
`agentic_core.L5_safety.config.structure_blueprint`.

| Hits | File |
|---|---|
| 28 | `agentic_core/L5_safety/reasoning/location_validator.py` |
| 20 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| 10 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` |
| 8 | `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` |
| 6 | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` |
| 6 | `agentic_core/L5_safety/utils/location_utils_util.py` |
| 4 | `agentic_core/interfaces/structure_config.py` |
| 4 | `agentic_core/L0_routing/scripts/execute_ssot.py` |
| 4 | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` |
| 4 | `agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py` |
| 4 | `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` |
| 2 | `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` |
| 2 | `agentic_core/L5_safety/enforcement/system_enforcer.py` |
| 2 | `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py` |
| 2 | `agentic_core/base_agents/L0RoutingBase.py` |
| 2 | `agentic_core/mixins/ast_enforcement_mixin.py` |
| 2 | `agentic_core/config/core/domain_constitution_config.py` |
| 2 | `agentic_core/config/core/registry_config.py` |
| *(+83 more files)* | |

**Test files with WRONG_IMPORT: 52 hits** — lower priority, but still violate SSOT.

---

## Top Offending Files (REPLACE + WRONG_IMPORT combined)

| Hits | File |
|---|---|
| 73 | `tests/governance/test_layer_sovereignty_enforcer.py` |
| 42 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| 32 | `agentic_core/L5_safety/reasoning/location_validator.py` |
| 27 | `tools/semantic_gap_analyzer.py` |
| 23 | `agentic_core/L5_safety/config/structure_blueprint/_constants.py` |
| 23 | `agentic_core/L5_safety/config/structure_blueprint/_verify.py` |
| 22 | `tests/unit_min_deps/test_unsafe_io_subprocess_detector.py` |
| 21 | `tests/guardian/test_mece_naming_compliance.py` |
| 20 | `agentic_core/L0_routing/scripts/execute_ssot.py` |

---

## Remediation Phases

### Phase A — HIGH: Fix WRONG_IMPORT in non-test production code (246 hits, 101 files)

**Pattern:** `from agentic_core.L5_safety.config.structure_blueprint_config import X`
**Fix:** `from agentic_core.L5_safety.config.structure_blueprint import X`

Note: The shim (`structure_blueprint_config.py`) still works but is the legacy path.
New code and existing production code must use the canonical package directly.

Priority order:
1. `agentic_core/L5_safety/reasoning/` (agents — highest churn risk)
2. `agentic_core/L5_safety/enforcement/` (enforcers)
3. `agentic_core/interfaces/`, `agentic_core/base_agents/`, `agentic_core/mixins/`
4. `agentic_core/config/core/`, `agentic_core/L0_routing/scripts/`

### Phase B — HIGH: Fix REPLACE hits for `LAYER_ROOTS` bare strings (non-test)

Bare `"L0_routing"`, `"L1_cognition"` etc. in non-test path construction.
**Fix:** `from agentic_core.L5_safety.config.structure_blueprint.ssot import LAYER_ROOTS`
and reference `LAYER_ROOTS` (frozenset) instead of literal strings.

Primary files:
- `ops_scripts/root_scripts/_ssot_dry_run.py`
- `ops_scripts/root_scripts/_ssot_dry_run_isolated.py`
- `ops_scripts/root_scripts/move_mislocated_tests_fixed.py`
- `agentic_core/L0_routing/scripts/execute_ssot.py`

### Phase C — MEDIUM: Fix REPLACE hits for root_dir strings in non-test code

Top constants needing replacement in non-test code:
- `AGENTIC_CORE_DIR` — `ops_scripts/ci/ast_gap_analysis.py`, `ops_scripts/ci/scan_broken_test_imports.py`
- `AGENT_DISCOVERY_JSON` — files using `"agent_discovery_full.json"` raw
- `RUNTIME_STATE_JSON` — files using `"runtime_state.json"` raw
- `DATA_DIR`, `DOCS_DIR` — newly added targets with ~249 and ~137 hits respectively

### Phase D — LOW: Fix WRONG_IMPORT in test files (52 hits)

Same pattern as Phase A but in test files. Lower risk since tests don't affect production
import graphs, but they violate SSOT and may break if the shim is ever removed.

---

## SSOT Constants Reference

| Constant | Value | Canonical Import |
|---|---|---|
| `ARCHIVES_DIR` | `"archives"` | `agentic_core.L0_routing.config.path_constants` |
| `AGENTIC_CORE_DIR` | `"agentic_core"` | `agentic_core.L0_routing.config.path_constants` |
| `APPS_LIC_DIR` | `"apps_lic"` | `agentic_core.L0_routing.config.path_constants` |
| `APPS_RG_DIR` | `"apps_rg"` | `agentic_core.L0_routing.config.path_constants` |
| `APPS_SHARED_DIR` | `"apps_shared"` | `agentic_core.L0_routing.config.path_constants` |
| `OPS_SCRIPTS_DIR` | `"ops_scripts"` | `agentic_core.L0_routing.config.path_constants` |
| `TESTS_DIR` | `"tests"` | `agentic_core.L0_routing.config.path_constants` |
| `L0_ROUTING_DIR`…`L6_OBSERVABILITY_DIR` | `"agentic_core/L*"` | `agentic_core.L0_routing.config.path_constants` |
| `LAYER_ROOTS` | frozenset of layer names | `agentic_core.L5_safety.config.structure_blueprint.ssot` |
| `TESTS_UNIT_DIR` | `"tests/unit"` | `agentic_core.L5_safety.config.structure_blueprint.ssot` |
| `TEST_CANONICAL_LOCATION_MAP` | dict source→test path | `agentic_core.L5_safety.config.structure_blueprint.ssot` |
| `DOCS_REPORTS_PLANS` | `"docs/reports/plans"` | `agentic_core.L5_safety.config.structure_blueprint.ssot` |
| `RUNTIME_STATE_JSON` | `"runtime_state.json"` | `agentic_core.L0_routing.config.path_constants` |
| `AGENT_DISCOVERY_JSON` | `"agent_discovery_full.json"` | `agentic_core.L5_safety.config.structure_blueprint.ssot` |

---

## Execution Order

```
Phase A (WRONG_IMPORT non-test)  →  Phase B (LAYER_ROOTS)
→  Phase C (root_dir REPLACE non-test)  →  Phase D (WRONG_IMPORT test)
```

Run `pytest tests/ --ignore=tests/e2e --ignore=tests/integration_full_deps` after each phase.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

