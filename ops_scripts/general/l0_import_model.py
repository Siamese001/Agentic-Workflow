"""
L0 Import Model — Deterministic import graph, cycle detection, layer matrix, upward imports.

Produces four JSON artifacts under a specified output directory:
  - import_graph.json       : nodes[] + edges[] (sorted)
  - circular_imports.json   : cycles[] (lexicographically normalized, sorted)
  - upward_imports.json     : edges where src_layer_rank > dst_layer_rank
  - layer_dependency_matrix.json : counts by (src_layer, dst_layer)

Uses AST only (no regex, no heuristics — per §6 AST-Required Refactoring).
Deterministic: sorted keys, sorted lists, no timestamps/UUIDs.

Usage:
    python ops_scripts/general/l0_import_model.py [--output-dir DIR] [--scan-roots R1 R2 ...]

Defaults:
    --output-dir  artifacts/l0_refactor
    --scan-roots  agentic_core apps_lic apps_rg apps_shared
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── Layer map: folder prefix → (layer_name, rank) ──
# Lower rank = lower layer. Upward import = src_rank > dst_rank.
LAYER_MAP: dict[str, tuple[str, int]] = {
    "L0_routing": ("L0_routing", 0),
    "L1_cognition": ("L1_cognition", 1),
    "L2_execution": ("L2_execution", 2),
    "L3_orchestration": ("L3_orchestration", 3),
    "L4_state": ("L4_state", 4),
    "L5_safety": ("L5_safety", 5),
    "L6_observability": ("L6_observability", 6),
}

# Top-level internal roots that constitute "our code".
INTERNAL_ROOTS: frozenset[str] = frozenset(
    {"agentic_core", "apps_lic", "apps_rg", "apps_shared"},
)

# Directories to skip during walk.
WALK_EXCLUDES: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "dist",
        "build",
        ".pytest_cache",
        "node_modules",
        ".nox",
        "archives",
        "dev_tools",
    },
)


def _classify_layer(repo_relative_path: str) -> tuple[str, int]:
    """Classify a repo-relative path into (layer_name, rank).

    Returns ("unknown", -1) if no layer prefix matches.
    For apps_* files, returns the app name as layer with rank -1.
    """
    parts = repo_relative_path.replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] == "agentic_core":
        layer_folder = parts[1]
        if layer_folder in LAYER_MAP:
            return LAYER_MAP[layer_folder]
        # Non-layer agentic_core subfolders (core, base_agents, runtime, etc.)
        return (f"agentic_core.{layer_folder}", -1)
    if parts[0] in ("apps_lic", "apps_rg", "apps_shared"):
        return (parts[0], -1)
    return ("unknown", -1)


def _classify_module_layer(module_path: str) -> tuple[str, int]:
    """Classify a dotted module path into (layer_name, rank)."""
    parts = module_path.split(".")
    if len(parts) >= 2 and parts[0] == "agentic_core":
        layer_folder = parts[1]
        if layer_folder in LAYER_MAP:
            return LAYER_MAP[layer_folder]
        return (f"agentic_core.{layer_folder}", -1)
    if parts[0] in ("apps_lic", "apps_rg", "apps_shared"):
        return (parts[0], -1)
    return ("unknown", -1)


# ── AST import extraction ──


def _extract_imports_from_file(
    fpath: Path,
    repo_root: Path,
) -> tuple[str, list[dict[str, Any]], list[str]]:
    """Parse a single .py file and extract internal import edges.

    Returns (repo_relative_path, edges_list, parse_errors).
    Each edge is a dict with: source, target_module, imported_names, lineno, is_dynamic.
    """
    rel = fpath.relative_to(repo_root).as_posix()
    errors: list[str] = []
    edges: list[dict[str, Any]] = []

    try:
        source = fpath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rel, edges, errors

    try:
        tree = ast.parse(source, filename=str(fpath))
    except SyntaxError as exc:
        errors.append(f"{rel}:{exc.lineno or '?'}: {exc.msg}")
        return rel, edges, errors

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top not in INTERNAL_ROOTS:
                continue
            names = sorted(a.name for a in (node.names or []))
            edges.append(
                {
                    "source": rel,
                    "target_module": node.module,
                    "imported_names": names,
                    "lineno": node.lineno,
                    "is_dynamic": False,
                },
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in INTERNAL_ROOTS:
                    continue
                edges.append(
                    {
                        "source": rel,
                        "target_module": alias.name,
                        "imported_names": [alias.name],
                        "lineno": node.lineno,
                        "is_dynamic": False,
                    },
                )
        elif isinstance(node, ast.Call):
            target_module = _extract_dynamic_import(node)
            if target_module:
                edges.append(
                    {
                        "source": rel,
                        "target_module": target_module,
                        "imported_names": [],
                        "lineno": node.lineno,
                        "is_dynamic": True,
                    },
                )

    return rel, edges, errors


def _extract_dynamic_import(node: ast.Call) -> str | None:
    """Extract module string from __import__('x') or importlib.import_module('x')."""
    call_name = ""
    if isinstance(node.func, ast.Name):
        call_name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            call_name = f"{node.func.value.id}.{node.func.attr}"

    if call_name not in ("__import__", "importlib.import_module"):
        return None

    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        module_str = node.args[0].value
        top = module_str.split(".")[0]
        if top in INTERNAL_ROOTS:
            return module_str
    return None


# ── Cycle detection (Tarjan's SCC on module-level adjacency) ──


def _find_cycles(edges: list[dict[str, Any]]) -> list[list[str]]:
    """Find all strongly connected components with >1 node using Tarjan's algorithm.

    Operates on module-level granularity: source file's module prefix → target module prefix.
    Returns normalized, sorted list of cycles.
    """
    # Build module-level adjacency
    adj: dict[str, set[str]] = {}
    all_nodes: set[str] = set()

    for edge in edges:
        # Convert source file path to module: a/b/c.py → a.b.c
        src_mod = edge["source"].replace("/", ".").removesuffix(".py")
        if src_mod.endswith(".__init__"):
            src_mod = src_mod.removesuffix(".__init__")
        tgt_mod = edge["target_module"]

        # Use top-level module prefix for grouping (up to 3 segments)
        src_key = ".".join(src_mod.split(".")[:3])
        tgt_key = ".".join(tgt_mod.split(".")[:3])

        if src_key != tgt_key:
            adj.setdefault(src_key, set()).add(tgt_key)
            all_nodes.add(src_key)
            all_nodes.add(tgt_key)

    # Tarjan's SCC
    index_counter = [0]
    stack: list[str] = []
    lowlinks: dict[str, int] = {}
    index_map: dict[str, int] = {}
    on_stack: set[str] = set()
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        index_map[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in sorted(adj.get(v, set())):
            if w not in index_map:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], index_map[w])

        if lowlinks[v] == index_map[v]:
            scc: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:
                sccs.append(scc)

    for node in sorted(all_nodes):
        if node not in index_map:
            strongconnect(node)

    # Normalize each cycle: sort members, rotate to lexicographic minimum
    normalized: list[list[str]] = []
    for scc in sccs:
        scc_sorted = sorted(scc)
        normalized.append(scc_sorted)

    normalized.sort()
    return normalized


# ── Main builder ──


def build_model(
    repo_root: Path,
    scan_roots: tuple[str, ...],
    output_dir: Path,
) -> dict[str, Any]:
    """Build the full import model and write JSON artifacts.

    Returns a summary dict.
    """
    all_edges: list[dict[str, Any]] = []
    all_nodes: set[str] = set()
    all_parse_errors: list[str] = []
    files_parsed = 0

    for scan_root in scan_roots:
        scan_dir = repo_root / scan_root
        if not scan_dir.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = sorted(d for d in dirnames if d not in WALK_EXCLUDES)
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                fpath = Path(dirpath) / fn
                rel, edges, errors = _extract_imports_from_file(fpath, repo_root)
                all_nodes.add(rel)
                all_edges.extend(edges)
                all_parse_errors.extend(errors)
                files_parsed += 1

    # ── 1. import_graph.json ──
    nodes_sorted = sorted(all_nodes)
    edges_sorted = sorted(
        all_edges,
        key=lambda e: (e["source"], e["target_module"], e["lineno"]),
    )
    import_graph = {
        "files_parsed": files_parsed,
        "parse_errors": sorted(all_parse_errors),
        "nodes": nodes_sorted,
        "edges": [
            {
                "source": e["source"],
                "target_module": e["target_module"],
                "imported_names": e["imported_names"],
                "lineno": e["lineno"],
                "is_dynamic": e["is_dynamic"],
            }
            for e in edges_sorted
        ],
    }

    # ── 2. circular_imports.json ──
    cycles = _find_cycles(all_edges)
    circular_imports = {
        "cycle_count": len(cycles),
        "cycles": cycles,
    }

    # ── 3. layer_dependency_matrix.json ──
    matrix: dict[str, dict[str, int]] = {}
    for edge in all_edges:
        src_layer, _ = _classify_layer(edge["source"])
        dst_layer, _ = _classify_module_layer(edge["target_module"])
        if src_layer not in matrix:
            matrix[src_layer] = {}
        matrix[src_layer][dst_layer] = matrix[src_layer].get(dst_layer, 0) + 1

    # Sort for determinism
    layer_dep_matrix = {
        "matrix": {k: dict(sorted(v.items())) for k, v in sorted(matrix.items())},
    }

    # ── 4. upward_imports.json ──
    # Upward = src_layer_rank > dst_layer_rank (higher layer importing from lower)
    # Only count edges where BOTH layers have known ranks (>= 0).
    upward_edges: list[dict[str, Any]] = []
    for edge in edges_sorted:
        src_layer, src_rank = _classify_layer(edge["source"])
        dst_layer, dst_rank = _classify_module_layer(edge["target_module"])
        if src_rank >= 0 and dst_rank >= 0 and src_rank > dst_rank:
            upward_edges.append(
                {
                    "source": edge["source"],
                    "source_layer": src_layer,
                    "source_rank": src_rank,
                    "target_module": edge["target_module"],
                    "target_layer": dst_layer,
                    "target_rank": dst_rank,
                    "lineno": edge["lineno"],
                },
            )

    upward_imports = {
        "upward_import_count": len(upward_edges),
        "edges": upward_edges,
    }

    # ── Write artifacts ──
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "import_graph.json": import_graph,
        "circular_imports.json": circular_imports,
        "layer_dependency_matrix.json": layer_dep_matrix,
        "upward_imports.json": upward_imports,
    }

    for filename, data in artifacts.items():
        outpath = output_dir / filename
        outpath.write_text(
            json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    summary = {
        "files_parsed": files_parsed,
        "parse_errors": len(all_parse_errors),
        "total_edges": len(all_edges),
        "total_nodes": len(nodes_sorted),
        "cycle_count": len(cycles),
        "upward_import_count": len(upward_edges),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="L0 Import Model — deterministic artifacts")
    parser.add_argument(
        "--output-dir",
        default="artifacts/l0_refactor",
        help="Output directory for JSON artifacts (default: artifacts/l0_refactor)",
    )
    parser.add_argument(
        "--scan-roots",
        nargs="+",
        default=["agentic_core", "apps_lic", "apps_rg", "apps_shared"],
        help="Top-level directories to scan (default: agentic_core apps_lic apps_rg apps_shared)",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    output_dir = Path(args.output_dir)
    scan_roots = tuple(args.scan_roots)

    print(f"repo_root: {repo_root}")
    print(f"output_dir: {output_dir}")
    print(f"scan_roots: {scan_roots}")
    print()

    summary = build_model(repo_root, scan_roots, output_dir)

    print("=== L0 Import Model Summary ===")
    for k, v in sorted(summary.items()):
        print(f"  {k}: {v}")
    print()
    print(f"Artifacts written to: {output_dir.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
