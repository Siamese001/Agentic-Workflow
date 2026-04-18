# G2 — Service-to-Service Wiring and Connectivity

## 1. Sub-wave ID, title, purpose

**G2** — *Service-to-Service Wiring and Connectivity*. Build the canonical repo wiring map by classifying every observed layer-to-layer edge as `expected` / `unexpected` / `violation`, reconstructing the canonical request lifecycle, reporting seam/interface/L_CONTRACTS usage, and enumerating dynamic-import sites that hide wiring from static analysis.

## 2. Inputs

- **ADG snapshot (frozen)**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (timestamp `04172026_0611`; 83,319 nodes, 638,815 edges; graph_projection not stale). Same snapshot as G1/G1b — ADG MCP probe returned healthy.
- **G0 planning**: `runtime_scope_map.md`, `output_contracts.md`, `wave_g_execution_plan.md`.
- **G1**: `component_inventory.yaml` (2014 `agentic_core/` modules), `layer_embodiment_map.md`, `cross_cutting_classification.md`.
- **G1b**: `app_inventory.yaml` (8 apps), `app_to_core_bindings.md`, `adapter_patterns.md`.
- **Wave F baseline**: `docs/wave_e/99_integration_v14/canonical/*` (v1.4 — commit `4b794d5d46`; 60 ACTIVE atoms, 26 NORMATIVE edges, 12 families GREEN).
- **ADG SQLite materialized views** (primary dependency probe, not grep):
  - `mv_new_cross_layer_dependencies` (162 rows, src_layer × dst_layer × relation_type × edge_count)
  - `mv_critical_path_segments` (177 rows, spine traces)
  - `mv_authority_boundary_breaches` (137 rows — all violations, pre-classified)
  - `mv_write_sovereignty_paths` (1902 rows — UWG compliance)
  - `mv_graph_chokepoint_bridges` (1836 rows — bridge candidates)
  - `mv_graph_critical_path_blast_radius` (28 hubs)
  - `mv_snapshot_baseline` (totals row)
- **Grep (literal matches only, allowed per constitutional Quick Gates)**: `importlib.import_module`, `__import__(`, `sys.modules[` for dynamic-import-site enumeration. NOT used for dependency analysis.

## 3. Outputs

- `README.md` — this index.
- `import_edge_matrix.md` — layer × layer (ADG-derived) matrix with classifications.
- `canonical_request_walk.md` — code-grounded walk from admit → plan → route → orchestrate → execute → heal → exit → UWG.
- `seam_usage_report.md` — seam + interface + L_CONTRACTS fan-in analysis.
- `boundary_violations.md` — authority-boundary breaches, write-sovereignty bypasses, shim-synthesized wiring flagged separately.

## 4. Stop condition

Met.

- Layer × layer matrix complete for all observed layers: `L0 L1 L2 L3 L4 L5 L6 L_RUNTIME L_SHARED L_APP L_PG L_TOOLS L_OPS L_INFRA L_SL L_UNKNOWN L_TEST`. Every non-zero (src, dst) cell is classified as `expected` / `unexpected` / `violation` in `import_edge_matrix.md`.
- Canonical request walk grounded in named modules from G1 inventory. Each stage cites a concrete file path or a named cluster.
- Seam / interface / L_CONTRACTS fan-in analysed: **seams=41 inbound (0 apps)**, **interfaces=283 inbound (3 apps, 3 files)**, **L_CONTRACTS=1 inbound (from an archived file; effectively zero live production use)**.
- Dynamic-wiring sites enumerated: **59 `importlib.import_module` matches in 37 files**, **245 `sys.modules[` writes in 123 files** (overwhelmingly in `agentic_core/adg/_compat/` shim package; 73 other files), **19 `__import__(` matches in 15 files**. Each category classified as real vs shim-synthetic.
- Shim-provided synthetic modules (per G1b adapter patterns) are excluded from "real" wiring counts and tracked separately in `boundary_violations.md` §Shim-synthesized wiring.
- ADG snapshot path and timestamp recorded in every artefact header.
- YAML / MD validate and conform to artefact-plan naming.

## 5. Risks encountered during execution

- **R-G-02 (dynamic wiring)**: substantially mitigated but NOT eliminated. The ADG static graph does not capture dynamic-import wiring. Enumeration shows:
  - 323 files containing at least one of `importlib.import_module`, `__import__`, or `sys.modules[` writes.
  - 93 of these 123 `sys.modules[` files are inside `agentic_core/adg/_compat/` — shim-driven, not runtime dispatch.
  - Remaining 30+ `sys.modules[` sites and 37 `importlib.import_module` sites are real dynamic-wiring candidates. Catalogued in `boundary_violations.md`.
