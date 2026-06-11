---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_anti_pattern_regression.md'
original_relative_path: 'RCA_anti_pattern_regression.md'
source_sha256: 4c2e269d88df8e22f41ff5dc0734ad03c099e924fff9012eba796572f4ca12a9
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Anti-Pattern Violation Regression (72→102)

## Executive Summary
Anti-pattern violations increased from **72 at commit 1597b1138** to **102 currently** (+30 violations). This regression occurred despite a successful burndown to 0 violations in earlier commits.

## Root Cause Analysis

### 1. The "0 violations" was a misconception
- The anti-pattern checker uses a **baseline system** that only reports NEW violations
- At commit 1597b1138, there were **72 existing violations** that were **baselined**
- The checker reported "0 new violations" which was misinterpreted as "0 total violations"
- No baseline file exists, so the system was running without proper state tracking

### 2. Scope expansion during skip elimination work
Our skip elimination work introduced violations in several ways:

#### A. New tooling files with anti-patterns
- Created `tools/_rewrite_stubs.py`, `tools/_move_infra_tests.py`, `tools/adg_ci_lane_gate.py`
- These files contain:
  - `sys.path.insert()` calls (global mutation anti-pattern)
  - Silent exception swallowers
  - Magic configuration values

#### B. Infrastructure scripts with legacy patterns
- Multiple `ops_scripts/ci/` checkers use `sys.path.insert()`
- Utility scripts contain hardcoded timeouts and thresholds
- Evidence collection scripts have silent exception handlers

#### C. Test file modifications inherited violations
- When we rewrote dead stub tests, some inherited anti-patterns from templates
- Test infrastructure files have path fragility issues

### 3. The anti-pattern detection scope widened
- The checker scans ALL Python files, including tools and ops scripts
- Previous burndowns focused on core application code
- Our work expanded into utility/tooling space where anti-patterns are more prevalent

## Violation Breakdown (Current: 102)

```
By Category:
- global_mutation (sys.path.insert): ~35
- silent_swallower: ~25
- magic_configuration: ~20
- path_fragility: ~15
- Other: ~7
```

## Timeline
1. **Commit 1597b1138**: 72 violations (baselined, reported as 0 new)
2. **Skip elimination work**: Created 30+ new files with anti-patterns
3. **Current state**: 102 total violations (no baseline = all reported)

## Immediate Actions Required

### Option 1: Proper Baseline Management (Recommended)
```bash
# Create proper baseline to track only NEW violations
ALLOW_LANDMINE_BASELINE_WRITE=1 python ops_scripts/ci/check_anti_patterns.py --write-baseline
```
- Pros: Tracks only regressions, ignores existing technical debt
- Cons: Leaves 102 violations in codebase

### Option 2: Full Remediation
- Fix all 102 violations
- High effort but achieves true zero-tolerance state

### Option 3: Scope Restriction
- Exclude tools/ and ops_scripts/ from anti-pattern checking
- Focus only on core application code
- Risks missing real issues in tooling

## Recommendation

1. **Immediate**: Create baseline to prevent further regression
2. **Short-term**: Remediate highest-impact violations (silent swallowers, global mutations)
3. **Long-term**: Gradual cleanup of remaining 102 violations
4. **Process**: Update anti-pattern checker to clearly distinguish between "new" vs "total" violations

## Lessons Learned

- "0 violations" in baseline-based systems ≠ "0 total violations"
- Tooling and utility code needs same anti-pattern discipline as application code
- Scope expansion without corresponding quality controls creates debt
- Clear reporting metrics are essential to avoid misconceptions

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

