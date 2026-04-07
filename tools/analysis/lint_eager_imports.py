"""AST-based linter for detecting eager/risky imports in test files.

Detects side-effectful or order-sensitive module-level imports and execution
that causes pytest collection failures in shared-interpreter environments.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

import yaml

# Safe top-level node types that don't cause collection issues
SAFE_TOP_LEVEL_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Assign,
    ast.AnnAssign,
    ast.Expr,  # docstrings only
    ast.Constant,
    ast.Pass,
)


@dataclass
class Violation:
    file: str
    line: int
    col: int
    rule_id: str
    import_name: str | None
    reason: str
    remediation: str


class EagerImportLinter:
    """Linter for detecting risky eager imports and module-scope execution."""

    def __init__(self, risky_roots: list[str], safe_roots: list[str]):
        self.risky_roots = tuple(risky_roots)
        self.safe_roots = tuple(safe_roots)

    def is_risky_import(self, module_name: str) -> bool:
        """Check if import is from a risky root."""
        if not module_name:
            return False
        return any(
            module_name.startswith(root) or module_name == root
            for root in self.risky_roots
        )

    def is_safe_import(self, module_name: str) -> bool:
        """Check if import is explicitly safe."""
        if not module_name:
            return False
        return any(
            module_name.startswith(root) or module_name == root
            for root in self.safe_roots
        )

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single test file for eager import violations."""
        violations = []
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            violations.append(Violation(
                file=str(file_path),
                line=e.lineno or 1,
                col=e.offset or 0,
                rule_id="SYNTAX_ERROR",
                import_name=None,
                reason=f"Syntax error: {e.msg}",
                remediation="Fix syntax error before linting",
            ))
            return violations
        except Exception as e:
            violations.append(Violation(
                file=str(file_path),
                line=1,
                col=0,
                rule_id="READ_ERROR",
                import_name=None,
                reason=f"Failed to read file: {e}",
                remediation="Check file permissions and encoding",
            ))
            return violations

        for node in ast.iter_child_nodes(tree):
            violations.extend(self._check_node(node, file_path, source))

        return violations

    def _check_node(self, node: ast.AST, file_path: Path, source: str) -> Iterator[Violation]:
        """Check a single top-level node for violations."""
        # Check for risky imports at module scope
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if self.is_risky_import(module) and not self.is_safe_import(module):
                names = ", ".join(alias.name for alias in node.names)
                yield Violation(
                    file=str(file_path),
                    line=node.lineno or 1,
                    col=node.col_offset or 0,
                    rule_id="RISKY_EAGER_IMPORT",
                    import_name=f"{module}.{names}" if module else names,
                    reason=f"Eager import from risky module '{module}' at module scope",
                    remediation="Move import inside a pytest fixture or test function",
                )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                if self.is_risky_import(alias.name) and not self.is_safe_import(alias.name):
                    yield Violation(
                        file=str(file_path),
                        line=node.lineno or 1,
                        col=node.col_offset or 0,
                        rule_id="RISKY_EAGER_IMPORT",
                        import_name=alias.name,
                        reason=f"Eager import from risky module '{alias.name}' at module scope",
                        remediation="Move import inside a pytest fixture or test function",
                    )

        # Check for module-scope calls (registry mutation, client creation, etc.)
        elif isinstance(node, ast.Call):
            func_name = self._get_call_name(node.func)
            yield Violation(
                file=str(file_path),
                line=node.lineno or 1,
                col=node.col_offset or 0,
                rule_id="MODULE_SCOPE_CALL",
                import_name=func_name,
                reason=f"Module-scope function call '{func_name}' may have side effects",
                remediation="Move call inside a fixture, test function, or if __name__ == '__main__' block",
            )

        # Check for module-scope assignments that call functions
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value if isinstance(node, ast.Assign) else node.value
            if isinstance(value, ast.Call):
                targets = self._get_assignment_targets(node)
                func_name = self._get_call_name(value.func)
                yield Violation(
                    file=str(file_path),
                    line=node.lineno or 1,
                    col=node.col_offset or 0,
                    rule_id="MODULE_SCOPE_ASSIGNMENT_CALL",
                    import_name=func_name,
                    reason=f"Module-scope assignment '{targets}' calls '{func_name}' - may trigger initialization",
                    remediation="Move initialization inside a fixture or lazy property",
                )

        # Check for decorator applications that might import risky modules
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    func_name = self._get_call_name(decorator.func)
                    # Check if decorator calls look risky
                    if any(risky in func_name for risky in ["registry", "register", "bootstrap", "init"]):
                        yield Violation(
                            file=str(file_path),
                            line=decorator.lineno or 1,
                            col=decorator.col_offset or 0,
                            rule_id="RISKY_DECORATOR_CALL",
                            import_name=func_name,
                            reason=f"Decorator call '{func_name}' may trigger side effects",
                            remediation="Ensure decorator is idempotent or move logic inside fixture",
                        )

    def _get_call_name(self, func: ast.expr) -> str:
        """Extract the name of a called function."""
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return f"{self._get_call_name(func.value)}.{func.attr}"
        return "<unknown>"

    def _get_assignment_targets(self, node: ast.AST) -> str:
        """Get string representation of assignment targets."""
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                return node.target.id
            return "<complex>"
        elif isinstance(node, ast.Assign):
            targets = []
            for t in node.targets:
                if isinstance(t, ast.Name):
                    targets.append(t.id)
                elif isinstance(t, ast.Attribute):
                    targets.append(f"{self._get_call_name(t.value)}.{t.attr}")
            return ", ".join(targets) if targets else "<unknown>"
        return "<unknown>"


