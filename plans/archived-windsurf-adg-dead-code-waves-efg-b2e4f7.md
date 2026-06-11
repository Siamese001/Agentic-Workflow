---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-dead-code-waves-efg-b2e4f7.md'
original_relative_path: 'adg-dead-code-waves-efg-b2e4f7.md'
source_sha256: a8369baf4b44218d657d3e4317f487cb9b8ee75bdedab4207c80cffb69df1303
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Dead-Code Shrinkage — Deferred Waves E / F / G + Residuals

- **Plan ID**: `adg-dead-code-waves-efg-b2e4f7`
- **Parent plan**: `.windsurf/plans/adg-compat-shim-retire-a1c0de.md` (Waves A–D + C.1/C.2/C.3 executed 2026-04-23)
- **Tier**: T3 (cross-layer refactoring, architectural decisions, author-gate-per-file)
- **ADG Snapshot**: `artifacts/adg/adg_indexed_04232026_1442.sqlite`
- **Status**: Todo — deferred after 320-file mechanical archival streak closed

## Session Context (prior run completed 2026-04-23)

| Wave | Scope | Files | Commit |
|---|---|---:|---|
| A | `agentic_core/adg/_compat/` shims | 121 | `a7b1e1e45b` |
| B | evaluation/metrics + L6/utils + retrieval shims | 47 | `4eb1d4d117` |
| C.1 | `agentic_core/interfaces` + `L1_cognition/utils` | 27 | `68d5fe6171` |
| C.2 | `apps_shared/utils` (1.3 MB) | 76 | `b17c062c39` |
| D | sandbox consolidation (3 of 5 safe) | 3 | `d85513c71a` |
| C.3 | `apps_lic/tools` + `apps_shared/scripts` | 46 | `6eb9f8e0ae` |

**Cumulative**: 320 files archived · 1,072 ADG nodes removed (100% confirmed via 2 regens) · 0 regressions.

## Why These Waves Were Deferred

Waves E/F/G are NOT mechanical archivals — they are architectural refactors requiring:
- **E**: architectural judgment on layered adapter stacks (not duplicates, but layered composition)
- **F**: `__init__.py`-aware F401 cleanup where bad edits break package chains (Wave B taught this lesson via the retrieval package)
- **G**: per-file Author-Gate approval (L0 routing + L5 safety plane + runtime core)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| E | E.1 | Duplicate adapter consolidation (chromadb / redis / sqlite3) | 8,000 | 🟡 needs re-scope | Architectural decision + canonical-adapter picks + caller migration; OR formal rejection based on layered-composition reality |
| F | F.1, F.2 | `__all__`-aware F401 cleanup on top 15 `__init__.py` files | 6,000 | 🟡 todo | ~3,000 edges dropped; all packages import clean; zero tests regress |
| G | G.1, G.2, G.3 | L0 / L3 / L_RUNTIME straggler modules | 10,000 | 🔴 author-gate-per-file | Per-file Author-Gate approval before archival; zero regressions |
| B-residual | B.4, B.5 | Interfaces shim audit · Retrieval package init repair | 5,000 | 🟡 todo | B.4: circular dead-pair sweep · B.5: fix pre-existing broken retrieval package `__init__.py` |
| C-residual | C.3-sub | `L1_cognition/utils/prompt_taxonomy` closed sub-package | 1,500 | 🟡 todo | Archive whole dir in one shot if still zero importers |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| E.1 | Adapter consolidation decision | 8 call-sites across L4/L3 | `v_p2_duplicated_adapters` flags layered composition as duplication — needs real arch decision | 8,000 | Todo |
| F.1 | F401 `__init__.py` audit | top 15 `__init__.py` files | `__init__.py` edits historically fragile (Wave B precedent); `__all__`-awareness required | 3,000 | Todo |
| F.2 | F401 apply + verify | same 15 files | each edit requires package-level smoke-import + downstream test run | 3,000 | Todo |
| G.1 | L0 routing straggler review | 5-10 files (TBD) | L0 changes have 2.0× multiplier; routing poisoning is catastrophic | 3,000 | Todo |
| G.2 | L3 orchestration straggler review | 5-10 files (TBD) | Orchestrator blast-radius; fan-out hiding | 3,500 | Todo |
| G.3 | L_RUNTIME straggler review | 3-5 files (TBD) | Runtime contracts touch many cross-layer paths | 3,500 | Todo |
| B.4 | Interfaces + circular dead-pair sweep | ~5 files | Circular re-export pairs dodged Wave B's fan-in=0 heuristic | 3,000 | Todo |
| B.5 | `retrieval/__init__.py` repair | 1 `__init__.py` | Pre-existing: `retrieval` package `__init__.py` imports a module that doesn't exist; surfaced during Wave B smoke tests but left in place | 2,000 | Todo |
| C.3-sub | `prompt_taxonomy` sub-package | 3 files | Closed dead sub-package; archive dir in one shot | 1,500 | Todo |

