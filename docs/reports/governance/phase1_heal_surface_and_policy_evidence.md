# Phase 1: Heal Surface and Policy Evidence

## Summary

Phase 1 implements deterministic governance for healing capabilities and LLM escalation policy.

### WAVE 1: Canonical Policy Types
- Updated `agentic_core/L5_safety/types/heal_policy_types.py` to match `execute_ssot.py` semantics
- Thresholds: 0.75 (high), 0.50 (medium) from environment variables
- Added `HealEscalationInputs` with `enable_llm`, `task_complexity`, `prior_failures`
- Added `decide_heal_escalation()` with judicious gating logic
- Maintained backward compatibility via `LegacyHealEscalationInputs` and `decide_reasoning_tier()`

### WAVE 2: Deterministic Repo-Wide Audit
- Verified AST-based scanner in `agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py`
- Added Escalation Policy Contract section to markdown report
- Generated deterministic report at `docs/reports/governance/agent_heal_audit.md`

### WAVE 3: Enforce Surface Availability
- Added `heal_repository()` stub to `SovereignBaseAgent`
- Added `heal()` and `heal_repository()` stubs to:
  - `ExecutiveStrategyAgent`
  - `OutreachMessageAgent`
  - `ResumeAssemblyAgent`
  - `PlaceholderDetectorAgent` (heal only)
  - `ReportLocationAgent` (heal_repository only)
- Created regression test `tests/governance/test_heal_surface_enforcement.py`

## Evidence

### Git Status
```
$ git diff --name-only
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
agentic_core/L5_safety/reasoning/ReportLocationAgent.py
agentic_core/L5_safety/types/heal_policy_types.py
agentic_core/base_agents/SovereignBaseAgent.py
apps_lic/config/placeholder_detector_agent_config.py
apps_lic/enforcement/ExecutiveStrategyAgent.py
apps_lic/reasoning/OutreachMessageAgent.py
apps_rg/reasoning/ResumeAssemblyAgent.py
docs/reports/governance/agent_heal_audit.md
ops_scripts/general/add_heal_stubs.py
ops_scripts/general/check_syntax.py
tests/governance/test_heal_policy_types.py
tests/governance/test_heal_surface_enforcement.py
```

### Test Results
```
$ pytest tests/governance/test_heal_policy_types.py tests/governance/test_agent_heal_audit.py tests/governance/test_heal_surface_enforcement.py -q
48 passed in 24.63s
```

### Audit Summary (JSON)
```json
{
  "summary": {
    "total_agents": 136,
    "missing_heal": 17,
    "missing_heal_repository": 28,
    "missing_both": 15
  }
}
```

Note: Remaining "missing" counts are for:
- Protocol/interface classes (IOrchestratorAgent, ITieredAgent, IAgent)
- Pydantic models with "Agent" suffix (GateDecisionAgent, etc.)
- Type definition classes (not runtime agents)

These are covered by the regression test's exemption lists and inherit from known base classes.

### Markdown Report
Generated at: `docs/reports/governance/agent_heal_audit.md`

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| No modifications to execute_ssot.py | ✓ PASS |
| New canonical policy types + tests pass | ✓ PASS (31 tests) |
| AST audit tool runs without importing agent modules | ✓ PASS |
| Audit JSON is identical across two consecutive runs | ✓ PASS |
| Markdown report generated | ✓ PASS |
| Enforcement stubs added where missing | ✓ PASS |
| Regression test added | ✓ PASS (4 tests) |

## Commit Message
```
governance(healing): policy contract + agent heal surface audit + stubs
```
