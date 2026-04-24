"""Phase 2 + 3: Classify every test file and detect violations.

Phase 2: MECE classification of every test into exactly one of:
  core, optional, platform, external, experimental

Phase 3: Violation detection for invalid skip patterns.

Outputs:
  - artifacts/test_enforcement/test_classification.json
  - artifacts/test_enforcement/test_violations.json
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

FIRST_PARTY_TOPS = frozenset(
    {
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
    }
)

# Third-party packages that are OPTIONAL (not in core dependencies)
OPTIONAL_THIRD_PARTY = frozenset(
    {
        "playwright",
        "dash",
        "plotly",
        "fastapi",
        "uvicorn",
        "waitress",
        "sentence_transformers",
        "chromadb",
        "duckdb",
        "numpy",
        "np",
        "pandas",
        "pd",
        "sklearn",
        "scikit_learn",
        "beautifulsoup4",
        "bs4",
        "rich",
        "opentelemetry",
        "livereload",
        "rank_bm25",
        "pydantic_settings",
        "aiofiles",
    }
)

# Third-party packages that are EXTERNAL (live services)
EXTERNAL_DEPS = frozenset(
    {
        "redis",
        "pinecone",
        "openai",
        "anthropic",
        "google",
        "google_genai",
    }
)

# Platform-specific markers
PLATFORM_INDICATORS = frozenset(
    {
        "torch",
        "cuda",
        "gpu",
        "tensorflow",
        "jax",
        "mps",
    }
)

# Directory-based classification rules
DIR_CATEGORY_MAP = {
    "tests/unit_min_deps": "core",
    "tests/unit": "core",
    "tests/architecture": "core",
    "tests/enforcement": "core",
    "tests/governance": "core",
    "tests/sovereign_hardening": "core",
    "tests/adg": "core",
    "tests/guardian": "core",
    "tests/ci": "core",
    "tests/integration/agentic_core": "core",
    "tests/agentic_core": "core",
    "tests/integration_full_deps": "optional",
    "tests/integration": "optional",
    "tests/e2e": "optional",
    "tests/evaluation": "experimental",
    "tests/performance": "experimental",
    "tests/stress": "experimental",
    "tests/hardening": "experimental",
    "tests/misc": "experimental",
    "tests/apps_eval": "optional",
    "tests/apps_exec": "optional",
    "tests/apps_research": "optional",
    "tests/apps_rfp": "optional",
    "tests/apps_rg": "optional",
    "tests/apps_lic": "optional",
    "tests/system_learning": "core",
}


def _is_first_party(module_name: str) -> bool:
    if not module_name:
        return False
    return module_name.split(".")[0] in FIRST_PARTY_TOPS


def _classify_dir(file_path: str) -> str:
    """Classify test by directory path (longest prefix match)."""
    fp_norm = file_path.replace("\\", "/")
    best_match = ""
    best_cat = "core"  # default
    for prefix, cat in DIR_CATEGORY_MAP.items():
        if fp_norm.startswith(prefix) and len(prefix) > len(best_match):
            best_match = prefix
            best_cat = cat
    return best_cat


def _has_marker(source: str, marker_name: str) -> bool:
    """Check if source contains a pytest marker."""
    return f"pytest.mark.{marker_name}" in source or f"@{marker_name}" in source


def _extract_markers(source: str) -> list[str]:
    """Extract all pytest markers from source."""
    markers = []
    for m in re.finditer(r"pytest\.mark\.(\w+)", source):
        markers.append(m.group(1))
    return markers


class TestFileAnalyzer:
    """Analyze a single test file for classification and violations."""

    def __init__(self, file_path: str, abs_path: pathlib.Path):
        self.file_path = file_path
        self.abs_path = abs_path
        self.source = ""
        self.tree: ast.Module | None = None
        self.has_syntax_error = False
        self.test_functions: list[str] = []
        self.markers: list[str] = []
        self.skip_patterns: list[dict] = []
        self.imports: list[dict] = []

    def analyze(self) -> bool:
        try:
            self.source = self.abs_path.read_text(encoding="utf-8", errors="replace")
        except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
            return False

        try:
            self.tree = ast.parse(self.source, filename=self.file_path)
        except SyntaxError:
            self.has_syntax_error = True
            return True  # Still analyzable at text level

        self.markers = _extract_markers(self.source)
        self._extract_test_functions()
        self._extract_imports()
        self._extract_skip_patterns()
        return True

    def _extract_test_functions(self):
        if not self.tree:
            return
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    self.test_functions.append(node.name)

    def _extract_imports(self):
        if not self.tree:
            return
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(
                        {
                            "module": alias.name,
                            "first_party": _is_first_party(alias.name),
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.append(
                        {
                            "module": node.module,
                            "first_party": _is_first_party(node.module),
                            "line": node.lineno,
                        }
                    )

    def _extract_skip_patterns(self):
        """Extract all skip-related patterns for violation detection."""
        if not self.tree:
            # Text-level analysis for syntax-error files
            self._text_level_skip_scan()
            return

        visitor = _SkipCollector(self.source.splitlines(), self.file_path)
        visitor.visit(self.tree)
        self.skip_patterns = visitor.patterns

    def _text_level_skip_scan(self):
        """Regex-based skip detection for files with syntax errors."""
        lines = self.source.splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if "pytest.skip(" in stripped:
                self.skip_patterns.append(
                    {
                        "line": i,
                        "pattern": "pytest_skip_call",
                        "text": stripped[:200],
                    }
                )
            if "pytest.importorskip(" in stripped:
                self.skip_patterns.append(
                    {
                        "line": i,
                        "pattern": "importorskip",
                        "text": stripped[:200],
                    }
                )
            if "except ImportError" in stripped or "except ModuleNotFoundError" in stripped:
                self.skip_patterns.append(
                    {
                        "line": i,
                        "pattern": "except_importerror",
                        "text": stripped[:200],
                    }
                )

    def classify(self) -> dict:
        """Classify this test file into exactly one MECE category."""
        dir_cat = _classify_dir(self.file_path)

        # Override by explicit marker
        if "external" in self.markers:
            category = "external"
            justification = "explicit @pytest.mark.external marker"
        elif "platform" in self.markers:
            category = "platform"
            justification = "explicit @pytest.mark.platform marker"
        elif "experimental" in self.markers:
            category = "experimental"
            justification = "explicit @pytest.mark.experimental marker"
        elif "optional" in self.markers:
            category = "optional"
            justification = "explicit @pytest.mark.optional marker"
        elif "playwright" in self.markers:
            category = "optional"
            justification = "playwright marker implies optional browser dependency"
        elif "e2e" in self.markers and dir_cat in ("optional", "experimental"):
            category = "optional"
            justification = "e2e marker in optional/experimental directory"
        elif "integration_full_deps" in self.markers:
            category = "optional"
            justification = "integration_full_deps marker"
        else:
            category = dir_cat
            justification = f"directory classification: {self.file_path.split('/')[0]}/{self.file_path.split('/')[1] if '/' in self.file_path else ''}"

        test_names = (
            self.test_functions
            if self.test_functions
            else ["<syntax-error: no functions parsed>"]
            if self.has_syntax_error
            else ["<no test functions>"]
        )

        result = {
            "file_path": self.file_path,
            "category": category,
            "justification": justification,
            "has_syntax_error": self.has_syntax_error,
            "test_count": len(self.test_functions),
            "markers": self.markers,
            "tests": test_names,
        }
        return result

    def detect_violations(self, category: str) -> list[dict]:
        """Detect all violations in this file given its category."""
        violations = []

        # V1: Syntax error in any test file is itself a violation
        if self.has_syntax_error:
            # Check if it's a known broken template
            if (
                "pytest.importorskip" in self.source
                and "except" not in self.source.split("pytest.importorskip")[0].split("try:")[-1]
            ):
                violations.append(
                    {
                        "file_path": self.file_path,
                        "test_name": "<all>",
                        "violation_type": "broken_template_missing_except",
                        "why_invalid": "Generated ADG test stub has broken try/except: missing 'except ImportError:' clause, replaced by misplaced pytest.importorskip",
                        "required_fix": "Replace broken template with direct first-party import (no skip wrapper)",
                    }
                )
            else:
                violations.append(
                    {
                        "file_path": self.file_path,
                        "test_name": "<all>",
                        "violation_type": "syntax_error",
                        "why_invalid": "File has syntax errors preventing test collection",
                        "required_fix": "Fix syntax errors to make file parseable",
                    }
                )

        # V2: First-party import wrapped in try/except ImportError
        for pat in self.skip_patterns:
            pattern_type = pat.get("pattern", "")
            text = pat.get("text", "")

            if pattern_type == "try_except_importerror":
                dep = pat.get("dependency", "")
                if _is_first_party(dep):
                    violations.append(
                        {
                            "file_path": self.file_path,
                            "test_name": pat.get("test_name", "<module-level>"),
                            "line": pat.get("line"),
                            "violation_type": "first_party_import_skip",
                            "why_invalid": f"First-party import '{dep}' wrapped in try/except ImportError — hides broken imports",
                            "required_fix": "Remove try/except wrapper; use direct import. If module doesn't exist, fix the import path or remove the test.",
                        }
                    )

            # V3: pytest.skip without category context in core tests
            if pattern_type == "pytest_skip_call" and category == "core":
                reason = pat.get("reason", text)
                if "import" in reason.lower():
                    violations.append(
                        {
                            "file_path": self.file_path,
                            "test_name": pat.get("test_name", "<unknown>"),
                            "line": pat.get("line"),
                            "violation_type": "core_test_import_skip",
                            "why_invalid": f"Core test uses pytest.skip() to hide import failure: {reason[:100]}",
                            "required_fix": "Remove skip; let import failure surface as test error",
                        }
                    )

            # V4: importorskip in core unmarked test
            if pattern_type == "importorskip" and category == "core":
                dep = pat.get("dependency", "")
                if dep not in OPTIONAL_THIRD_PARTY and dep != "playwright":
                    violations.append(
                        {
                            "file_path": self.file_path,
                            "test_name": pat.get("test_name", "<module-level>"),
                            "line": pat.get("line"),
                            "violation_type": "importorskip_in_core",
                            "why_invalid": f"pytest.importorskip('{dep}') used in core test without optional marker",
                            "required_fix": "Either mark test as @pytest.mark.optional or remove importorskip and use direct import",
                        }
                    )

            # V5: skipif tied to import availability on core test
            if pattern_type == "skipif_import" and category == "core":
                dep = pat.get("dependency", "")
                if _is_first_party(dep) or dep.startswith("HAS_") or dep.startswith("has_"):
                    violations.append(
                        {
                            "file_path": self.file_path,
                            "test_name": pat.get("test_name", "<unknown>"),
                            "line": pat.get("line"),
                            "violation_type": "skipif_import_in_core",
                            "why_invalid": f"Core test uses skipif to skip on import availability: {dep}",
                            "required_fix": "Remove skipif; first-party imports must not be optional in core tests",
                        }
                    )

        # V6: stub/flag patterns for first-party in core
        if category == "core" and self.tree:
            for pat in self.skip_patterns:
                if pat.get("pattern") == "try_except_importerror":
                    behavior = pat.get("handler_behavior", "")
                    dep = pat.get("dependency", "")
                    if behavior in ("stub", "flag", "pass") and _is_first_party(dep):
                        violations.append(
                            {
                                "file_path": self.file_path,
                                "test_name": pat.get("test_name", "<module-level>"),
                                "line": pat.get("line"),
                                "violation_type": f"first_party_{behavior}_on_importerror",
                                "why_invalid": f"First-party '{dep}' import failure silently handled with {behavior} pattern",
                                "required_fix": "Remove try/except; use direct import. Broken first-party imports must surface as errors.",
                            }
                        )

        return violations


class _SkipCollector(ast.NodeVisitor):
    """Lightweight AST visitor to collect skip patterns with context."""

    def __init__(self, lines: list[str], file_path: str):
        self.lines = lines
        self.file_path = file_path
        self.patterns: list[dict] = []
        self._current_func: str | None = None
        self._current_class: str | None = None

    def _test_name(self) -> str:
        parts = []
        if self._current_class:
            parts.append(self._current_class)
        if self._current_func:
            parts.append(self._current_func)
        return "::".join(parts) if parts else "<module-level>"

    def visit_ClassDef(self, node):
        old = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old

    def visit_FunctionDef(self, node):
        old = self._current_func
        if node.name.startswith("test_"):
            self._current_func = node.name
        self._check_decorators(node)
        self.generic_visit(node)
        self._current_func = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check_decorators(self, node):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.func.attr == "skipif":
                    src = self._source_range(dec.lineno, dec.end_lineno or dec.lineno)
                    dep = self._extract_skipif_dep(dec, src)
                    self.patterns.append(
                        {
                            "line": dec.lineno,
                            "pattern": "skipif_import",
                            "test_name": self._test_name(),
                            "dependency": dep,
                            "text": src[:200],
                        }
                    )
                elif dec.func.attr == "skip":
                    reason = ""
                    for kw in dec.keywords:
                        if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                            reason = str(kw.value.value)
                    self.patterns.append(
                        {
                            "line": dec.lineno,
                            "pattern": "skip_decorator",
                            "test_name": self._test_name(),
                            "reason": reason,
                        }
                    )

    def _extract_skipif_dep(self, call, src):
        m = re.search(r'find_spec\(["\']([^"\']+)', src)
        if m:
            return m.group(1)
        m = re.search(r"import\s+(\w[\w.]*)", src)
        if m:
            return m.group(1)
        # Check for HAS_X flags
        for arg in call.args:
            if isinstance(arg, ast.UnaryOp) and isinstance(arg.operand, ast.Name):
                return arg.operand.id
            if isinstance(arg, ast.Name) and (arg.id.startswith("HAS_") or arg.id.startswith("_")):
                return arg.id
        return ""

    def visit_Call(self, node):
        name = self._call_name(node.func)
        if name in ("pytest.skip", "skip"):
            reason = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                reason = str(node.args[0].value)
            for kw in node.keywords:
                if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                    reason = str(kw.value.value)
            self.patterns.append(
                {
                    "line": node.lineno,
                    "pattern": "pytest_skip_call",
                    "test_name": self._test_name(),
                    "reason": reason,
                    "text": reason[:200],
                }
            )
        elif name in ("pytest.importorskip", "importorskip"):
            dep = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                dep = str(node.args[0].value)
            self.patterns.append(
                {
                    "line": node.lineno,
                    "pattern": "importorskip",
                    "test_name": self._test_name(),
                    "dependency": dep,
                }
            )
        self.generic_visit(node)

    def visit_Try(self, node):
        for handler in node.handlers:
            if self._is_import_error(handler):
                deps = []
                for stmt in node.body:
                    if isinstance(stmt, ast.Import):
                        for a in stmt.names:
                            deps.append(a.name)
                    elif isinstance(stmt, ast.ImportFrom) and stmt.module:
                        deps.append(stmt.module)
                dep_str = ", ".join(deps) if deps else "<unknown>"

                behavior = self._handler_behavior(handler)
                self.patterns.append(
                    {
                        "line": node.lineno,
                        "pattern": "try_except_importerror",
                        "test_name": self._test_name(),
                        "dependency": dep_str,
                        "handler_behavior": behavior,
                    }
                )
        self.generic_visit(node)

    def _is_import_error(self, handler):
        if handler.type is None:
            return False
        if isinstance(handler.type, ast.Name):
            return handler.type.id in ("ImportError", "ModuleNotFoundError")
        if isinstance(handler.type, ast.Tuple):
            return any(
                isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
                for e in handler.type.elts
            )
        return False

    def _handler_behavior(self, handler):
        for stmt in handler.body:
            if isinstance(stmt, ast.Pass):
                return "pass"
            if isinstance(stmt, ast.Raise):
                return "raise"
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                name = self._call_name(stmt.value.func)
                if "skip" in name.lower():
                    return "skip"
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name):
                        if t.id.startswith("HAS_") or t.id.startswith("has_"):
                            return "flag"
                        if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                            return "stub"
        return "other"

    def _call_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = self._call_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def _source_range(self, start, end):
        s = max(0, start - 1)
        e = min(end, len(self.lines))
        return " ".join(self.lines[s:e]).strip()


def collect_all_test_files(root: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """Collect all test files with relative paths."""
    test_dir = root / "tests"
    files = []
    if test_dir.exists():
        for fp in sorted(test_dir.rglob("test_*.py")):
            rel = str(fp.relative_to(root)).replace("\\", "/")
            files.append((rel, fp))
        for fp in sorted(test_dir.rglob("*_test.py")):
            rel = str(fp.relative_to(root)).replace("\\", "/")
            files.append((rel, fp))
        # conftest files
        for fp in sorted(test_dir.rglob("conftest.py")):
            rel = str(fp.relative_to(root)).replace("\\", "/")
            files.append((rel, fp))
    # Root test files
    for fp in sorted(root.glob("test_*.py")):
        rel = str(fp.relative_to(root)).replace("\\", "/")
        files.append((rel, fp))
    # Root conftest
    rc = root / "conftest.py"
    if rc.exists():
        files.append(("conftest.py", rc))

    # Deduplicate
    seen = set()
    unique = []
    for rel, fp in files:
        if rel not in seen:
            seen.add(rel)
            unique.append((rel, fp))
    return unique


def main():
    out_dir = ROOT / "artifacts" / "test_enforcement"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_files = collect_all_test_files(ROOT)
    print(f"Analyzing {len(all_files)} test files...", file=sys.stderr)

    classifications = []
    all_violations = []
    unclassified_count = 0

    for i, (rel, fp) in enumerate(all_files):
        if i % 500 == 0 and i > 0:
            print(f"  ...{i}/{len(all_files)}", file=sys.stderr)

        analyzer = TestFileAnalyzer(rel, fp)
        if not analyzer.analyze():
            unclassified_count += 1
            continue

        classification = analyzer.classify()
        classifications.append(classification)

        violations = analyzer.detect_violations(classification["category"])
        all_violations.extend(violations)

    # Write classification
    cls_path = out_dir / "test_classification.json"
    with open(cls_path, "w", encoding="utf-8") as f:
        json.dump(classifications, f, indent=2, default=str)

    # Write violations
    vio_path = out_dir / "test_violations.json"
    with open(vio_path, "w", encoding="utf-8") as f:
        json.dump(all_violations, f, indent=2, default=str)

    # Summary
    import collections

    cat_counts = collections.Counter(c["category"] for c in classifications)
    syntax_err = sum(1 for c in classifications if c.get("has_syntax_error"))
    test_total = sum(c["test_count"] for c in classifications)

    vio_types = collections.Counter(v["violation_type"] for v in all_violations)
    vio_files = len(set(v["file_path"] for v in all_violations))

    print(f"\n{'=' * 60}")
    print("PHASE 2 — CLASSIFICATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total files classified: {len(classifications)}")
    print(f"Total test functions: {test_total}")
    print(f"Files with syntax errors: {syntax_err}")
    print(f"Unreadable files: {unclassified_count}")
    print("\nBy category:")
    for cat in ["core", "optional", "platform", "external", "experimental"]:
        print(f"  {cat}: {cat_counts.get(cat, 0)}")

    print(f"\n{'=' * 60}")
    print("PHASE 3 — VIOLATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total violations: {len(all_violations)}")
    print(f"Files with violations: {vio_files}")
    print("\nBy violation type:")
    for k, v in vio_types.most_common():
        print(f"  {k}: {v}")

    print("\nOutputs:")
    print(f"  {cls_path}")
    print(f"  {vio_path}")


if __name__ == "__main__":
    main()
