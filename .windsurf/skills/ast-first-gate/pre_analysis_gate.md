# Pre-Analysis Gate

**MANDATORY BLOCKER before any code investigation per §0 DEFAULT ANALYSIS MODE.**

## Constitutional Requirement

**DEFAULT = DETAILED AST DEPENDENCY GRAPH**

This gate BLOCKS all code investigation work until AST dependency graph is built.

## Gate Protocol

### Step 1: Detect Code Investigation Request

Check if user request involves:

```
CODE_INVESTIGATION_TRIGGERS:
✓ Mentions specific files, functions, classes, modules
✓ Asks "what uses", "what depends on", "impact of", "blast radius"
✓ Requests refactor, modify, analyze, investigate, debug, trace
✓ Inquires about test coverage, dead code, duplicates, boundaries
✓ Asks about architecture, layers, dependencies, imports
✓ Requests scope determination or file selection
```

If ANY trigger matches → PROCEED TO STEP 2

If NO triggers match → SKIP GATE (not a code investigation request)

### Step 2: BLOCK Until Graph Built

**DO NOT PROCEED** with user request until dependency graph is built.

```
GATE STATUS: 🔒 BLOCKED

REASON: §0 DEFAULT ANALYSIS MODE requires AST dependency graph FIRST

REQUIRED ACTIONS:
1. Invoke dependency-graph-analysis skill
2. Build AST dependency graph per graph_construction_protocol.md
3. Extract all required edge types
4. Document in DEPENDENCY_GRAPH section
5. Validate graph completeness

FORBIDDEN ACTIONS:
❌ Responding to user without building graph first
❌ Using grep/ripgrep to answer user question
❌ Using filename searches to determine scope
❌ Making assumptions about dependencies without graph
❌ Claiming "no dependencies" without graph proof
```

### Step 3: Build Dependency Graph

Follow `dependency-graph-analysis/graph_construction_protocol.md`:

```
GRAPH_CONSTRUCTION_CHECKLIST:
[ ] Define graph roots (files mentioned in user request)
[ ] Specify required node types (modules, classes, functions, symbols)
[ ] Specify required edge types (imports, calls, inheritance, registry, tests)
[ ] Build graph using AST parsing
[ ] Extract upstream dependencies
[ ] Extract downstream dependents
[ ] Extract call edges
[ ] Extract inheritance edges
[ ] Extract registry/factory edges
[ ] Extract test coverage edges
[ ] Detect cross-layer edges
[ ] Detect cycles and SCCs
[ ] Validate boundary compliance
[ ] Document graph metadata
[ ] Record any parse failures (fail-closed discipline)
```

### Step 4: Document DEPENDENCY_GRAPH Section

Create DEPENDENCY_GRAPH section per `evidence-bundle/evidence_template.md`:

```
## DEPENDENCY_GRAPH

### Graph Roots
[List files from user request]

### Node Types Included
[List all node types analyzed]

### Edge Types Analyzed
[List all edge types with counts]

### Impacted Nodes
[Total count and list]

### Upstream Dependencies
[What the files depend on]

### Downstream Dependents
[What depends on the files]

### Cross-Layer Edges
[Any layer boundary crossings]

### Cycle/SCC Findings
[Any circular dependencies]

### Boundary Violations
[Any architecture violations]

### Test Surface Implications
[Test coverage via graph edges]

### Scope Justification
[Graph evidence for each file]
```

### Step 5: Validate Graph Completeness

Check graph quality:

```
GRAPH_VALIDATION:
[ ] All graph roots successfully parsed
[ ] All required edge types extracted
[ ] Upstream dependencies complete
[ ] Downstream dependents complete
[ ] Test coverage edges mapped
[ ] Parse errors recorded (if any)
[ ] Completeness percentage calculated
[ ] Confidence level assessed

COMPLETENESS LEVELS:
- 100%: All files parsed, all edges extracted → HIGH confidence
- 90-99%: Minor parse failures, mostly complete → MEDIUM confidence
- <90%: Significant parse failures → LOW confidence, mark as PARTIAL
```

### Step 6: Gate Decision

```
IF graph_built AND graph_documented AND graph_validated:
    GATE STATUS: ✅ OPEN
    PROCEED with user request using graph-backed evidence
ELSE:
    GATE STATUS: 🔒 BLOCKED
    REPORT: "Cannot proceed - dependency graph required per §0"
    PROVIDE: Exact reason for block (parse failures, missing edges, etc.)
    RECOMMEND: Remediation steps
```

## Fail-Closed Behavior

If graph construction fails:

```
PARSE_FAILURES_DETECTED:
❌ Cannot build complete dependency graph
❌ Parse errors in: [list files]

GATE DECISION: 🔒 BLOCKED (fail-closed per §3.6)

FORBIDDEN:
- Proceeding with incomplete graph
- Silently falling back to grep/regex
- Making high-confidence claims with partial graph

REQUIRED:
- Record exact parse errors
- Mark analysis as PARTIAL
- Reduce confidence level to LOW
- Report limitation explicitly to user
- Offer remediation path
```

## Example: Gate in Action

```
USER REQUEST: "What files depend on agentic_core/L5_safety/validators/new_validator.py?"

GATE TRIGGERED: ✅ (user asks "what depends on")

GATE STATUS: 🔒 BLOCKED (graph not yet built)

ACTIONS TAKEN:
1. Invoke dependency-graph-analysis skill
2. Build AST dependency graph with root: new_validator.py
3. Extract downstream dependents via import edges and call edges
4. Document in DEPENDENCY_GRAPH section
5. Validate graph completeness: 100%, HIGH confidence

DEPENDENCY_GRAPH:
Graph roots: [agentic_core/L5_safety/validators/new_validator.py]
Downstream dependents:
  - agentic_core/L0_routing/scripts/execute_ssot.py (import edge)
  - agentic_core/L5_safety/enforcement/existing_enforcer.py (call edge)
  - tests/unit/L5_safety/test_new_validator.py (test coverage edge)
Total: 3 downstream dependents

GATE STATUS: ✅ OPEN (graph built and documented)

RESPONSE TO USER:
"Per AST dependency graph analysis, 3 files depend on new_validator.py:
1. execute_ssot.py (imports new_validator)
2. existing_enforcer.py (calls new_validator.validate_input)
3. test_new_validator.py (test coverage)

[Full DEPENDENCY_GRAPH section included in evidence]"
```

## Bypass Warning

If user explicitly requests bypass:

```
USER: "Skip dependency graph, just use grep"

WINDSURF RESPONSE:
⚠️ CONSTITUTIONAL VIOLATION WARNING ⚠️

User requested bypass of §0 DEFAULT ANALYSIS MODE.

IMPACT:
- Violates "DEFAULT = DETAILED AST DEPENDENCY GRAPH" requirement
- Results will be LOW confidence (text search is unreliable)
- May miss dependencies (grep cannot detect dynamic resolution)
- May have false positives (grep matches comments/strings)
- Cannot detect cycles, boundaries, or architecture violations

RECOMMENDATION: Build AST dependency graph for HIGH confidence results.

PROCEED WITH BYPASS? (User must confirm)
```

## Constitutional References

- **§0:** DEFAULT = DETAILED AST DEPENDENCY GRAPH
- **§0:** Build AST dependency graph FIRST (before any other analysis)
- **§0:** Use graph as PRIMARY evidence
- **§0:** Block work if graph cannot be built
- **§0:** Document graph in all evidence
- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED
- **§3.5:** Low-signal search FORBIDDEN as primary method
- **§3.6:** Fail closed if AST parsing fails
