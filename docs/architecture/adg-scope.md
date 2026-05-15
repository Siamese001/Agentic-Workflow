# ADG Scope — Explicit In-Scope / Out-of-Scope Boundary

**Document type**: Architecture Decision Record (ADR)
**Status**: Accepted
**Wave**: W3.1

---

## What the ADG IS (In-Scope)

The ADG (Architectural Dependency Graph) is the **structural truth engine** for this codebase.

It answers:
- **Topology**: What modules exist? What are their layers (L0–L6)?
- **Blast radius**: If I change X, which modules are reachable via import/call chains?
- **Seams**: Where are the boundary-crossing edges between layers?
- **Violations**: Which imports cross layer governance rules?
- **Centrality**: Which modules are highest-fan-in (most imported)?
- **Determinism proof**: Does this ADG snapshot reproducibly represent the current commit?

### In-Scope Outputs

#### Canonical Artifacts (source of truth)

| Output | Location | Purpose |
|--------|----------|---------|
| `adg_indexed_<ts>.sqlite` | `artifacts/adg/` | **Primary canonical DB** (nodes, edges, violations, meta) |
| `adg_snapshot_<ts>.json` | `artifacts/adg/` | Lightweight metrics/counts snapshot |
| `adg_file_graph_<ts>.json` | `artifacts/adg/` | File-level import graph |
| `adg_symbol_graph_<ts>.json` | `artifacts/adg/` | Symbol-level call graph |
| `adg_governance_graph_<ts>.json` | `artifacts/adg/` | Layer violation edges |
| `layer_coverage_report_<ts>.json` | `artifacts/adg/` | Module distribution across layers |
| `edge_density_report_<ts>.json` | `artifacts/adg/` | Edge type distribution |
| `provenance_report_<ts>.json` | `artifacts/adg/` | Commit SHA + digest chain |
| `replay_determinism_report_<ts>.json` | `artifacts/adg/` | Determinism proof |
| `boundary_report_<ts>.json` | `artifacts/adg/` | Unresolved cross-boundary imports |
| `mutation_integrity_report_<ts>.json` | `artifacts/adg/` | Mutation signature coverage |
| `test_surface_coverage_<ts>.json` | `artifacts/adg/` | Test→execution linkage |
| `closure_validation_report_<ts>.json` | `artifacts/adg/` | 13-gate closure checklist |

#### Derived Artifacts (non-canonical)

Derived artifacts are built from canonical outputs and carry no independent authority.
They are rebuilt automatically when the canonical artifact is regenerated. CI gates do
not depend on derived artifacts — their build step is non-blocking.

| Output | Location | Built from | Purpose |
|--------|----------|------------|---------|
| `adg_graph_<ts>.sqlite` | `artifacts/adg/` | `adg_indexed_<ts>.sqlite` | **Graph-native metrics** (centrality, SCC, reachability, cross-run diff). Non-canonical. Freshness verified via `source_artifact_digest`. See [`adg-graph-projection.md`](adg-graph-projection.md). |

### In-Scope Queries (via ADG MCP tools)

- `adg_nodes_by_layer` — find all modules in a layer
- `adg_nodes_by_file` — find all symbols in a file
- `adg_edge_fanout` — trace outgoing dependencies
- `adg_edge_fanin` — find all callers/importers of a node
- `adg_node` — get full metadata for a specific node
- `adg_violations` — list layer boundary violations

---

## What the ADG IS NOT (Out-of-Scope)

The ADG does **not** make decisions — it provides structural evidence for decisions made elsewhere.

| NOT In-Scope | Where It Belongs |
|---|---|
| Runtime behavior analysis | `L6_observability` trace logs |
| Test execution results | pytest / CI pipeline |
| Code quality scores | Ruff / Pylint linters |
| Security scanning | `ops_scripts/ci/check_secrets_scan.py` |
| Business logic correctness | Unit/integration tests |
| Deployment decisions | CI promotion gates (Wave 4) |
| Refactor ordering / ranking | Refactor Accelerator (W3.3–3.4, consumes ADG) |
| Governance allow/deny decisions | Guardian exemption gate + constitutional rules |

---

## Consumer Hierarchy

```
ADG (structural truth)
  └── Refactor Accelerator (W3.3–3.4) — consumes ADG for ranked candidates
  └── Governance Gate — consumes ADG violations for P1/P2/P3 defect counts
  └── MCP Server (adg_sqlite) — serves ADG queries to Cursor Agent at T3 analysis time
  └── Memory MCP — receives ADG snapshot for session context
  └── Redis hot cache — serves ADG topology for fast Cursor Agent queries
  └── Graph Projection (derived) — adg_graph_<ts>.sqlite, built non-blocking from adg_indexed_<ts>.sqlite
        └── GraphProjectionBackend — read-only adapter (tools/adg/core/graph_projection_backend.py)
        └── Analyst CLI — tools/adg/adg_graph_query.py
```

---

## Authority Assignment

| Query Need | Authority | Tool |
|---|---|---|
| Structural dependencies | **ADG** | `adg_edge_fanout`, `adg_edge_fanin` |
| Layer membership | **ADG** | `adg_nodes_by_layer` |
| Violation detection | **ADG** | `adg_violations` |
| Blast radius (topology) | **ADG** | `adg_edge_fanin` (transitive) |
| Blast radius (pre-computed scalar) | **Graph Projection** | `adg_graph_query.py blast-radius` |
| SCC / cycle detection | **Graph Projection** | `adg_graph_query.py scc` |
| Cross-run metric deltas | **Graph Projection** | `adg_graph_query.py diff` |
| Runtime traces | **OTel / L6** | Not ADG |
| Test pass/fail | **pytest** | Not ADG |
| Refactor priority | **Refactor Accelerator** | Consumes ADG |

---

## Regeneration Trigger

The ADG must be regenerated after:
1. Any structural code change (new module, moved file, new import)
2. Any layer assignment change in `adg_layer_overrides.yaml`
3. Any guardian comment added/removed (changes violation counts)

Command: `python tools/generate/generate_full_adg.py`
Workflow: `/adg-redis-refresh`
