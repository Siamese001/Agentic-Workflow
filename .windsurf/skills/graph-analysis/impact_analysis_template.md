# Impact Analysis Template

## DEPENDENCY_GRAPH Section Format

Required for all T3 operations. Include in the evidence file.

```
## DEPENDENCY_GRAPH
**Graph Roots**: <primary changed nodes — file or symbol names>
**Impacted Nodes**: <N> nodes total
**Upstream Set**: <nodes that depend on the changed nodes>
**Downstream Set**: <nodes that the changed nodes depend on>
**Edge Classes**: <types of edges involved — IMPORTS, CALLS, INHERITS, etc.>
**Boundary/Cycle Findings**: <layer violations, circular imports, or NONE>
**Scope Justification**:
  - path/to/file1.py — Reason: root module per ADG cluster X
  - path/to/file2.py — Reason: imports file1 via IMPORTS edge in graph
  - ...
```

## Blast Radius Determination

1. Start at graph roots (changed files)
2. Fan-out: find all nodes that import or call the changed nodes (upstream dependents)
3. Fan-in: find all nodes the changed nodes depend on (downstream dependencies)
4. Flag any cross-layer edges or cycles
5. Determine if blast radius is contained (T2) or cross-layer (T3)

## SCOPE_DECLARATION Section Format

Required before any file edits.

```
## SCOPE_DECLARATION
Files to modify: N
1. path/to/file1.py — Reason: root module per ADG cluster X
2. path/to/file2.py — Reason: imports file1, edge (file2 → file1) in graph
...
Baseline: git diff clean (no uncommitted changes)
```
