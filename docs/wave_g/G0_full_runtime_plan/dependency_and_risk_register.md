# Wave G — Dependency and Risk Register

## Sub-wave dependencies

```
G1 ─┬─► G2 ──► G3 ──► G3b ──┐
    │                        │
    ├─► G1b ──► G2 (cross)   │
    │                        │
    ├─► G2b ──────────────┐  │
    │                     │  │
    └─► G4 ──► G4b        │  │
        ▲                 │  │
        └───► G5 ◄────────┘  │
              ▼                │
              G6 ◄─── (unclassified from G1/G1b, duplicates from G2/G4)
              ▼
              G7 ◄─── (consumes ALL G1–G6)
```

### Hard preconditions

| Sub-wave | Must have before start |
|---|---|
| G1 | Fresh ADG snapshot (`/adg-redis-refresh`); v1.3 canonical available |
| G1b | G1 complete (core classification needed to resolve app-to-core bindings) |
| G2 | G1 **and** G1b complete (wiring spans both) |
| G2b | G1 complete; env-key scan can start in parallel with G1b |
| G3 | G1 complete; G2 optional but strongly recommended (wiring informs pipelines) |
| G3b | G3 complete; G3b specializes a subset of pipelines |
| G4 | G1 complete (to know which modules own which stores) |
| G4b | G1 **and** G4 complete (control plane references stores + modules) |
| G5 | G1, G1b, G4b at least partially complete (ops scripts reference modules + configs) |
| G6 | G1, G1b, G2, G4 complete (so unclassified + duplicate surfaces are known) |
| G7 | All of G1–G6 complete |

### Parallelization allowed

- G1b can start once G1's `component_inventory.yaml` has at least L0–L6 entries (cross-cutting classification can still be in progress).
- G2b can run in parallel with G1b and G2 (egress inventory is largely orthogonal).
- G4 and G4b can run in parallel after G1 (G4b adds store cross-refs once G4 is done).
- G5 can run in parallel with G4b (different surfaces).

### Gate between phases

- **Gate 1** (after G1, G1b): `unclassified_modules.md` and app inventory complete → G2 can start.
- **Gate 2** (after G2, G2b, G3, G3b): wiring + pipelines + egress mapped → G4 and G4b may finalize.
- **Gate 3** (after G4, G4b, G5): storage + control plane + ops mapped → G6 normalizes.
- **Gate 4** (after G6): taxonomy clean → G7 integrates.

Failure at any gate blocks downstream sub-waves; the owning sub-wave MUST be re-run until the gate condition passes.

## Risk register

### Graph-analysis risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-G-01 | ADG snapshot stale when G1/G2 run — missed modules or stale edges | High | Regenerate ADG at start of G1 and G2 via `/adg-redis-refresh`; record snapshot timestamp in every YAML catalogue. |
| R-G-02 | Dynamic imports (`importlib`, `__import__`) hide wiring from ADG | High | In G2, scan for `importlib` / `__import__` literals and cross-check via `grep_search` (allowed for literals per constitutional §Quick Gates). Document each dynamic import and its target surface. |
| R-G-03 | `grep_search` drift — using grep for dependency analysis instead of ADG | Critical | Enforced by constitutional rule §ADG-First. Violation would invalidate the artefact. Use ADG MCP exclusively for dependency queries. |
| R-G-04 | Cycles in imports misclassify a module's home layer | Medium | Tie-break by "where is the dominant entry point?" rule and record cycle in `boundary_violations.md`. |

### Taxonomy risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-G-05 | L5_safety and L2_execution both contain 300+ items; role taxonomy drifts | High | Freeze role enum in `output_contracts.md`; force every module to one role. |
| R-G-06 | Cross-cutting modules end up double-homed (layer + cross-cutting) | Medium | Cross-cutting is exclusive: a module either has a layer or is CROSS_CUTTING; never both. |
| R-G-07 | `apps_shared/` is mis-inventoried as an app | Medium | `is_library_only: true` required for apps_shared; no `__main__` entry permitted. |
| R-G-08 | `_compat/` and `archives/` dead code picked up | Medium | Skip `archives/`; classify `_compat/` explicitly as shim per role enum. |
| R-G-09 | Duplicate responsibilities (Redis client in both `tools/mcp/redis_mcp/` and `agentic_core/`; retrieval helpers split across `tools/retrieval/` and `agentic_core/embeddings/`) | High | G6 `duplicate_responsibility_register.md` is the only place these are surfaced and proposed for consolidation. |

