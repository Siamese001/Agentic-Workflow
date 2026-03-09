# Timeout & Progress Enforcement Skill

**Trigger:** Use before any query, search, analysis, or long-running operation to ensure timeout and progress reporting compliance per §9.

## Purpose

Enforces Constitutional Rule §9: All queries require explicit timeouts and progress reporting (% completion).

## When to Use

- Before building AST dependency graphs
- Before running test collection or execution
- Before file searches or grep operations
- Before evidence generation commands
- Before any operation expected to take >5 seconds
- When implementing new query or analysis functions

## Enforcement Protocol

### Step 1: Pre-Operation Timeout Declaration

Before executing any query or long-running operation:

1. **Identify operation type** and select timeout range:
   - Fast queries (grep, file reads, simple AST): 5-30s
   - Medium queries (dependency graph, test collection): 30-120s
   - Heavy queries (full repo analysis, multi-file refactor): 120-600s
   - External API calls: 10-60s with retry budget

2. **Declare timeout explicitly** in code:
   ```python
   TIMEOUT_SECONDS = 60  # Explicit, not default
   ```

3. **Implement fail-closed timeout guard**:
   ```python
   with timeout_guard(TIMEOUT_SECONDS, "operation_name"):
       # operation code
   ```

### Step 2: Progress Reporting Setup

For operations >5 seconds expected duration:

1. **Calculate total work units** (files, tests, items, etc.)

2. **Initialize progress bar**:
   ```python
   from tqdm import tqdm

   with tqdm(total=total_items, desc="Operation", unit="item") as pbar:
       for item in items:
           # process item
           pbar.update(1)
   ```

3. **Ensure incremental updates**:
   - Every 5s for operations >30s
   - Every 10s for operations >120s
   - On phase transitions
   - On completion (100%)

### Step 3: Evidence Documentation

In evidence files, document:

```markdown
## TIMEOUT_CONFIGURATION

- Operation: <operation_name>
- Timeout: <seconds>s
- Timeout triggered: <yes/no>
- Progress reporting: <enabled/disabled>
- Total items: <count>
- Completed items: <count>
- Duration: <actual_seconds>s
```

### Step 4: Validation Checklist

Before committing code with queries:

- [ ] All queries have explicit timeout parameters
- [ ] No infinite loops without termination conditions
- [ ] No blocking operations without timeout guards
- [ ] Timeout failures raise exceptions (fail-closed)
- [ ] Operations >5s have progress bars
- [ ] Progress shows percentage completion (0-100%)
- [ ] Progress updates occur at required intervals
- [ ] Evidence documents timeout configuration

## Hard Failures

The following are CONSTITUTIONAL VIOLATIONS:

❌ Query without timeout parameter
❌ Infinite loop without termination condition
❌ Silent timeout handling (must raise/log)
❌ Long operation (>5s) without progress reporting
❌ Progress bar without percentage completion
❌ Evidence missing timeout documentation

## Code Patterns

### Pattern 1: Timeout Guard (Unix/Linux)

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout_guard(seconds: int, operation: str):
    """Context manager for operation timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"{operation} exceeded {seconds}s timeout")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
with timeout_guard(30, "AST parsing"):
    result = parse_ast_tree(file_path)
```

### Pattern 2: Timeout Guard (Cross-platform)

```python
import threading
from contextlib import contextmanager

@contextmanager
def timeout_guard(seconds: int, operation: str):
    """Cross-platform timeout guard."""
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = yield
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=seconds)

    if thread.is_alive():
        raise TimeoutError(f"{operation} exceeded {seconds}s timeout")

    if exception[0]:
        raise exception[0]

    return result[0]
```

### Pattern 3: Progress Bar with tqdm

```python
from tqdm import tqdm

def process_files_with_progress(file_paths: list[str]) -> dict:
    """Process files with progress reporting."""
    results = {}

    with tqdm(total=len(file_paths), desc="Processing files", unit="file") as pbar:
        for file_path in file_paths:
            results[file_path] = process_single_file(file_path)
            pbar.update(1)

    return results
```

### Pattern 4: Combined Timeout + Progress

```python
from tqdm import tqdm
import signal
from contextlib import contextmanager

def analyze_with_timeout_and_progress(items: list, timeout: int) -> list:
    """Analyze items with both timeout and progress reporting."""
    results = []

    with timeout_guard(timeout, "batch analysis"):
        with tqdm(total=len(items), desc="Analyzing", unit="item") as pbar:
            for item in items:
                result = analyze_item(item)
                results.append(result)
                pbar.update(1)

    return results
```

## Integration Points

### AST Dependency Graph Construction (§0, §3.4)

```python
def build_dependency_graph(root_paths: list[str]) -> DependencyGraph:
    """Build AST dependency graph with timeout and progress."""
    TIMEOUT_SECONDS = 120  # Medium query

    with timeout_guard(TIMEOUT_SECONDS, "dependency graph construction"):
        graph = DependencyGraph()

        with tqdm(total=len(root_paths), desc="Parsing files", unit="file") as pbar:
            for path in root_paths:
                graph.add_file(path)
                pbar.update(1)

        return graph
```

### Test Collection (§1, §5.2)

```python
def collect_tests_with_timeout(test_dirs: list[str]) -> list:
    """Collect tests with timeout and progress."""
    TIMEOUT_SECONDS = 60  # Medium query

    with timeout_guard(TIMEOUT_SECONDS, "test collection"):
        collected = []

        with tqdm(total=len(test_dirs), desc="Collecting tests", unit="dir") as pbar:
            for test_dir in test_dirs:
                collected.extend(collect_from_dir(test_dir))
                pbar.update(1)

        return collected
```

### Evidence Generation (§2)

```python
def generate_evidence_with_progress(commands: list[str]) -> str:
    """Generate evidence with command execution progress."""
    evidence_lines = []

    with tqdm(total=len(commands), desc="Executing commands", unit="cmd") as pbar:
        for cmd in commands:
            # Each command has its own timeout
            with timeout_guard(30, f"command: {cmd}"):
                output = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30  # subprocess-level timeout
                )
                evidence_lines.append(output.stdout)
                pbar.update(1)

    return "\n".join(evidence_lines)
```

## Fail-Closed Behavior

When timeout is exceeded:

1. **Raise TimeoutError** (do not silently continue)
2. **Log timeout details** (operation, duration, expected timeout)
3. **Document in evidence** (timeout section)
4. **Do NOT fall back** to unbounded operation
5. **Do NOT retry** without explicit user approval

## CI Validation

CI gates MUST verify:

```python
def validate_timeout_compliance(code_file: str) -> list[str]:
    """Validate timeout compliance in code."""
    violations = []

    # Check for queries without timeouts
    if has_query_without_timeout(code_file):
        violations.append(f"{code_file}: Query without timeout")

    # Check for long operations without progress
    if has_long_op_without_progress(code_file):
        violations.append(f"{code_file}: Long operation without progress")

    return violations
```

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9
- AST Graph Construction: §0, §3.4
- Test Execution: §1, §5.2
- Evidence Generation: §2
