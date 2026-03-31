---
trigger: always_on
---
# Plan Location and Format Rule

Plans MUST always be saved to the SSOT-approved location:

```
docs/reports/plans/
```

## Hard Constraints — Location

- **NEVER** save plans to `C:\Users\amita\.windsurf\plans\` or any path outside the repository
- **NEVER** save plans to `.windsurf/plans/` inside the repository
- **ALWAYS** use `docs/reports/plans/<filename>.md` as the canonical plan path
- Plan filenames should be descriptive with a short hex suffix (e.g. `execute-ssot-streamlining-hardened.md`)

## Hard Constraints — Format (Execution Plans)

Before writing ANY execution plan, you MUST:

1. **READ the template**: `.windsurf/templates/execution-plan-template.md`
2. **Include a wave summary table** at the very top of the plan body, with columns:
   `| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |`
3. **Run token estimation** per wave using `agentic_core/planning/token_estimator.py` (`ContextWindowEstimator`)
4. **Include per-wave token budgets** with GREEN/YELLOW/RED status
5. **Validate** against `.windsurf/rules/plan_ci_enforcement.md` requirements

A plan without a wave summary table and token estimates is **invalid and must not be saved**.

## Why

- `docs/reports/plans/` is the SSOT-approved territory defined in `SOVEREIGN_TERRITORIES` and `structure_blueprint_config.py` (`DOCS_REPORTS_PLANS = "docs/reports/plans"`)
- Paths outside the repository (`C:\Users\amita\.windsurf\plans\`) are not in `PROJECT_ROOT_WHITELIST` and violate sovereignty rules
- `.windsurf/plans/` inside the repo is a Windsurf system directory, not a sovereign plans territory
- Wave table and token estimates are mandated by `plan_ci_enforcement.md` §10.1/§10.2 but Windsurf plan mode system instructions do not reference them — this rule compensates for that gap

## Reference

- SSOT constant: `agentic_core/L5_safety/config/structure_blueprint_config.py` → `DOCS_REPORTS_PLANS`
- RCA: `docs/reports/plans/RCA_windsurf_plans_violation.md`
- Plan template: `.windsurf/templates/execution-plan-template.md`
- Token estimator: `agentic_core/planning/token_estimator.py`
- Enforcement rules: `.windsurf/rules/plan_ci_enforcement.md`
- Validation skill: `.windsurf/skills/plan-validation/main.py`
