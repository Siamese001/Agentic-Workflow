# Test Rigor Validation for Process Improvements

## PRE-CODE-GENERATION GATE

### SCOPE_DECLARATION
- agentic_core/L4_state/lifecycle/lifecycle_policy_applier.py (modified exports)
- tools/generate_full_adg.py (enhanced auto-commit flow)
- check_unknown.py (dynamic SQLite selection)

### DEPENDENCY_GRAPH
✅ BUILT (see dependency_graph_analysis.md)

Graph roots: [lifecycle_policy_applier.py, generate_full_adg.py, check_unknown.py]
Impacted nodes: 3 primary files + dependency chains
Upstream dependencies:
  - lifecycle_policy_applier.py imports: state_lifecycle, lifecycle_trace_contract
  - generate_full_adg.py imports: static_scanner, artifact builder, subprocess
  - check_unknown.py imports: sqlite3, pathlib
Downstream dependents:
  - lifecycle_policy_applier.py used by: L4_state/lifecycle/__init__.py
  - generate_full_adg.py used by: CI/CD pipelines, dev workflows
  - check_unknown.py used by: validation scripts, QA workflows
Cross-layer edges: All follow architectural constraints
Test coverage edges:
  - tests/unit/test_l4_state_lifecycle.py → lifecycle_policy_applier.py
  - Manual validation → check_unknown.py
  - Integration tests → generate_full_adg.py

### CHANGED_SURFACES

#### lifecycle_policy_applier.py
  - function: state_active (exported function)
    type: api_surface
    risk: missing import failures
    graph_justification: imported by L4_state/lifecycle/__init__.py

  - function: get_state_lifecycle_registry (exported function)
    type: api_surface
    risk: missing import failures
    graph_justification: imported by L4_state/lifecycle/__init__.py

  - function: reset_state_lifecycle_registry (exported function)
    type: api_surface
    risk: missing import failures
    graph_justification: imported by L4_state/lifecycle/__init__.py

#### generate_full_adg.py
  - function: _auto_commit_artifacts (modified logic)
    type: side_effect_surface
    risk: git operations must handle ignored files gracefully
    graph_justification: called during ADG generation pipeline

#### check_unknown.py
  - function: main script logic (modified file selection)
    type: integration_surface
    risk: must find latest SQLite reliably
    graph_justification: entrypoint for validation workflow

### GRAPH_IDENTIFIED_TESTS
✅ COMPLETE
- tests/unit/test_l4_state_lifecycle.py (direct import edge for lifecycle_policy_applier.py)
- Manual validation workflow (check_unknown.py)
- Integration testing (generate_full_adg.py)

### TEST_REQUIREMENTS

#### lifecycle_policy_applier.py exports
  Import validation (§1.8):
    - state_active can be imported successfully
    - get_state_lifecycle_registry can be imported successfully
    - reset_state_lifecycle_registry can be imported successfully
    - __all__ contains all required exports

  Test count: minimum 4 tests

#### generate_full_adg.py auto-commit
  Fail-closed (§1.8):
    - ignored files are skipped gracefully
    - no staged changes exits cleanly
    - git operations don't raise exceptions on ignored files

  Side-effect safety (§1.8):
    - staged changes committed successfully
    - commit message includes correct metrics
    - no partial commits

  Test count: minimum 6 tests

#### check_unknown.py dynamic selection
  Edge cases (§1.5):
    - no SQLite files exist
    - multiple SQLite files exist
    - corrupted SQLite file
    - permission denied on SQLite file

  Determinism (§1.7):
    - always selects latest file by mtime
    - identical file set → identical selection

  Test count: minimum 5 tests

TOTAL_REQUIRED_TESTS: 15

### GATE STATUS
✅ APPROVED
- Dependency graph complete with all required edge types
- All surfaces identified and graph-justified
- All test requirements specified
- Tests identified via graph relationships
- Test-first protocol will be followed

NEXT STEP: Execute post-code validation since changes already implemented
