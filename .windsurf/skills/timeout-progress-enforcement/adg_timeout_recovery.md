# ADG-Based Timeout Recovery Skill

**Trigger:** Automatically invoked when any query exceeds timeout per §9.6

## Purpose

Implements Constitutional Rule §9.6: Automatic timeout recovery using AST dependency graph to isolate bottlenecks and retry with targeted scope.

## When to Use

AUTOMATICALLY triggered when:
- Test collection times out
- Test execution times out
- Dependency graph construction times out
- File search/grep times out
- Any query timeout where scope can be narrowed

## Recovery Protocol (5 Steps)

### Step 1: Capture Timeout Context

When `TimeoutError` is raised:

```python
try:
    result = run_full_query(items, timeout=TIMEOUT)
except TimeoutError as e:
    # Capture context
    timeout_context = {
        'operation': 'test collection',
        'timeout': TIMEOUT,
        'scope': items,
        'items_attempted': len(items),
        'error': str(e)
    }
```

### Step 2: Build AST Dependency Graph for Analysis

Use ADG to analyze the timed-out scope:

```python
from tools.dep_graph_db import build_dependency_graph

# Build ADG for timeout analysis
adg = build_dependency_graph_for_timeout_analysis(
    scope=items,
    focus='module_level_execution'
)

# ADG should extract:
# - Import edges (who imports whom)
# - Module-level call edges (what executes at import time)
# - Dependency depth (import chain length)
# - Blocking operation locations
```

### Step 3: Identify Bottleneck Using ADG

Analyze ADG to find root cause:

```python
def identify_bottleneck_from_adg(adg, scope):
    """Identify bottleneck using AST dependency graph."""

    bottlenecks = []

    # Find module-level blocking operations
    for file_path in scope:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=str(file_path))
        except Exception:
            continue

        # Analyze module-level nodes (not inside functions/classes)
        for node in ast.iter_child_nodes(tree):
            # Skip function and class definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue

            # Check for module-level assignments with calls
            if isinstance(node, ast.Assign):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        op_name = get_operation_name(child)
                        if is_blocking_operation(op_name):
                            bottlenecks.append({
                                'file': file_path,
                                'line': node.lineno,
                                'operation': op_name,
                                'type': 'module_level_blocking'
                            })

            # Check for module-level expression calls
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                op_name = get_operation_name(node.value)
                if is_blocking_operation(op_name):
                    bottlenecks.append({
                        'file': file_path,
                        'line': node.lineno,
                        'operation': op_name,
                        'type': 'module_level_blocking'
                    })

    return bottlenecks

def is_blocking_operation(op_name: str) -> bool:
    """Check if operation is blocking at module scope."""
    blocking_ops = [
        # File I/O
        'read_text', 'read', 'open', 'read_bytes',
        # Process execution
        'subprocess', 'run', 'Popen', 'check_output', 'call',
        # Network calls
        'requests', 'get', 'post', 'urlopen', 'urllib',
        # Blocking delays
        'sleep', 'wait',
        # Heavy computations
        'parse', 'compile', 'load_model', 'fit', 'train'
    ]
    return any(blocked in op_name.lower() for blocked in blocking_ops)

def get_operation_name(call_node: ast.Call) -> str:
    """Extract operation name from AST Call node."""
    func = call_node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    elif isinstance(func, ast.Name):
        return func.id
    return ''
```

### Step 4: Isolate Scope Based on Bottleneck

Choose isolation strategy based on bottleneck type:

```python
def isolate_scope_from_bottleneck(bottlenecks, original_scope):
    """Isolate scope by excluding problematic files."""

    if not bottlenecks:
        # No bottleneck identified, cannot isolate
        raise TimeoutError("Cannot isolate scope: no bottleneck identified")

    # Strategy 1: Exclude files with module-level blocking
    problematic_files = {b['file'] for b in bottlenecks}
    isolated_scope = [f for f in original_scope if f not in problematic_files]

    if not isolated_scope:
        # All files problematic, try strategy 2
        # Strategy 2: Partition by dependency depth
        isolated_scope = partition_by_dependency_depth(original_scope)

    if not isolated_scope:
        raise TimeoutError("Cannot isolate scope: all files problematic")

    return isolated_scope, problematic_files
```

