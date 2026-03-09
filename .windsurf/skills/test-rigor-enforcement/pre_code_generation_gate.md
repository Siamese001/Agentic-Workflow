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

### Step 2: Identify Changed Surfaces

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

  - function: save_result(data: dict) -> None
    type: side_effect_surface
    risk: file write must fail-closed on invalid input

file2.py:
  - class: StateMachine
    type: state_transition
    risk: transitions must validate predecessor states
```

### Step 3: Specify Required Test Coverage

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

### Step 4: Gate Decision

**BLOCK code generation if:**
- Scope not declared
- Changed surfaces not identified
- Test requirements not specified
- Test count < minimum required

**ALLOW code generation only if:**
- All surfaces identified
- All test requirements specified
- Test-first protocol will be followed (next step)

## Enforcement

```
IF test_requirements_complete:
    PROCEED to test_first_protocol.md
ELSE:
    BLOCK code generation
    REQUIRE user to complete test requirements
```

## Example Gate Execution

```
[PRE-CODE-GENERATION GATE]

SCOPE: 2 files
  - agentic_core/L5_safety/validators/new_validator.py (new)
  - agentic_core/L5_safety/enforcement/existing_enforcer.py (modified)

CHANGED_SURFACES: 3
  - new_validator.py::validate_input (decision surface)
  - new_validator.py::sanitize_path (side-effect surface)
  - existing_enforcer.py::enforce_rule (modified logic)

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
