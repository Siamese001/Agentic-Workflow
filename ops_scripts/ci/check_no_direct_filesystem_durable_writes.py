"""CI gate: check_no_direct_filesystem_durable_writes.py

Plan 03 W5.1 — Scan apps_rg runtime paths for direct filesystem durable writes.
Uses allowlist semantics to distinguish forbidden durable runtime writes from
sanctioned sandbox/temp/test/ci writes.

Fail-closed via: APPS_RG_FS_WRITE_GATE_FAIL_CLOSED=1
Bypass via:      APPS_RG_FS_WRITE_GATE_BYPASS=1
Report:          artifacts/ci/apps_rg_fs_write_gate.json
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_RUNTIME_PATHS = [
    "apps_rg/runtime",
    "apps_rg/cache",
    "apps_rg/providers",
]

FORBIDDEN_WRITE_PATTERNS = [
    "write_text",
    "write_bytes",
    "pickle",
    "shutil",
]

FORBIDDEN_OPEN_MODES = {"w", "wb", "a", "ab", "x"}

ALLOWED_PATHS = [
    "tests/",
    "artifacts/ci/",
    "artifacts/cursor/",
    "agentic_core/L4_state/uwg/",
    ".claude/plans/",
    "docs/",
]


def _is_allowlisted(filepath: Path) -> bool:
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    return any(rel.startswith(a) for a in ALLOWED_PATHS)


def _scan_file(filepath: Path) -> list[dict]:
    violations = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):
        return violations

    rel = filepath.relative_to(REPO_ROOT).as_posix()

    for node in ast.walk(tree):
        # Check attribute calls like path.write_text(...), path.write_bytes(...)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                if attr in ("write_text", "write_bytes"):
                    violations.append({
                        "file": rel,
                        "line": node.lineno,
                        "pattern": attr,
                        "severity": "ERROR",
                    })
                # pickle.dump
                if attr in ("dump",) and isinstance(node.func.value, ast.Name):
                    if node.func.value.id in ("pickle",):
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "pattern": "pickle.dump",
                            "severity": "ERROR",
                        })
                # shutil.copy / shutil.move
                if attr in ("copy", "copy2", "move", "copytree") and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == "shutil":
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "pattern": f"shutil.{attr}",
                            "severity": "ERROR",
                        })
            # json.dump(data, f) — open file handle write
            if isinstance(node.func, ast.Attribute) and node.func.attr == "dump":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "json":
                    if len(node.args) >= 2:
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "pattern": "json.dump",
                            "severity": "ERROR",
                        })

        # open(..., 'w') / open(..., 'wb') / open(..., 'a')
        if isinstance(node, ast.Call):
            func = node.func
            is_open = (
                (isinstance(func, ast.Name) and func.id == "open")
                or (isinstance(func, ast.Attribute) and func.attr == "open")
            )
            if is_open and len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                    if any(m in mode_arg.value for m in FORBIDDEN_OPEN_MODES):
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "pattern": f"open(..., '{mode_arg.value}')",
                            "severity": "ERROR",
                        })
            # also check keyword mode=
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    if any(m in str(kw.value.value) for m in FORBIDDEN_OPEN_MODES):
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "pattern": f"open(mode='{kw.value.value}')",
                            "severity": "ERROR",
                        })

    return violations


def main() -> int:
    bypass = os.environ.get("APPS_RG_FS_WRITE_GATE_BYPASS", "0") == "1"
    fail_closed = os.environ.get("APPS_RG_FS_WRITE_GATE_FAIL_CLOSED", "0") == "1"

    if bypass:
        print("BYPASS_RECEIPT: gate=check_no_direct_filesystem_durable_writes reason=APPS_RG_FS_WRITE_GATE_BYPASS=1")
        return 0

    all_violations: list[dict] = []

    for runtime_path in FORBIDDEN_RUNTIME_PATHS:
        scan_root = REPO_ROOT / runtime_path
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if _is_allowlisted(py_file):
                continue
            all_violations.extend(_scan_file(py_file))

    report = {
        "gate": "check_no_direct_filesystem_durable_writes",
        "scanned_paths": FORBIDDEN_RUNTIME_PATHS,
        "violation_count": len(all_violations),
        "violations": all_violations,
    }

    out_dir = REPO_ROOT / "artifacts" / "ci"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "apps_rg_fs_write_gate.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if all_violations:
        print(f"[APPS-FS-WRITE] ERROR: {len(all_violations)} durable filesystem write violation(s) found")
        for v in all_violations:
            print(f"  {v['file']}:{v['line']} — {v['pattern']}")
        if fail_closed:
            return 1
        print("[APPS-FS-WRITE] Advisory mode — set APPS_RG_FS_WRITE_GATE_FAIL_CLOSED=1 to enforce")
        return 0

    print(f"[APPS-FS-WRITE] OK — zero durable write violations in {FORBIDDEN_RUNTIME_PATHS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
