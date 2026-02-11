# Guardian Test Design Pattern

## Architecture Position

Guardian tests represent the **Guardian (Validation Gate)** in the center of the architecture (The Red Shield). They act as the final **Compliance Gate** that a "Proposed Fix" must pass before entering the **Symmetric Validator-Healer Pipe**.

## CRITICAL: Guardian Tests are COMPLEMENTARY, Not Replacements

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TEST HIERARCHY                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  tests/unit/        → Functional correctness (unit tests)           │
│  tests/e2e/         → End-to-end workflows                          │
│  tests/integration/ → Component integration                          │
│  tests/guardian/    → Architectural compliance (validation gate)    │
│                                                                      │
│  Guardian tests DO NOT replace unit/e2e tests!                      │
│  They are COMPLEMENTARY - different purposes.                       │
└─────────────────────────────────────────────────────────────────────┘
```

### What Guardian Tests Do:
- Validate architectural compliance (MRO, SSOT, schema integrity)
- Enforce hard structural rules
- Emit signed artifacts (pass/fail with metadata)

### What Guardian Tests Do NOT Do:
- Replace unit tests for functional correctness
- Delete files based on filename patterns (e.g., "phase1")
- Use string regex for obsolescence detection

## Obsolescence Detection: AST-Based Analysis Required

**NEVER use string regex or filename patterns to determine obsolescence.**

### ❌ WRONG: String Regex / Filename Patterns
```python
# DO NOT DO THIS
if 'phase ' in line_lower:
    issues.append("Obsolete indicator found")

# DO NOT DO THIS
if 'phase1' in filename:
    delete_file(filename)
```

### ✅ CORRECT: AST-Based Analysis
```python
def analyze_with_ast(self, file_path: Path) -> Dict:
    """Use AST to determine if file is obsolete."""
    tree = ast.parse(content)

    # Extract and verify imports
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            spec = importlib.util.find_spec(node.module)
            if spec is None:
                broken_imports.append(node.module)

    # Only mark obsolete if ALL imports are broken
    if len(broken_imports) == len(all_imports):
        return {'is_obsolete': True, 'confidence': 0.9}
```

### Obsolescence Criteria (AST-Based):
1. **ALL imports are broken** (not just some)
2. **No valid test classes/functions exist**
3. **File has syntax errors** (may be corrupted)
4. **Fuzzy matching finds renamed modules** (not deleted)

### Files Requiring Manual Review:
- Files with "phase1", "phase2" in filename → May be valid tests
- Files with some broken imports → May need import updates
- Files with no test functions → May be utility modules

## Test Directory Scanning: ALL Levels Required

Guardian tests must scan ALL levels of the tests/ hierarchy:

```
tests/                          ← Level 1: Root test files
├── test_audit_pipeline.py
├── test_meta_learning.py
├── unit/                       ← Level 2: Unit test root
│   ├── test_environment.py
│   └── agentic_core/           ← Level 3: Module root
│       ├── L0_maintenance/     ← Level 4: Layer root
│       │   └── scripts/        ← Level 5: Subfolder
│       ├── L5_safety/
│       │   └── validators/
│       └── ...
├── e2e/                        ← Level 2: E2E tests
├── integration/                ← Level 2: Integration tests
└── guardian/                   ← Level 2: Guardian tests (this folder)
```

### Implementation:
```python
def collect_test_files_all_levels(self, tests_root: Path) -> Dict[str, List[Path]]:
    """Collect test files at ALL levels of tests/ hierarchy."""
    result = {}

    # Level 1: tests/ root
    result['tests_root'] = list(tests_root.glob("test_*.py"))

    # Level 2+: Recursive subdirectories
    for subdir in tests_root.iterdir():
        if subdir.is_dir():
            result[f'tests_{subdir.name}'] = list(subdir.glob("test_*.py"))
            # Continue recursively...
```

## Design Principles

### 1. Separation of Concerns

**Guardian Tests (Compliance Gates):**
- Enforce structural and architectural "Hard Rules"
- Emit **Signed Artifacts** (Pass/Fail results with metadata)
- Verify MRO, SSOT compliance, and Schema integrity
- Block non-compliant code from execution

**Validation Agents (Validators):**
- Implement validation logic
- Perform structural checks
- Execute healing operations
- Maintain domain expertise

### 2. Call Agents, Don't Replicate

❌ **WRONG: Replicating Logic**
```python
def check_naming_violations(self, file_path):
    # Don't implement PascalCase detection here
    if file_path.stem != file_path.stem.lower():
        return ["PascalCase violation"]
```

✅ **CORRECT: Calling Agents**
```python
def check_naming_violations(self, file_path, project_root):
    # Call existing agent for validation
    agent = FileClassificationAgent(project_root)
    violations = agent.detect_naming_violations([file_path])
    return violations
