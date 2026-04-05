#!/usr/bin/env python3
"""
Phase 1: Full Test Surface Inventory
Scans the entire tests/ directory for skip patterns, import-only tests,
silent dependency swallowers, hollowed tests, and all other violations
per the Constitutional Testing Directive.
"""

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Known third-party packages (not first-party)
THIRD_PARTY = frozenset({
    "redis", "pinecone", "torch", "tensorflow", "transformers", "langchain",
    "openai", "anthropic", "cohere", "chromadb", "weaviate", "qdrant",
    "faiss", "numpy", "pandas", "scipy", "sklearn", "matplotlib",
    "fastapi", "uvicorn", "flask", "django", "celery", "dramatiq",
    "boto3", "botocore", "google", "azure", "docker", "kubernetes",
    "psycopg2", "pymongo", "sqlalchemy", "alembic", "pydantic",
    "httpx", "aiohttp", "requests", "grpc", "protobuf",
    "PIL", "cv2", "spacy", "nltk", "sentence_transformers",
    "litellm", "tiktoken", "tokenizers", "huggingface_hub",
    "voyageai", "fireworks", "groq", "mistralai",
    "playwright", "selenium", "bs4", "scrapy",
    "ray", "dask", "spark", "pyspark",
    "neo4j", "networkx", "igraph",
})

FIRST_PARTY_ROOTS = frozenset({
    "agentic_core", "tools", "scripts", "config",
})


def is_first_party(module_name: str) -> bool:
    """Determine if a module is first-party (repo-owned)."""
    if not module_name:
        return False
    root = module_name.split(".")[0]
    if root in FIRST_PARTY_ROOTS:
        return True
    if root in THIRD_PARTY:
        return False
    # Check if it exists in the repo
    candidate = Path(root)
    if candidate.exists() and candidate.is_dir():
        return True
    if Path(f"{root}.py").exists():
        return True
    return False


def classify_dependency(module_name: str) -> str:
    if not module_name:
        return "unknown"
    return "first-party" if is_first_party(module_name) else "third-party"


