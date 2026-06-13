"""
Phase 2 helper -- build a static catalog of code symbols.

Walks the canonical Python source roots and uses ast.parse to extract every
top-level ClassDef and FunctionDef name with its file path and line number.

The catalog is then queried by implementation_mapper to resolve anchor
symbols extracted from doc requirements.

Determinism: the walk order is sorted; the catalog is independent of import
order. Catalog construction is in-memory only (no on-disk cache yet).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Roots to walk for code symbols. Test directories are intentionally
# excluded -- those are catalogued separately by test_evidence_scanner.
CODE_ROOTS: Tuple[str, ...] = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "apps_underwriting_ai",
    "infrastructure",
    "system_learning",
    "tools",
)


# Directories to skip even if they live under a code root.
SKIP_DIRS = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "archives",
        "_deleted",
    }
)


@dataclass(frozen=True)
class SymbolLocation:
    """One occurrence of a code symbol in the repo."""

    name: str
    kind: str  # "class" | "function"
    relative_path: str
    line: int


def _is_skipped(p: Path) -> bool:
    parts = set(p.parts)
    return bool(parts & SKIP_DIRS)


def _walk_python_files(repo_root: Path, root: str) -> List[Path]:
    base = repo_root / root
    if not base.exists():
        return []
    out: List[Path] = []
    for p in base.rglob("*.py"):
        if _is_skipped(p):
            continue
        out.append(p)
    return sorted(out)


def _extract_symbols_from_file(
    repo_root: Path, py_path: Path
) -> List[SymbolLocation]:
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []
    try:
        tree = ast.parse(src, filename=str(py_path))
    except SyntaxError:
        return []
    rel = py_path.relative_to(repo_root).as_posix()
    out: List[SymbolLocation] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            out.append(
                SymbolLocation(name=node.name, kind="class", relative_path=rel, line=node.lineno)
            )
            # Also harvest top-level method names of public classes (light)
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not sub.name.startswith("_"):
                        out.append(
                            SymbolLocation(
                                name=f"{node.name}.{sub.name}",
                                kind="method",
                                relative_path=rel,
                                line=sub.lineno,
                            )
                        )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(
                SymbolLocation(
                    name=node.name, kind="function", relative_path=rel, line=node.lineno
                )
            )
    return out


def build_catalog(repo_root: Path) -> Dict[str, List[SymbolLocation]]:
    """Walk all code roots and return {symbol_name: [SymbolLocation, ...]}."""
    catalog: Dict[str, List[SymbolLocation]] = {}
    for root in CODE_ROOTS:
        for py in _walk_python_files(repo_root, root):
            for sym in _extract_symbols_from_file(repo_root, py):
                catalog.setdefault(sym.name, []).append(sym)
    return catalog


def file_count(repo_root: Path) -> int:
    """Count the .py files that would be included in the catalog walk."""
    n = 0
    for root in CODE_ROOTS:
        n += len(_walk_python_files(repo_root, root))
    return n
