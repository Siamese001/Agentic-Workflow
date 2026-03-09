---
description: Automatic timeout recovery using AST dependency graph analysis
---

# ADG-Based Timeout Recovery Workflow

This workflow implements automatic timeout recovery per §9.6 using AST dependency graph analysis to isolate bottlenecks and retry with targeted scope.

## When This Workflow Triggers

AUTOMATICALLY when:
- Test collection exceeds timeout
- Test execution exceeds timeout
- Dependency graph construction exceeds timeout
- File search/grep exceeds timeout
- Any query timeout where scope can be narrowed

## Workflow Steps

### Step 1: Detect Timeout

When `TimeoutError` is raised during any query operation:

```python
try:
    result = run_full_query(items, timeout=TIMEOUT)
except TimeoutError as e:
    # Timeout detected - proceed to recovery
    logger.warning(f"Query timed out after {TIMEOUT}s")
    proceed_to_recovery = True
```

### Step 2: Build AST Dependency Graph

Use ADG to analyze the timed-out scope:

```python
from tools.dep_graph_db import build_dependency_graph

# Build ADG focused on module-level execution
adg = build_dependency_graph_for_timeout_analysis(
    scope=items,
    analysis_type='module_level_blocking'
)
```

**ADG should extract:**
- Import edges (who imports whom)
- Module-level call edges (what executes at import time)
- Dependency depth (import chain length)
- Blocking operation locations

### Step 3: Identify Bottleneck

Scan AST for module-level blocking operations:

```python
import ast
from pathlib import Path

def find_module_level_blocking_ops(file_paths):
    """Find blocking operations at module scope."""
    blocking_ops = []

    for file_path in file_paths:
        try:
            source = Path(file_path).read_text(encoding='utf-8')
            tree = ast.parse(source, filename=str(file_path))
        except Exception:
            continue

        # Analyze only module-level nodes
        for node in ast.iter_child_nodes(tree):
            # Skip function/class definitions
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                continue

            # Check module-level assignments
            if isinstance(node, ast.Assign):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        op_name = get_operation_name(child)
                        if is_blocking(op_name):
                            blocking_ops.append({
                                'file': file_path,
                                'line': node.lineno,
                                'operation': op_name
                            })

    return blocking_ops
```

**Blocking operations to detect:**
- `read_text()`, `read()`, `open()` - File I/O at module scope
- `subprocess.run()`, `Popen()` - Process execution at module scope
- `requests.get()`, `urllib.request()` - Network calls at module scope
- `time.sleep()` - Blocking delays at module scope
- Heavy computations (AST parsing, model loading, filesystem scans)

### Step 4: Choose Isolation Strategy

Based on bottleneck findings, select strategy:

**Strategy A: Exclude Problematic Files**
```python
# If specific files have module-level blocking
problematic_files = {b['file'] for b in blocking_ops}
isolated_scope = [f for f in all_files if f not in problematic_files]
```

**Strategy B: Partition by Dependency Depth**
```python
# Run shallow dependencies first, deep separately
shallow = adg.filter_by_import_depth(max_depth=2)
deep = adg.filter_by_import_depth(min_depth=3)
```

**Strategy C: Target Modified Files Only**
```python
# For test timeouts, run only tests covering modified files
modified_files = get_git_modified_files()
relevant_tests = adg.find_tests_covering_files(modified_files)
```

**Strategy D: Isolate by Import Independence**
```python
# Group files by independent import chains
independent_groups = adg.partition_by_import_independence()
for group in independent_groups:
    run_isolated_query(group, timeout=TIMEOUT)
```

### Step 5: Retry with Isolated Scope

Execute query with isolated scope:

```python
logger.info(f"Retrying with isolated scope: {len(isolated_scope)} items")
logger.info(f"Excluded: {len(excluded_items)} items")

with timeout_guard(TIMEOUT, "query (isolated)"):
    result = run_query(isolated_scope)
```

### Step 6: Document Recovery in Evidence

Add TIMEOUT_RECOVERY section to evidence:

```markdown
## TIMEOUT_RECOVERY

### Initial Timeout
- Operation: test collection
- Timeout: 60s
- Scope: tests/
- Items attempted: 150

### ADG Analysis
- Bottleneck identification method: module_level_blocking_detection
- Blocking operations found: 3
- Problematic files:
  - tests/guardian/test_v15_p8_cat_c.py:34 - read_text
  - tests/guardian/test_v15_p8_cat_d.py:29 - read_text
  - tests/guardian/test_v15_p8_cat_e.py:30 - read_text

### Isolation Strategy
- Strategy used: exclude_problematic_modules
- Isolated scope: tests/ (excluding 3 files)
- Items in isolated scope: 147
- Items excluded: 3

### Recovery Result
- Retry timeout: 60s
- Retry succeeded: yes
- Items processed: 147
- Duration: 45.2s
```

## Example: Test Collection Timeout Recovery

Complete implementation:

