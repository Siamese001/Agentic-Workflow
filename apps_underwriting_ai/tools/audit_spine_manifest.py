"""CLI: verify ``spine_manifest.yaml`` claims against the source tree.

Runs two checks:
  1. Every ``entry_points`` / ``exit_points`` symbol resolves via import.
  2. :class:`PreMigrationAuditService` finds zero forbidden durable-write
     tokens anywhere under ``apps_underwriting_ai/``.

Exits non-zero on any drift. Suitable for CI wiring.

Usage::

    python -m apps_underwriting_ai.tools.audit_spine_manifest
    python -m apps_underwriting_ai.tools.audit_spine_manifest --json
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from apps_underwriting_ai.services.pre_migration_audit_service import (
    PreMigrationAuditService,
)


_APP_ROOT = Path(__file__).resolve().parent.parent
_SPINE_MANIFEST = _APP_ROOT / "spine_manifest.yaml"


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"spine_manifest not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"spine_manifest must be a mapping, got {type(raw).__name__}")
    return raw


def _resolve_symbol(dotted: str) -> tuple[bool, str]:
    """Return (ok, reason). ``dotted`` may be ``pkg.mod.Class.method`` etc.

    Walks down trying longer module prefixes first, then treats the
    remainder as a dotted attribute chain. This handles all three common
    shapes:
      - ``pkg.module``                    → module
      - ``pkg.module.function``           → module attr
      - ``pkg.module.Class``              → module attr
      - ``pkg.module.Class.method``       → module attr then attr-walk
    """
    if not dotted or "." not in dotted:
        return False, "empty or not dotted"
    parts = dotted.split(".")
    module = None
    module_prefix_len = 0
    # Longest-prefix module import
    for i in range(len(parts), 0, -1):
        candidate = ".".join(parts[:i])
        try:
            module = importlib.import_module(candidate)
            module_prefix_len = i
            break
        except ImportError:
            continue
    if module is None:
        return False, f"no importable module prefix in {dotted!r}"
    current: object = module
    for attr in parts[module_prefix_len:]:
        if not hasattr(current, attr):
            return False, f"object {current!r} has no attribute {attr!r}"
        current = getattr(current, attr)
    return True, "ok"


def audit(
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Run both checks; return a structured report."""
    manifest_path = manifest_path or _SPINE_MANIFEST
    manifest = _load_manifest(manifest_path)
    routes = manifest.get("claimed_routes") or []
    entry_results: list[dict[str, Any]] = []
    exit_results: list[dict[str, Any]] = []
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_type = route.get("type", "<unknown>")
        for ep in route.get("entry_points") or ():
            ok, reason = _resolve_symbol(str(ep))
            entry_results.append(
                {"route": route_type, "symbol": ep, "ok": ok, "reason": reason}
            )
        for ep in route.get("exit_points") or ():
            ok, reason = _resolve_symbol(str(ep))
            exit_results.append(
                {"route": route_type, "symbol": ep, "ok": ok, "reason": reason}
            )

    audit_report = PreMigrationAuditService().audit()

    all_entries_ok = all(r["ok"] for r in entry_results)
    all_exits_ok = all(r["ok"] for r in exit_results)
    passed = all_entries_ok and all_exits_ok and audit_report.passed
    return {
        "passed": passed,
        "manifest_path": str(manifest_path),
        "entry_points": entry_results,
        "exit_points": exit_results,
        "audit_summary": audit_report.summary(),
        "audit_findings": [asdict(f) for f in audit_report.findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="apps_underwriting_ai.tools.audit_spine_manifest",
        description="Validate spine_manifest.yaml claims against source.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=f"Path to spine_manifest.yaml (default: {_SPINE_MANIFEST}).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON report to stdout.",
    )
    args = parser.parse_args(argv)
    try:
        report = audit(args.manifest)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        _render_text(report)

    return 0 if report["passed"] else 1


def _render_text(report: dict[str, Any]) -> None:
    status = "PASS" if report["passed"] else "FAIL"
    print(f"spine_manifest audit: {status}")
    print(f"  manifest: {report['manifest_path']}")
    print(f"  entry_points checked: {len(report['entry_points'])}")
    for r in report["entry_points"]:
        mark = "ok" if r["ok"] else "FAIL"
        print(f"    [{mark}] {r['route']} :: {r['symbol']}  ({r['reason']})")
    print(f"  exit_points checked: {len(report['exit_points'])}")
    for r in report["exit_points"]:
        mark = "ok" if r["ok"] else "FAIL"
        print(f"    [{mark}] {r['route']} :: {r['symbol']}  ({r['reason']})")
    summary = report["audit_summary"]
    print(f"  pre-migration audit: scanned={summary['scanned_files']} findings={summary['finding_count']}")
    for f in report.get("audit_findings", ())[:10]:
        print(f"    - {f['file_path']}:{f['line_number']} token={f['token']}")


if __name__ == "__main__":
    raise SystemExit(main())
