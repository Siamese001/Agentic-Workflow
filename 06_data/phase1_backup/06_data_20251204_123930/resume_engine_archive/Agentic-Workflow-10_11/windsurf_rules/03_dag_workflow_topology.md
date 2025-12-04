# /windsurf_rules/03_dag_workflow_topology.md
## DAG, Workflow, and Module Topology Rules (Condensed)

### 1. DAG Orchestration (L3 Only)
- DAG must be typed, acyclic, resumable.
- All node transitions validate OutputSchema → InputSchema.
- Only L3 may orchestrate; agents must not self-route.
- Branching must be explicit and validated.

### 2. Module & Folder Topology
- /l1 = planning  
- /l2 = tools  
- /l3 = orchestration  
- /l4 = state/memory  
- /l5 = safety  
- /prompts = templates & constitutions  
- /tests mirrors module topology  
- /refactoring = notes/docs only; no `.py`  

### 3. Public API Surfaces
- Each layer must expose a single stable facade:  
  - l1.api, l2.api, l3.api, l4.api, l5.api

### 4. Import Matrix (Golden)
All modules must satisfy the layer import matrix without exception.
