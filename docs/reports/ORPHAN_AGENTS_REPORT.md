# Orphan Agents Report

**Generated:** 2026-02-02  
**Total Agents Discovered:** 171  
**Orphan Agents Identified:** 46  
**Orphan Percentage:** 26.9%

---

## Executive Summary

This report documents all orphan agents in the Agentic-Workflow codebase. An **orphan agent** is defined as an agent class that:
1. Has fewer than 2 references outside its own file
2. Is not imported or used in production orchestration code
3. May represent dead code, incomplete implementations, or candidates for deprecation

### Remediation Categories

| Category | Action | Priority |
|----------|--------|----------|
| **DELETE** | Remove entirely - no value | High |
| **DEPRECATE** | Mark deprecated, schedule removal | Medium |
| **INTEGRATE** | Wire into orchestration pipeline | Medium |
| **REFACTOR** | Consolidate with similar agents | Low |

---

## Orphan Agents by Layer

### L1 Cognition Layer (2 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `LLMPromptGovernorAgent` | `agentic_core/L1_cognition/thought_engine/` | 1 | **INTEGRATE** - Valuable for prompt governance |
| `UnifiedASTValidatorAgent` | `agentic_core/L1_cognition/thought_engine/` | 1 | **REFACTOR** - Merge with existing validators |

### L2 Execution Layer (1 agent)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `HistorianAgent` | `agentic_core/L2_execution/tool_registry/` | 1 | **INTEGRATE** - Useful for audit trails |

### L3 Orchestration Layer (2 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `DomainPlannerAgent` | `agentic_core/L3_orchestration/workflow_engines/` | 1 | **INTEGRATE** - Core orchestration capability |
| `DecompositionOrchestratorAgent` | `agentic_core/L3_orchestration/workflow_engines/` | 1 | **INTEGRATE** - Task decomposition needed |

### L4 State Layer (4 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `GravityStateAgent` | `agentic_core/L4_state/ValidationContext/` | 1 | **REFACTOR** - Consolidate with state management |
| `UiValidationAgent` | `agentic_core/L4_state/ValidationContext/` | 1 | **DEPRECATE** - UI validation not core |
| `UnifiedCheckpointManagerAgent` | `agentic_core/L4_state/ValidationContext/` | 1 | **INTEGRATE** - Checkpoint management needed |
| `UnifiedStateManagementAgent` | `agentic_core/L4_state/ValidationContext/` | 1 | **INTEGRATE** - Core state capability |

### L5 Safety Layer - Red Teaming (4 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `AdversarialProbeAgent` | `agentic_core/L5_safety/red_teaming/` | 1 | **INTEGRATE** - Security testing valuable |
| `BoundaryTestingAgent` | `agentic_core/L5_safety/red_teaming/` | 1 | **INTEGRATE** - Boundary validation needed |
| `ChaosEngineeringAgent` | `agentic_core/L5_safety/red_teaming/` | 1 | **DEPRECATE** - Low priority |
| `PromptInjectionAgent` | `agentic_core/L5_safety/red_teaming/` | 0 | **DELETE** - Zero references |

### L5 Safety Layer - Guardrails (3 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `CostGovernorAgent` | `agentic_core/L5_safety/guardrails/` | 1 | **INTEGRATE** - Cost governance valuable |
| `DependencyPruningAgent` | `agentic_core/L5_safety/guardrails/` | 1 | **DEPRECATE** - Overlap with other tools |
| `HallucinationHunterAgent` | `agentic_core/L5_safety/guardrails/` | 1 | **INTEGRATE** - Critical for LLM safety |

### L5 Safety Layer - Validators (9 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `GlobalComplianceAggregatorAgent` | `agentic_core/L5_safety/validators/` | 1 | **INTEGRATE** - Compliance aggregation needed |
| `GospelSyncAgent` | `agentic_core/L5_safety/validators/` | 1 | **DEPRECATE** - Unclear purpose |
| `InterfaceBoundaryAgent` | `agentic_core/L5_safety/validators/` | 1 | **REFACTOR** - Merge with boundary testing |
| `OmniContextAgent` | `agentic_core/L5_safety/validators/` | 1 | **DEPRECATE** - Overly broad scope |
| `PolicyNeuralAutoImmuneAgent` | `agentic_core/L5_safety/validators/` | 1 | **DEPRECATE** - Complex, low usage |
| `PreCommitSovereignAgent` | `agentic_core/L5_safety/validators/` | 1 | **INTEGRATE** - Pre-commit hooks valuable |
| `SemanticDebuggerAgent` | `agentic_core/L5_safety/validators/` | 1 | **INTEGRATE** - Debugging capability needed |
| `SherlockAgent` | `agentic_core/L5_safety/validators/` | 1 | **DEPRECATE** - Novelty naming, unclear scope |
| `TestGeneratorAgent` | `agentic_core/L5_safety/validators/` | 1 | **INTEGRATE** - Test generation valuable |

