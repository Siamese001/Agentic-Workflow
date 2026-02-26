from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple

# --- Configuration ---

# The root of the repository to scan.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Namespaces that are allowed to perform gateway-like operations.
# The gateway itself and its direct dependencies are exempt.
GATEWAY_NAMESPACE = "agentic_core.L2_execution.enforcement"
ALLOWED_NAMESPACES: set[str] = {
    GATEWAY_NAMESPACE,
    "tests",  # Tests need to import things to mock them.
}

# Forbidden imports that indicate a direct SDK or HTTP client usage.
FORBIDDEN_IMPORTS: set[str] = {
    "boto3",
    "openai",
    "anthropic",
    "google.cloud",
    "requests",
    "httpx",
    "urllib3",
    "subprocess",
}

# Forbidden string literals that indicate direct model usage.
FORBIDDEN_LITERALS: set[str] = {
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-2",
    "claude-3-opus",
    "gemini-pro",
}

# --- Violation Data Structures ---


class Violation(NamedTuple):
    """A single instance of a gateway bypass violation."""

    file_path: str
    line_number: int
    code: str
    message: str


# --- AST Visitor for Detection ---


class GatewayBypassVisitor(ast.NodeVisitor):
    """An AST visitor that detects gateway bypass violations."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[Violation] = []
        self._current_namespace = self._get_namespace(file_path)

    def _get_namespace(self, path: Path) -> str:
        """Converts a file path to a Python namespace."""
        try:
            return str(path.relative_to(REPO_ROOT)).replace("/", ".").replace("\\", ".")[:-3]
        except ValueError:
            return str(path)

    def _is_exempt(self) -> bool:
        """Checks if the current file is in an allowed namespace."""
        return any(self._current_namespace.startswith(ns) for ns in ALLOWED_NAMESPACES)

    def visit_Import(self, node: ast.Import) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return

        for alias in node.names:
            if alias.name in FORBIDDEN_IMPORTS:
                self.violations.append(
                    Violation(
                        file_path=str(self.file_path),
                        line_number=node.lineno,
                        code=ast.dump(node),
                        message=f"Direct import of forbidden module '{alias.name}'. Use the gateway.",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return

        if node.module and node.module in FORBIDDEN_IMPORTS:
            self.violations.append(
                Violation(
                    file_path=str(self.file_path),
                    line_number=node.lineno,
                    code=ast.dump(node),
                    message=f"Direct import from forbidden module '{node.module}'. Use the gateway.",
                )
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return

        if isinstance(node.value, str) and node.value in FORBIDDEN_LITERALS:
            self.violations.append(
                Violation(
                    file_path=str(self.file_path),
                    line_number=node.lineno,
                    code=ast.dump(node),
                    message=f"Direct use of forbidden model literal '{node.value}'. Use the gateway.",
                )
            )
        self.generic_visit(node)


# --- Main Scanner Logic ---


def scan_file(file_path: Path) -> list[Violation]:
    """Scans a single Python file for violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        visitor = GatewayBypassVisitor(file_path)
        visitor.visit(tree)
        return visitor.violations
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return []


def main() -> int:
    """Runs the scanner across the entire repository and reports violations."""
    print("--- Running Gateway Bypass Scanner (AST-Based) ---")
    all_violations: list[Violation] = []
    python_files = list(REPO_ROOT.rglob("*.py"))

    for file_path in python_files:
        if "__pycache__" in str(file_path):
            continue
        violations = scan_file(file_path)
        all_violations.extend(violations)

    if not all_violations:
        print("\n\033[92mSuccess: No gateway bypass violations found.\033[0m")
        return 0
    else:
        print(f"\n\033[91mFailure: Found {len(all_violations)} gateway bypass violations:\033[0m")
        for violation in all_violations:
            print(f"  - \033[93m{violation.file_path}:{violation.line_number}\033[0m: {violation.message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
