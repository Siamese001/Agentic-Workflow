---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\burn-down-syntax-errors-wave-plan-20260406.md'
original_relative_path: 'burn-down-syntax-errors-wave-plan-20260406.md'
source_sha256: 5fa9015c5161220bb81032b3b4960aeb82bd43fb0569eb9d20b94a3c32944a37
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave Plan: Burn Down Syntax Errors in ADG Scan

**Date**: 2026-04-06  
**Priority**: HIGH  
**Status**: PENDING

---

## Executive Summary

ADG scan reports 21 syntax errors across the codebase that prevent clean parsing. These must be fixed to enable reliable ADG analysis and ensure full codebase coverage.

**Total Files**: 21  
**Total Errors**: 21  
**Estimated Effort**: 3-4 waves

---

## Error Inventory

**Total Files**: 21
**Total Errors**: 21

### Wave 1: Cache & Config Layer (COMPLETED ✓)
All 5 cache files fixed by removing duplicate imports and adding missing functions.

### Wave 2: Config & L0 (2 files)
| File | Line | Error Type | Complexity |
|------|------|------------|------------|
| `agentic_core/config/non_conforming_agent_finder_config.py` | - | SyntaxError | LOW |
| `agentic_core/L0_routing/utils/observability_seam.py` | 198 | unindent does not match | LOW |

**Wave 2 Actions**:
1. Fix syntax error in non_conforming_agent_finder_config.py
2. Fix indentation in observability_seam.py line 198

**Estimated Time**: 30 minutes

### Wave 3: L2 Execution (3 files)
| File | Line | Error Type | Complexity |
|------|------|------------|------------|
| `agentic_core/L2_execution/enforcement/filesystem_mcp.py` | 169 | unindent does not match | MEDIUM |
| `agentic_core/L2_execution/enforcement/preventative_sandbox.py` | 291 | expected indented block after except | HIGH |
| `agentic_core/L2_execution/utils/read_gateway.py` | 319 | unindent does not match | MEDIUM |

**Wave 3 Actions**:
1. Fix indentation in filesystem_mcp.py line 169
2. Fix except block in preventative_sandbox.py line 291
3. Fix indentation in read_gateway.py line 319

**Estimated Time**: 45 minutes

### Wave 4: L3/L4 Orchestration (3 files)
| File | Line | Error Type | Complexity |
|------|------|------------|------------|
| `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | 184 | unindent does not match | MEDIUM |
| `agentic_core/L3_orchestration/reasoning/engines/autonomous_execution_engine.py` | 189 | unindent does not match | MEDIUM |
| `agentic_core/L4_state/enforcement/neo4j_store.py` | 93 | unindent does not match | MEDIUM |

**Wave 4 Actions**:
1. Fix indentation in DomainPlannerAgent.py line 184
2. Fix indentation in autonomous_execution_engine.py line 189
3. Fix indentation in neo4j_store.py line 93

**Estimated Time**: 45 minutes

### Wave 5: L5 Safety (6 files)
| File | Line | Error Type | Complexity |
|------|------|------------|------------|
| `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py` | 10 | unindent does not match | MEDIUM |
| `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | 120 | unindent does not match | MEDIUM |
| `agentic_core/L5_safety/utils/guard_ddd_alignment_util.py` | 175 | unindent does not match | MEDIUM |
| `agentic_core/L5_safety/utils/register_all_validators_util.py` | 287 | unindent does not match | MEDIUM |
| `agentic_core/L5_safety/utils/verify_no_mock_data_util.py` | 176 | unindent does not match | MEDIUM |
| `agentic_core/L5_safety/validators/mission_preflight_validator.py` | 202 | expected indented block after except | HIGH |

**Wave 5 Actions**:
1. Fix indentation in ConstitutionalReviewerAgent.py line 10
2. Fix indentation in GovernanceAgent.py line 120
3. Fix indentation in guard_ddd_alignment_util.py line 175
4. Fix indentation in register_all_validators_util.py line 287
5. Fix indentation in verify_no_mock_data_util.py line 176
6. Fix except block in mission_preflight_validator.py line 202

