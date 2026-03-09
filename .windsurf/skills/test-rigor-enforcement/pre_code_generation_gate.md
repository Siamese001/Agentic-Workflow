# Pre-Code-Generation Gate

**MANDATORY before any code changes.**

Enforces §1.1, §1.2, §1.5, §1.6, §1.7 from `.windsurfrules`.

## Protocol

### Step 1: Declare Scope

Record files to be changed:

```bash
git diff --name-only
```

If no changes yet, list files you PLAN to change.

**Output:**
```
SCOPE_DECLARATION:
- file1.py (new logic)
- file2.py (modified logic)
- file3.py (refactored logic)
```

### Step 2: Build Dependency Graph (§3.4 MANDATORY)

**BEFORE identifying changed surfaces, build AST dependency graph per §3.4.**

Required graph analysis:
- Module import edges
- Symbol import edges
- Class inheritance edges
- Function/method call edges
- Registry/factory resolution edges
- Test → production coverage edges

**Output:**
```
DEPENDENCY_GRAPH:
Graph roots: [file1.py, file2.py]
Impacted nodes: 5
Upstream dependencies:
  - file1.py imports: common/utils.py, config/settings.py
  - file2.py imports: file1.py, common/base.py
Downstream dependents:
  - file1.py used by: file2.py, tests/test_file1.py
  - file2.py used by: apps_lic/engines/control_plane.py, tests/test_file2.py
Cross-layer edges: None
Test coverage edges:
  - tests/test_file1.py → file1.py (direct import)
  - tests/test_file2.py → file2.py (direct import)
```

**FORBIDDEN:** Using grep, filename guessing, or text search to determine impact.

### Step 3: Identify Changed Surfaces

For each file in scope, identify:

- **Functions/methods** being added or modified
- **Classes** being added or modified
- **State transitions** being added or modified
- **Decision surfaces** (routing, scoring, hashing, ranking, thresholds)
- **Integration seams** (external calls, file I/O, database operations)
- **Side-effect surfaces** (mutations, writes, external calls)

**Output:**
```
CHANGED_SURFACES:
file1.py:
  - function: calculate_score(input: dict) -> float
    type: deterministic_decision_surface
    risk: scoring logic must be deterministic
    graph_justification: called by file2.py::process_data

  - function: save_result(data: dict) -> None
    type: side_effect_surface
    risk: file write must fail-closed on invalid input
    graph_justification: entrypoint for side-effect path

file2.py:
  - class: StateMachine
    type: state_transition
    risk: transitions must validate predecessor states
    graph_justification: inherits from common/base.py::BaseStateMachine
```

### Step 4: Identify Required Tests via Dependency Graph (§5.2)

**Use dependency graph to identify test files:**
- Direct test imports of changed files
- Fixture dependency edges
- Integration entrypoint coverage
- Registry/factory reachability

**Output:**
```
GRAPH_IDENTIFIED_TESTS:
- tests/test_file1.py (direct import edge)
- tests/test_file2.py (direct import edge)
- tests/integration/test_control_plane.py (downstream dependent edge)

COVERAGE_GAPS:
- file1.py::calculate_score has no direct test coverage edge
  → MUST create test_calculate_score.py
```

### Step 5: Specify Required Test Coverage

For each changed surface, declare required tests per §1.5:

**Template:**
```
TEST_REQUIREMENTS:

file1.py::calculate_score:
  Edge cases (§1.5):
    - null/None input
    - empty dict input
    - malformed structure (missing required keys)
    - boundary values (min/max scores)
    - invalid input types

  Determinism (§1.7):
    - identical input → identical output
    - normalized equivalent input → identical output
    - stable tie-break ordering

  Test count: minimum 7 tests

file1.py::save_result:
  Fail-closed (§1.8):
    - invalid preconditions block operation
    - no side-effects occur before block

  Side-effect safety (§1.8):
    - file write on valid input
    - exception on invalid input
    - no partial writes

  Edge cases (§1.5):
    - null/None data
    - empty dict
    - malformed structure

  Test count: minimum 6 tests

file2.py::StateMachine:
  State transitions (§1.6):
    - valid predecessor → valid successor
    - invalid predecessor → attempted successor
    - repeated transition
    - interrupted transition
    - replayed transition

  Test count: minimum 5 tests

TOTAL_REQUIRED_TESTS: 18
```

