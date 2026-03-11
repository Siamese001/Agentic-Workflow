---
name: ast-first-gate
description: BLOCKS all code investigation and analysis work until AST dependency graph is built per §0 DEFAULT ANALYSIS MODE. Use automatically before any code investigation, impact analysis, refactoring, or modification. Enforces "DEFAULT = DETAILED AST DEPENDENCY GRAPH" constitutional requirement.
enforcement_layer: windsurf
enforcement_timing: before_work
enforcement_type: behavioural
---

# AST-First Gate Skill

**AUTOMATIC BLOCKER** - Enforces §0 DEFAULT ANALYSIS MODE.

This skill MUST be invoked BEFORE any code investigation or analysis work begins.

## Purpose

Enforce the constitutional default: **DEFAULT = DETAILED AST DEPENDENCY GRAPH**

BLOCK all work until dependency graph is built, documented, and validated.

## Files

- **`pre_analysis_gate.md`** — MANDATORY gate before any code investigation. Blocks work until AST dependency graph is built, all required edge types extracted, and DEPENDENCY_GRAPH section documented. NO BYPASS.

- **`ast_first_checklist.md`** — Quick checklist to verify AST-first compliance. Use before responding to any user request involving code analysis.

## When to use

**AUTOMATIC TRIGGERS (§0):**
- User mentions: files, functions, classes, modules, imports, dependencies
- User asks: "what uses this", "what depends on", "impact of", "blast radius"
- User requests: refactor, modify, analyze, investigate, debug, trace
- User inquires: test coverage, dead code, duplicates, boundaries

**MANDATORY BEFORE:**
- Any code investigation
- Any impact analysis
- Any file selection
- Any scope declaration
- Any refactoring
- Any modification
- Any debugging
- Any tracing

## Gate Enforcement

```
IF user_request_involves_code:
    INVOKE ast-first-gate
    BUILD dependency_graph
    DOCUMENT graph in DEPENDENCY_GRAPH section
    VALIDATE graph completeness
    THEN proceed with user request
ELSE:
    Proceed normally
```

## Constitutional Requirements Enforced

- **§0:** DEFAULT = DETAILED AST DEPENDENCY GRAPH
- **§0:** Build AST dependency graph FIRST (before any other analysis)
- **§0:** Use graph as PRIMARY evidence (text search only as secondary)
- **§0:** Block work if graph cannot be built (fail-closed)
- **§0:** Document graph in all evidence (DEPENDENCY_GRAPH section mandatory)
- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED analysis primitive
- **§3.5:** Low-signal search (grep/regex) FORBIDDEN as primary analysis method
- **§3.6:** If AST parsing fails, MUST fail closed

## Integration with Other Skills

This skill is a PREREQUISITE for:
- `test-rigor-enforcement` (needs graph for test identification)
- `scope-guard` (needs graph for scope justification)
- `evidence-bundle` (needs graph for DEPENDENCY_GRAPH section)
- `dependency-graph-analysis` (provides the actual graph construction)

## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE any tool call involving code analysis, file editing, or impact assessment:**

1. **Execute**: Build AST dependency graph using `tools/generate_full_adg.py` or equivalent
2. **Write output to**: Evidence section titled `## DEPENDENCY_GRAPH`
3. **Document**:
   - Graph node count (modules scanned)
   - Graph edge count (dependencies found)
   - Edge types extracted (G1 imports, G3 implements, G4 calls, GT covers, GV violates, GG governance)
   - Blast radius for changed files (if applicable)
4. **Verify**: Graph contains >0 nodes and >0 edges

**IF any step fails → STOP. Do not proceed with code investigation.**

Only after `DEPENDENCY_GRAPH` section is written may you:
- Trace import chains
- Identify root modules
- Compute blast radius
- Select files to edit
- Declare scope

## Bypass Conditions

**NONE.** This gate cannot be bypassed unless user explicitly states:
- "Skip dependency graph analysis"
- "Use text search only"
- "Don't build AST graph"

Even then, Windsurf MUST warn about constitutional violation and reduced confidence.
