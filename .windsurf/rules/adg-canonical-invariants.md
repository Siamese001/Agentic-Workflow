---
trigger: always_on
---

# ADG Canonical Invariants — Doctrinal Floor

> ⛔ These are **the non-negotiables** encoded in the ADG doctrine
> (`docs/reference/AST Dependency Graphs (ADG)/`). Every T1/T2/T3 task that
> interacts with the ADG MUST honor these invariants without exception.

## 1. Source-of-Truth Hierarchy (invariant)

```
SQLite  =  CANONICAL TRUTH           (mutable only via generate_full_adg.py)
Redis   =  HOT READ-ONLY PROJECTION  (deterministic subset of SQLite)
MCP     =  READ-ONLY GATEWAY         (serves SQLite; lazy-warms Redis)
```

- **No divergence**: Redis / MCP responses that disagree with SQLite are invalid by definition — SQLite wins.
- **No writes through the graph layer**: MCP is read-only. Graph mutations happen ONLY through `tools/generate_full_adg.py`.
- **Provenance every time**: ADG-backed answers MUST report `backend_used` (`redis_cache` / `sqlite` / `degraded_grep`) — see `graph-analysis/SKILL.md`.

## 2. The ADG Wins Conflicts

When graph facts and text-search / intuition / "feels important" disagree:

> **The ADG wins. If a node lies, the graph is invalid — fix the graph, not your analysis.**

A plan that asserts a claim NOT backed by an ADG node/edge/MV is a **guess**, not evidence.

## 3. The 5 ADG Surfaces (risk boundaries — always consider these)

| Surface | What It Guards | Why Hotspots Here Matter |
|---------|----------------|---------------------------|
| **Execution** | Tool invocations, agent dispatches, subprocess boundaries | Lost failures = silent wrong-action |
| **Write** | State mutations through UWG / SovereignBaseAgent | Partial writes = corrupt system of record |
| **Security** | Guardrail / safety-plane / policy enforcement | Swallowed checks = no safety |
| **State** | Memory / cache / checkpoint / canonical store | Silent inconsistency across sessions |
| **Observability** | OTEL spans / audit trail / evidence ledger | Swallowed failures = broken forensics |

**Rule:** When ranking hotspots, a catch site that **intersects any surface** is higher-priority than the same catch site in an isolated module. Plans MUST note surface intersections.

## 4. The 4 Deadly Catch-Site Antipatterns

| Antipattern | Edge Kind | Failure Mode | ADG Band |
|-------------|-----------|--------------|:--------:|
| `broad_exception_catch` | `except Exception: ...` | Collapses specific failures into one generic bucket | **P2** |
| `log_and_swallow` | `except X: log(e); continue` | Keeps running in bad state | **P2** |
| `silent_exception_swallow` | `except X: pass` | Total invisibility | **P2** |
| `return_none_swallow` | `except X: return None` | Failure → ambiguity → later crash |  **P2** |

All four have guardian exemption paths BUT require explicit Author-Gate approval per `anti-pattern-author-gate.md` (§constitutional 8). No new instances without approval.

## 5. Hotspot Archetypes (required classification in plans)

| Archetype | Signature | Why Dangerous |
|-----------|-----------|---------------|
| **CENTRAL_DEPENDENCY** | High fan-in | Bad swallow poisons many callers |
| **ORCHESTRATOR** | High fan-out / flows_to density | Swallow hides chain failures |
| **STATE_NODE** | Write/read path (UWG, cache, canonical store) | Swallow = silent inconsistency |
| **SAFETY_GATEKEEPER** | Guardrail / policy / safety-plane code | Swallow suppresses guardrails |

Every row in `## ADG_HOTSPOT_REPORT` MUST include one of these archetypes.

## 6. Layer Criticality Multipliers (applied to impact score)

