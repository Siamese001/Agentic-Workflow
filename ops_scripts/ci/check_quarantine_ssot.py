"""Narrow CI gate: quarantine SSOT vs disk (plan apps-rg-quarantine-ssot-fanin-delete-c7e4a1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

REMOVED_PATHS = (
    "apps_rg/reasoning",
    "apps_rg/_quarantine",
    "apps_rg/runtime/entry",
    "apps_rg/engines/judges",
    "apps_rg/integrations/gates",
)

NON_PRODUCT_DIRS = (
    "apps_rg/runtime/dry_run",
    "apps_rg/runtime/internal",
)

SPINE_FILES = (
    "apps_rg/__main__.py",
    "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
)


def main() -> int:
    violations: list[str] = []
    for rel in REMOVED_PATHS:
        if (REPO / rel).exists():
            violations.append(f"removed_path_still_exists:{rel}")
    for spine in SPINE_FILES:
        text = (REPO / spine).read_text(encoding="utf-8")
        for forbidden in (
            "from apps_rg.reasoning",
            "from apps_rg._quarantine",
            "from apps_rg.runtime.entry",
            "from apps_rg.integrations.hops",
            "from apps_rg.engines",
        ):
            if forbidden in text:
                violations.append(f"spine_import:{spine}:{forbidden}")
    matrix = REPO / "artifacts/governance/quarantine_fanin_matrix_20260524.json"
    if not matrix.is_file():
        violations.append("missing_fanin_matrix")
    out = {
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
        "non_product_dirs": list(NON_PRODUCT_DIRS),
    }
    report = REPO / "artifacts/ci/quarantine_ssot_gate_report.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
