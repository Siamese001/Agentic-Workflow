# Implementation Plan: AST-Based Territory Subdivision for High-Count Agent Territories

**Date:** January 17, 2026  
**Objective:** Break out territories with >15 agents into 2-3 sub-territories using AST analysis to improve signal quality

---

## Problem Statement

**Current Issue:** Several territories have excessively high agent counts (>15), making them too high-level to provide meaningful signal in the dashboard.

**High-Count Territories (>15 agents):**
1. **L3 Orchestration/Core**: 50 agents ← PRIMARY TARGET
2. **Apps Lic**: 37 agents
3. **L2 Execution/Core**: 36 agents
4. **L5 Safety/Guardrails**: 28 agents
5. **L1 Cognition/Core**: 27 agents
6. **Apps Rg**: 24 agents
7. **L5 Safety/Validators**: 23 agents

**Goal:** Subdivide these territories into 2-3 meaningful sub-categories based on AST analysis to improve dashboard signal quality.

---

## AST-Based Categorization Strategies

### Strategy 1: **Functional Role Analysis** (RECOMMENDED)

Use AST to analyze agent purpose and categorize by functional role:

**AST Signals:**
- **Class docstring keywords**: Extract first line of docstring, identify role keywords
- **Method patterns**: Analyze method names for common patterns (e.g., `execute_*`, `validate_*`, `monitor_*`)
- **Base class inheritance**: Group by shared base classes beyond layer bases
- **Import patterns**: Analyze imports to identify domain (e.g., DAG, workflow, metrics, MCP)

**Example for L3 Orchestration/Core (50 agents):**

Based on grep results, natural subdivisions:
1. **L3 Orchestration/DAG** (DAG-related agents)
   - `DagEngineAgent`, `DagExecutorAgent`, `DagManagerAgent`, `DAGMutatorAgent`, `DagRuntimeInspectorAgent`
   
2. **L3 Orchestration/Workflow** (Workflow orchestration)
   - `NervousSystemAgent`, `NervousSystemPhaseOrchestratorAgent`, `HardenedWorkflowOrchestratorAgent`, `OrchestrationHandshakeAgent`
   
3. **L3 Orchestration/Routing** (Routing and connection management)
   - `ModelRouterAgent`, `McpRouterAgent`, `McpConnectionManagerAgent`
   
4. **L3 Orchestration/Monitoring** (Metrics, coverage, detection)
   - `MetricsAgent`, `CoverageAgent`, `MetaCoverageOptimizerAgent`, `DeadlockDetectorAgent`, `HallucinationDetectorAgent`

**AST Implementation:**
```python
def categorize_l3_orchestration_agent(class_node: ast.ClassDef, source: str) -> str:
    """Categorize L3 Orchestration agents into sub-territories."""
    class_name = class_node.name
    
    # Strategy 1: Name-based patterns (most reliable)
    if 'Dag' in class_name or 'DAG' in class_name:
        return 'L3 Orchestration/DAG'
    if 'Router' in class_name or 'Connection' in class_name:
        return 'L3 Orchestration/Routing'
    if 'Metrics' in class_name or 'Coverage' in class_name or 'Detector' in class_name:
        return 'L3 Orchestration/Monitoring'
    if 'Workflow' in class_name or 'Orchestrat' in class_name or 'Nervous' in class_name:
        return 'L3 Orchestration/Workflow'
    
    # Strategy 2: Docstring analysis
    docstring = ast.get_docstring(class_node)
    if docstring:
        doc_lower = docstring.lower()
        if 'dag' in doc_lower or 'graph' in doc_lower:
            return 'L3 Orchestration/DAG'
        if 'route' in doc_lower or 'connection' in doc_lower:
            return 'L3 Orchestration/Routing'
        if 'metric' in doc_lower or 'coverage' in doc_lower or 'detect' in doc_lower:
            return 'L3 Orchestration/Monitoring'
        if 'workflow' in doc_lower or 'orchestrat' in doc_lower:
            return 'L3 Orchestration/Workflow'
    
    # Strategy 3: Import analysis
    imports = extract_imports(source)
    if any('dag' in imp.lower() for imp in imports):
        return 'L3 Orchestration/DAG'
    
    # Default: Keep in Core if no clear categorization
    return 'L3 Orchestration/Core'
```

### Strategy 2: **Complexity-Based Subdivision**

Group agents by complexity tier:
- **High Complexity** (CC > 20): Complex orchestrators
- **Medium Complexity** (10 < CC ≤ 20): Standard agents
- **Low Complexity** (CC ≤ 10): Simple utilities

**Pros:** Objective, quantitative
**Cons:** Less semantically meaningful than functional role

### Strategy 3: **Inheritance Hierarchy**

Group by immediate base class:
- **MCPHardenedMixin-based**: MCP-integrated agents
- **HealerMixin-based**: Self-healing agents
- **SubatomicTestingMixin-based**: Testing-focused agents

**Pros:** Clear architectural grouping
**Cons:** Many agents share multiple mixins, creates overlap

---

