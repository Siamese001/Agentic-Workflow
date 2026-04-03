---
trigger: always_on
---
# Plan Location and Format Rule

Plans MUST always be saved to the SSOT-approved location:

```
.windsurf/plans/
```

## Hard Constraints — Location

- **NEVER** save plans to `C:\Users\amita\.windsurf\plans\` or any path outside the repository
- **ALWAYS** use `.windsurf/plans/<filename>.md` as the canonical plan path
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

- `.windsurf/plans/` is the SSOT-approved territory for Windsurf-generated execution plans
- Paths outside the repository (`C:\Users\amita\.windsurf\plans\`) violate sovereignty rules
- Plans are IDE-system metadata, not project documentation, and belong in `.windsurf/`
- Wave table and token estimates are mandated by `plan_ci_enforcement.md` §10.1/§10.2

## Reference

- Plan template: `.windsurf/templates/execution-plan-template.md`
- Token estimator: `agentic_core/planning/token_estimator.py`
- Enforcement rules: `.windsurf/rules/plan_ci_enforcement.md`
- Validation skill: `.windsurf/skills/plan-validation/main.py`
