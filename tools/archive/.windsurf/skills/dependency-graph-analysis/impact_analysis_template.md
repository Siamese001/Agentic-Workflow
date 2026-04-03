# Impact Analysis Template

**Use for T2/T3 changes per §0 and §2.4.**

## Template

```
## DEPENDENCY_GRAPH

### Analysis Context
- Trigger: <what prompted analysis>
- Graph roots: <list>
- Total nodes: <count> | Total edges: <count>

### Directly Affected Nodes
1. <file>::<symbol> — change type, risk level

### Upstream Dependencies
<file> depends on:
  - <dep> (edge type)

### Downstream Dependents
<file> used by:
  - <dependent> (edge type)
  Regression testing required for all dependents.

### Required Tests (§1.3)
- Direct test coverage: <tests>
- Integration test coverage: <tests>
- Coverage gaps: <any missing> → MUST create before proceeding

### Cross-Layer Boundary Analysis
- Cross-layer edges: <list with validity>
- Layer inversions: <none | list — HARD FAIL>

### Cycle Detection
- Cycles: <none | list — HARD FAIL per §8.2>

### Blast Radius Summary
- Direct changes: <N> files
- Upstream: <N> files
- Downstream: <N> files
- Required tests: <N> test files
- Risk: HIGH/MEDIUM/LOW per node

### Scope Justification (§2.4)
For each file: reason in scope + graph evidence.
Any file NOT justified by graph = scope contamination.

### Confidence
- Completeness: COMPLETE/PARTIAL
- Parse errors: <count>
- Confidence: HIGH/MEDIUM/LOW
```
