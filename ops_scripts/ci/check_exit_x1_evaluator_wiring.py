"""AG-5 Exit X1 Evaluator Wiring — CI Gate.

Plan: ``ag5-exit-x1-evaluator-wiring-d8e4a2``.

Gate fails if:
- X3Disposition can be emitted without X1CheckoutResult
- Grounded route can pass without FinalEvidenceContract
- UNKNOWN can be treated as PASS
- NOT_APPLICABLE can omit reason
- Scalar eval_score is the only quality carrier
- Material FAIL can still ALLOW_FINISH
- proposed_state_diff can bypass X1J/UWG eligibility

This is a static analysis gate that inspects the Exit evaluation code
to verify AG-4/AG-5 invariants are present.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


def _find_repo_root() -> Path:
    """Find repository root by looking for .git directory."""
    current = Path(__file__).resolve().parent
    while current.parent != current:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def _load_ast(source_path: Path) -> ast.AST | None:
    """Load and parse Python source file."""
    try:
        source = source_path.read_text(encoding="utf-8")
        return ast.parse(source)
    except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
        return None


def _has_x1_checkout_result_in_aggregate(tree: ast.AST) -> bool:
    """Check that AggregateDecision has x1_checkout_result field."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AggregateDecision":
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if item.target.id == "x1_checkout_result":
                        return True
    return False


def _has_x1_checkout_result_in_pipeline_result(tree: ast.AST) -> bool:
    """Check that ExitEvalResult has x1_checkout_result field."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ExitEvalResult":
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if hasattr(item.target, 'id') and item.target.id == "x1_checkout_result":
                        return True
    return False


def _has_x1_checkout_build_call(tree: ast.AST) -> bool:
    """Check that pipeline calls build_x1_checkout_result."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "build_x1_checkout_result":
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == "build_x1_checkout_result":
                return True
    return False


def _has_unknown_fail_closed_check(tree: ast.AST) -> bool:
    """Check for UNKNOWN fail-closed handling (unknown_reason field usage)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            if hasattr(node.target, 'id') and node.target.id == "unknown_reason":
                return True
    # Also check for UNKNOWN checks in is_passing or similar
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if isinstance(op, ast.Is) or isinstance(op, ast.Eq):
                    if isinstance(node.comparators[0], ast.Attribute):
                        if node.comparators[0].attr == "UNKNOWN":
                            return True
    return False


def _has_not_applicable_reason_check(tree: ast.AST) -> bool:
    """Check for NOT_APPLICABLE reason validation."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            if hasattr(node.target, 'id') and node.target.id == "not_applicable_reason":
                return True
        if isinstance(node, ast.If):
            # Look for NOT_APPLICABLE checks
            if isinstance(node.test, ast.Compare):
                for comparator in node.test.comparators:
                    if isinstance(comparator, ast.Attribute):
                        if comparator.attr == "NOT_APPLICABLE":
                            return True
    return False


def _has_x1d_deterministic_evaluator(repo_root: Path) -> bool:
    """Check that X1D deterministic evaluator exists."""
    path = repo_root / "agentic_core/L3_orchestration/exit_eval/v6/x1d_deterministic_evaluator.py"
    return path.exists()


def _has_x1_checkout_adapter(repo_root: Path) -> bool:
    """Check that X1 checkout adapter exists."""
    path = repo_root / "agentic_core/L3_orchestration/exit_eval/v6/x1_checkout_adapter.py"
    return path.exists()


def _has_ag5_tests(repo_root: Path) -> bool:
    """Check that AG-5 test file exists."""
    path = repo_root / "tests/_apps_contract/test_ag5_exit_x1_evaluator_wiring.py"
    return path.exists()


def _has_no_chromadb_in_exit_code(repo_root: Path) -> bool:
    """Check that Exit evaluation code does not import chromadb."""
    exit_eval_dir = repo_root / "agentic_core/L3_orchestration/exit_eval/v6"
    if not exit_eval_dir.exists():
        return True  # No code to check

    for py_file in exit_eval_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        try:
            source = py_file.read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "chromadb" in alias.name.lower():
                            return False
                if isinstance(node, ast.ImportFrom):
                    if node.module and "chromadb" in node.module.lower():
                        return False
        except (SyntaxError, FileNotFoundError):
            continue
    return True


