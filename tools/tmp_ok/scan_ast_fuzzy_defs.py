#!/usr/bin/env python3
"""
Deterministic AST + Fuzzy library inventory scanner.

Scans SSOT-approved folders for:
- Import usage of AST libs (ast, libcst, parso, tree_sitter, typed_ast, astroid, inspect, tokenize, symtable, compile)
- Import usage of fuzzy libs (difflib, rapidfuzz, fuzzywuzzy, Levenshtein, jaro, jellyfish)
- Candidate definitions (functions/classes) with keywords: parse, ast, dump, hash, normalize, token, similarity, fuzzy, match, compare

Output: deterministic JSON with stable ordering, UTF-8 with error handling.
"""

import ast
import json
from pathlib import Path
from typing import Any

AST_LIBS = {
    "ast",
    "libcst",
    "parso",
    "tree_sitter",
    "typed_ast",
    "astroid",
    "inspect",
    "tokenize",
    "symtable",
    "compile",
}

FUZZY_LIBS = {"difflib", "rapidfuzz", "fuzzywuzzy", "Levenshtein", "jaro", "jellyfish"}

CANDIDATE_KEYWORDS = {
    "parse",
    "ast",
    "dump",
    "hash",
    "normalize",
    "token",
    "similarity",
    "fuzzy",
    "match",
    "compare",
}

SCANNED_ROOTS = [
    "agentic_core",
    "tools",
    "ops_scripts",
]

EXCLUDED_ROOTS = {
    "tests",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "archives",
    ".backup",
}


def should_scan_path(path: Path, repo_root: Path) -> bool:
    """Check if path should be scanned."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return False

    parts = rel.parts
    if not parts:
        return False

    # Must start with a scanned root
    if parts[0] not in SCANNED_ROOTS:
        return False

    # Must not contain excluded roots in path
    for excluded in EXCLUDED_ROOTS:
        if excluded in parts:
            return False

    return True


def extract_imports(tree: ast.AST) -> tuple[list[str], list[str]]:
    """Extract AST and fuzzy library imports from AST."""
    ast_imports = []
    fuzzy_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if name in AST_LIBS:
                    ast_imports.append(name)
                elif name in FUZZY_LIBS:
                    fuzzy_imports.append(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split(".")[0]
                if name in AST_LIBS:
                    ast_imports.append(name)
                elif name in FUZZY_LIBS:
                    fuzzy_imports.append(name)

    return sorted(set(ast_imports)), sorted(set(fuzzy_imports))


def extract_candidates(tree: ast.AST, source: str) -> list[dict[str, Any]]:
    """Extract candidate definitions (functions/classes) with relevant keywords."""
    candidates = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            name = node.name
            line = node.lineno

            # Check if name or docstring contains keywords
            keywords_found = []
            name_lower = name.lower()
            for kw in CANDIDATE_KEYWORDS:
                if kw in name_lower:
                    keywords_found.append(kw)

            # Check docstring
            docstring = ast.get_docstring(node)
            if docstring:
                docstring_lower = docstring.lower()
                for kw in CANDIDATE_KEYWORDS:
                    if kw in docstring_lower and kw not in keywords_found:
                        keywords_found.append(kw)

            if keywords_found:
                candidates.append(
                    {"kind": kind, "name": name, "line": line, "keywords": sorted(set(keywords_found))}
                )

    return sorted(candidates, key=lambda x: x["line"])


def scan_file(file_path: Path) -> dict[str, Any]:
    """Scan a single Python file."""
    result = {
        "path": str(file_path.relative_to(Path.cwd())).replace("\\", "/"),
        "imports": {"ast": [], "fuzzy": []},
        "candidates": [],
        "parse_status": "ok",
        "parse_error": None,
    }

    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)

        ast_imports, fuzzy_imports = extract_imports(tree)
        result["imports"]["ast"] = ast_imports
        result["imports"]["fuzzy"] = fuzzy_imports

        candidates = extract_candidates(tree, source)
        result["candidates"] = candidates

    except SyntaxError as e:
        result["parse_status"] = "failed"
        result["parse_error"] = f"SyntaxError at line {e.lineno}: {e.msg}"
    except (UnicodeDecodeError, OSError) as e:
        result["parse_status"] = "failed"
        result["parse_error"] = f"{type(e).__name__}: {str(e)}"

    return result


def scan_directory(repo_root: Path) -> list[dict[str, Any]]:
    """Scan all Python files in approved directories."""
    results = []

    for root_dir in SCANNED_ROOTS:
        root_path = repo_root / root_dir
        if not root_path.exists():
            continue

        for py_file in sorted(root_path.rglob("*.py")):
            if should_scan_path(py_file, repo_root):
                result = scan_file(py_file)
                results.append(result)

    return sorted(results, key=lambda x: x["path"])


def main():
    """Main entry point."""
    repo_root = Path.cwd()

    print(f"Scanning from: {repo_root}")
    print(f"Scanned roots: {SCANNED_ROOTS}")
    print(f"Excluded roots: {sorted(EXCLUDED_ROOTS)}")
    print()

    results = scan_directory(repo_root)

    # Build output structure
    output = {
        "scanned_roots": sorted(SCANNED_ROOTS),
        "excluded_roots": sorted(EXCLUDED_ROOTS),
        "files": results,
    }

    # Statistics
    file_count = len(results)
    with_ast = sum(1 for r in results if r["imports"]["ast"])
    with_fuzzy = sum(1 for r in results if r["imports"]["fuzzy"])
    with_candidates = sum(1 for r in results if r["candidates"])
    parse_failures = sum(1 for r in results if r["parse_status"] == "failed")

    print(f"Files scanned: {file_count}")
    print(f"Files with AST imports: {with_ast}")
    print(f"Files with fuzzy imports: {with_fuzzy}")
    print(f"Files with candidates: {with_candidates}")
    print(f"Parse failures: {parse_failures}")
    print()

    # Write JSON output
    output_path = repo_root / "docs" / "reports" / "sub" / "ast_fuzzy_inventory.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Output written to: {output_path}")
    print(f"SHA256: {_file_sha256(output_path)}")


def _file_sha256(path: Path) -> str:
    """Compute SHA256 of file."""
    import hashlib

    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


if __name__ == "__main__":
    main()
