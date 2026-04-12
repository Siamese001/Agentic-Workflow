#!/usr/bin/env python3
"""
AST-based Test Collection Tool - Replaces pytest+grep with unified AST parsing.

Implements the ADG vs AST Reconciliation Architecture:
- Phase 1: ADG identifies suspect files (structural topology)
- Phase 2: AST execution persona reconciles false positives/negatives
- Phase 3: Deterministic truth via verified C0 context

Compliance: Windsurf Constitutional Rule §4.3 - No grep/regex for structural logic.
"""

import ast
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestType(Enum):
    """Test classification per ADG vs AST reconciliation."""

    STRUCTURAL_ONLY = "structural_only"  # ADG sees, AST disproves (false positive)
    BEHAVIORAL = "behavioral"  # Both ADG and AST see (true positive)
    DYNAMIC_ONLY = "dynamic_only"  # AST sees, ADG misses (false negative)


@dataclass
class TestNode:
    """AST-derived test node with reconciliation metadata."""

    node_id: str
    file_path: str
    function_name: str
    is_skipped: bool
    skip_reason: str
    test_type: TestType
    line_number: int
    has_logic: bool


class ASTTestCollector:
    """Unified AST-based test collection with ADG reconciliation."""

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"

    def collect_all_tests(self) -> list[TestNode]:
        """Collect all test nodes using pure AST parsing."""
        test_nodes = []

        for test_file in self.tests_dir.rglob("test_*.py"):
            try:
                nodes = self._parse_test_file(test_file)
                test_nodes.extend(nodes)
            except (SyntaxError, OSError) as e:
                print(f"Warning: Could not parse {test_file}: {e}", file=sys.stderr)
                continue

        return test_nodes

    def _parse_test_file(self, file_path: Path) -> list[TestNode]:
        """Parse a single test file using AST."""
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))

        nodes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("test_"):
                    continue

                test_node = self._create_test_node(file_path, node, source)
                nodes.append(test_node)

        return nodes

    def _create_test_node(self, file_path: Path, node: ast.FunctionDef, source: str) -> TestNode:
        """Create TestNode from AST function definition."""
        rel_path = file_path.relative_to(self.repo_root).as_posix()
        node_id = f"{rel_path}::{node.name}"

        # Analyze decorators for skip markers
        is_skipped, skip_reason = self._analyze_skip_decorators(node)

        # Determine if function has actual logic (not just pass/placeholder)
        has_logic = self._has_function_logic(node, source)

        # Classify test type (will be refined with ADG data)
        test_type = TestType.BEHAVIORAL if has_logic else TestType.STRUCTURAL_ONLY

        return TestNode(
            node_id=node_id,
            file_path=rel_path,
            function_name=node.name,
            is_skipped=is_skipped,
            skip_reason=skip_reason,
            test_type=test_type,
            line_number=node.lineno,
            has_logic=has_logic,
        )

    def _analyze_skip_decorators(self, node: ast.FunctionDef) -> tuple[bool, str]:
        """Analyze AST decorators for skip markers."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == "skip":
                    return True, "@pytest.mark.skip"
                elif decorator.id == "skipif":
                    return True, "@pytest.mark.skipif"

            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id == "skip":
                        return True, "@pytest.mark.skip()"
                    elif decorator.func.id == "skipif":
                        return True, "@pytest.mark.skipif(...)"

            elif isinstance(decorator, ast.Attribute):
                if hasattr(decorator, "attr"):
                    if decorator.attr == "skip":
                        return True, "@pytest.mark.skip"
                    elif decorator.attr == "skipif":
                        return True, "@pytest.mark.skipif(...)"

        return False, ""

    def _has_function_logic(self, node: ast.FunctionDef, source: str) -> bool:
        """Determine if function has actual logic beyond placeholders."""
        # Check for non-trivial statements
        logic_indicators = [
            ast.Assert,
            ast.Raise,
            ast.Return,
            ast.Yield,
            ast.YieldFrom,
            ast.For,
            ast.While,
            ast.If,
            ast.Try,
            ast.With,
            ast.AsyncWith,
            ast.Call,
            ast.Assign,
            ast.AnnAssign,
            ast.AugAssign,
            ast.NamedExpr,
        ]

        for child in ast.walk(node):
            if type(child) in logic_indicators:
                # Special case: skip placeholder patterns
                if self._is_placeholder_logic(child):
                    continue
                return True

        return False

    def _is_placeholder_logic(self, node: ast.AST) -> bool:
        """Check if AST node is just placeholder logic."""
        if isinstance(node, ast.Pass):
            return True
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if node.value.value is None or node.value.value in ("TODO", "FIXME", "Not implemented"):
                return True
        elif isinstance(node, ast.Raise):
            if (
                isinstance(node.exc, ast.Call)
                and isinstance(node.exc.func, ast.Name)
                and node.exc.func.id == "NotImplementedError"
            ):
                return True
        return False

    def reconcile_with_adg(self, test_nodes: list[TestNode], adg_suspect_files: set[str]) -> list[TestNode]:
        """Phase 2: AST execution persona reconciles ADG findings."""
        reconciled = []

        for node in test_nodes:
            # ADG Scenario A: Structural file with no actual test logic
            if node.file_path in adg_suspect_files and not node.has_logic:
                node.test_type = TestType.STRUCTURAL_ONLY

            # ADG Scenario B: Dynamic test that ADG missed
            elif node.file_path not in adg_suspect_files and node.has_logic:
                node.test_type = TestType.DYNAMIC_ONLY

            # Normal case: Both see the test
            else:
                node.test_type = TestType.BEHAVIORAL

            reconciled.append(node)

        return reconciled

    def generate_deterministic_truth(self, reconciled_nodes: list[TestNode]) -> dict[str, Any]:
        """Phase 3: Generate verified C0 context for enhancement targeting."""
        summary = {
            "total_tests": len(reconciled_nodes),
            "by_type": {
                "structural_only": 0,
                "behavioral": 0,
                "dynamic_only": 0,
            },
            "skipped": 0,
            "active": 0,
            "target_files": set(),
            "suspect_files": set(),
        }

        for node in reconciled_nodes:
            summary["by_type"][node.test_type.value] += 1

            if node.is_skipped:
                summary["skipped"] += 1
            else:
                summary["active"] += 1

            if node.test_type in [TestType.BEHAVIORAL, TestType.DYNAMIC_ONLY]:
                summary["target_files"].add(node.file_path)
            else:
                summary["suspect_files"].add(node.file_path)

        # Convert sets to lists for JSON serialization
        summary["target_files"] = sorted(summary["target_files"])
        summary["suspect_files"] = sorted(summary["suspect_files"])

        return summary

    def print_summary(self, summary: dict[str, Any]) -> None:
        """Print collection summary in Windsurf-compatible format."""
        print("AST Test Collection Results:")
        print(f"  Total tests: {summary['total_tests']}")
        print(f"  Active tests: {summary['active']}")
        print(f"  Skipped tests: {summary['skipped']}")
        print()
        print("By Type (ADG vs AST Reconciliation):")
        print(f"  Behavioral tests (both see): {summary['by_type']['behavioral']}")
        print(f"  Dynamic-only tests (AST sees): {summary['by_type']['dynamic_only']}")
        print(f"  Structural-only files (ADG sees): {summary['by_type']['structural_only']}")
        print()
        print("Phase 3 Deterministic Truth:")
        print(f"  Target files for enhancement: {len(summary['target_files'])}")
        print(f"  Suspect files to discard: {len(summary['suspect_files'])}")


def main() -> int:
    """CLI entry point for AST test collection."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ast_test_collector",
        description="AST-based test collection with ADG reconciliation",
    )
    parser.add_argument(
        "--adg-suspects",
        nargs="*",
        help="ADG-identified suspect files for Phase 2 reconciliation",
    )
    parser.add_argument(
        "--json-output",
        help="Write detailed results to JSON file",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only summary, not individual test details",
    )

    args = parser.parse_args()

    collector = ASTTestCollector()

    # Phase 1: Collect all tests via AST
    print("Phase 1: AST-based test collection...", file=sys.stderr)
    test_nodes = collector.collect_all_tests()

    # Phase 2: Reconcile with ADG data if provided
    adg_suspects = set(args.adg_suspects or [])
    if adg_suspects:
        print(f"Phase 2: ADG reconciliation with {len(adg_suspects)} suspects...", file=sys.stderr)
        reconciled_nodes = collector.reconcile_with_adg(test_nodes, adg_suspects)
    else:
        reconciled_nodes = test_nodes

    # Phase 3: Generate deterministic truth
    print("Phase 3: Generating deterministic truth...", file=sys.stderr)
    summary = collector.generate_deterministic_truth(reconciled_nodes)

    # Output results
    if not args.summary_only:
        print("\nDetailed Test Nodes:")
        for node in reconciled_nodes:
            status = "SKIPPED" if node.is_skipped else "ACTIVE"
            print(f"  {node.node_id} [{status}] ({node.test_type.value})")

    print()
    collector.print_summary(summary)

    # Write JSON output if requested
    if args.json_output:
        output_data = {
            "summary": summary,
            "tests": [
                {
                    "node_id": n.node_id,
                    "file_path": n.file_path,
                    "function_name": n.function_name,
                    "is_skipped": n.is_skipped,
                    "skip_reason": n.skip_reason,
                    "test_type": n.test_type.value,
                    "line_number": n.line_number,
                    "has_logic": n.has_logic,
                }
                for n in reconciled_nodes
            ],
        }

        output_path = Path(args.json_output)
        output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        print(f"\nDetailed results written to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
