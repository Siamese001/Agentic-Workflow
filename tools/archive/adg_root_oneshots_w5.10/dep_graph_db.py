"""Persistent import-graph database for the Agentic-Workflow repo.

Builds a directed NetworkX graph from AST-parsed imports across all SSOT
directories, persists it to a SQLite file, and exposes query helpers:

    build(force=False)          -> DepGraph   # parse + persist (cached)
    blast_radius(module)        -> set[str]   # transitive dependents
    dependencies(module)        -> set[str]   # transitive dependencies
    shortest_path(src, dst)     -> list[str]  # shortest import path
    pinecone_importers()        -> list[str]  # all modules touching Pinecone
    orphans()                   -> list[str]  # no importers AND no imports
    layer_violations()          -> list[tuple] # (src, dst, src_layer, dst_layer)
    cycles()                    -> list[list]  # all import cycles
    subgraph_for_layer(layer)   -> nx.DiGraph

CLI:
    python tools/dep_graph_db.py --build          # (re)build and save
    python tools/dep_graph_db.py --blast module   # blast radius
    python tools/dep_graph_db.py --pinecone       # Pinecone transitive importers
    python tools/dep_graph_db.py --orphans        # orphaned modules
    python tools/dep_graph_db.py --violations     # layer inversions
    python tools/dep_graph_db.py --cycles         # import cycles
    python tools/dep_graph_db.py --stats          # summary counts
"""

from __future__ import annotations

import ast
import json
import pickle
import sqlite3
from pathlib import Path
from typing import Any

try:
    import networkx as nx
except ImportError as _e:
    raise ImportError("networkx required: pip install networkx") from _e
ROOT = Path(__file__).resolve().parent.parent
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)

SSOT_DIRS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]
SSOT_DIR_PATHS = [ROOT / d for d in SSOT_DIRS]
DB_PATH = ROOT / "artifacts" / "dep_graph.sqlite"
LAYER_ORDER: dict[str, int] = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}
PINECONE_MARKERS = ("pinecone", "PineconeSovereign", "pinecone_vector", "pinecone_mcp")


def _get_imports(tree: ast.Module) -> list[str]:
    deps: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                deps.append(node.module)
    return deps


def _module_name(py_path: Path) -> str:
    rel = py_path.relative_to(ROOT).as_posix()
    return rel.replace("/", ".").removesuffix(".py")


def _get_layer(mod: str) -> tuple[int, str | None]:
    for layer_name, rank in LAYER_ORDER.items():
        if layer_name in mod:
            return (rank, layer_name)
    return (-1, None)


def _is_intra_repo(dep: str) -> bool:
    return any(dep == d or dep.startswith(d + ".") for d in SSOT_DIRS)


def _build_graph() -> tuple[nx.DiGraph, dict[str, str], list]:
    """Parse all SSOT Python files and return (DiGraph, module_to_file)."""
    g: nx.DiGraph = nx.DiGraph()
    module_to_file: dict[str, str] = {}
    syntax_errors: list[tuple[str, str]] = []
    for scan_root in SSOT_DIR_PATHS:
        if not scan_root.exists():
            continue
        for py in sorted(scan_root.rglob("*.py")):
            if ".git" in py.parts:
                continue
            mod = _module_name(py)
            rel = py.relative_to(ROOT).as_posix()
            module_to_file[mod] = rel
            layer_rank, layer_name = _get_layer(mod)
            g.add_node(mod, file=rel, layer=layer_name, layer_rank=layer_rank)
            try:
                src = py.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
                syntax_errors.append((rel, str(e)))
                continue
            for dep in _get_imports(tree):
                if _is_intra_repo(dep):
                    g.add_edge(mod, dep)
    return (g, module_to_file, syntax_errors)


