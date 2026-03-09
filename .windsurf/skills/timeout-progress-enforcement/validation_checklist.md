# Timeout & Progress Validation Checklist

## Pre-Commit Validation

Before committing any code with queries or long-running operations:

### Timeout Validation

- [ ] **All queries have explicit timeout parameters**
  - Check: Every query/search/analysis function has a timeout argument or constant
  - Violation: Query without timeout parameter
  - Fix: Add timeout parameter with appropriate value from §9.1 ranges

- [ ] **No infinite loops without termination conditions**
  - Check: All while loops have break conditions or iteration limits
  - Violation: `while True:` without timeout or break condition
  - Fix: Add timeout guard or maximum iteration count

- [ ] **No blocking operations without timeout guards**
  - Check: All blocking I/O, network calls, subprocess calls have timeouts
  - Violation: `subprocess.run()` without timeout parameter
  - Fix: Add `timeout=<seconds>` parameter

- [ ] **Timeout failures raise exceptions (fail-closed)**
  - Check: Timeout handlers raise TimeoutError, not return None or continue
  - Violation: Silent timeout handling with `pass` or `continue`
  - Fix: Raise TimeoutError with descriptive message

- [ ] **Timeout values within acceptable ranges**
  - Check: Timeout values match §9.1 ranges for operation type
  - Violation: 1000s timeout for simple grep operation
  - Fix: Use appropriate timeout from TimeoutConfig

### Progress Reporting Validation

- [ ] **Operations >5s have progress bars**
  - Check: Any operation expected to take >5s has tqdm or equivalent
  - Violation: Long-running loop without progress reporting
  - Fix: Wrap with `tqdm()` or ProgressReporter

- [ ] **Progress shows percentage completion (0-100%)**
  - Check: Progress bar displays percentage or fraction
  - Violation: Progress bar without percentage display
  - Fix: Use `bar_format` with `{percentage:3.0f}%`

- [ ] **Progress updates occur at required intervals**
  - Check: Updates every 5s for ops >30s, every 10s for ops >120s
  - Violation: Progress bar updated only at start/end
  - Fix: Add incremental `pbar.update(1)` calls

- [ ] **Progress bar has descriptive operation name**
  - Check: `desc` parameter is meaningful
  - Violation: `desc="Processing"` without context
  - Fix: Use specific description like "Parsing AST files"

### Evidence Documentation Validation

- [ ] **Evidence includes TIMEOUT_CONFIGURATION section**
  - Check: Evidence file has `## TIMEOUT_CONFIGURATION` section
  - Violation: Evidence missing timeout documentation
  - Fix: Add timeout configuration section with all required fields

- [ ] **Evidence includes PROGRESS_REPORTING section**
  - Check: Evidence file has `## PROGRESS_REPORTING` section
  - Violation: Evidence missing progress documentation
  - Fix: Add progress reporting section with completion metrics

- [ ] **Timeout values documented**
  - Check: Evidence lists timeout value for each operation
  - Violation: Missing timeout value in evidence
  - Fix: Document timeout used for each command/operation

- [ ] **Timeout violations documented**
  - Check: If timeout occurred, it's documented in evidence
  - Violation: Timeout occurred but not recorded
  - Fix: Add timeout violation details to evidence

## Code Review Checklist

### Pattern Detection

#### ❌ Anti-Pattern: Query without timeout

```python
# VIOLATION
result = subprocess.run(["grep", "-r", "pattern", "."])
```

#### ✅ Correct Pattern: Query with timeout

```python
# COMPLIANT
result = subprocess.run(
    ["grep", "-r", "pattern", "."],
    timeout=15,  # Fast query timeout
    capture_output=True,
    text=True
)
```

#### ❌ Anti-Pattern: Infinite loop without timeout

```python
# VIOLATION
while not condition_met():
    process_item()
    time.sleep(1)
```

#### ✅ Correct Pattern: Loop with timeout guard

```python
# COMPLIANT
with timeout_guard(60, "waiting for condition"):
    while not condition_met():
        process_item()
        time.sleep(1)
```

#### ❌ Anti-Pattern: Long operation without progress

```python
# VIOLATION
for file in large_file_list:
    process_file(file)
```

#### ✅ Correct Pattern: Long operation with progress

```python
# COMPLIANT
with tqdm(total=len(large_file_list), desc="Processing files", unit="file") as pbar:
    for file in large_file_list:
        process_file(file)
        pbar.update(1)
```

#### ❌ Anti-Pattern: Silent timeout handling

```python
# VIOLATION
try:
    result = operation_with_timeout(30)
except TimeoutError:
    pass  # Silent failure
```

#### ✅ Correct Pattern: Fail-closed timeout handling

```python
# COMPLIANT
try:
    result = operation_with_timeout(30)
except TimeoutError as e:
    logger.error(f"Operation timed out: {e}")
    raise  # Re-raise, fail-closed
```

## Automated Validation Script

