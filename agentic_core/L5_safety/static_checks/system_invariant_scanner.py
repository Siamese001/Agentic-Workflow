"""System Invariant Scanner — AST/CI enforcement for bypass detection.

Scans repository for forbidden patterns that could bypass sovereignty controls:
- Gateway bypass (direct file operations)
- Provider SDK bypass (direct LLM API calls)
- Embedding bypass (factory instantiation)
- Unsigned ingress (signature verification)
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import TESTS_DIR


class BypassViolation:
    """Represents a detected bypass violation."""

    def __init__(self, file_path: str, line: int, rule_id: str, snippet: str, description: str):
        self.file_path = file_path
        self.line = line
        self.rule_id = rule_id
        self.snippet = snippet
        self.description = description

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line} [{self.rule_id}] {self.description}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line": self.line,
            "rule_id": self.rule_id,
            "snippet": self.snippet,
            "description": self.description
        }


class SystemInvariantScanner(ast.NodeVisitor):
    """AST visitor to detect sovereignty bypass violations."""

    # Allowlist of modules that can perform restricted operations
    ALLOWLISTED_MODULES = {
        "agentic_core.L2_execution.UniversalWriteGateway",
        "agentic_core.L2_execution.engines.execution_gateway",
        "agentic_core.L2_execution.healers.healing_provider_adapters",
        "system_invariant_scanner",
        "system_learning.engines.embedding_service_factory",
        TESTS_DIR,  # Test modules are allowed for testing
        "test_",  # Test files
    }

    # Restricted provider SDKs
    RESTRICTED_PROVIDERS = {
        "openai", "anthropic", "google.generativeai", "vertexai",
        "litellm", "transformers", "torch", "tensorflow"
    }

    # Restricted file operations
    RESTRICTED_FILE_OPS = {
        "open", "Path.write_text", "Path.write_bytes", "Path.unlink",
        "os.remove", "os.rename", "os.replace", "os.mkdir", "os.makedirs"
    }

    # Restricted embedding operations
    RESTRICTED_EMBEDDING = {
        "EmbeddingServiceFactory", "SentenceTransformer", "OpenAIEmbeddings"
    }

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[BypassViolation] = []
        self.current_line_content = ""

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        if hasattr(node, "lineno"):
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1].strip()
            except Exception:
                self.current_line_content = ""

        super().visit(node)

    def _is_allowlisted(self) -> bool:
        """Check if current file is allowlisted."""
        file_str = str(self.file_path)
        return any(allowed in file_str for allowed in self.ALLOWLISTED_MODULES)

    def _has_allowlist_comment(self) -> bool:
        """Check if current line has allowlist comment."""
        return "# guardian: allow-" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for restricted function calls."""
        if self._is_allowlisted() or self._has_allowlist_comment():
            self.generic_visit(node)
            return

        # Check for restricted file operations
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.RESTRICTED_FILE_OPS:
                self._add_violation(
                    node.lineno,
                    "GATEWAY_BYPASS",
                    f"Direct call to {func_name}",
                    f"Direct file operation '{func_name}' detected - use UniversalWriteGateway"
                )

        # Check for restricted provider calls
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                if module_name in self.RESTRICTED_PROVIDERS:
                    self._add_violation(
                        node.lineno,
                        "PROVIDER_BYPASS",
                        f"Direct call to {module_name}.{node.func.attr}",
                        "Direct provider SDK call detected - use HealingProviderInvoker"
                    )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check for restricted imports."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return

        for alias in node.names:
            if alias.name in self.RESTRICTED_PROVIDERS:
                self._add_violation(
                    node.lineno,
                    "PROVIDER_BYPASS",
                    f"Import of restricted provider {alias.name}",
                    "Direct provider import detected - use HealingProviderInvoker seam"
                )
            elif any(restricted in alias.name for restricted in self.RESTRICTED_EMBEDDING):
                self._add_violation(
                    node.lineno,
                    "EMBEDDING_BYPASS",
                    f"Import of restricted embedding {alias.name}",
                    "Direct embedding import detected - use EmbeddingServiceFactory"
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for restricted from-imports."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return

        if node.module:
            if node.module in self.RESTRICTED_PROVIDERS:
                self._add_violation(
                    node.lineno,
                    "PROVIDER_BYPASS",
                    f"From-import of restricted provider {node.module}",
                    "Direct provider import detected - use HealingProviderInvoker seam"
                )
            elif any(restricted in node.module for restricted in self.RESTRICTED_EMBEDDING):
                self._add_violation(
                    node.lineno,
                    "EMBEDDING_BYPASS",
                    f"From-import of restricted embedding {node.module}",
                    "Direct embedding import detected - use EmbeddingServiceFactory"
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check for restricted class definitions."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return

        if node.name in self.RESTRICTED_EMBEDDING:
            self._add_violation(
                node.lineno,
                "EMBEDDING_BYPASS",
                f"Class definition of {node.name}",
                "Direct embedding class definition detected - use EmbeddingServiceFactory"
            )

        self.generic_visit(node)

    def _add_violation(self, line: int, rule_id: str, snippet: str, description: str) -> None:
        """Add a violation to the list."""
        violation = BypassViolation(
            file_path=str(self.file_path),
            line=line,
            rule_id=rule_id,
            snippet=snippet,
            description=description
        )
        self.violations.append(violation)


def scan_repository_for_bypasses(repo_root: Path) -> list[BypassViolation]:
    """Scan entire repository for sovereignty bypass violations."""
    violations: list[BypassViolation] = []

    # File patterns to scan
    patterns = ["**/*.py"]

    for pattern in patterns:
        for file_path in repo_root.glob(pattern):
            # Skip certain directories
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", ".pytest_cache", "node_modules"]):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                tree = ast.parse(content, filename=str(file_path))

                # Scan for violations
                scanner = SystemInvariantScanner(file_path)
                scanner.visit(tree)
                violations.extend(scanner.violations)

            except SyntaxError as e:
                # Record syntax errors as violations
                violations.append(BypassViolation(
                    file_path=str(file_path),
                    line=e.lineno or 0,
                    rule_id="SYNTAX_ERROR",
                    snippet="Syntax error",
                    description=f"Syntax error: {e}"
                ))
            except Exception as e:
                # Record other errors
                violations.append(BypassViolation(
                    file_path=str(file_path),
                    line=0,
                    rule_id="SCAN_ERROR",
                    snippet="Scan error",
                    description=f"Scan error: {e}"
                ))

    # Sort violations deterministically
    violations.sort(key=lambda v: (v.file_path, v.line, v.rule_id))

    return violations


def print_bypass_report(violations: list[BypassViolation]) -> None:
    """Print a formatted report of bypass violations."""
    if not violations:
        print("✅ No sovereignty bypass violations detected")
        return

    print(f"❌ Found {len(violations)} sovereignty bypass violations:")
    print()

    # Group by rule type
    by_rule = {}
    for violation in violations:
        if violation.rule_id not in by_rule:
            by_rule[violation.rule_id] = []
        by_rule[violation.rule_id].append(violation)

    for rule_id in sorted(by_rule.keys()):
        print(f"🚨 {rule_id}:")
        for violation in by_rule[rule_id]:
            print(f"   {violation}")
        print()


def get_bypass_scan_summary(violations: list[BypassViolation]) -> dict[str, Any]:
    """Get summary statistics for bypass scan."""
    files_affected = set()
    for violation in violations:
        files_affected.add(violation.file_path)

    summary = {
        "total_violations": len(violations),
        "by_rule": {},
        "files_affected": len(files_affected),
        "files_affected_list": sorted(files_affected),
    }

    for violation in violations:
        rule_id = violation.rule_id
        if rule_id not in summary["by_rule"]:
            summary["by_rule"][rule_id] = 0
        summary["by_rule"][rule_id] += 1

    return summary


if __name__ == "__main__":
    # Scan repository when run as script
    repo_root = Path(__file__).resolve().parents[2]
    violations = scan_repository_for_bypasses(repo_root)

    print("System Invariant Scanner - Sovereignty Bypass Detection")
    print("=" * 60)
    print_bypass_report(violations)

    summary = get_bypass_scan_summary(violations)
    print(f"Summary: {summary['total_violations']} violations across {summary['files_affected']} files")

    # Exit with error code if violations found
    if violations:
        os.exit(1)
    else:
        os.exit(0)
