# Artifact Type Resolver

Given an artifact type, look up the canonical SSOT path.
Use this BEFORE choosing a write target path.

---

## Canonical Path Table

| Artifact Type | Canonical Path | SSOT Reference |
|---|---|---|
| Plans (implementation plans) | `docs/reports/plans/` | `DOCS_REPORTS_PLANS` constant |
| Evidence files (phase evidence) | `docs/reports/plans/` | `DOCS_REPORTS_PLANS` constant |
| RCA files | `docs/reports/plans/` | `DOCS_REPORTS_PLANS` constant |
| Gap analysis reports | `docs/reports/plans/` | `DOCS_REPORTS_PLANS` constant |
| Governance reports | `docs/reports/governance/` | sovereign territory |
| Telemetry reports | `docs/reports/telemetry/` | sovereign territory |
| Security reports | `docs/reports/security/` | sovereign territory |
| Audit reports | `docs/reports/audit/` | sovereign territory |
| Coverage reports | `docs/reports/coverage/` | sovereign territory |
| Mission reports | `docs/reports/missions/` | sovereign territory |
| Freeze reports | `data/freeze_reports/` | `FREEZE_REPORTS_DIR` constant |
| Architecture docs | `docs/architecture/` | sovereign territory |
| Technical docs | `docs/technical/` | sovereign territory |
| Specifications | `docs/specs/` | sovereign territory |
| Runbooks | `docs/runbooks/` | sovereign territory |
| Test files | `tests/<category>/` | `TESTS_DIR` constant |
| CI scripts | `ops_scripts/ci/` | sovereign territory |
| General ops scripts | `ops_scripts/general/` | sovereign territory |
| Source (agentic_core) | `agentic_core/L<N>_*/` | layer gravity rules |
| Source (apps) | `apps_rg/` or `apps_lic/` or `apps_shared/` | sovereign territory |
| Tools/utilities | `tools/` | `TOOLS_DIR` constant |
| Artifacts/snapshots | `artifacts/` | sovereign territory |
| Data files | `data/` | sovereign territory |
| Skill files | `.windsurf/skills/<skill-name>/` | IDE config territory |
| Workflow files | `.windsurf/workflows/` | IDE config territory |

---

## Filename Conventions

| Artifact Type | Filename Pattern |
|---|---|
| Plans | `<descriptive-name>-<6-char-hex>.md` |
| RCA files | `RCA_<topic>.md` |
| Evidence files | `<phase-name>_evidence.md` or `<phase-name>_EVIDENCE.md` |
| Gap analyses | `<topic>-gap-analysis-<hex>.md` |
| Governance reports | `<topic>_report.md` |

---

## Resolution Examples

| "I need to write..." | → Use path |
|---|---|
| A plan for MRO refactoring | `docs/reports/plans/MRO-refactoring-plan-<hex>.md` |
| Evidence for phase 3 | `docs/reports/plans/phase_03_evidence.md` |
| An RCA for import failures | `docs/reports/plans/RCA_import_failures.md` |
| A freeze report | `data/freeze_reports/06_new_freeze_report.json` |
| A new CI validator script | `ops_scripts/ci/validate_<topic>.py` |
| A new test for shim contract | `tests/unit_min_deps/test_<name>_shim_contract.py` |

---

## SSOT Constants Reference

Key constants in `agentic_core/L5_safety/config/structure_blueprint_config.py`:

```python
DOCS_REPORTS_PLANS = "docs/reports/plans"
FREEZE_REPORTS_DIR = "data/freeze_reports"
TOOLS_DIR = "tools"
SYSTEM_LEARNING_DIR = "system_learning"
```
