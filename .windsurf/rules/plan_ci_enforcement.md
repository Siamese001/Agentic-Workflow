# Plan CI Enforcement Rules
# Enforces CI validation for all plans in the repository

## Rule: Plan CI Required
All plans must pass Windsurf CI validation before commit.

### Requirements:
1. Plans must have proper wave structure table
2. Plans must include required sections (Wave Structure, Rules, Success Criteria)
3. Plans must have token estimates
4. Plans must include implementation details

### Enforcement:
- Pre-commit hook: `windsurf-plan-ci`
- CI validation: `tools/windsurf_ci.py`
- Manual check: `python ops_scripts/hooks/windsurf_plan_ci.py`

### Failure Modes:
- Missing wave table → Block commit
- Missing required sections → Block commit
- No token estimates → Warning
- No implementation details → Warning

## Rule: Plan Location Standards
Plans must be stored in approved locations only.

### Approved Locations:
1. `docs/reports/plans/` - Repository plans (canonical location for long-lived plans)
2. `.windsurf/plans/` - Workspace plans (acceptable for active work)

### Forbidden:
- Plans in root directory
- Plans in random subdirectories
- Plans without .md extension
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

## Rule: Token Estimator Mandate (Kimi K2.5)
All plans must use the official Windsurf ContextWindowEstimator for token validation.

### Required Tool:
```python
from agentic_core.planning.token_estimator import ContextWindowEstimator, TokenBudget

# Initialize estimator
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

# Must be GREEN or YELLOW status
assert estimate.status in ['green', 'yellow'], f"Token budget exceeded: {estimate.total_projected_tokens}"
```

### Token Estimator Location:
- **File:** `agentic_core/planning/token_estimator.py`
- **Class:** `ContextWindowEstimator`
- **Method:** `estimate_step_tokens()`
- **Configuration:** `TokenBudget` class with 262K context limits (Kimi K2.5)

## Rule: Kimi 2.5 Context Optimization
Plans must optimize for Kimi 2.5's 200K token context window.

### Requirements:
1. Single-turn execution preferred
2. Sub-waves for organization
3. Token estimates must be accurate using ContextWindowEstimator
4. Total context < 200K tokens (HARD_MAX_CONTEXT)
5. Must pass CI validation with GREEN/YELLOW status

### Enforcement:
- CI calculates total tokens using `agentic_core/planning/token_estimator.py`
- CI flags excessive token usage (>150K WARNING_THRESHOLD)
- CI suggests optimizations via compression policies
- CI validates token estimates against ContextWindowEstimator output

## Rule: Evidence Requirements
Plans must include evidence for all claims.

### Required Evidence:
- Package usage evidence for dependencies
- Import pattern examples
- Test results
- Performance metrics

### Enforcement:
- CI checks for evidence sections
- CI validates evidence quality
- CI flags missing evidence

## Rule: Rollback Strategy
All plans must include rollback strategy.

### Required Elements:
1. Git checkpoints
2. Rollback commands
3. Validation steps
4. Success criteria

### Enforcement:
- CI validates rollback section
- CI checks for checkpoint strategy
- CI ensures validation steps

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

### Enforcement:
- CI checks for ADG section when relevant
- CI validates regeneration commands
- CI ensures impact analysis
