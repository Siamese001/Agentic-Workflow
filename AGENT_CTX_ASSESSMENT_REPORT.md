# Agent `ctx` Parameter Assessment Report

**Date:** January 1, 2026  
**Scope:** All agents in `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`  
**Policy:** Make `ctx` mandatory for production/sovereign agents — optional only for pure-computation or testing agents

---

## Executive Summary

| Metric | Count |
|--------|------:|
| **Total Agents Analyzed** | 120+ |
| **Agents Changed (ctx now mandatory)** | 6 |
| **Agents Unchanged (already compliant or testing/utility)** | 114+ |

---

## Agents Changed (ctx Now Mandatory)

These sovereign L5 agents were updated to enforce mandatory `ctx`:

| Agent | Layer | Previous Pattern | New Pattern | File |
|-------|-------|------------------|-------------|------|
| **DocstringComplianceAgent** | L5 | `ctx=None` (optional) | `ctx` (mandatory) | `L5_safety/validators/DocstringComplianceAgent.py` |
| **InferenceTypeHintAgent** | L5 | `ctx=None` (optional) | `ctx` (mandatory) | `L5_safety/validators/InferenceTypeHintAgent.py` |
| **TypeHintEnforcementAgent** | L5 | `ctx=None` (optional) | `ctx` (mandatory) | `L5_safety/validators/TypeHintEnforcementAgent.py` |
| **GravityLeakRepairAgent** | L5 | `ctx=None` (optional) | `ctx` (mandatory) | `L5_safety/gravity/GravityLeakRepairAgent.py` |
| **TerritoryHealerAgent** | L5 | `ctx=None` (optional) | `ctx` (mandatory) | `L5_safety/guardrails/TerritoryHealerAgent.py` |
| **PascalSovereigntyEnforcerAgent** | L5 | `ctx=None` with MagicMock | `ctx` (mandatory) + `_allow_mock` flag | `L5_safety/validators/PascalSovereigntyEnforcerAgent.py` |

### Change Details

Each changed agent now includes:

```python
def __init__(self, ctx, project_root=None):
    """Initialize with mandatory ctx for sovereign operation."""
    if ctx is None:
        raise ValueError("ctx is mandatory for <AgentName> (sovereign agent)")
    self.ctx = ctx
    ...
```

For `PascalSovereigntyEnforcerAgent`, an `_allow_mock` flag was added for testing:

```python
def __init__(self, ctx: Any, dry_run: bool = False, _allow_mock: bool = False):
    """Initialize with mandatory ctx for sovereign operation.
    
    Args:
        ctx: Execution context (mandatory for production)
        dry_run: If True, audit only without making changes
        _allow_mock: Internal flag for testing - allows MagicMock ctx
    """
    if ctx is None:
        if _allow_mock:
            from unittest.mock import MagicMock
            ctx = MagicMock()
        else:
            raise ValueError("ctx is mandatory for PascalSovereigntyEnforcerAgent (sovereign agent)")
```

---

## Agents Unchanged (Already Compliant)

### Base Classes (ctx Mandatory by Design)

| Agent | Layer | Status |
|-------|-------|--------|
| ExecutionCanonBaseAgent | L2 | ✅ ctx mandatory in dataclass |
| CognitionCanonBaseAgent | L1 | ✅ ctx mandatory in base |

### Production/Sovereign Agents (ctx Already Mandatory)

| Agent | Layer | Status |
|-------|-------|--------|
| BootstrapAgent | L0 | ✅ ctx mandatory |
| FilesystemSSOTReconcilerAgent | L0 | ✅ ctx mandatory |
| DependencySentinelAgent | L1 | ✅ ctx mandatory |
| GovernanceAgent | L1 | ✅ ctx mandatory |
| MetaLearningAgent | L1 | ✅ ctx mandatory |
| ReflectionAgent | L1 | ✅ ctx mandatory |
| CodeDeduplicationAgent | L2 | ✅ ctx mandatory |
| CodeJanitorAgent | L2 | ✅ ctx mandatory |
| ContextCuratorAgent | L2 | ✅ ctx mandatory |
| DependencyDiplomatAgent | L2 | ✅ ctx mandatory |
| DynamicModelRouterAgent | L2 | ✅ ctx mandatory |
| GitAgent | L2 | ✅ ctx mandatory |
| HealerAgent | L2 | ✅ ctx mandatory |
| IntegrityGateExecutorAgent | L2 | ✅ ctx mandatory |
| MemoryArchitectAgent | L2 | ✅ ctx mandatory |
| SovereignActionPlaneAgent | L2 | ✅ ctx mandatory |
| StructuralEngineerAgent | L2 | ✅ ctx mandatory |
| SystemArchitectAgent | L2 | ✅ ctx mandatory |
| ToolsmithAgent | L2 | ✅ ctx mandatory |
| AgentRegistryValidatorAgent | L3 | ✅ ctx mandatory |
| DagEngineAgent | L3 | ✅ ctx mandatory |
| NervousSystemAgent | L3 | ✅ ctx mandatory |
| P1CoreSemanticTerritoryMapperAgent | L3 | ✅ ctx mandatory |
| P1CoreTerritoryHealerAgent | L3 | ✅ ctx mandatory |
| SemanticGatekeeperAgent | L3 | ✅ ctx mandatory |
| SubatomicHopAgent | L3 | ✅ ctx mandatory |
| TerritoryHealerAgent (L3) | L3 | ✅ ctx mandatory |
| AutonomousCheckpointManagerAgent | L4 | ✅ ctx mandatory |
| AutonomousStateGuardianAgent | L4 | ✅ ctx mandatory |
| RedisSovereignAgent | L4 | ✅ ctx mandatory |
| SchemaEvolverAgent | L4 | ✅ ctx mandatory |
| SovereignPineconeStoreAgent | L4 | ✅ ctx mandatory |
| SubAtomicRegistryAgent | L4 | ✅ ctx mandatory |
| AdversarialRedTeamerAgent | L5 | ✅ ctx mandatory |
| AutonomousThreatEvolutionAgent | L5 | ✅ ctx mandatory |
| CodeFormatterAgent | L5 | ✅ ctx mandatory |
| CodeSSOTEnforcerAgent | L5 | ✅ ctx mandatory |
| DependencyPruningAgent | L5 | ✅ ctx mandatory |
| DuplicateCodeDetectorAgent | L5 | ✅ ctx mandatory |
| FileCleanupAgent | L5 | ✅ ctx mandatory |
| FilenameUniquenessGuardianAgent | L5 | ✅ ctx mandatory |
| FilesystemAgent | L5 | ✅ ctx mandatory |
| GitHygieneAgent | L5 | ✅ ctx mandatory |
| GovernanceAgent (L5) | L5 | ✅ ctx mandatory |
| GravityEnforcerAgent | L5 | ✅ ctx mandatory |
| HallucinationHunterAgent | L5 | ✅ ctx mandatory |
| HealerAgent (L5) | L5 | ✅ ctx mandatory |
| HierarchyAgent | L5 | ✅ ctx mandatory |
| HygieneGuardianAgent | L5 | ✅ ctx mandatory |
| ImportAgent | L5 | ✅ ctx mandatory |
| L5IntegrityGateExecutorAgent | L5 | ✅ ctx mandatory |
| LocationAgent | L5 | ✅ ctx mandatory |
| NeuralAutoImmuneAgent | L5 | ✅ ctx mandatory |
| PolicyNeuralAutoImmuneAgent | L5 | ✅ ctx mandatory |
| RedTeamAgent | L5 | ✅ ctx mandatory |
| RegressionOracleAgent | L5 | ✅ ctx mandatory |
| SelfUpdatingSafetyEngineAgent | L5 | ✅ ctx mandatory |
| UnusedCleanupAgent | L5 | ✅ ctx mandatory |

