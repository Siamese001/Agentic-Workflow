# Guardian Test Design Pattern

## Architecture Position

Guardian tests are part of the **Event & Anomaly Detection Layer** in the agentic architecture. They act as **sensors** that detect anomalies and trigger alerts, positioned between policy enforcement and fix execution.

## Design Principles

### 1. Separation of Concerns

**Guardian Tests (Sensors):**
- Detect anomalies and patterns
- Orchestrate existing validation agents
- Aggregate results and flag issues
- Generate alerts and reports

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
- **Cross-cutting concerns** (not specific to one agent)
- **Meta-level detection** (detecting patterns across multiple files)
- **Temporal patterns** (obsolete/phase files, old dates)
- **Import/reference validation** (checking if referenced code exists)

## Implementation Pattern

```python
class TestGuardianDetection:
    """Guardian test following the sensor pattern."""
    
    def test_detect_anomalies(self, project_root):
        """Main detection orchestration."""
        files = self.collect_files()
        issues = {}
        
        for file in files:
            file_issues = []
            
            # 1. Call existing agents for validation
            file_issues.extend(self.check_with_file_classification_agent(file))
            file_issues.extend(self.check_with_location_agent(file))
            file_issues.extend(self.check_with_hierarchy_agent(file))
            
            # 2. Guardian-specific checks
            file_issues.extend(self.check_imports_exist(file))
            file_issues.extend(self.check_obsolete_patterns(file))
            
            if file_issues:
                issues[file] = file_issues
        
        # 3. Aggregate and report
        self.generate_report(issues)
        
        # 4. Fail if critical issues found
        if self.has_critical_issues(issues):
            pytest.fail("Critical anomalies detected")
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
5. **Separation of Concerns**: Clear boundary between detection and validation
6. **Graceful Degradation**: Fallback to basic checks if agents unavailable

## Guardian-Specific Responsibilities

Guardian tests should focus on:

### 1. Temporal Detection
- Obsolete phase/migration files
- Old date patterns in comments
- Deprecated functionality markers

### 2. Cross-File Patterns
- Duplicate files with different naming
- Missing imports across multiple files
- Broken references to non-existent code

### 3. Meta-Level Checks
- Import validation (does imported module exist?)
- File reference validation (does referenced file exist?)
- Test coverage gaps

### 4. Aggregation & Reporting
- Collect results from multiple agents
- Generate comprehensive reports
- Create deletion scripts for obsolete files
- Flag critical vs. warning-level issues

## Example: Obsolete Functionality Detection

```python
def test_detect_obsolete_tests(self, project_root):
    """Detect obsolete test files using agent orchestration."""
    test_files = self.collect_test_files()
    issues = {}
    
    for test_file in test_files:
        file_issues = []
        
        # Agent-based validation
        file_issues.extend(
            self.check_naming_violations(test_file, project_root)
        )
        file_issues.extend(
            self.check_location_violations(test_file, project_root)
        )
        
        # Guardian-specific checks
        file_issues.extend(self.check_imports_exist(test_file))
        file_issues.extend(self.check_file_references(test_file))
        file_issues.extend(self.detect_obsolete_patterns(test_file))
        
        if file_issues:
            issues[test_file] = file_issues
    
    # Generate report and fail if critical issues found
    self.report_and_fail_if_critical(issues)
```

## Constitutional Rules

From the user's memory:

> **Guardian tests are SENSORS that call VALIDATORS (agents).**
> 
> - Maintain separation from validation code in agents
> - Be able to call agents for validation
> - Don't replicate logic already in FileClassificationAgent, LocationAgent, etc.

## References

- Architecture Diagram: Event & Anomaly Detection Layer
- FileClassificationAgent: `agentic_core/L5_safety/validators/file_classification_agent.py`
- LocationAgent: `agentic_core/L5_safety/validators/location_agent.py`
- HierarchyAgent: `agentic_core/L5_safety/validators/hierarchy_agent.py`