## Recommended Approach: Hybrid Strategy

**Combine Functional Role (primary) + Name Patterns (secondary) + Docstring Analysis (fallback)**

### Implementation Steps

#### Phase 1: AST Analysis Enhancement (1-2 hours)

**File:** `scripts/full_agent_discovery.py`

**Add function:**
```python
def categorize_agent_by_role(
    class_node: ast.ClassDef, 
    source: str, 
    layer: str, 
    current_territory: str
) -> str:
    """
    Subdivide high-count territories using AST analysis.
    
    Returns refined territory name or original if no subdivision needed.
    """
    class_name = class_node.name
    docstring = ast.get_docstring(class_node) or ""
    
    # Only subdivide territories with >15 agents
    if current_territory not in HIGH_COUNT_TERRITORIES:
        return current_territory
    
    # L3 Orchestration/Core → 4 sub-territories
    if current_territory == 'L3 Orchestration/Core':
        return categorize_l3_orchestration(class_name, docstring, source)
    
    # Apps Lic → 2-3 sub-territories
    if current_territory == 'Apps Lic':
        return categorize_apps_lic(class_name, docstring, source)
    
    # L2 Execution/Core → 2-3 sub-territories
    if current_territory == 'L2 Execution/Core':
        return categorize_l2_execution(class_name, docstring, source)
    
    # ... similar for other high-count territories
    
    return current_territory
```

**Integration point:**
```python
# In discover_agents_in_directory():
territory = determine_territory(rel_path, layer)

# NEW: Subdivide high-count territories
territory = categorize_agent_by_role(node, source, layer, territory)
```

#### Phase 2: Territory-Specific Categorization (2-3 hours)

**Implement categorization for each high-count territory:**

1. **L3 Orchestration/Core (50 agents) → 4 sub-territories**
   - L3 Orchestration/DAG
   - L3 Orchestration/Workflow
   - L3 Orchestration/Routing
   - L3 Orchestration/Monitoring

2. **Apps Lic (37 agents) → 3 sub-territories**
   - Apps Lic/Engines (campaign, outreach engines)
   - Apps Lic/Domain (validators, quality agents)
   - Apps Lic/Utilities (helpers, formatters)

3. **L2 Execution/Core (36 agents) → 3 sub-territories**
   - L2 Execution/Runners (task execution)
   - L2 Execution/Handlers (event handling)
   - L2 Execution/Coordinators (coordination logic)

4. **L5 Safety/Guardrails (28 agents) → 2 sub-territories**
   - L5 Safety/Guardrails/MCP (MCP-related safety)
   - L5 Safety/Guardrails/Core (general guardrails)

5. **L1 Cognition/Core (27 agents) → 3 sub-territories**
   - L1 Cognition/Reasoning (LLM, reasoning)
   - L1 Cognition/Memory (context, memory)
   - L1 Cognition/Planning (planning, strategy)

6. **Apps Rg (24 agents) → 2 sub-territories**
   - Apps Rg/Engines (resume engines)
   - Apps Rg/Domain (content, quality agents)

7. **L5 Safety/Validators (23 agents) → 2 sub-territories**
   - L5 Safety/Validators/Content (content validation)
   - L5 Safety/Validators/Structure (structure validation)

#### Phase 3: Testing & Validation (1 hour)

**Test script:**
```python
# scripts/test_territory_subdivision.py

def test_territory_subdivision():
    """Verify territory subdivision reduces high-count territories."""
    agents = json.load(open('agent_discovery_full.json'))
    
    # Count agents per territory
    territory_counts = Counter(a['territory'] for a in agents)
    
    # Verify no territory has >15 agents
    high_count = {t: c for t, c in territory_counts.items() if c > 15}
    
    if high_count:
        print(f"❌ FAILED: {len(high_count)} territories still have >15 agents:")
        for t, c in sorted(high_count.items(), key=lambda x: -x[1]):
            print(f"   - {t}: {c} agents")
        return False
    
    print(f"✅ PASSED: All territories have ≤15 agents")
    print(f"   Total territories: {len(territory_counts)}")
    print(f"   Avg agents per territory: {sum(territory_counts.values()) / len(territory_counts):.1f}")
    return True
```

#### Phase 4: Dashboard Integration (30 min)

**No changes needed!** Dashboard automatically adapts to new territory names.

**Verify:**
- Dashboard shows new sub-territories as separate rows
- Drill-down still works for sub-territories
- Metrics aggregate correctly

---

## AST Analysis Patterns

### Pattern 1: Name-Based Classification

```python
def classify_by_name(class_name: str) -> Optional[str]:
    """Extract role from class name patterns."""
    patterns = {
        'DAG': 'DAG',
        'Dag': 'DAG',
        'Router': 'Routing',
        'Connection': 'Routing',
        'Manager': 'Routing',
        'Metrics': 'Monitoring',
        'Coverage': 'Monitoring',
        'Detector': 'Monitoring',
        'Monitor': 'Monitoring',
        'Workflow': 'Workflow',
        'Orchestrat': 'Workflow',
        'Nervous': 'Workflow',
        'Phase': 'Workflow',
    }
    
    for pattern, category in patterns.items():
        if pattern in class_name:
            return category
    return None
```

