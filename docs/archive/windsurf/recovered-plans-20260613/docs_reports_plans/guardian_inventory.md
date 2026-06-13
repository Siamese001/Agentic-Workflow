# Guardian Inventory — Phase 0 Discovery

Generated: 2026-02-08

## Guardian Scripts

| # | Script Path | What It Verifies | Inputs | Outputs | Test Coverage | Artifacts Written |
|---|------------|-------------------|--------|---------|---------------|-------------------|
| 1 | `agentic_core/L0_maintenance/scripts/run_hygiene_guardian_util.py` | Temp artifacts, empty folders, init-only folders | `PROJECT_ROOT` filesystem | Console + dict return | None (no test in tests/guardian/) | None (console only) |
| 2 | `agentic_core/L0_maintenance/scripts/compare_autonomy_guardian_files_util.py` | Diff between two AutonomyGuardianAgent copies | Two hardcoded file paths | Console diff output | None | None |
| 3 | `agentic_core/L0_maintenance/utils/manifest_guardian_util.py` | Manifest.json SHA-256 integrity vs .manifest.lock | `manifest.json`, `.manifest.lock` | bool (verify_integrity) | None | `.manifest.lock` (seal_manifest) |

## Guardian Agents (L5_safety/reasoning/)

| # | Agent Path | What It Verifies | Inputs | Outputs |
|---|-----------|-------------------|--------|---------|
| 4 | `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` | Empty files, orphan inits, backups, temp files, debug prints, commented code, copy patterns | `project_root` filesystem scan | `HygieneViolation` list, heal dict |
| 5 | `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | Agent has `heal_repository()`, no forbidden runner scripts | `agent_discovery_full.json` + filesystem | Violation list, heal dict |
| 6 | `agentic_core/L5_safety/reasoning/MCPGuardianAgent.py` | No hardcoded credentials, timeout config, SSL enforcement | Filesystem scan (regex) | Violation list, scan dict |
| 7 | `agentic_core/L5_safety/reasoning/TestCoverageGuardianAgent.py` | Line/branch coverage, mutation score, property tests | `coverage` + `mutmut` CLI tools | Coverage metrics dict |

## Existing Schema (tests/guardian/guardian_report.py)

- `GuardianStatus`: Enum {PASS, BLOCKING}
- `ViolationCode`: 22 violation codes across MRO/Import/SSOT/Subatomic/Forensic/Constitutional
- `FixAction`: 14 fix action types
- `Violation`: dataclass (code, file, line, message, fix_action, severity, context)
- `GuardianReport`: dataclass (status, timestamp, test_suite, violations, summary, metadata)
- `GuardianReportBuilder`: Thread-safe singleton builder
- `write_guardian_report()`: Writes JSON to `logs/guardian_report.json`

## Existing Guardian Tests (tests/guardian/)

| # | Test File | What It Tests | Uses guardian_report.py? |
|---|----------|---------------|--------------------------|
| 1 | `test_mro_integrity.py` | Diamond inheritance, mixin ordering, duplicate mixins, dataclass fields | Yes |
| 2 | `test_import_safety.py` | Syntax validation, circular deps, forbidden imports, init completeness | Yes |
| 3 | `test_ssot_alignment.py` | Blueprint reality, file naming, orphan detection, path depth | No |
| 4 | `test_ssot_compliance.py` | SSOT structural compliance | No |
| 5 | `test_subatomic_compliance.py` | Subatomic limits (LOC, mixins, methods) | No |
| 6 | `test_agent_autonomy.py` | Agent has heal_repository, forbidden scripts | No |
| 7 | `test_agent_validation.py` | Agent class structure validation | No |
| 8 | `test_anti_patterns.py` | Code anti-pattern detection | No |
| 9 | `test_architecture_governance.py` | Layer governance, territory compliance | No |
| 10 | `test_code_quality_metrics.py` | Code quality metrics (complexity, etc.) | No |
| 11 | `test_comprehensive_structure.py` | Comprehensive structural checks | No |
| 12 | `test_core_components.py` | Core component integrity | No |
| 13 | `test_folder_purity_hardening.py` | Folder purity enforcement | No |
| 14 | `test_forensic_audit_unified.py` | Forensic audit checks | No |
| 15 | `test_integration.py` | Cross-guardian integration | No |
| 16 | `test_manual_verification.py` | Manual verification helpers | No |
| 17 | `test_mece_naming_compliance.py` | MECE naming rules | No |
| 18 | `test_mro_mixin_order.py` | MRO mixin ordering details | No |
| 19 | `test_obsolete_functionality_detection.py` | Obsolete code detection | No |
| 20 | `test_orphan_agent_detection.py` | Orphan agent detection | No |
| 21 | `test_pascal_edge_cases.py` | PascalCase edge cases | No |
| 22 | `test_regression.py` | Regression tests | No |

## Drift Assessment

### Issues Found
1. **No canonical contract schema** — `guardian_report.py` uses ad-hoc `GuardianReport` dataclass with fields that don't match the contract spec (missing `guardian_id`, `version`, `checks[]`, `artifacts[]`, `metrics`, `remediation_hints`).
2. **Scripts emit no structured artifacts** — `run_hygiene_guardian_util.py` returns a dict but writes no JSON.
3. **No CLI entrypoints** — None of the scripts support `--write-artifacts`, `--format`, `--strict`, `--baseline`.
4. **Hardcoded PROJECT_ROOT** — Every file re-computes `Path(__file__).resolve().parents[N]` independently.
5. **Timestamps not injectable** — `GuardianReport.__post_init__` calls `datetime.now()` directly.
6. **Absolute paths in output** — `write_guardian_report()` uses absolute path to write; report JSON uses absolute `test_suite` field.
7. **Only 2/22 test files use `GuardianReportBuilder`** — Most tests are standalone pytest with no schema-locked output.
8. **`pytest.ini` does not collect `tests/guardian/`** — `testpaths` only includes `tests/unit_min_deps` and `tests/integration/agentic_core`.
9. **No CI workflow for guardian tests** — Only a passing mention of "guardian" in `dashboard-freshness.yml`.

## SSOT Modules Available for Import
- `agentic_core.L5_safety.config.structure_blueprint` — 163 exports (paths, constants, territories)
- `agentic_core.L5_safety.config.structure_blueprint.ssot` — `ROOT_WHITELIST`, `DOCS_REPORTS_PLANS`, `get_validated_project_root`, etc.
- `agentic_core.core.classification_kernel` — `classify_file_standalone`, `is_agent_file`
- `agent_discovery_full.json` — Canonical agent registry (SSOT via `AGENT_DISCOVERY_JSON`)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

