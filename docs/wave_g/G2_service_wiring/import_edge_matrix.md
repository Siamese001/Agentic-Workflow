# G2 — Import Edge Matrix

Layer × layer import counts derived from the ADG SQLite (`mv_new_cross_layer_dependencies`, `imports` relation only). Every non-zero cell is classified as `expected`, `unexpected`, or `violation`.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Primary source view**: `mv_new_cross_layer_dependencies` — 162 distinct (src_layer, dst_layer, relation_type) tuples.

## ADG layer taxonomy

ADG recognizes 17 layer partitions (v1.4 only specifies `L0..L6 + CROSS_CUTTING`). G2 uses ADG's richer split and maps back:

| ADG layer | v1.4 mapping | Membership |
|---|---|---|
| `L0` | L0 | `agentic_core/L0_routing/` (88 modules) |
| `L1` | L1 | `agentic_core/L1_cognition/` (152) |
| `L2` | L2 | `agentic_core/L2_execution/` (194) |
| `L3` | L3 | `agentic_core/L3_orchestration/` (167) |
| `L4` | L4 | `agentic_core/L4_state/` (141) |
| `L5` | L5 | `agentic_core/L5_safety/` (382) |
| `L6` | L6 | `agentic_core/L6_observability/` (89) |
| `L_RUNTIME` | CROSS_CUTTING | `agentic_core/runtime/`, `agentic_core/L_CONTRACTS/` |
| `L_SHARED` | CROSS_CUTTING + apps_shared | `agentic_core/cache/`, `agentic_core/mixins/`, `agentic_core/base_agents/`, `apps_shared/` |
| `L_APP` | apps_* | 6 runtime apps + `apps_underwriting_ai/` |
| `L_PG` | CROSS_CUTTING | `agentic_core/prompt_governance/` |
| `L_TOOLS` | out-of-scope for v1.4 | `tools/`, parts of `agentic_core/adg/` |
| `L_OPS` | out-of-scope | `ops_scripts/`, `.claude/governance/scripts/` |
| `L_INFRA` | out-of-scope | `infrastructure/` |
| `L_SL` | out-of-scope | `system_learning/` |
| `L_TEST` | out-of-scope | `tests/` |
| `L_UNKNOWN` | unclassified | modules ADG could not layer-assign (37+ files) |

## Full matrix (imports only)

Columns = destination. Rows = source. Values = edge count. `-` = zero.

| src \ dst | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L_APP | L_INFRA | L_OPS | L_PG | L_RUNTIME | L_SHARED | L_SL | L_TOOLS | L_UNKNOWN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **L0** | - | - | 12 | - | 10 | 4 | 2 | - | - | 9 | 5 | **2324** | 7 | 1 | 3 | 1 |
| **L1** | 17 | - | 11 | 4 | 9 | - | 2 | - | - | - | - | **4741** | 14 | 3 | 1 | - |
| **L2** | 39 | 2 | - | 4 | 37 | 19 | 7 | 1 | - | - | - | **9485** | 52 | 2 | 1 | - |
| **L3** | 54 | 3 | 30 | - | 5 | 3 | 11 | 5 | - | 1 | 4 | **5677** | 63 | 2 | 4 | - |
| **L4** | 11 | - | 14 | 5 | - | 2 | 2 | - | - | - | 1 | **6184** | 45 | 13 | 3 | - |
| **L5** | 368 | 2 | 78 | 9 | 12 | - | 1 | - | - | 14 | 1 | **21958** | 209 | 6 | 17 | - |
| **L6** | 23 | - | 21 | 2 | - | 8 | - | 1 | - | 1 | - | **2462** | 16 | 10 | 8 | - |
| **L_APP** | 58 | 11 | 24 | 30 | 22 | 7 | 5 | - | - | - | 5 | **20862** | 105 | 7 | 16 | - |
| **L_INFRA** | - | - | - | - | - | - | - | - | - | - | - | 17 | - | 1 | - | - |
| **L_OPS** | 699 | 4 | 14 | 7 | 7 | 26 | 1 | 14 | - | - | - | **15664** | 84 | 20 | 2 | - |
| **L_PG** | 30 | - | - | - | 4 | 2 | - | - | - | - | - | 1662 | 7 | 2 | 2 | - |
| **L_RUNTIME** | 25 | 1 | 4 | - | - | 5 | 1 | - | - | - | - | - | 13 | - | - | - |
| **L_SHARED** | 81 | 3 | 26 | 4 | 20 | 104 | 23 | 9 | - | 3 | 7 | 7550 | - | 20 | 11 | - |
| **L_SL** | 46 | - | 1 | - | 3 | 2 | 2 | 2 | - | - | 1 | 8043 | 56 | - | 2 | - |
| **L_TOOLS** | 169 | 2 | 55 | 58 | 24 | 125 | 35 | 58 | - | 4 | 6 | 10042 | 56 | 24 | - | 71 |
| **L_UNKNOWN** | - | - | - | - | - | - | - | - | - | - | - | 10 | 2 | - | - | - |
| **L_TEST** (not in principal diagonal, shown for reference) | — | 401 (→L3) | — | 401 | — | — | — | — | — | — | — | 372 | 403 | — | 975 | 1029 |

