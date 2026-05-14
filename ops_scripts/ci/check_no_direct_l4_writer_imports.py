"""CI gate: check_no_direct_l4_writer_imports.py

Plan 03 W5.4 — Scan apps_rg/ for direct imports from core L4 write modules.
apps_rg may only import proposal types, CommitRequest, contracts, typed exceptions.
It must NOT import StateStore, DurableWriteGateway.commit, cache/vector writers.

Fail-closed via: APPS_RG_L4_IMPORT_GATE_FAIL_CLOSED=1
Bypass via:      APPS_RG_L4_IMPORT_GATE_BYPASS=1
Report:          artifacts/ci/apps_rg_l4_import_gate.json
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOT = REPO_ROOT / "apps_rg"

FORBIDDEN_MODULE_PATTERNS = [
    "agentic_core.L4_state.state_store",
    "agentic_core.L4_state.durable_write_gateway",
    "agentic_core.L4_state.cache_writer",
    "agentic_core.L4_state.vector_writer",
    "agentic_core.L4_state.archive_writer",
    "agentic_core.L4_state.uwg.commit",
]

FORBIDDEN_NAMES = {
    "StateStore",
    "DurableWriteGateway",
    "CacheWriter",
    "VectorWriter",
    "ArchiveWriter",
    "write_section_to_semantic_cache",
}

ALLOWED_PATTERNS = [
    "agentic_core.L4_state.contracts",
    "agentic_core.L4_state.types",
    "agentic_core.runtime.contracts",
]

EXCLUDED_PATHS = [
    "tests/",
    "apps_rg/_quarantine/",
]


def _is_excluded(filepath: Path) -> bool:
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    return any(rel.startswith(e) for e in EXCLUDED_PATHS)


def _module_is_forbidden(module: str) -> bool:
    if any(module.startswith(a) for a in ALLOWED_PATTERNS):
        return False
    return any(module.startswith(f) for f in FORBIDDEN_MODULE_PATTERNS)


def _scan_file(filepath: Path) -> list[dict]:
    violations = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):
        return violations

    rel = filepath.relative_to(REPO_ROOT).as_posix()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if _module_is_forbidden(module):
                imported_names = [alias.name for alias in node.names]
                violations.append({
                    "file": rel,
                    "line": node.lineno,
                    "import": f"from {module} import {', '.join(imported_names)}",
                    "severity": "ERROR",
                    "reason": "Direct import from core L4 writer module forbidden in apps_rg",
                })
            else:
                for alias in node.names:
                    if alias.name in FORBIDDEN_NAMES:
                        violations.append({
                            "file": rel,
                            "line": node.lineno,
                            "import": f"from {module} import {alias.name}",
                            "severity": "ERROR",
                            "reason": f"Direct import of forbidden writer symbol '{alias.name}'",
                        })

        elif isinstance(node, ast.Import):
            for alias in node.names:
                if _module_is_forbidden(alias.name):
                    violations.append({
                        "file": rel,
                        "line": node.lineno,
                        "import": f"import {alias.name}",
                        "severity": "ERROR",
                        "reason": "Direct import of core L4 writer module forbidden in apps_rg",
                    })

    return violations


def main() -> int:
    bypass = os.environ.get("APPS_RG_L4_IMPORT_GATE_BYPASS", "0") == "1"
    fail_closed = os.environ.get("APPS_RG_L4_IMPORT_GATE_FAIL_CLOSED", "0") == "1"

    if bypass:
        print("BYPASS_RECEIPT: gate=check_no_direct_l4_writer_imports reason=APPS_RG_L4_IMPORT_GATE_BYPASS=1")
        return 0

    all_violations: list[dict] = []

    for py_file in sorted(SCAN_ROOT.rglob("*.py")):
        if _is_excluded(py_file):
            continue
        all_violations.extend(_scan_file(py_file))

    report = {
        "gate": "check_no_direct_l4_writer_imports",
        "scan_root": str(SCAN_ROOT.relative_to(REPO_ROOT)),
        "violation_count": len(all_violations),
        "violations": all_violations,
    }

    out_dir = REPO_ROOT / "artifacts" / "ci"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "apps_rg_l4_import_gate.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if all_violations:
        print(f"[APPS-L4-IMPORT] ERROR: {len(all_violations)} forbidden L4 writer import(s) found")
        for v in all_violations:
            print(f"  {v['file']}:{v['line']} — {v['import']}")
        if fail_closed:
            return 1
        print("[APPS-L4-IMPORT] Advisory mode — set APPS_RG_L4_IMPORT_GATE_FAIL_CLOSED=1 to enforce")
        return 0

    print("[APPS-L4-IMPORT] OK — zero forbidden L4 writer imports in apps_rg/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
