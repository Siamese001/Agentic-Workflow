# Contributing to Agentic Workflow

## Dashboard Development Guidelines

### MANDATORY: Dashboard QA Protocol

**Before committing ANY changes to dashboard templates or generator code:**

1. **Run automated QA checks**:
   ```bash
   python scripts/dashboard_qa.py
   ```
   
   This script validates:
   - HTML template syntax (balanced tags, no duplicate IDs)
   - Timer configuration (5-minute refresh, no conflicting timers)
   - Generated dashboard integrity
   - Embedded data consistency

2. **Regenerate the dashboard**:
   ```bash
   python canon_validator_agentic_v2_thin.py --report
   ```

3. **Manual browser testing** (see `docs/DASHBOARD_QA_CHECKLIST.md` for full checklist):
   - Clear browser cache (`Ctrl+Shift+R`)
   - Open `reports/autonomy_dashboard.html`
   - Verify all KPIs display (not "---%")
   - Verify countdown timer shows "Xm Ys" format and decrements smoothly
   - Check browser console for JavaScript errors
   - Test manual refresh button
   - Test at least one drill-down modal

### Dashboard File Locations

- **Template**: `agentic_core/L5_safety/validators/dashboard_template.html`
- **Generator**: `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py`
- **Output**: `reports/autonomy_dashboard.html`
- **QA Checklist**: `docs/DASHBOARD_QA_CHECKLIST.md`
- **QA Script**: `scripts/dashboard_qa.py`

### Pre-Commit Hook

A pre-commit hook automatically runs QA checks when you commit dashboard files:

```bash
# Hook location: .git/hooks/pre-commit
# Automatically runs when committing dashboard_template.html or AutonomyGuardianAgent.py
```

To bypass (NOT RECOMMENDED):
```bash
git commit --no-verify
```

### Common Issues & Fixes

#### Issue: Countdown Timer Jumps to "29s"
**Root Cause**: Multiple conflicting timer systems updating the same element.

**Fix**: Ensure only ONE `setInterval` updates `refreshStatus`. Search for duplicate timer code.

#### Issue: KPIs Show "---%"
**Root Cause**: JavaScript population logic not running or `totalRow` undefined.

**Fix**: 
1. Check browser console for errors
2. Verify `dashboardData` is embedded in HTML
3. Ensure `loadData()` executes on page load

#### Issue: Browser Shows Old Dashboard
**Root Cause**: Aggressive browser caching.

**Fix**: Hard refresh with `Ctrl+Shift+R` or open in Incognito mode.

### Testing Checklist

Before marking a dashboard PR as ready:

- [ ] `python scripts/dashboard_qa.py` passes
- [ ] Dashboard regenerated successfully
- [ ] All 3 KPIs display correctly in browser
- [ ] Countdown timer works (smooth decrement, no jumps)
- [ ] No JavaScript errors in console
- [ ] Manual refresh button works
- [ ] Drill-down modals functional
- [ ] Tested in Chrome/Edge and Firefox
- [ ] Responsive layout verified (desktop/laptop/tablet)

### Code Review Requirements

Dashboard PRs must include:

1. **QA Script Output**: Paste `python scripts/dashboard_qa.py` results in PR description
2. **Browser Screenshots**: Show top section with KPIs and countdown timer
3. **Console Screenshot**: Show no JavaScript errors
4. **Test Summary**: Confirm all manual tests passed

### Documentation

When adding new dashboard features:

1. Update `docs/DASHBOARD_QA_CHECKLIST.md` with new test cases
2. Update `scripts/dashboard_qa.py` with automated checks (if applicable)
3. Document new elements/IDs in this guide

### Performance Guidelines

- Dashboard HTML: < 1MB
- CSV data: < 100KB
- Markdown report: < 500KB
- Page load time: < 2 seconds (local file://)

### Version Control

Always commit template + generated output together:

```bash
git add agentic_core/L5_safety/validators/dashboard_template.html
git add reports/autonomy_dashboard.html
git commit -m "Dashboard: [description of change]"
```

This ensures consistency between template and output.

---

## General Contribution Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Add docstrings for public methods
- Keep functions focused (single responsibility)

### Testing

- Add unit tests for new functionality
- Ensure existing tests pass: `pytest`
- Aim for >80% test coverage

### Commit Messages

Format: `[Component]: Brief description`

Examples:
- `Dashboard: Add anomaly detection for missing infrastructure`
- `L5 Safety: Fix base class inheritance validation`
- `Docs: Update QA checklist with new test cases`

### Pull Requests

1. Create feature branch: `git checkout -b feature/description`
2. Make changes with atomic commits
3. Run all QA checks
4. Push and create PR with detailed description
5. Address review feedback
6. Squash commits before merge (if requested)

---

For questions or issues, open a GitHub issue or contact the maintainers.
