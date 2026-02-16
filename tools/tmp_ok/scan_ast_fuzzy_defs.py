#!/usr/bin/env python3
"""
AST + Fuzzy/Similarity Discovery Scanner for SSOT Consolidation (Phase 1)

Scans SSOT-approved folders to inventory AST parsing and fuzzy/similarity logic.
Provides deterministic JSON output for clustering analysis.

Usage:
    python tools/tmp_ok/scan_ast_fuzzy_defs.py --roots agentic_core tools ops_scripts --out-json docs/reports/sub/ast_fuzzy_inventory.json
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

# Conservative keyword sets for detection
AST_KEYWORDS = {
    "parse", "ast", "node", "visitor", "walk", "dump", "unparse", "literal_eval",
    "getsource", "compile", "tokenize", "symtable", "inspect", "hash"
}

FUZZY_KEYWORDS = {
    "fuzzy", "similar", "distance", "match", "compare", "normalize", "similarity",
    "levenshtein", "jaro", "jaccard", "cosine", "approx", "sequence",
    "edit", "token", "ngram", "shingle"
}

# Known library imports to track
AST_LIBS = {
    "ast", "libcst", "parso", "tree_sitter", "typed_ast", "astroid", "inspect",
    "tokenize", "symtable"
}

FUZZY_LIBS = {
    "rapidfuzz", "fuzzywuzzy", "difflib", "Levenshtein", "jaro", "jellyfish"
}

class ScanResult:
    def __init__(self):
        self.files_scanned = 0
        self.files_with_errors = 0
        self.files_data: list[dict[str, Any]] = []

    def add_file(self, file_path: str, data: dict[str, Any]):
        self.files_data.append({"path": file_path, **data})
        self.files_scanned += 1

    def add_error(self, file_path: str, error: str):
        self.files_data.append({
            "path": file_path,
            "imports": {"ast": [], "fuzzy": []},
            "candidates": [],
            "parse_status": "failed",
            "parse_error": error
        })
        self.files_with_errors += 1

def extract_imports(tree: ast.AST) -> dict[str, list[str]]:
    """Extract relevant imports from AST."""
    ast_imports = []
    fuzzy_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if any(lib in name for lib in AST_LIBS):
                    ast_imports.append(name)
                if any(lib in name for lib in FUZZY_LIBS):
                    fuzzy_imports.append(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if any(lib in node.module for lib in AST_LIBS):
                    for alias in node.names:
                        fuzzy_imports.append(f"{node.module}.{alias.name}")
                if any(lib in node.module for lib in FUZZY_LIBS):
                    for alias in node.names:
                        fuzzy_imports.append(f"{node.module}.{alias.name}")

    return {
        "ast": sorted(set(ast_imports)),
        "fuzzy": sorted(set(fuzzy_imports))
    }

def extract_candidates(tree: ast.AST) -> list[dict[str, Any]]:
    """Extract function and class definitions with relevant keywords."""
    candidates = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name_lower = node.name.lower()
            keywords = [kw for kw in (AST_KEYWORDS | FUZZY_KEYWORDS) if kw in name_lower]
            if keywords:
                candidates.append({
                    "kind": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "keywords": sorted(keywords)
                })
        elif isinstance(node, ast.ClassDef):
            name_lower = node.name.lower()
            keywords = [kw for kw in (AST_KEYWORDS | FUZZY_KEYWORDS) if kw in name_lower]
            if keywords:
                candidates.append({
                    "kind": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "keywords": sorted(keywords)
                })

    return sorted(candidates, key=lambda x: (x["line"], x["name"]))

def extract_candidates_fallback(content: str) -> list[dict[str, Any]]:
    """Fallback: extract candidates using regex when AST parse fails."""
    candidates = []

    # Pattern for function definitions
    func_pattern = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE)
    for match in func_pattern.finditer(content):
        name = match.group(1)
        name_lower = name.lower()
        keywords = [kw for kw in (AST_KEYWORDS | FUZZY_KEYWORDS) if kw in name_lower]
        if keywords:
            line_num = content[:match.start()].count('\n') + 1
            candidates.append({
                "kind": "fallback_function",
                "name": name,
                "line": line_num,
                "keywords": sorted(keywords)
            })

    # Pattern for class definitions
    class_pattern = re.compile(r"^\s*class\s+(\w+)\s*[\(:]", re.MULTILINE)
    for match in class_pattern.finditer(content):
        name = match.group(1)
        name_lower = name.lower()
        keywords = [kw for kw in (AST_KEYWORDS | FUZZY_KEYWORDS) if kw in name_lower]
        if keywords:
            line_num = content[:match.start()].count('\n') + 1
            candidates.append({
                "kind": "fallback_class",
                "name": name,
                "line": line_num,
                "keywords": sorted(keywords)
            })

    return sorted(candidates, key=lambda x: (x["line"], x["name"]))

def scan_file(file_path: Path) -> dict[str, Any]:
    """Scan a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=str(file_path))

        imports = extract_imports(tree)
        candidates = extract_candidates(tree)

        # Only include if has relevant imports or candidates
        if imports["ast"] or imports["fuzzy"] or candidates:
            return {
                "imports": imports,
                "candidates": candidates,
                "parse_status": "ok"
            }
        else:
            return None

    except SyntaxError as e:
        # Fallback to regex extraction
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            candidates = extract_candidates_fallback(content)
            if candidates:
                return {
                    "imports": {"ast": [], "fuzzy": []},
                    "candidates": candidates,
                    "parse_status": "failed",
                    "parse_error": f"SyntaxError at line {e.lineno}"
                }
        except Exception:
            pass
        return None
    except Exception as e:
        # Fallback to regex extraction
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            candidates = extract_candidates_fallback(content)
            if candidates:
                return {
                    "imports": {"ast": [], "fuzzy": []},
                    "candidates": candidates,
                    "parse_status": "failed",
                    "parse_error": str(e)[:100]
                }
        except Exception:
            pass
        return None