- **R-G-03 (grep drift)**: avoided. Every dependency/boundary/edge statistic in G2 comes from ADG SQLite views. Grep is used ONLY for literal string matching of `importlib.import_module`, `sys.modules[`, `__import__(`.
- **ADG layer taxonomy mismatch with v1.4**: ADG uses `L_RUNTIME`, `L_SHARED`, `L_APP`, `L_TOOLS`, `L_OPS`, `L_INFRA`, `L_PG`, `L_SL`, `L_UNKNOWN` in addition to `L0..L6`. v1.4 uses only `L0..L6 + CROSS_CUTTING`. G2 records ADG's taxonomy in the matrix but maps back to v1.4 layers in `canonical_request_walk.md` — every ADG `L_*` splinter is documented.
- **`mv_runtime_spine_gaps` shows 100% gap** for L0–L6, L_APP, L_SHARED. The view measures "connected to runtime spine" which appears to use a narrow definition; `mv_critical_path_segments` shows the spine L5→L0 pair with `both_on_spine=1`. G2 treats the gap metric as suggestive, not authoritative — see `canonical_request_walk.md` §Spine reconstruction.
- **No `meta` table field specifies v1.4 atoms**: ADG does not natively cross-reference v1.4 atom IDs. Cross-walk is done by code path, not atom ID. G7 traceability matrix will close this.
- **Double-counting risk in L_TEST edges**: the matrix includes `L_TEST → everything` edges (975 into L_TOOLS, 401 into L3, etc.). Tests legitimately import from all layers. These are not `violation`; they are `expected` test-only edges and labelled as such.

## 6. B7 candidates surfaced

G2 observations that G7's `b7_candidate_register.md` should log:

- **B7-G2-01** — `agentic_core/L_CONTRACTS/*` has effectively zero live importers (1 inbound, from archived code). The 4 contract modules exist in the inventory but are unused at runtime. Candidate: either delete (consolidation, owned by G6) or record an interaction candidate if apps/core *should* bind through L_CONTRACTS and currently don't.
- **B7-G2-02** — 0 apps import `agentic_core/seams/*`. Seams are currently a core-internal convention (importers: L2, L3 enforcement / reasoning). If architectural intent is that apps SHOULD bind through seams, the zero-use signal is a B7 gap.
- **B7-G2-03** — L6 → L0 downstream-mutation breaches (23+ instances). L6_observability importing L0_routing config directly bypasses the observability "read-only downstream" architectural assumption. Could be either a v1.4 edge missing (L6 legitimately reads L0 config) or a real violation requiring cleanup. v1.4 has no L6→L0 edge.
- **B7-G2-04** — 24 `L_UNKNOWN` critical write-sovereignty bypasses. These are modules the ADG could not layer-assign — they write directly to infra without going through UWG.
- **B7-G2-05** — `agentic_core.L3_orchestration.inference.qwen_vllm` imported by 6 apps. A concrete L3 → apps binding through a reasoner module. v1.4 has no APP→L3 edge first-classed.
- **B7-G2-06** — `agentic_core.L4_state.config.vllm_routing_predicates` imported by 5 apps. Apps reaching into L4 config predicates directly — likely architecturally suspect; apps should not know about L4 internals.

## 7. Hand-off note for G2b and G3

- **For G2b (provider / gateway / egress)**: G2 identifies internal wiring only. Provider surfaces enter via `agentic_core/gateway/` (1 module), `infrastructure/sdks_mcps/` (wrappers), and MCP servers in `tools/mcp/` (egress as transport). `mv_new_provider_surfaces` (19 rows) shows the ADG-side of provider references; G2b should consume this view plus env-var scan. Bridge-candidate `agentic_core/cache/redis_cache_client.py` (L_SHARED, fan_in=fan_out=70) is the single largest chokepoint — external dependency.
- **For G3 (pipelines)**: G2's canonical request walk in `canonical_request_walk.md` is the skeleton for pipeline identification. G3 should consume it as the "spine pipeline" and add named auxiliary pipelines (ADG regen, eval, healing, memory lifecycle, UWG write, replay).
- **ADG snapshot reuse**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` is recorded in every G2 file. G2b/G3 may use the same snapshot or regenerate — either is acceptable per G0 policy.
- **Gate 2 status**: G2 is ready for sign-off. G2b and G3 can run in parallel; G3b depends on G3.

## Summary counts (authoritative; derivable from ADG)

| Dimension | Value |
|---|---:|
| Total ADG nodes | 83,319 |
| Total ADG edges | 638,815 |
| Cross-layer edges | 124,904 |
| Authority boundary breaches | **137** |
| Write-sovereignty bypasses | 1,821 (56 critical) |
| Provider surfaces | 56 |
| Violations (all) | 7,641 |
| Seams inbound import edges | 41 (0 from apps) |
| Interfaces inbound import edges | 283 (5 from apps) |
| L_CONTRACTS inbound import edges | **1** (archived importer) |
| `importlib.import_module` sites | 59 in 37 files |
| `__import__(` sites | 19 in 15 files |
| `sys.modules[` write sites | 245 in 123 files (93 in adg/_compat) |

Ready for G2b and G3.
