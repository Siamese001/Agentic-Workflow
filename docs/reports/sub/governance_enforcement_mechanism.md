# Governance Enforcement Mechanism

## Overview

`docs/rules/governance.md` is no longer just documentation - it's now **actively enforced** through automated validation hooks.

## Enforcement Chain

### 1. Pre-commit Hook T3g: Governance Policy Validation
- **Location**: `.pre-commit-config.yaml` (lines 144-153)
- **Script**: `ops_scripts/hooks/validate_governance_policy.py`
- **Trigger**: Runs on every commit (all files, not just staged)
- **Status**: **Active enforcement** - blocks commits if policies not documented

### 2. What T3g Enforces

The validation hook checks that configuration changes have corresponding policy documentation:

#### .pre-commit-config.yaml
- **Manual stage hooks**: Must have "Folder Purity Validation (T3d)" section in governance.md
- **Exclude patterns**: Must have "Third-Party Code Exclusions" section in governance.md

#### pytest.ini
- **Testpaths changes**: Must have "pytest.ini testpaths Adjustment (Phase 2.8.3)" section in governance.md

#### ops_scripts/ci/check_anti_patterns.py
- **Baseline protection**: Must have "Baseline Write Protection (Phase 2.7)" section in governance.md

#### .windsurfrules
- **Policy references**: Must reference docs/rules/governance.md for policy details

### 3. Enforcement Actions

When a commit violates governance policies:

```
[GOVERNANCE] Policy validation failed:
  - .pre-commit-config.yaml: manual_stage_hooks: Hooks moved to manual stage must have policy documentation. Missing section 'Folder Purity Validation (T3d)' in docs/rules/governance.md

[GOVERNANCE] Fix required:
  1. Update docs/rules/governance.md with missing sections
  2. Ensure all configuration changes have policy documentation
  3. Reference governance policies in relevant files
```

**Result**: Commit is **blocked** until policy documentation is added.

### 4. Example Enforcement Scenarios

#### Scenario 1: Moving a Hook to Manual Stage
```yaml
# Developer changes:
- id: some-hook
  stages: [manual]  # New manual stage
```

**T3g Validation**: Fails with missing "Folder Purity Validation (T3d)" section

**Fix Required**: Add policy documentation explaining why hook is manual-only

#### Scenario 2: Changing pytest.ini testpaths
```ini
# Developer changes:
testpaths = tests/some/other/path
```

**T3g Validation**: Fails with missing "pytest.ini testpaths Adjustment" section

**Fix Required**: Add policy documentation with rationale for testpaths change

#### Scenario 3: Adding Exclude Pattern
```yaml
# Developer changes:
exclude: (some/new/pattern/.*)
```

**T3g Validation**: Fails with missing "Third-Party Code Exclusions" section

**Fix Required**: Add policy documentation explaining architectural rationale

### 5. Bypass Prevention

#### No Silent Bypasses
- SKIP variables don't work (hook checks all files, not just staged)
- --no-verify is forbidden by constitutional rules
- Hook cannot be removed without breaking the enforcement chain

#### Documentation Required
- Every configuration change must have policy rationale
- Policy sections must exist and be findable
- References must point to actual policy documents

#### Automated Detection
- Pattern matching detects configuration changes
- Section parsing validates policy existence
- Cross-file validation ensures consistency

### 6. Governance Evolution

#### Adding New Policies
1. Update `GOVERNANCE_REQUIREMENTS` in validation script
2. Add corresponding section to docs/rules/governance.md
3. Test validation with `python ops_scripts/hooks/validate_governance_policy.py`

#### Strengthening Enforcement
- Add more configuration files to validation
- Add more sophisticated pattern matching
- Add cross-reference validation between policies

#### Policy Auditing
- Validation script logs all checks in verbose mode
- Pre-commit run shows T3g status explicitly
- Evidence files capture enforcement actions

### 7. Current Enforcement Status

✅ **Active Enforcement**: T3g hook runs on every commit
✅ **Policy Coverage**: Manual hooks, testpaths, baselines, exclusions
✅ **Automated Detection**: Pattern-based validation
✅ **Bypass Prevention**: No silent bypasses possible
✅ **Documentation Required**: Every change needs policy rationale

### 8. Future Enhancements

#### Potential Expansions
- Validate .windsurfrules references to policies
- Check for policy consistency across sections
- Validate that policy dates match implementation dates
- Add policy expiration checks

#### Integration Points
- CI/CD pipeline validation
- PR comment automation
- Policy change detection
- Governance metrics dashboard

## Conclusion

The governance policy is now **enforced, not just documented**. T3g provides automated validation that ensures every configuration change has proper policy documentation. This transforms governance from advisory to mandatory, preventing the compliance struggles encountered in Phase 2.

**The days of "documentation sitting around" are over - governance is now actively enforced.**
