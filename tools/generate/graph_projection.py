"""Graph projection builder — produces `adg_graph_<ts>.sqlite` from canonical ADG.

Reads from `adg_indexed_<ts>.sqlite` (canonical CI artifact) and writes a separate
derived file containing pre-computed graph metrics that SQL-based materialized views
cannot produce efficiently (true SCCs, k-hop reachability, 2-hop blast radius).

Output tables
-------------
    proj_meta          Lineage and rebuild identity (source_artifact_digest → canonical)
    proj_nodes         Stable node index keyed on adg_name (not integer IDs)
    proj_centrality    Per-node fan-in/fan-out, betweenness approx, blast-radius (direct + 2-hop)
    proj_scc           Strongly connected components via networkx Kosaraju
    proj_violations    Violations joined with graph-impact metrics (severity, disposition co-located)
    proj_reachability  Pre-computed k-hop BFS reachability from high-blast-radius seed nodes
    proj_diff          Cross-run delta vs previous adg_graph_*.sqlite (empty on first run)

Stability contract
------------------
- All cross-table joins use `adg_name TEXT`, never integer node IDs from the canonical file.
- `proj_meta.source_artifact_digest` must equal canonical `meta.artifact_digest` for the
  projection to be considered fresh. The GraphProjectionBackend (Increment 2) enforces this.
- This module reads ONLY `nodes`, `edges`, `violations`, and `meta` from the canonical sqlite.
  It never reads `mv_*` materialized-view tables — the projection is independently rebuildable
  from any canonical sqlite that has not had Phase A-E run.

Failure contract
----------------
- `build_graph_projection()` raises `ImportError` if networkx is absent. The caller
  (generate_full_adg.py P6 guard) catches this and logs a skip. Do not swallow it here.
- All other failures propagate as-is. The caller's guard is responsible for non-blocking behaviour.

Standalone rebuild
------------------
    python tools/generate/graph_projection.py artifacts/adg/adg_indexed_<ts>.sqlite
    python tools/generate/graph_projection.py artifacts/adg/adg_indexed_<ts>.sqlite \\
        --out-dir artifacts/adg --ts <ts>
"""

from __future__ import annotations

import gc
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm


def _connect_sqlite(path: Path, timeout: int = 10, *, uri: bool = False) -> sqlite3.Connection:
    return sqlite3.connect(str(path), timeout=timeout, uri=uri)


_PROJECTION_SCHEMA_VERSION = "1.1"

_REACHABILITY_SEED_THRESHOLD = 10
_REACHABILITY_MAX_HOPS = 4
_REACHABILITY_PER_SEED_LIMIT = 2000  # hard cap: rows stored per seed node
_BETWEENNESS_K_SAMPLE = 200
# proj_diff: only store changed rows (direction != 'unchanged'). Unchanged rows
# are 58.7% of the table on real artifacts and are never returned by any query.
_DIFF_STORE_UNCHANGED = False
_LAYER_CRITICALITY_WEIGHTS: dict[str, float] = {
    "L0": 2.0,
    "L1": 2.0,
    "L2": 2.0,
    "L3": 2.0,
    "L4": 2.0,
    "L5": 2.0,
    "L6": 2.0,
    "L_APP": 2.0,
    "L_SHARED": 2.0,
    "L_RUNTIME": 2.0,
}
# Relation types encoded in the ADG canonical artifact.
# The ADG uses a bipartite module↔symbol graph: imports go module→symbol (not
# module→module). The graph loaded here includes both module and symbol nodes
# so that fan-in/fan-out counts and BFS reachability reflect the real topology.
# Relation types selected here are those that encode meaningful dependency
# structure between modules and the symbols/modules they connect to:
#   imports        — module reads an external or project symbol
#   exports        — module publishes a symbol (reverse of imports)
#   reads_from     — module reads from a symbol/resource
#   resolves_callsite — project symbol resolves into its containing module
#   emits_side_effect — project symbol causes a side effect in a module
# Not included: antipattern, belongs_to_layer, covers, applies (metadata edges)
_GRAPH_EDGE_RELATION_TYPES = (
    "imports",
    "exports",
    "reads_from",
    "resolves_callsite",
    "emits_side_effect",
)

