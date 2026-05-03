"""CI gate: forbid new cross-app Python imports between apps_* packages.

Plan: apps-cross-app-precursors-c94c71 Wave 6 (AG-1 Option C).

Scans every .py under `apps_<name>/` and flags any `import apps_<other>` or
`from apps_<other> ...` lines that are NOT in
`config/cross_app_import_allowlist.yaml`.

Cross-app imports are not strictly banned (plan allows `apps_shared` as a
common dependency; apps_* -> apps_shared is always permitted). This gate
catches peer-to-peer couplings like `apps_eval -> apps_exec`, which must be
allowlisted with a reason and expiry.

Exit codes:
    0 -- clean
    1 -- unallowlisted cross-app import detected OR expired allowlist entry
    2 -- config malformed
"""

from __future__ import annotations

import argparse
import ast
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "config" / "cross_app_import_allowlist.yaml"

# apps_shared is a shared-contracts surface — apps_* -> apps_shared is always allowed.
SHARED_TARGETS = {"apps_shared", "apps_common"}


def _apps_packages() -> list[str]:
    return sorted(
        p.name for p in REPO_ROOT.iterdir()
        if p.is_dir() and p.name.startswith("apps_")
    )


def _load_allowlist() -> list[dict]:
    if not ALLOWLIST_PATH.is_file():
        return []
    raw = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
    entries = raw.get("allowed_imports") or []
    if not isinstance(entries, list):
        raise ValueError("allowed_imports must be a list")
    return entries


def _allowlist_index(entries: list[dict]) -> dict[tuple[str, str], dict]:
    """Keyed by (source_module, target_package)."""
    idx: dict[tuple[str, str], dict] = {}
    today = date.today()
    for entry in entries:
        src = entry.get("source", "")
        tgt = entry.get("target", "")
        reason = (entry.get("reason") or "").strip()
        expires_raw = entry.get("expires", "")
        if not src or not tgt or not reason:
            raise ValueError(
                f"Allowlist entry missing source/target/reason: {entry!r}"
            )
        try:
            expires_date = datetime.strptime(expires_raw, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(
                f"Allowlist entry has malformed expires: {entry!r}"
            ) from exc
        if expires_date < today:
            raise ValueError(
                f"Allowlist entry EXPIRED on {expires_date}: {src} -> {tgt}"
            )
        idx[(src, tgt)] = entry
    return idx


def _module_path(py_file: Path) -> str:
    rel = py_file.relative_to(REPO_ROOT).with_suffix("")
    parts = [p for p in rel.parts if p != "__init__"]
    return ".".join(parts)


def _collect_imports(py_file: Path) -> list[tuple[str, int]]:
    """Return list of (top_level_package, lineno) from a python file."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".", 1)[0]
                out.append((top, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                top = node.module.split(".", 1)[0]
                out.append((top, node.lineno))
    return out


def scan() -> tuple[list[dict], list[str]]:
    """Return (violations, errors). Empty lists = clean."""
    errors: list[str] = []
    try:
        entries = _load_allowlist()
        allow = _allowlist_index(entries)
    except ValueError as exc:
        return [], [f"Allowlist malformed: {exc}"]

    apps = _apps_packages()
    violations: list[dict] = []
    for app in apps:
        app_dir = REPO_ROOT / app
        for py_file in app_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts or "tests" in py_file.parts:
                continue
            src_mod = _module_path(py_file)
            for imp_top, lineno in _collect_imports(py_file):
                # apps_shared / apps_common always allowed
                if imp_top in SHARED_TARGETS:
                    continue
                # self-imports fine
                if imp_top == app:
                    continue
                # non-apps imports fine
                if not imp_top.startswith("apps_"):
                    continue
                # peer apps_* -> apps_*: must be allowlisted
                if (src_mod, imp_top) not in allow:
                    violations.append(
                        {
                            "source_module": src_mod,
                            "source_file": str(
                                py_file.relative_to(REPO_ROOT)
                            ).replace("\\", "/"),
                            "target_package": imp_top,
                            "lineno": lineno,
                        }
                    )
    return violations, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit JSON violations report"
    )
    args = parser.parse_args(argv)

    violations, errors = scan()
    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    if args.json:
        import json as _json

        print(_json.dumps(violations, indent=2))

    if violations:
        print(
            f"FAIL: {len(violations)} unallowlisted cross-app import(s) detected:",
            file=sys.stderr,
        )
        for v in violations:
            print(
                f"  {v['source_file']}:{v['lineno']}  "
                f"{v['source_module']} -> {v['target_package']}",
                file=sys.stderr,
            )
        print(
            "\nAdd an entry to config/cross_app_import_allowlist.yaml if the "
            "coupling is sanctioned, or refactor to remove the import.",
            file=sys.stderr,
        )
        return 1

    print("OK: no unallowlisted cross-app imports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
