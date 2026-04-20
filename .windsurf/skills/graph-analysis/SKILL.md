---
name: graph-analysis
description: Unified AST dependency graph analysis for tier-aware investigation, impact analysis, scope validation, duplicate prevention, and retrieval-tool routing. Enforces ADG MCP over grep_search for ALL dependency/import/consumer/reference/blast-radius queries. Invoke this skill when analyzing dependencies, imports, consumers, references, blast radius, who-uses-X, what-depends-on-Y, or any code relationship query.
metadata:
  enforcement_layer: both
  enforcement_timing: before_work
  enforcement_type: behavioural_primary_structural_secondary
---

# Graph Analysis Skill (Consolidated)

**PREREQUISITE:** None (primary analysis skill)

Unified skill that consolidates `dependency-graph-analysis`, `scope-guard`, and `dedup-guard` into a single comprehensive graph-first analysis framework.

## CRITICAL: Retrieval-Tool Routing Matrix (read FIRST)

| Query type | Required tool | grep allowed? | Degraded fallback |
|---|---|---|---|
| imports / consumers / blast radius / fanin / fanout | `adg_sqlite` fanin/fanout | **FORBIDDEN** | Only after `mcp1_adg_health` red — emit `DEGRADED_FALLBACK: reason=...` |
| function / class / constant name in `*.py` | `adg_sqlite` find_node | **FORBIDDEN** | Same |
| Layer analysis (L0–L6) | `adg_sqlite` nodes_by_layer | **FORBIDDEN** | Same |
| Refactoring hotspots / centrality / chokepoints / critical paths | `adg_sqlite` SQL query on `mv_*` materialized views (e.g. `mv_graph_reverse_dependency_hotspots`, `mv_hotspot_centrality`, `mv_graph_chokepoint_bridges`, `mv_debt_concentration_hotspots`) | **FORBIDDEN** | Fallback: manual `adg_edge_fanin` walk — must cite why MV is unavailable |
| Pre-classified concerns (apps→infra, layer bypass, mis-layered, duplicated adapters, etc.) | `adg_sqlite` SQL query on `v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*` P-views | **FORBIDDEN** | — |
| Dataflow / side-effects / call resolution (what reads/writes X, what triggers Y, who calls Z) | `adg_sqlite` semantic edges: `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` | **FORBIDDEN** | — |
| Semantic / concept / meaning | `vector_db` semantic_search | explicit only | Explicit reason required |
| Runtime traces / anomalies / spans | `otel_mcp` | — | — |
| Literal text / TODOs / comments / non-Python | `grep_search` / `filesystem` | ✅ ALWAYS OK | — |

**Graph-layer primary rule (Constitutional §22):** for any refactoring,
wave planning, or prioritization task, the materialized views (`mv_*`),
pre-built P-views (`v_p0_*`..`v_p3_*`), and semantic edges are the PRIMARY
analysis primitives. Using only the raw `edges`/`violations` tables is
**insufficient** and fails the `check_graph_layer_evidence.py` CI gate.

**Health-first rule**: if `adg_sqlite` may be unhealthy, call `mcp1_adg_health` BEFORE any grep fallback.
**Silent degraded fallback** (grep for graph queries without health check + reason code) = **policy violation** (`severity: critical`).

**Before calling `grep_search` for ANY dependency/import/consumer/reference query, STOP.**
**Read `tool_routing_decision_tree.md` and use ADG MCP tools instead.**

`grep_search` is ONLY permitted for literal string searches (TODOs, comments, non-Python content).
For ALL dependency analysis: `mcp1_adg_nodes_by_file` → `mcp1_adg_edge_fanin` / `mcp1_adg_edge_fanout`.

## Module→Symbol Auto-Expansion Protocol

**AFTER `adg_nodes_by_file` returns nodes for a file, expand to symbol-level fan-in:**