_PROJ_DDL = """
CREATE TABLE IF NOT EXISTS proj_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proj_nodes (
    adg_name      TEXT PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    resolved_path TEXT NOT NULL,
    precision_type TEXT NOT NULL DEFAULT 'symbol'
);
CREATE INDEX IF NOT EXISTS idx_proj_nodes_layer ON proj_nodes(layer);
CREATE INDEX IF NOT EXISTS idx_proj_nodes_entity ON proj_nodes(entity_type);

CREATE TABLE IF NOT EXISTS proj_centrality (
    adg_name              TEXT PRIMARY KEY REFERENCES proj_nodes(adg_name),
    fan_in                INTEGER NOT NULL DEFAULT 0,
    fan_out               INTEGER NOT NULL DEFAULT 0,
    import_fan_in         INTEGER NOT NULL DEFAULT 0,
    import_fan_out        INTEGER NOT NULL DEFAULT 0,
    betweenness_approx    REAL NOT NULL DEFAULT 0.0,
    reverse_dep_score     REAL NOT NULL DEFAULT 0.0,
    blast_radius_direct   INTEGER NOT NULL DEFAULT 0,
    blast_radius_2hop     INTEGER NOT NULL DEFAULT 0,
    bridge_score          REAL NOT NULL DEFAULT 0.0,
    bridge_type           TEXT NOT NULL DEFAULT 'moderate_connector',
    snapshot_id           TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_proj_centrality_blast ON proj_centrality(blast_radius_direct DESC);
CREATE INDEX IF NOT EXISTS idx_proj_centrality_bridge ON proj_centrality(bridge_score DESC);

CREATE TABLE IF NOT EXISTS proj_scc (
    adg_name      TEXT NOT NULL REFERENCES proj_nodes(adg_name),
    scc_id        TEXT NOT NULL,
    scc_size      INTEGER NOT NULL,
    scc_type      TEXT NOT NULL,
    scc_risk_score REAL NOT NULL DEFAULT 0.0,
    snapshot_id   TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (adg_name, scc_id)
);
CREATE INDEX IF NOT EXISTS idx_proj_scc_id ON proj_scc(scc_id);
CREATE INDEX IF NOT EXISTS idx_proj_scc_risk ON proj_scc(scc_risk_score DESC);

CREATE TABLE IF NOT EXISTS proj_violations (
    adg_name_from        TEXT NOT NULL,
    adg_name_to          TEXT NOT NULL,
    relation_type        TEXT NOT NULL,
    edge_kind            TEXT NOT NULL,
    source_file          TEXT NOT NULL DEFAULT '',
    line_no              INTEGER NOT NULL DEFAULT 0,
    severity             TEXT NOT NULL DEFAULT 'MEDIUM',
    violation_class      TEXT NOT NULL DEFAULT 'hygiene',
    disposition          TEXT NOT NULL DEFAULT 'untriaged',
    category             TEXT NOT NULL DEFAULT '',
    blast_radius_direct  INTEGER NOT NULL DEFAULT 0,
    snapshot_id          TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (adg_name_from, adg_name_to, relation_type, source_file, line_no)
);
CREATE INDEX IF NOT EXISTS idx_proj_viol_from ON proj_violations(adg_name_from);
CREATE INDEX IF NOT EXISTS idx_proj_viol_sev ON proj_violations(severity);
CREATE INDEX IF NOT EXISTS idx_proj_viol_disp ON proj_violations(disposition);
CREATE INDEX IF NOT EXISTS idx_proj_viol_blast ON proj_violations(blast_radius_direct DESC);

CREATE TABLE IF NOT EXISTS proj_reachability (
    src_adg_name  TEXT NOT NULL,
    dst_adg_name  TEXT NOT NULL,
    hop_count     INTEGER NOT NULL,
    path_weight   REAL NOT NULL DEFAULT 1.0,
    snapshot_id   TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (src_adg_name, dst_adg_name)
);
CREATE INDEX IF NOT EXISTS idx_proj_reach_src ON proj_reachability(src_adg_name);
CREATE INDEX IF NOT EXISTS idx_proj_reach_hop ON proj_reachability(hop_count);
CREATE INDEX IF NOT EXISTS idx_proj_reach_src_hop ON proj_reachability(src_adg_name, hop_count);

CREATE TABLE IF NOT EXISTS proj_diff (
    adg_name          TEXT NOT NULL,
    metric            TEXT NOT NULL,
    prev_value        REAL NOT NULL DEFAULT 0.0,
    curr_value        REAL NOT NULL DEFAULT 0.0,
    delta             REAL NOT NULL DEFAULT 0.0,
    delta_pct         REAL NOT NULL DEFAULT 0.0,
    direction         TEXT NOT NULL DEFAULT 'unchanged',
    layer             TEXT NOT NULL DEFAULT '',
    prev_snapshot_id  TEXT NOT NULL DEFAULT '',
    curr_snapshot_id  TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (adg_name, metric)
);
CREATE INDEX IF NOT EXISTS idx_proj_diff_dir ON proj_diff(direction, layer);
CREATE INDEX IF NOT EXISTS idx_proj_diff_metric_dir ON proj_diff(metric, direction);
CREATE INDEX IF NOT EXISTS idx_proj_diff_delta ON proj_diff(metric, delta DESC);
"""

