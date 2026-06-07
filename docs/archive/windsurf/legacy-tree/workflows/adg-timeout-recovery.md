---
description: Automatic timeout recovery using AST dependency graph analysis
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# ADG-Based Timeout Recovery Workflow

Implements automatic timeout recovery per §5.3 using AST dependency graph analysis to isolate bottlenecks and retry with targeted scope.

## When This Triggers

AUTOMATICALLY when `TimeoutError` is raised during: test collection, test execution, dependency graph construction, file search/grep, or any query where scope can be narrowed.

## Steps

### Step 1: Detect Timeout

Catch `TimeoutError` from any query operation. Log the timeout duration and scope size.

### Step 2: Build ADG for Bottleneck Analysis

Use ADG to analyze the timed-out scope. Extract: import edges, module-level call edges, dependency depth, blocking operation locations.

### Step 3: Identify Bottleneck

Scan AST for **module-level blocking operations**: `read_text()`, `read()`, `open()`, `subprocess.run()`, `requests.get()`, `time.sleep()`, heavy computations (model loading, filesystem scans).

Only module-level nodes (not inside functions/classes) are suspects.

### Step 4: Choose Isolation Strategy

| Strategy | When to Use |
|----------|-------------|
| **A: Exclude problematic files** | Specific files have module-level blocking |
| **B: Partition by dependency depth** | Deep import chains cause cascading timeouts |
| **C: Target modified files only** | Test timeout — run only tests covering changed files |
| **D: Isolate by import independence** | Group files by independent import chains |

### Step 5: Retry with Isolated Scope

Execute query with isolated scope using same timeout. Log excluded items and isolated scope size.

### Step 6: Document Recovery

Add to evidence:

```markdown
## TIMEOUT_RECOVERY

### Initial Timeout
- Operation: <name>
- Timeout: <N>s
- Items attempted: <count>

### ADG Analysis
- Blocking operations found: <count>
- Problematic files: <list with line numbers>

### Isolation Strategy
- Strategy: <A|B|C|D>
- Isolated scope: <count> items
- Excluded: <count> items

### Recovery Result
- Retry succeeded: <yes|no>
- Duration: <seconds>
```

## Fail-Closed Rules

- If ADG cannot be built → raise original `TimeoutError`
- If no bottleneck identified → raise original `TimeoutError`
- If isolated scope is empty → raise original `TimeoutError`
- If retry times out → raise `TimeoutError` with both attempts
- **Never** silently skip work or return partial results
