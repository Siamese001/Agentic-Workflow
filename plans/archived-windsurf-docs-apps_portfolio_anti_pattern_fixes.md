---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps_portfolio_anti_pattern_fixes.md'
original_relative_path: 'apps_portfolio_anti_pattern_fixes.md'
source_sha256: 04a499b22ef10a68c2568e26c2dd4fc1862064a359eff99ee8d440bfbf184589
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps Portfolio Anti-Pattern Fixes

## Problem Analysis

### Issue 1: Multiple Ruff Runs
**Root Cause:** Python script adding guardian comments with CRLF → mixed-line-ending hook fixes → ruff re-runs

**Fix:** Remove all guardian bypass comments and fix the actual code issues

### Issue 2: Silent Swallower Violations (20 instances)
**Pattern:** `except Exception as exc:` catching all exceptions

**Proper Fix:**
```python
# BEFORE (anti-pattern)
except Exception as exc:
    log.warning("Failed: %s", exc)

# AFTER (fixed)
except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
    log.warning("Failed: %s", exc)
```

**Files Fixed:**
- apps_exec/config/agent_spec_config.py
- apps_rfp/config/agent_spec_config.py
- apps_research/config/agent_spec_config.py
- apps_eval/config/agent_spec_config.py
- apps_exec/reasoning/ExecOrchestrator.py (pipeline error handler)
- apps_rfp/reasoning/RfpOrchestrator.py (pipeline error handler)
- apps_research/reasoning/ResearchOrchestrator.py (pipeline error handler)
- apps_eval/reasoning/EvalOrchestrator.py (pipeline error handler)
- apps_eval/engines/scenario_runner.py (13 test scenario handlers)

### Issue 3: Magic Configuration Violations (2 instances)
**Pattern:** Hardcoded threshold values in validators

**Files:**
- apps_eval/engines/scenario_runner.py: Hardcoded timeout values
- apps_eval/validators/eval_gate_validator.py: Hardcoded score thresholds

**Fix:** Extract to named constants at module level

## Pre-Commit Hook Optimization Recommendations

### Current Issues:
1. **T3a-c0, T3a-dedup, T3a-sprawl, T3a-shim, T3a-rollback** run on EVERY commit
2. **T3f: Module Collision Guard** overlaps with dedup guard
3. **T0-guard: Agent Deletion** only relevant when deleting agents

### Recommended Changes:

```yaml
# Move specialized guards to manual stage
- id: check-c0-sovereignty
  stages: [manual]  # Only run when explicitly invoked

- id: check-dedup-violations
  stages: [manual]  # Run in CI, not every local commit

- id: check-script-sprawl
  stages: [manual]

- id: check-shim-discipline
  stages: [manual]

- id: check-rollback-checkpoints
  stages: [manual]

# Make agent deletion guard conditional
- id: guard-agent-deletion
  files: '.*Agent\.py$'  # Only run when Agent files are modified
```

### Impact:
- **Before:** 10+ hooks run on every commit (~15-20 seconds)
- **After:** 5 core hooks run (~5-8 seconds), specialized guards run manually or in CI

## Commit Strategy

1. ✅ Remove all guardian bypass comments
2. ✅ Fix silent_swallower by specifying exception types
3. ⏳ Fix magic_configuration by extracting constants
4. ⏳ Optimize .pre-commit-config.yaml
5. ⏳ Commit with clean code (no bypasses, no anti-patterns)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

