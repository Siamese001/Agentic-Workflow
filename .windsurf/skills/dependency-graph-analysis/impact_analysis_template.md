# Impact Analysis Template

Use this template to document graph-backed impact analysis per §3.7, §4.4.

## 1. Analysis Context

```
ANALYSIS_DATE: <ISO timestamp>
TRIGGER: <What prompted this analysis>
SCOPE: <Initial files under consideration>
```

## 2. Dependency Graph Summary

```
GRAPH_ROOTS: [list]
TOTAL_NODES: <count>
TOTAL_EDGES: <count>
EDGE_TYPES_ANALYZED: [import, call, inheritance, registry, test, ...]
```

## 3. Directly Affected Nodes

List nodes that will be directly modified:

```
DIRECT_CHANGES:
1. path/to/file1.py::function_a
   - Change type: Logic modification
   - Risk level: HIGH (deterministic decision surface)

2. path/to/file2.py::MyClass
   - Change type: New method addition
   - Risk level: MEDIUM (state transition surface)
```

## 4. First-Order Upstream Dependencies

What do the changed files depend on?

```
UPSTREAM_DEPENDENCIES:
file1.py depends on:
  - common/utils.py::helper_function (call edge)
  - config/settings.py::THRESHOLD (symbol import)
  - agentic_core/L2_execution/base.py::BaseClass (inheritance edge)

Impact: Changes to file1.py may require compatibility with these upstream dependencies.
```

## 5. First-Order Downstream Dependents

What depends on the changed files?

```
DOWNSTREAM_DEPENDENTS:
file1.py is used by:
  - file2.py::process_data (call edge: calls file1.function_a)
  - apps_lic/engines/control_plane.py::run (import edge)
  - apps_rg/reasoning/SomeAgent.py::execute (call edge)
  - tests/test_file1.py (test coverage edge)

Impact: Changes to file1.py will affect 4 downstream dependents.
Regression testing required for all 4.
```

## 6. Required Test Nodes (§5.2)

Identify tests via graph relationships:

```
GRAPH_IDENTIFIED_TESTS:
Direct test coverage:
  - tests/test_file1.py → file1.py (direct import edge)
  - tests/test_file2.py → file2.py (direct import edge)

Integration test coverage:
  - tests/integration/test_control_plane.py → apps_lic/engines/control_plane.py → file1.py

Fixture dependencies:
  - tests/conftest.py::file1_fixture → file1.py

COVERAGE_GAPS:
  - file1.py::new_function_a (NO TEST COVERAGE EDGE)
    → MUST create test_new_function_a before proceeding
```

## 7. Cross-Layer Boundary Analysis

Check if changes cross architectural layer boundaries:

```
CROSS_LAYER_IMPACT:
file1.py location: agentic_core/L5_safety/validators/
file1.py imports: agentic_core/L2_execution/base.py

Cross-layer edge: L5 → L2 (VALID per architecture - safety can depend on execution)

Downstream cross-layer:
  - apps_lic/engines/control_plane.py (apps layer) → file1.py (L5 layer)
    Edge type: import
    Validity: VALID (apps can depend on core layers)
```

## 8. Registry/Factory Edge Analysis

Check if changes affect dynamic resolution:

```
REGISTRY_IMPACT:
file1.py::MyAgent registered as:
  - "my_agent" in agent_registry (via @register_agent decorator)

Factory edges:
  - file1.py::create_processor() returns ProcessorA or ProcessorB
  - Resolution depends on config.mode

Impact: Changes to file1.py::MyAgent will affect all registry lookups for "my_agent".
Impact: Changes to create_processor() will affect all factory resolution call sites.
```

## 9. Cycle Detection

```
CYCLE_ANALYSIS:
No cycles detected in affected subgraph.
OR
Cycle detected: file1.py → file2.py → file3.py → file1.py
  - Cycle type: Import cycle
  - Severity: HARD FAIL per §4.3
  - Required action: Break cycle before proceeding
```

## 10. Boundary Violations

```
BOUNDARY_VIOLATIONS:
None detected.
OR
Violation: apps_lic/reasoning/Agent.py → tools/evidence/helper.py
  - Violation type: Layer inversion (apps → tools)
  - Severity: HARD FAIL per §4.3
  - Required action: Remove dependency or refactor
```

## 11. Blast Radius Summary

```
BLAST_RADIUS:
Direct changes: 2 files
First-order upstream: 3 files
First-order downstream: 4 files
Required tests: 5 test files
Total impacted nodes: 14

Risk assessment:
  - HIGH: 2 nodes (deterministic decision surfaces)
  - MEDIUM: 3 nodes (state transition surfaces)
  - LOW: 9 nodes (pure data/config)
```

## 12. Execution Path Analysis

Trace execution paths through the graph:

```
EXECUTION_PATHS:
CLI entrypoint → affected code:
  - ops_scripts/ci/run_contract_gates.py::main()
    → agentic_core/L0_routing/scripts/execute_ssot.py::run()
    → file1.py::function_a()

User-facing entrypoint → affected code:
  - apps_lic/engines/control_plane.py::run()
    → file1.py::function_a()
    → file2.py::process_data()
```

## 13. Graph-Backed Scope Justification (§3.7)

For each file in scope, provide graph justification:

```
SCOPE_JUSTIFICATION:
file1.py:
  - Reason: Direct modification target
  - Graph evidence: Root node of analysis
  - Impact: 4 downstream dependents require regression testing

file2.py:
  - Reason: Downstream dependent of file1.py
  - Graph evidence: Call edge from file2.py::process_data → file1.py::function_a
  - Impact: Must update to handle file1.py changes

tests/test_file1.py:
  - Reason: Test coverage edge
  - Graph evidence: Direct import edge tests/test_file1.py → file1.py
  - Impact: Must add tests for new file1.py::function_a logic

Any file NOT justified by graph = scope contamination per §3.7
```

## 14. Confidence Assessment

```
CONFIDENCE_LEVEL:
Graph completeness: COMPLETE / PARTIAL
Parse errors: 0 / <count>
Incomplete files: None / [list]

Overall confidence: HIGH / MEDIUM / LOW

If PARTIAL or LOW:
  - Exact limitations: <describe>
  - Missing edges: <list>
  - Blocked files: <list>
  - Recommended action: <next steps>
```

## Constitutional Compliance

- [ ] Graph roots explicitly defined (§3.4)
- [ ] All required edge types analyzed (§3.4)
- [ ] Upstream dependencies identified (§4.4)
- [ ] Downstream dependents identified (§4.4)
- [ ] Test nodes identified via graph (§5.2)
- [ ] Cross-layer edges checked (§4.3)
- [ ] Cycles detected (§4.3)
- [ ] Boundary violations checked (§4.3)
- [ ] Each file has graph justification (§3.7)
- [ ] NO grep/regex used for primary analysis (§3.5)
- [ ] Parse failures recorded if any (§3.6)