```
Step 1: nodes = mcp1_adg_nodes_by_file(file_path="path/to/file.py")
Step 2: Separate nodes into:
         - module_nodes: entity_type="module"
         - symbol_nodes: entity_type="symbol" OR identity_kind="inferred_symbol"
Step 3: Run fan-in on EACH node:
         - mcp1_adg_edge_fanin(tgt_id=<module_node_id>, relation_type="imports")
           → catches file-level imports (from X import Y, import X)
         - mcp1_adg_edge_fanin(tgt_id=<symbol_node_id>, relation_type="imports")
           → catches name-level imports (from X import SpecificClass)
Step 4: Merge all fan-in results — deduplicate by source node ID
```

**Why this matters:** A module-only fan-in query misses callers that import specific
symbols (e.g., `from mcp_deferred_loader import DeferredLoader`). The symbol-level
expansion catches these name-level references that the module node alone misses.

**When to use:** Any dependency/consumer/blast-radius query on a file with exported
symbols. Skip expansion only for leaf files with no public API (e.g., `__init__.py`
re-exports, config files).

## Files

- **`tool_routing_decision_tree.md`** — **START HERE.** Concrete decision tree for ADG MCP vs grep_search routing (per OpenDev §3.2)
- **`tier_aware_protocol.md`** — T0/T1/T2/T3 analysis protocols with ADG cache usage guidelines
- **`graph_construction_standards.md`** — Node types, edge types, graph roots, analysis depth requirements
- **`impact_analysis_template.md`** — Upstream/downstream analysis, blast radius determination, cross-layer impacts
- **`scope_validation_checklist.md`** — Pre-edit scope declaration, graph justification, contamination prevention
- **`duplicate_prevention_protocol.md`** — AST-backed duplicate detection before symbol creation
- **`fail_closed_discipline.md`** — Error handling when AST parsing fails, no silent fallback

## Tier-Aware Enforcement

| Tier | When | This Skill's Role |
|------|------|--------------------|
| **T0 — Question** | No code changes | Use ADG hot cache if available. No ceremony. |
| **T1 — Trivial** | ≤1 file, ≤20 lines | ADG cache query optional. No `DEPENDENCY_GRAPH` section. |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG cache for blast radius. Brief scope note. |
| **T3 — Architectural** | >5 files, cross-layer, governance | **Full protocol below.** `DEPENDENCY_GRAPH` section mandatory. |

**This skill is MANDATORY for T2 and T3.** For T0/T1, best-effort cache use is sufficient.

## Core Rules

1. **AST dependency graph is PRIMARY.** Text search is secondary confirmation only.
2. **Graph wins disagreements.** If graph and text search conflict, graph wins unless extractor limitation is proven and recorded.
3. **Fail-closed on parse failure.** No silent fallback to grep/regex (§2.3).
4. **T3 evidence requires `## DEPENDENCY_GRAPH` section** with graph justification for each changed file.

## When to Use

**T2/T3 MANDATORY for:** root cause analysis, impact analysis, file selection, duplicate detection, dead code, boundary validation, layer inversion, test selection, healing scope, refactor planning, execution path analysis, registry/wiring validation.

**FORBIDDEN to skip:** If a task involves architecture, orchestration, healing, routing, registry wiring, or blast radius → this skill is REQUIRED even if the user does not restate it.

## Scope Validation Protocol

**BEFORE any file edits:**

1. **Execute**: Build AST dependency graph
2. **Declare scope**: Create artifact listing exact files to be modified
3. **Justify each file**: Document graph edge path showing why file is in blast radius
4. **Record baseline**: Execute `git diff --name-only HEAD` and verify output is empty
5. **Write to**: Evidence section titled `## SCOPE_DECLARATION`

**Format required**:
```
## SCOPE_DECLARATION
Files to modify: N
1. path/to/file1.py — Reason: root module per ADG cluster X
2. path/to/file2.py — Reason: imports file1, edge (file2 → file1) in graph
...
Baseline: git diff clean (no uncommitted changes)
```

