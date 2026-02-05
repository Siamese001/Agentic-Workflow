# SSOT Report Storage Guide

## Overview

All reports in the Agentic-Workflow repository must be stored in the canonical SSOT location: `docs/reports/`.

This guide documents the enforcement mechanisms, approved locations, and migration procedures.

## SSOT Principle

**Single Source of Truth (SSOT)**: All report files must reside in `docs/reports/` or approved subdirectories to ensure:

- Consistent discoverability
- Centralized governance
- Simplified maintenance
- Clear ownership

## Approved Report Locations

| Location | Purpose |
|----------|---------|
| `docs/reports/` | Primary SSOT for all reports |
| `docs/reports/MCP/` | MCP-related reports |
| `logs/compliance_reports/` | Automated compliance logs |
| `data/freeze_reports/` | Frozen state reports |

## Report File Patterns

Files matching these patterns are considered reports:

- `*Report*.md` / `*Report*.json` / `*Report*.txt`
- `RCA*.md` (Root Cause Analysis)
- `PHASE*.md` / `PHASE*.json`
- `*_SUMMARY.md`
- `*_ANALYSIS.md`
- `*_AUDIT*.md`
- `*_FINDINGS.md`
- `*_IMPLEMENTATION*.md`
- `*_COMPLETION*.md`
- `*_STATUS*.md`

## Enforcement Mechanisms

### 1. Pre-commit Hook

The `validate_report_location.py` hook validates report locations before commits.

**Modes:**

- `dry-run`: Report violations without blocking (default during rollout)
- `warn`: Report violations, allow commit, encourage fix
- `strict`: Block commits with violations

**Usage:**

```bash
# Check violations (dry-run)
python scripts/hooks/validate_report_location.py --mode dry-run

# Check with logging
python scripts/hooks/validate_report_location.py --mode warn --log

# Strict enforcement
python scripts/hooks/validate_report_location.py --mode strict

# Auto-fix violations
python scripts/hooks/validate_report_location.py --fix
```

### 2. ReportLocationAgent

The `ReportLocationAgent` provides programmatic validation and healing.

**Usage:**

```python
from agentic_core.L5_safety.validators.ReportLocationAgent import ReportLocationAgent
from pathlib import Path

# Initialize agent
agent = ReportLocationAgent(project_root=Path("."))

# Validate all reports
result = agent.validate()
print(f"Compliance: {result['compliance_percentage']}%")
print(f"Violations: {result['misplaced_reports']}")

# Heal violations (dry-run)
heal_result = agent.heal()

# Heal violations (live)
agent = ReportLocationAgent(project_root=Path("."), dry_run=False)
heal_result = agent.heal()
```

### 3. Migration Script

For bulk migrations, use the migration script:

```bash
# Dry-run (preview changes)
python ops_scripts/maintenance/migrate_reports_to_ssot.py --dry-run

# Pilot migration (first 5 files)
python ops_scripts/maintenance/migrate_reports_to_ssot.py --pilot 5

# Full migration
python ops_scripts/maintenance/migrate_reports_to_ssot.py --force

# Rollback if needed
python ops_scripts/maintenance/migrate_reports_to_ssot.py --rollback
```

## Migration Workflow

### Step 1: Generate Inventory

```bash
python -c "
from agentic_core.L5_safety.validators.ReportLocationAgent import ReportLocationAgent
from pathlib import Path
agent = ReportLocationAgent(project_root=Path('.'))
agent.save_inventory()
print('Inventory saved to docs/reports/report_location_inventory.json')
"
```

### Step 2: Review Violations

Check `docs/reports/report_location_inventory.json` for:

- `misplaced_reports`: Count of violations
- `misplaced_files`: List of files to migrate
- `compliance_percentage`: Current compliance level

### Step 3: Pilot Migration

```bash
python ops_scripts/maintenance/migrate_reports_to_ssot.py --pilot 5 --dry-run
```

### Step 4: Execute Migration

```bash
python ops_scripts/maintenance/migrate_reports_to_ssot.py --force
```

### Step 5: Verify

```bash
python scripts/hooks/validate_report_location.py --mode strict
```

## Excluded Directories

These directories are excluded from report scanning:

- `.git`
- `.venv` / `venv`
- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- `node_modules`
- `.sovereign_healing_backup`
- `archives`

## Rollback Procedure

If migration causes issues:

1. **Using Migration Script:**
   ```bash
   python ops_scripts/maintenance/migrate_reports_to_ssot.py --rollback
   ```

2. **Using Git:**
   ```bash
   git checkout HEAD~1 -- <file_path>
   ```

3. **From Backup:**
   Backups are stored in `.sovereign_healing_backup/reports/`

## Integration with CI/CD

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-report-location
      name: Check Report Location
      entry: python scripts/hooks/validate_report_location.py --mode warn
      language: system
      pass_filenames: false
      always_run: true
```

## Troubleshooting

### "Destination file already exists"

A file with the same name exists in `docs/reports/`. Options:

1. Rename the source file
2. Merge content manually
3. Delete duplicate

### "Failed to create backup"

Check write permissions for `.sovereign_healing_backup/` directory.

### "Move operation failed"

For git-tracked files, ensure no uncommitted changes exist.

## Related Files

| File | Purpose |
|------|---------|
| `agentic_core/utils/report_location_validator_types.py` | Core validation logic |
| `agentic_core/L5_safety/validators/ReportLocationAgent.py` | Agent integration |
| `scripts/hooks/validate_report_location.py` | Pre-commit hook |
| `ops_scripts/maintenance/migrate_reports_to_ssot.py` | Migration script |

## Test Coverage

- Phase 1 (Validator): 38 tests
- Phase 2 (Migration): 35 tests
- Phase 3 (Enforcement): 19 tests
- Phase 4 (Agent): 33 tests

Total: **125+ unit tests** with 100% pass rate.
