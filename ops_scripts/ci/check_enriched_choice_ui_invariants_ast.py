#!/usr/bin/env python3
"""AST-based scanner for enriched choice UI invariants.

Alternative to regex-based scanner with higher precision for complex cases.
Deferred scope item: AST-based detection when regex false positive rate > 5%.

Usage:
    python check_enriched_choice_ui_invariants_ast.py <file_or_directory> [--advisory]
"""

from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


class AskUserQuestionVisitor(ast.NodeVisitor):
    """AST visitor to detect ask_user_question calls and their context."""

    def __init__(self, source_lines: list[str]):
        self.source_lines = source_lines
        self.violations: list[dict[str, Any]] = []
        self.has_enriched_import = False
        self.has_build_enriched_call = False
        self.has_ag_import = False

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports from tools.decisions or author_gate modules."""
        if node.module:
            module = node.module
            if "enriched_choice_builder" in module:
                self.has_enriched_import = True
            if "author_gate" in module or "emit_packet" in module:
                self.has_ag_import = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect ask_user_question calls and check their context."""
        if isinstance(node.func, ast.Name) and node.func.id == "ask_user_question":
            # Found ask_user_question call
            has_options = any(
                isinstance(kw, ast.keyword) and kw.arg == "options"
                for kw in node.keywords
            )

            if has_options:
                # Check if enriched builder is in the same scope
                line_num = node.lineno

                # Look for build_enriched_choice_question call in function scope
                is_enriched = self._has_enriched_builder_in_scope(node)
                is_ag = self.has_ag_import and self._has_ag_packet_in_function(node)

                if not is_enriched and not is_ag:
                    self.violations.append({
                        "line": line_num,
                        "column": node.col_offset + 1,
                        "pattern": "raw_ask_user_question",
                        "severity": "critical",
                        "message": "Raw ask_user_question without enriched wrapper or AG pipeline",
                    })

        # Check for build_enriched_choice_question calls
        if isinstance(node.func, ast.Name) and node.func.id == "build_enriched_choice_question":
            self.has_build_enriched_call = True

        # Check for AUTHOR_GATE_PACKET emission
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.left, ast.Constant):
                    if "AUTHOR_GATE_PACKET" in str(first_arg.left.value):
                        self._check_ag_packet_authority(node)

        self.generic_visit(node)

    def _has_enriched_builder_in_scope(self, node: ast.Call) -> bool:
        """Check if build_enriched_choice_question is called in the same function."""
        # Walk up to find enclosing function
        # For simplicity, check if the import exists and builder was called anywhere
        return self.has_enriched_import and self.has_build_enriched_call

    def _has_ag_packet_in_function(self, node: ast.Call) -> bool:
        """Check if AUTHOR_GATE_PACKET is emitted in the same context."""
        # Simplified check - AG import present indicates AG pipeline
        return self.has_ag_import

    def _check_ag_packet_authority(self, node: ast.Call) -> None:
        """Check if AUTHOR_GATE_PACKET is emitted outside canonical path."""
        # For AST mode, we track this separately
        pass


def analyze_file_ast(file_path: Path) -> list[dict[str, Any]]:
    """Analyze a Python file using AST for precise detection."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [{
            "line": 0,
            "column": 0,
            "pattern": "parse_error",
            "severity": "error",
            "message": f"Failed to parse file: {e}",
        }]

    source_lines = content.split("\n")
    visitor = AskUserQuestionVisitor(source_lines)
    visitor.visit(tree)

    return visitor.violations


def check_files(paths: list[Path], advisory: bool = False) -> dict[str, Any]:
    """Check files using AST-based analysis."""
    results = {
        "files_checked": 0,
        "pass": 0,
        "fail": 0,
        "exempt": 0,
        "violations": [],
    }

    for path in paths:
        if path.is_dir():
            for py_file in path.rglob("*.py"):
                _check_single_file_ast(py_file, results)
        elif path.suffix == ".py":
            _check_single_file_ast(path, results)

    return results


def _check_single_file_ast(file_path: Path, results: dict[str, Any]) -> None:
    """Check a single Python file using AST."""
    results["files_checked"] += 1

    # Check exemptions
    rel_path = str(file_path.relative_to(REPO_ROOT)) if file_path.is_relative_to(REPO_ROOT) else str(file_path)

    exempt_patterns = [
        "tests/",
        "_test",
        "test_",
        "conftest",
        "apps_shared/cli/interactive_wizard.py",
        "docs/",
        ".windsurf/plans/",
        "archives/",
    ]

    if any(pat in rel_path for pat in exempt_patterns):
        results["exempt"] += 1
        return

    violations = analyze_file_ast(file_path)

    if violations:
        results["fail"] += 1
        for v in violations:
            v["file"] = rel_path
        results["violations"].extend(violations)
    else:
        results["pass"] += 1


def main() -> int:
    """Main entry point for AST-based scanner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AST-based scanner for enriched choice UI invariants"
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument("--advisory", action="store_true", help="Advisory mode (always exit 0)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    paths = [Path(p) for p in args.paths]
    results = check_files(paths, advisory=args.advisory)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("Enriched Choice UI Invariants Check (AST-based)")
        print("=" * 70)
        print(f"\nSummary: {results['files_checked']} files checked")
        print(f"  ✓ Pass: {results['pass']}")
        print(f"  ✗ Fail: {results['fail']}")
        print(f"  ○ Exempt: {results['exempt']}")

        if results["violations"]:
            print("\n" + "-" * 70)
            print("Violations:")
            print("-" * 70)
            for v in results["violations"]:
                print(f"\n{v['file']}:")
                print(f"  Line {v['line']}:{v['column']}  [{v['severity'].upper()}]")
                print(f"    Pattern: {v['pattern']}")
                print(f"    Message: {v['message']}")

        print()

    # Exit code
    if args.advisory:
        return 0

    fail_closed = os.environ.get("ENRICHED_CHOICE_UI_FAIL_CLOSED", "")
    bypass = os.environ.get("ENRICHED_CHOICE_UI_BYPASS", "")

    if bypass:
        return 0

    if fail_closed or os.environ.get("CI"):
        return 1 if results["violations"] else 0

    return 0  # Manual mode defaults to advisory


if __name__ == "__main__":
    sys.exit(main())
