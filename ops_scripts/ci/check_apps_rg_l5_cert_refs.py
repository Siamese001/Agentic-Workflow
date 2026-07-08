#!/usr/bin/env python3
"""CI gate: apps_rg L5 certification refs (GAP-009).

Scans governed apps_rg runtime surfaces for ``APPS_RG_*_CERT_REF`` assignments,
verifies each value is a non-empty string (``verify_certification_ref``), and
that all discovered values are unique.

Fail-closed in CI or via ``APPS_RG_L5_CERT_REFS_FAIL_CLOSED=1``.
``APPS_RG_L5_CERT_REFS_BYPASS=1`` is forbidden in CI/fail-closed mode.
"""
from __future__ import annotations

import ast
import argparse
import os
import re
import sys
from pathlib import Path

from agentic_core.L5_safety.contracts.verify import verify_certification_ref

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (
    REPO_ROOT / "apps_rg" / "runtime" / "bindings",
    REPO_ROOT / "apps_rg" / "runtime" / "spine",
    REPO_ROOT / "apps_rg" / "runtime" / "l5",
)
_NAME_RE = re.compile(r"^APPS_RG_[A-Z0-9_]+_CERT_REF$")


def _string_value(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collect_refs(tree: ast.AST) -> list[tuple[str, str, int]]:
    out: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        name: str | None = None
        val_node: ast.expr | None = None
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            name = node.targets[0].id
            val_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            val_node = node.value
        if not name or not _NAME_RE.match(name):
            continue
        s = _string_value(val_node)
        if s is None:
            continue
        out.append((name, s, getattr(node, "lineno", 0)))
    return out


def _iter_python_files(roots: tuple[Path, ...]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".py":
            files.append(root)
        elif root.is_dir():
            files.extend(path for path in root.rglob("*.py") if path.is_file())
    return sorted(set(files))


def _ci_mode() -> bool:
    return os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra-path", action="append", default=[])
    args = parser.parse_args(argv)

    fail_closed = os.getenv("APPS_RG_L5_CERT_REFS_FAIL_CLOSED") == "1" or _ci_mode()

    if os.getenv("APPS_RG_L5_CERT_REFS_BYPASS") == "1":
        if fail_closed:
            print("ERROR: APPS_RG_L5_CERT_REFS_BYPASS=1 is forbidden in CI/fail-closed mode")
            return 1
        print("WARNING: APPS-RG-L5-CREFS bypassed via APPS_RG_L5_CERT_REFS_BYPASS=1")
        return 0

    roots = SCAN_ROOTS + tuple((REPO_ROOT / p).resolve() for p in args.extra_path)

    errors: list[str] = []
    all_pairs: list[tuple[str, str, str, int]] = []  # file, name, value, line

    files = _iter_python_files(roots)
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            errors.append(f"SYNTAX_ERROR {rel}: {exc}")
            continue
        for name, value, lineno in _collect_refs(tree):
            all_pairs.append((rel, name, value, lineno))
            if not verify_certification_ref(value):
                errors.append(
                    f"INVALID_REF {rel}:{lineno} {name}={value!r} "
                    "(verify_certification_ref failed)"
                )

    values = [p[2] for p in all_pairs]
    dup_vals = {v for v in values if values.count(v) > 1}
    if dup_vals:
        for rel, name, value, lineno in all_pairs:
            if value in dup_vals:
                errors.append(f"DUPLICATE_VALUE {rel}:{lineno} {name}={value!r}")

    if not all_pairs:
        errors.append("NO_CERT_REFS_FOUND expected APPS_RG_*_CERT_REF in governed runtime paths")

    print(
        f"[APPS-RG-L5-CREFS] scanned {len(files)} file(s): {len(all_pairs)} ref(s), "
        f"{len(errors)} issue(s)"
    )
    if errors:
        for e in errors:
            print(f"  ERROR  {e}")
        if fail_closed:
            print("[APPS-RG-L5-CREFS] fail-closed - exiting 1")
            return 1
        print(
            "[APPS-RG-L5-CREFS] advisory - exiting 0 "
            "(set APPS_RG_L5_CERT_REFS_FAIL_CLOSED=1 to enforce)"
        )
        return 0

    print("[APPS-RG-L5-CREFS] all apps_rg L5 cert refs OK - gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
