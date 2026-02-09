#!/usr/bin/env python3
"""MRO Diamond Contract Check — CI Gate (Ratchet).

AST-based scan for classes that inherit the same mixin via two paths
(e.g. SubatomicTestingMixin listed explicitly AND inherited via
SovereignBaseAgent).  Such diamonds cause TypeError at import time.

Policy (machine-enforceable per-PR):
  1. count > ceiling  → HARD FAIL (requires MRO_BASELINE_BUMP:<reason>).
  2. count == ceiling → PASS.
  3. count < ceiling  → PASS + INFO recommending baseline update.
     Improvements are never blocked.
  4. Allowlisted entries (with justification string) are tolerated.

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""

from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

SCAN_ROOTS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
]

BASELINE_PATH = "artifacts/consolidation/mro_diamond_baseline.json"

SOVEREIGN_INHERITED_MIXINS = {
    "SubatomicTestingMixin",
    "AtomicExecutionMixin",
}

CARRIER_BASES = {
    "SovereignBaseAgent",
    "AppBase",
    "RGAgentBase",
    "LICAgentBase",
}

# Allowlist: entries here are counted but tolerated.
# Each key is "file:class", value is justification string.
ALLOWLIST: dict[str, str] = {
    # Example: "apps_shared/utils/AppBase.py:AppBase": "AppBase intentionally re-exports mixin for app-layer convenience",
}


def _get_base_names(cls_node: ast.ClassDef) -> list[str]:
    names: list[str] = []
    for base in cls_node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def scan_diamonds(project_root: Path) -> list[dict]:
    """Return list of diamond dicts: {file, line, class, redundant_mixins, carriers}."""
    results: list[dict] = []
    for scan_root in SCAN_ROOTS:
        root_path = project_root / scan_root
        if not root_path.is_dir():
            continue
        for pyfile in root_path.rglob("*.py"):
            if "__pycache__" in str(pyfile):
                continue
            try:
                source = pyfile.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(pyfile))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                bases = set(_get_base_names(node))
                has_carrier = bool(bases & CARRIER_BASES)
                dupes = bases & SOVEREIGN_INHERITED_MIXINS
                if has_carrier and dupes:
                    rel = str(pyfile.relative_to(project_root)).replace("\\", "/")
                    results.append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "class": node.name,
                            "redundant_mixins": sorted(dupes),
                            "carriers": sorted(bases & CARRIER_BASES),
                        },
                    )
    return results


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    baseline_file = project_root / BASELINE_PATH

    # Load baseline ceiling
    if not baseline_file.is_file():
        print(f"FAIL: baseline not found: {BASELINE_PATH}", file=sys.stderr)
        return 1
    baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    ceiling = baseline["total"]

    # Scan current diamonds
    diamonds = scan_diamonds(project_root)
    count = len(diamonds)

    # Separate allowlisted
    allowlisted = 0
    non_allowlisted = []
    for d in diamonds:
        key = f"{d['file']}:{d['class']}"
        if key in ALLOWLIST:
            allowlisted += 1
        else:
            non_allowlisted.append(d)

    delta = count - ceiling
    print("MRO Diamond Contract Check (ratcheting):")
    print(f"  scanned={len(SCAN_ROOTS)} roots")
    print(f"  count={count}  ceiling={ceiling}  delta={delta}")
    print(f"  allowlisted={allowlisted}  non_allowlisted={len(non_allowlisted)}")

    errors: list[str] = []

    # Rule 1: Fail if count exceeds ceiling
    if count > ceiling:
        commit_msg = os.environ.get("COMMIT_MESSAGE", "")
        if "MRO_BASELINE_BUMP:" in commit_msg:
            print(f"WARN: count {count} > ceiling {ceiling} but MRO_BASELINE_BUMP tag present")
        else:
            errors.append(
                f"count {count} exceeds baseline ceiling {ceiling} (+{delta})",
            )
            for d in non_allowlisted:
                errors.append(
                    f"  {d['file']}:{d['line']} class {d['class']} "
                    f"{d['redundant_mixins']} with {d['carriers']}",
                )

    if errors:
        print(f"FAIL: {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    # Rule 3: count < ceiling → debt was reduced. Always PASS.
    # Improvements must never be blocked.
    if count < ceiling:
        commit_msg = os.environ.get("COMMIT_MESSAGE", "")
        tag_present = "MRO_BASELINE_LOWERED:" in commit_msg
        improvement = ceiling - count
        print(
            f"PASS: {count} MRO diamonds < ceiling {ceiling} (improved by {improvement})",
        )
        print(f"  old_ceiling={ceiling}  new_count={count}  delta=-{improvement}")
        print(
            f"  Update baseline: edit {BASELINE_PATH} "
            f'set "total": {count} and remove {improvement} resolved entries',
        )
        if tag_present:
            print("  (MRO_BASELINE_LOWERED tag detected)")
        return 0

    # Rule 2: count == ceiling → PASS
    print(f"PASS: {count} MRO diamonds == baseline ceiling {ceiling}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
