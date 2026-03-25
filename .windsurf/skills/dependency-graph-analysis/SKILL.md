---
name: dependency-graph-analysis
description: Provides AST-based dependency graph analysis workflows per §0 (tier-aware) and §2. Use before any non-trivial code investigation, impact analysis, file selection, or blast radius determination. Enforces graph-first discipline and forbids low-signal search methods. Includes graph construction protocol, impact analysis template, and fail-closed error handling.
---

# Dependency Graph Analysis Skill

**Unified graph-first skill** — replaces the former `ast-first-gate` + `dependency-graph-analysis` pair. Enforces §0 tier-aware analysis and §2 ADG framework requirements.

## Tier-Aware Enforcement (§0)

| Tier | When | This Skill's Role |
|------|------|--------------------|
| **T0 — Question** | No code changes | Use ADG hot cache if available. No ceremony. |
| **T1 — Trivial** | ≤1 file, ≤20 lines | ADG cache query optional. No `DEPENDENCY_GRAPH` section. |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG cache for blast radius. Brief scope note. |
| **T3 — Architectural** | >5 files, cross-layer, governance | **Full protocol below.** `DEPENDENCY_GRAPH` section mandatory. |

**This skill is MANDATORY for T2 and T3.** For T0/T1, best-effort cache use is sufficient.

## Files

- **`graph_construction_protocol.md`** — T3 protocol: node types, edge types, graph roots, analysis depth.
- **`impact_analysis_template.md`** — T2/T3 template: upstream, downstream, cross-layer, cycles, blast radius.
- **`fail_closed_discipline.md`** — If AST parsing fails: record errors, mark partial, STOP. No silent fallback.
- **`forbidden_methods_checklist.md`** — Forbidden: grep/regex/filename guessing as primary analysis.

## When to Use

**T2/T3 MANDATORY for:** root cause analysis, impact analysis, file selection, duplicate detection, dead code, boundary validation, layer inversion, test selection, healing scope, refactor planning, execution path analysis, registry/wiring validation.

**FORBIDDEN to skip:** If a task involves architecture, orchestration, healing, routing, registry wiring, or blast radius → this skill is REQUIRED even if the user does not restate it.

## Core Rules

1. **AST dependency graph is PRIMARY.** Text search is secondary confirmation only.
2. **Graph wins disagreements.** If graph and text search conflict, graph wins unless extractor limitation is proven and recorded.
3. **Fail-closed on parse failure.** No silent fallback to grep/regex (§2.3).
4. **T3 evidence requires `## DEPENDENCY_GRAPH` section** with graph justification for each changed file.
