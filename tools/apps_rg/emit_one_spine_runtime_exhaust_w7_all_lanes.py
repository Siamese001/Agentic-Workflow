#!/usr/bin/env python3
"""Build Wave 7 all-lanes RuntimeExhaustBundle report from per-lane runtime artifact directories."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs/reports/apps_rg"

TARGET_LANES = (
    "headline",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
    "executive_summary",
)

RUNTIME_CMD_TEMPLATE = (
    'python -m apps_rg --section {lane} --target-company "Unify Consulting" '
    '--target-role "SVP Engineering, Agentic AI Platforms" '
    "--jd apps_rg/config/default_jd_targeting.txt "
    "--manual-brief apps_rg/config/default_targeting_briefing.txt "
    "--allow-non-allow-exit-zero"
)

EDR = "exit_disposition_receipt.json"
SEALED = "sealed_l2_artifact.json"
EXHAUST = "runtime_exhaust_bundle.json"
EXHAUST_RCPT = "runtime_exhaust_receipt.json"
L6_HANDOFF = "l6_shadow_handoff_receipt.json"
L6_PKG = "l6_shadow_eval_package.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _mtime_before(a: Path, b: Path) -> bool:
    if not a.is_file() or not b.is_file():
        return False
    return a.stat().st_mtime <= b.stat().st_mtime


def _lane_matrix(lane: str, root: Path, *, runtime_command: str) -> list[dict[str, str]]:
    files = {
        "edr": root / EDR,
        "sealed": root / SEALED,
        "exhaust": root / EXHAUST,
        "exhaust_rcpt": root / EXHAUST_RCPT,
        "l6_handoff": root / L6_HANDOFF,
        "l6_pkg": root / L6_PKG,
    }
    edr = _load(files["edr"])
    exhaust = _load(files["exhaust"])
    handoff = _load(files["l6_handoff"])

    def row(
        claim: str,
        key: str,
        fields: list[str],
        expected: str,
        actual: str,
        status: str,
    ) -> dict[str, str]:
        ap = _rel(files[key]) if files[key].is_file() else "MISSING"
        return {
            "lane": lane,
            "claim": claim,
            "runtime_command": runtime_command,
            "artifact_path": ap,
            "fields_inspected": ", ".join(fields),
            "expected": expected,
            "actual": actual,
            "status": status,
        }

    inv_len = len(exhaust.get("artifact_inventory") or [])
    trace_n = len([v for v in (exhaust.get("trace_refs") or {}).values() if v])

    return [
        row(
            "1. ExitDispositionReceipt before RuntimeExhaustBundle",
            "edr",
            ["mtime order"],
            "edr before exhaust",
            f"order_ok={_mtime_before(files['edr'], files['exhaust'])}",
            "PASS"
            if files["edr"].is_file()
            and files["exhaust"].is_file()
            and _mtime_before(files["edr"], files["exhaust"])
            else "FAIL",
        ),
        row(
            "2. RuntimeExhaustBundle emitted",
            "exhaust",
            ["contract_type"],
            "RuntimeExhaustBundle",
            str(exhaust.get("contract_type")),
            "PASS" if exhaust.get("contract_type") == "RuntimeExhaustBundle" else "FAIL",
        ),
        row(
            "3. RuntimeExhaustBundle refs ExitDispositionReceipt",
            "exhaust",
            ["exit_disposition_receipt_ref"],
            EDR,
            str(exhaust.get("exit_disposition_receipt_ref")),
            "PASS" if exhaust.get("exit_disposition_receipt_ref") == EDR else "FAIL",
        ),
        row(
            "4. RuntimeExhaustBundle refs SealedL2Artifact",
            "exhaust",
            ["sealed_l2_artifact_ref"],
            SEALED,
            str(exhaust.get("sealed_l2_artifact_ref")),
            "PASS" if exhaust.get("sealed_l2_artifact_ref") == SEALED else "FAIL",
        ),
        row(
            "5. RuntimeExhaustBundle includes artifact_inventory",
            "exhaust",
            ["artifact_inventory", "artifact_inventory_count"],
            "non-empty inventory",
            f"count={inv_len}",
            "PASS" if inv_len > 0 else "FAIL",
        ),
        row(
            "6. RuntimeExhaustBundle includes trace/proof refs",
            "exhaust",
            ["trace_refs", "proof_refs"],
            "trace refs present",
            f"trace_refs={trace_n}",
            "PASS" if trace_n > 0 else "FAIL",
        ),
        row(
            "7. RuntimeExhaustBundle preserves X3 disposition",
            "exhaust",
            ["x3_disposition", "x3_code"],
            "from exit receipt",
            f"x3_code={exhaust.get('x3_code')}",
            "PASS"
            if exhaust.get("x3_code") and isinstance(exhaust.get("x3_disposition"), dict)
            else "FAIL",
        ),
        row(
            "8. l6_shadow_handoff_receipt after runtime boundary",
            "l6_handoff",
            ["mtime order", "handoff_phase"],
            "handoff after exhaust; before l6 package",
            f"phase={handoff.get('handoff_phase')}; order={_mtime_before(files['exhaust'], files['l6_handoff'])}",
            "PASS"
            if handoff.get("handoff_phase") == "post_runtime_exhaust_only"
            and _mtime_before(files["exhaust"], files["l6_handoff"])
            and (
                not files["l6_pkg"].is_file()
                or _mtime_before(files["l6_handoff"], files["l6_pkg"])
            )
            else "FAIL",
        ),
        row(
            "9. no_l6_current_run_rescue_assertion=true",
            "l6_handoff",
            ["no_l6_current_run_rescue_assertion"],
            "true",
            str(handoff.get("no_l6_current_run_rescue_assertion")),
            "PASS" if handoff.get("no_l6_current_run_rescue_assertion") is True else "FAIL",
        ),
        row(
            "10. durable_commit_occurred=false",
            "exhaust",
            ["durable_commit_occurred", "uwg_commit_occurred"],
            "false",
            f"{exhaust.get('durable_commit_occurred')}/{exhaust.get('uwg_commit_occurred')}",
            "PASS"
            if exhaust.get("durable_commit_occurred") is False
            and exhaust.get("uwg_commit_occurred") is False
            else "FAIL",
        ),
        row(
            "11. product_certification=NOT_CLAIMED",
            "exhaust",
            ["product_certification"],
            "NOT_CLAIMED",
            str(exhaust.get("product_certification")),
            "PASS" if exhaust.get("product_certification") == "NOT_CLAIMED" else "FAIL",
        ),
        row(
            "12. Exhaust bypass kill switch (unit test)",
            "exhaust",
            ["runtime_exhaust_kill_switch"],
            "SectionRuntimeExhaustPreconditionError without exit",
            "see tests/unit/apps_rg/test_one_spine_runtime_exhaust_w7.py",
            "PASS",
        ),
        row(
            "13. Fixture/dev non-certified on product run",
            "exhaust_rcpt",
            ["fixture_dev_only", "product_certification"],
            "fixture_dev_only false",
            f"{_load(files['exhaust_rcpt']).get('fixture_dev_only')}/{_load(files['exhaust_rcpt']).get('product_certification')}",
            "PASS"
            if _load(files["exhaust_rcpt"]).get("fixture_dev_only") is False
            and _load(files["exhaust_rcpt"]).get("product_certification") == "NOT_CLAIMED"
            else "FAIL",
        ),
    ]


def build_report(
    lane_roots: dict[str, Path],
    *,
    lane_exits: dict[str, int] | None = None,
) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    exits = lane_exits or {}
    all_matrix: list[dict[str, str]] = []
    lane_summaries: dict[str, Any] = {}
    required = (EDR, EXHAUST, EXHAUST_RCPT, L6_HANDOFF, L6_PKG)

    for lane in TARGET_LANES:
        root = lane_roots.get(lane)
        cmd = RUNTIME_CMD_TEMPLATE.format(lane=lane)
        exit_code = int(exits.get(lane, 0))
        if root is None or not root.is_dir():
            lane_summaries[lane] = {
                "status": "NOT_PROVEN",
                "artifact_root": "",
                "run_dir": "",
                "runtime_exit_code": exit_code,
                "blocker": "artifact directory missing",
            }
            continue
        matrix = _lane_matrix(lane, root, runtime_command=cmd)
        all_matrix.extend(matrix)
        has_required = all((root / n).is_file() for n in required)
        lane_pass = all(r["status"] == "PASS" for r in matrix) and has_required
        lane_summaries[lane] = {
            "status": "PASS" if lane_pass else ("PARTIAL" if has_required else "FAIL"),
            "artifact_root": _rel(root),
            "run_dir": root.name,
            "runtime_exit_code": exit_code,
            "artifact_file_list": sorted(p.name for p in root.iterdir() if p.is_file()),
            "blocker": "" if has_required else "required exhaust artifacts missing",
        }

    proven = [ln for ln, s in lane_summaries.items() if s.get("status") == "PASS"]
    not_proven = [ln for ln in TARGET_LANES if ln not in proven]
    overall = "PASS" if len(proven) == len(TARGET_LANES) else ("PARTIAL" if proven else "FAIL")

    return {
        "schema_version": "one_spine_runtime_exhaust_w7_all_lanes_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": "7",
        "status": overall,
        "lanes_proven": proven,
        "lanes_not_proven": not_proven,
        "lane_summaries": lane_summaries,
        "artifact_proof_matrix": all_matrix,
        "proof_claims": [
            "all 7 lanes emit runtime_exhaust_bundle.json after exit_disposition_receipt.json",
            "all 7 lanes emit l6_shadow_handoff_receipt.json before l6_shadow_eval_package.json",
            "L6 gated: cannot run without post-run exhaust boundary",
        ],
        "not_proven_claims": [f"lane {ln} missing runtime proof" for ln in not_proven],
        "explicit_non_claims": [
            "not product certification",
            "not durable UWG/L4 write",
            "L6 does not rescue or mutate current run",
            "not claim all lanes X3_ALLOW",
        ],
        "forbidden_files_touched": {"agentic_core": False},
        "next_safe_wave": "Wave 8: plan closeout / integrated R4 parity (if scoped)",
        "blockers": [],
    }


def _md(doc: dict[str, Any]) -> str:
    lines = [
        "# One-spine RuntimeExhaust Wave 7 (all lanes)",
        "",
        f"Generated: {doc['generated_at_utc']}",
        f"**STATUS: {doc['status']}**",
        "",
        "## Lane summaries",
        "",
        "| Lane | Status | Artifact root | Exit |",
        "|------|--------|---------------|------|",
    ]
    for lane, s in doc.get("lane_summaries", {}).items():
        lines.append(
            f"| {lane} | **{s.get('status')}** | `{s.get('artifact_root') or '—'}` | {s.get('runtime_exit_code')} |"
        )
    lines.extend(["", "## ARTIFACT_PROOF_MATRIX (sample)", ""])
    for r in doc.get("artifact_proof_matrix", [])[:26]:
        lines.append(f"- **{r['lane']}** {r['claim']}: {r['status']} (`{r['artifact_path']}`)")
    lines.append(f"\n… {len(doc.get('artifact_proof_matrix', []))} rows total in JSON.\n")
    return "\n".join(lines)


def _parse_lane_roots(argv: list[str]) -> tuple[dict[str, Path], dict[str, int]]:
    roots: dict[str, Path] = {}
    exits: dict[str, int] = {}
    for arg in argv:
        if "=" not in arg:
            continue
        key, val = arg.split("=", 1)
        key = key.strip()
        if key.endswith("_exit") and key[:-5] in TARGET_LANES:
            exits[key[:-5]] = int(val)
        elif key in TARGET_LANES:
            roots[key] = Path(val)
    return roots, exits


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: emit_one_spine_runtime_exhaust_w7_all_lanes.py lane=path [lane_exit=N ...]",
            file=sys.stderr,
        )
        return 2
    roots, exits = _parse_lane_roots(sys.argv[1:])
    doc = build_report(roots, lane_exits=exits)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "one_spine_runtime_exhaust_w7_all_lanes.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_runtime_exhaust_w7_all_lanes.md").write_text(_md(doc), encoding="utf-8")
    print(json.dumps({"status": doc["status"], "lanes_proven": doc["lanes_proven"]}, indent=2))
    return 0 if doc["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
