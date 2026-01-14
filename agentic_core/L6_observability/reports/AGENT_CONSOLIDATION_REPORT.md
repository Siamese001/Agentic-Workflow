# Agent Consolidation Analysis Report
## L3 Orchestration Core (41 agents) & L2 Execution Core (69 agents)

**Generated:** January 5, 2026  
**Analyst:** Autonomous System Architect  
**Scope:** Consolidation opportunities without losing granularity or functionality

---

## Executive Summary

| Metric | Current | After Consolidation | Reduction |
|--------|---------|---------------------|-----------|
| **L3 Orchestration Agents** | 49 | 18 | -63% |
| **L2 Execution Agents** | 53 | 22 | -58% |
| **Total Agents** | 102 | 40 | **-61%** |
| **Duplicate Agents Eliminated** | 13 | 0 | -100% |
| **Code Duplication** | High | Minimal | -70% |

### Key Findings
1. **13 exact name duplicates** across both layers (same agent defined in multiple files)
2. **16 orchestrator variants** in L3 that can be unified into 3 coordinators
3. **5 DAG-related agents** that should be a single DAG engine with strategies
4. **7 monitor/detector agents** duplicated between L3 and L2
5. **5 enforcer agents** in L2 with nearly identical patterns

---

## Part 1: L3 Orchestration Core Consolidation

### Current State: 49 Agents in 8 Categories

| Category | Count | Agents | Consolidation Target |
|----------|-------|--------|----------------------|
| Core Orchestration | 16 | Various orchestrators | 1 UnifiedWorkflowEngine |
| RL/Learning | 5 | PPO, QLearning, ActorCritic, etc. | 1 RLCoordinator |
| Territory/Semantic | 5 | Mapper, Healer, Handler agents | 1 TerritoryCoordinator |
| DAG/Workflow | 5 | DAGManager, DagEngine, etc. | 1 DAGCoordinator |
| MCP/Tool | 2 | MCP Router, Connection Manager | 1 MCPCoordinator |
| Monitoring | 5 | Monitor, Detector agents | 1 HealthCoordinator |
| Governance | 3 | Permission, Registry, Governor | 1 GovernanceCoordinator |
| Fission | 3 | FissionManager variants | 1 FissionCoordinator |
| Other/Specialized | 5 | Keep as specialized | 5 (no change) |

### Detailed Consolidation Plan

#### 1.1 Core Orchestration → UnifiedWorkflowEngine

**Current (16 agents):**
- `ActorCriticOrchestratorAgent`
- `CachedOrchestratorAgent`
- `HardenedWorkflowOrchestratorAgent`
- `NervousSystemAgent`
- `NervousSystemPhaseOrchestratorAgent`
- `L3OrchestrationBaseAgent`
- `OrchestrationHandshake`
- `PPOOrchestratorAgent`
- `QLearningOrchestratorAgent`
- `RLOrchestratorAgent`
- `ReinforceCriticOrchestratorAgent`
- `ResumeOrchestratorAgent`
- `SelfRecoveringOrchestratorAgent`
- `SovereignRagOrchestratorAgent`
- `SubatomicOrchestratorAgent`
- `SubatomicHopAgent`

**Target (1 engine + 3 coordinators):**

```python
# agentic_core/L3_orchestration/unified_workflow_engine.py
class UnifiedWorkflowEngine(HealerMixin, MCPHardenedMixin):
    """
    Single entry point for all workflow orchestration.
    Replaces 16 overlapping orchestrators with pluggable strategies.
    """
    
    def __init__(self):
        self.strategies = {
            'rl': RLCoordinator(),          # Replaces 5 RL orchestrators
            'recovery': RecoveryCoordinator(), # Replaces SelfRecovering, Resume
            'caching': CachingCoordinator(),   # Replaces CachedOrchestrator
        }
        self.nervous_system = NervousSystemCore()  # Core logic from NervousSystem
    
    async def execute_workflow(self, workflow: WorkflowSpec) -> WorkflowResult:
        """Unified workflow execution with strategy selection."""
        strategy = self._select_strategy(workflow)
        return await strategy.execute(workflow, self.nervous_system)
```

