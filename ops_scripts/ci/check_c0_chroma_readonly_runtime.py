"""CI gate: check_c0_chroma_readonly_runtime.py

Plan 03 W5.3 — Scan apps_rg runtime/cache/tools/providers paths for Chroma
mutation calls. Only read-only operations (query, get, peek) are permitted.

Fail-closed via: APPS_RG_CHROMA_RO_GATE_FAIL_CLOSED=1
Bypass via:      APPS_RG_CHROMA_RO_GATE_BYPASS=1
Report:          artifacts/ci/apps_rg_chroma_ro_gate.json
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_PATHS = [
    "apps_rg/runtime",
    "apps_rg/cache",
    "apps_rg/tools",
    "apps_rg/providers",
    "apps_rg/runtime/bindings",
]

FORBIDDEN_CHROMA_METHODS = {
    # 'add' and 'update' are excluded — too ambiguous in AST scan
    # (set.add, hashlib.update, dict.update are false positives).
    # Chroma-specific add/update are caught by import analysis in check_no_direct_l4_writer_imports.py.
    "upsert",
    "delete",
    "create_collection",
    "get_or_create_collection",
    "persist",
    "reset",
    "delete_collection",
}

ALLOWED_CHROMA_METHODS = {"query", "get", "peek", "count"}


def _scan_file(filepath: Path) -> list[dict]:
    violations = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):
        return violations

    rel = filepath.relative_to(REPO_ROOT).as_posix()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in FORBIDDEN_CHROMA_METHODS:
                violations.append({
                    "file": rel,
                    "line": node.lineno,
                    "method": method,
                    "severity": "ERROR",
                    "reason": f"Chroma mutation '{method}' forbidden in runtime — read-only (query/get/peek) only",
                })

    return violations


def main() -> int:
    bypass = os.environ.get("APPS_RG_CHROMA_RO_GATE_BYPASS", "0") == "1"
    fail_closed = os.environ.get("APPS_RG_CHROMA_RO_GATE_FAIL_CLOSED", "0") == "1"

    if bypass:
        print("BYPASS_RECEIPT: gate=check_c0_chroma_readonly_runtime reason=APPS_RG_CHROMA_RO_GATE_BYPASS=1")
        return 0

    all_violations: list[dict] = []
    scanned: list[str] = []

    seen_paths: set[Path] = set()
    for scan_path in SCAN_PATHS:
        scan_root = REPO_ROOT / scan_path
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if py_file in seen_paths:
                continue
            seen_paths.add(py_file)
            scanned.append(py_file.relative_to(REPO_ROOT).as_posix())
            all_violations.extend(_scan_file(py_file))

    report = {
        "gate": "check_c0_chroma_readonly_runtime",
        "scanned_count": len(scanned),
        "violation_count": len(all_violations),
        "violations": all_violations,
    }

    out_dir = REPO_ROOT / "artifacts" / "ci"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "apps_rg_chroma_ro_gate.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if all_violations:
        print(f"[APPS-CHROMA-RO] ERROR: {len(all_violations)} Chroma mutation violation(s) found")
        for v in all_violations:
            print(f"  {v['file']}:{v['line']} — {v['method']}")
        if fail_closed:
            return 1
        print("[APPS-CHROMA-RO] Advisory mode — set APPS_RG_CHROMA_RO_GATE_FAIL_CLOSED=1 to enforce")
        return 0

    print(f"[APPS-CHROMA-RO] OK — zero Chroma mutation calls in {len(scanned)} scanned files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
