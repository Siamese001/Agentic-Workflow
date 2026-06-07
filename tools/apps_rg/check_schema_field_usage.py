"""Verify apps_rg apps_research_call_required migration usage.

Wave 3 keeps the field as a false-valued compatibility carrier while
apps_research delegation is removed from the critical path.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD = "apps_research_call_required"
CHECK_FILES = (
    "agentic_core/runtime/contracts/apps_rg_ingress_payload.py",
    "agentic_core/runtime/contracts/route_contract.py",
    "agentic_core/runtime/contracts/l1_plan_contract.py",
    "apps_rg/runtime/bindings/l0_binding.py",
    "apps_rg/runtime/bindings/l1_binding.py",
    "apps_rg/runtime/bindings/briefing_u0_signals.py",
    "apps_rg/config/domain_contract/route_profiles.yaml",
)


def _occurrences(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    out: list[dict[str, object]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FIELD in line:
            out.append({"line": lineno, "text": line.strip()})
    return out


def main() -> int:
    usage = {
        rel: _occurrences(REPO_ROOT / rel)
        for rel in CHECK_FILES
    }
    true_patterns: list[str] = []
    for rel, rows in usage.items():
        for row in rows:
            text = str(row["text"])
            if re.search(rf"\b{FIELD}\b\s*[:=]\s*True\b", text) or re.search(
                rf"\b{FIELD}\b\s*:\s*true\b", text
            ):
                true_patterns.append(f"{rel}:{row['line']}:{text}")

    report = {
        "field": FIELD,
        "status": "KEEP_FALSE_COMPATIBILITY_FIELD",
        "usage": usage,
        "true_patterns": true_patterns,
        "field_removal_safe": False,
        "reason": (
            "L1PlanContract and RouteContract still expose the field; Wave 3 "
            "therefore keeps it during migration but requires false-valued "
            "delegation semantics."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if true_patterns else 0


if __name__ == "__main__":
    raise SystemExit(main())
