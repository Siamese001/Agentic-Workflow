# SSOT CLI - Sovereign Single Source of Truth

Professional-grade command-line tool for SSOT architectural governance.

## Overview

The SSOT CLI provides a unified interface for scanning, validating, and enforcing architectural compliance across your codebase. Similar to `git` or `npm`, it offers a discoverable, subcommand-based interface that makes architectural governance a first-class citizen of your workflow.

## Installation

The SSOT CLI is located at `scripts/ssot.py` and requires Python 3.8+.

```bash
# Run from project root
python scripts/ssot.py <command>
```

### Optional: Create an Alias

For convenience, add an alias to your shell:

```bash
# Bash/Zsh
alias ssot="python /path/to/Agentic-Workflow/scripts/ssot.py"

# PowerShell
Set-Alias -Name ssot -Value "python C:\Git\Agentic-Workflow\scripts\ssot.py"
```

## Commands

### `ssot scan` - Agent Discovery

Scan the filesystem and list all discovered agents with their metadata.

```bash
# Full listing of all agents
python scripts/ssot.py scan

# Summary by layer
python scripts/ssot.py scan --summary

# Show only violations
python scripts/ssot.py scan --violations-only

# Limit output
python scripts/ssot.py scan --limit 10
```

**Output:**
- Agent file paths
- Class names
- Layer assignments
- Base classes
- Compliance statistics

### `ssot validate` - Comprehensive Validation

Run all SSOT validation checks and generate a health report.

```bash
# Full validation report
python scripts/ssot.py validate

# Brief summary
python scripts/ssot.py validate --summary

# Save as Markdown
python scripts/ssot.py validate --markdown

# Output as JSON
python scripts/ssot.py validate --json

# Custom output path
python scripts/ssot.py validate --output my_report.md
```

**Validation Checks:**
1. **Gravity Violations**: Agents in wrong layers (physical location)
2. **Import Violations**: Illegal upward dependencies (L1→L2, etc.)
3. **Hierarchy Violations**: Folders exceeding depth limits
4. **Drift Violations**: Unauthorized folders not in blueprint

**Exit Codes:**
- `0`: System is compliant
- `1`: Violations found

### `ssot enforce` - Automated Remediation

Apply automated fixes for detected violations.

```bash
# Dry-run (preview only, default)
python scripts/ssot.py enforce

# Execute enforcement
python scripts/ssot.py enforce --execute

# Skip confirmation prompt
python scripts/ssot.py enforce --execute --yes

# Fix specific violation types
python scripts/ssot.py enforce --drift --execute
python scripts/ssot.py enforce --hierarchy --execute
python scripts/ssot.py enforce --gravity --execute
```

**Safety Features:**
- **Dry-run by default**: Preview changes before applying
- **Confirmation prompt**: Requires explicit confirmation for `--execute`
- **Comprehensive logging**: All operations logged to `enforcement_history.log`
- **Error handling**: Graceful failure with detailed error messages

**What Gets Fixed:**
- ✅ **Drift violations**: Orphaned folders → `archives/unmapped_drift/`
- ✅ **Hierarchy violations**: Deep folders → flattened to max depth
- ✅ **Gravity violations**: Agents → correct layers
- ⚠️ **Import violations**: Require manual refactoring (not auto-fixable)

### `ssot status` - Compliance Dashboard

Show high-level compliance dashboard with actionable recommendations.

```bash
python scripts/ssot.py status
```

**Output:**
- Overall compliance score
- Violation breakdown by category
- System statistics
- Recommended actions with exact commands

## Workflow Examples

### Daily Health Check

```bash
# Quick status check
python scripts/ssot.py status

# If violations found, get details
python scripts/ssot.py validate --summary
```

### Fix All Violations

```bash
# 1. Preview changes
python scripts/ssot.py enforce

# 2. Review dry-run output
# 3. Execute if satisfied
python scripts/ssot.py enforce --execute

# 4. Verify compliance
python scripts/ssot.py status
```

### Incremental Fixes

```bash
# Fix drift violations first
python scripts/ssot.py enforce --drift --execute

# Then hierarchy violations
python scripts/ssot.py enforce --hierarchy --execute

# Verify progress
python scripts/ssot.py validate --summary
```

### Generate Report for Review

```bash
# Generate comprehensive Markdown report
python scripts/ssot.py validate --markdown

# Share with team or commit to repo
git add SSOT_Health_Report_*.md
git commit -m "docs: Add SSOT health report"
```

## Architecture

The SSOT CLI is built on three core components:

### 1. SSOTScanner (`agentic_core/utils/core_extensions/ssot_scanner.py`)
- Direct filesystem scanning (no registry needed)
- On-demand AST parsing
- Layer assignment derivation
- **Performance**: <1 second (95% faster than legacy registry)