def load_risk_config(config_path: Path | None = None) -> dict:
    """Load risky import configuration."""
    default_risky = [
        "agentic_core",
        "apps_exec",
        "apps_shared.bootstrap",
        "apps_eval.runtime",
        "apps_rg.runtime",
        "apps_lic.runtime",
        "apps_research.runtime",
        "apps_rfp.runtime",
        "system_learning.runtime",
        "tools.adg",
    ]
    default_safe = [
        "typing",
        "pathlib",
        "dataclasses",
        "pytest",
        "unittest",
        "functools",
        "collections",
        "enum",
        "json",
        "os",
        "sys",
        "tempfile",
        "time",
        "datetime",
        "hashlib",
        "random",
        "string",
        "re",
        "itertools",
        "collections.abc",
    ]

    if config_path and config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text())
            return {
                "risky_roots": config.get("risky_roots", default_risky),
                "safe_roots": config.get("safe_roots", default_safe),
            }
        except Exception:
            pass

    return {"risky_roots": default_risky, "safe_roots": default_safe}


def main():
    parser = argparse.ArgumentParser(
        description="Lint test files for eager/risky imports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/lint_eager_imports.py tests
  python tools/lint_eager_imports.py tests --json out.json
  python tools/lint_eager_imports.py tests --config config/eager_import_risk.yml
  python tools/lint_eager_imports.py tests --strict  # fail on any violation
        """,
    )
    parser.add_argument("paths", nargs="+", help="Paths to lint")
    parser.add_argument("--config", type=Path, help="Path to risk config YAML")
    parser.add_argument("--json", type=Path, help="Output JSON report to file")
    parser.add_argument("--strict", action="store_true", help="Exit with error on any violation")
    parser.add_argument("--fix-report", action="store_true", help="Generate fix suggestions")

    args = parser.parse_args()

    # Load configuration
    config = load_risk_config(args.config)
    linter = EagerImportLinter(config["risky_roots"], config["safe_roots"])

    # Collect all violations
    all_violations: list[Violation] = []
    files_checked = 0

    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == ".py":
            files_checked += 1
            all_violations.extend(linter.lint_file(path))
        elif path.is_dir():
            for py_file in path.rglob("test*.py"):
                files_checked += 1
                all_violations.extend(linter.lint_file(py_file))
            for py_file in path.rglob("conftest.py"):
                files_checked += 1
                all_violations.extend(linter.lint_file(py_file))

    # Output results
    if args.json:
        report = {
            "summary": {
                "files_checked": files_checked,
                "violations_found": len(all_violations),
                "risky_roots": config["risky_roots"],
            },
            "violations": [asdict(v) for v in all_violations],
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2))
        print(f"Report written to {args.json}")
    else:
        # Console output
        if all_violations:
            print(f"Found {len(all_violations)} violation(s) in {files_checked} file(s):\n")
            for v in all_violations:
                print(f"{v.file}:{v.line}:{v.col} [{v.rule_id}] {v.reason}")
                if args.fix_report:
                    print(f"  -> {v.remediation}\n")
        else:
            print(f"✓ No violations found in {files_checked} file(s)")

    # Exit with error if strict mode and violations found
    if args.strict and all_violations:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