**IF any step fails → STOP. Do not make any edits.**

After each edit batch:
- Execute `git diff --name-only HEAD`
- Verify output matches declared scope exactly
- If unexpected files appear → invoke decontamination protocol

## Duplicate Prevention Protocol

**BEFORE creating any new Agent, Mixin, Orchestrator, Engine, utility function, or SSOT constant:**

1. **Execute 4-step search**:
   - AST symbol search (find all classes/functions with equivalent signatures)
   - Name pattern search (find all symbols with overlapping name stems)
   - Behavioral search (find all symbols that read/write same data or call same APIs)
   - Registry check (verify not in agent registry or SSOT constants)

2. **Document search results**: Write to evidence section titled `## DEDUP_SEARCH`

3. **Make decision**:
   - If exact duplicate found → STOP, reuse existing
   - If near-duplicate found → STOP, extend existing
   - If no duplicate found → proceed with creation, document justification

**Format required**:
```
## DEDUP_SEARCH
Symbol to create: <ClassName> or <function_name> or <CONSTANT_NAME>
AST search: <N> matches found [list if >0]
Name pattern search: <N> matches found [list if >0]
Behavioral search: <N> matches found [list if >0]
Registry check: <found | not found>
Decision: <reuse | extend | create>
Justification (if create): <why no existing symbol is suitable>
```

**IF any match found → STOP. Do not create duplicate.**

## Impact Analysis Template

**For T2/T3 operations, include:**

```
## DEPENDENCY_GRAPH
**Graph Roots**: <primary nodes>
**Impacted Nodes**: <N> nodes total
**Upstream Set**: <nodes that depend on changes>
**Downstream Set**: <nodes that changes depend on>
**Edge Classes**: <types of edges found>
**Boundary/Cycle Findings**: <any layer violations or cycles>
**Scope Justification**: <reason each file is included>
**Backend Provenance**: <redis_cache | sqlite | degraded_grep>
```

## Backend Provenance Reporting

**Every ADG-backed answer MUST include `backend_used` provenance.**

ADG MCP responses include a `backend_used` field in their metadata:
- **`redis_cache`** — Result served from Redis hot cache (fast path, ~75ms)
- **`sqlite`** — Result served from canonical SQLite (fallback, ~200ms)
- **`degraded_grep`** — ADG was unavailable; grep used with `DEGRADED_FALLBACK` reason

**Reporting format** (include in any ADG analysis output):
```
ADG Provenance: backend_used=<redis_cache|sqlite|degraded_grep>, query_count=<N>, cache_hits=<M>
```

**Why this matters:** Provenance makes the data source visible. If all queries
fall back to SQLite, it signals Redis cache needs warming. If degraded_grep
appears, it flags an ADG health issue requiring `/mcp-failure-rca`.

## Constitutional Requirements Enforced

- **§0:** Tier-aware analysis with ADG primacy
- **§2:** ADG framework mandatory for T2/T3
- **§2.3:** Fail-closed discipline (no silent fallback)
- **§3.4:** AST dependency graphs PRIMARY analysis primitive
- **§3.7:** Each changed file MUST have graph justification
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis

## Forbidden Patterns

- ❌ Long operations (>5s) without progress display
- ❌ Progress updates less frequent than every 5 seconds
- ❌ Monochrome output (no color coding)
- ❌ Missing percentage completion
- ❌ Missing ETA for operations >30s
- ❌ **Unbounded file operations** (processing unlimited files without limits)
- ❌ **Missing PowerShell compatibility** (Unix-only commands like `head`, `tail`)
- ❌ **Inline Python complexity** (complex scripts in shell commands)
- ❌ **No early termination conditions** (process all files even when patterns converge)
- ❌ **Missing batch processing** (process files one by one without progress reporting)
- ❌ Assuming relationships without graph proof
- ❌ Silent fallback from AST failure to text search
- ❌ Claiming "no dependencies" without graph analysis
