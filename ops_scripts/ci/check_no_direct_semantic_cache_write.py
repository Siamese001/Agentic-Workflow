"""CI gate L6-W1: no direct semantic cache write outside UWG.

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f  W0

Walks the AST of every *.py under apps_rg/runtime/ and agentic_core/ and flags
any import of write_section_to_semantic_cache (or the module apps_rg.cache.r1b_semantic)
from a file that is not in the approved-caller set.

Approved callers:
  - apps_rg/cache/r1b_semantic.py  (the definition itself)
  - any file under apps_rg/cache/   (cache module internals)
  - any file under agentic_core/runtime/uwg/  (UWG admission surface)

All other imports of write_section_to_semantic_cache = violation.

Exit codes:
  0 — clean
  1 — violation(s) found

Bypass: DIRECT_CACHE_WRITE_BYPASS=1
Report: artifacts/ci/direct_semantic_cache_write.json
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_SCAN_ROOTS = [
    REPO_ROOT / "apps_rg" / "runtime",
    REPO_ROOT / "agentic_core",
]

_ALLOWED_PREFIXES = (
    str(REPO_ROOT / "apps_rg" / "cache"),
    str(REPO_ROOT / "agentic_core" / "runtime" / "uwg"),
)

_VIOLATION_NAMES = {"write_section_to_semantic_cache"}
_VIOLATION_MODULES = {"apps_rg.cache.r1b_semantic"}


def _is_allowed(path: Path) -> bool:
    s = str(path)
    return any(s.startswith(prefix) for prefix in _ALLOWED_PREFIXES)


def _check_file(path: Path) -> list[dict]:
    violations: list[dict] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = {alias.name for alias in node.names}
            if module in _VIOLATION_MODULES or names & _VIOLATION_NAMES:
                violations.append({
                    "file": str(path.relative_to(REPO_ROOT)),
                    "line": node.lineno,
                    "type": "ImportFrom",
                    "module": module,
                    "names": sorted(names),
                })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in _VIOLATION_MODULES:
                    violations.append({
                        "file": str(path.relative_to(REPO_ROOT)),
                        "line": node.lineno,
                        "type": "Import",
                        "module": alias.name,
                        "names": [],
                    })
    return violations


def run() -> int:
    if os.environ.get("DIRECT_CACHE_WRITE_BYPASS") == "1":
        print("[L6-W1] DIRECT_CACHE_WRITE_BYPASS=1 — skipping gate", flush=True)
        return 0

    all_violations: list[dict] = []
    files_scanned = 0

    for scan_root in _SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if _is_allowed(py_file):
                continue
            files_scanned += 1
            all_violations.extend(_check_file(py_file))

    report = {
        "gate": "L6-W1",
        "description": "no direct semantic cache write outside UWG",
        "files_scanned": files_scanned,
        "violations": all_violations,
        "status": "PASS" if not all_violations else "FAIL",
    }

    artifacts_dir = REPO_ROOT / "artifacts" / "ci"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "direct_semantic_cache_write.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if all_violations:
        print(f"[L6-W1] FAIL — {len(all_violations)} violation(s):", flush=True)
        for v in all_violations:
            print(f"  {v['file']}:{v['line']}  import {v.get('module','')!r} names={v['names']}",
                  flush=True)
        return 1

    print(f"[L6-W1] PASS — {files_scanned} files scanned, 0 violations", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