def _save(g: nx.DiGraph, module_to_file: dict[str, str], syntax_errors: list) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(
        "\n        CREATE TABLE IF NOT EXISTS graph_blob (\n            id INTEGER PRIMARY KEY,\n            graph_pickle BLOB NOT NULL,\n            module_to_file_json TEXT NOT NULL,\n            syntax_errors_json TEXT NOT NULL,\n            built_at TEXT NOT NULL\n        );\n        DELETE FROM graph_blob;\n    "
    )
    import datetime

    cur.execute(
        "INSERT INTO graph_blob VALUES (1, ?, ?, ?, ?)",
        (
            pickle.dumps(g),
            json.dumps(module_to_file),
            json.dumps(syntax_errors),
            datetime.datetime.now(datetime.UTC).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def _load() -> tuple[nx.DiGraph, dict[str, str], list] | None:
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute(
        "SELECT graph_pickle, module_to_file_json, syntax_errors_json FROM graph_blob WHERE id=1"
    ).fetchone()
    conn.close()
    if row is None:
        return None
    g = pickle.loads(row[0])
    module_to_file = json.loads(row[1])
    syntax_errors = json.loads(row[2])
    return (g, module_to_file, syntax_errors)


class DepGraph:
    """Queryable wrapper around a NetworkX DiGraph of the repo's import graph."""

    def __init__(self, g: nx.DiGraph, module_to_file: dict[str, str], syntax_errors: list) -> None:
        self._g = g
        self._module_to_file = module_to_file
        self._syntax_errors = syntax_errors

    def stats(self) -> dict[str, Any]:
        return {
            "total_nodes": self._g.number_of_nodes(),
            "total_edges": self._g.number_of_edges(),
            "total_unique_modules": len(self._module_to_file),
            "orphan_count": len(self.orphans()),
            "cycle_count": len(self.cycles()),
            "layer_violation_count": len(self.layer_violations()),
            "pinecone_importer_count": len(self.pinecone_importers()),
            "syntax_error_count": len(self._syntax_errors),
        }

    def blast_radius(self, module: str) -> set[str]:
        """All modules that (transitively) import `module`."""
        if module not in self._g:
            return set()
        return set(nx.ancestors(self._g.reverse(copy=False), module))

    def dependencies(self, module: str) -> set[str]:
        """All modules that `module` (transitively) imports."""
        try:
            return set(nx.descendants(self._g, module))
        except (ValueError, TypeError, RuntimeError) as e:
            return set()

    def direct_dependents(self, module: str) -> list[str]:
        """Modules that directly import `module` (1-hop)."""
        if module not in self._g:
            return []
        return list(self._g.predecessors(module))

    def direct_dependencies(self, module: str) -> list[str]:
        """Modules that `module` directly imports (1-hop)."""
        if module not in self._g:
            return []
        return list(self._g.successors(module))

    def shortest_path(self, src: str, dst: str) -> list[str]:
        """Shortest directed import path from src to dst. Empty list if none."""
        try:
            return nx.shortest_path(self._g, src, dst)  # guardian:  should be handled with specific context
        except (nx.NetworkXNoPath, nx.NodeNotFound):  # guardian: allow-silent-swallow - acceptable exception handling
            return []

    def all_paths(self, src: str, dst: str, cutoff: int = 6) -> list[list[str]]:
        """All simple directed paths from src to dst (up to cutoff length)."""
        if src not in self._g or dst not in self._g:
            return []
        try:
            return list(nx.all_simple_paths(self._g, src, dst, cutoff=cutoff))
        except (ValueError, TypeError, RuntimeError) as e:
            return []

    def pinecone_nodes(self) -> list[str]:
        """Nodes whose module name contains a Pinecone marker."""
        return [n for n in self._g.nodes if any(m.lower() in n.lower() for m in PINECONE_MARKERS)]

    def pinecone_importers(self) -> list[str]:
        """All modules that (transitively) import any Pinecone node."""
        importers: set[str] = set()
        for pn in self.pinecone_nodes():
            importers.update(self.blast_radius(pn))
            importers.add(pn)
        return sorted(importers)

    def pinecone_import_paths(self) -> list[tuple[str, list[str]]]:
        """For each non-Pinecone module that imports a Pinecone node, return
        (module, shortest_path_to_pinecone_node)."""
        results: list[tuple[str, list[str]]] = []
        pinecone = set(self.pinecone_nodes())
        for importer in self.pinecone_importers():
            if importer in pinecone:
                continue
            for pn in pinecone:
                path = self.shortest_path(importer, pn)
                if path:
                    results.append((importer, path))
                    break
        return results

    def orphans(self) -> list[str]:
        """Modules with no inbound edges (not imported) AND no outbound edges
        (imports nothing in-repo). Excludes __init__ files."""
        result = []
        for n in self._g.nodes:
            if n.endswith("__init__"):
                continue
            if self._g.in_degree(n) == 0 and self._g.out_degree(n) == 0:
                result.append(n)
        return sorted(result)

    def unreachable_from(self, root: str) -> list[str]:
        """Modules not reachable (by import chain) starting from `root`."""
        try:
            reachable = nx.descendants(self._g, root) | {root}
        except (ValueError, TypeError, RuntimeError) as e:
            reachable = set()
        return sorted(n for n in self._g.nodes if n not in reachable)

    def cycles(self) -> list[list[str]]:
        """All simple cycles in the import graph."""
        return list(nx.simple_cycles(self._g))

    def layer_violations(self) -> list[tuple[str, str, str, str]]:
        """(src, dst, src_layer, dst_layer) where a lower-numbered layer
        imports a higher-numbered layer."""
        violations = []
        for src, dst in self._g.edges:
            src_rank, src_layer = _get_layer(src)
            dst_rank, dst_layer = _get_layer(dst)
            if src_rank < 0 or dst_rank < 0:
                continue
            if dst_rank > src_rank:
                violations.append((src, dst, src_layer, dst_layer))
        return violations

    def subgraph_for_layer(self, layer: str) -> nx.DiGraph:
        """Extract the subgraph containing only nodes in `layer`."""
        nodes = [n for n in self._g.nodes if layer in n]
        return self._g.subgraph(nodes).copy()

    def fan_in_top(self, n: int = 20) -> list[tuple[str, int]]:
        """Top n most-imported modules (highest fan-in)."""
        return sorted(
            ((node, self._g.in_degree(node)) for node in self._g.nodes), key=lambda x: x[1], reverse=True
        )[:n]

    def fan_out_top(self, n: int = 15) -> list[tuple[str, int]]:
        """Top n modules with most imports (highest fan-out)."""
        return sorted(
            ((node, self._g.out_degree(node)) for node in self._g.nodes), key=lambda x: x[1], reverse=True
        )[:n]

    def file_for(self, module: str) -> str | None:
        """Return the relative file path for a module name, or None."""
        return self._module_to_file.get(module)

    def module_for_file(self, rel_path: str) -> str | None:
        """Reverse lookup: file path → module name."""
        for mod, fp in self._module_to_file.items():
            if fp == rel_path or fp == rel_path.replace("\\", "/"):
                return mod
        return None

    def syntax_errors(self) -> list[tuple[str, str]]:
        return list(self._syntax_errors)


def build(force: bool = False) -> DepGraph:
    """Build (or load from cache) the persistent dep graph.

    Args:
        force: If True, re-parse even if DB exists.

    Returns:
        DepGraph instance ready for queries.
    """
    if not force:
        cached = _load()
        if cached is not None:
            return DepGraph(*cached)
    g, module_to_file, syntax_errors = _build_graph()
    _save(g, module_to_file, syntax_errors)
    return DepGraph(g, module_to_file, syntax_errors)


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Dep graph DB query tool")
    parser.add_argument("--build", action="store_true", help="(Re)build graph from source")
    parser.add_argument("--blast", metavar="MODULE", help="Show blast radius for MODULE")
    parser.add_argument("--deps", metavar="MODULE", help="Show transitive dependencies of MODULE")
    parser.add_argument("--path", nargs=2, metavar=("SRC", "DST"), help="Shortest import path")
    parser.add_argument("--pinecone", action="store_true", help="List all Pinecone importers")
    parser.add_argument("--pinecone-paths", action="store_true", help="Show import paths to Pinecone")
    parser.add_argument("--orphans", action="store_true", help="List orphaned modules")
    parser.add_argument("--violations", action="store_true", help="List layer inversions")
    parser.add_argument("--cycles", action="store_true", help="List import cycles")
    parser.add_argument("--stats", action="store_true", help="Print summary stats")
    parser.add_argument("--fan-in", action="store_true", help="Top 20 most-imported modules")
    args = parser.parse_args()
    force = bool(args.build)
    dg = build(force=force)
    if args.build:
        s = dg.stats()
        print("Graph built and saved to:", DB_PATH)
        print(f"  nodes={s['total_nodes']}  edges={s['total_edges']}")
        print(f"  orphans={s['orphan_count']}  cycles={s['cycle_count']}")
        print(f"  layer_violations={s['layer_violation_count']}")
        print(f"  pinecone_importers={s['pinecone_importer_count']}")
    elif args.stats:
        for k, v in dg.stats().items():
            print(f"  {k}: {v}")
    elif args.blast:
        radius = dg.blast_radius(args.blast)
        print(f"Blast radius of '{args.blast}': {len(radius)} modules")
        for m in sorted(radius)[:50]:
            print(" ", m)
        if len(radius) > 50:
            print(f"  ... and {len(radius) - 50} more")
    elif args.deps:
        deps = dg.dependencies(args.deps)
        print(f"Dependencies of '{args.deps}': {len(deps)} modules")
        for m in sorted(deps)[:50]:
            print(" ", m)
    elif args.path:
        path = dg.shortest_path(args.path[0], args.path[1])
        if path:
            print(" -> ".join(path))
        else:
            print("No import path found")
    elif args.pinecone:
        importers = dg.pinecone_importers()
        print(f"Pinecone importers (transitive): {len(importers)}")
        for m in importers:
            print(" ", m)
    elif args.pinecone_paths:
        for mod, path in dg.pinecone_import_paths():
            print(f"  {mod}")
            print(f"    via: {' -> '.join(path)}")
    elif args.orphans:
        orph = dg.orphans()
        print(f"Orphaned modules: {len(orph)}")
        for m in orph[:60]:
            print(" ", m)
        if len(orph) > 60:
            print(f"  ... and {len(orph) - 60} more")
    elif args.violations:
        viols = dg.layer_violations()
        print(f"Layer violations: {len(viols)}")
        for src, dst, sl, dl in viols[:30]:
            print(f"  {src} ({sl}) -> {dst} ({dl})")
    elif args.cycles:
        cycs = dg.cycles()
        print(f"Cycles: {len(cycs)}")
        for c in cycs:
            print(" ", " -> ".join(c))
    elif args.fan_in:
        for mod, count in dg.fan_in_top(20):
            print(f"  {count:4d}  {mod}")
    else:
        parser.print_help()


if __name__ == "__main__":
    _cli()
