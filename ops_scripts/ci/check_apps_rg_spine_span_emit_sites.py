#!/usr/bin/env python3
"""APPS-RG-SPINE-SPAN-EMIT-SITES — static W4 ratchet for checklist binding seams."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REPORT_JSON = REPO_ROOT / "artifacts" / "ci" / "apps_rg_spine_span_emit_sites_gate.json"
EMIT_NEEDLE = "emit_spine_span_event"


def _check_row(row: object) -> tuple[bool, str]:
    from agentic_core.L6_system_learning.span_contracts import AppsRgSpineSpanRow

    if not isinstance(row, AppsRgSpineSpanRow):
        return False, "invalid_row"
    rel = str(row.binding_seam).replace("\\", "/")
    path = REPO_ROOT / rel
    if not path.is_file():
        return False, f"MISSING_FILE {rel}"
    text = path.read_text(encoding="utf-8")
    if EMIT_NEEDLE in text:
        return True, "emit_in_binding_seam"
    # Known delegated emitters (front/C0/exhaust compose paths)
    delegated = (
        "apps_rg/runtime/spine/front_contracts.py",
        "apps_rg/runtime/spine/c0_fec_compose.py",
        "apps_rg/runtime/section_runtime_exhaust_spine_receipt.py",
        "apps_rg/runtime/spine/governed_pa_compose.py",
        "apps_rg/runtime/section_l2_lane_integration.py",
        "apps_rg/runtime/spine/section_x3_finalize.py",
    )
    for dep in delegated:
        dep_path = REPO_ROOT / dep.replace("/", os.sep)
        if dep_path.is_file() and EMIT_NEEDLE in dep_path.read_text(encoding="utf-8"):
            return True, f"emit_delegated_via {dep}"
    return False, f"MISSING_EMIT {rel}"


def main() -> int:
    if os.environ.get("APPS_RG_SPINE_CONVERGENCE_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[APPS-RG-SPINE-SPAN-EMIT-SITES] BYPASS")
        return 0

    from agentic_core.L6_system_learning.span_contracts import APPS_RG_SPINE_SPAN_CHECKLIST

    rows: list[dict[str, object]] = []
    errors: list[str] = []
    for row in APPS_RG_SPINE_SPAN_CHECKLIST:
        ok, reason = _check_row(row)
        rows.append({"layer_key": row.layer_key, "binding_seam": row.binding_seam, "ok": ok, "reason": reason})
        if not ok:
            errors.append(f"{row.layer_key}: {reason}")

    report = {
        "gate": "APPS-RG-SPINE-SPAN-EMIT-SITES",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "error_count": len(errors),
        "rows": rows,
        "errors": errors,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"[APPS-RG-SPINE-SPAN-EMIT-SITES] FAIL errors={len(errors)}")
        for err in errors:
            print(f"  {err}")
        return 1
    print(f"[APPS-RG-SPINE-SPAN-EMIT-SITES] PASS rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