**File Diff - Create `unified_workflow_engine.py`:**
```diff
+ # agentic_core/L3_orchestration/unified_workflow_engine.py
+ from __future__ import annotations
+ from typing import Dict, Any, Optional, List
+ from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
+ from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
+ 
+ class UnifiedWorkflowEngine(HealerMixin, MCPHardenedMixin):
+     """
+     Unified Workflow Engine - Single entry point for all L3 orchestration.
+     
+     Consolidates:
+     - 5 RL orchestrators → RLCoordinator with pluggable strategies
+     - 3 recovery orchestrators → RecoveryCoordinator
+     - NervousSystem + SubatomicOrchestrator → NervousSystemCore
+     - Caching, Hardening, RAG → Optional coordinators
+     
+     Architecture:
+     ```
+     UnifiedWorkflowEngine
+     ├── NervousSystemCore (brain)
+     ├── CoordinatorRegistry
+     │   ├── RLCoordinator (PPO, QLearning, ActorCritic, Reinforce)
+     │   ├── RecoveryCoordinator (SelfRecovering, Resume)
+     │   ├── CachingCoordinator
+     │   ├── HardeningCoordinator
+     │   └── RAGCoordinator
+     └── ExecutionStrategies
+         ├── DAGStrategy
+         ├── StateMachineStrategy
+         └── EventDrivenStrategy
+     ```
+     """
+     
+     def __init__(self, project_root: Path = None):
+         super().__init__()
+         self.project_root = project_root or Path.cwd()
+         self._coordinators: Dict[str, WorkflowCoordinator] = {}
+         self._strategies: Dict[str, ExecutionStrategy] = {}
+         self._initialize_coordinators()
+     
+     def _initialize_coordinators(self):
+         """Register all coordinators."""
+         from .coordinators import (
+             RLCoordinator,
+             RecoveryCoordinator, 
+             CachingCoordinator,
+             HardeningCoordinator,
+             RAGCoordinator
+         )
+         self._coordinators = {
+             'rl': RLCoordinator(),
+             'recovery': RecoveryCoordinator(),
+             'caching': CachingCoordinator(),
+             'hardening': HardeningCoordinator(),
+             'rag': RAGCoordinator(),
+         }
+     
+     async def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
+         """Execute a workflow through the unified engine."""
+         workflow_type = workflow.get('type', 'default')
+         coordinator = self._select_coordinator(workflow_type)
+         return await coordinator.coordinate(workflow)
+     
+     def _select_coordinator(self, workflow_type: str) -> 'WorkflowCoordinator':
+         """Select appropriate coordinator for workflow type."""
+         if workflow_type in ('ppo', 'qlearning', 'actor_critic', 'reinforce'):
+             return self._coordinators['rl']
+         elif workflow_type in ('resume', 'recover', 'self_heal'):
+             return self._coordinators['recovery']
+         elif workflow_type == 'cached':
+             return self._coordinators['caching']
+         return self._coordinators.get(workflow_type, self._coordinators['recovery'])
+     
+     def heal_repository(self) -> dict:
+         """Invoke healing chain."""
+         return super().heal_repository()
```

#### 1.2 RL Orchestrators → RLCoordinator

**Current (5 agents):**
- `RLOrchestratorAgent` (base)
- `PPOOrchestratorAgent` (PPO strategy)
- `QLearningOrchestratorAgent` (Q-learning strategy)
- `ActorCriticOrchestratorAgent` (A2C strategy)
- `ReinforceCriticOrchestratorAgent` (REINFORCE strategy)

**Target (1 coordinator with strategies):**

