# GraphDB Enhancement — User & Developer Documentation

## Overview

`tools/graphdb` provides a **NetworkX-based graph projection layer** on top of the canonical ADG SQLite artifacts. It adds structural analysis, blast-radius exploration, and historical diffing without touching the CI truth path.

```
Canonical SQLite (artifacts/adg/adg_indexed_*.sqlite)
        ↓
GraphProjector  (tools/graphdb/projection.py)
        ↓
NetworkX DiGraph (in-memory)
        ↓
Query Workbench
    ├── StructuralQueries   — layer gravity, UWG conformance, spine completeness
    ├── BlastRadiusQueries  — transitive dependents, impact analysis, bypass paths
    ├── HistoricalQueries   — diff between two snapshots
    └── AnalystQueries      — subgraph extraction, violation explanation
```

**Key invariants:**
- The canonical SQLite is the **only source of truth**. The graph projection is read/query-only.
- No policy logic lives exclusively in the graph layer.
- Graph projection is additive — all existing ADG/CI pipelines are unchanged.

---

## Quick Start

### Project a graph from a SQLite artifact

```bash
python -m tools.graphdb.cli project artifacts/adg/adg_indexed_20260101_120000.sqlite
```

### Run a structural query

```bash
python -m tools.graphdb.cli query gravity_violations --commit <sha>
```

### Show historical diff between two commits

```bash
python -m tools.graphdb.cli diff <from_sha> <to_sha>
```

### List saved snapshots

```bash
python -m tools.graphdb.cli list
```

### Show graph statistics

```bash
python -m tools.graphdb.cli stats --commit <sha>
```

---

## Module Reference

### `tools/graphdb/projection.py` — `GraphProjector`

Projects the canonical SQLite into a NetworkX `DiGraph`.

```python
from tools.graphdb.projection import GraphProjector

projector = GraphProjector(Path("artifacts/adg/adg_indexed_20260101.sqlite"))
graph = projector.project_graph()
stats = projector.get_graph_statistics()
warnings = projector.validate_projection(graph)
```

**Node attributes:**

| Attribute | Type | Description |
|---|---|---|
| `adg_id` | str | Canonical entity ID from SQLite |
| `adg_type` | str | Raw ADG entity type (e.g. `module`) |
| `graph_type` | str | Projected type (e.g. `Module`) |
| `name` | str | Human-readable name |
| `properties` | dict | All entity properties from SQLite |

**Edge attributes:**

| Attribute | Type | Description |
|---|---|---|
| `adg_type` | str | Raw ADG relation type (e.g. `imports`) |
| `graph_type` | str | Projected type (e.g. `IMPORTS`) |
| `properties` | dict | All relation properties from SQLite |

**Unknown entity types are silently skipped.** Only ADG types present in `NODE_TYPE_MAPPING` are projected.

---

### `tools/graphdb/schema.py` — Type Mappings

Defines `NODE_TYPE_MAPPING` (ADG → graph node type) and `EDGE_TYPE_MAPPING` (ADG → graph edge type).

```python
from tools.graphdb.schema import NODE_TYPE_MAPPING, EDGE_TYPE_MAPPING, validate_node_type

validate_node_type("module")   # → "Module"
validate_node_type("unknown")  # → raises ValueError
```

**Supported node types:** `File`, `Module`, `Symbol`, `Layer`, `Package`, `ThirdPartyPackage`,
`Agent`, `Tool`, `Gateway`, `Provider`, `DataStore`, `Sink`, `Ingress`, `TraceSurface`,
`Evaluator`, `PolicySurface`, `DecisionPoint`, `RetrievalComponent`, `Seam`, `Snapshot`,
`Commit`, `PromptSlot`, `PromptTemplate`, + extended types.

---

### `tools/graphdb/snapshot.py` — `SnapshotManager`

Saves/loads/lists graph projections keyed by commit SHA.

```python
from tools.graphdb.snapshot import SnapshotManager, SnapshotMetadata

mgr = SnapshotManager(Path("artifacts/graphdb"))

# Save
mgr.save_snapshot(graph, metadata)

# Load
graph, meta = mgr.load_snapshot("abc123")

# List all
snapshots = mgr.list_snapshots()  # {commit_sha: {...metadata dict...}}

# Cleanup (keep last 30)
deleted = mgr.cleanup_old_snapshots(keep_count=30)
```

**Snapshot storage layout:**
```
artifacts/graphdb/
├── projections/
│   └── <commit_sha>/
│       └── graph_projection_<commit_sha>_<timestamp>.pkl
└── metadata/
    └── <commit_sha>.json
```

**`SnapshotMetadata` fields:**