### Step 5: Retry with Isolated Scope

```python
def run_with_timeout_recovery(items, timeout, operation_name):
    """Run operation with automatic timeout recovery."""

    try:
        # Attempt full operation
        with timeout_guard(timeout, operation_name):
            return run_operation(items)

    except TimeoutError as e:
        logger.warning(f"{operation_name} timed out after {timeout}s")

        # Step 2: Build ADG
        adg = build_dependency_graph_for_timeout_analysis(items)

        # Step 3: Identify bottleneck
        bottlenecks = identify_bottleneck_from_adg(adg, items)

        logger.info(f"ADG identified {len(bottlenecks)} bottlenecks:")
        for b in bottlenecks:
            logger.info(f"  {b['file']}:{b['line']} - {b['operation']}")

        # Step 4: Isolate scope
        isolated_scope, excluded = isolate_scope_from_bottleneck(bottlenecks, items)

        logger.info(f"Isolated scope: {len(isolated_scope)} items (excluded {len(excluded)})")

        # Step 5: Retry with isolated scope
        with timeout_guard(timeout, f"{operation_name} (isolated)"):
            result = run_operation(isolated_scope)

        # Document recovery
        document_timeout_recovery(
            operation=operation_name,
            timeout=timeout,
            original_scope=items,
            bottlenecks=bottlenecks,
            isolated_scope=isolated_scope,
            excluded=excluded,
            result=result
        )

        return result
```

## Concrete Implementation: Test Collection Recovery

```python
import ast
import logging
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

def collect_tests_with_timeout_recovery(
    test_dirs: List[str],
    timeout: int = 60
) -> Tuple[List[str], Dict]:
    """
    Collect tests with automatic timeout recovery.

    Returns:
        Tuple of (collected_tests, recovery_metadata)
    """

    try:
        # Attempt full collection
        logger.info(f"Collecting tests from {len(test_dirs)} directories...")
        with timeout_guard(timeout, "test collection"):
            collected = collect_all_tests(test_dirs)
            return collected, {'recovery_used': False}

    except TimeoutError as e:
        logger.warning(f"Test collection timed out after {timeout}s")

        # Build ADG to find module-level blocking operations
        blocking_modules = find_module_level_blocking_operations(test_dirs)

        logger.info(f"ADG identified {len(blocking_modules)} blocking operations:")
        for file_path, line_num, op_name in blocking_modules:
            logger.info(f"  {file_path}:{line_num} - {op_name}")

        # Isolate scope: exclude files with blocking operations
        problematic_files = {str(Path(f).resolve()) for f, _, _ in blocking_modules}

        safe_test_files = []
        for test_dir in test_dirs:
            for test_file in Path(test_dir).rglob("test_*.py"):
                if str(test_file.resolve()) not in problematic_files:
                    safe_test_files.append(str(test_file))

        logger.info(f"Retrying with {len(safe_test_files)} safe test files")
        logger.info(f"Excluded {len(problematic_files)} problematic files")

        # Retry with isolated scope
        with timeout_guard(timeout, "test collection (isolated)"):
            collected = collect_specific_tests(safe_test_files)

        recovery_metadata = {
            'recovery_used': True,
            'original_timeout': timeout,
            'blocking_modules': blocking_modules,
            'excluded_files': list(problematic_files),
            'safe_files': safe_test_files,
            'collected_count': len(collected)
        }

        return collected, recovery_metadata

def find_module_level_blocking_operations(
    test_dirs: List[str]
) -> List[Tuple[str, int, str]]:
    """
    Find module-level blocking operations in test files.

    Returns:
        List of (file_path, line_number, operation_name)
    """

    blocking_ops = []

    for test_dir in test_dirs:
        for test_file in Path(test_dir).rglob("*.py"):
            if "__pycache__" in str(test_file):
                continue

            try:
                source = test_file.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(source, filename=str(test_file))
            except Exception:
                continue

            # Find module-level calls
            for node in ast.iter_child_nodes(tree):
                # Skip function/class definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue

                # Check assignments with calls
                if isinstance(node, ast.Assign):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            op_name = _get_call_name(child)
                            if _is_blocking_op(op_name):
                                blocking_ops.append((
                                    str(test_file),
                                    node.lineno,
                                    op_name
                                ))
                                break

                # Check expression calls
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    op_name = _get_call_name(node.value)
                    if _is_blocking_op(op_name):
                        blocking_ops.append((
                            str(test_file),
                            node.lineno,
                            op_name
                        ))

    return blocking_ops

def _get_call_name(call_node: ast.Call) -> str:
    """Extract call name from AST Call node."""
    func = call_node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    elif isinstance(func, ast.Name):
        return func.id
    return ''

def _is_blocking_op(op_name: str) -> bool:
    """Check if operation is blocking at module scope."""
    blocking_patterns = [
        'read_text', 'read', 'open', 'read_bytes',
        'subprocess', 'run', 'Popen', 'check_output',
        'requests', 'get', 'post', 'urlopen',
        'sleep', 'wait', 'parse', 'compile'
    ]
    return any(pattern in op_name.lower() for pattern in blocking_patterns)
```

