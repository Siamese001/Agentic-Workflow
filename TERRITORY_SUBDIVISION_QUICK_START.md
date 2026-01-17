# Territory Subdivision Quick Start Guide

**Goal:** Break out 7 high-count territories (>15 agents) into 2-4 sub-territories each using AST analysis.

---

## High-Count Territories to Subdivide

| Territory | Current Count | Target Sub-Territories | Strategy |
|-----------|---------------|------------------------|----------|
| **L3 Orchestration/Core** | 50 agents | 4 sub-territories | Name + docstring patterns |
| **Apps Lic** | 37 agents | 3 sub-territories | Directory structure |
| **L2 Execution/Core** | 36 agents | 3 sub-territories | Name + method patterns |
| **L5 Safety/Guardrails** | 28 agents | 2 sub-territories | MCP vs Core |
| **L1 Cognition/Core** | 27 agents | 3 sub-territories | Reasoning/Memory/Planning |
| **Apps Rg** | 24 agents | 2 sub-territories | Directory structure |
| **L5 Safety/Validators** | 23 agents | 2 sub-territories | Content vs Structure |

---

## Implementation Approach

### Step 1: Add Subdivision Logic to `territory_ssot_definitions.py`

Add new function after `get_territory_from_path()`:

```python
def refine_territory_by_ast(
    territory: str,
    class_name: str,
    docstring: str,
    path_str: str
) -> str:
    """
    Refine high-count territories into sub-territories using AST analysis.
    
    Args:
        territory: Current territory from get_territory_from_path()
        class_name: Agent class name
        docstring: Class docstring (first line)
        path_str: Normalized path string
    
    Returns:
        Refined territory name or original if no subdivision needed
    """
    # Only subdivide high-count territories
    if territory not in HIGH_COUNT_TERRITORIES:
        return territory
    
    # L3 Orchestration/Core → 4 sub-territories
    if territory == 'L3 Orchestration/Core':
        return _categorize_l3_orchestration(class_name, docstring, path_str)
    
    # Apps Lic → 3 sub-territories
    if territory == 'Apps Lic':
        return _categorize_apps_lic(class_name, docstring, path_str)
    
    # L2 Execution/Core → 3 sub-territories
    if territory == 'L2 Execution/Core':
        return _categorize_l2_execution(class_name, docstring, path_str)
    
    # L5 Safety/Guardrails → 2 sub-territories
    if territory == 'L5 Safety/Guardrails':
        return _categorize_l5_guardrails(class_name, docstring, path_str)
    
    # L1 Cognition/Core → 3 sub-territories
    if territory == 'L1 Cognition/Core':
        return _categorize_l1_cognition(class_name, docstring, path_str)
    
    # Apps Rg → 2 sub-territories
    if territory == 'Apps Rg':
        return _categorize_apps_rg(class_name, docstring, path_str)
    
    # L5 Safety/Validators → 2 sub-territories
    if territory == 'L5 Safety/Validators':
        return _categorize_l5_validators(class_name, docstring, path_str)
    
    return territory


# High-count territories that need subdivision
HIGH_COUNT_TERRITORIES = {
    'L3 Orchestration/Core',
    'Apps Lic',
    'L2 Execution/Core',
    'L5 Safety/Guardrails',
    'L1 Cognition/Core',
    'Apps Rg',
    'L5 Safety/Validators',
}


def _categorize_l3_orchestration(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L3 Orchestration/Core agents into 4 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or '').lower()
    
    # DAG-related agents
    if 'dag' in name_lower or 'dag' in doc_lower or 'graph' in doc_lower:
        return 'L3 Orchestration/DAG'
    
    # Routing and connection management
    if any(kw in name_lower for kw in ['router', 'connection', 'manager']):
        return 'L3 Orchestration/Routing'
    
    # Monitoring, metrics, coverage, detection
    if any(kw in name_lower for kw in ['metric', 'coverage', 'detector', 'monitor', 'benchmark']):
        return 'L3 Orchestration/Monitoring'
    
    # Workflow orchestration
    if any(kw in name_lower for kw in ['workflow', 'orchestrat', 'nervous', 'phase']):
        return 'L3 Orchestration/Workflow'
    
    # Fallback: Keep in Core
    return 'L3 Orchestration/Core'


def _categorize_apps_lic(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize Apps Lic agents into 3 sub-territories."""
    # Use directory structure
    if '/engines/' in path_str or 'engine' in class_name.lower():
        return 'Apps Lic/Engines'
    if '/domain/' in path_str or '/validators/' in path_str:
        return 'Apps Lic/Domain'
    if '/utils/' in path_str or 'util' in class_name.lower() or 'helper' in class_name.lower():
        return 'Apps Lic/Utilities'
    
    # Fallback: Domain
    return 'Apps Lic/Domain'


def _categorize_l2_execution(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L2 Execution/Core agents into 3 sub-territories."""
    name_lower = class_name.lower()
    
    # Task runners and executors
    if any(kw in name_lower for kw in ['runner', 'executor', 'task', 'worker']):
        return 'L2 Execution/Runners'
    
    # Event handlers
    if any(kw in name_lower for kw in ['handler', 'event', 'listener']):
        return 'L2 Execution/Handlers'
    
    # Coordinators and managers
    if any(kw in name_lower for kw in ['coordinator', 'manager', 'scheduler']):
        return 'L2 Execution/Coordinators'
    
    # Fallback: Runners
    return 'L2 Execution/Runners'


def _categorize_l5_guardrails(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L5 Safety/Guardrails agents into 2 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or '').lower()
    
    # MCP-related safety
    if 'mcp' in name_lower or 'mcp' in doc_lower or 'hardened' in name_lower:
        return 'L5 Safety/Guardrails/MCP'
    
    # Core guardrails
    return 'L5 Safety/Guardrails/Core'


def _categorize_l1_cognition(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L1 Cognition/Core agents into 3 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or '').lower()
    
    # Reasoning and LLM
    if any(kw in name_lower for kw in ['reason', 'llm', 'model', 'inference']):
        return 'L1 Cognition/Reasoning'
    
    # Memory and context
    if any(kw in name_lower for kw in ['memory', 'context', 'cache', 'recall']):
        return 'L1 Cognition/Memory'
    
    # Planning and strategy
    if any(kw in name_lower for kw in ['plan', 'strategy', 'goal', 'intent']):
        return 'L1 Cognition/Planning'
    
    # Fallback: Reasoning
    return 'L1 Cognition/Reasoning'


def _categorize_apps_rg(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize Apps Rg agents into 2 sub-territories."""
    # Use directory structure
    if '/engines/' in path_str or 'engine' in class_name.lower():
        return 'Apps Rg/Engines'
    
    # Domain and content
    return 'Apps Rg/Domain'


def _categorize_l5_validators(class_name: str, docstring: str, path_str: str) -> str:
    """Categorize L5 Safety/Validators agents into 2 sub-territories."""
    name_lower = class_name.lower()
    doc_lower = (docstring or '').lower()
    
    # Content validation
    if any(kw in name_lower for kw in ['content', 'text', 'ascii', 'format']):
        return 'L5 Safety/Validators/Content'
    
    # Structure validation
    return 'L5 Safety/Validators/Structure'
```