```python
import ast
import re
from pathlib import Path

def validate_timeout_compliance(file_path: str) -> list[str]:
    """Validate timeout and progress compliance in Python file."""
    violations = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for subprocess.run without timeout
    if re.search(r'subprocess\.run\([^)]*\)', content):
        if not re.search(r'timeout\s*=', content):
            violations.append(f"{file_path}: subprocess.run without timeout parameter")

    # Check for while True without timeout guard
    if re.search(r'while\s+True\s*:', content):
        # Look for timeout_guard in context
        if not re.search(r'with\s+timeout_guard', content):
            violations.append(f"{file_path}: while True without timeout guard")

    # Check for long loops without progress
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            # Check if loop body is substantial (>10 lines)
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                loop_length = node.end_lineno - node.lineno
                if loop_length > 10:
                    # Check for tqdm or progress reporting
                    loop_content = content.split('\n')[node.lineno-1:node.end_lineno]
                    if not any('tqdm' in line or 'progress' in line.lower() for line in loop_content):
                        violations.append(
                            f"{file_path}:{node.lineno}: Long loop without progress reporting"
                        )

    return violations

def validate_evidence_compliance(evidence_path: str) -> list[str]:
    """Validate evidence file has required timeout/progress sections."""
    violations = []

    with open(evidence_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for TIMEOUT_CONFIGURATION section
    if '## TIMEOUT_CONFIGURATION' not in content:
        violations.append(f"{evidence_path}: Missing TIMEOUT_CONFIGURATION section")

    # Check for PROGRESS_REPORTING section
    if '## PROGRESS_REPORTING' not in content:
        violations.append(f"{evidence_path}: Missing PROGRESS_REPORTING section")

    # Check for timeout values
    if not re.search(r'Timeout:\s*\d+s', content):
        violations.append(f"{evidence_path}: Missing timeout value documentation")

    # Check for completion percentage
    if not re.search(r'Completion:\s*\d+\.?\d*%', content):
        violations.append(f"{evidence_path}: Missing completion percentage")

    return violations

def run_full_validation(repo_path: str) -> dict:
    """Run full timeout/progress validation on repository."""

    all_violations = {
        "code": [],
        "evidence": []
    }

    # Validate Python files
    for py_file in Path(repo_path).rglob("*.py"):
        if ".git" not in str(py_file) and "__pycache__" not in str(py_file):
            violations = validate_timeout_compliance(str(py_file))
            all_violations["code"].extend(violations)

    # Validate evidence files
    evidence_dir = Path(repo_path) / "docs" / "reports" / "plans"
    if evidence_dir.exists():
        for evidence_file in evidence_dir.glob("*.md"):
            if "EVIDENCE_" in evidence_file.name:
                violations = validate_evidence_compliance(str(evidence_file))
                all_violations["evidence"].extend(violations)

    return all_violations
```

## CI Gate Integration

```python
# ops_scripts/ci/validate_timeout_progress.py

def ci_timeout_progress_gate() -> int:
    """CI gate for timeout and progress compliance."""

    violations = run_full_validation(".")

    if violations["code"] or violations["evidence"]:
        print("❌ TIMEOUT/PROGRESS COMPLIANCE VIOLATIONS")
        print("\nCode violations:")
        for v in violations["code"]:
            print(f"  - {v}")

        print("\nEvidence violations:")
        for v in violations["evidence"]:
            print(f"  - {v}")

        return 1  # Fail CI

    print("✅ All timeout and progress requirements met")
    return 0  # Pass CI

if __name__ == "__main__":
    exit(ci_timeout_progress_gate())
```

## Manual Review Checklist

### For Each Query/Operation

1. **Identify operation type**
   - [ ] Fast query (5-30s)
   - [ ] Medium query (30-120s)
   - [ ] Heavy query (120-600s)
   - [ ] External API (10-60s)

2. **Verify timeout**
   - [ ] Timeout parameter exists
   - [ ] Timeout value appropriate for operation type
   - [ ] Timeout failure raises exception

3. **Verify progress (if >5s expected)**
   - [ ] Progress bar initialized with total
   - [ ] Progress bar has descriptive name
   - [ ] Progress updates incrementally
   - [ ] Progress shows percentage

4. **Verify evidence**
   - [ ] TIMEOUT_CONFIGURATION section present
   - [ ] PROGRESS_REPORTING section present
   - [ ] Timeout value documented
   - [ ] Completion percentage documented

## Quick Reference

### Required Sections in Evidence

```markdown
## TIMEOUT_CONFIGURATION

- Operation: <name>
- Timeout: <seconds>s
- Timeout triggered: <yes/no>
- Progress reporting: <enabled/disabled>
- Total items: <count>
- Completed items: <count>
- Duration: <seconds>s

## PROGRESS_REPORTING

- Operation: <name>
- Total items: <count>
- Completed items: <count>
- Completion: <percentage>%
- Duration: <seconds>s
- Rate: <items/sec> items/sec
```

### Timeout Ranges Quick Reference

| Operation Type | Timeout Range | Example |
|---------------|---------------|---------|
| Fast queries | 5-30s | grep, file read, single AST parse |
| Medium queries | 30-120s | dependency graph, test collection |
| Heavy queries | 120-600s | full repo analysis, refactor plan |
| External API | 10-60s | HTTP requests, API calls |

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9
- Timeout patterns: `timeout_patterns.md`
- Progress patterns: `progress_patterns.md`
- Main skill: `skill.md`