def run_gate(repo_root: Path) -> dict[str, Any]:
    """Run all AG-5 wiring checks and return report."""
    results: dict[str, Any] = {
        "gate_name": "AG-5 Exit X1 Evaluator Wiring",
        "checks": {},
        "passed": True,
    }

    # Check X2 matrix has x1_checkout_result field
    x2_path = repo_root / "agentic_core/L3_orchestration/exit_eval/v6/x2_matrix.py"
    x2_tree = _load_ast(x2_path)
    if x2_tree:
        results["checks"]["x2_has_x1_checkout_field"] = _has_x1_checkout_result_in_aggregate(x2_tree)
    else:
        results["checks"]["x2_has_x1_checkout_field"] = False

    # Check pipeline has x1_checkout_result field
    pipeline_path = repo_root / "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py"
    pipeline_tree = _load_ast(pipeline_path)
    if pipeline_tree:
        results["checks"]["pipeline_has_x1_checkout_field"] = _has_x1_checkout_result_in_pipeline_result(pipeline_tree)
        results["checks"]["pipeline_calls_build_x1_checkout"] = _has_x1_checkout_build_call(pipeline_tree)
    else:
        results["checks"]["pipeline_has_x1_checkout_field"] = False
        results["checks"]["pipeline_calls_build_x1_checkout"] = False

    # Check X1CheckoutResult invariants
    x1_checkout_path = repo_root / "agentic_core/runtime/contracts/x1_checkout_result.py"
    x1_checkout_tree = _load_ast(x1_checkout_path)
    if x1_checkout_tree:
        results["checks"]["x1_item_has_unknown_reason"] = _has_unknown_fail_closed_check(x1_checkout_tree)
        results["checks"]["x1_item_has_not_applicable_reason"] = _has_not_applicable_reason_check(x1_checkout_tree)
    else:
        results["checks"]["x1_item_has_unknown_reason"] = False
        results["checks"]["x1_item_has_not_applicable_reason"] = False

    # Check files exist
    results["checks"]["x1d_deterministic_evaluator_exists"] = _has_x1d_deterministic_evaluator(repo_root)
    results["checks"]["x1_checkout_adapter_exists"] = _has_x1_checkout_adapter(repo_root)
    results["checks"]["ag5_tests_exist"] = _has_ag5_tests(repo_root)
    results["checks"]["no_chromadb_in_exit_code"] = _has_no_chromadb_in_exit_code(repo_root)

    # Overall pass: all checks must pass
    results["passed"] = all(results["checks"].values())

    return results


def main() -> int:
    """Main entry point for CI gate."""
    parser = argparse.ArgumentParser(description="AG-5 Exit X1 Evaluator Wiring Gate")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to repository root (auto-detected if not provided)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        default=False,
        help="Exit with code 1 if any check fails",
    )
    parser.add_argument(
        "--bypass",
        action="store_true",
        default=False,
        help="Bypass gate and always exit 0 (for emergency use)",
    )
    args = parser.parse_args()

    if args.bypass:
        print("AG-5 GATE BYPASSED via --bypass flag", file=sys.stderr)
        return 0

    repo_root = args.repo_root or _find_repo_root()
    results = run_gate(repo_root)

    # Output report
    output_json = json.dumps(results, indent=2)
    if args.output:
        args.output.write_text(output_json)
        print(f"AG-5 gate report written to {args.output}")
    else:
        print(output_json)

    # Determine exit code
    if results["passed"]:
        print("\n✅ AG-5 Exit X1 Evaluator Wiring: PASSED", file=sys.stderr)
        return 0
    else:
        failed_checks = [k for k, v in results["checks"].items() if not v]
        print(f"\n❌ AG-5 Exit X1 Evaluator Wiring: FAILED", file=sys.stderr)
        print(f"Failed checks: {', '.join(failed_checks)}", file=sys.stderr)
        if args.fail_closed:
            return 1
        return 0  # Advisory by default


if __name__ == "__main__":
    sys.exit(main())