```diff
+ # agentic_core/L3_orchestration/coordinators/rl_coordinator.py
+ class RLCoordinator(WorkflowCoordinator):
+     """
+     Unified RL Coordinator - Replaces 5 separate RL orchestrators.
+     
+     Strategies:
+     - PPO: Proximal Policy Optimization
+     - QLearning: Q-Learning with experience replay
+     - ActorCritic: A2C with advantage estimation
+     - REINFORCE: Policy gradient with baseline
+     """
+     
+     def __init__(self):
+         self.strategies = {
+             'ppo': PPOStrategy(),
+             'qlearning': QLearningStrategy(),
+             'actor_critic': ActorCriticStrategy(),
+             'reinforce': REINFORCEStrategy(),
+         }
+         self.default_strategy = 'ppo'
+     
+     async def coordinate(self, workflow: Dict) -> Dict:
+         strategy_name = workflow.get('rl_strategy', self.default_strategy)
+         strategy = self.strategies.get(strategy_name, self.strategies['ppo'])
+         return await strategy.execute(workflow)
```

**Files to deprecate:**
- `PPOOrchestratorAgent.py` → Logic moves to `RLCoordinator.PPOStrategy`
- `QLearningOrchestratorAgent.py` → Logic moves to `RLCoordinator.QLearningStrategy`
- `ActorCriticOrchestratorAgent.py` → Logic moves to `RLCoordinator.ActorCriticStrategy`
- `ReinforceCriticOrchestratorAgent.py` → Logic moves to `RLCoordinator.REINFORCEStrategy`
- `RLOrchestratorAgent.py` → Base logic moves to `RLCoordinator`

#### 1.3 DAG Agents → DAGCoordinator

**Current (5 agents with duplicates):**
- `DAGManagerAgent` (workflow_engines/DAGManagerAgent.py)
- `DAGMutatorAgent` (same file)
- `DagEngineAgent` (workflow_engines/DagEngineAgent.py)
- `DagExecutorAgent` (workflow_engines/healer_dag.py)
- `DagManagerAgent` (workflow_engines/subatomic_orchestrator_impl.py) - **DUPLICATE**

**Target (1 coordinator):**

```diff
+ # agentic_core/L3_orchestration/coordinators/dag_coordinator.py
+ class DAGCoordinator(WorkflowCoordinator):
+     """
+     Unified DAG Coordinator - Replaces 5 DAG-related agents.
+     
+     Capabilities:
+     - DAG construction and validation
+     - DAG mutation and optimization
+     - DAG execution with parallelism
+     - DAG healing and recovery
+     """
+     
+     def __init__(self):
+         self.dag_builder = DAGBuilder()      # From DAGManagerAgent
+         self.dag_mutator = DAGMutator()      # From DAGMutatorAgent  
+         self.dag_executor = DAGExecutor()    # From DagEngineAgent
+         self.dag_healer = DAGHealer()        # From DagExecutorAgent
+     
+     async def build_dag(self, spec: Dict) -> DAG:
+         """Build DAG from specification."""
+         return self.dag_builder.build(spec)
+     
+     async def execute_dag(self, dag: DAG) -> Dict:
+         """Execute DAG with healing support."""
+         try:
+             return await self.dag_executor.execute(dag)
+         except Exception as e:
+             return await self.dag_healer.heal_and_retry(dag, e)
```

#### 1.4 Territory/Semantic → TerritoryCoordinator

**Current (5 agents with duplicates):**
- `SemanticTerritoryMapperAgent` (2 copies)
- `TerritoryHealerAgent` (2 copies)
- `TerritoryChangeHandlerAgent`

**Target (1 coordinator):**

