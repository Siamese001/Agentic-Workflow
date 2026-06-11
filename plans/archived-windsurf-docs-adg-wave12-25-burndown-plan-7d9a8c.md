---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-wave12-25-burndown-plan-7d9a8c.md'
original_relative_path: 'adg-wave12-25-burndown-plan-7d9a8c.md'
source_sha256: 0a8eae72d402031d5f514097151417ae20eba8d1c68e01354ceada56cc9a14ab
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-29'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Antipattern Burndown Wave Plan (Wave 12-25)
# HIGH Severity Column 3 → Column 4 Exception Precision

## Executive Summary

**Remaining HIGH Severity Violations:** 963 (as of ADG run 03292026_0557)
**Target Violations per Wave:** 60-80 (aggressive burn-down)
**Estimated Total Waves:** 12-15 waves to completion
**Strategy:** Batch fixes by file clusters, regenerate ADG every 2-3 waves

## Token Budget Estimates by Wave

| Wave | Files | Est. Violations | Token Budget | Regenerate ADG |
|------|-------|-----------------|--------------|----------------|
| 12 | 12-15 files | 70-80 | ~45K tokens | No |
| 13 | 12-15 files | 65-75 | ~42K tokens | No |
| 14 | 10-12 files | 60-70 | ~38K tokens | **YES** |
| 15 | 12-15 files | 65-75 | ~40K tokens | No |
| 16 | 12-15 files | 60-70 | ~38K tokens | No |
| 17 | 10-12 files | 55-65 | ~35K tokens | **YES** |
| 18 | 12-15 files | 60-70 | ~38K tokens | No |
| 19 | 10-12 files | 50-60 | ~32K tokens | No |
| 20 | 10-12 files | 45-55 | ~30K tokens | **YES** |
| 21 | 10-12 files | 40-50 | ~28K tokens | No |
| 22 | 8-10 files | 35-45 | ~25K tokens | No |
| 23 | 8-10 files | 30-40 | ~22K tokens | **YES** |
| 24 | 6-8 files | 25-35 | ~18K tokens | No |
| 25 | 5-7 files | 20-30 | ~15K tokens | **FINAL** |

**Total Estimated Token Budget:** ~446K tokens across all waves
**ADG Regeneration Points:** Waves 14, 17, 20, 23, 25 (5 total)

## Violation Breakdown by Type (HIGH Severity Only)

| Evidence Type | Count | Percentage |
|---------------|-------|------------|
| except:Exception | 743 | 77.2% |
| except:bare | 106 | 11.0% |
| except:Exception:return_False | 54 | 5.6% |
| except:Exception:return_None | 24 | 2.5% |
| except:Exception:return_empty_list | 13 | 1.4% |
| except:Exception:return_empty_str | 7 | 0.7% |
| except:Exception:return_empty_dict | 6 | 0.6% |
| except:bare variants | 10 | 1.0% |

## Wave 12: Core Routing Scripts (Highest Impact)

**Target:** 80 violations across 15 files
**Token Budget:** ~45K tokens
**Priority:** Critical L0 routing infrastructure