### 2. UnifiedSSOTValidator (`agentic_core/utils/core_extensions/unified_validator.py`)
- Consolidates 5 validation tools into one
- Comprehensive health reporting
- Markdown/JSON export
- **Performance**: ~30 seconds for complete validation

### 3. SSOTRelocator (`agentic_core/L0_maintenance/mixins/ssot_relocator.py`)
- Automated violation remediation
- Replaces 4 manual relocation scripts
- Safety mechanisms (dry-run, logging, error handling)
- **Performance**: <5 seconds for typical enforcement

## Comparison: Before vs After

### Before (Fragmented Tools)

```bash
# 5 separate commands for validation
python scripts/audit_ssot.py
python audit_architectural_violations.py
python -m agentic_core.L5_safety.guardrails.HierarchyAgent
python -m agentic_core.L5_safety.validators.LocationAgent
python -m agentic_core.L0_maintenance.scripts.FilesystemSSOTReconcilerAgent

# 4 separate scripts for enforcement
python phase2_gravity_relocation.py
python phase4_final_gravity_relocation.py
python phase4_final_observability_relocation.py
python phase4_perfection_absolute.py
```

**Issues:**
- 9 different commands to remember
- Inconsistent output formats
- No unified reporting
- Manual coordination required
- 60+ seconds total execution time

### After (Unified CLI)

```bash
# Single command for everything
python scripts/ssot.py status          # Dashboard
python scripts/ssot.py validate        # Full validation
python scripts/ssot.py enforce         # Automated fixes
```

**Benefits:**
- ✅ 1 command to remember
- ✅ Consistent output format
- ✅ Unified health reporting
- ✅ Automated workflow
- ✅ 30 seconds total execution time (50% faster)

## Exit Codes

All commands follow standard Unix exit code conventions:

- `0`: Success / Compliant
- `1`: Failure / Non-compliant

Use in CI/CD pipelines:

```bash
# Fail build if violations found
python scripts/ssot.py validate --summary || exit 1

# Or just check status
python scripts/ssot.py status
```

## Logging

All enforcement operations are logged to:

```
agentic_core/L0_maintenance/logs/enforcement_history.log
```

Log format:
```
2026-01-07 12:30:45 - INFO - ARCHIVED: agentic_core/config/validators -> archives/unmapped_drift/20260107/...
2026-01-07 12:30:46 - INFO - FLATTENED: apps_lic/engines/outreach_engine/planners -> apps_lic/engines/outreach_engine
```

## Troubleshooting

### Command Not Found

```bash
# Ensure you're in the project root
cd /path/to/Agentic-Workflow

# Or use absolute path
python /path/to/Agentic-Workflow/scripts/ssot.py status
```

### Import Errors

```bash
# Ensure project root is in Python path
export PYTHONPATH="/path/to/Agentic-Workflow:$PYTHONPATH"
```

### Permission Errors (Enforcement)

```bash
# Ensure you have write permissions
ls -la agentic_core/

# Run with appropriate permissions
sudo python scripts/ssot.py enforce --execute  # Unix
# Or run as administrator on Windows
```

## Contributing

When adding new validation logic:

1. Add detection logic to `UnifiedSSOTValidator`
2. Add remediation logic to `SSOTRelocator`
3. Update CLI commands in `scripts/ssot.py`
4. Update this README

## Migration Guide

### From Legacy Tools

If you were using the old tools, here's the migration:

| Old Command | New Command |
|-------------|-------------|
| `python scripts/audit_ssot.py` | `python scripts/ssot.py scan` |
| `python scripts/validate_ssot.py` | `python scripts/ssot.py validate` |
| `python scripts/enforce_ssot.py` | `python scripts/ssot.py enforce` |
| `python audit_architectural_violations.py` | `python scripts/ssot.py validate` (included) |

### Deprecated Scripts

The following scripts have been deprecated and moved to `scripts/_deprecated_*`:

- `audit_ssot.py` → Use `ssot scan`
- `validate_ssot.py` → Use `ssot validate`
- `enforce_ssot.py` → Use `ssot enforce`

These files are kept for reference but should not be used in new workflows.

## Future Enhancements

Planned features:

- [ ] `ssot fix` - Interactive violation fixing with prompts
- [ ] `ssot watch` - Continuous monitoring mode
- [ ] `ssot report` - Generate HTML/PDF reports
- [ ] `ssot ci` - CI/CD integration helpers
- [ ] `ssot config` - Configuration management

## Support

For issues or questions:

1. Check this README
2. Run `python scripts/ssot.py <command> --help`
3. Review enforcement logs
4. Check validation reports

---

**Version**: 1.0.0  
**Last Updated**: January 7, 2026  
**Maintainer**: SSOT Governance Team
