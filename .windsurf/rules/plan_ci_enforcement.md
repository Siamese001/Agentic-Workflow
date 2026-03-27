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
1. `docs/reports/plans/` - Repository plans
2. `.windsurf/plans/` - Workspace plans
3. `C:\Users\amita\.windsurf\plans\` - User plans

### Forbidden:
- Plans in root directory
- Plans in random subdirectories
- Plans without .md extension

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

## Rule: Token Optimizer Mandate
All plans must use mandated token optimizer infrastructure.

### Required Imports:
```python
from tools.evidence._run_token_optimizer_plan import chars, build_legacy_phase, rough_token_estimate, run_plan
from tools.adg.wave_packer import pack_waves, summarize_wave
```

### Required Constants:
- DEFAULT_SHARED_PREFIX_TOKENS = 4000
- DEFAULT_HISTORY_TOKENS = 2000
- GENERATION_RESERVE_TOKENS = 25000
- SAFETY_BUFFER_TOKENS = 5000

### Enforcement:
- CI checks for required imports
- CI validates constant usage
- CI verifies token estimates

## Rule: SWE 1.5 Context Optimization
Plans must optimize for SWE 1.5's 200K token context window.

### Requirements:
1. Single-turn execution preferred
2. Sub-waves for organization
3. Token estimates must be accurate
4. Total context < 200K tokens

### Enforcement:
- CI calculates total tokens
- CI flags excessive token usage
- CI suggests optimizations

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
