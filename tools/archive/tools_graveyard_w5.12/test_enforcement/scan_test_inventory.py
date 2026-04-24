"""Phase 1: Scan all test files for skip patterns and produce test_inventory.json.

Scans for:
- pytest.skip(...)
- pytest.importorskip(...)
- try/except ImportError -> skip
- conditional imports with skip
- skipif decorators tied to import availability
- bare try/except ImportError blocks
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FIRST_PARTY_PREFIXES = (
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "apps_exec",
    "apps_rfp",
    "apps_research",
    "apps_eval",
    "system_learning",
    "infrastructure",
    "tools",
    "ops_scripts",
    "data",
)


def _is_first_party(module_name: str) -> bool:
    if not module_name:
        return False
    top = module_name.split(".")[0]
    return top in FIRST_PARTY_PREFIXES


def _classify_party(module_name: str) -> str:
    if not module_name:
        return "unknown"
    return "first_party" if _is_first_party(module_name) else "third_party"


class SkipPatternVisitor(ast.NodeVisitor):
    """AST visitor that finds all skip-related patterns in a test file."""

    def __init__(self, source_lines: list[str], file_path: str):
        self.source_lines = source_lines
        self.file_path = file_path
        self.findings: list[dict[str, Any]] = []
        self._in_test_func: str | None = None
        self._in_class: str | None = None

    def _current_test_name(self) -> str:
        parts = []
        if self._in_class:
            parts.append(self._in_class)
        if self._in_test_func:
            parts.append(self._in_test_func)
        return "::".join(parts) if parts else "<module-level>"

    def _add_finding(
        self, line: int, pattern: str, dependency: str, behavior: str, extra: dict | None = None
    ):
        entry = {
            "file_path": self.file_path,
            "test_name": self._current_test_name(),
            "line": line,
            "skip_pattern": pattern,
            "dependency": dependency,
            "first_party_or_third_party": _classify_party(dependency),
            "current_behavior": behavior,
        }
        if extra:
            entry.update(extra)
        self.findings.append(entry)

    def visit_ClassDef(self, node: ast.ClassDef):
        old = self._in_class
        self._in_class = node.name
        self.generic_visit(node)
        self._in_class = old

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old = self._in_test_func
        if node.name.startswith("test_"):
            self._in_test_func = node.name
        # Check decorators for skipif / skip patterns
        self._check_decorators(node)
        self.generic_visit(node)
        self._in_test_func = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check_decorators(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        for dec in node.decorator_list:
            self._check_skipif_decorator(dec, node)
            self._check_skip_decorator(dec, node)
            self._check_mark_skip(dec, node)

    def _check_skipif_decorator(self, dec: ast.expr, node: ast.AST):
        """Detect @pytest.mark.skipif(...) patterns."""
        if not isinstance(dec, ast.Call):
            return
        func = dec.func
        # pytest.mark.skipif(...)
        if isinstance(func, ast.Attribute) and func.attr == "skipif":
            source_line = ""
            if dec.lineno and dec.lineno <= len(self.source_lines):
                # Grab a few lines for context
                start = dec.lineno - 1
                end = min(dec.end_lineno or dec.lineno, len(self.source_lines))
                source_line = " ".join(
                    self.source_lines[start:end],
                ).strip()

            dep = self._extract_dependency_from_skipif(dec, source_line)
            if dep or "import" in source_line.lower():
                self._add_finding(
                    dec.lineno,
                    "skipif_import",
                    dep or "<unknown>",
                    f"skip if import unavailable: {source_line[:200]}",
                )

    def _check_skip_decorator(self, dec: ast.expr, node: ast.AST):
        """Detect @pytest.mark.skip(reason=...) patterns."""
        if isinstance(dec, ast.Call):
            func = dec.func
            if isinstance(func, ast.Attribute) and func.attr == "skip":
                reason = ""
                for kw in dec.keywords:
                    if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                        reason = str(kw.value.value)
                self._add_finding(
                    dec.lineno,
                    "skip_decorator",
                    "",
                    f"unconditional skip: {reason[:200]}",
                )

    def _check_mark_skip(self, dec: ast.expr, node: ast.AST):
        """Detect bare @pytest.mark.skip (no call)."""
        if isinstance(dec, ast.Attribute) and dec.attr == "skip":
            self._add_finding(
                dec.lineno,
                "skip_decorator_bare",
                "",
                "unconditional skip (bare marker)",
            )

    def _extract_dependency_from_skipif(self, call: ast.Call, source_line: str) -> str:
        """Try to extract the dependency name from a skipif condition."""
        # Look for patterns like: not HAS_X, importlib.util.find_spec("x") is None
        for arg in call.args:
            dep = self._dep_from_expr(arg)
            if dep:
                return dep
        # Fallback: regex on source
        m = re.search(r'find_spec\(["\']([^"\']+)', source_line)
        if m:
            return m.group(1)
        m = re.search(r"import\s+(\w[\w.]*)", source_line)
        if m:
            return m.group(1)
        return ""

    def _dep_from_expr(self, node: ast.expr) -> str:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self._dep_from_expr(node.operand)
        if isinstance(node, ast.Name):
            name = node.id
            if name.startswith("HAS_") or name.startswith("has_"):
                return name
        if isinstance(node, ast.Compare):
            return self._dep_from_expr(node.left)
        if isinstance(node, ast.Call):
            # importlib.util.find_spec(...)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "find_spec":
                if node.args and isinstance(node.args[0], ast.Constant):
                    return str(node.args[0].value)
        return ""

    def visit_Call(self, node: ast.Call):
        """Detect pytest.skip(...) and pytest.importorskip(...) calls."""
        func = node.func
        func_name = self._get_call_name(func)

        if func_name in ("pytest.skip", "skip"):
            reason = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                reason = str(node.args[0].value)
            for kw in node.keywords:
                if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                    reason = str(kw.value.value)
            dep = ""
            if "import" in reason.lower():
                m = re.search(r"(\w[\w.]*)", reason)
                dep = m.group(1) if m else ""
            self._add_finding(
                node.lineno,
                "pytest_skip_call",
                dep,
                f"pytest.skip({reason[:200]})",
            )

        elif func_name in ("pytest.importorskip", "importorskip"):
            dep = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                dep = str(node.args[0].value)
            self._add_finding(
                node.lineno,
                "importorskip",
                dep,
                f"pytest.importorskip({dep})",
            )

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        """Detect try/except ImportError patterns."""
        for handler in node.handlers:
            if self._is_import_error_handler(handler):
                self._analyze_import_error_block(node, handler)
        self.generic_visit(node)

    # Python 3.11+ TryStar not used here but handle gracefully
    def visit_TryStar(self, node: ast.AST):
        self.generic_visit(node)

    def _is_import_error_handler(self, handler: ast.ExceptHandler) -> bool:
        if handler.type is None:
            return False
        if isinstance(handler.type, ast.Name):
            return handler.type.id in ("ImportError", "ModuleNotFoundError")
        if isinstance(handler.type, ast.Tuple):
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("ImportError", "ModuleNotFoundError"):
                    return True
        return False

    def _analyze_import_error_block(self, try_node: ast.Try, handler: ast.ExceptHandler):
        # Extract what's being imported in the try block
        deps = []
        for stmt in try_node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    deps.append(alias.name)
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module:
                    deps.append(stmt.module)

        dep_str = ", ".join(deps) if deps else "<unknown>"

        # Classify what the except block does
        handler_actions = []
        has_skip = False
        has_flag = False
        has_pass = False
        has_stub = False

        for stmt in handler.body:
            if isinstance(stmt, ast.Pass):
                has_pass = True
                handler_actions.append("pass")
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                name = self._get_call_name(stmt.value.func)
                if "skip" in name.lower():
                    has_skip = True
                    handler_actions.append(f"call:{name}")
                else:
                    handler_actions.append(f"call:{name}")
            elif isinstance(stmt, ast.Assign):
                # HAS_X = False pattern
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        if target.id.startswith("HAS_") or target.id.startswith("has_"):
                            has_flag = True
                            handler_actions.append(f"flag:{target.id}=False")
                        elif isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                            has_stub = True
                            handler_actions.append(f"stub:{target.id}=None")
                        else:
                            handler_actions.append(f"assign:{target.id}")
            elif isinstance(stmt, ast.Raise):
                handler_actions.append("raise")
            else:
                handler_actions.append(type(stmt).__name__)

        behavior = (
            "skip"
            if has_skip
            else "flag"
            if has_flag
            else "stub"
            if has_stub
            else "pass"
            if has_pass
            else "other"
        )
        action_desc = "; ".join(handler_actions) if handler_actions else "empty"

        self._add_finding(
            try_node.lineno,
            "try_except_importerror",
            dep_str,
            f"try/except ImportError -> {behavior} ({action_desc})",
            {"handler_behavior": behavior, "handler_actions": handler_actions},
        )

    def _get_call_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = self._get_call_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""


def scan_file(filepath: pathlib.Path, rel_path: str) -> list[dict]:
    """Scan a single test file and return findings."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return [{"file_path": rel_path, "error": "could not read file"}]

    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError:
        return [{"file_path": rel_path, "error": "syntax error"}]

    lines = source.splitlines()
    visitor = SkipPatternVisitor(lines, rel_path)
    visitor.visit(tree)
    return visitor.findings


