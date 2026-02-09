"""
Import Graph Builder — Cached adjacency map of all internal imports.

Built once per _verify.py run, then passed to enforcement modules that need it.
Consumers: volatile_rules.py, import_verifier.py, cross_layer.py.

Uses AST parsing only (no regex, no heuristics — per §6 AST-Required Refactoring).
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

# Internal roots that constitute "our code" for import resolution.
INTERNAL_ROOTS: frozenset[str] = frozenset(
    {"agentic_core", "apps_lic", "apps_rg", "apps_shared"},
)

# Directories to skip during file collection.
_WALK_EXCLUDES: frozenset[str] = frozenset(
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
    },
)


class ImportEdge:
    """A single import relationship extracted from AST."""

    __slots__ = ("source_file", "target_module", "imported_names", "lineno", "is_star")

    def __init__(
        self,
        source_file: str,
        target_module: str,
        imported_names: tuple[str, ...],
        lineno: int,
        *,
        is_star: bool = False,
    ) -> None:
        self.source_file = source_file
        self.target_module = target_module
        self.imported_names = imported_names
        self.lineno = lineno
        self.is_star = is_star

    def __repr__(self) -> str:
        return f"ImportEdge({self.source_file}:{self.lineno} -> {self.target_module})"


class ImportGraph:
    """Cached adjacency map of all internal imports across SCAN_ROOTS.

    Built once, queried by multiple enforcement modules.
    """

    def __init__(self, root: Path, scan_roots: tuple[str, ...]) -> None:
        self._root = root
        self._scan_roots = scan_roots

        # file (repo-relative, forward-slash) → list of ImportEdge
        self._edges: dict[str, list[ImportEdge]] = {}

        # module path → set of importing files
        self._reverse: dict[str, set[str]] = {}

        # Stats
        self.files_parsed: int = 0
        self.parse_errors: list[str] = []

        self._build()

    # ── Public query API ──

    def edges_from(self, file: str) -> list[ImportEdge]:
        """All import edges originating from a file (repo-relative path)."""
        return self._edges.get(file, [])

    def files_importing_module(self, module_prefix: str) -> set[str]:
        """All files that import from a module matching the prefix."""
        result: set[str] = set()
        for mod, files in self._reverse.items():
            if mod == module_prefix or mod.startswith(module_prefix + "."):
                result.update(files)
        return result

    def files_importing_territory(self, territory: str) -> set[str]:
        """All files outside a territory that import FROM that territory."""
        importers = self.files_importing_module(territory)
        return {f for f in importers if not f.startswith(territory + "/")}

    def resolve_module_path(self, module: str) -> Path | None:
        """Resolve a dotted module path to a filesystem Path, or None."""
        parts = module.split(".")
        # Try as package (directory with __init__.py)
        pkg_path = self._root / "/".join(parts) / "__init__.py"
        if pkg_path.is_file():
            return pkg_path
        # Try as module file
        mod_path = self._root / "/".join(parts[:-1]) / (parts[-1] + ".py")
        if mod_path.is_file():
            return mod_path
        # Try as direct file (e.g. agentic_core.core -> agentic_core/core.py)
        direct_path = self._root / "/".join(parts) + ".py"
        if direct_path.is_file():
            return direct_path
        return None

    def all_files(self) -> set[str]:
        """All repo-relative file paths that were parsed."""
        return set(self._edges.keys())

    # ── Build logic ──

    def _build(self) -> None:
        """Walk SCAN_ROOTS, AST-parse each .py file, extract internal imports."""
        for scan_root in self._scan_roots:
            scan_dir = self._root / scan_root
            if not scan_dir.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(scan_dir):
                dirnames[:] = [d for d in dirnames if d not in _WALK_EXCLUDES]
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    fpath = Path(dirpath) / fn
                    rel = fpath.relative_to(self._root).as_posix()
                    self._parse_file(fpath, rel)

    def _parse_file(self, fpath: Path, rel: str) -> None:
        """Parse a single file and extract internal import edges."""
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        try:
            tree = ast.parse(source, filename=str(fpath))
        except SyntaxError as exc:
            self.parse_errors.append(f"{rel}:{exc.lineno or '?'}: {exc.msg}")
            return

        self.files_parsed += 1
        edges: list[ImportEdge] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top not in INTERNAL_ROOTS:
                    continue
                names = tuple(a.name for a in (node.names or []))
                is_star = "*" in names
                edge = ImportEdge(
                    source_file=rel,
                    target_module=node.module,
                    imported_names=names,
                    lineno=node.lineno,
                    is_star=is_star,
                )
                edges.append(edge)
                self._reverse.setdefault(node.module, set()).add(rel)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in INTERNAL_ROOTS:
                        continue
                    edge = ImportEdge(
                        source_file=rel,
                        target_module=alias.name,
                        imported_names=(alias.name,),
                        lineno=node.lineno,
                    )
                    edges.append(edge)
                    self._reverse.setdefault(alias.name, set()).add(rel)

            # Detect dynamic imports: __import__("...") and importlib.import_module("...")
            elif isinstance(node, ast.Call):
                target_module = self._extract_dynamic_import(node)
                if target_module:
                    edge = ImportEdge(
                        source_file=rel,
                        target_module=target_module,
                        imported_names=(),
                        lineno=node.lineno,
                    )
                    edges.append(edge)
                    self._reverse.setdefault(target_module, set()).add(rel)

        if edges:
            self._edges[rel] = edges

    @staticmethod
    def _extract_dynamic_import(node: ast.Call) -> str | None:
        """Extract module string from __import__("x") or importlib.import_module("x")."""
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"

        if call_name not in ("__import__", "importlib.import_module"):
            return None

        if (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(
                node.args[0].value,
                str,
            )
        ):
            module_str = node.args[0].value
            top = module_str.split(".")[0]
            if top in INTERNAL_ROOTS:
                return module_str
        return None
