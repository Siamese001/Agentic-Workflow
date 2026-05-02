---
trigger: always_on
---

# ADG Canonical Invariants — Doctrinal Floor

> ⛔ Non-negotiables encoded in `docs/reference/_primers/AST Dependency Graphs (ADG)/`. Every T1/T2/T3 task interacting with the ADG MUST honor these without exception.

## 1. Source-of-Truth Hierarchy (invariant)

```
SQLite  =  CANONICAL TRUTH           (mutable only via generate_full_adg.py)
Redis   =  HOT READ-ONLY PROJECTION  (deterministic subset of SQLite)
MCP     =  READ-ONLY GATEWAY         (serves SQLite; lazy-warms Redis)
```

- **No divergence**: Redis/MCP responses disagreeing with SQLite are invalid by definition — SQLite wins.
- **No writes through the graph layer**: graph mutations ONLY through `tools/generate_full_adg.py`.
- **Provenance every time**: ADG-backed answers MUST report `backend_used` (`redis_cache` / `sqlite` / `degraded_grep`) — see `graph-analysis` skill.

## 2. The ADG Wins Conflicts

When graph facts and text-search/intuition disagree:

> **The ADG wins. If a node lies, the graph is invalid — fix the graph, not your analysis.**

A plan asserting a claim NOT backed by an ADG node/edge/MV is a **guess**, not evidence.

## 3. The 5 ADG Surfaces (risk boundaries)

`Execution` (tool/agent dispatch), `Write` (UWG/SovereignBaseAgent state mutation), `Security` (guardrail/policy), `State` (memory/cache/canonical store), `Observability` (OTEL/audit/evidence). When ranking hotspots, a catch site intersecting ANY surface is higher-priority than the same site in an isolated module. Plans MUST note surface intersections.

## 4. The 4 Deadly Catch-Site Antipatterns (all P2 band)

`broad_exception_catch` (`except Exception:`), `log_and_swallow` (`except X: log; continue`), `silent_exception_swallow` (`except X: pass`), `return_none_swallow` (`except X: return None`). All four have guardian exemption paths BUT require Author-Gate approval per `anti-pattern-author-gate.md` (constitutional §8). No new instances without approval.

## 5. Hotspot Archetypes (required classification in plans)

`CENTRAL_DEPENDENCY` (high fan-in — bad swallow poisons many callers), `ORCHESTRATOR` (high fan-out / `flows_to` density — swallow hides chain failures), `STATE_NODE` (write/read path — swallow = silent inconsistency), `SAFETY_GATEKEEPER` (guardrail/policy — swallow suppresses guardrails). Every row in `## ADG_HOTSPOT_REPORT` MUST include one archetype.

## 6. Layer Criticality Multipliers (impact score)

L0 routing ×2.0, L5 safety ×2.0, L3 orchestration ×1.75, L4 state/cache ×1.75, L1/L2 cognition/execution ×1.0, L6 observability ×0.75.

```
impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier
```

## 7. Zero-Loss Propagation Pipeline (hotspot discovery)

Catch site → antipattern edge (broad_catch | log_and_swallow | silent_swallow | return_none) → ownership bridge (Symbol → owning Module → Layer) → ranked HOTSPOT. At the ranking step, weigh: how bad is the pattern, what layer (L0/L5 > L3/L4 > L1/L2 > L6), fan-in (who breaks), fan-out (what's hidden), surface intersections (5 above). A target skipping any step of this pipeline is **unproven** and cannot be scheduled.

## 8. Static ADG vs Runtime ADG (distinct stores, distinct MCPs)

| Dimension | Static ADG | Runtime ADG |
|-----------|-----------|-------------|
| MCP server | `adg_sqlite` | `otel_mcp` (ingest via `otel_ingest_to_runtime_adg`) |
| Source | AST scan | OTEL spans |
| Use | Structural deps, refactoring, hotspot analysis | Live behavior, healing chain, anomaly spans |
| Questions | "who imports X?" | "what happened at runtime when Y was called?" |

NEVER conflate. Plans asking structural questions of `otel_mcp` or runtime questions of `adg_sqlite` are wrong-routed.

## 9. ADG vs Hardcoded String

When a path/identifier/layer-name has an ADG representation, query the ADG — never grep, never hardcode. `grep_search("L0_routing")` → `adg_nodes_by_layer("L0")`. Hardcoded path lists → `adg_nodes_by_file` / `nodes.file_path` query. Magic layer strings → import from `agentic_core.adg.severity_bands` or `agentic_core/*/path_constants.py`.

## 10. Required Plan Sections (T2/T3 refactoring)

Every T2/T3 refactoring plan MUST contain both (CI-enforced via `check_graph_layer_evidence.py`):

1. `## ADG_HOTSPOT_REPORT` — ranked table of hotspots with layer, fan-in, impact, archetype
2. `## ADG_GRAPH_LAYER_EVIDENCE` — ≥3 MVs + semantic edges + P-view cross-references

## 11. Provenance Stamp on ADG Answers

When presenting ADG-backed facts: `ADG Provenance: backend=<redis_cache|sqlite|degraded_grep>, snapshot=adg_indexed_<ts>.sqlite`. If `degraded_grep` appears, a `DEGRADED_FALLBACK: reason=<...>` line MUST accompany it.

## 12. Doctrinal References

Source primers under `docs/reference/_primers/AST Dependency Graphs (ADG)/`: ADG Mental Model, ADG SQLite Hotspot Cheat Sheet, ADG SQLite vs Redis, ADG and Blast Radius, ADG Static vs Runtime Mental Model, Dependency Graph vs GraphDB Design, ADG vs Hardcoded String. **Updating this rule requires updating the source docs too — no SSOT drift.**