class TestSurfaceVisitor(ast.NodeVisitor):
    """AST visitor that detects all skip patterns, import-only tests, etc."""

    def __init__(self, filepath: str, source: str):
        self.filepath = filepath
        self.source = source
        self.findings: list[dict[str, Any]] = []
        self.test_functions: list[ast.FunctionDef] = []
        self.current_class = None

    def _add_finding(self, node, **kwargs):
        self.findings.append({
            "file": self.filepath,
            "line": getattr(node, "lineno", 0),
            **kwargs,
        })

    def visit_Import(self, node):
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            self.test_functions.append(node)
            self._analyze_test_function(node)
        elif node.name.startswith("_") or node.name in ("setup", "teardown", "setup_method", "teardown_method"):
            self._analyze_fixture_or_helper(node)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _analyze_test_function(self, node):
        test_name = node.name
        if self.current_class:
            test_name = f"{self.current_class}::{node.name}"

        # Check decorators for skip/skipif/xfail
        for deco in node.decorator_list:
            self._check_decorator(node, deco, test_name)

        # Check body for skip calls, assertions, imports
        has_assert = False
        has_skip_call = False
        has_pass_only = False
        has_import_only = False
        has_real_call = False
        body_nodes = list(ast.walk(node))

        for child in body_nodes:
            if isinstance(child, ast.Assert):
                has_assert = True
            if isinstance(child, ast.Call):
                func_name = self._get_call_name(child)
                if func_name in ("pytest.skip", "skip"):
                    has_skip_call = True
                    reason = self._extract_reason(child)
                    self._add_finding(child,
                        test_name=test_name,
                        pattern_type="pytest.skip_call",
                        reason=reason,
                        dependency=self._extract_dependency_from_reason(reason),
                    )
                elif func_name in ("pytest.importorskip", "importorskip"):
                    module = self._extract_first_arg_str(child)
                    self._add_finding(child,
                        test_name=test_name,
                        pattern_type="pytest.importorskip",
                        dependency=module,
                        classification=classify_dependency(module),
                    )
                elif func_name and not func_name.startswith(("assert", "isinstance", "len", "dir", "getattr", "hasattr", "type", "str", "int", "print")):
                    has_real_call = True

        # Check for pass-only body
        body_stmts = [s for s in node.body if not isinstance(s, (ast.Expr,)) or not isinstance(s.value, (ast.Constant,))]
        if len(body_stmts) == 1 and isinstance(body_stmts[0], ast.Pass):
            has_pass_only = True

        # Detect import-only / hollow test
        if not has_assert and not has_skip_call and has_pass_only:
            self._add_finding(node,
                test_name=test_name,
                pattern_type="import_only_test",
                current_behavior="import-only",
                severity="invalid" if "adg" in self.filepath.lower() or "core" in self.filepath.lower() else "questionable",
            )
        elif has_assert and not has_real_call:
            # Has assertions but no real function calls — check if it's just checking module attributes
            assertion_sources = []
            for child in body_nodes:
                if isinstance(child, ast.Assert):
                    assertion_sources.append(ast.dump(child.test))
            all_module_checks = all(
                ".__name__" in s or "dir(" in s or "hasattr" in s or "isinstance" in s or "len(" in s
                for s in assertion_sources
            )
            if all_module_checks and len(assertion_sources) <= 3:
                self._add_finding(node,
                    test_name=test_name,
                    pattern_type="shallow_assertion_only",
                    current_behavior="shallow-assertion",
                    severity="questionable",
                )

    def _check_decorator(self, node, deco, test_name):
        if isinstance(deco, ast.Attribute):
            attr = deco.attr
            if attr == "skip":
                self._add_finding(node,
                    test_name=test_name,
                    pattern_type="@pytest.mark.skip",
                )
            elif attr == "skipif":
                self._add_finding(node,
                    test_name=test_name,
                    pattern_type="@pytest.mark.skipif",
                )
            elif attr == "xfail":
                self._add_finding(node,
                    test_name=test_name,
                    pattern_type="@pytest.mark.xfail",
                )
        elif isinstance(deco, ast.Call):
            func = deco.func
            if isinstance(func, ast.Attribute):
                attr = func.attr
                if attr == "skip":
                    reason = self._extract_keyword(deco, "reason") or self._extract_first_arg_str(deco)
                    self._add_finding(node,
                        test_name=test_name,
                        pattern_type="@pytest.mark.skip",
                        reason=reason,
                    )
                elif attr == "skipif":
                    reason = self._extract_keyword(deco, "reason") or ""
                    condition = ast.dump(deco.args[0]) if deco.args else ""
                    self._add_finding(node,
                        test_name=test_name,
                        pattern_type="@pytest.mark.skipif",
                        reason=reason,
                        condition=condition,
                    )
                elif attr == "xfail":
                    reason = self._extract_keyword(deco, "reason") or ""
                    strict = self._extract_keyword(deco, "strict")
                    self._add_finding(node,
                        test_name=test_name,
                        pattern_type="@pytest.mark.xfail",
                        reason=reason,
                        strict=str(strict),
                    )

    def _analyze_fixture_or_helper(self, node):
        """Check fixtures and helpers for silent dependency swallowers."""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                for handler in child.handlers:
                    if handler.type:
                        handler_name = self._get_exception_name(handler.type)
                        if handler_name in ("ImportError", "ModuleNotFoundError"):
                            self._add_finding(child,
                                test_name=node.name,
                                pattern_type="try_except_import_error_in_fixture",
                                severity="invalid" if self._handler_swallows(handler) else "questionable",
                            )

    def _handler_swallows(self, handler):
        """Check if an exception handler silently swallows the error."""
        body = handler.body
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Assign):
                return True  # e.g. _mod = None
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                return True
        return False

    def _get_call_name(self, node):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return None

    def _get_exception_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Tuple):
            return ", ".join(self._get_exception_name(e) for e in node.elts)
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _extract_first_arg_str(self, node):
        if node.args and isinstance(node.args[0], ast.Constant):
            return str(node.args[0].value)
        return ""

    def _extract_keyword(self, node, name):
        for kw in node.keywords:
            if kw.arg == name:
                if isinstance(kw.value, ast.Constant):
                    return str(kw.value.value)
                return ast.dump(kw.value)
        return ""

    def _extract_reason(self, node):
        if node.args and isinstance(node.args[0], ast.Constant):
            return str(node.args[0].value)
        return self._extract_keyword(node, "reason")

    def _extract_dependency_from_reason(self, reason):
        if not reason:
            return ""
        # Try to extract module name from reason text
        for pattern in [r"(\w+(?:\.\w+)+)", r"(\w+)"]:
            match = re.search(pattern, reason)
            if match:
                return match.group(1)
        return ""


def scan_file_for_try_except_patterns(filepath: str, source: str) -> list[dict]:
    """Scan for try/except ImportError patterns at module level."""
    findings = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type:
                    exc_name = ""
                    if isinstance(handler.type, ast.Name):
                        exc_name = handler.type.id
                    elif isinstance(handler.type, ast.Tuple):
                        exc_name = ", ".join(
                            getattr(e, "id", getattr(e, "attr", "")) for e in handler.type.elts
                        )

                    if any(x in exc_name for x in ("ImportError", "ModuleNotFoundError", "ValueError", "TypeError", "RuntimeError")):
                        # Check what's being imported in the try block
                        imported_modules = []
                        for stmt in node.body:
                            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                                if isinstance(stmt, ast.ImportFrom) and stmt.module:
                                    imported_modules.append(stmt.module)
                                elif isinstance(stmt, ast.Import):
                                    for alias in stmt.names:
                                        imported_modules.append(alias.name)

                        for mod in imported_modules:
                            findings.append({
                                "file": filepath,
                                "line": node.lineno,
                                "pattern_type": "try_except_import_swallower",
                                "exception_type": exc_name,
                                "dependency": mod,
                                "classification": classify_dependency(mod),
                                "severity": "invalid" if is_first_party(mod) else "valid-but-avoidable",
                            })

    return findings