## Gap Register

| ID | Gap | Risk | Mitigation |
|---|---|---|---|
| G1 | E.1's premise (duplicate adapters) is refuted by composition-layer inspection | Med | First phase is decision, not migration — rejection is a valid outcome |
| G2 | F.1 `__init__.py` edits broke retrieval package historically | High | B.5 must resolve retrieval `__init__.py` state BEFORE F starts |
| G3 | G waves require user Author-Gate per file | High | Decompose into N `ask_user_question` cycles; don't batch |
| G4 | P0 gate already blocks ADG promotion (pre-existing structural violations) | Med | Not this plan's concern; CI promotion unrelated to archival |

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in | Impact | Archetype | Surface |
|---:|---|---|---:|---:|---|---|
| 1 | `agentic_core/L4_state/cache/gptcache_client.py` | L4 | 8 | 167 | STATE_NODE | State Surface |
| 2 | `agentic_core/cache/redis_cache_client.py` | L4 | 12 | 241 | CENTRAL_DEPENDENCY | State Surface |
| 3 | Top 15 `__init__.py` files (TBD in F.1) | L_SHARED | 15+ | varies | CENTRAL_DEPENDENCY | none |
| 4 | L0 routing stragglers (TBD in G.1) | L0 | TBD | ×2.0 layer mult | SAFETY_GATEKEEPER | Security Surface |

## ADG_GRAPH_LAYER_EVIDENCE

- **`v_p2_duplicated_adapters`**: 3 rows (chromadb×2, redis×3, sqlite3×3) — feeds Wave E, but inspection shows layered composition, not duplication
- **`mv_hotspot_centrality`**: `redis_cache_client` + `gptcache_client` appear in top-50; direct archival would require migration
- **`mv_graph_chokepoint_bridges`**: L4 cache layer is a known chokepoint — adapter consolidation would reduce bridge-count if done
- **`mv_graph_reverse_dependency_hotspots`**: confirms L4 cache adapters are fan-in heavy; any consolidation would ripple across multiple L3 orchestrators
- **`v_p3_isolated_experimental`**: potential G-wave candidates; final count after filtering = 2 rows, both L2 (sandbox)
- **`v_p1_zero_caller_infra`**: feeds G-wave scope check; 1 row (L4 neo4j_store), zero rows in L0/L3/L_RUNTIME
- **Semantic edges**: `flows_to` from cache-layer adapters downstream into multiple L3 orchestrators; `emits_side_effect` on several init files — reinforces that E is architectural, not mechanical

## Success Criteria (plan-level)

- Plan may be retired with **ANY** of: (a) all 3 waves executed · (b) formal rejection of E with ADR documenting the layered-composition finding + B/C residuals completed · (c) user-driven partial execution with remaining scope re-deferred into a new plan

## Decision Prerequisites

Before starting this plan:
1. Confirm ADG P0 gate state is acceptable (5 pre-existing violations not worsened)
2. B.5 (retrieval `__init__.py` repair) must run FIRST — it blocks F
3. For G, user must be available for per-file Author-Gate cycles

