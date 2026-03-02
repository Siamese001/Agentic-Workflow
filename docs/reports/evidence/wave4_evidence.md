# Wave 4 — V15ExecutionGateway Missing agent_id at All Call Sites

## Scope
Add `agent_id` kwarg to all 11 `V15ExecutionGateway.execute()` call sites in
production code. Add 6 new `AgentExecutionProfile` entries to `AGENT_REGISTRY`
for the internal components making these calls.

## CODE_COMMIT
a06ae39a86138d436e00e07eed214a3bd3cc78fa

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L3_orchestration/enforcement/mission_runner.py
agentic_core/L3_orchestration/enforcement/mission_runner_enforcer.py
agentic_core/L3_orchestration/engines/orchestrator_engine.py
agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py
agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py
agentic_core/agents/agent_registry.py
agentic_core/base_agents/SovereignBaseAgent.py
agentic_core/mixins/tool_reliability_mixin.py
agentic_core/runtime/config/security_level_config.py
agentic_core/runtime/engine/agent_engine.py
tests/agentic_core/test_wave4_v15_agent_id.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave4_evidence.md

## INSPECTED_FILES
agentic_core/L0_routing/enforcement/execution_gateway.py
agentic_core/agents/agent_registry.py
agentic_core/base_agents/SovereignBaseAgent.py
agentic_core/mixins/tool_reliability_mixin.py
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L3_orchestration/enforcement/mission_runner.py
agentic_core/L3_orchestration/enforcement/mission_runner_enforcer.py
agentic_core/L3_orchestration/engines/orchestrator_engine.py
agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py
agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py
agentic_core/runtime/config/security_level_config.py
agentic_core/runtime/engine/agent_engine.py
tests/agentic_core/test_wave4_v15_agent_id.py

## Registry Entries Added
agent_id=sovereign_base       -> SovereignBaseAgent.py
agent_id=tool_reliability_mixin -> tool_reliability_mixin.py
agent_id=ssot_audit           -> execute_ssot.py
agent_id=mission_runner       -> mission_runner.py, mission_runner_enforcer.py
agent_id=orchestrator_engine  -> orchestrator_engine.py, NervousSystemAgent.py, SubatomicHopAgent.py, SovereignActionPlaneAgent.py
agent_id=agent_engine         -> security_level_config.py, agent_engine.py

## pytest wave4
$ python -m pytest -q --color=no tests/agentic_core/test_wave4_v15_agent_id.py
collected 3 items

tests/agentic_core/test_wave4_v15_agent_id.py::test_no_execute_calls_missing_agent_id PASSED [ 33%]
tests/agentic_core/test_wave4_v15_agent_id.py::test_wave4_registry_entries_exist PASSED [ 66%]
tests/agentic_core/test_wave4_v15_agent_id.py::test_execute_calls_count_at_least_eleven PASSED [100%]

3 passed in 0.68s