def should_exclude(file_path: Path, excluded_patterns: list[str]) -> bool:
    """Check if file should be excluded."""
    path_str = str(file_path).replace("\\", "/")
    for pattern in excluded_patterns:
        if pattern in path_str:
            return True
    return False

def scan_roots(roots: list[str], excluded_patterns: list[str]) -> ScanResult:
    """Scan all Python files in given root directories."""
    result = ScanResult()

    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            print(f"Warning: Root {root} does not exist, skipping", file=sys.stderr)
            continue

        for py_file in sorted(root_path.rglob("*.py")):
            # Skip excluded patterns
            if should_exclude(py_file, excluded_patterns):
                continue

            rel_path = str(py_file).replace("\\", "/")
            file_data = scan_file(py_file)

            if file_data is not None:
                result.add_file(rel_path, file_data)

    return result

def main():
    parser = argparse.ArgumentParser(
        description="Scan for AST and fuzzy/similarity definitions in SSOT-approved folders"
    )
    parser.add_argument("--roots", nargs="+", required=True,
                       help="Root directories to scan (e.g., agentic_core tools ops_scripts)")
    parser.add_argument("--out-json", required=True,
                       help="Output JSON file path")

    args = parser.parse_args()

    # Define exclusions
    excluded_patterns = ["tests", "apps_lic", "apps_rg", "apps_shared", "archives", ".backup", "__pycache__"]

    print(f"Scanning roots: {args.roots}", file=sys.stderr)
    print(f"Excluded patterns: {excluded_patterns}", file=sys.stderr)
    result = scan_roots(args.roots, excluded_patterns)

    # Generate deterministic output
    json_output = {
        "scanned_roots": sorted(args.roots),
        "excluded_roots": ["tests", "apps_lic", "apps_rg", "apps_shared", "archives", ".backup"],
        "files": sorted(result.files_data, key=lambda x: x["path"])
    }

    # Write JSON
    json_path = Path(args.out_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_output, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Results written to: {json_path}", file=sys.stderr)
    print(f"Files scanned: {result.files_scanned}, Files with relevant content: {len(result.files_data)}", file=sys.stderr)

if __name__ == "__main__":
    main()
