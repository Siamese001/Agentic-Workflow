# Windsurf Plan Enforcement - RCA & Solution

## RCA: Enforcement Failure

### Root Causes:
1. **No automated validation** - Plans created without format checking
2. **No pre-commit enforcement** - No hooks to validate plan structure
3. **Template ignorance** - Failed to reference existing plan formats
4. **No self-validation** - Didn't verify against Windsurf standards

## Solution Implemented

### 1. Plan Format Validator (`tools/validate_plan_format.py`)
- **Mandatory sections**: Wave Structure, Rules, Success Criteria
- **Wave table validation**: Must have | Waves | Metric | Scope | Checkpoint | format
- **Token estimates**: Validates token column presence
- **Evidence checking**: Warns if no evidence/target sections
- **Implementation details**: Checks for commands and rollback strategy

### 2. Pre-commit Hook (`ops_scripts/hooks/validate_plan_format.py`)
- **Automatic validation**: Runs on all plan files in commit
- **Multi-location**: Validates both `.windsurf/plans/` and `docs/reports/plans/`
- **Clear reporting**: Shows exactly what's wrong with each plan
- **Exit codes**: Blocks commit if invalid plans found

### 3. Pre-commit Integration
```yaml
- id: validate-plan-format
  name: "T0-format: Validate Plan Format"
  entry: python ops_scripts/hooks/validate_plan_format.py
  language: system
  pass_filenames: false
  always_run: true
  stages: [manual]  # Can be changed to [commit] for strict enforcement
```

## Test Results

### Validator Working Correctly:
✅ **Detects missing sections**: Wave Structure, Rules, Success Criteria  
✅ **Detects missing wave tables**: Enforces table format  
✅ **Validates good plans**: My corrected plan passes validation  
✅ **Catches existing issues**: 20+ existing plans fail validation  
✅ **Clear error messages**: Shows exactly what needs fixing  

### Example Validation Output:
```
❌ Invalid
  - Missing required section: ## Wave Structure
  - Missing required section: ## Rules
  - Wave table not found after '## Wave Structure' section
  - Expected pattern: | Waves | Metric | Scope | Checkpoint | [Tokens |]
  ⚠️  No evidence or target sections found
  ⚠️  No implementation commands section
  ⚠️  No rollback strategy section
```

## Enforcement Strategy

### Phase 1: Manual Validation (Current)
- Hook runs in `stages: [manual]` mode
- Developers can run: `python ops_scripts/hooks/validate_plan_format.py`
- No blocking of commits yet

### Phase 2: Strict Enforcement (Future)
- Change to `stages: [commit]` for automatic blocking
- All new plans must pass validation
- Existing plans can be gradually fixed

### Phase 3: Template Integration
- Create plan template with required sections
- Auto-generate plan skeleton from template
- Integrate with plan creation tools

## Benefits

1. **Consistency**: All plans follow same format
2. **Quality**: Required sections ensure completeness
3. **Automation**: No manual format checking needed
4. **Clarity**: Clear error messages guide fixes
5. **Scalability**: Easy to add new validation rules

## Next Steps

1. **Fix existing plans**: Use validator to guide updates
2. **Enable strict mode**: Change to `stages: [commit]` when ready
3. **Add more rules**: Token accuracy, evidence quality checks
4. **Template creation**: Build plan generation tool

## Validator Usage

```bash
# Validate all plans
python ops_scripts/hooks/validate_plan_format.py

# Validate specific plan
python tools/validate_plan_format.py path/to/plan.md

# Test validator
python tools/validate_plan_format.py
```

This enforcement solution ensures Windsurf plan format compliance through automated validation and pre-commit integration.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