### Step 2: Update `full_agent_discovery.py`

Find the section where territory is assigned (around line 1510) and add refinement:

```python
# SSOT: Use centralized territory name function
path_str = str(rel_path).replace('\\', '/').lower()
territory = get_territory_from_path(
    layer=layer,
    path_str=path_str,
    is_base_class=is_base_class,
    class_name=class_name
)

# NEW: Refine high-count territories using AST analysis
docstring = ast.get_docstring(node) or ""
territory = refine_territory_by_ast(
    territory=territory,
    class_name=class_name,
    docstring=docstring,
    path_str=path_str
)
```

### Step 3: Update Imports

Add to imports in `full_agent_discovery.py`:

```python
from territory_ssot_definitions import get_territory_from_path, refine_territory_by_ast
```

### Step 4: Test & Validate

```bash
# Regenerate discovery
python scripts/full_agent_discovery.py

# Check territory distribution
python -c "import json; from collections import Counter; agents = json.load(open('agent_discovery_full.json')); territories = Counter(a['territory'] for a in agents); high_count = {t: c for t, c in territories.items() if c > 15}; print(f'High-count territories: {len(high_count)}'); [print(f'  {t}: {c}') for t, c in sorted(high_count.items(), key=lambda x: -x[1])]"

# Regenerate dashboard
python scripts/regenerate_dashboard_data.py

# View in browser
# http://localhost:8765/autonomy_dashboard.html
```

---

## Expected Results

### Before Subdivision
- 7 territories with >15 agents
- Low signal quality for high-count territories

### After Subdivision
- 0 territories with >15 agents (all ≤15)
- 20-25 total territories (up from ~24)
- High signal quality across all territories
- Better drill-down granularity

---

## Validation Checklist

- [ ] All high-count territories subdivided
- [ ] No territory has >15 agents
- [ ] Sub-territory names are semantically meaningful
- [ ] Dashboard displays new territories correctly
- [ ] Drill-down functionality works for sub-territories
- [ ] Metrics aggregate correctly
- [ ] No agents lost or duplicated

---

## Rollback Plan

If subdivision causes issues:

1. Revert changes to `territory_ssot_definitions.py`
2. Revert changes to `full_agent_discovery.py`
3. Regenerate: `python scripts/full_agent_discovery.py`
4. Regenerate dashboard: `python scripts/regenerate_dashboard_data.py`

---

## Timeline

- **Implementation:** 2-3 hours
- **Testing:** 1 hour
- **Validation:** 30 minutes
- **Total:** 3.5-4.5 hours
