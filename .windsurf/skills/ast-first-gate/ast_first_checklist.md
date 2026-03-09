# AST-First Checklist

**Quick compliance check before responding to any code investigation request.**

## Pre-Response Checklist

Before responding to user request involving code:

### 1. Request Classification

- [ ] Does request mention files, functions, classes, or modules?
- [ ] Does request ask about dependencies, imports, or relationships?
- [ ] Does request involve impact analysis or blast radius?
- [ ] Does request involve refactoring, modification, or debugging?
- [ ] Does request ask about test coverage or dead code?

**If ANY checkbox is checked → AST dependency graph is REQUIRED per §0**

### 2. Graph Status

- [ ] AST dependency graph has been built
- [ ] Graph includes all required node types
- [ ] Graph includes all required edge types
- [ ] Upstream dependencies extracted
- [ ] Downstream dependents extracted
- [ ] Test coverage edges mapped
- [ ] Cross-layer edges identified
- [ ] Cycles/boundaries checked

**If ANY checkbox is UNCHECKED → BLOCK and build graph first**

### 3. Documentation Status

- [ ] DEPENDENCY_GRAPH section created
- [ ] Graph roots documented
- [ ] Node types documented
- [ ] Edge types documented
- [ ] Upstream dependencies documented
- [ ] Downstream dependents documented
- [ ] Test surface implications documented
- [ ] Scope justification documented (if applicable)

**If ANY checkbox is UNCHECKED → Complete documentation before proceeding**

### 4. Forbidden Methods Check

- [ ] NOT using grep as primary analysis method
- [ ] NOT using ripgrep as primary analysis method
- [ ] NOT using filename searches to infer dependencies
- [ ] NOT using text pattern matching to determine relationships
- [ ] NOT making assumptions without graph proof

**If ANY checkbox is UNCHECKED → CONSTITUTIONAL VIOLATION (§3.5)**

### 5. Confidence Assessment

- [ ] Graph completeness: ___% (100% = HIGH, 90-99% = MEDIUM, <90% = LOW)
- [ ] Parse errors: ___ (0 = HIGH, 1-2 = MEDIUM, >2 = LOW)
- [ ] Confidence level: HIGH / MEDIUM / LOW

**If LOW confidence → Mark analysis as PARTIAL and report limitations**

### 6. Evidence Compliance

- [ ] DEPENDENCY_GRAPH section included in response
- [ ] Graph-backed evidence for all claims
- [ ] No high-confidence claims without graph proof
- [ ] Parse failures recorded (if any)
- [ ] Limitations explicitly stated (if any)

**If ANY checkbox is UNCHECKED → Complete before responding**

## Quick Decision Tree

```
User request received
    ↓
Does it involve code? → NO → Respond normally
    ↓ YES
    ↓
Has AST graph been built? → NO → BLOCK, build graph first (§0)
    ↓ YES
    ↓
Is graph documented? → NO → BLOCK, document DEPENDENCY_GRAPH section
    ↓ YES
    ↓
Is graph complete? → NO → Mark as PARTIAL, reduce confidence
    ↓ YES
    ↓
✅ PROCEED with graph-backed response
```

## Common Violations to Avoid

### ❌ VIOLATION 1: Responding without graph

```
USER: "What depends on file1.py?"
WRONG: "Let me search... [uses grep]"
RIGHT: "Building AST dependency graph first... [builds graph, then responds]"
```

### ❌ VIOLATION 2: Using grep as primary method

```
USER: "Find all imports of MyClass"
WRONG: grep -r "import MyClass" .
RIGHT: Build AST graph, extract import edges, then confirm with grep if needed
```

### ❌ VIOLATION 3: Assuming relationships

```
USER: "Does file2.py depend on file1.py?"
WRONG: "Probably, they're in the same directory"
RIGHT: Build graph, check for import/call edges, provide graph-backed answer
```

### ❌ VIOLATION 4: Incomplete documentation

```
WRONG: [Builds graph but doesn't document DEPENDENCY_GRAPH section]
RIGHT: [Builds graph AND documents complete DEPENDENCY_GRAPH section]
```

### ❌ VIOLATION 5: High confidence with partial graph

```
WRONG: "All dependencies identified" (when graph is 85% complete)
RIGHT: "Known dependencies include... (PARTIAL analysis, 85% complete)"
```

## Enforcement Actions

If violation detected:

```
VIOLATION: [Describe violation]
CONSTITUTIONAL REFERENCE: [§0, §3.4, §3.5, or §3.6]
REQUIRED ACTION: [Build graph, document, fail-closed, etc.]
BLOCK RESPONSE: YES/NO
```

## Example: Compliant Response

```
USER REQUEST: "What's the blast radius of changing file1.py?"

✅ CHECKLIST PASSED:
[✓] Request involves code (blast radius analysis)
[✓] AST dependency graph built
[✓] All edge types extracted
[✓] DEPENDENCY_GRAPH section documented
[✓] No forbidden methods used
[✓] Confidence: HIGH (100% completeness)
[✓] Evidence includes graph section

RESPONSE:
"Per AST dependency graph analysis:

## DEPENDENCY_GRAPH
Graph roots: [file1.py]
Downstream dependents: 5 files
  - file2.py (import edge)
  - file3.py (call edge: calls file1.function_a)
  - apps_lic/engines/control_plane.py (indirect via file2.py)
  - tests/test_file1.py (test coverage edge)
  - tests/integration/test_workflow.py (integration test edge)

Blast radius: 5 files require regression testing
Risk level: MEDIUM (2 production files, 3 test files)

[Full DEPENDENCY_GRAPH section with all details...]"
```

## Constitutional References

- **§0:** DEFAULT = DETAILED AST DEPENDENCY GRAPH
- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED
- **§3.5:** Low-signal search FORBIDDEN as primary method
- **§3.6:** Fail closed if AST parsing fails
- **§3.7:** Evidence MUST include DEPENDENCY_GRAPH section