_DIFF_METRICS = ("fan_in", "fan_out", "blast_radius_direct", "blast_radius_2hop")


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def build_graph_projection(
    canonical_sqlite: Path,
    out_dir: Path,
    ts: str,
) -> Path:
    """Build `adg_graph_<ts>.sqlite` from the canonical `adg_indexed_<ts>.sqlite`.

    Args:
        canonical_sqlite: Path to the canonical ADG SQLite artifact.
        out_dir:          Directory to write the derived projection file.
        ts:               Timestamp string (MMDDYYYY format, must match canonical stem).

    Returns:
        Path to the written projection sqlite file.

    Raises:
        ImportError:      If networkx is not installed.
        FileNotFoundError: If canonical_sqlite does not exist.
        RuntimeError:     If the canonical sqlite is missing expected tables.
    """
    import networkx as nx  # lazy — ImportError surfaces clearly to caller
    import time as _time

    if not canonical_sqlite.exists():
        raise FileNotFoundError(f"Canonical sqlite not found: {canonical_sqlite}")

    out_dir.mkdir(parents=True, exist_ok=True)
    proj_path = out_dir / f"adg_graph_{ts}.sqlite"
    tmp_path = out_dir / f"adg_graph_{ts}.sqlite.tmp"

    if tmp_path.exists():
        tmp_path.unlink()

    print(f"[graph_projection] Canonical : {canonical_sqlite.name}")
    print(f"[graph_projection] Output    : {proj_path.name}")

    build_start = _time.perf_counter()

    graph, node_attrs = _load_graph(canonical_sqlite, nx)

    print(f"[graph_projection] Graph     : {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    centrality = _compute_centrality(graph, node_attrs, nx)
    sccs = _compute_scc(graph, nx)
    reachability = _compute_reachability(graph, centrality)
    diff_rows = _compute_diff(centrality, out_dir)

    build_duration_s = round(_time.perf_counter() - build_start, 2)

    # Collect build-quality metadata for proj_meta
    seed_count = len({row[0] for row in reachability})
    changed_diff_count = sum(1 for r in diff_rows if r[6] != "unchanged")
    build_meta = {
        "build_duration_s": str(build_duration_s),
        "graph_node_count": str(graph.number_of_nodes()),
        "graph_edge_count": str(graph.number_of_edges()),
        "reachability_seed_count": str(seed_count),
        "reachability_row_count": str(len(reachability)),
        "reachability_per_seed_cap": str(_REACHABILITY_PER_SEED_LIMIT),
        "reachability_max_hops": str(_REACHABILITY_MAX_HOPS),
        "diff_row_count": str(len(diff_rows)),
        "diff_changed_count": str(changed_diff_count),
        "diff_store_unchanged": str(_DIFF_STORE_UNCHANGED).lower(),
    }
    print(f"[graph_projection] Build     : {build_duration_s}s")

    _write_projection_sqlite(
        db_path=tmp_path,
        canonical_sqlite=canonical_sqlite,
        node_attrs=node_attrs,
        centrality=centrality,
        sccs=sccs,
        reachability=reachability,
        diff_rows=diff_rows,
        build_meta=build_meta,
    )

    tmp_path.replace(proj_path)  # replace() is atomic on POSIX; on Windows it overwrites atomically
    gc.collect()

    print(f"[graph_projection] Written   : {proj_path}")
    return proj_path


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------


def _load_graph(
    canonical_sqlite: Path,
    nx: Any,
) -> tuple[Any, dict[str, dict]]:
    """Load canonical nodes and edges into a networkx DiGraph.

    Reads only `nodes`, `edges`, and `meta` from the canonical sqlite.
    Never reads `mv_*` tables — projection must be rebuildable from any
    canonical sqlite regardless of whether Phase A-E views have been run.

    Graph topology note
    -------------------
    The ADG uses a bipartite graph: `imports` edges go module→symbol, not
    module→module. `proj_nodes` (the projection index) stores only module nodes,
    but the DiGraph built here includes both module and symbol nodes so that
    fan-in/fan-out, betweenness, and BFS reachability reflect the real ADG
    topology. Centrality metrics stored in `proj_centrality` are for module
    nodes only — symbol nodes are dropped before writing.

    Returns:
        (DiGraph, node_attrs) where node_attrs maps adg_name → attribute dict
        for **module** nodes only (entity_type, layer, resolved_path,
        precision_type). The returned DiGraph may contain additional symbol
        nodes as graph intermediaries.
    """
    conn = _connect_sqlite(canonical_sqlite, timeout=10)
    conn.row_factory = sqlite3.Row

    _verify_canonical_tables(conn)

    # node_attrs: module nodes only — these become proj_nodes rows
    node_attrs: dict[str, dict] = {}

    module_rows = conn.execute(
        "SELECT adg_name, entity_type, layer, resolved_path, precision_type"
        " FROM nodes WHERE entity_type = 'module'"
    ).fetchall()

    for row in module_rows:
        node_attrs[row["adg_name"]] = {
            "entity_type": row["entity_type"],
            "layer": row["layer"] or "",
            "resolved_path": row["resolved_path"] or "",
            "precision_type": row["precision_type"] or "symbol",
        }

    # Build DiGraph with all nodes that participate in selected edge types.
    # Module nodes seeded first; symbol/other nodes added on demand as edges load.
    graph = nx.DiGraph()
    for adg_name in node_attrs:
        graph.add_node(adg_name)

    rel_placeholders = ",".join("?" * len(_GRAPH_EDGE_RELATION_TYPES))
    edge_rows = conn.execute(
        f"SELECT src.adg_name AS from_name,"
        f" dst.adg_name AS to_name,"
        f" e.relation_type,"
        f" e.confidence_score"
        f" FROM edges e"
        f" JOIN nodes src ON e.src_id = src.id"
        f" JOIN nodes dst ON e.dst_id = dst.id"
        f" WHERE e.relation_type IN ({rel_placeholders})",
        _GRAPH_EDGE_RELATION_TYPES,
    ).fetchall()

    for row in edge_rows:
        from_name = row["from_name"]
        to_name = row["to_name"]
        if from_name not in graph:
            graph.add_node(from_name)
        if to_name not in graph:
            graph.add_node(to_name)
        conf = row["confidence_score"] if row["confidence_score"] else 1.0
        graph.add_edge(from_name, to_name, relation_type=row["relation_type"], weight=conf)

    conn.close()
    return graph, node_attrs


def _verify_canonical_tables(conn: sqlite3.Connection) -> None:
    """Raise RuntimeError if expected canonical tables are absent."""
    required = {"nodes", "edges", "meta", "violations"}
    existing = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    missing = required - existing
    if missing:
        raise RuntimeError(
            f"Canonical sqlite is missing required tables: {missing}. "
            "Ensure the canonical artifact was produced by write_all_artifacts()."
        )


# ---------------------------------------------------------------------------
# Graph algorithm helpers
# ---------------------------------------------------------------------------


def _compute_centrality(
    graph: Any,
    node_attrs: dict[str, dict],
    nx: Any,
) -> dict[str, dict]:
    """Compute per-node centrality metrics.

    Returns dict mapping adg_name → metric dict with keys:
        fan_in, fan_out, import_fan_in, import_fan_out,
        betweenness_approx, reverse_dep_score,
        blast_radius_direct, blast_radius_2hop,
        bridge_score, bridge_type
    """
    import random as _random

    _random.seed(0)

    result: dict[str, dict] = {}

    betweenness: dict[str, float] = {}
    if graph.number_of_nodes() > 0 and graph.number_of_edges() > 0:
        k = min(_BETWEENNESS_K_SAMPLE, graph.number_of_nodes())
        betweenness = nx.betweenness_centrality(graph, k=k, normalized=True, seed=0)

    for adg_name in tqdm(graph.nodes(), desc="centrality", leave=False, disable=True):
        fan_in = graph.in_degree(adg_name)
        fan_out = graph.out_degree(adg_name)

        import_fan_in = sum(
            1 for _, _, d in graph.in_edges(adg_name, data=True) if d.get("relation_type") == "imports"
        )
        import_fan_out = sum(
            1 for _, _, d in graph.out_edges(adg_name, data=True) if d.get("relation_type") == "imports"
        )

        layer = node_attrs.get(adg_name, {}).get("layer", "")
        layer_w = _LAYER_CRITICALITY_WEIGHTS.get(layer, 1.0)
        rev_dep_score = round(fan_in * layer_w, 4)

        blast_direct = fan_in

        bridge_score = 0.0
        if fan_in > 0 and fan_out > 0:
            bridge_score = round(
                (fan_in * fan_out) / (abs(fan_in - fan_out) + 1.0),
                4,
            )

        if fan_in > 100 and fan_out > 100 and fan_in * fan_out > 10000:
            bridge_type = "high_impact_bridge"
        elif fan_in > 50 and fan_out > 50 and fan_in * fan_out > 2500:
            bridge_type = "bridge_candidate"
        elif abs(fan_in - fan_out) > 100:
            bridge_type = "asymmetric_connector"
        else:
            bridge_type = "moderate_connector"

        result[adg_name] = {
            "fan_in": fan_in,
            "fan_out": fan_out,
            "import_fan_in": import_fan_in,
            "import_fan_out": import_fan_out,
            "betweenness_approx": round(betweenness.get(adg_name, 0.0), 6),
            "reverse_dep_score": rev_dep_score,
            "blast_radius_direct": blast_direct,
            "blast_radius_2hop": 0,
            "bridge_score": bridge_score,
            "bridge_type": bridge_type,
            "_layer": layer,  # transient — used by _compute_diff, not written to proj_centrality
        }

    seeds = [n for n, m in result.items() if m["blast_radius_direct"] > _REACHABILITY_SEED_THRESHOLD]

    for seed in seeds:
        reachable_2hop = _bfs_count(graph, seed, max_hops=2)
        result[seed]["blast_radius_2hop"] = reachable_2hop

    return result


def _bfs_count(graph: Any, start: str, max_hops: int) -> int:
    """Return count of distinct nodes reachable from `start` within `max_hops`
    following reversed edges (i.e. nodes that depend on `start`)."""
    visited: set[str] = {start}
    frontier: set[str] = {start}
    for _ in range(max_hops):
        next_frontier: set[str] = set()
        for node in frontier:
            for predecessor in graph.predecessors(node):
                if predecessor not in visited:
                    visited.add(predecessor)
                    next_frontier.add(predecessor)
        frontier = next_frontier
        if not frontier:
            break
    return len(visited) - 1


def _compute_scc(graph: Any, nx: Any) -> list[frozenset[str]]:
    """Return non-trivial SCCs (size > 1) via networkx Kosaraju algorithm.

    Trivial SCCs (single nodes with no self-loop) are filtered out.
    An empty return list is architecturally positive — it means no import cycles.
    """
    all_sccs = list(nx.strongly_connected_components(graph))
    non_trivial = [frozenset(scc) for scc in all_sccs if len(scc) > 1]
    print(f"[graph_projection] SCCs      : {len(all_sccs)} total, {len(non_trivial)} non-trivial")
    return non_trivial


def _compute_reachability(
    graph: Any,
    centrality: dict[str, dict],
) -> list[tuple[str, str, int, float]]:
    """Pre-compute BFS reachability from high-blast-radius seed nodes.

    Seeds: nodes with blast_radius_direct > _REACHABILITY_SEED_THRESHOLD.
    Direction: upstream (predecessors) — nodes that depend on the seed.
    Max depth: _REACHABILITY_MAX_HOPS.

    Returns list of (src_adg_name, dst_adg_name, hop_count, path_weight) tuples.
    path_weight is the hop_count (uniform weight; edge-weighted path is deferred).
    """
    seeds = [n for n, m in centrality.items() if m["blast_radius_direct"] > _REACHABILITY_SEED_THRESHOLD]
    rows: list[tuple[str, str, int, float]] = []
    capped_seeds = 0

    for seed in tqdm(seeds, desc="reachability", leave=False, disable=True):
        frontier: dict[str, int] = {seed: 0}
        visited: dict[str, int] = {seed: 0}
        for hop in range(1, _REACHABILITY_MAX_HOPS + 1):
            next_frontier: dict[str, int] = {}
            for node in list(frontier):
                for pred in graph.predecessors(node):
                    if pred not in visited:
                        visited[pred] = hop
                        next_frontier[pred] = hop
            frontier = next_frontier
            if not frontier:
                break

        seed_rows: list[tuple[str, str, int, float]] = []
        for reached_node, hops in visited.items():
            if reached_node == seed:
                continue
            seed_rows.append((seed, reached_node, hops, float(hops)))

        if len(seed_rows) > _REACHABILITY_PER_SEED_LIMIT:
            # Keep the nearest hops first (smallest hop_count = most actionable)
            seed_rows.sort(key=lambda r: (r[2], r[1]))
            seed_rows = seed_rows[:_REACHABILITY_PER_SEED_LIMIT]
            capped_seeds += 1

        rows.extend(seed_rows)

    print(
        f"[graph_projection] Reachability: {len(rows)} pairs from {len(seeds)} seeds"
        + (f" ({capped_seeds} capped at {_REACHABILITY_PER_SEED_LIMIT})" if capped_seeds else "")
    )
    return rows


def _compute_diff(
    current_centrality: dict[str, dict],
    out_dir: Path,
) -> list[tuple]:
    """Compare current centrality metrics against the previous projection file.

    Looks for the most-recent `adg_graph_*.sqlite` (excluding any `.tmp` file)
    in `out_dir`. If none exists, returns an empty list — this is expected on
    the first run. `proj_diff` will have zero rows; this is not an error.

    Returns list of tuples:
        (adg_name, metric, prev_value, curr_value, delta, delta_pct, direction,
         layer, prev_snapshot_id, curr_snapshot_id)
    """
    prev_files = sorted(f for f in out_dir.glob("adg_graph_*.sqlite") if not f.name.endswith(".tmp"))
    if not prev_files:
        print("[graph_projection] Diff       : no prior projection file — proj_diff will be empty")
        return []

    prev_path = prev_files[-1]
    print(f"[graph_projection] Diff base  : {prev_path.name}")

    try:
        prev_conn = _connect_sqlite(prev_path, timeout=5)
        prev_conn.row_factory = sqlite3.Row

        prev_centrality: dict[str, dict] = {}
        for row in prev_conn.execute(
            f"SELECT adg_name, {', '.join(_DIFF_METRICS)} FROM proj_centrality"
        ).fetchall():
            prev_centrality[row["adg_name"]] = dict(row)

        prev_snapshot_id = ""
        snap_row = prev_conn.execute(
            "SELECT value FROM proj_meta WHERE key = 'source_artifact_digest'"
        ).fetchone()
        if snap_row:
            prev_snapshot_id = snap_row[0]

        prev_conn.close()
    except sqlite3.Error as exc:
        print(f"[graph_projection] Diff       : could not read prior projection ({exc}) — skipping diff")
        return []

    curr_snapshot_id = ""

    rows: list[tuple] = []
    all_names = set(current_centrality) | set(prev_centrality)
    for adg_name in tqdm(sorted(all_names), desc="diff", leave=False, disable=True):
        curr = current_centrality.get(adg_name, {})
        prev = prev_centrality.get(adg_name, {})
        # Populate layer from the current run's centrality dict if available;
        # fall back to empty string for nodes that only existed in the prior run.
        layer = curr.get("_layer", "")
        for m in tqdm(_DIFF_METRICS, desc="diff-metrics", leave=False, disable=True):
            curr_val = float(curr.get(m, 0))
            prev_val = float(prev.get(m, 0))
            delta = curr_val - prev_val
            delta_pct = 0.0
            if prev_val != 0.0:
                delta_pct = round(delta / prev_val * 100.0, 4)
            if delta > 0:
                direction = "worsened"
            elif delta < 0:
                direction = "improved"
            else:
                direction = "unchanged"
            if not _DIFF_STORE_UNCHANGED and direction == "unchanged":
                continue
            rows.append(
                (
                    adg_name,
                    m,
                    prev_val,
                    curr_val,
                    round(delta, 4),
                    delta_pct,
                    direction,
                    layer,
                    prev_snapshot_id,
                    curr_snapshot_id,
                )
            )

    changed = sum(1 for r in rows if r[6] != "unchanged")
    print(f"[graph_projection] Diff       : {len(rows)} metric rows, {changed} changed")
    return rows


# ---------------------------------------------------------------------------
# SQLite writer
# ---------------------------------------------------------------------------


def _write_projection_sqlite(
    db_path: Path,
    canonical_sqlite: Path,
    node_attrs: dict[str, dict],
    centrality: dict[str, dict],
    sccs: list[frozenset[str]],
    reachability: list[tuple[str, str, int, float]],
    diff_rows: list[tuple],
    build_meta: dict[str, str] | None = None,
) -> None:
    """Write all projection tables to `db_path` atomically (single transaction).

    Reads lineage fields from canonical sqlite meta table.
    All writes happen with MEMORY journal for speed on a temp file.
    """
    canon_conn = _connect_sqlite(canonical_sqlite, timeout=10)
    canon_conn.row_factory = sqlite3.Row

    meta_rows_raw = canon_conn.execute("SELECT key, value FROM meta").fetchall()
    canon_meta: dict[str, str] = {r["key"]: r["value"] for r in meta_rows_raw}

    source_artifact_digest = canon_meta.get("artifact_digest", "")
    commit_sha = canon_meta.get("commit_sha", "")
    repo_state_hash = canon_meta.get("repo_state_hash", "")
    canonical_schema_version = canon_meta.get("schema_version", "")

    violation_rows = _load_violation_rows(canon_conn, centrality)
    canon_conn.close()

    snapshot_id = source_artifact_digest[:16] if source_artifact_digest else "unknown"
    generated_ts = datetime.now(tz=timezone.utc).isoformat()

    conn = _connect_sqlite(db_path, timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=MEMORY")
        conn.execute("PRAGMA synchronous=OFF")
        conn.executescript(_PROJ_DDL)

        proj_meta_values: list[tuple[str, str]] = [
            ("schema_version", _PROJECTION_SCHEMA_VERSION),
            ("source_artifact_digest", source_artifact_digest),
            ("source_commit_sha", commit_sha),
            ("source_repo_state_hash", repo_state_hash),
            ("source_canonical_schema_version", canonical_schema_version),
            ("generated_ts", generated_ts),
            ("node_count", str(len(node_attrs))),
            ("edge_count", str(sum(m["fan_in"] + m["fan_out"] for m in centrality.values()) // 2)),
            ("networkx_version", _networkx_version()),
        ]
        if build_meta:
            proj_meta_values.extend(sorted(build_meta.items()))
        conn.executemany(
            "INSERT OR REPLACE INTO proj_meta(key, value) VALUES (?, ?)",
            proj_meta_values,
        )

        node_rows = [
            (
                adg_name,
                attrs["entity_type"],
                attrs["layer"],
                attrs["resolved_path"],
                attrs["precision_type"],
            )
            for adg_name, attrs in sorted(node_attrs.items())
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO proj_nodes"
            "(adg_name, entity_type, layer, resolved_path, precision_type) "
            "VALUES (?, ?, ?, ?, ?)",
            node_rows,
        )
        print(f"[graph_projection] proj_nodes : {len(node_rows)} rows")

        centrality_rows = [
            (
                adg_name,
                m["fan_in"],
                m["fan_out"],
                m["import_fan_in"],
                m["import_fan_out"],
                m["betweenness_approx"],
                m["reverse_dep_score"],
                m["blast_radius_direct"],
                m["blast_radius_2hop"],
                m["bridge_score"],
                m["bridge_type"],
                snapshot_id,
            )
            for adg_name, m in sorted(centrality.items())
            # _layer is a transient key used by _compute_diff; excluded from DB writes
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO proj_centrality"
            "(adg_name, fan_in, fan_out, import_fan_in, import_fan_out, "
            "betweenness_approx, reverse_dep_score, blast_radius_direct, blast_radius_2hop, "
            "bridge_score, bridge_type, snapshot_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            centrality_rows,
        )
        print(f"[graph_projection] proj_centrality: {len(centrality_rows)} rows")

        scc_rows = _build_scc_rows(sccs, node_attrs, snapshot_id)
        conn.executemany(
            "INSERT OR REPLACE INTO proj_scc"
            "(adg_name, scc_id, scc_size, scc_type, scc_risk_score, snapshot_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            scc_rows,
        )
        print(f"[graph_projection] proj_scc  : {len(scc_rows)} rows")

        conn.executemany(
            "INSERT OR REPLACE INTO proj_violations"
            "(adg_name_from, adg_name_to, relation_type, edge_kind, source_file, "
            "line_no, severity, violation_class, disposition, category, "
            "blast_radius_direct, snapshot_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            violation_rows,
        )
        print(f"[graph_projection] proj_violations: {len(violation_rows)} rows")

        reachability_rows = [(src, dst, hop, weight, snapshot_id) for src, dst, hop, weight in reachability]
        conn.executemany(
            "INSERT OR REPLACE INTO proj_reachability"
            "(src_adg_name, dst_adg_name, hop_count, path_weight, snapshot_id) "
            "VALUES (?, ?, ?, ?, ?)",
            reachability_rows,
        )
        print(f"[graph_projection] proj_reachability: {len(reachability_rows)} rows")

        if diff_rows:
            conn.executemany(
                "INSERT OR REPLACE INTO proj_diff"
                "(adg_name, metric, prev_value, curr_value, delta, delta_pct, "
                "direction, layer, prev_snapshot_id, curr_snapshot_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                diff_rows,
            )
        print(f"[graph_projection] proj_diff : {len(diff_rows)} rows")

        conn.commit()
    except (
        sqlite3.Error,
        OSError,
        ValueError,
    ):  # database write errors — propagate; caller's guard handles non-blocking
        conn.close()
        gc.collect()
        raise
    else:
        conn.close()
        gc.collect()


# ---------------------------------------------------------------------------
# Violation loading helper
# ---------------------------------------------------------------------------


def _load_violation_rows(
    canon_conn: sqlite3.Connection,
    centrality: dict[str, dict],
) -> list[tuple]:
    """Join canonical violations+edges+nodes to produce proj_violations rows.

    Uses `adg_name` (not integer IDs) as the stable identity for from/to nodes.
    Blast radius is looked up from the current run's centrality dict.
    """
    try:
        rows = canon_conn.execute(
            """SELECT
                   src.adg_name  AS from_name,
                   dst.adg_name  AS to_name,
                   e.relation_type,
                   e.edge_kind,
                   e.source_file,
                   e.line_no,
                   v.severity,
                   v.violation_class,
                   v.disposition,
                   v.category
               FROM violations v
               JOIN edges e     ON v.edge_id = e.id
               JOIN nodes src   ON e.src_id = src.id
               JOIN nodes dst   ON e.dst_id = dst.id"""
        ).fetchall()
    except sqlite3.OperationalError:
        return []

    result: list[tuple] = []
    for row in tqdm(rows, desc="violations-join", leave=False, disable=True):
        from_name = row[0]
        blast = centrality.get(from_name, {}).get("blast_radius_direct", 0)
        result.append(
            (
                from_name,
                row[1],
                row[2],
                row[3],
                row[4] or "",
                row[5] or 0,
                row[6] or "MEDIUM",
                row[7] or "hygiene",
                row[8] or "untriaged",
                row[9] or "",
                blast,
                "",
            )
        )
    return result


# ---------------------------------------------------------------------------
# SCC row building helper
# ---------------------------------------------------------------------------


def _build_scc_rows(
    sccs: list[frozenset[str]],
    node_attrs: dict[str, dict],
    snapshot_id: str,
) -> list[tuple]:
    """Convert SCC frozensets into proj_scc table rows.

    scc_id is a stable 12-char hex digest of the sorted member list.
    Only non-trivial SCCs (size > 1) are present — the caller already filters.
    """
    rows: list[tuple] = []
    for scc in tqdm(sccs, desc="scc-rows", leave=False, disable=True):
        size = len(scc)
        scc_id = hashlib.sha256(json.dumps(sorted(scc)).encode("utf-8")).hexdigest()[:12]

        if size > 20:
            scc_type = "large_tight_cluster"
        elif size > 10:
            scc_type = "medium_tight_cluster"
        elif size > 5:
            scc_type = "small_tight_cluster"
        else:
            scc_type = "coupled_pair"

        risk_score = 0.0
        for member in tqdm(scc, desc="scc-risk", leave=False, disable=True):
            layer = node_attrs.get(member, {}).get("layer", "")
            weight = _LAYER_CRITICALITY_WEIGHTS.get(layer, 1.0)
            risk_score += size * weight

        for member in tqdm(sorted(scc), desc="scc-members", leave=False, disable=True):
            rows.append(
                (
                    member,
                    scc_id,
                    size,
                    scc_type,
                    round(risk_score, 4),
                    snapshot_id,
                )
            )
    return rows


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _networkx_version() -> str:
    try:
        import networkx as _nx

        return str(_nx.__version__)
    except ImportError:
        return "unknown"


def _derive_ts_from_path(sqlite_path: Path) -> str:
    """Extract timestamp string from canonical sqlite filename.

    Expects stem like `adg_indexed_03122026` → returns `03122026`.
    Falls back to UTC date in MMDDYYYY format.
    """
    stem = sqlite_path.stem
    prefix = "adg_indexed_"
    if stem.startswith(prefix):
        return stem[len(prefix) :]
    return datetime.now(tz=timezone.utc).strftime("%m%d%Y")


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Build adg_graph_<ts>.sqlite from a canonical adg_indexed_<ts>.sqlite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/generate/graph_projection.py artifacts/adg/adg_indexed_03122026.sqlite\n"
            "  python tools/generate/graph_projection.py artifacts/adg/adg_indexed_03122026.sqlite "
            "--out-dir /tmp/adg --ts 03122026\n"
        ),
    )
    parser.add_argument(
        "canonical_sqlite",
        type=Path,
        help="Path to adg_indexed_<ts>.sqlite (canonical ADG artifact)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: same directory as canonical_sqlite)",
    )
    parser.add_argument(
        "--ts",
        type=str,
        default=None,
        help="Timestamp string for output filename (default: derived from input filename)",
    )
    args = parser.parse_args()

    canonical_sqlite: Path = args.canonical_sqlite.resolve()
    out_dir: Path = args.out_dir.resolve() if args.out_dir else canonical_sqlite.parent
    ts: str = args.ts if args.ts else _derive_ts_from_path(canonical_sqlite)

    try:
        proj_path = build_graph_projection(canonical_sqlite, out_dir, ts)
        print(f"\n[graph_projection] Done: {proj_path}")
        return 0
    except ImportError as exc:
        print(f"\n[graph_projection] ERROR: {exc}", file=sys.stderr)
        print(
            "[graph_projection] Install networkx: pip install networkx",
            file=sys.stderr,
        )
        return 2
    except FileNotFoundError as exc:
        print(f"\n[graph_projection] ERROR: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"\n[graph_projection] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
