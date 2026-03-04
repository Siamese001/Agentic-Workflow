# Plan Location Rule

Plans MUST always be saved to the SSOT-approved location:

```
docs/reports/plans/
```

## Hard Constraints

- **NEVER** save plans to `C:\Users\amita\.windsurf\plans\` or any path outside the repository
- **NEVER** save plans to `.windsurf/plans/` inside the repository
- **ALWAYS** use `docs/reports/plans/<filename>.md` as the canonical plan path
- Plan filenames should be descriptive with a short hex suffix (e.g. `execute-ssot-streamlining-hardened.md`)

## Why

- `docs/reports/plans/` is the SSOT-approved territory defined in `SOVEREIGN_TERRITORIES` and `structure_blueprint_config.py` (`DOCS_REPORTS_PLANS = "docs/reports/plans"`)
- Paths outside the repository (`C:\Users\amita\.windsurf\plans\`) are not in `PROJECT_ROOT_WHITELIST` and violate sovereignty rules
- `.windsurf/plans/` inside the repo is a Windsurf system directory, not a sovereign plans territory

## Reference

- SSOT constant: `agentic_core/L5_safety/config/structure_blueprint_config.py` → `DOCS_REPORTS_PLANS`
- RCA: `docs/reports/plans/RCA_windsurf_plans_violation.md`