### Completeness risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-G-10 | Silent gaps: a v1.3 atom has no embodying module | High | G7 `traceability_matrix.yaml` REQUIRES `unmatched.atoms: []` at completion; any gap is either a runtime-missing blocker or a B7 candidate. |
| R-G-11 | B7 candidates absorbed into prose without label | Medium | `B7-<sub-wave>-NN` format enforced; G7 integration step cross-checks. |
| R-G-12 | End-to-end walk in G7 cannot cite concrete modules at a stage | High | Every stage of `operational_flow_walkthrough.md` MUST cite ≥1 module from G1/G1b's inventory. |

### Operational risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-G-13 | In-repo `.windsurf/mcp_config.json` drifts from active `~/.codeium/windsurf/mcp_config.json` | Medium | G5 documents the sync mechanism (`post_write_mcp_config_sync.py`) and uses in-repo as source of truth. |
| R-G-14 | Env var inventory surfaces secret KEY NAMES that look sensitive | Low | Names only (not values) — standard operational practice; no additional mitigation needed. |
| R-G-15 | Ops scripts with no known caller are pruned out of the inventory | Medium | G5 inventories every `ops_scripts/**/*.py`; orphan scripts are marked "no known caller" but NOT excluded. |
| R-G-16 | G1 misclassifies SRC-ADR-007 context assembler as multi-layer because of F04's historical C0 discussion | Low | OOS-003 is now SUPERSEDED in v1.4; F04 is L1. Use v1.4 baseline only. |

### Cross-wave risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-G-17 | G7 can't assemble traceability matrix because an earlier sub-wave's YAML is malformed | High | Per-sub-wave validation checklist in `output_contracts.md` §Validation; must pass before sub-wave closes. |
| R-G-18 | B7 deferred work re-opens during G execution and blocks progress | Medium | Policy: B7 signals are recorded only — never closed inside G. If a G sub-wave blocks on a B7 fact, mark the sub-wave's stop as "partial, blocked on B7-<id>" and continue. |
| R-G-19 | Refactor temptation: someone edits code to fit a tidier taxonomy | Critical | Hard prohibition: G authors ONLY produce documentation. Any proposed code change lives in `G6_taxonomy_cleanup/proposed_consolidation_followups.md` and requires a separate HITL wave to execute. |
| R-G-20 | Scope creep into Wave E/F graph authoring | Critical | G may NOT author atoms, edges, sources, or exclusions. Any such authoring re-opens Wave E/F. |

## Biggest blind spots to watch (top 5)

1. **Dynamic wiring** (R-G-02): `importlib`, `__import__`, string-keyed dispatch tables, plugin registries. These will look like low-degree nodes in the ADG but be high-degree at runtime. G2 must enumerate every dynamic-import site explicitly.
2. **Duplicate responsibilities across `agentic_core/` ↔ `tools/` ↔ `infrastructure/`** (R-G-09): Redis clients, MCP transports, retrieval adapters, embeddings. Easy to catalogue each in isolation and miss the duplication.
3. **Seams declared but not used** (G2 `seam_usage_report.md`): a seam that has zero callers is a runtime anti-pattern — it signals either dead code or direct cross-layer imports bypassing the seam.
4. **Control-plane rules with no code enforcer** (G4b): constitutional rules that are doctrine-only must be labelled, otherwise G7's operational flow will overstate enforcement.
5. **Eval spine trace-to-write boundary** (G3b): the transition from F08 evaluation outcomes to F09 UWG writes is the load-bearing integrity path in the whole system. Missing a step here invalidates the operational flow walk.

## Definition of "done" for Wave G as a whole

All four conditions hold simultaneously:

1. Every v1.3 atom (60 ACTIVE) has at least one embodying module in `G7_runtime_map/traceability_matrix.yaml`, OR is explicitly recorded in `G7_runtime_map/open_questions.md` as a runtime-missing atom (with an owner tagged for follow-up).
2. Every v1.3 edge (26) has a call-chain in the traceability matrix, OR is recorded as B7 candidate / runtime-missing edge.
3. Every repo surface enumerated in `repo_surface_inventory.md` is classified in at least one G1–G6 artefact.
4. `G7_runtime_map/operational_flow_walkthrough.md` has a single end-to-end walk from operator trigger through memory write-back, citing only concrete modules and v1.3 IDs.
