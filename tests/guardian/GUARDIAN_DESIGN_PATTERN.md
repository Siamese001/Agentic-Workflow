# Guardian Test Design Pattern

## Architecture Position

Guardian tests represent the **Guardian (Validation Gate)** in the center of the architecture (The Red Shield). They act as the final **Compliance Gate** that a "Proposed Fix" must pass before entering the **Symmetric Validator-Healer Pipe**.

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