def scan_all_tests(root: pathlib.Path) -> list[dict]:
    """Scan all test files under root."""
    all_findings = []
    test_dirs = [root / "tests"]
    # Also check root-level test files
    root_tests = list(root.glob("test_*.py"))

    test_files = []
    for td in test_dirs:
        if td.exists():
            test_files.extend(td.rglob("test_*.py"))
            test_files.extend(td.rglob("*_test.py"))
    test_files.extend(root_tests)

    # Also scan conftest.py files (they can contain skip logic)
    for td in test_dirs:
        if td.exists():
            test_files.extend(td.rglob("conftest.py"))
    root_conftest = root / "conftest.py"
    if root_conftest.exists():
        test_files.append(root_conftest)

    # Deduplicate
    test_files = sorted(set(test_files))

    print(f"Scanning {len(test_files)} test files...", file=sys.stderr)

    for i, fp in enumerate(test_files):
        if i % 500 == 0 and i > 0:
            print(f"  ...{i}/{len(test_files)}", file=sys.stderr)
        try:
            rel = str(fp.relative_to(root)).replace("\\", "/")
        except ValueError:
            rel = str(fp)
        findings = scan_file(fp, rel)
        all_findings.extend(findings)

    return all_findings


def infer_category(finding: dict) -> str:
    """Infer the test category from the finding context."""
    fp = finding.get("file_path", "")
    dep = finding.get("dependency", "")
    party = finding.get("first_party_or_third_party", "")
    pattern = finding.get("skip_pattern", "")

    # Platform indicators
    platform_deps = {"torch", "cuda", "gpu", "tensorflow", "jax"}
    if dep.lower() in platform_deps or "gpu" in fp.lower():
        return "platform"

    # External service indicators
    external_deps = {"redis", "pinecone", "openai", "anthropic", "google"}
    if dep.split(".")[0].lower() in external_deps:
        return "external"

    # Optional third-party
    optional_third = {
        "playwright",
        "dash",
        "plotly",
        "fastapi",
        "uvicorn",
        "sentence_transformers",
        "chromadb",
        "duckdb",
        "numpy",
        "pandas",
        "scikit-learn",
        "sklearn",
        "beautifulsoup4",
        "bs4",
        "rich",
        "opentelemetry",
    }
    if dep.split(".")[0].lower() in optional_third:
        return "optional"

    # First-party that's being skipped = violation candidate
    if party == "first_party":
        return "core"

    # Integration tests
    if "integration" in fp:
        return "optional"

    # Default for tests with unknown deps
    if pattern == "try_except_importerror" and party == "unknown":
        return "core"

    return "core"


def enrich_findings(findings: list[dict]) -> list[dict]:
    """Add inferred_category to each finding."""
    for f in findings:
        if "error" not in f:
            f["inferred_category"] = infer_category(f)
    return findings


def main():
    findings = scan_all_tests(ROOT)
    findings = enrich_findings(findings)

    out_dir = ROOT / "artifacts" / "test_enforcement"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test_inventory.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, default=str)

    # Summary stats
    patterns = {}
    parties = {}
    categories = {}
    for finding in findings:
        if "error" in finding:
            continue
        p = finding.get("skip_pattern", "unknown")
        patterns[p] = patterns.get(p, 0) + 1
        party = finding.get("first_party_or_third_party", "unknown")
        parties[party] = parties.get(party, 0) + 1
        cat = finding.get("inferred_category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print("\n=== INVENTORY SUMMARY ===")
    print(f"Total findings: {len(findings)}")
    print(f"Files with errors: {sum(1 for f in findings if 'error' in f)}")
    print("\nBy pattern:")
    for k, v in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\nBy party:")
    for k, v in sorted(parties.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\nBy inferred category:")
    for k, v in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nOutput: {out_path}")


if __name__ == "__main__":
    main()