```diff
+ # agentic_core/L3_orchestration/coordinators/territory_coordinator.py
+ class TerritoryCoordinator(WorkflowCoordinator):
+     """
+     Unified Territory Coordinator - Semantic territory management.
+     
+     Consolidates:
+     - SemanticTerritoryMapperAgent (mapping)
+     - TerritoryHealerAgent (healing)
+     - TerritoryChangeHandlerAgent (change detection)
+     """
+     
+     def __init__(self):
+         self.mapper = SemanticMapper()
+         self.healer = TerritoryHealer()
+         self.change_handler = ChangeHandler()
+     
+     async def map_territory(self, path: Path) -> TerritoryMap:
+         return await self.mapper.map(path)
+     
+     async def heal_territory(self, territory: str) -> Dict:
+         return await self.healer.heal(territory)
+     
+     async def handle_change(self, change: TerritoryChange) -> Dict:
+         return await self.change_handler.handle(change)
```

**Files to delete (duplicates):**
- `P1CoreSemanticTerritoryMapperAgent.py` → Merge into `SemanticTerritoryMapperAgent.py`
- `P1CoreTerritoryHealerAgent.py` → Merge into `TerritoryHealerAgent.py`

---

## Part 2: L2 Execution Core Consolidation

### Current State: 53 Agents in 11 Categories

| Category | Count | Consolidation Target |
|----------|-------|----------------------|
| Enforcement | 8 | 1 EnforcementCoordinator |
| MCP/Sovereign | 7 | 1 MCPClientCoordinator |
| Architecture/Planning | 6 | 1 ArchitectureCoordinator |
| Safety/Security | 6 | 1 SafetyCoordinator |
| Memory/Context | 4 | 1 MemoryCoordinator |
| Inspection/Audit | 3 | 1 AuditCoordinator |
| Resource Management | 3 | 1 ResourceCoordinator |
| Tooling | 3 | 1 ToolingCoordinator |
| Code Quality | 2 | 1 CodeQualityCoordinator |
| Git/VCS | 2 | 1 GitCoordinator |
| Other | 9 | Keep specialized |

### Detailed Consolidation Plan

#### 2.1 Enforcer Agents → EnforcementCoordinator

**Current (8 agents):**
- `DocEnforcerAgent` (LOC=77, CC=2)
- `NamingEnforcerAgent` (LOC=77, CC=2)
- `PatternEnforcerAgent` (LOC=292, CC=62)
- `TypeEnforcerAgent` (LOC=77, CC=2)
- `SecurityEnforcerAgent` (LOC=164, CC=2)
- `DependencySentinelAgent` (LOC=77, CC=2)
- `RedSentinelAgent` (LOC=164, CC=2)
- `ConcurrencyGuardianAgent` (LOC=116, CC=31)

**Target (1 coordinator with pluggable rules):**

```diff
+ # agentic_core/L2_execution/coordinators/enforcement_coordinator.py
+ class EnforcementCoordinator(HealerMixin, MCPHardenedMixin):
+     """
+     Unified Enforcement Coordinator - Replaces 8 enforcer/sentinel agents.
+     
+     Rule Categories:
+     - Documentation (DocEnforcerAgent)
+     - Naming conventions (NamingEnforcerAgent)
+     - Code patterns (PatternEnforcerAgent)
+     - Type safety (TypeEnforcerAgent)
+     - Security (SecurityEnforcerAgent)
+     - Dependencies (DependencySentinelAgent)
+     - Red flags (RedSentinelAgent)
+     - Concurrency (ConcurrencyGuardianAgent)
+     """
+     
+     def __init__(self):
+         super().__init__()
+         self.rules = {
+             'documentation': DocumentationRules(),
+             'naming': NamingRules(),
+             'patterns': PatternRules(),
+             'types': TypeRules(),
+             'security': SecurityRules(),
+             'dependencies': DependencyRules(),
+             'red_flags': RedFlagRules(),
+             'concurrency': ConcurrencyRules(),
+         }
+     
+     def enforce(self, file_path: Path, categories: List[str] = None) -> EnforcementResult:
+         """Run enforcement rules on a file."""
+         categories = categories or list(self.rules.keys())
+         violations = []
+         for cat in categories:
+             if cat in self.rules:
+                 violations.extend(self.rules[cat].check(file_path))
+         return EnforcementResult(violations=violations)
```