### Files (by violation count):
1. `agentic_core/L0_routing/scripts/execute_ssot.py` (21 violations)
2. `agentic_core/L0_routing/scripts/full_agent_discovery.py` (7 violations)
3. `agentic_core/L0_routing/utils/complexity_visitor_util.py` (11 violations)
4. `agentic_core/L2_execution/enforcement/execution_guardrail_chokepoint.py` (16 violations)
5. `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py` (12 violations)
6. `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (13 violations)
7. `agentic_core/L3_orchestration/engines/orchestrator_engine.py` (15 violations)
8. `agentic_core/L3_orchestration/enforcement/mission_runner.py` (8 violations)

### Exception Mapping Strategy:
- `execute_ssot.py`: Replace with `SSOTExecutionError`, `FileNotFoundError`, `PermissionError`
- `full_agent_discovery.py`: Replace with `DiscoveryError`, `ImportError`, `AttributeError`
- `complexity_visitor_util.py`: Replace with `SyntaxError`, `ValueError`, `TypeError`
- `execution_guardrail_chokepoint.py`: Replace with `GuardrailViolationError`, `RuntimeError`
- `sovereign_filesystem_mcp.py`: Replace with `OSError`, `PermissionError`, `FileNotFoundError`
- `healing_tier_dispatcher.py`: Replace with `HealingError`, `RuntimeError`, `ValueError`
- `orchestrator_engine.py`: Replace with `OrchestrationError`, `RuntimeError`, `StateError`
- `mission_runner.py`: Replace with `MissionError`, `RuntimeError`, `ValidationError`

## Wave 13: L5 Safety Agents (High Complexity)

**Target:** 75 violations across 12 files
**Token Budget:** ~42K tokens
**Priority:** Safety plane agents require careful analysis

### Files:
1. `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` (16 violations)
2. `agentic_core/L5_safety/reasoning/hierarchy_healer.py` (16 violations)
3. `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` (13 violations)
4. `agentic_core/L5_safety/reasoning/GovernanceAgent.py` (13 violations)
5. `agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py` (13 violations)
6. `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py` (12 violations)
7. `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` (10 violations)
8. `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py` (9 violations)

### Exception Mapping Strategy:
- Safety agents: Use `SafetyPlaneError`, `GovernanceError`, `ValidationError`
- Classification agents: Use `ClassificationError`, `ValueError`, `TypeError`
- Healing agents: Use `HealingError`, `RecoveryError`, `RuntimeError`

## Wave 14: L2/L3 Execution Layer + ADG Regen

**Target:** 70 violations across 12 files
**Token Budget:** ~38K tokens
**ADG Regeneration:** YES - Verify progress after 3 waves

### Files:
1. `agentic_core/L2_execution/config/unified_workflow_config.py` (8 violations)
2. `agentic_core/L2_execution/config/hybrid_retriever_config.py` (6 violations)
3. `agentic_core/L2_execution/tools/git_ops_impl.py` (6 violations)
4. `agentic_core/L2_execution/utils/analysis_ops_util.py` (6 violations)
5. `agentic_core/L3_orchestration/reasoning/StateManagementAgent.py` (11 violations)
6. `agentic_core/L3_orchestration/reasoning/GravityStateAgent.py` (8 violations)
7. `agentic_core/L2_execution/cache/gptcache_client.py` (7 violations)
8. Plus 5 additional files with 5-6 violations each

## Wave 15: Remaining L5 Agents

**Target:** 75 violations across 15 files
**Token Budget:** ~40K tokens

### Files:
- `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` (9 violations)
- `agentic_core/L5_safety/reasoning/CodeJanitorAgent.py` (8 violations)
- `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` (7 violations)
- `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` (7 violations)
- `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` (7 violations)
- `agentic_core/L5_safety/validators/HygieneGuardianAgent.py` (8 violations)
- `agentic_core/L5_safety/enforcement/audit_healing_strategy.py` (7 violations)
- Plus 8 additional L5 safety files

## Wave 16: Tools and Scripts

**Target:** 70 violations across 15 files
**Token Budget:** ~38K tokens

### Focus Areas:
- `tools/` directory scripts with HIGH violations
- Test utilities with silent swallowers
- ADG tooling exceptions
- CI/CD script exception handling

## Wave 17: Apps Layer + ADG Regen

**Target:** 65 violations across 12 files
**Token Budget:** ~35K tokens
**ADG Regeneration:** YES

### Focus Areas:
- `apps_exec/` exception handlers
- `apps_research/` exception handlers
- `apps_rfp/` exception handlers
- `apps_lic/` exception handlers
- `apps_rg/` exception handlers

## Wave 18: System Learning Layer

**Target:** 70 violations across 15 files
**Token Budget:** ~38K tokens

### Focus Areas:
- `system_learning/adapters/` exception handlers
- `system_learning/engines/` exception handlers
- `system_learning/pipelines/` exception handlers
- Meta-learning exception classification

## Wave 19: Remaining Core Files

**Target:** 60 violations across 12 files
**Token Budget:** ~32K tokens

### Focus Areas:
- Core mixins with exception swallowers
- Utility modules with broad exceptions
- Configuration loaders with exception masking

## Wave 20: Final Core + ADG Regen

**Target:** 55 violations across 12 files
**Token Budget:** ~30K tokens
**ADG Regeneration:** YES

### Focus Areas:
- Remaining L0-L6 core files
- Edge case exception handlers
- Complex multi-exception blocks

## Wave 21-25: Mop-Up Waves

**Target:** 30-50 violations per wave
**Token Budget:** 15-28K tokens per wave
**ADG Regeneration:** Waves 23, 25

### Strategy:
- Wave 21-22: Medium severity antipatterns that were deprioritized
- Wave 23: Final sweep + ADG regen
- Wave 24-25: Edge cases + stragglers + final verification

## SQLite Query Templates for Wave Planning

### Get violations for specific wave:
```sql
SELECT file_path, line_no, evidence, severity 
FROM violations 
WHERE severity = 'HIGH' 
  AND file_path LIKE 'agentic_core/L0_routing/scripts/%'
ORDER BY file_path, line_no;
```

### Get count by file:
```sql
SELECT file_path, COUNT(*) as cnt 
FROM violations 
WHERE severity = 'HIGH' 
GROUP BY file_path 
ORDER BY cnt DESC;
```

### Get specific exception types to fix:
```sql
SELECT evidence, file_path, line_no 
FROM violations 
WHERE severity = 'HIGH' 
  AND evidence = 'except:Exception'
ORDER BY file_path, line_no;
```

## Success Metrics

- **Wave 12-14 Goal:** Reduce violations from 963 → ~750 (-213)
- **Wave 15-17 Goal:** Reduce violations from ~750 → ~550 (-200)
- **Wave 18-20 Goal:** Reduce violations from ~550 → ~350 (-200)
- **Wave 21-25 Goal:** Reduce violations from ~350 → ~100 (-250)
- **Final Target:** <50 HIGH severity violations (acceptable noise floor)

## Risk Factors

1. **Complex Exception Chains:** Some files have nested exception handlers requiring careful analysis
2. **Test Dependencies:** Some exceptions may be intentionally broad for test mocking
3. **Guardian Comment Corruption:** Long guardian lines may cause edit tool issues
4. **Token Budget Overruns:** Complex files may exceed per-wave token estimates

## Mitigation Strategies

1. Use `multi_edit` for files with multiple violations
2. Query ADG for specific exception types each operation can raise
3. Keep guardian comments concise (single line)
4. Skip files with >20 violations to dedicated waves
5. Commit after every wave regardless of pre-commit hook status

## Plan Location

**This plan saved to:** `docs/reports/plans/adg-wave12-25-burndown-plan-7d9a8c.md`

**SSOT Compliance:** Plan saved to approved docs/reports/plans/ territory per structure_blueprint_config.py
