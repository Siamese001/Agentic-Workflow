#!/usr/bin/env python3
"""Build agentic_core W1 spine axes JSON from runtime assessment (inventory-only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSESSMENT = REPO / "docs/reports/agentic_core_agent_inventory_runtime_assessment.json"
OUT = (
    REPO
    / "agentic_core/L2_execution/types/data/agentic_core_w1_spine_axes.json"
)


def _agenthood(truly_agent: str, inventory_role: str) -> str:
    if inventory_role == "SHIM_OR_DEAD_LEGACY":
        return "SHIM_OR_DEAD_LEGACY"
    if inventory_role == "UTILITY_OR_WRAPPER":
        return "WRAPPER_ONLY"
    if truly_agent == "YES":
        return "TRUE_AGENT"
    return "NOT_AGENT"


def main() -> int:
    if not ASSESSMENT.is_file():
        print(f"BLOCKED: missing {ASSESSMENT}", file=sys.stderr)
        return 1
    doc = json.loads(ASSESSMENT.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for row in doc.get("rows") or []:
        agent = str(row.get("agent") or "")
        if not agent or agent.startswith("("):
            continue
        path = str(row.get("module_path") or "")
        if not path.startswith("agentic_core/"):
            continue
        inventory_role = str(row.get("inventory_role") or "UTILITY_OR_WRAPPER")
        truly = str(row.get("truly_agent") or "NO")
        rows.append(
            {
                "class_name": agent,
                "file_path": path,
                "declared_layer": str(row.get("declared_layer") or ""),
                "agenthood_status": _agenthood(truly, inventory_role),
                "inventory_role": inventory_role,
                "product_spine_invocation_status": "NOT_ARTIFACT_PROVEN",
                "runtime_proof_class": "NONE",
                "spine_proof_ref": "",
                "assessment_truly_agent": truly,
            },
        )
    rows.sort(key=lambda r: r["class_name"].lower())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_from": str(ASSESSMENT.relative_to(REPO)).replace("\\", "/"),
        "adr": "ADR-088",
        "w1_defaults": {
            "product_spine_invocation_status": "NOT_ARTIFACT_PROVEN",
            "runtime_proof_class": "NONE",
        },
        "agentic_core_row_count": len(rows),
        "true_agent_count": sum(1 for r in rows if r["agenthood_status"] == "TRUE_AGENT"),
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)} ({len(rows)} rows, {payload['true_agent_count']} TRUE_AGENT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
