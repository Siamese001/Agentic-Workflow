"""ADG Semantic Graph Builder — Phase 1/2/3 of the test stabilization pipeline.

Layers AST-level semantic nodes on top of the existing module-level ADG artifact.

Produces:
  artifacts/adg_semantic_graph.json     — full semantic node+edge graph
  artifacts/adg_test_surface_map.json   — symbol -> [test_ids]
  artifacts/adg_failure_clusters.json   — ranked risk clusters
  artifacts/adg_validation_report.json  — Phase 0 validation result

Node types extracted:
  ModuleNode, ClassNode, FunctionNode, TestFunctionNode, FixtureNode,
  ParametrizedTestNode, AssertionNode, MockNode

Edge types extracted:
  IMPORT_EDGE, CALL_EDGE, INHERIT_EDGE, TEST_COVERS_EDGE,
  FIXTURE_DEPENDS_EDGE, ASSERT_TARGET_EDGE, MOCK_TARGET_EDGE
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# guardian: allow-global_mutation
_REPO_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("adg_semantic_builder")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SemanticNode:
    node_id: str
    node_type: str          # ModuleNode, ClassNode, FunctionNode, TestFunctionNode, FixtureNode, ParametrizedTestNode, AssertionNode, MockNode
    module_path: str
    name: str
    qualified_name: str
    lineno: int = 0
    decorators: list[str] = field(default_factory=list)
    layer: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "module_path": self.module_path,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "lineno": self.lineno,
            "decorators": self.decorators,
            "layer": self.layer,
            "meta": self.meta,
        }


@dataclass
class SemanticEdge:
    edge_type: str          # IMPORT_EDGE, CALL_EDGE, INHERIT_EDGE, TEST_COVERS_EDGE, FIXTURE_DEPENDS_EDGE, ASSERT_TARGET_EDGE, MOCK_TARGET_EDGE
    from_id: str
    to_id: str
    from_module: str
    to_module: str
    lineno: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "edge_type": self.edge_type,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "from_module": self.from_module,
            "to_module": self.to_module,
            "lineno": self.lineno,
            "meta": self.meta,
        }


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    names = []
    for d in node.decorator_list:
        if isinstance(d, ast.Name):
            names.append(d.id)
        elif isinstance(d, ast.Attribute):
            names.append(f"{ast.unparse(d)}")
        elif isinstance(d, ast.Call):
            if isinstance(d.func, ast.Name):
                names.append(d.func.id)
            elif isinstance(d.func, ast.Attribute):
                names.append(ast.unparse(d.func))
    return names


def _is_test_function(name: str, decorators: list[str]) -> bool:
    return name.startswith("test_") or name.startswith("Test")


def _is_fixture(decorators: list[str]) -> bool:
    return any("fixture" in d for d in decorators)


def _is_parametrized(decorators: list[str]) -> bool:
    return any("parametrize" in d for d in decorators)


def _is_mock_call(node: ast.expr) -> bool:
    s = ast.unparse(node)
    return any(k in s for k in ("mock.", "Mock(", "MagicMock(", "patch(", "patch.object(", "mocker.patch"))


def _extract_assert_targets(body: list[ast.stmt]) -> list[str]:
    """Walk body and collect names/attrs used in assert statements."""
    targets: list[str] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Assert):
            targets.append(ast.unparse(node.test)[:120])
    return targets


def _extract_mock_targets(body: list[ast.stmt]) -> list[str]:
    targets: list[str] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Call) and _is_mock_call(node):
            targets.append(ast.unparse(node)[:120])
    return targets


def _extract_fixture_deps(args: ast.arguments) -> list[str]:
    return [a.arg for a in args.args]


def _node_id(module_path: str, qualified_name: str) -> str:
    raw = f"{module_path}::{qualified_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-file AST extraction
# ---------------------------------------------------------------------------

def extract_file(rel_path: str, source: str) -> tuple[list[SemanticNode], list[SemanticEdge]]:
    """Parse one Python file and return all semantic nodes and intra-file edges."""
    from agentic_core.adg.schema import module_path_to_layer

    nodes: list[SemanticNode] = []
    edges: list[SemanticEdge] = []

    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError:
        return nodes, edges

    layer = module_path_to_layer(rel_path)
    module_qname = rel_path.replace("/", ".").removesuffix(".py")
    module_nid = _node_id(rel_path, module_qname)

    module_node = SemanticNode(
        node_id=module_nid,
        node_type="ModuleNode",
        module_path=rel_path,
        name=rel_path.split("/")[-1],
        qualified_name=module_qname,
        layer=layer,
    )
    nodes.append(module_node)

    # Collect top-level imports for IMPORT_EDGE
    import_targets: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_targets.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_targets.append((node.module, node.lineno))

    for imp_name, lineno in import_targets:
        # Convert dotted module name to a path candidate
        candidate_path = imp_name.replace(".", "/") + ".py"
        imp_id = _node_id(candidate_path, imp_name)
        edges.append(SemanticEdge(
            edge_type="IMPORT_EDGE",
            from_id=module_nid,
            to_id=imp_id,
            from_module=rel_path,
            to_module=candidate_path,
            lineno=lineno,
        ))

    # Walk top-level class and function definitions
    fixture_names: set[str] = set()
    test_function_ids: dict[str, str] = {}  # func_name -> node_id

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = _decorator_names(node)
            is_fixture = _is_fixture(decorators)
            is_test = _is_test_function(node.name, decorators)
            is_parametrized = _is_parametrized(decorators)

            qname = f"{module_qname}.{node.name}"
            nid = _node_id(rel_path, qname)

            if is_fixture:
                fixture_names.add(node.name)
                ntype = "FixtureNode"
            elif is_parametrized and is_test:
                ntype = "ParametrizedTestNode"
            elif is_test:
                ntype = "TestFunctionNode"
            else:
                ntype = "FunctionNode"

            fn_node = SemanticNode(
                node_id=nid,
                node_type=ntype,
                module_path=rel_path,
                name=node.name,
                qualified_name=qname,
                lineno=node.lineno,
                decorators=decorators,
                layer=layer,
            )

            if is_test or is_fixture:
                # Assert targets
                assert_targets = _extract_assert_targets(node.body)
                mock_targets = _extract_mock_targets(node.body)
                fn_node.meta["assert_targets"] = assert_targets[:20]
                fn_node.meta["mock_targets"] = mock_targets[:10]

                # Fixture dependencies from function args
                fixture_deps = _extract_fixture_deps(node.args)
                fn_node.meta["fixture_deps"] = fixture_deps

                for dep_name in fixture_deps:
                    dep_id = _node_id(rel_path, f"{module_qname}.{dep_name}")
                    edges.append(SemanticEdge(
                        edge_type="FIXTURE_DEPENDS_EDGE",
                        from_id=nid,
                        to_id=dep_id,
                        from_module=rel_path,
                        to_module=rel_path,
                        lineno=node.lineno,
                        meta={"dep_name": dep_name},
                    ))

            nodes.append(fn_node)
            if is_test:
                test_function_ids[node.name] = nid

        elif isinstance(node, ast.ClassDef):
            decorators = _decorator_names(node)
            qname = f"{module_qname}.{node.name}"
            nid = _node_id(rel_path, qname)

            bases = []
            for b in node.bases:
                bases.append(ast.unparse(b))

            class_node = SemanticNode(
                node_id=nid,
                node_type="ClassNode",
                module_path=rel_path,
                name=node.name,
                qualified_name=qname,
                lineno=node.lineno,
                decorators=decorators,
                layer=layer,
                meta={"bases": bases},
            )
            nodes.append(class_node)

            for base_name in bases:
                base_id = _node_id(rel_path, base_name)
                edges.append(SemanticEdge(
                    edge_type="INHERIT_EDGE",
                    from_id=nid,
                    to_id=base_id,
                    from_module=rel_path,
                    to_module=rel_path,
                    lineno=node.lineno,
                    meta={"base": base_name},
                ))

    return nodes, edges


# ---------------------------------------------------------------------------
# Repository-wide scan
# ---------------------------------------------------------------------------

_SCAN_DIRS = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "tools",
    "ops_scripts",
    "tests",
    "system_learning",
]

_EXCLUDE_PATTERNS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", "dist", "build",
}


def iter_python_files(repo_root: Path):
    for scan_dir in _SCAN_DIRS:
        base = repo_root / scan_dir
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            if any(part in _EXCLUDE_PATTERNS for part in py_file.parts):
                continue
            try:
                rel = py_file.relative_to(repo_root).as_posix()
                yield rel, py_file
            except ValueError:
                continue


def build_semantic_graph(repo_root: Path) -> dict:
    """Full semantic graph build. Returns the graph dict."""
    all_nodes: list[SemanticNode] = []
    all_edges: list[SemanticEdge] = []

    file_count = 0
    error_count = 0

    for rel_path, abs_path in iter_python_files(repo_root):
        try:
            source = abs_path.read_text(encoding="utf-8", errors="replace")
        # guardian: allow-silent-swallow
        except Exception:
            error_count += 1
            continue
        file_nodes, file_edges = extract_file(rel_path, source)
        all_nodes.extend(file_nodes)
        all_edges.extend(file_edges)
        file_count += 1
        if file_count % 200 == 0:
            logger.info("Scanned %d files, %d nodes, %d edges...", file_count, len(all_nodes), len(all_edges))

    logger.info("Scan complete: %d files, %d nodes, %d edges, %d errors", file_count, len(all_nodes), len(all_edges), error_count)

    # Split by type
    symbols = [n for n in all_nodes if n.node_type in ("FunctionNode", "ClassNode")]
    tests = [n for n in all_nodes if n.node_type in ("TestFunctionNode", "ParametrizedTestNode")]
    fixtures = [n for n in all_nodes if n.node_type == "FixtureNode"]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(
        json.dumps([e.to_dict() for e in all_edges], sort_keys=True).encode()
    ).hexdigest()

    return {
        "schema_version": "semantic-1.0.0",
        "timestamp": ts,
        "digest": digest,
        "file_count": file_count,
        "entities": [n.to_dict() for n in all_nodes],
        "relations": [e.to_dict() for e in all_edges],
        "symbols": [n.to_dict() for n in symbols],
        "tests": [n.to_dict() for n in tests],
        "fixtures": [n.to_dict() for n in fixtures],
        "counts": {
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "module_nodes": sum(1 for n in all_nodes if n.node_type == "ModuleNode"),
            "class_nodes": sum(1 for n in all_nodes if n.node_type == "ClassNode"),
            "function_nodes": sum(1 for n in all_nodes if n.node_type == "FunctionNode"),
            "test_functions": len(tests),
            "fixtures": len(fixtures),
            "parametrized": sum(1 for n in all_nodes if n.node_type == "ParametrizedTestNode"),
        },
    }


# ---------------------------------------------------------------------------
# Phase 2: Test surface map
# ---------------------------------------------------------------------------

def build_test_surface_map(graph: dict) -> dict:
    """Map every non-test symbol -> list of test_ids that cover it.

    Strategy: a test covers a symbol if:
      1. The test module imports the symbol's module (IMPORT_EDGE)
      2. OR the test's assert_targets mention the symbol name
    """
    # Build module -> test list
    module_to_tests: dict[str, list[str]] = defaultdict(list)
    for node in graph["tests"]:
        mod = node["module_path"]
        qn = node["qualified_name"]
        test_id = f"{mod}::{node['name']}"
        module_to_tests[mod].append(test_id)

    # Build import edges: test_module -> set of imported modules
    test_imports: dict[str, set[str]] = defaultdict(set)
    for edge in graph["relations"]:
        if edge["edge_type"] == "IMPORT_EDGE":
            from_mod = edge["from_module"]
            to_mod = edge["to_module"]
            if from_mod.startswith("tests/"):
                test_imports[from_mod].add(to_mod)

    # Build symbol map: module -> [symbols]
    module_to_symbols: dict[str, list[str]] = defaultdict(list)
    for sym in graph["symbols"]:
        module_to_symbols[sym["module_path"]].append(sym["name"])

    # Now build the coverage map: symbol_qname -> [test_ids]
    surface_map: dict[str, list[str]] = {}

    for sym in graph["symbols"]:
        sym_mod = sym["module_path"]
        sym_name = sym["name"]
        sym_qname = sym["qualified_name"]

        covering_tests: list[str] = []

        # Find all test modules that import this symbol's module
        for test_mod, imported in test_imports.items():
            # Direct module import match
            if sym_mod in imported or any(
                sym_mod.startswith(imp.replace(".", "/")) or
                imp.startswith(sym_mod.replace("/", ".").removesuffix(".py"))
                for imp in imported
            ):
                covering_tests.extend(module_to_tests.get(test_mod, []))

        # Also check assert targets in tests for explicit symbol mention
        for test_node in graph["tests"]:
            for target in test_node.get("meta", {}).get("assert_targets", []):
                if sym_name in target:
                    tid = f"{test_node['module_path']}::{test_node['name']}"
                    if tid not in covering_tests:
                        covering_tests.append(tid)

        if covering_tests:
            surface_map[sym_qname] = sorted(set(covering_tests))

    # Also build module-level map (used in Phase 3)
    module_surface: dict[str, list[str]] = {}
    for test_mod, imported in test_imports.items():
        for imp_mod in imported:
            tests_for_mod = module_to_tests.get(test_mod, [])
            if imp_mod not in module_surface:
                module_surface[imp_mod] = []
            module_surface[imp_mod].extend(tests_for_mod)

    # Deduplicate
    for k in module_surface:
        module_surface[k] = sorted(set(module_surface[k]))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "symbol_coverage": surface_map,
        "module_coverage": module_surface,
        "covered_symbol_count": len(surface_map),
        "covered_module_count": len(module_surface),
    }


# ---------------------------------------------------------------------------
# Phase 3: Root cause cluster discovery
# ---------------------------------------------------------------------------

def build_failure_clusters(graph: dict, surface_map: dict) -> dict:
    """Rank modules by risk signals: fan-out, test surface size, centrality.

    No pytest is run. Risk is inferred purely from graph signals.
    """
    from agentic_core.adg.schema import module_path_to_layer

    module_coverage = surface_map.get("module_coverage", {})

    # Fan-out per module (count of outgoing IMPORT_EDGEs)
    fan_out: dict[str, int] = defaultdict(int)
    fan_in: dict[str, int] = defaultdict(int)
    for edge in graph["relations"]:
        if edge["edge_type"] == "IMPORT_EDGE":
            fan_out[edge["from_module"]] += 1
            fan_in[edge["to_module"]] += 1

    # Test surface size per module
    test_surface_size: dict[str, int] = {
        mod: len(tests) for mod, tests in module_coverage.items()
    }

    # Collect all non-test modules
    all_modules = set(
        n["module_path"] for n in graph["entities"]
        if n["node_type"] == "ModuleNode" and not n["module_path"].startswith("tests/")
    )

    clusters = []
    for mod in all_modules:
        fo = fan_out.get(mod, 0)
        fi = fan_in.get(mod, 0)
        ts_size = test_surface_size.get(mod, 0)
        layer = module_path_to_layer(mod)

        # Risk score: weighted combination
        risk = fo * 2 + fi * 3 + ts_size * 1
        if risk == 0:
            continue

        clusters.append({
            "module": mod,
            "layer": layer,
            "fan_out": fo,
            "fan_in": fi,
            "test_surface_size": ts_size,
            "risk_score": risk,
            "covering_tests": module_coverage.get(mod, []),
        })

    # Sort by risk descending
    clusters.sort(key=lambda c: c["risk_score"], reverse=True)
    top_clusters = clusters[:50]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "total_modules_analyzed": len(all_modules),
        "clusters_with_risk": len(clusters),
        "top_clusters": top_clusters,
    }


# ---------------------------------------------------------------------------
# Phase 0: Validation report
# ---------------------------------------------------------------------------

def build_validation_report(latest_artifact_path: Path, semantic_graph: dict) -> dict:
    try:
        adg = json.loads(latest_artifact_path.read_text(encoding="utf-8"))
    # guardian: allow-silent-swallow
    except Exception as e:
        adg = {}
        logger.warning("Could not load adg_latest.json: %s", e)

    required_fields = ["entities", "relations", "symbols", "tests", "fixtures"]
    missing_in_adg = [f for f in required_fields if not adg.get(f)]
    missing_in_sem = [f for f in required_fields if not semantic_graph.get(f)]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "timestamp": ts,
        "adg_latest_path": str(latest_artifact_path),
        "adg_entity_count": len(adg.get("entities", [])),
        "adg_relation_count": len(adg.get("relations", [])),
        "adg_missing_fields": missing_in_adg,
        "semantic_graph_node_count": semantic_graph["counts"]["total_nodes"],
        "semantic_graph_edge_count": semantic_graph["counts"]["total_edges"],
        "semantic_missing_fields": missing_in_sem,
        "test_node_count": semantic_graph["counts"]["test_functions"],
        "fixture_count": semantic_graph["counts"]["fixtures"],
        "symbol_count": len(semantic_graph["symbols"]),
        "validation_passed": len(missing_in_sem) == 0,
    }


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    artifacts_dir = _REPO_ROOT / "artifacts"
    adg_dir = _REPO_ROOT / "artifacts" / "adg"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    adg_dir.mkdir(parents=True, exist_ok=True)

    latest = adg_dir / "adg_latest.json"
    if not latest.exists():
        logger.error("adg_latest.json not found. Run: python tools/adg_cli.py build --rebuild")
        return 1

    # --- PHASE 1: Semantic graph ---
    logger.info("PHASE 1: Building semantic graph...")
    sem_graph = build_semantic_graph(_REPO_ROOT)
    sem_path = artifacts_dir / "adg_semantic_graph.json"
    sem_path.write_text(json.dumps(sem_graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 1 DONE: %d nodes, %d edges -> %s",
                sem_graph["counts"]["total_nodes"], sem_graph["counts"]["total_edges"], sem_path)

    # --- PHASE 2: Test surface map ---
    logger.info("PHASE 2: Building test surface map...")
    surface_map = build_test_surface_map(sem_graph)
    surf_path = artifacts_dir / "adg_test_surface_map.json"
    surf_path.write_text(json.dumps(surface_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 2 DONE: %d symbols covered, %d modules covered -> %s",
                surface_map["covered_symbol_count"], surface_map["covered_module_count"], surf_path)

    # --- PHASE 3: Root cause clusters ---
    logger.info("PHASE 3: Building failure clusters...")
    clusters = build_failure_clusters(sem_graph, surface_map)
    clust_path = artifacts_dir / "adg_failure_clusters.json"
    clust_path.write_text(json.dumps(clusters, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 3 DONE: %d clusters (top 50 ranked) -> %s",
                clusters["clusters_with_risk"], clust_path)

    # --- PHASE 0: Validation report ---
    logger.info("PHASE 0: Emitting validation report...")
    validation = build_validation_report(latest, sem_graph)
    val_path = artifacts_dir / "adg_validation_report.json"
    val_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("PHASE 0 DONE: validation_passed=%s -> %s", validation["validation_passed"], val_path)

    # Print summary
    print("\n=== ADG SEMANTIC GRAPH SUMMARY ===")
    print(f"  ModuleNodes:       {sem_graph['counts']['module_nodes']}")
    print(f"  ClassNodes:        {sem_graph['counts']['class_nodes']}")
    print(f"  FunctionNodes:     {sem_graph['counts']['function_nodes']}")
    print(f"  TestFunctionNodes: {sem_graph['counts']['test_functions']}")
    print(f"  FixtureNodes:      {sem_graph['counts']['fixtures']}")
    print(f"  ParametrizedTests: {sem_graph['counts']['parametrized']}")
    print(f"  Total edges:       {sem_graph['counts']['total_edges']}")
    print(f"\n=== TEST SURFACE MAP ===")
    print(f"  Symbols covered:   {surface_map['covered_symbol_count']}")
    print(f"  Modules covered:   {surface_map['covered_module_count']}")
    print(f"\n=== TOP 10 RISK CLUSTERS ===")
    for c in clusters["top_clusters"][:10]:
        print(f"  {c['module']:<70} tests={c['test_surface_size']:>4}  risk={c['risk_score']:>6}")
    print(f"\n=== VALIDATION ===")
    print(f"  passed={validation['validation_passed']}")
    print(f"\nArtifacts written:")
    print(f"  {val_path}")
    print(f"  {sem_path}")
    print(f"  {surf_path}")
    print(f"  {clust_path}")

    return 0 if validation["validation_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