```

### 3. Guardian-Specific Checks

Guardian tests should only implement checks that are:
- **Hard architectural rules** that cannot be overridden
- **Compliance verification** (MRO, SSOT, schema integrity)
- **Boundary validation** (layer hierarchy, naming conventions)
- **Final gate checks** before code execution

## Implementation Pattern

```python
class TestGuardianCompliance:
    """Guardian test following the validation gate pattern."""

    def test_architectural_compliance(self, project_root):
        """Main compliance verification."""
        violations = {}

        # 1. Call existing agents for validation
        violations.update(self.check_mro_integrity())
        violations.update(self.check_ssot_compliance())
        violations.update(self.check_naming_conventions())

        # 2. Guardian-specific hard rules
        violations.update(self.check_layer_hierarchy())
        violations.update(self.check_boundary_violations())

        # 3. Emit signed artifact (pass/fail with metadata)
        if violations:
            self.emit_failure_artifact(violations)
            pytest.fail(f"Architectural compliance failed: {len(violations)} violations")
        else:
            self.emit_success_artifact()
```

## Agent Integration Examples

### FileClassificationAgent
```python
def check_naming_violations(self, file_path, project_root):
    """Detect naming convention violations."""
    try:
        agent = FileClassificationAgent(project_root)
        return agent.detect_naming_violations([file_path])
    except ImportError:
        # Fallback to basic check if agent unavailable
        return self._basic_naming_check(file_path)
```

### LocationAgent
```python
def check_location_violations(self, file_path, project_root):
    """Detect depth and placement violations."""
    try:
        agent = LocationAgent(project_root, healing_enabled=False)
        return agent.validate_file_location(file_path)
    except ImportError:
        return []  # Skip if agent unavailable
```

### HierarchyAgent
```python
def check_hierarchy_violations(self, file_path, project_root):
    """Detect structural hierarchy violations."""
    try:
        agent = HierarchyAgent(project_root, healing_enabled=False)
        return agent.validate_file_hierarchy(file_path)
    except ImportError:
        return []  # Skip if agent unavailable
```

## Benefits of This Pattern

1. **No Logic Duplication**: Validation logic stays in agents
2. **Single Source of Truth**: Agents are the authoritative validators
3. **Maintainability**: Changes to validation logic only need to be made in agents
4. **Composability**: Guardian tests can orchestrate multiple agents
5. **Separation of Concerns**: Clear boundary between validation gate and validators
6. **Graceful Degradation**: Fallback to basic checks if agents unavailable

## Guardian-Specific Responsibilities

Guardian tests should focus on:

### 1. Hard Rule Enforcement
- MRO integrity (Method Resolution Order)
- SSOT compliance (Single Source of Truth)
- Layer hierarchy violations
- Naming convention enforcement

### 2. Boundary Validation
- Sovereign territory boundaries
- Forbidden root folder enforcement
- Gravity violations (lower layers importing higher)
- Path depth limits

### 3. Compliance Verification
- Schema integrity checks
- Blueprint reality validation
- Constitutional rule compliance
- Base agent location enforcement

### 4. Signed Artifact Emission
- Pass/fail results with metadata
- Violation reports with line numbers
- Technical debt tracking
- Compliance certificates

## Example: Architectural Compliance Gate

```python
def test_architectural_compliance_gate(self, project_root):
    """Guardian gate that enforces architectural compliance."""
    violations = {}

    # 1. Hard Rules - MRO Integrity
    mro_violations = self.check_mro_integrity()
    if mro_violations:
        violations['mro'] = mro_violations

    # 2. Hard Rules - SSOT Compliance
    ssot_violations = self.check_ssot_compliance()
    if ssot_violations:
        violations['ssot'] = ssot_violations

    # 3. Hard Rules - Layer Hierarchy
    hierarchy_violations = self.check_layer_hierarchy()
    if hierarchy_violations:
        violations['hierarchy'] = hierarchy_violations

    # 4. Emit Signed Artifact
    if violations:
        self.emit_compliance_failure(violations)
        pytest.fail(f"GUARDIAN GATE FAILED: {len(violations)} architectural violations")
    else:
        self.emit_compliance_certificate()
```

## Constitutional Rules

From the user's memory and architecture diagram:

> **Guardian tests are VALIDATION GATES that call VALIDATORS (agents).**
>
> - Maintain separation from validation code in agents
> - Be able to call agents for validation
> - Don't replicate logic already in FileClassificationAgent, LocationAgent, etc.
> - Enforce hard architectural rules that cannot be overridden
> - Emit signed artifacts (pass/fail with metadata)
> - Act as the final gate before code execution

## References

- Architecture Diagram: Guardian (Validation Gate) - Center Red Shield
- FileClassificationAgent: `agentic_core/L5_safety/validators/file_classification_agent.py`
- LocationAgent: `agentic_core/L5_safety/validators/location_agent.py`
- HierarchyAgent: `agentic_core/L5_safety/validators/hierarchy_agent.py`
- Guardian Tests: `tests/guardian/` - MRO verification, SSOT compliance, Schema checks
