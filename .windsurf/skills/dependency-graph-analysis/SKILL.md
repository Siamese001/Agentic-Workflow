---
name: dependency-graph-analysis
description: Provides AST-based dependency graph analysis workflows per §3.4-§3.7. Use before any non-trivial code investigation, impact analysis, file selection, or blast radius determination. Enforces graph-first discipline and forbids low-signal search methods. Includes graph construction protocol, impact analysis template, and fail-closed error handling.
---

# Dependency Graph Analysis Skill

Enforces constitutional requirements for AST-based dependency graph analysis (§3.4-§3.7, §4.4, §5.2).

## Files

- **`graph_construction_protocol.md`** — Step-by-step protocol for building AST dependency graphs. Defines required node types, edge types, graph roots, and analysis depth. MANDATORY before any code investigation.

- **`impact_analysis_template.md`** — Template for documenting graph-backed impact analysis. Includes upstream dependencies, downstream dependents, cross-layer edges, cycle detection, boundary violations, and test surface implications.

- **`fail_closed_discipline.md`** — Protocol for handling AST parsing failures. Defines exact error recording, partial conclusion marking, and prohibition of silent fallback to text search.

- **`forbidden_methods_checklist.md`** — Checklist of forbidden low-signal search methods (grep, regex, filename guessing). Use to verify compliance with §3.5.

## When to use

**MANDATORY for (§3.4):**
- Root cause analysis
- Impact analysis
- File selection
- Duplicate detection
- Dead code detection
- Boundary validation
- Layer inversion detection
- Test selection
- Healing scope
- Refactor planning
- Execution path analysis
- Registry and wiring validation

**FORBIDDEN to skip:**
If a task involves architecture, orchestration, healing, validation, routing, registry wiring, or blast radius, the dependency graph is REQUIRED even if the user does not restate it.

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED analysis primitive
- **§3.5:** Low-signal search (grep/regex) FORBIDDEN as primary analysis method
- **§3.6:** If AST parsing fails, MUST fail closed (no silent fallback)
- **§3.7:** Evidence MUST include DEPENDENCY_GRAPH section with graph justification for each changed file
- **§4.3:** Boundary enforcement MUST use AST dependency graph
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis
- **§5.2:** Test selection MUST be dependency-graph-backed

## Graph vs Text Search

**The graph wins:**
If the dependency graph and text search disagree, the graph wins unless you prove the graph extractor is incomplete and record the limitation explicitly.

**Text search MAY be used only:**
- AFTER the AST dependency graph has identified a bounded candidate set
- ONLY as a secondary confirmation tool for literal strings or exact constants

**Text search MUST NEVER be used to:**
- Define blast radius
- Infer architecture
- Infer ownership
- Infer call flow
- Infer dependency direction
- Infer dead code
- Infer test coverage
- Infer whether a component is unused
- Infer whether a file is authoritative