### Pattern 2: Docstring Keyword Analysis

```python
def classify_by_docstring(docstring: str) -> Optional[str]:
    """Extract role from docstring keywords."""
    if not docstring:
        return None
    
    doc_lower = docstring.lower()
    
    keywords = {
        'DAG': ['dag', 'graph', 'directed acyclic'],
        'Routing': ['route', 'router', 'connection', 'switch'],
        'Monitoring': ['metric', 'coverage', 'detect', 'monitor', 'track'],
        'Workflow': ['workflow', 'orchestrat', 'coordinate', 'phase'],
    }
    
    for category, words in keywords.items():
        if any(word in doc_lower for word in words):
            return category
    return None
```

### Pattern 3: Method Pattern Analysis

```python
def classify_by_methods(class_node: ast.ClassDef) -> Optional[str]:
    """Extract role from method name patterns."""
    methods = [n.name for n in class_node.body if isinstance(n, ast.FunctionDef)]
    
    patterns = {
        'DAG': ['execute_dag', 'build_dag', 'mutate_dag', 'validate_dag'],
        'Routing': ['route_', 'connect_', 'dispatch_'],
        'Monitoring': ['track_', 'measure_', 'detect_', 'monitor_'],
        'Workflow': ['orchestrate_', 'coordinate_', 'execute_phase'],
    }
    
    for category, method_patterns in patterns.items():
        if any(any(pattern in m for pattern in method_patterns) for m in methods):
            return category
    return None
```

---

## Expected Outcomes

### Before Subdivision
```
L3 Orchestration/Core: 50 agents  ← Too broad
Apps Lic: 37 agents               ← Too broad
L2 Execution/Core: 36 agents      ← Too broad
```

### After Subdivision
```
L3 Orchestration/DAG: 12 agents           ← High signal
L3 Orchestration/Workflow: 15 agents      ← High signal
L3 Orchestration/Routing: 8 agents        ← High signal
L3 Orchestration/Monitoring: 10 agents    ← High signal
L3 Orchestration/Core: 5 agents           ← Residual

Apps Lic/Engines: 14 agents
Apps Lic/Domain: 13 agents
Apps Lic/Utilities: 10 agents

L2 Execution/Runners: 13 agents
L2 Execution/Handlers: 12 agents
L2 Execution/Coordinators: 11 agents
```

**Benefits:**
- ✅ All territories ≤15 agents (high signal)
- ✅ Semantically meaningful groupings
- ✅ Better drill-down granularity
- ✅ Easier to identify problem areas

---

## Implementation Timeline

| Phase | Task | Duration | Owner |
|-------|------|----------|-------|
| 1 | AST analysis enhancement | 1-2 hours | Dev |
| 2 | Territory-specific categorization | 2-3 hours | Dev |
| 3 | Testing & validation | 1 hour | Dev |
| 4 | Dashboard integration verification | 30 min | Dev |
| **Total** | | **4.5-6.5 hours** | |

---

## Risks & Mitigations

### Risk 1: Agents don't fit clear categories
**Mitigation:** Keep residual "Core" category for uncategorized agents

### Risk 2: Over-subdivision creates too many territories
**Mitigation:** Limit to 2-4 sub-territories per high-count territory, max 15 agents per sub-territory

### Risk 3: Dashboard becomes cluttered
**Mitigation:** Dashboard already handles 24 territories well, adding 10-15 more is manageable

### Risk 4: Breaking changes to existing queries
**Mitigation:** Territory names are additive (e.g., `L3 Orchestration/DAG` is still in `L3 Orchestration` layer)

---

## Next Steps

1. **Review & approve** this implementation plan
2. **Implement** AST categorization functions in `full_agent_discovery.py`
3. **Test** with `python scripts/full_agent_discovery.py`
4. **Validate** with `python scripts/test_territory_subdivision.py`
5. **Regenerate** dashboard: `python scripts/generate_dashboard.py`
6. **Verify** in browser: Check new sub-territories display correctly

---

## Appendix: L3 Orchestration/Core Agent List

Based on grep results, L3 Orchestration/Core contains agents like:
- NervousSystemAgent, NervousSystemPhaseOrchestratorAgent
- ModelRouterAgent, McpRouterAgent, McpConnectionManagerAgent
- MetricsAgent, MetaCoverageOptimizerAgent, CoverageAgent
- DagEngineAgent, DagExecutorAgent, DagManagerAgent, DAGMutatorAgent, DagRuntimeInspectorAgent
- HardenedWorkflowOrchestratorAgent, OrchestrationHandshakeAgent
- DeadlockDetectorAgent, HallucinationDetectorAgent
- GitSafetyHandlerAgent, GeneralExerciserAgent
- HierarchyEnforcerAgent, L3OrchestrationBaseAgent, L3Agent

**Natural groupings emerge from naming patterns**, making AST-based categorization highly feasible.
