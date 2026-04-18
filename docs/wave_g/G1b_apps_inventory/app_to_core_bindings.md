# G1b — App-to-Core Bindings

All bindings derived from static AST import analysis of every `.py` under `apps_*/`, with target paths resolved against G1 `component_inventory.yaml` (2,014 modules). Zero unresolved imports.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Resolver source**: `docs/wave_g/G1_core_runtime_inventory/component_inventory.yaml`.

## 1. Top binding hotspots (core modules imported by multiple apps)

| # apps | `agentic_core` module | G1 layer | Likely nature |
|---:|---|---|---|
| **7** | `agentic_core.adg.runtime.behavioral_index` | CROSS_CUTTING (`adg/`) | ADG-runtime behavioral index; used for disposition/routing signals across apps |
| **6** | `agentic_core.L3_orchestration.inference.qwen_vllm` | L3 | Direct L3 inference target — VLLM-backed qwen model driver |
| **6** | `agentic_core.adg.applications.execute_ssot_integration` | CROSS_CUTTING (`adg/`) | SSOT integration helper consumed by app pipelines |
| **6** | `agentic_core.runtime.contracts.lifecycle_trace_contract` | CROSS_CUTTING (`runtime/`) | Lifecycle trace contract — the runtime-scaffold contract apps bind against |
| **5** | `agentic_core.mixins.embedding_mixin` | CROSS_CUTTING (`mixins/`) | Embedding composition mixin |
| **5** | `agentic_core.mixins.semantic_cache_mixin` | CROSS_CUTTING (`mixins/`) | Semantic cache composition mixin |
| **5** | `agentic_core.L2_execution.types.local_first_disposition` | L2 | Typed disposition enum for execution-local-first policy |
| **5** | `agentic_core.L2_execution.types.vllm_gateway_adapter_types` | L2 | Adapter types for VLLM gateway binding |
| **5** | `agentic_core.L4_state.config.vllm_routing_predicates` | L4 | Routing predicates for VLLM (L4-owned config surface) |
| **3** | `agentic_core.L0_routing.config` | L0 | Routing config |
| **3** | `agentic_core.L0_routing.config.path_constants` | L0 | Path constants for L0 routing |
| **3** | `agentic_core.L4_state.enforcement.graph_memory_bridge` | L4 | Graph-memory bridge enforcement |
| **2** | `agentic_core.L1_cognition.reasoning.meta_client` | L1 | L1 meta client |
| **2** | `agentic_core.L1_cognition.types.client_types` | L1 | L1 client types |
| **2** | `agentic_core.L1_cognition.utils.guardrails_util` | L1 | L1 guardrails util |
| **2** | `agentic_core.L2_execution.utils` | L2 | L2 util package |
| **2** | `agentic_core.base_agents.SovereignBaseAgent` | CROSS_CUTTING (`base_agents/`) | Canonical base-agent class |
| **2** | `agentic_core.interfaces.gateway` | CROSS_CUTTING (`interfaces/`) | Gateway interface |
| **2** | `agentic_core.interfaces.mixins` | CROSS_CUTTING (`interfaces/`) | Mixin interfaces |
| **2** | `agentic_core.interfaces.spine` | CROSS_CUTTING (`interfaces/`) | Spine interface |

## 2. Per-app binding profile

Counts below are **import-statement occurrences** (a single import statement may count once even if used many times). `CROSS_CUTTING` dominates every app that has non-zero bindings — apps compose against runtime contracts, mixins, and ADG runtime primitives far more than they reach into specific layers.

| App | CROSS_CUTTING | L0 | L1 | L2 | L3 | L4 | L5 | L6 | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| APP-EVAL | 11 | 3 | 0 | 2 | 2 | 0 | 3 | 0 | 21 |
| APP-EXEC | 36 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 40 |
| APP-LIC | 126 | 3 | 3 | 6 | 2 | 4 | 0 | 0 | 144 |
| APP-RESEARCH | 23 | 0 | 0 | 2 | 3 | 1 | 0 | 1 | 30 |
| APP-RFP | 7 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 11 |
| APP-RG | 243 | 9 | 4 | 9 | 4 | 2 | 0 | 0 | 271 |
| APP-SHARED | 363 | 30 | 1 | 2 | 5 | 8 | 3 | 3 | 415 |
| APP-UNDERWRITING_AI | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |

