# G2 — Seam / Interface / L_CONTRACTS Usage Report

Fan-in analysis for every designated cross-boundary surface: `agentic_core/seams/`, `agentic_core/interfaces/`, `agentic_core/L_CONTRACTS/`.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Primary source**: ADG `nodes` + `edges` tables; relation_type = `imports`.

## Headline numbers

| Surface | Module count | Inbound import edges | Distinct importer files | 0-importer modules |
|---|---:|---:|---:|---:|
| `agentic_core/seams/` | 7 | 41 | 7 (all inside core or tests) | 0 |
| `agentic_core/interfaces/` | 38 | 283 | ~60 | ≥ 30 (see §2) |
| `agentic_core/L_CONTRACTS/` | 4 | **1** | **1** (archived) | **3** |

## 1. Seams — `agentic_core/seams/` (7 modules)

### Module list and fan-in

| Seam module | Inbound imports | Importer category |
|---|---:|---|
| `agentic_core/seams/contracts/authority.py` | multi | L2 + L3 enforcement / reasoning / engines |
| `agentic_core/seams/contracts/mcp.py` | multi | L2 enforcement |
| `agentic_core/seams/contracts/safety_agents.py` | multi | L3 enforcement / reasoning |
| `agentic_core/seams/contracts/orchestration_protocols.py` | multi | tests |
| `agentic_core/seams/workflow_learning_bridge.py` | multi | tests |
| (2 more seam modules) | — | — |

### Observed importers (examples)

| Importer | Seam target |
|---|---|
| `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py` | `seams/contracts/authority.py`, `seams/contracts/mcp.py` |
| `agentic_core/L3_orchestration/enforcement/safety_strategy.py` | `seams/contracts/safety_agents.py` |
| `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` | `seams/contracts/safety_agents.py` |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_marketplace.py` | `seams/contracts/authority.py` |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py` | `seams/contracts/authority.py` |
| `tests/unit/agentic_core/seams/test_seams_hardening.py` | all 4 contract seams |

### Apps → seams

**Zero.** No app in `apps_*/` imports from `agentic_core/seams/`. This confirms the G1b finding. Classification:

- **Architectural reading**: seams are currently a core-internal cross-layer contract mechanism (L2↔L3 sovereign-filesystem-mcp, safety-strategy). Apps consume core primitives via `base_agents/`, `mixins/`, `runtime/contracts/` — NOT via `seams/`.
- **Implication for G7**: if v1.4 edges intend seams to be the sole app→core crossing, the zero-app-use signal is a `violation`. If v1.4's seam atoms scope only core-internal contracts, the signal is `expected`. v1.4 has no explicit atom asserting "apps MUST bind through seams/". **B7-G2-02**.

## 2. Interfaces — `agentic_core/interfaces/` (38 modules)

### Fan-in distribution

- Total inbound import edges: **283**.
- Top used interface modules (≥2 apps importing):
  - `agentic_core/interfaces/gateway.py`
  - `agentic_core/interfaces/mixins.py`
  - `agentic_core/interfaces/spine.py`
- **3 apps** that import from `interfaces/`: APP-LIC, APP-RG, APP-SHARED. Each touches only these same 3 interface files (per G1b finding).
- **Remaining ≈ 35 interface modules have no app consumers.**

### Breakdown

| Interface subsystem | Status |
|---|---|
| `interfaces/gateway.py` | **consumed** by 2 apps + core |
| `interfaces/mixins.py` | **consumed** by 2 apps + core |
| `interfaces/spine.py` | **consumed** by 2 apps + core |
| Other 35 interface modules | consumed by core only (or not at all) |

### Interpretation

`interfaces/` has a live, load-bearing subset (gateway, mixins, spine) that carries most of its 283 inbound edges. The remaining 35 modules are either:
- Future-facing (declared for upcoming bindings not yet wired in core or apps), or
- Dead (never wired).

G6 should inspect the 35 unused interface modules for classification (live-but-core-only vs dead). No B7 candidate created at G2.

## 3. L_CONTRACTS — `agentic_core/L_CONTRACTS/` (4 modules)

### Module list

