# Dependency Graph Analysis for Process Improvements

## DEPENDENCY_GRAPH

### Graph Roots
- agentic_core/L4_state/lifecycle/lifecycle_policy_applier.py
- tools/generate_full_adg.py
- check_unknown.py

### Node Types Included
- Modules (Python files)
- Functions/methods
- Classes
- Import statements
- Git operations
- ADG scanner operations

### Edge Types Analyzed
- Module import edges (import statements)
- Symbol import edges (from X import Y)
- Function/method call edges
- Git subprocess edges
- ADG scanner invocation edges

### Impacted Nodes
Total: 3 primary files with their dependency chains

### Upstream Dependencies

#### lifecycle_policy_applier.py
- agentic_core.L4_state.lifecycle.state_lifecycle (LifecycleStatus, RetentionClass, StateLifecycleError, StateLifecycleRecord, get_state_lifecycle_registry, reset_state_lifecycle_registry)
- agentic_core.runtime.lifecycle_trace_contract (multiple _emit_* functions)
- dataclasses, logging, time, typing

#### generate_full_adg.py
- agentic_core.adg.extraction.static_scanner (ADGStaticScanner)
- agentic_core.adg.artifact.builder (ADGArtifactBuilder)
- pathlib, subprocess, sys
- Git operations (add, check-ignore, commit, diff)

#### check_unknown.py
- sqlite3, pathlib

### Downstream Dependents

#### lifecycle_policy_applier.py
- agentic_core/L4_state/lifecycle/__init__.py (imports state_active and other functions)
- Any code using L4 state lifecycle functions

#### generate_full_adg.py
- CI/CD pipelines (calls this script)
- Development workflows (manual ADG generation)
- ADG-dependent analysis tools

#### check_unknown.py
- Development validation scripts
- Quality assurance workflows

### Cross-Layer Edges
- generate_full_adg.py: L5_TOOLS → L0_ROUTING (git operations)
- lifecycle_policy_applier.py: L4_STATE → L2_EXECUTION (lifecycle trace contract)
- check_unknown.py: L_TOOLS → L5_SAFETY (SQLite validation)

### Cycle/SCC Findings
No cycles detected in the dependency graph

### Boundary Violations
None detected - all cross-layer edges follow architectural constraints

### Test Surface Implications
- lifecycle_policy_applier.py: Tests in tests/unit/test_l4_state_lifecycle.py
- generate_full_adg.py: Integration tests via ADG generation
- check_unknown.py: Manual validation testing

### Scope Justification
All three files are directly modified for process improvements:
1. lifecycle_policy_applier.py: Fixed missing exports to resolve import failures
2. generate_full_adg.py: Enhanced auto-commit flow to avoid ignored-file warnings
3. check_unknown.py: Made SQLite selection dynamic for reliable validation

### Graph Metadata
Construction timestamp: 2026-03-22T16:43
Graph extractor: tools/generate_full_adg.py
AST parser version: Python 3.12 ast module
Repository commit: 1f2a17ea2a487f0af23f04e29dc672d065dd9abd
Total files analyzed: 6,556
Parse errors: 0
Incomplete files: 0