#### 2.2 MCP/Sovereign Clients → MCPClientCoordinator

**Current (7 agents with 2 duplicates):**
- `SovereignActionPlaneAgent`
- `SovereignDeepWikiClient`
- `SovereignFetchClient`
- `SovereignFetchMcpClient`
- `SovereignPlaywrightMcpClient`
- `SovereignRedisOrchestratorAgent` (2 copies) - **DUPLICATE**

**Target (1 coordinator):**

```diff
+ # agentic_core/L2_execution/coordinators/mcp_client_coordinator.py
+ class MCPClientCoordinator(HealerMixin, MCPHardenedMixin):
+     """
+     Unified MCP Client Coordinator - All MCP client access through one interface.
+     
+     Clients:
+     - DeepWiki (documentation)
+     - Fetch (HTTP requests)
+     - Playwright (browser automation)
+     - Redis (caching)
+     - Filesystem (file operations)
+     """
+     
+     def __init__(self):
+         self.clients = {}
+         self._lazy_init = True
+     
+     def get_client(self, client_type: str) -> MCPClient:
+         if client_type not in self.clients:
+             self.clients[client_type] = self._create_client(client_type)
+         return self.clients[client_type]
+     
+     def _create_client(self, client_type: str) -> MCPClient:
+         factories = {
+             'deepwiki': lambda: SovereignDeepWikiClient(),
+             'fetch': lambda: SovereignFetchMcpClient(),
+             'playwright': lambda: SovereignPlaywrightMcpClient(),
+             'redis': lambda: SovereignRedisMcpClient(),
+         }
+         return factories.get(client_type, lambda: None)()
```

**Files to delete (duplicates):**
- `P2_tools_autonomous_redis_orchestrator.py` → Keep `SovereignRedisOrchestratorAgent.py`
- `SovereignFetchClient.py` → Merge into `SovereignFetchMcpClient.py`

#### 2.3 Architect/Engineer → ArchitectureCoordinator

**Current (6 agents with duplicates):**
- `ArchitectureGovernorAgent` (also in L3) - **DUPLICATE**
- `StructuralEngineerAgent` (2 copies) - **DUPLICATE**
- `SystemArchitectAgent` (2 copies) - **DUPLICATE**
- `StrategicPlannerAgent`

**Target (1 coordinator):**

```diff
+ # agentic_core/L2_execution/coordinators/architecture_coordinator.py
+ class ArchitectureCoordinator(HealerMixin, MCPHardenedMixin):
+     """
+     Unified Architecture Coordinator - System design and engineering.
+     
+     Capabilities:
+     - Architecture governance
+     - Structural engineering (code structure)
+     - System architecture (high-level design)
+     - Strategic planning
+     """
+     
+     def __init__(self):
+         self.governor = ArchitectureGovernor()
+         self.engineer = StructuralEngineer()
+         self.architect = SystemArchitect()
+         self.planner = StrategicPlanner()
```

**Files to delete (duplicates):**
- `governance.py` (has duplicate ArchitectureGovernorAgent) → Keep `ArchitectureGovernorAgent.py`
- `engineering.py` (has duplicate StructuralEngineerAgent) → Keep `StructuralEngineerAgent.py`
- `system_architect.py` (has duplicate SystemArchitectAgent) → Keep `SystemArchitectAgent.py`

#### 2.4 Safety/Security → SafetyCoordinator

**Current (6 agents):**
- `IntegrityGateExecutorAgent` (4 copies!) - **MAJOR DUPLICATE**
- `SafetyInspectorAgent`
- `SecurityEnforcerAgent`

**Target (1 coordinator):**