**Grand total cross-layer edges** (matches `mv_snapshot_baseline.cross_layer_edge_count`): **124,904**.

## Classification rules

- **`expected`**: edge matches v1.4 intended-wiring baseline. Intended edges:
  - any layer → L_RUNTIME (runtime contracts, exceptions, types).
  - Lx → Lx+1 in the intended control flow (per v1.4 SRC-ADR-008 L3→L2, SRC-ADR-009 L2→L3, SRC-ADR-007 L1→L4 context, SRC-ADR-003 eval→L5→UWG).
  - L_APP → L_SHARED, L_APP → L_RUNTIME, L_APP → L2/L3/L4 (apps consume layered primitives).
  - L_TEST → any (tests exercise all layers).
  - L_TOOLS → any (tools observe/analyze all layers).
  - L_OPS → any (ops scripts drive all layers).
  - Intra-core CROSS_CUTTING ↔ layered (runtime scaffolding, shared mixins).
- **`unexpected`**: edge is not architecturally forbidden but is not first-classed in v1.4. Candidate for future B7 interaction or v1.4 extension.
- **`violation`**: edge is pre-classified in `mv_authority_boundary_breaches` (137 rows) OR writes durable state outside UWG (1,821 rows in `mv_write_sovereignty_paths`). See `boundary_violations.md`.

## Top 20 edges by count (imports relation)

| # | src | dst | count | classification | reason |
|---|---|---|---:|---|---|
| 1 | L5 | L_RUNTIME | 21,958 | **expected** | L5 enforcement uses runtime contracts everywhere |
| 2 | L_APP | L_RUNTIME | 20,862 | **expected** | apps bind lifecycle_trace_contract + runtime types |
| 3 | L_OPS | L_RUNTIME | 15,664 | **expected** | ops scripts use runtime types |
| 4 | L_TOOLS | L_RUNTIME | 10,042 | **expected** | tools use runtime types |
| 5 | L2 | L_RUNTIME | 9,485 | **expected** | L2 executes via runtime scaffolding |
| 6 | L_SL | L_RUNTIME | 8,043 | **expected** | system_learning uses runtime contracts |
| 7 | L_SHARED | L_RUNTIME | 7,550 | **expected** | shared primitives use runtime |
| 8 | L4 | L_RUNTIME | 6,184 | **expected** | L4 uses runtime types |
| 9 | L3 | L_RUNTIME | 5,677 | **expected** | L3 orchestration uses runtime |
| 10 | L1 | L_RUNTIME | 4,741 | **expected** | L1 uses runtime |
| 11 | L0 | L_RUNTIME | 2,324 | **expected** | L0 uses runtime |
| 12 | L6 | L_RUNTIME | 2,462 | **expected** | L6 observability uses runtime |
| 13 | L_PG | L_RUNTIME | 1,662 | **expected** | prompt_governance uses runtime |
| 14 | L_OPS | L0 | 699 | **expected** | ops scripts inspect L0 config (path_constants is a key bridge) |
| 15 | L_TEST | L_UNKNOWN | 1,029 | unexpected | tests importing unclassified modules — suggests L_UNKNOWN has real surface area |
| 16 | L_TEST | L_TOOLS | 975 | **expected** | tests exercise tools |
| 17 | L5 | L0 | 368 | **expected** | L5 enforces on L0 routing (SRC-RULE-001) |
| 18 | L_TEST | L_SHARED | 403 | **expected** | tests exercise shared |
| 19 | L_TEST | L3 | 401 | **expected** | tests exercise orchestration |
| 20 | L_TEST | L_RUNTIME | 372 | **expected** | tests exercise runtime |

## Top 15 unexpected or violation edges