```python
import ast
import logging
from pathlib import Path
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

def collect_tests_with_recovery(test_dirs: List[str], timeout: int = 60):
    """Collect tests with automatic timeout recovery."""

    try:
        # Step 1: Attempt full collection
        logger.info(f"Collecting tests from {len(test_dirs)} directories...")
        with timeout_guard(timeout, "test collection"):
            return collect_all_tests(test_dirs), {'recovery': False}

    except TimeoutError as e:
        # Step 2: Build ADG and identify bottleneck
        logger.warning(f"Test collection timed out after {timeout}s")
        blocking_ops = find_module_level_blocking_ops(test_dirs)

        logger.info(f"ADG identified {len(blocking_ops)} blocking operations:")
        for op in blocking_ops:
            logger.info(f"  {op['file']}:{op['line']} - {op['operation']}")

        # Step 3: Isolate scope
        problematic = {op['file'] for op in blocking_ops}
        safe_files = [
            str(f) for d in test_dirs
            for f in Path(d).rglob("test_*.py")
            if str(f) not in problematic
        ]

        logger.info(f"Isolated scope: {len(safe_files)} safe files")
        logger.info(f"Excluded: {len(problematic)} problematic files")

        # Step 4: Retry
        with timeout_guard(timeout, "test collection (isolated)"):
            collected = collect_specific_tests(safe_files)

        # Step 5: Document recovery
        recovery_meta = {
            'recovery': True,
            'blocking_ops': blocking_ops,
            'excluded': list(problematic),
            'safe_count': len(safe_files)
        }

        return collected, recovery_meta

def find_module_level_blocking_ops(test_dirs: List[str]) -> List[Dict]:
    """Find module-level blocking operations."""
    blocking_ops = []

    for test_dir in test_dirs:
        for test_file in Path(test_dir).rglob("*.py"):
            if "__pycache__" in str(test_file):
                continue

            try:
                source = test_file.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(source)
            except Exception:
                continue

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    continue

                if isinstance(node, ast.Assign):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            op = get_call_name(child)
                            if is_blocking_op(op):
                                blocking_ops.append({
                                    'file': str(test_file),
                                    'line': node.lineno,
                                    'operation': op
                                })
                                break

    return blocking_ops

def get_call_name(call_node: ast.Call) -> str:
    """Extract call name from AST node."""
    if isinstance(call_node.func, ast.Attribute):
        return call_node.func.attr
    elif isinstance(call_node.func, ast.Name):
        return call_node.func.id
    return ''

def is_blocking_op(op_name: str) -> bool:
    """Check if operation is blocking at module scope."""
    blocking = [
        'read_text', 'read', 'open', 'subprocess', 'run',
        'Popen', 'requests', 'get', 'sleep', 'parse'
    ]
    return any(b in op_name.lower() for b in blocking)
```

## Fail-Closed Guarantees

Recovery MUST fail-closed:

```python
def safe_recovery(items, timeout, operation):
    """Recovery with fail-closed guarantees."""

    try:
        return run_with_recovery(items, timeout, operation)
    except Exception as recovery_error:
        # If recovery fails, raise with full context
        raise TimeoutError(
            f"{operation} timed out and recovery failed.\n"
            f"Original scope: {len(items)} items\n"
            f"Recovery error: {str(recovery_error)}"
        ) from recovery_error
```

**Fail-closed rules:**
- If ADG cannot be built → raise original TimeoutError
- If no bottleneck identified → raise original TimeoutError
- If isolated scope is empty → raise original TimeoutError
- If retry times out → raise TimeoutError with both attempts
- Never silently skip work or return partial results

## Integration with Existing Workflows

### With Evidence Bundle

```python
# In evidence generation
if recovery_meta.get('recovery'):
    evidence.append("## TIMEOUT_RECOVERY")
    evidence.append(f"Blocking operations: {len(recovery_meta['blocking_ops'])}")
    for op in recovery_meta['blocking_ops']:
        evidence.append(f"  - {op['file']}:{op['line']} - {op['operation']}")
```

### With Test Rigor Enforcement

```python
# Test execution with recovery
def run_tests_with_recovery(test_files, timeout=300):
    try:
        return run_all_tests(test_files, timeout)
    except TimeoutError:
        # Use ADG to isolate slow tests
        adg = build_test_dependency_graph(test_files)
        isolated = adg.exclude_heavy_dependencies()
        return run_all_tests(isolated, timeout)
```

## Quick Command Reference

### Find Module-Level Blocking Operations

```bash
python -c "
import ast
from pathlib import Path

for f in Path('tests').rglob('*.py'):
    if '__pycache__' in str(f): continue
    try:
        tree = ast.parse(f.read_text(encoding='utf-8'))
    except: continue

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)): continue
        if isinstance(node, ast.Assign):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    name = func.attr if hasattr(func, 'attr') else getattr(func, 'id', '')
                    if name in ['read_text', 'read', 'subprocess', 'run']:
                        print(f'{f}:{node.lineno} - {name}')
"
```

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9.6
- ADG Timeout Recovery Skill: `.windsurf/skills/timeout-progress-enforcement/adg_timeout_recovery.md`
- AST Dependency Graph: §0, §3.4
- Timeout Requirements: §9.1
- Evidence Contract: §2