| Layer | Multiplier | Rationale |
|-------|:----------:|-----------|
| **L0** routing | ×2.0 | Poisoned routing = all downstream lies |
| **L5** safety / guardrail | ×2.0 | Swallowed controls = no safety |
| **L3** orchestration | ×1.75 | Chain failure hiding |
| **L4** state / cache | ×1.75 | Silent inconsistency |
| **L1/L2** cognition / execution | ×1.0 | Standard weight |
| **L6** observability | ×0.75 | Bad, but less structural risk |

Impact score used for wave ordering:
```
impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier
```

## 7. Zero-Loss Propagation Pipeline (hotspot discovery)

Every hotspot claim MUST be traceable through this chain:

```
[ catch site at file:line ]
       │
       ▼
[ antipattern edge ]       (broad_catch | log_and_swallow | silent_swallow | return_none)
       │
       ▼
[ ownership bridge ]       (Symbol → owning Module → Layer — closes the type gap)
       │
   ├─► How bad is the pattern itself?
   ├─► What layer? (L0/L5 > L3/L4 > L1/L2 > L6)
   ├─► Fan-in? (who breaks)
   ├─► Fan-out? (what gets hidden)
   └─► Does the flow cross any of the 5 ADG Surfaces?
       │
       ▼
  [ HOTSPOT — ranked ]
```

A refactoring target that skips any step of this pipeline is **unproven** and cannot be scheduled.

## 8. Static ADG vs Runtime ADG (distinct stores, distinct MCPs)

| Dimension | Static ADG | Runtime ADG |
|-----------|-----------|-------------|
| MCP server | `adg_sqlite` | `otel_mcp` (ingest via `otel_ingest_to_runtime_adg`) |
| Source | AST scan of code | OTEL spans at runtime |
| Use | Structural deps, refactoring, hotspot analysis | Live behavior, healing chain, anomaly spans |
| Questions | "who imports X?" | "what happened at runtime when Y was called?" |

NEVER conflate the two. Plans that ask structural questions of `otel_mcp` or runtime questions of `adg_sqlite` are wrong-routed.

## 9. ADG vs Hardcoded String

When a path, identifier, or layer name has an ADG representation:

| FORBIDDEN | REQUIRED |
|-----------|----------|
| `grep_search("L0_routing")` | `adg_nodes_by_layer("L0")` |
| Hardcoded path lists in code | `adg_nodes_by_file` / `nodes.file_path` query |
| "Which files are in L2?" by directory walking | `adg_nodes_by_layer("L2")` |
| Magic layer strings scattered in checks | Import from `agentic_core.adg.severity_bands` (for bands) or `agentic_core/*/path_constants.py` (for paths) |

## 10. Required Plan Sections (T2/T3 refactoring)

Every T2/T3 refactoring plan MUST contain both sections (CI-enforced):

1. `## ADG_HOTSPOT_REPORT` — ranked table of hotspots with layer, fan-in, impact, archetype
2. `## ADG_GRAPH_LAYER_EVIDENCE` — ≥3 MVs + semantic edges + P-view cross-references

Missing either = plan invalid (gate: `ops_scripts/ci/check_graph_layer_evidence.py`).

## 11. Provenance Stamp on ADG Answers

When presenting ADG-backed facts (in a response, plan, or evidence file), include a provenance line:

```
ADG Provenance: backend=<redis_cache|sqlite|degraded_grep>, snapshot=adg_indexed_<timestamp>.sqlite
```

If `degraded_grep` appears, a `DEGRADED_FALLBACK: reason=<...>` line MUST accompany it (see `global_rules.md` ADG-First Analysis).

## 12. Doctrinal References

- `docs/reference/AST Dependency Graphs (ADG)/ADG Mental Model.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG SQLite Hotspot Cheat Sheet.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG - SQLite vs. Redis.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG and Blast Radius.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG STATIC vs. RUNTIME MENTAL MODEL.md`
- `docs/reference/AST Dependency Graphs (ADG)/DEPENDENCY GRAPH vs GRAPHDB Design.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG vs, Hardcoded String.md`

These invariants are extracted from the above. Updating this rule requires updating the source docs too — **no SSOT drift**.
