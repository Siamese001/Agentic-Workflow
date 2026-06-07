---
trigger: model_decision
description: Converted from Cursor rule adg-canonical-invariants.md Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/adg-canonical-invariants.mdc (alwaysApply: false).
---

# ADG Canonical Invariants

> ⛔ Non-negotiables for every T1/T2/T3 task interacting with the ADG. Detail: `docs/reference/_primers/AST Dependency Graphs (ADG)/`.

## 1. Source-of-Truth Hierarchy

SQLite = CANONICAL TRUTH (mutable only via `generate_full_adg.py`). Redis = hot read-only projection. MCP = read-only gateway. SQLite wins on divergence. Provenance required: `backend_used` (`redis_cache`/`sqlite`/`degraded_grep`).

## 2. ADG Wins Conflicts

> **The ADG wins. If a node lies, fix the graph, not your analysis.** Claims not backed by ADG node/edge/MV are guesses.

## 3. The 5 Surfaces

`Execution`, `Write`, `Security`, `State`, `Observability`. Catch sites intersecting any surface = higher priority. Plans MUST note surface intersections.

## 4. Antipatterns + Archetypes + Multipliers

4 deadly catch-site antipatterns (P2): `broad_exception_catch`, `log_and_swallow`, `silent_exception_swallow`, `return_none_swallow`. Author-Gate required for new instances (§8).

4 archetypes (required in `ADG_HOTSPOT_REPORT` rows): `CENTRAL_DEPENDENCY`, `ORCHESTRATOR`, `STATE_NODE`, `SAFETY_GATEKEEPER`.

Layer multipliers: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75. `impact = violations × (1 + log10(1 + fan_in)) × multiplier`.

## 5. Static vs Runtime ADG

Static (`adg_sqlite`): AST scan, structural deps. Runtime (`otel_mcp`): OTEL spans, live behavior. NEVER conflate.

## 6. ADG vs Hardcoded String

Query ADG for paths/identifiers/layer-names — never grep, never hardcode. Detailed retrieval procedure in `global_rules.md` §ADG-First Analysis.

## 7. Required Plan Sections (T2/T3)

`## ADG_HOTSPOT_REPORT` (ranked hotspots) + `## ADG_GRAPH_LAYER_EVIDENCE` (≥3 MVs + semantic edges + P-views). CI: `check_graph_layer_evidence.py`.

## 8. Provenance Stamp

`ADG Provenance: backend=<...>, snapshot=adg_indexed_<ts>.sqlite`. `DEGRADED_FALLBACK: reason=<...>` required if degraded.
