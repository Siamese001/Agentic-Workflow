from agentic_core.L2_execution.tools import write_gateway as _wg

"\nLazy Seam Scanner - Phase 4 Option A: Thin wrapper over Phase 3B metric.\n\nThis scanner uses the exact Phase 3B lazy upward import metric to ensure\nthe same seam universe (44 seams) and scan scope.\n"
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class LazyUpwardImport:
    """A lazy upward import excluded by function/try guard."""

    source_file: Path
    source_layer: int
    target_layer: int
    import_statement: str
    line_number: int
    context: str


LAYER_PATTERN = re.compile("^L(\\d+)_")
IMPORT_LAYER_PATTERN = re.compile("agentic_core\\.L(\\d+)_")


def layer_of_path(path: Path, agentic_root: Path) -> int | None:
    """Extract layer number from a path."""
    try:
        rel = path.relative_to(agentic_root)
    except ValueError:
        return None
    parts = rel.parts
    if not parts:
        return None
    match = LAYER_PATTERN.match(parts[0])
    if match:
        return int(match.group(1))
    return None


def extract_import_targets(node: ast.AST) -> list[tuple[str, int]]:
    """Extract import target strings and line numbers from an AST node."""
    targets = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            targets.append((alias.name, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            targets.append((node.module, node.lineno))
    return targets


def _is_inside_function_or_guarded(tree: ast.AST, target_lineno: int) -> bool:
    """Check if a line is inside a function, method, or try/except block."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
    return False


def _get_enclosing_function(
    tree: ast.AST, target_lineno: int
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return the innermost FunctionDef/AsyncFunctionDef enclosing target_lineno."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        if best is None or (
                            best.end_lineno is not None
                            and node.end_lineno - node.lineno < best.end_lineno - best.lineno
                        ):
                            best = node
    return best


def _is_inside_try_module_scope(tree: ast.AST, target_lineno: int) -> bool:
    """Return True if target_lineno is inside a Try block at module scope."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        enclosing_fn = _get_enclosing_function(tree, node.lineno)
                        if enclosing_fn is None:
                            return True
    return False


def collect_lazy_upward_imports(agentic_root: Path) -> list[LazyUpwardImport]:
    """Collect all upward imports excluded ONLY because they are inside a
    function/try guard (the 'lazy seam')."""
    results: list[LazyUpwardImport] = []
    for layer in range(7):
        layer_dir = None
        for item in agentic_root.iterdir():
            if item.is_dir() and item.name.startswith(f"L{layer}_"):
                layer_dir = item
                break
        if layer_dir is None:
            continue
        for py_file in layer_dir.rglob("*.py"):
            try:
                rel = py_file.relative_to(agentic_root)
            except ValueError:
                continue
            parts = rel.parts
            if not parts:
                continue
            m = LAYER_PATTERN.match(parts[0])
            if not m:
                continue
            src_layer = int(m.group(1))
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                targets = extract_import_targets(node)
                for import_str, line_no in targets:
                    match = IMPORT_LAYER_PATTERN.search(import_str)
                    if not match:
                        continue
                    tgt_layer = int(match.group(1))
                    if tgt_layer <= src_layer:
                        continue
                    if not _is_inside_function_or_guarded(tree, line_no):
                        continue
                    fn = _get_enclosing_function(tree, line_no)
                    if fn is not None:
                        context = fn.name
                    elif _is_inside_try_module_scope(tree, line_no):
                        context = "__try_module_scope__"
                    else:
                        context = "__unknown__"
                    results.append(
                        LazyUpwardImport(
                            source_file=py_file,
                            source_layer=src_layer,
                            target_layer=tgt_layer,
                            import_statement=import_str,
                            line_number=line_no,
                            context=context,
                        )
                    )
    return results


def lazy_upward_import_metric(agentic_root: Path) -> dict:
    """Compute the LAZY_UPWARD_IMPORTS metric."""
    items = collect_lazy_upward_imports(agentic_root)
    by_pair: dict[tuple[int, int], int] = {}
    by_file: dict[str, int] = {}
    for item in items:
        pair = (item.source_layer, item.target_layer)
        by_pair[pair] = by_pair.get(pair, 0) + 1
        key = str(item.source_file)
        by_file[key] = by_file.get(key, 0) + 1
    return {"total": len(items), "by_pair": by_pair, "by_file": by_file, "items": items}


class LazySeamScanner:
    """Scanner for lazy loader seams using Phase 3B metric output."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.seams: list[dict[str, Any]] = []

    def scan_codebase(self) -> list[dict[str, Any]]:
        """Scan codebase using Phase 3B lazy upward import metric."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "LazySeamScanner.scan_codebase")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:LazySeamScanner.scan_codebase".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        agentic_core_path = self.root_path / AGENTIC_CORE_DIR
        metric = lazy_upward_import_metric(agentic_core_path)
        self.seams = []
        for item in metric["items"]:
            seam_entry = {
                "file_path": str(item.source_file.relative_to(self.root_path)),
                "function_name": item.context,
                "imported_modules": [item.import_statement] if item.import_statement else [],
                "imported_symbols": [],
                "reason_code": "TBD",
                "justification": "TBD",
            }
            self.seams.append(seam_entry)
        self.seams.sort(key=lambda x: (x["file_path"], x["function_name"], x["imported_modules"]))
        return self.seams

    def export_allowlist(self, output_path: Path) -> None:
        """Export allowlist to JSON file."""
        allowlist = {
            "description": "Lazy Seam Allowlist - Phase 4 Option A (Phase 3B universe)",
            "seams": self.seams,
        }
        _wg.write_json(output_path, allowlist, indent=2)
        print(f"Allowlist exported to: {output_path}")


def main():
    """Main entry point."""
    root_path = Path.cwd()
    scanner = LazySeamScanner(root_path)
    print("Scanning codebase for lazy seams (Phase 3B universe)...")
    seams = scanner.scan_codebase()
    print(f"Found {len(seams)} lazy seams")
    output_path = root_path / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_allowlist.json"
    scanner.export_allowlist(output_path)
    by_file = {}
    for seam in seams:
        file_path = seam["file_path"]
        by_file[file_path] = by_file.get(file_path, 0) + 1
    print("\nSummary by file:")
    for file_path, count in sorted(by_file.items()):
        print(f"  {file_path}: {count}")
    agentic_core_path = root_path / AGENTIC_CORE_DIR
    phase3b_metric = lazy_upward_import_metric(agentic_core_path)
    phase3b_total = phase3b_metric["total"]
    assert len(seams) == phase3b_total, (
        f"Phase 4 scanner total ({len(seams)}) != Phase 3B total ({phase3b_total}). Scanner must be aligned to Phase 3B universe."
    )
    print(f"\n✓ Phase 4 scanner matches Phase 3B total: {len(seams)} seams")


if __name__ == "__main__":
    main()