```diff
+ # agentic_core/L2_execution/coordinators/safety_coordinator.py
+ class SafetyCoordinator(HealerMixin, MCPHardenedMixin):
+     """
+     Unified Safety Coordinator - All safety and security checks.
+     
+     Components:
+     - IntegrityGate (validation gates)
+     - SafetyInspector (safety audits)
+     - SecurityEnforcer (security rules)
+     """
+     
+     def __init__(self):
+         self.integrity_gate = IntegrityGate()
+         self.safety_inspector = SafetyInspector()
+         self.security_enforcer = SecurityEnforcer()
```

**Files to delete (duplicates - 4 copies!):**
- `healer_executive.py` (IntegrityGateExecutorAgent) → Delete
- `peer_intelligence_auditor_impl.py` (IntegrityGateExecutorAgent) → Delete
- `section_scope_integrator_engine.py` (IntegrityGateExecutorAgent) → Delete
- Keep only `IntegrityGateExecutorAgent.py`

---

## Part 3: Cross-Layer Duplicates to Eliminate

### Agents Duplicated Between L3 and L2

| Agent | L3 Location | L2 Location | Action |
|-------|-------------|-------------|--------|
| `ArchitectureGovernorAgent` | workflow_engines/ | governance.py | Keep L3, delete L2 |
| `DeadlockDetectorAgent` | deadlock_detector.py | concurrency.py | Keep L3, delete L2 |
| `MemoryLeakDetectorAgent` | memory_leak_detector.py | concurrency.py | Keep L3, delete L2 |
| `TestPilotAgent` | TestPilotAgent.py | repair.py | Keep L3, delete L2 |

### Recommended Layer Assignment

| Agent Type | Correct Layer | Reason |
|------------|---------------|--------|
| Orchestrators | L3 | Coordinate workflows |
| Detectors/Monitors | L3 | System-wide monitoring |
| Executors | L2 | Tool execution |
| Enforcers | L2 | Rule enforcement on code |
| MCP Clients | L2 | External tool access |

---

## Part 4: Implementation Roadmap

### Phase 1: Delete Exact Duplicates (Week 1)
**Estimated effort:** 2-3 days  
**Risk:** Low  
**Impact:** -13 files, cleaner codebase

```bash
# Files to delete (exact duplicates)
rm agentic_core/L3_orchestration/fission_logic/FissionManager/__init__.py
rm agentic_core/L3_orchestration/workflow_engines/P1CoreSemanticTerritoryMapperAgent.py
rm agentic_core/L3_orchestration/workflow_engines/P1CoreTerritoryHealerAgent.py
rm agentic_core/L2_execution/ToolRegistry/governance.py
rm agentic_core/L2_execution/ToolRegistry/engineering.py
rm agentic_core/L2_execution/ToolRegistry/system_architect.py
rm agentic_core/L2_execution/ToolRegistry/healer_executive.py
rm agentic_core/L2_execution/ToolRegistry/peer_intelligence_auditor_impl.py
rm agentic_core/L2_execution/ToolRegistry/section_scope_integrator_engine.py
rm agentic_core/L2_execution/ToolRegistry/P2_tools_autonomous_redis_orchestrator.py
rm agentic_core/L2_execution/ToolRegistry/concurrency.py  # Has duplicates from L3
rm agentic_core/L2_execution/ToolRegistry/repair.py  # Has TestPilotAgent duplicate
rm agentic_core/L2_execution/ToolRegistry/infrastructure.py  # Has GitAgent duplicate
```

### Phase 2: Create Coordinator Framework (Week 2)
**Estimated effort:** 3-4 days  
**Risk:** Medium  
**Impact:** Foundation for consolidation

```bash
# New directory structure
mkdir -p agentic_core/L3_orchestration/coordinators
mkdir -p agentic_core/L2_execution/coordinators

# Create base coordinator class
touch agentic_core/L3_orchestration/coordinators/__init__.py
touch agentic_core/L3_orchestration/coordinators/base_coordinator.py
touch agentic_core/L2_execution/coordinators/__init__.py
touch agentic_core/L2_execution/coordinators/base_coordinator.py
```