**Estimated Time**: 60 minutes

### Wave 6: Apps & Ops (7 files)
| File | Line | Error Type | Complexity |
|------|------|------------|------------|
| `agentic_core/prompt_governance/scripts/dry_run_compiler.py` | 15 | unindent does not match | LOW |
| `agentic_core/runtime/utils/main_util.py` | 181 | unindent does not match | MEDIUM |
| `agentic_core/runtime/utils/sovereign_index_util.py` | 90 | unindent does not match | MEDIUM |
| `apps_lic/utils/manifest_manager_util.py` | 90 | unindent does not match | LOW |
| `ops_scripts/dev_tools/L0_routing_scripts/_ssot_pipeline.py` | 678 | expected except or finally | HIGH |
| `ops_scripts/dev_tools/L0_routing_scripts/emoji_fixer.py` | 179 | unexpected indent | MEDIUM |
| `ops_scripts/dev_tools/L0_routing_scripts/handler.py` | 186 | unindent does not match | MEDIUM |

**Wave 6 Actions**:
1. Fix indentation in manifest_manager_util.py line 90
2. Fix except/finally block in _ssot_pipeline.py line 678 (HIGH PRIORITY - likely structural)
3. Fix indentation in emoji_fixer.py line 179
4. Fix indentation in handler.py line 186
5. Fix indentation in dry_run_compiler.py line 15
6. Fix indentation in main_util.py line 181
7. Fix indentation in sovereign_index_util.py line 90

**Estimated Time**: 60 minutes (due to _ssot_pipeline.py complexity)

---

## Execution Strategy

### Prerequisites
1. Backup current state: `git commit -am "Pre-syntax-error-fix snapshot"`
2. Enable syntax error detection in ADG scan (already enabled)

### Wave Execution Order
1. **Wave 1** (Cache & Config) - Start here, lowest complexity
2. **Wave 2** (L0/L2) - Core execution layer
3. **Wave 3** (L3/L4) - Orchestration and state
4. **Wave 4** (L5 Safety) - Safety layer
5. **Wave 5** (Validators & Runtime) - Infrastructure
6. **Wave 6** (Apps & Ops) - Highest complexity last

### Validation After Each Wave
1. Run ADG scan: `python tools/generate/generate_full_adg.py`
2. Verify syntax error count reduced
3. Run tests for modified files
4. Commit wave with message: `fix(syntax-errors): Wave N - [description]`

### Success Criteria
- Zero syntax errors in ADG scan output
- All files parse correctly with Python AST
- No regressions in existing tests
- Full ADG generation succeeds with `--full` flag

---

## Rollback Plan

If any wave introduces regressions:
1. Revert to previous commit
2. Identify specific file causing issue
3. Fix individually before re-applying wave
4. Re-run validation

---

## Tracking

| Wave | Status | Files Fixed | Errors Remaining | Commit |
|------|--------|-------------|-----------------|--------|
| Wave 1 | COMPLETED | 5/5 | 21 | - |
| Wave 2 | IN PROGRESS | 0/2 | 19 | - |
| Wave 3 | PENDING | 0/3 | 16 | - |
| Wave 4 | PENDING | 0/3 | 13 | - |
| Wave 5 | PENDING | 0/6 | 10 | - |
| Wave 6 | PENDING | 0/7 | 4 | - |

---

## Notes

- Most errors are indentation issues (unindent does not match)
- Three structural errors (except/finally blocks) need careful review:
  - `agentic_core/L2_execution/enforcement/preventative_sandbox.py` line 291
  - `agentic_core/L5_safety/validators/mission_preflight_validator.py` line 202
  - `ops_scripts/dev_tools/L0_routing_scripts/_ssot_pipeline.py` line 678
- _ssot_pipeline.py line 678 is highest risk - likely missing try/except structure
- Wave 1 completed successfully - 5 cache files fixed by removing duplicate imports

---

**Last Updated**: 2026-04-06 04:45 UTC
**Next Action**: Begin Wave 2 - Config & L0 layer fixes (non_conforming_agent_finder_config.py, observability_seam.py)