### Observations

- **APP-UNDERWRITING_AI has zero `agentic_core` imports** across all 72 modules. It is a pure library with no runtime coupling to core. Candidate for G2 / G7 to confirm this is intended (ingestion-only library consumed by other apps via their own agentic_core bindings).
- **APP-SHARED is the second-heaviest core consumer** (415 import occurrences) despite being library-only. This is consistent with its role as the shared primitive layer — it wraps agentic_core for app reuse.
- **APP-RG is the heaviest runtime-app consumer** (271 occurrences across 164 modules) — the flagship runtime app.
- **No app touches L5 meaningfully except APP-SHARED (3)** and APP-EVAL (3). L5 safety enforcement is expected to be core-internal, not app-consumed — consistent with architectural expectations.
- **No app touches L6 directly except APP-RESEARCH (1), APP-SHARED (3).** L6 observability is expected to record runs, not be consumed by apps — consistent.

## 3. Seam, interface, and L_CONTRACT usage

`agentic_core/seams/` (7 modules), `agentic_core/interfaces/` (38 modules), and `agentic_core/L_CONTRACTS/` (4 modules) are the sanctioned cross-boundary surfaces.

| App | seam_uses | interface_uses | l_contract_uses |
|---|---:|---:|---:|
| APP-EVAL | 0 | 0 | 0 |
| APP-EXEC | 0 | 0 | 0 |
| APP-LIC | 0 | **5** | 0 |
| APP-RESEARCH | 0 | 0 | 0 |
| APP-RFP | 0 | 0 | 0 |
| APP-RG | 0 | **5** | 0 |
| APP-SHARED | 0 | **5** | 0 |
| APP-UNDERWRITING_AI | 0 | 0 | 0 |
| **Total** | **0** | **15** (3 apps × 5 same interfaces) | **0** |

### Finding

- **No app directly imports from `agentic_core/seams/`.** Seams appear to be core-internal only. G2 must determine whether this is architecturally correct (apps should always bind through `interfaces/` or `L_CONTRACTS/`, never raw seams) or an indication of dead/underused seams.
- **No app directly imports from `agentic_core/L_CONTRACTS/`.** The 4 layer-contract modules (including `execution_trace.py`) are not app-consumed. Apps that embody F08.02 (ExecutionTrace) must do so via `L2_execution/types/execution_trace_types.py` or `L3_orchestration/types/execution_trace_types.py` (both tagged F08.02 in G1).
- **Apps that use `interfaces/` touch only 3 specific files**: `agentic_core.interfaces.gateway`, `agentic_core.interfaces.mixins`, `agentic_core.interfaces.spine`. That means the other 35 interface modules under `agentic_core/interfaces/` have zero app consumers. G2's `seam_usage_report.md` should extend this analysis to interfaces and flag unused ones.

## 4. Unresolved bindings

**None.** Every `agentic_core.*` import across all 8 apps resolved to a path in G1's `component_inventory.yaml`.

Resolution strategy used:
1. Exact dotted-module match against `path.removesuffix(".py")` → hit for normal module imports.
2. Package `__init__.py` match when the dotted module ends at a directory.
3. Prefix-reduction (drop trailing components) for `from package.module import ClassOrFunc` cases — the class/func name is trimmed; the parent module resolves.

All 243 distinct core module references across all apps resolved via step 1 or 2 or 3.

## 5. Per-app outputs / data paths

| App | Directories observed |
|---|---|
| APP-EVAL | `apps_eval/data`, `apps_eval/outputs` |
| APP-EXEC | `apps_exec/outputs` |
| APP-LIC | `apps_lic/outputs` |
| APP-RESEARCH | — |
| APP-RFP | `apps_rfp/data`, `apps_rfp/outputs` |
| APP-RG | `apps_rg/outputs` |
| APP-SHARED | `apps_shared/data` |
| APP-UNDERWRITING_AI | `apps_underwriting_ai/outputs` |

Output paths are captured for G4 storage topology. None are app-authored durable-state stores — they are scratch output locations consumed by tests and downstream tooling.