### L5 Safety Layer - Unified (9 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `UnifiedCodeDetectorAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedCodeEnforcerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedCodeHealerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedResourceManagerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedSafetyDetectorAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedSafetyExecutorAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedSecurityManagerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedStructureEnforcerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |
| `UnifiedStructureHealerAgent` | `agentic_core/L5_safety/unified/` | 0 | **DELETE** - Zero references |

### L6 Observability Layer (1 agent)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `SovereignObservabilityAgent` | `agentic_core/L6_observability/agents/` | 1 | **INTEGRATE** - Observability is critical |

### Apps LIC - HOP Pipeline (7 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `HOP3SenderGroundingAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP4RoutingAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP5GenerationAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP6ValidationAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP7GateDecisionAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP8QAReportAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |
| `HOP9IntegrationAgent` | `apps_lic/engines/` | 1 | **INTEGRATE** - Part of HOP pipeline |

### Legacy/Archive (1 agent)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `HOPOrchestratorAgent` | `apps_lic/legacy_archive/` | 1 | **DELETE** - Already archived |

### Stub Agents (3 agents)

| Agent | Path | Refs | Recommendation |
|-------|------|------|----------------|
| `ContentStrategyAgent` | `apps_rg/engines/` | 1 | **DEPRECATE** - Stub implementation |
| `IntelligenceLibrarianAgent` | `apps_lic/engines/` | 1 | **DEPRECATE** - Stub implementation |
| `AppContentValidatorAgent` | `apps_lic/shared/` | 1 | **REFACTOR** - Has self-tests only |

---

## Remediation Summary

| Action | Count | Files |
|--------|-------|-------|
| **DELETE** | 11 | Unified agents (9), PromptInjectionAgent, HOPOrchestratorAgent |
| **DEPRECATE** | 10 | Various low-value agents |
| **INTEGRATE** | 21 | HOP pipeline (7), L5 validators, L3/L4 core agents |
| **REFACTOR** | 4 | Consolidation candidates |

---

## File Diffs for Deletion

### Delete Unified Agents (Zero References)

```bash
# These files have ZERO references and can be safely deleted
rm agentic_core/L5_safety/unified/UnifiedCodeDetectorAgent.py
rm agentic_core/L5_safety/unified/UnifiedCodeEnforcerAgent.py
rm agentic_core/L5_safety/unified/UnifiedCodeHealerAgent.py
rm agentic_core/L5_safety/unified/UnifiedResourceManagerAgent.py
rm agentic_core/L5_safety/unified/UnifiedSafetyDetectorAgent.py
rm agentic_core/L5_safety/unified/UnifiedSafetyExecutorAgent.py
rm agentic_core/L5_safety/unified/UnifiedSecurityManagerAgent.py
rm agentic_core/L5_safety/unified/UnifiedStructureEnforcerAgent.py
rm agentic_core/L5_safety/unified/UnifiedStructureHealerAgent.py
rm agentic_core/L5_safety/red_teaming/PromptInjectionAgent.py
```

### Delete Legacy Archive

```bash
rm apps_lic/legacy_archive/HOPOrchestratorAgent.py
```

---

## Test Cases for Orphan Agent Removal

### Guardian Test Suite

Location: `tests/guardian/test_orphan_agents.py`

| Test | Purpose |
|------|---------|
| `test_agent_discovery_exists` | Verify SSOT discovery file exists |
| `test_all_agents_have_file_path` | Validate agent paths are populated |
| `test_no_new_orphan_agents` | Catch new orphans (regression prevention) |
| `test_known_orphans_still_exist` | Track orphan remediation progress |
| `test_agents_have_test_coverage` | Advisory test coverage check |
| `test_legacy_archive_agents_documented` | Ensure archive agents are tracked |
| `test_orphan_inventory_report` | Generate inventory statistics |
| `test_remediation_plan_exists` | Check for remediation documentation |
| `test_no_duplicate_agent_classes` | Prevent duplicate class names |

### Running Tests

```bash
# Run orphan agent tests only
pytest tests/guardian/test_orphan_agents.py -v

# Run full guardian suite
pytest tests/guardian/ -v -m guardian

# Generate guardian report
./run_guardian.sh
```

---

## Next Steps

1. **Phase 1 (Immediate):** Delete 11 zero-reference agents
2. **Phase 2 (Sprint 1):** Integrate HOP pipeline agents (7 agents)
3. **Phase 3 (Sprint 2):** Integrate L5 validators (9 agents)
4. **Phase 4 (Sprint 3):** Deprecate and remove low-value agents (10 agents)
5. **Phase 5 (Ongoing):** Refactor and consolidate (4 agents)

---

## Appendix: Agent Discovery JSON Schema

Each agent in `agent_discovery_full.json` contains:

```json
{
  "class_name": "AgentClassName",
  "path": "relative/path/to/AgentClassName.py",
  "layer": "L0-L6 or Apps",
  "territory": "Sovereign territory assignment",
  "category": "Validator|Healer|Executor|etc",
  "inheritance": ["BaseClass1", "BaseClass2"],
  "has_healing": true,
  "has_tests": true,
  "loc": 150
}
```

---

*Report generated by orphan agent detection system. See `tests/guardian/test_orphan_agents.py` for automated validation.*
