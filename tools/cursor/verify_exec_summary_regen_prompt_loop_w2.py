"""W2 — verify judge regen prompt-loop fix on a REAL_LLM run directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _resolve(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def _user_content_from_provider_request(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    messages = payload.get("messages") or []
    for msg in reversed(messages):
        if not isinstance(msg, dict):
            continue
        if msg.get("role") == "user":
            return str(msg.get("content") or "")
    return None


def _regen_delta_digest(user_content: str | None) -> str | None:
    if not user_content:
        return None
    m = re.search(r"REGEN_DELTA(?:_v1)?:\s*(.+)", user_content, re.DOTALL)
    if not m:
        return None
    block = m.group(1).strip()
    return hashlib.sha256(block.encode("utf-8")).hexdigest()[:16]


def verify(run_dir: Path) -> dict:
    report: dict = {
        "schema": "executive_summary_regen_prompt_loop_w2_verify_v1",
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/")
        if run_dir.is_relative_to(ROOT)
        else str(run_dir).replace("\\", "/"),
        "checks": {},
        "passed": True,
    }
    cycles_p = run_dir / "judge_remediation_cycles.json"
    if not cycles_p.is_file():
        report["passed"] = False
        report["error"] = "missing judge_remediation_cycles.json"
        return report

    cycles = json.loads(cycles_p.read_text(encoding="utf-8"))
    cycle_list = cycles.get("cycles") or []
    report["regen_outcome"] = cycles.get("regen_outcome")
    report["stopped_reason"] = cycles.get("stopped_reason")

    c1 = next((c for c in cycle_list if c.get("cycle") == 1), None)
    if c1:
        dc = c1.get("delta_class")
        report["checks"]["cycle1_delta_class"] = dc
        report["checks"]["cycle1_delta_class_s6"] = dc == "S6_forward_synthesis"
        if dc != "S6_forward_synthesis":
            report["passed"] = False

    c2 = next((c for c in cycle_list if c.get("cycle") == 2), None)
    if c2:
        report["checks"]["cycle2_delta_class"] = c2.get("delta_class")
        report["checks"]["cycle2_has_scores_after"] = "scores_after" in c2
        report["checks"]["cycle2_g5_passed"] = c2.get("g5_passed")

    regen_files = sorted(run_dir.glob("provider_request_judge_regen_cycle*.json"))
    digests: dict[str, str | None] = {}
    edit_budget: dict[str, bool] = {}
    for fp in regen_files:
        content = _user_content_from_provider_request(fp)
        digests[fp.name] = _regen_delta_digest(content)
        edit_budget[fp.name] = bool(
            content and ("EDIT_BUDGET" in content or "delta_class=S6_forward_synthesis" in content)
        )
    report["regen_request_files"] = [f.name for f in regen_files]
    report["regen_delta_digests"] = digests
    report["edit_budget_present"] = edit_budget

    c01 = [n for n in digests if "cycle01" in n]
    c02 = [n for n in digests if "cycle02" in n]
    if c01 and c02:
        d01 = digests.get(c01[0])
        d02 = digests.get(c02[0])
        report["checks"]["cycle02_delta_differs_from_cycle01"] = bool(
            d01 and d02 and d01 != d02
        )
        if not report["checks"]["cycle02_delta_differs_from_cycle01"]:
            report["passed"] = False
    elif len(cycle_list) >= 2:
        report["checks"]["cycle02_delta_differs_from_cycle01"] = False
        report["passed"] = False

    if c01 and not any(edit_budget.get(n) for n in c01):
        report["passed"] = False
        report["checks"]["cycle01_edit_budget_line"] = False
    else:
        report["checks"]["cycle01_edit_budget_line"] = True

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir")
    parser.add_argument("--write-receipt", default="")
    args = parser.parse_args()
    run_dir = _resolve(args.artifact_dir)
    if not run_dir.is_dir():
        print(json.dumps({"passed": False, "error": f"not a directory: {run_dir}"}, indent=2))
        return 2
    report = verify(run_dir)
    if args.write_receipt:
        out = _resolve(args.write_receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