### Step 6: Gate Decision

**BLOCK code generation if:**
- Scope not declared
- **Dependency graph not built (§3.4 violation)**
- **Changed surfaces not justified by graph edges**
- Changed surfaces not identified
- Test requirements not specified
- Test count < minimum required
- **Test identification not graph-backed (§5.2 violation)**

**ALLOW code generation only if:**
- Dependency graph complete with all required edge types
- All surfaces identified and graph-justified
- All test requirements specified
- Tests identified via graph relationships
- Test-first protocol will be followed (next step)

## Enforcement

```
IF dependency_graph_built AND test_requirements_complete AND graph_backed_test_selection:
    PROCEED to test_first_protocol.md
ELSE:
    BLOCK code generation
    IF NOT dependency_graph_built:
        FAIL: §3.4 violation - AST dependency graph is mandatory
    IF NOT graph_backed_test_selection:
        FAIL: §5.2 violation - test selection must be graph-backed
    REQUIRE user to complete all requirements
```

## Example Gate Execution

```
[PRE-CODE-GENERATION GATE]

SCOPE: 2 files
  - agentic_core/L5_safety/validators/new_validator.py (new)
  - agentic_core/L5_safety/enforcement/existing_enforcer.py (modified)

DEPENDENCY_GRAPH: ✅ BUILT
  Graph roots: [new_validator.py, existing_enforcer.py]
  Upstream: config/structure_blueprint.py, L2_execution/tools/write_gateway.py
  Downstream: L0_routing/scripts/execute_ssot.py
  Test edges: tests/unit/L5_safety/test_new_validator.py → new_validator.py
  Cross-layer: existing_enforcer.py → L2_execution/tools/write_gateway.py (VALID)

CHANGED_SURFACES: 3
  - new_validator.py::validate_input (decision surface)
    graph_justification: called by execute_ssot.py::run_validation
  - new_validator.py::sanitize_path (side-effect surface)
    graph_justification: entrypoint for file mutation path
  - existing_enforcer.py::enforce_rule (modified logic)
    graph_justification: registry edge to write_gateway.py

GRAPH_IDENTIFIED_TESTS: ✅ COMPLETE
  - tests/unit/L5_safety/test_new_validator.py (direct import)
  - tests/unit/L5_safety/test_existing_enforcer.py (direct import)
  - tests/integration/test_execute_ssot.py (downstream dependent)

TEST_REQUIREMENTS: 21 tests minimum
  - Edge cases: 12 tests
  - Determinism: 4 tests
  - Fail-closed: 3 tests
  - State transitions: 2 tests

GATE STATUS: ✅ APPROVED
NEXT STEP: test_first_protocol.md
```

## Constitutional References

- **§1.1:** Every line of changed logic MUST be covered by deterministic tests
- **§1.2:** Tests MUST exist before logic changes are committed
- **§1.5:** Every changed surface MUST include edge case tests
- **§1.6:** Every changed state transition MUST test valid/invalid predecessors
- **§1.7:** Deterministic decision surfaces MUST prove identical input → identical output
- **§1.8:** Tests MUST prove invalid preconditions block operation
- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED analysis primitive
- **§3.5:** Low-signal search (grep/regex) FORBIDDEN as primary analysis method
- **§3.6:** If AST parsing fails, MUST fail closed (no silent fallback to text search)
- **§3.7:** Evidence MUST include DEPENDENCY_GRAPH section
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis
- **§5.2:** Test selection MUST be dependency-graph-backed