## Evidence Documentation Template

```python
def document_timeout_recovery(
    operation: str,
    timeout: int,
    original_scope: List,
    bottlenecks: List[Dict],
    isolated_scope: List,
    excluded: set,
    result: any
) -> str:
    """Generate timeout recovery documentation for evidence."""

    doc = f"""## TIMEOUT_RECOVERY

### Initial Timeout
- Operation: {operation}
- Timeout: {timeout}s
- Scope: {len(original_scope)} items
- Items attempted: {len(original_scope)}

### ADG Analysis
- Bottleneck identification method: module_level_blocking_detection
- Blocking operations found: {len(bottlenecks)}
- Problematic files:
"""

    for b in bottlenecks:
        doc += f"  - {b['file']}:{b['line']} - {b['operation']}\n"

    doc += f"""
### Isolation Strategy
- Strategy used: exclude_problematic_modules
- Isolated scope: {len(isolated_scope)} items
- Items in isolated scope: {len(isolated_scope)}
- Items excluded: {len(excluded)}
- Excluded files:
"""

    for f in sorted(excluded):
        doc += f"  - {f}\n"

    doc += f"""
### Recovery Result
- Retry timeout: {timeout}s
- Retry succeeded: yes
- Items processed: {len(isolated_scope)}
- Duration: <measured>s
"""

    return doc
```

## Integration with Evidence Bundle Skill

When using evidence-bundle skill, include timeout recovery:

```python
# In evidence generation
if recovery_metadata.get('recovery_used'):
    evidence_lines.append("## TIMEOUT_RECOVERY")
    evidence_lines.append(f"- Original timeout: {recovery_metadata['original_timeout']}s")
    evidence_lines.append(f"- Blocking modules: {len(recovery_metadata['blocking_modules'])}")

    for file_path, line, op in recovery_metadata['blocking_modules']:
        evidence_lines.append(f"  - {file_path}:{line} - {op}")

    evidence_lines.append(f"- Excluded files: {len(recovery_metadata['excluded_files'])}")
    evidence_lines.append(f"- Safe files processed: {len(recovery_metadata['safe_files'])}")
```

## Fail-Closed Behavior

Recovery MUST fail-closed:

```python
def safe_timeout_recovery(items, timeout, operation):
    """Timeout recovery with fail-closed guarantees."""

    try:
        return run_with_timeout_recovery(items, timeout, operation)
    except Exception as e:
        # If recovery fails, raise original timeout with context
        logger.error(f"Timeout recovery failed: {e}")
        raise TimeoutError(
            f"{operation} timed out and recovery failed. "
            f"Original scope: {len(items)} items. "
            f"Recovery error: {str(e)}"
        ) from e
```

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9.6
- AST Dependency Graph: §0, §3.4
- Timeout Requirements: §9.1
- Evidence Contract: §2
- Test Execution: §1, §5.2