### Phase 3: Consolidate L3 Orchestrators (Week 3-4)
**Estimated effort:** 5-7 days  
**Risk:** Medium-High  
**Impact:** 49 → 18 agents

1. Create `UnifiedWorkflowEngine`
2. Create `RLCoordinator` (replace 5 RL agents)
3. Create `DAGCoordinator` (replace 5 DAG agents)
4. Create `TerritoryCoordinator` (replace 5 territory agents)
5. Create `HealthCoordinator` (replace monitoring agents)
6. Create `GovernanceCoordinator` (replace governance agents)
7. Update all callers to use new coordinators
8. Deprecate old orchestrators

### Phase 4: Consolidate L2 Executors (Week 5-6)
**Estimated effort:** 5-7 days  
**Risk:** Medium  
**Impact:** 53 → 22 agents

1. Create `EnforcementCoordinator` (replace 8 enforcers)
2. Create `MCPClientCoordinator` (replace 7 MCP clients)
3. Create `ArchitectureCoordinator` (replace 6 architects)
4. Create `SafetyCoordinator` (replace 6 safety agents)
5. Create `MemoryCoordinator` (replace 4 memory agents)
6. Update all callers
7. Deprecate old executors

### Phase 5: Testing & Validation (Week 7)
**Estimated effort:** 3-4 days  
**Risk:** Low  
**Impact:** Ensure no functionality loss

1. Run full test suite
2. Validate all workflows still function
3. Performance benchmarking
4. Documentation updates

---

## Part 5: File Diffs Summary

### Files to Delete (13 exact duplicates)

| File | Reason |
|------|--------|
| `L3/fission_logic/FissionManager/__init__.py` | Duplicate of FissionManagerAgent.py |
| `L3/workflow_engines/P1CoreSemanticTerritoryMapperAgent.py` | Duplicate of SemanticTerritoryMapperAgent.py |
| `L3/workflow_engines/P1CoreTerritoryHealerAgent.py` | Duplicate of TerritoryHealerAgent.py |
| `L2/ToolRegistry/governance.py` | Duplicate ArchitectureGovernorAgent |
| `L2/ToolRegistry/engineering.py` | Duplicate StructuralEngineerAgent |
| `L2/ToolRegistry/system_architect.py` | Duplicate SystemArchitectAgent |
| `L2/ToolRegistry/healer_executive.py` | Duplicate IntegrityGateExecutorAgent |
| `L2/ToolRegistry/peer_intelligence_auditor_impl.py` | Duplicate IntegrityGateExecutorAgent |
| `L2/ToolRegistry/section_scope_integrator_engine.py` | Duplicate IntegrityGateExecutorAgent |
| `L2/ToolRegistry/P2_tools_autonomous_redis_orchestrator.py` | Duplicate SovereignRedisOrchestratorAgent |
| `L2/ToolRegistry/concurrency.py` | Duplicates DeadlockDetector, MemoryLeakDetector |
| `L2/ToolRegistry/repair.py` | Duplicates TestPilotAgent, ToolsmithAgent |
| `L2/ToolRegistry/infrastructure.py` | Duplicate GitAgent |

### Files to Create (10 coordinators)

| File | Purpose | Replaces |
|------|---------|----------|
| `L3/unified_workflow_engine.py` | Central orchestration | 16 orchestrators |
| `L3/coordinators/rl_coordinator.py` | RL strategies | 5 RL agents |
| `L3/coordinators/dag_coordinator.py` | DAG operations | 5 DAG agents |
| `L3/coordinators/territory_coordinator.py` | Territory management | 5 territory agents |
| `L3/coordinators/health_coordinator.py` | Health monitoring | 5 monitor agents |
| `L2/coordinators/enforcement_coordinator.py` | Rule enforcement | 8 enforcers |
| `L2/coordinators/mcp_client_coordinator.py` | MCP access | 7 MCP clients |
| `L2/coordinators/architecture_coordinator.py` | System design | 6 architects |
| `L2/coordinators/safety_coordinator.py` | Safety checks | 6 safety agents |
| `L2/coordinators/memory_coordinator.py` | Memory management | 4 memory agents |

