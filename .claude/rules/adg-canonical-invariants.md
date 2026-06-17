
<!-- Converted from `.claude/rules/adg-canonical-invariants.md`. Original legacy editor trigger: `always_on`. -->

# ADG Canonical Invariants

> ⛔ Non-negotiables for every T1/T2/T3 task interacting with the ADG. Detail: `docs/reference/_primers/AST Dependency Graphs (ADG)/`.

## 1. Source-of-Truth Hierarchy

**Canonical retrieval ladder (one line):** Redis warm projection → MCP read-only gateway (**`adg_sqlite`**) → SQLite direct only with **`DEGRADED_FALLBACK: reason=<…>`** unless matching a **named CI parity script**.

**Doctrine (verbatim):** SQLite is canonical truth. Redis is a hot projection/read-through optimization, never authority. MCP is the preferred read-only gateway for agents. Direct sqlite3 or SQLiteBackend access in plans requires either a named CI parity script or an explicit DEGRADED_FALLBACK reason. Warm Redis hits may serve MCP responses only when provenance is visible through backend_used and, where required, rows hydrate or validate against canonical SQLite. Cold, missing, error, empty, or divergent Redis falls back to SQLite. Agents must not silently default to raw sqlite3 for refactor or analysis work.

SQLite remains mutable only via `generate_full_adg.py`. SQLite wins on divergence. Provenance required on MCP/tool responses: **`backend_used`** (e.g. `redis`, `sqlite`, `projection`, plus legacy/cache strings where applicable). Never treat Redis rows as authoritative without SQLite hydration or canonical fallback where the pipeline defines it.

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

Query ADG for paths/identifiers/layer-names — never grep, never hardcode. Detailed retrieval procedure: constitutional §5/§28 + the [`graph-analysis`](../skills/graph-analysis/SKILL.md) / [`adg-sqlite`](../skills/adg-sqlite/SKILL.md) skills.

## 7. Required Plan Sections (T2/T3)

`## ADG_HOTSPOT_REPORT` (ranked hotspots) + `## ADG_GRAPH_LAYER_EVIDENCE` (≥3 MVs + semantic edges + P-views). CI: `check_graph_layer_evidence.py`.

## 8. Provenance Stamp

`ADG Provenance: backend=<...>, snapshot=adg_indexed_<ts>.sqlite`. `DEGRADED_FALLBACK: reason=<...>` required if degraded.