| Field | Description |
|---|---|
| `commit_sha` | 40-char git commit SHA |
| `repo_state_hash` | Git tree hash |
| `schema_version` | ADG schema version |
| `scanner_digest` | SHA256 of scanner code |
| `artifact_digest` | SHA256 of canonical SQLite |
| `run_id` | Unique run identifier |
| `timestamp` | ISO8601 UTC timestamp |
| `scanner_version` | Scanner version string |
| `node_count` | Total projected nodes |
| `edge_count` | Total projected edges |
| `projection_version` | Graph schema version |

---

### `tools/graphdb/queries/structural.py` — `StructuralQueries`

```python
from tools.graphdb.queries.structural import StructuralQueries

sq = StructuralQueries(graph)

sq.gravity_import_violations()           # List[Dict] — upward imports
sq.illegal_layer_reach()                 # List[Dict] — forbidden transitions
sq.l2_lifecycle_conformance()            # Dict — L2 phase coverage
sq.uwg_durable_write_conformance()       # List[Dict] — UWG bypass violations
sq.capability_tool_provider_chokepoint_conformance()  # Dict
sq.agentic_spine_completeness()          # Dict — L0–L6 spine check
sq.l0_l1_l6_role_purity()               # Dict — role purity analysis
sq.grounding_contract_separation()       # List[Dict]
sq.trace_replay_eval_coverage()          # Dict — trace coverage rate
```

---

### `tools/graphdb/queries/blast_radius.py` — `BlastRadiusQueries`

```python
from tools.graphdb.queries.blast_radius import BlastRadiusQueries

bq = BlastRadiusQueries(graph)

bq.transitive_dependents("node_id", max_depth=10)   # Dict — all upstream dependents
bq.shortest_illegal_path("source", "sink")           # Dict — illegal path analysis
bq.bypass_paths("gateway_id")                        # List[Dict] — gateway bypass paths
bq.impact_analysis("node_id")                        # Dict — removal impact score
bq.high_fan_in_out_hubs(min_connections=10)          # Dict — hub analysis
bq.affected_neighborhoods([("src", "tgt"), ...])     # Dict — edge addition impact
```

---

### `tools/graphdb/queries/historical.py` — `HistoricalQueries`

```python
from tools.graphdb.queries.historical import HistoricalQueries

hq = HistoricalQueries(snapshot_manager)

hq.new_forbidden_edges("from_sha", "to_sha")             # List[Dict]
hq.new_direct_writes("from_sha", "to_sha")               # List[Dict]
hq.orphaned_interfaces("from_sha", "to_sha")             # List[Dict]
hq.new_l2_phase_coverage_regressions("from_sha", "to_sha")  # Dict
hq.new_tool_provider_call_surfaces("from_sha", "to_sha") # List[Dict]
hq.new_cross_layer_dependencies("from_sha", "to_sha")    # List[Dict]
hq.regression_analysis("from_sha", "to_sha")             # Dict — comprehensive summary
```

---

### `tools/graphdb/queries/analyst.py` — `AnalystQueries`

```python
from tools.graphdb.queries.analyst import AnalystQueries

aq = AnalystQueries(graph)

aq.extract_subgraph_by_layer("L2")          # Dict — layer neighborhood
aq.extract_subgraph_by_agent("WorkerAgent") # Dict — agent neighborhood
aq.extract_subgraph_by_gateway("UWGGateway") # Dict — gateway context
aq.extract_subgraph_by_provider("OpenAIProvider") # Dict — provider context
aq.violation_explanation_paths("node_id")   # Dict — violation root-cause paths
aq.top_changed_neighborhoods(from_graph, to_graph, top_n=10) # Dict
```

---

## Architecture Constraints

1. **No policy logic in graph layer** — all P0-P3 checks remain in `tools/generate/validation/`.
2. **Read-only projection** — `GraphProjector` never writes to the canonical SQLite.
3. **Optional CI step** — graph projection is additive; existing CI pipeline is unaffected.
4. **No external dependencies** — only Python standard library + `networkx`.
5. **Deterministic** — same SQLite input always produces the same graph output.

---

## Testing

```bash
# Run all graphdb unit tests
pytest tests/unit/tools/graphdb/ -v

# Run a single test file
pytest tests/unit/tools/graphdb/test_projection.py -v

# Run with coverage
pytest tests/unit/tools/graphdb/ --cov=tools/graphdb --cov-report=term-missing
```

---

## Related Documentation

- `docs/reference/GraphDB/Graph DB vs. Dependency Graph.md` — design rationale
- `docs/reference/ADG/DEPENDENCY GRAPH vs GRAPHDB Design.md` — ADG architecture context
- `.codex/plans/graphdb-enhancement-phase-a-4f2e8b.md` — Phase A design decisions
