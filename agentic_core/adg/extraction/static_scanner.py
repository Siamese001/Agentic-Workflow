"""ADG Static Scanner -- AST-based edge extraction for the Architecture Dependency Graph.

Produces a deterministic, commit-scoped canonical edge list and digest.
All analysis uses Python AST parsing. Regex/grep for structural logic is forbidden.

Output format per run:
    ADG-DETERMINISM-DIGEST: <sha256_hex>

Canonical edge list sort order: from_name, relation_type, to_name, line_no.
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from agentic_core.adg.schema import (
    EMBEDDING_SYMBOLS,
    NETWORK_SYMBOLS,
    PROVIDER_SDK_SYMBOLS,
    WRITE_SIDE_EFFECT_SYMBOLS,
    canonical_name,
    module_path_to_layer,
)

logger = logging.getLogger(__name__)

_SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "system_learning",
    "tools",
)


@dataclass(frozen=True, order=True)
class Edge:
    """A single directed dependency edge in the ADG."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""


@dataclass
class ScanResult:
    """Full output of a single scanner run."""

    edges: list[Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = ""
    commit_sha: str = ""

    def canonical_edge_text(self) -> str:
        """Stable serialization of edges for digest computation."""
        lines = []
        for e in sorted(self.edges):
            lines.append(
                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"
                f"|{e.source_file}|{e.line_no}|{e.symbol}"
            )
        return "\n".join(lines)

    def compute_digest(self) -> str:
        """Compute and store the ADG-DETERMINISM-DIGEST."""
        text = self.canonical_edge_text()
        self.digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.digest

    def print_digest(self) -> None:
        """Print the determinism digest exactly once per run."""
        print(f"ADG-DETERMINISM-DIGEST: {self.digest}")


class _ImportVisitor(ast.NodeVisitor):
    """Extract import edges from an AST."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            imported = alias.name
            to_name = canonical_name("Symbol", imported)
            edge_kind = self._classify_import_kind(imported)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=imported,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            full_sym = f"{module}.{alias.name}" if module else alias.name
            edge_kind = self._classify_import_kind(module)
            to_name = canonical_name("Symbol", full_sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=full_sym,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _classify_import_kind(module_name: str) -> str:
        base = module_name.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network"
        return "import"


class _CallVisitor(ast.NodeVisitor):
    """Extract call edges for sensitive symbols."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            edge_kind, relation = self._classify_call(sym)
            if edge_kind:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type=relation,
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _classify_call(sym: str) -> tuple[str, str]:
        if sym in EMBEDDING_SYMBOLS or any(sym.endswith(e) for e in EMBEDDING_SYMBOLS):
            return "embedding", "instantiates"
        if sym in WRITE_SIDE_EFFECT_SYMBOLS or any(
            sym.endswith(w.split(".")[-1]) for w in WRITE_SIDE_EFFECT_SYMBOLS
        ):
            return "write", "writes_to"
        if sym in NETWORK_SYMBOLS or any(sym.startswith(n.split(".")[0]) for n in NETWORK_SYMBOLS):
            return "network", "invokes_provider"
        base = sym.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network", "invokes_provider"
        return "", ""


def _iter_python_files(repo_root: Path) -> Iterator[Path]:
    """Yield all .py files under SCAN_ROOTS, deterministic (sorted) order."""
    all_files: list[Path] = []
    for scan_root in _SCAN_ROOTS:
        root_path = repo_root / scan_root
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames.sort()
            for fname in sorted(filenames):
                if fname.endswith(".py") and not fname.endswith(".pyc"):
                    all_files.append(Path(dirpath) / fname)
    all_files.sort()
    yield from all_files


def _repo_relative(path: Path, repo_root: Path) -> str:
    """Return forward-slash repo-relative path."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


def _scan_file(filepath: Path, repo_root: Path) -> list[Edge]:
    """Scan a single Python file and return its edges."""
    rel = _repo_relative(filepath, repo_root)
    module_adg = canonical_name("Module", rel)
    edges: list[Edge] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        logger.debug("SyntaxError in %s: %s", filepath, exc)
        return []
    except OSError as exc:
        logger.debug("OSError reading %s: %s", filepath, exc)
        return []

    import_visitor = _ImportVisitor(module_adg, rel)
    import_visitor.visit(tree)
    edges.extend(import_visitor.edges)

    call_visitor = _CallVisitor(module_adg, rel)
    call_visitor.visit(tree)
    edges.extend(call_visitor.edges)

    return edges


class ADGStaticScanner:
    """Main entry point for ADG static analysis.

    Usage:
        scanner = ADGStaticScanner(repo_root=Path("."))
        result = scanner.scan(commit_sha="abc123")
        result.print_digest()
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()

    def scan(self, commit_sha: str = "") -> ScanResult:
        """Run full static scan. Returns ScanResult with digest computed."""
        result = ScanResult(commit_sha=commit_sha)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []

        for filepath in _iter_python_files(self.repo_root):
            rel = _repo_relative(filepath, self.repo_root)
            modules_seen.append(rel)
            file_edges = _scan_file(filepath, self.repo_root)
            all_edges.extend(file_edges)

        result.edges = sorted(set(all_edges))
        result.modules = sorted(modules_seen)
        result.compute_digest()
        return result

    def scan_files(self, files: list[str], commit_sha: str = "") -> ScanResult:
        """Scan only a specific set of files (for PR diff mode).

        files: list of repo-relative forward-slash paths.
        """
        result = ScanResult(commit_sha=commit_sha)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []

        for rel in sorted(files):
            filepath = self.repo_root / rel.replace("/", os.sep)
            if not filepath.exists() or not rel.endswith(".py"):
                continue
            modules_seen.append(rel)
            all_edges.extend(_scan_file(filepath, self.repo_root))

        result.edges = sorted(set(all_edges))
        result.modules = sorted(modules_seen)
        result.compute_digest()
        return result

    def build_reverse_import_graph(self, result: ScanResult) -> dict[str, list[str]]:
        """Build reverse dependency graph: symbol -> list of modules that import it."""
        reverse: dict[str, list[str]] = {}
        for edge in result.edges:
            if edge.relation_type == "imports":
                rev_key = edge.to_name
                if rev_key not in reverse:
                    reverse[rev_key] = []
                if edge.from_name not in reverse[rev_key]:
                    reverse[rev_key].append(edge.from_name)
        for k in reverse:
            reverse[k].sort()
        return reverse

    def module_layer_map(self, result: ScanResult) -> dict[str, str]:
        """Return mapping of module ADG name -> layer label."""
        mapping: dict[str, str] = {}
        for rel in result.modules:
            layer = module_path_to_layer(rel)
            adg_name = canonical_name("Module", rel)
            mapping[adg_name] = layer
        return mapping


__all__ = ["ADGStaticScanner", "Edge", "ScanResult"]
