# G1 — Cross-Cutting Classification

G1 recorded **801** of 2,014 `agentic_core/` modules as `layer: CROSS_CUTTING` (≈39.8%). Per the G0 scope rule, cross-cutting is **exclusive**: a module either has a layer (L0–L6) or is CROSS_CUTTING, never both. This document catalogues each CROSS_CUTTING subsystem with its size, top roles, canonical purpose, and downstream owner.

All data below is derivable from `component_inventory.yaml` by filtering `layer: CROSS_CUTTING`.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Subsystem table

| Subsystem path | Module count | Dominant roles | Purpose | Downstream owner |
|---|---:|---|---|---|
| `agentic_core/adg/` | 277 | other, util, contract | AST Dependency Graph runtime and extractors. Tool-side of what `tools/adg/` and `tools/mcp/adg/` expose over MCP. Large bucket because ADG has parsers, analyzers, applications, clients, processing, artifact handlers — each a small module family. | G2 (wiring uses ADG), G5 (MCP registry), G6 (role refinement on `other`-tagged internals) |
| `agentic_core/evaluation/` | 85 | other, reasoner, contract | Evaluation subsystem. Hosts metrics/, judges/, retrieval/, monitoring/, feedback/, etc. Candidate host for F08 evaluation-spine atoms (F08.01, F08.05). | G3b (exit/eval/replay traceability), G7 (atom-to-module mapping for F08 family) |
| `agentic_core/knowledge/` | 82 | other, reader, util | Knowledge bases, document loaders, chunking, retrieval, ingestion, canonical stores. Candidate host for F02/F04 plan-input atoms. | G4 (storage topology — knowledge-backed stores), G7 |
| `agentic_core/utils/` | 65 | util | Shared utilities used by multiple layers. Classic grab-bag; no single layer owns these. | G6 (classify which are truly cross-cutting vs layer-specific strays) |
| `agentic_core/runtime/` | 62 | runtime-scaffold, contract | Runtime scaffold: `config/`, `contracts/`, `engine/`, `exceptions/`, `types/`, `utils/`, `enforcement/`. The engine-level plumbing under which all layers run. | G2 (wiring; runtime is the root of many call-chains), G4b (runtime config knobs) |
| `agentic_core/mixins/` | 55 | mixin | Composition mixins reused across layers (telemetry, retry, validation, etc.). Must remain CROSS_CUTTING per G0 rule — they have no layer home. | G2 (their consumers span layers) |
| `agentic_core/prompt_governance/` | 43 | policy, other, reasoner | Governance over prompt surfaces. Candidate host for F11 sub-claims on prompt policy. Has `core/`, `security/`, `scripts/`. | G4b (prompt surface + rules map), G7 |
| `agentic_core/interfaces/` | 38 | interface | Typed interface surfaces that layers implement or depend on. Each interface in here likely corresponds to a v1.4 edge target. | G2 (seams + interfaces are the sanctioned crossing points) |
| `agentic_core/config/` | 24 | runtime-scaffold, contract | Core-level config. Runtime knob surface separate from per-layer `*/config/` dirs. | G4b (config catalogue) |
| `agentic_core/cache/` | 20 | reader, util | Shared in-process cache surfaces. Distinct from `L4_state/cache/` — this one is cross-cutting, not durable-state. | G4 (cache surface inventory) |
| `agentic_core/base_agents/` | 11 | agent, contract | Agent base classes used by `agentic_core/agents/` and per-layer agents. Inheritance roots. | G1b (apps re-inherit these), G7 |
| `agentic_core/embeddings/` | 9 | util, other | Vector embeddings support. Pairs with `tools/mcp/vector_db_server.py`. | G2b (provider/egress), G4 (vector storage) |
| `agentic_core/seams/` | 7 | seam | Explicit seam authority. Small on purpose: seams are contracts, not implementations. | G2 (seam usage report) |
| `agentic_core/agents/` | 6 | agent | Concrete agents registered at runtime. | G1b (apps often bind through these), G2 |
| `agentic_core/case_memory/` | 4 | reader | Case-specific memory surface. Special — link to F12 memory lifecycle unclear at G1. | G4 (memory stores), G4b (memory rules), G6 (classify) |
| `agentic_core/L_CONTRACTS/` | 4 | contract | Layer-to-layer contract surface. Candidate canonical embodiment target for seam atoms. | G2 (formal contracts), G7 |
| `agentic_core/core/` | 2 | runtime-scaffold, other | Thin "core" shim under `agentic_core/core/`. Possibly legacy; needs classification. | G6 (special surface) |
| `agentic_core/_compat/` | 2 | shim | Compat shims for backward-compat imports. | G6 (shim discipline) |
| `agentic_core/cloud_native/` | 1 | other | Single file; unclear role. | G6 (classify) |
| `agentic_core/gateway/` | 1 | other | External-gateway stub. Pairs with `infrastructure/sdks_mcps/`. | G2b (provider/egress) |
| `agentic_core/tracing/` | 1 | other | Single file tracing stub. Pairs with `tools/otel/`. | G3b (replay/exit/eval trace paths), G5 (otel integration) |
| `agentic_core/visualization/` | 1 | other | Single file; unclear role. | G6 (classify) |
| `agentic_core/__init__.py` | 1 | other | Top-level package init. | (none — packaging) |
| **Total CROSS_CUTTING** | **801** | — | — | — |