| L_CONTRACTS module | Inbound imports |
|---|---:|
| `agentic_core/L_CONTRACTS/execution_trace.py` | **1** (from archive) |
| `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` | **1** (from archive) |
| (2 other L_CONTRACTS modules) | **0** |

### The one observed importer

```
tools/archive/ops_scripts_ci_oneshots_w4.2/_typed_tool_gate.py
  -> agentic_core/L_CONTRACTS/lifecycle_trace_contract.py
```

**This is the only inbound import across all 4 L_CONTRACTS modules, and it comes from an archived tool.** No live production code under `agentic_core/`, `apps_*/`, `tools/mcp/`, or `ops_scripts/` imports from `L_CONTRACTS/`.

### Critical finding

`agentic_core/L_CONTRACTS/` is **effectively dead code** in runtime terms. Four modules with coordinated "layer-contract" semantics exist, but nothing consumes them except one archived importer.

**Options for classification**:
1. **Dead infrastructure** — G6 should propose deletion / archival.
2. **Declared-but-not-wired layer contracts** — architectural intent was for L_CONTRACTS to be the canonical cross-layer binding surface; production code never migrated. A B7 candidate in the "missing interaction" sense: every cross-layer import should go through L_CONTRACTS, but 124,904 cross-layer edges skip it.
3. **Documentation-only surface** — L_CONTRACTS serves as a specification reference, consumed only by humans.

Decision is **B7-G2-01**, deferred to G7 and ultimately to the deferred B7 interaction-completeness wave. G2 does not close it.

### Implication: execution trace is duplicated, L_CONTRACTS copy is unused

G1's layer_embodiment_map reported 3 hosts for F08.02 (ExecutionTrace):
- `agentic_core/L2_execution/types/execution_trace_types.py` ← live
- `agentic_core/L3_orchestration/types/execution_trace_types.py` ← live (duplicate — G6 candidate)
- `agentic_core/L_CONTRACTS/execution_trace.py` ← **0 live imports**

The canonical-seeming L_CONTRACTS copy is the unused one.

## 4. Apps' declared boundary — what they actually cross

Per G1b, every app's binding surface is:

| App | Imports seams | Imports interfaces | Imports L_CONTRACTS |
|---|---|---|---|
| APP-EVAL | 0 | 0 | 0 |
| APP-EXEC | 0 | 0 | 0 |
| APP-LIC | 0 | ✓ (5) | 0 |
| APP-RESEARCH | 0 | 0 | 0 |
| APP-RFP | 0 | 0 | 0 |
| APP-RG | 0 | ✓ (5) | 0 |
| APP-SHARED | 0 | ✓ (5) | 0 |
| APP-UNDERWRITING_AI | 0 | 0 | 0 |

5 of 8 apps import NO sanctioned cross-boundary surface at all. They reach directly into `agentic_core/runtime/contracts/lifecycle_trace_contract.py`, `agentic_core/mixins/*`, `agentic_core/base_agents/SovereignBaseAgent.py`, `agentic_core/L0/L2/L3/L4/...` types. This is the source of the 137 authority-boundary breaches classified as `L_APP_core_bypass` (see `boundary_violations.md`).

## 5. Summary classifications

| Surface | Status | Classification |
|---|---|---|
| Seams | Narrowly used (7 core importers, 0 apps) | architectural — core-internal today |
| Interfaces | Partially used (3 of 38 live; 35 dormant) | mixed — G6 should inspect |
| L_CONTRACTS | Effectively dead (1 archived importer total) | **B7-G2-01** — dead or missing-wiring |

## 6. Hand-offs

- **G2b**: consumes this file's `interfaces/gateway.py` observation — gateway interface is live on 2 apps; G2b should trace the concrete gateway class and its provider implementations.
- **G3**: consumes this file's seam-importer list to identify pipeline entry points that cross the L2↔L3 seam.
- **G6**: owner of (a) 35 unused interface modules, (b) 4 L_CONTRACTS modules, (c) duplicate `execution_trace_types.py` pairs.
- **G7 `b7_candidate_register.md`**: records B7-G2-01 (L_CONTRACTS dead), B7-G2-02 (apps-seam-zero-use).