### Testing Agents (ctx Optional by Design)

| Agent | Layer | Status | Reason |
|-------|-------|--------|--------|
| TestSovereigntyAgent | L5 | ✅ ctx optional | Testing specialist - standalone validation |
| TestPilotAgent | L3 | ✅ ctx optional | Testing agent |
| TestCoverageGuardianAgent | L5 | ✅ ctx optional | Testing agent |

### Utility/Observability Agents (ctx Optional by Design)

| Agent | Layer | Status | Reason |
|-------|-------|--------|--------|
| BenchmarkingAgent | observability | ✅ ctx optional | Pure computation |
| CoordinateObservabilityOperationsAgent | observability | ✅ ctx optional | Utility |
| HierarchyEnforcerAgent | observability | ✅ ctx optional | Utility |
| MetricsAgent | observability | ✅ ctx optional | Pure computation |
| PredictiveCostAuditorAgent | observability | ✅ ctx optional | Utility |
| ReportingAgent | observability | ✅ ctx optional | Utility |
| SignatureVerifierAgent | observability | ✅ ctx optional | Pure computation |
| TelemetryAgent | observability | ✅ ctx optional | Utility |
| TracingAgent | observability | ✅ ctx optional | Utility |
| TrackObservabilityCostAgent | observability | ✅ ctx optional | Utility |
| DeadCodeDetectorAgent | utils | ✅ ctx optional | Pure computation |
| DriftDetectorAgent | utils | ✅ ctx optional | Pure computation |
| GlobalComplianceAggregatorAgent | utils | ✅ ctx optional | Utility |
| NamingAgent | utils | ✅ ctx optional | Pure computation |
| NamingLawHealerAgent | utils | ✅ ctx optional | Utility |
| NamingNormalizationAgent | utils | ✅ ctx optional | Pure computation |

---

## Policy Summary

### Mandatory `ctx` (Production/Sovereign Agents)

- **Layers:** L0, L1, L2, L3, L4, L5 (core agents)
- **Pattern:**
  ```python
  def __init__(self, ctx, ...):
      if ctx is None:
          raise ValueError("ctx is mandatory for <AgentName> (sovereign agent)")
  ```

### Optional `ctx` (Testing/Utility Agents)

- **Layers:** Testing agents, observability, utils
- **Pattern:**
  ```python
  def __init__(self, ctx=None, ...):
      # ctx optional for standalone operation
  ```

### Testing with Mock (Development Only)

- **Pattern:** Use `_allow_mock=True` flag for testing
  ```python
  def __init__(self, ctx, ..., _allow_mock: bool = False):
      if ctx is None:
          if _allow_mock:
              from unittest.mock import MagicMock
              ctx = MagicMock()
          else:
              raise ValueError("ctx is mandatory")
  ```

---

## Commit Summary

```
feat: Enforce mandatory ctx for sovereign agents

AGENTS CHANGED (6):
- DocstringComplianceAgent: ctx now mandatory
- InferenceTypeHintAgent: ctx now mandatory
- TypeHintEnforcementAgent: ctx now mandatory
- GravityLeakRepairAgent: ctx now mandatory
- TerritoryHealerAgent: ctx now mandatory
- PascalSovereigntyEnforcerAgent: ctx mandatory + _allow_mock flag

AGENTS UNCHANGED (114+):
- Already compliant with mandatory ctx
- Testing agents (ctx optional by design)
- Utility agents (ctx optional by design)

POLICY:
- Production/Sovereign agents: ctx MANDATORY
- Testing agents: ctx OPTIONAL
- Utility/Computation agents: ctx OPTIONAL
```

---

*Report generated by PascalSovereigntyEnforcerAgent — Ultra Phase 13*