def scan_conftest_patterns(filepath: str, source: str) -> list[dict]:
    """Scan conftest.py for patterns that optionalize first-party code."""
    findings = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type:
                    exc_name = ""
                    if isinstance(handler.type, ast.Name):
                        exc_name = handler.type.id
                    elif isinstance(handler.type, ast.Tuple):
                        exc_name = ", ".join(
                            getattr(e, "id", getattr(e, "attr", "")) for e in handler.type.elts
                        )

                    if "ImportError" in exc_name or "ModuleNotFoundError" in exc_name:
                        imported_modules = []
                        for stmt in node.body:
                            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                                if isinstance(stmt, ast.ImportFrom) and stmt.module:
                                    imported_modules.append(stmt.module)
                                elif isinstance(stmt, ast.Import):
                                    for alias in stmt.names:
                                        imported_modules.append(alias.name)

                        for mod in imported_modules:
                            findings.append({
                                "file": filepath,
                                "line": node.lineno,
                                "pattern_type": "conftest_optionalizes_first_party" if is_first_party(mod) else "conftest_optionalizes_third_party",
                                "dependency": mod,
                                "classification": classify_dependency(mod),
                                "severity": "invalid" if is_first_party(mod) else "valid-required",
                            })
    return findings


def count_meaningful_assertions(func_node: ast.FunctionDef) -> int:
    """Count assertions that go beyond module-level checks."""
    count = 0
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            # Check if it's a meaningful assertion vs shallow module check
            test_dump = ast.dump(node.test)
            if "__name__" not in test_dump and "dir(" not in test_dump:
                count += 1
    return count


def main():
    tests_dir = Path("tests")
    all_findings = []
    file_count = 0
    test_count = 0
    error_files = []

    print("Scanning test surface...", file=sys.stderr)

    # Scan all test files
    for p in sorted(tests_dir.rglob("*.py")):
        filepath = str(p).replace("\\", "/")
        try:
            source = p.read_text(encoding="utf-8")
        except Exception as e:
            error_files.append((filepath, str(e)))
            continue

        file_count += 1

        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            error_files.append((filepath, f"SyntaxError: {e}"))
            continue

        # Run AST visitor
        visitor = TestSurfaceVisitor(filepath, source)
        visitor.visit(tree)
        test_count += len(visitor.test_functions)
        all_findings.extend(visitor.findings)

        # Scan for try/except patterns at module level
        all_findings.extend(scan_file_for_try_except_patterns(filepath, source))

        # Scan conftest files specially
        if p.name == "conftest.py":
            all_findings.extend(scan_conftest_patterns(filepath, source))

    # Classify findings
    summary = {
        "total_files_scanned": file_count,
        "total_test_functions": test_count,
        "total_findings": len(all_findings),
        "error_files": len(error_files),
        "by_pattern_type": Counter(),
        "by_severity": Counter(),
        "by_classification": Counter(),
        "by_file_top20": Counter(),
    }

    for f in all_findings:
        pt = f.get("pattern_type", "unknown")
        summary["by_pattern_type"][pt] += 1
        sev = f.get("severity", "unclassified")
        summary["by_severity"][sev] += 1
        cls = f.get("classification", "unknown")
        summary["by_classification"][cls] += 1
        summary["by_file_top20"][f["file"]] += 1

    # Sort top files
    top_files = summary["by_file_top20"].most_common(20)

    # Output structured report
    report = {
        "meta": {
            "total_files_scanned": file_count,
            "total_test_functions": test_count,
            "total_findings": len(all_findings),
            "error_files_count": len(error_files),
        },
        "counts": {
            "by_pattern_type": dict(summary["by_pattern_type"].most_common()),
            "by_severity": dict(summary["by_severity"].most_common()),
            "by_classification": dict(summary["by_classification"].most_common()),
        },
        "top_20_files_by_finding_density": [
            {"file": f, "count": c} for f, c in top_files
        ],
        "findings": all_findings,
        "error_files": [{"file": f, "error": e} for f, e in error_files],
    }

    # Write JSON report
    output_path = Path("artifacts/test_surface_inventory.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary to stdout
    print("=== TEST SURFACE INVENTORY ===")
    print(f"Files scanned: {file_count}")
    print(f"Test functions found: {test_count}")
    print(f"Total findings: {len(all_findings)}")
    print(f"Error files: {len(error_files)}")
    print()
    print("BY PATTERN TYPE:")
    for pt, count in summary["by_pattern_type"].most_common():
        print(f"  {pt}: {count}")
    print()
    print("BY SEVERITY:")
    for sev, count in summary["by_severity"].most_common():
        print(f"  {sev}: {count}")
    print()
    print("BY CLASSIFICATION:")
    for cls, count in summary["by_classification"].most_common():
        print(f"  {cls}: {count}")
    print()
    print("TOP 20 FILES BY FINDING DENSITY:")
    for f, c in top_files:
        print(f"  {c:3d}  {f}")
    print()
    print(f"Full report written to: {output_path}")


if __name__ == "__main__":
    main()