---

## Part 6: Risk Assessment

### Low Risk (Proceed immediately)
- Deleting exact name duplicates
- Creating coordinator base classes
- Documentation updates

### Medium Risk (Requires careful testing)
- Consolidating enforcer agents (similar patterns)
- Consolidating MCP clients (shared interface)
- Consolidating territory agents (semantic overlap)

### High Risk (Incremental migration)
- Consolidating core orchestrators (deeply integrated)
- Consolidating RL orchestrators (complex state)
- Removing NervousSystemAgent dependencies

### Mitigation Strategies
1. **Feature flags** for gradual rollout
2. **Parallel running** of old and new during transition
3. **Comprehensive test coverage** before deprecation
4. **Rollback plan** for each phase

---

## Appendix A: Agent Inventory with Metrics

### L3 Orchestration (49 agents)

| Agent | LOC | CC | Category | Action |
|-------|-----|-----|----------|--------|
| NervousSystemAgent | 645 | 666 | Core | → UnifiedWorkflowEngine |
| SubatomicOrchestratorAgent | 439 | 60 | Core | → UnifiedWorkflowEngine |
| DAGManagerAgent | 285 | 89 | DAG | → DAGCoordinator |
| DagEngineAgent | 172 | 58 | DAG | → DAGCoordinator |
| RLOrchestratorAgent | 157 | 44 | RL | → RLCoordinator |
| PPOOrchestratorAgent | 133 | 38 | RL | → RLCoordinator |
| QLearningOrchestratorAgent | 139 | 42 | RL | → RLCoordinator |
| ActorCriticOrchestratorAgent | 137 | 36 | RL | → RLCoordinator |
| SemanticTerritoryMapperAgent | 242 | 57 | Territory | → TerritoryCoordinator |
| TerritoryHealerAgent | 159 | 43 | Territory | → TerritoryCoordinator |
| DeadlockDetectorAgent | 649 | 41 | Monitor | → HealthCoordinator |
| MemoryLeakDetectorAgent | 649 | 74 | Monitor | → HealthCoordinator |

### L2 Execution (53 agents)

| Agent | LOC | CC | Category | Action |
|-------|-----|-----|----------|--------|
| CodeDeduplicationAgent | 565 | 171 | Code Quality | → CodeQualityCoordinator |
| MemoryArchitectAgent | 374 | 69 | Memory | → MemoryCoordinator |
| HealerAgent | 336 | 67 | Tooling | Keep (core) |
| PatternEnforcerAgent | 292 | 62 | Enforcement | → EnforcementCoordinator |
| StructuralEngineerAgent | 292 | 60 | Architecture | → ArchitectureCoordinator |
| CodeJanitorAgent | 267 | 79 | Code Quality | → CodeQualityCoordinator |
| GitAgent | 248 | 66 | Git | → GitCoordinator |
| IntegrityGateExecutorAgent | 235 | 37 | Safety | → SafetyCoordinator |

---

## Appendix B: Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Total Agents | 102 | 40 | Agent count in discovery.json |
| Duplicate Agents | 13 | 0 | Exact name matches |
| Avg Cyclomatic Complexity | 35.7 | <25 | Radon analysis |
| Test Coverage | 89.6% | >95% | pytest-cov |
| Workflow Latency | ~2000ms | <500ms | Performance tests |
| Code Duplication | High | <10% | Sonar/PMD |

---

**Report Generated:** January 5, 2026  
**Next Steps:** Review this report and approve Phase 1 (duplicate deletion) to begin consolidation.
