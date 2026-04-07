---
trigger:
  - file_change
---
# Plan CI Enforcement Rules

## Rule: Plan CI Required
All plans must pass Windsurf CI validation before commit.

### Requirements:
1. Plans must have proper wave structure table
2. Plans must include required sections (Wave Structure, Rules, Success Criteria)
3. Plans must have token estimates
4. Plans must include implementation details

### Enforcement:
- Pre-commit hook: `windsurf-plan-ci` validates plan format
- CI gate: `tools/ci/ci_validate_plans.py` validates plan structure
- Manual check: `python ops_scripts/hooks/windsurf_plan_ci.py`

CI triggers on any file in `.windsurf/plans/`.

### Failure Modes:
- Missing wave table → Block commit
- Missing required sections → Block commit
- **No token estimates (T2/T3) → Block commit** (T0/T1: Warning)
- **No implementation details (T2/T3) → Block commit** (T0/T1: Warning)

## Rule: Plan Location Standards
Plans must be stored in the approved location only.

### Approved Location (SSOT):
- `.windsurf/plans/` — **ONLY** approved location for all plans

### Forbidden:
- Plans in `docs/reports/plans/` (reports/evidence only, not plans)
- Plans in root directory
- Plans in random subdirectories
- Plans without `.md` extension
- Plans outside repository (e.g., `C:\Users\amita\.windsurf\plans\`)

## Rule: Plan Naming Convention
Plan files must follow naming convention.

### Format:
- Descriptive name with hex suffix
- Example: `dependency-reclassification-plan-8a2c4d.md`
- Hex suffix: 6 characters, lowercase, a-f0-9

### Enforcement:
- CI validates naming pattern
- Pre-commit checks format
- Manual validation available

## Rule: Token Estimator Mandate
All plans must use the official Windsurf ContextWindowEstimator for token validation.

### Required Tool:
```python
from tools.utils.planning.token_estimator import ContextWindowEstimator, TokenBudget

estimator = ContextWindowEstimator()
```

### Required Constants (Kimi K2.5 - 262K Context Window):
- `HARD_MAX_CONTEXT = 262000` (absolute ceiling)
- `SAFE_OPERATING_CAP = 223000` (green zone limit)
- `WARNING_THRESHOLD = 197000` (yellow zone)
- `DEFAULT_RESERVED_OUTPUT = 12000`
- `DEFAULT_SAFETY_BUFFER = 8000`

### Mandatory CI Check:
```python
estimate = estimator.estimate_step_tokens(
    plan_step="Wave N: Description",
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    files=[...],
    diffs=[...],
    logs=[...],
    retrieved_context=[...],
    prior_steps=[...]
)

assert estimate.status in ['green', 'yellow'], f"Token budget exceeded: {estimate.total_projected_tokens}"
```

### Token Estimator Location:
- **File:** `tools/utils/planning/token_estimator.py`
- **Class:** `ContextWindowEstimator`
- **Method:** `estimate_step_tokens()`
- **Configuration:** `TokenBudget` class with 262K context limits (Kimi K2.5)

## Rule: Evidence Requirements
Plans must include evidence for all claims.

### Required Evidence:
- Package usage evidence for dependencies
- Import pattern examples
- Test results
- Performance metrics

## Rule: Rollback Strategy
All plans must include rollback strategy.

### Required Elements:
1. Git checkpoints
2. Rollback commands
3. Validation steps
4. Success criteria

## Rule: ADG Impact Assessment
Plans affecting code structure must include ADG impact assessment.

### Required for:
- Dependency changes
- Module restructuring
- Import pattern changes
- Architecture modifications

### Requirements:
- ADG regeneration steps
- Impact analysis
- Metrics validation
- Burndown gates
