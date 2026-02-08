# RCA: Dedup Reports — SSOT Placement & ARTIFACT_ROUTING_MAP Violation

**Date**: 2026-02-08
**Severity**: Constitutional Rule #0 Violation (two-phase)
**Status**: RESOLVED

---

## Symptom (Phase 1)

Three markdown report/plan artifacts were written to `artifacts/dedup/` instead of
`docs/reports/` subfolders. Constitutional Rule #0 mandates all plans, reports, and
markdown artifacts be saved inside `docs/reports/plans/` (SSOT constant
`DOCS_REPORTS_PLANS`).

## Symptom (Phase 2)

After initial correction, all three files were placed into `docs/reports/plans/dedup/`
— a non-standard subfolder. The `ARTIFACT_ROUTING_MAP` in `structure_blueprint_config.py`
defines content-signal-based routing to specific subfolders (`assessments`, `audit`,
`coverage`, `security`, `telemetry`, `missions`, `plans`). Files were not classified
against these signals, and the `dedup/` sub-subfolder violated the flat-file pattern
used by all existing `docs/reports/` subfolders.

Additionally, two files were found in the `docs/reports/` root, which is forbidden.

---

## Root Causes

### RC-1: Hardcoded output path in `run_dedup_analysis.py`

```python
# BEFORE (hardcoded)
OUT_DIR = PROJECT_ROOT / "artifacts" / "dedup"
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"
```

The script had zero awareness of `structure_blueprint_config.py`. All constants
were derived from `__file__` instead of importing SSOT constants.

### RC-2: No ARTIFACT_ROUTING_MAP classification of output files

Files were dumped to a single output directory without content-signal analysis.
The blueprint defines explicit routing rules:

- `docs/reports/audit` — keywords: audit, drift, variance, **compliance**, **SSOT**
- `docs/reports/plans` — plans, implementation, migration, policy

The `validation_report.md` (compliance verification) and `RCA_*.md` (SSOT violation
analysis) match **audit** signals, not **plans** signals.

### RC-3: Sub-subfolder creation (`plans/dedup/`)

Existing `docs/reports/plans/` contains 40+ flat files. Creating a `dedup/` subfolder
violated the established flat-file convention and is not a valid destination in the
`ARTIFACT_ROUTING_MAP`.

### RC-4: Root-level files in `docs/reports/`

Two pre-existing files sat in `docs/reports/` root:
- `RCA_SSOT_REPORTS_PATH_VIOLATION.md` (audit content)
- `file_classification_healing_agentic_core.json` (audit content)

---

## Content-Signal Classification

Each file was classified against `ARTIFACT_ROUTING_MAP` keywords:

| File | Key Signals | Destination |
|------|------------|-------------|
| `consolidation_plan.md` | plan, migration, implementation | `docs/reports/plans/` |
| `stop_sprawl_policy.md` | policy, CI gate, rules | `docs/reports/plans/` |
| `validation_report.md` | compliance, SSOT, violations | `docs/reports/audit/` |
| `RCA_dedup_report_SSOT_violation.md` | SSOT, Constitutional Rule, compliance | `docs/reports/audit/` |
| `RCA_SSOT_REPORTS_PATH_VIOLATION.md` | SSOT, compliance | `docs/reports/audit/` |
| `file_classification_healing_agentic_core.json` | healing, audit | `docs/reports/audit/` |

Files in `plans/` use `dedup_` prefix for namespace disambiguation.

---

## Fixes Applied

### Fix 1: Blueprint import hardening in `run_dedup_analysis.py`

```python
# AFTER (blueprint-driven)
from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENT_DISCOVERY_JSON,
    DOCS_REPORTS_PLANS,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
REPORTS_DIR = PROJECT_ROOT / DOCS_REPORTS_PLANS
```

With fallback for standalone execution when package is not importable.

### Fix 2: Content-signal-based file placement

| File | Old Location | Final Location |
|------|-------------|---------------|
| `dedup_consolidation_plan.md` | `artifacts/dedup/` | `docs/reports/plans/` |
| `dedup_stop_sprawl_policy.md` | `artifacts/dedup/` | `docs/reports/plans/` |
| `dedup_validation_report.md` | `artifacts/dedup/` | `docs/reports/audit/` |
| `RCA_dedup_report_SSOT_violation.md` | `artifacts/dedup/` | `docs/reports/audit/` |

### Fix 3: Root-level file evacuation

| File | Old Location | Final Location |
|------|-------------|---------------|
| `RCA_SSOT_REPORTS_PATH_VIOLATION.md` | `docs/reports/` (root) | `docs/reports/audit/` |
| `file_classification_healing_agentic_core.json` | `docs/reports/` (root) | `docs/reports/audit/` |

### Fix 4: Removed non-standard `dedup/` sub-subfolder

Eliminated `docs/reports/plans/dedup/` — flat-file convention restored.

---

## Hardening Summary

| Concern | Before | After |
|---------|--------|-------|
| Path source | Hardcoded `Path(__file__).parents[2]` | `get_validated_project_root()` from blueprint |
| Discovery JSON | Hardcoded string `"agent_discovery_full.json"` | `AGENT_DISCOVERY_JSON` from blueprint |
| Reports dir | Hardcoded `"docs" / "reports" / "plans" / "dedup"` | `DOCS_REPORTS_PLANS` from blueprint |
| File routing | All MD → single directory | Content-signal classification via `ARTIFACT_ROUTING_MAP` |
| Sub-subfolders | `plans/dedup/` created | Flat files with `dedup_` prefix |
| Root files | 2 files in `docs/reports/` root | Evacuated to `audit/` |

---

## Verification

```bash
# No files in docs/reports/ root
ls docs/reports/*.md docs/reports/*.json
# Expected: empty

# No .md files in artifacts/dedup/
ls artifacts/dedup/*.md
# Expected: empty

# Plans in correct location
ls docs/reports/plans/dedup_*.md
# Expected: dedup_consolidation_plan.md, dedup_stop_sprawl_policy.md

# Audit reports in correct location
ls docs/reports/audit/dedup_*.md docs/reports/audit/RCA_dedup_*.md
# Expected: dedup_validation_report.md, RCA_dedup_report_SSOT_violation.md

# Pipeline re-run writes to blueprint-derived path
python artifacts/dedup/run_dedup_analysis.py
# Log should show: "Wrote dedup_consolidation_plan.md -> ...docs\reports\plans"
```