| # | src | dst | count | classification | detail |
|---|---|---|---:|---|---|
| 1 | L6 | L0 | 23 | **violation** | L6 downstream_mutation; L6_observability/__init__.py imports L0/config/path_constants multiple times — breach_class `L6_downstream_mutation` |
| 2 | L6 | L2 | 21 | **violation** | L6 downstream_mutation — L6 types import L2 execution internals |
| 3 | L_APP | L0 | 58 | **violation** | L_APP_core_bypass — apps (top offender: `apps_shared/config/operational_config.py`) reach into L0 directly instead of via seams |
| 4 | L_APP | L2 | 24 | **violation** | L_APP_core_bypass |
| 5 | L_APP | L1 | 11 | **violation** | L_APP_core_bypass |
| 6 | L_APP | L3 | 30 | unexpected | apps directly import L3 (e.g. `qwen_vllm`) — not flagged as breach but not in v1.4 edges |
| 7 | L_APP | L4 | 22 | unexpected | apps read L4 config directly (`vllm_routing_predicates`) |
| 8 | L3 | L0 | 54 | unexpected | L3 imports L0 routing — possibly legitimate admit-side binding |
| 9 | L5 | L2 | 78 | **expected** | L5 policy applied at L2 execution — v1.4 F11 scope |
| 10 | L2 | L0 | 39 | unexpected | L2 reaching back to L0 — test for circular or rediscovering routing |
| 11 | L3 | L2 | 30 | **expected** | L3 dispatches L2 per SRC-ADR-008 L3-I1 (v1.4 edge INT-F05.04-F06.01-01) |
| 12 | L6 | L5 | 8 | unexpected | L6 reads L5 audit surfaces — may be legitimate |
| 13 | L_SHARED | L5 | 104 | unexpected | apps_shared reaching deep into L5 validators/enforcement — requires inspection |
| 14 | L_TOOLS | L5 | 125 | **expected** | tools include L5 validator test scaffolding |
| 15 | L4 | L5 | 2 | unexpected | L4 → L5 upward call |

## Spine trace

`mv_critical_path_segments.both_on_spine=1` only ticks on: **L5 → L0 (368 imports, 101 files)**. That pair is recognized by ADG as "critical path spine". Every other cross-layer pair is `both_on_spine=0`. This is consistent with L5's role as the policy authority applied at L0 routing admission (SRC-RULE-001).

## Classification totals

| Class | Distinct (src, dst) pairs | Total edges |
|---|---:|---:|
| `expected` | ≈ 140 pairs | ≈ 122,500 |
| `unexpected` | ≈ 15 pairs | ≈ 250 |
| `violation` | 6 pairs (per `mv_authority_boundary_breaches`) | 137 |

Detailed violation list is in `boundary_violations.md`.

## Hotspot modules (highest blast radius)

From `mv_graph_critical_path_blast_radius` (top of critical-path impact rankings):

| Module | ADG layer | Direct downstream | Classification |
|---|---|---:|---|
| `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | L_RUNTIME | **2,224** | high_impact_hub (architectural — all layers bind here) |
| `agentic_core/L0_routing/config/path_constants.py` | L0 | 374 | high_impact_hub (path shared constants) |
| `agentic_core/__init__.py` | L_UNKNOWN | 363 | high_impact_hub (package init) |
| `agentic_core/base_agents/SovereignBaseAgent.py` | L_SHARED | 132 | high_impact_hub (base agent class) |
| `agentic_core/L0_routing/config/__init__.py` | L0 | 127 | high_impact_hub |
| `agentic_core/L2_execution/utils/write_gateway.py` | L2 | 80 | moderate_impact_hub (canonical L2 write path) |

Blast radius of `lifecycle_trace_contract.py` (2,224 direct downstream) explains the 124k cross-layer edge count — this single module accounts for a dominant share of inbound imports across every layer.

## Observations driving G3 and G7

- **`L_RUNTIME` is the dominant sink.** Every layer converges on `runtime/contracts/lifecycle_trace_contract.py`. This is an expected design outcome — not a risk — but it means G3's pipeline analysis should trace through runtime contracts as a shared backbone.
- **v1.4 edge set (26 NORMATIVE) covers a tiny fraction of observed wiring.** The requirement graph first-classes only the integrity-critical edges; the thousands of `*→L_RUNTIME` edges are legitimate implementation detail that v1.4 deliberately does not enumerate.
- **B7 candidates** from this matrix are listed in the G2 README §6 and will be cross-posted to `G7_runtime_map/b7_candidate_register.md`.
