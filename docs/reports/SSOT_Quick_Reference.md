# SSOT Report Locations - Quick Reference

## Approved Report Locations

All reports MUST be stored in one of the following locations:

### Primary Location

- `docs/reports/` - Main SSOT directory for all reports

### Sub-directories

- `docs/reports/plans/` - Planning documents
- `docs/reports/MCP/` - MCP-related reports
- `logs/compliance_reports/` - Compliance logs
- `data/freeze_reports/` - Freeze analysis reports

## Report File Patterns

Files matching these patterns are considered reports:

- `*Report*.md`
- `*Report*.json`
- `*Report*.txt`
- `RCA*.md`
- `PHASE#*.*`
- `*_SUMMARY.md`
- `*_ANALYSIS.md`
- `*_AUDIT*.md`
- `*_FINDINGS.md`
- `*_IMPLEMENTATION*.md`
- `*_COMPLETION*.md`
- `*_STATUS*.md`

## Validation Commands

### Check All Reports

```bash
python scripts/hooks/validate_report_location.py
```

### Check Staged Files Only

```bash
python scripts/hooks/validate_report_location.py --staged-only
```

### Auto-fix Misplaced Reports

```bash
python scripts/hooks/validate_report_location.py --fix
```

### Strict Mode (Blocks Commits)

```bash
python scripts/hooks/validate_report_location.py --mode strict
```

## Common Mistakes to Avoid

1. **Saving plans to user directory**: Always use `docs/reports/plans/`
2. **Creating reports in root**: Move to `docs/reports/`
3. **Ignoring file patterns**: If it matches report patterns, it belongs in SSOT
4. **Forgetting sub-directories**: Use appropriate sub-directory when available

## Pre-commit Hook

The validation runs automatically on commit. To ensure compliance:

- Run validation before committing
- Use `--fix` option to auto-move misplaced reports
- Check the output for any violations

## Need Help?

- Check: `agentic_core/utils/report_location_validator_types.py`
- Run: `python scripts/hooks/validate_report_location.py --help`
- Review: Test files in `tests/unit/docs/test_ssot_report_storage_*.py`

---

**Remember**: SSOT compliance is mandatory for all report files!