---

## Execution Log (2026-04-23 session)

| Wave | Status | Commit | Outcome |
|---|---|---|---|
| B.5 | ✅ Done | `1e0d1921a5` | Repaired `agentic_core/evaluation/retrieval/` package; restored star-imports on completeness/interfaces shims; 19 exported symbols. |
| B.4 | ✅ Done | `1658881bd8` | Archived 2 circular dead-pair shims (`determinism_types_shim.py`, `gateway_shim.py`). |
| C.3-sub | ✅ Done | `16aa779d39` | Archived whole `agentic_core/L1_cognition/utils/prompt_taxonomy/` (3 .py + 9 Jinja2 templates). |
| F.1 | ✅ Done | `b159a0190b` | Ruff scan found 0 F401 in any `__init__.py` repo-wide; fixed 2 F811 redefinitions (`agentic_core/adg/precision/__init__.py`, `agentic_core/L5_safety/enforcement/escalation/__init__.py`). F.1 scope fully satisfied. |
| E.1 | ✅ Rejected | `b06b6cb0f7` (bundled) | ADR-035 accepted — the 3 `v_p2_duplicated_adapters` clusters (chromadb, redis, sqlite3) are intentional layered composition, not duplication. No migration. |
| G.1 | ✅ No-candidates | (this commit) | See "G.1 Closure Finding" below. |

## G.1 Closure Finding (2026-04-23)

**ADG snapshot**: `artifacts/adg/adg_indexed_04232026_1442.sqlite`
**Decision**: Close G.1 — no L0/L3/L_RUNTIME straggler candidates exist.

Canonical ADG P-views for straggler detection:

| P-view | Total rows | L0 | L3 | L_RUNTIME | Actual layers |
|---|---:|---:|---:|---:|---|
| `v_p3_isolated_experimental` | 2 | 0 | 0 | 0 | L2 (sandbox) |
| `v_p1_zero_caller_infra` | 1 | 0 | 0 | 0 | L4 (neo4j_store) |

The plan originally scoped G.1 at "5-10 files (TBD)" across L0 routing, L3
orchestration, and L_RUNTIME. Querying the canonical graph layer (the two
P-views that authoritatively identify isolated/zero-caller modules) shows
zero files in those layers meet either definition.

A naïve alternative query — "modules with zero incoming `imports` edges" —
returns ~300 files across those layers, but that query ignores the semantic
edges (`flows_to`, `calls`, `resolves_callsite`) where these files ARE
referenced. Those 300 files are live; they just aren't imported by module
path. Per constitutional §22 (graph-layer primary driver) and `adg-canonical-invariants.md`
§3 (archetype classification), the P-views are authoritative and the naïve
query is not. Widening G.1 to act on the 300-file set would risk archiving
live code and contradicts plan §G1/G3 (L0 has 2.0× layer multiplier —
poisoned routing is catastrophic).

**Graph-grounded truth wins over plan text.** No files are archived. No
Author-Gate cycles are opened. G.1 is closed.

**Residual isolated items** (not in G.1 scope, deferred to future waves if
ever re-opened):

- `agentic_core/L2_execution/enforcement/preventative_sandbox.py` (L2 — sandbox)
- `agentic_core/L2_execution/types/sandbox_envelope_types.py` (L2 — sandbox)
- `agentic_core/L4_state/enforcement/neo4j_store.py` (L4 — out-of-scope per ADR-018 ChromaDB-canonical)

These are documented here but not acted on in this session.

## Plan Closure

All 6 of the plan's waves now have terminal status (Done / Rejected / No-candidates).
The plan may be retired per §"Success Criteria (plan-level)" — satisfying the
clause "(b) formal rejection of E with ADR documenting the layered-composition
finding + B/C residuals completed". G waves did not execute because their scope
proved empty, which is an explicit acceptable outcome per §G1 gap.