## Biggest buckets (by size)

Top 5 cross-cutting subsystems by module count:

1. **`adg/` (277 modules, 34.6% of CROSS_CUTTING)** — dominant bucket. Not part of the agentic runtime per se; it is the dependency-graph infrastructure the whole repo uses. Large because it parses, analyzes, models, stores, and serves the graph, each in small modules.
2. **`evaluation/` (85)** — F08 atoms map here; will be sharpened in G3b/G7.
3. **`knowledge/` (82)** — F02/F04 inputs; will be sharpened in G4/G7.
4. **`utils/` (65)** — generic utilities. G6 candidate for cleanup (some are layer-specific strays).
5. **`runtime/` (62)** — scaffold; G2 will rely on this as a root.

## Classification discipline honored

- **No double-homing**: every CROSS_CUTTING module has `layer: CROSS_CUTTING` and no layer atom anchor. Layer-anchor atoms (F02.01 etc.) are attached only to modules physically inside `agentic_core/Lx_*/`.
- **Mixins stay mixins**: all 55 modules in `mixins/` are role=`mixin` (not re-classified into the layers they are mixed into).
- **Seams vs interfaces**: `seams/` (7) are role=`seam`; `interfaces/` (38) are role=`interface`. Both are CROSS_CUTTING.
- **Special surfaces (`cloud_native/`, `case_memory/`, `visualization/`, `core/`, `_compat/`, `gateway/`, `tracing/`) are isolated** and will be re-classified in G6 — G1 holds them as CROSS_CUTTING with their best-guess role.

## Special-handling surfaces (from G0 spec) — status

The G0 spec listed 21 subsystems that must be preserved with special handling. All 21 are present in the inventory and classified exactly as CROSS_CUTTING (where applicable):

| Subsystem | G0 listed? | G1 state |
|---|---|---|
| `runtime/` | ✅ | 62 modules, dominant role runtime-scaffold |
| `agents/` | ✅ | 6 modules, role agent |
| `base_agents/` | ✅ | 11 modules, role agent/contract |
| `seams/` | ✅ | 7 modules, role seam |
| `interfaces/` | ✅ | 38 modules, role interface |
| `mixins/` | ✅ | 55 modules, role mixin |
| `evaluation/` | ✅ | 85 modules |
| `prompt_governance/` | ✅ | 43 modules |
| `knowledge/` | ✅ | 82 modules |
| `adg/` | ✅ | 277 modules |
| `cache/` | ✅ | 20 modules |
| `case_memory/` | ✅ | 4 modules |
| `embeddings/` | ✅ | 9 modules |
| `gateway/` | ✅ | 1 module |
| `tracing/` | ✅ | 1 module |
| `cloud_native/` | ✅ | 1 module |
| `core/` | ✅ | 2 modules |
| `visualization/` | ✅ | 1 module |
| `config/` | ✅ | 24 modules |
| `_compat/` | ✅ | 2 modules |
| `utils/` | ✅ | 65 modules |

**Gaps**: none — every G0-requested subsystem is catalogued.
