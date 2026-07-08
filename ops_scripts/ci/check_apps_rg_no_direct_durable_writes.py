#!/usr/bin/env python3
"""Static guard proving apps_rg durable cache writes stay on Exit -> UWG -> L4."""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (
    REPO_ROOT / "apps_rg" / "runtime",
    REPO_ROOT / "apps_rg" / "cache",
)
CHROMA_WRITE_ALLOWLIST = {
    "apps_rg/cache/r1b_chroma_read_surface_projection.py",
    "apps_rg/cache/r1b_uwg_promotion.py",
    "apps_rg/runtime/bindings/c0_binding.py",
    "apps_rg/runtime/c0/c02_fact_vector_ingest.py",
    "apps_rg/runtime/c0/fact_vector_write_back.py",
    "apps_rg/runtime/c0/chroma_persistent_client.py",
    "apps_rg/runtime/chroma_precomputed_collection.py",
}
GOVERNED_NAMESPACE_WRITE_ALLOWLIST = {
    "apps_rg/cache/r1b_governed_receipt_emission.py",
    "apps_rg/cache/r1b_uwg_promotion.py",
    "apps_rg/cache/r1b_chroma_read_surface_projection.py",
}


def _iter_python_files(paths: tuple[Path, ...] | list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*.py") if p.is_file())
    return sorted(set(files))


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _scan_file(path: Path) -> list[str]:
    rel = _rel(path)
    source = path.read_text(encoding="utf-8")
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:
        return [f"{rel}: syntax error: {exc}"]

    chroma_allowed = rel in CHROMA_WRITE_ALLOWLIST
    namespace_allowed = rel in GOVERNED_NAMESPACE_WRITE_ALLOWLIST

    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if "APPS_RG_CACHE_WRITE_ENABLED" in stripped and not stripped.startswith("#"):
            errors.append(f"{rel}:{lineno} retired APPS_RG_CACHE_WRITE_ENABLED direct-write flag")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "chromadb" and not chroma_allowed:
                    errors.append(f"{rel}:{node.lineno} direct chromadb import outside governed L4/UWG path")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "chromadb" or module.startswith("chromadb."):
                if not chroma_allowed:
                    errors.append(f"{rel}:{node.lineno} direct chromadb import outside governed L4/UWG path")
        elif isinstance(node, ast.Call):
            call = _call_name(node.func)
            tail = call.rsplit(".", 1)[-1]
            if tail == "write_section_to_semantic_cache":
                errors.append(f"{rel}:{node.lineno} direct semantic cache write bypass")
            if tail in {"PersistentClient", "upsert"} and not chroma_allowed:
                errors.append(f"{rel}:{node.lineno} direct Chroma durable write primitive {call!r}")
            if tail == "write_text" and not namespace_allowed:
                rendered = ast.unparse(node) if hasattr(ast, "unparse") else ""
                if "l4_namespace_object_ref" in rendered or "target_l4_namespace" in rendered:
                    errors.append(f"{rel}:{node.lineno} L4 namespace ref write outside governed path")
        elif isinstance(node, ast.Name):
            if node.id == "write_section_to_semantic_cache":
                errors.append(f"{rel}:{getattr(node, 'lineno', 0)} direct semantic cache writer reference")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra-path", action="append", default=[])
    args = parser.parse_args(argv)

    roots = SCAN_ROOTS + tuple((REPO_ROOT / p).resolve() for p in args.extra_path)
    files = _iter_python_files(roots)
    errors: list[str] = []
    for path in files:
        errors.extend(_scan_file(path))

    print(f"[APPS-RG-DURABLE-WRITES] scanned {len(files)} file(s), {len(errors)} issue(s)")
    if errors:
        for error in errors:
            print(f"  ERROR  {error}")
        return 1
    print("[APPS-RG-DURABLE-WRITES] no direct durable cache write bypass found - gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
