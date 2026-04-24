"""AST-based skip-site auditor for pytest test files."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Iterable

from tqdm import tqdm


def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return ast.dump(node, annotate_fields=False)


def iter_test_files(root: Path) -> Iterable[Path]:
    yield from sorted(root.rglob("test_*.py"))


def audit_skip_sites(root: Path) -> tuple[list[str], list[str]]:
    out: list[str] = []
    warnings: list[str] = []

    for path in tqdm(list(iter_test_files(root)), desc="Auditing test files", unit="file"):
        try:
            src = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src, filename=str(path))
        except SyntaxError as exc:
            warnings.append(f"SKIP PARSE ERROR|{path}|{exc.lineno}|{exc.msg}")
            continue
        except OSError as exc:
            warnings.append(f"SKIP READ ERROR|{path}|0|{exc}")
            continue

        rel = str(path.relative_to(root))
        for node in tqdm(list(ast.walk(tree)), desc="Walking AST", unit="node", leave=False):
            if not isinstance(node, ast.Call):
                continue

            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "importorskip":
                args = [_safe_unparse(arg) for arg in node.args]
                out.append(f"importorskip|{rel}|{node.lineno}|{args}")
                continue

            if (
                isinstance(func, ast.Attribute)
                and func.attr == "skip"
                and isinstance(func.value, ast.Name)
                and func.value.id == "pytest"
            ):
                raw_args = [_safe_unparse(arg) for arg in node.args]
                reason = raw_args[0].strip("\"'") if raw_args else ""
                out.append(f"pytest.skip|{rel}|{node.lineno}|{reason[:140]}")

    return out, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tests-root",
        type=Path,
        default=Path.cwd() / "tests",
        help="Root directory containing pytest files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd() / "skip_audit.txt",
        help="Destination file for audit results.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tests_root = args.tests_root.resolve()
    output_path = args.output.resolve()

    if not tests_root.exists():
        print(f"CRITICAL: tests root not found: {tests_root}", file=sys.stderr)
        return 1

    results, warnings = audit_skip_sites(tests_root)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(results), encoding="utf-8")
    except OSError as exc:
        print(f"CRITICAL: could not write audit file: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(warning, file=sys.stderr)

    print(f"TOTAL SKIP SITES: {len(results)}")
    if warnings:
        print(f"PARSE/READ WARNINGS: {len(warnings)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
