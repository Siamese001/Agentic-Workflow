#!/usr/bin/env python3
"""W6: Brown REAL_LLM smoke + PA core-law compile markers for sections rollout lanes."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

TARGET_COMPANY = "Brown & Brown"
TARGET_ROLE = "SVP IT Strategy & Innovation"
JD_PATH = _REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF_PATH = _REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md"

W6_SECTIONS = (
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

PRODUCT_SHAPE_HEADER = "PRODUCT_SHAPE (deterministic X2 authority"
_CHARS_PER_TOKEN = 3
_TOKEN_SAFETY = 1.12


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int((len(text) // _CHARS_PER_TOKEN) * _TOKEN_SAFETY))


def _lane_cmd(section: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        section,
        "--target-company",
        TARGET_COMPANY,
        "--target-role",
        TARGET_ROLE,
        "--jd",
        str(JD_PATH.relative_to(_REPO)).replace("\\", "/"),
        "--manual-brief",
        str(BRIEF_PATH.relative_to(_REPO)).replace("\\", "/"),
        "--provider",
        "qwen_vllm",
        "--allow-non-allow-exit-zero",
    ]


def _latest_real_dir(section: str) -> Path | None:
    real = _REPO / "artifacts/apps_rg/runtime_proofs" / section / "real"
    if not real.is_dir():
        return None
    runs = [p for p in real.iterdir() if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _x2_product_status(run_dir: Path) -> str:
    data = _read_json(run_dir / "x2_gate_outputs.json")
    gates = data.get("gates") or []
    if not gates:
        return str(data.get("product_quality_status") or "UNKNOWN")
    failed = [g.get("gate_id") for g in gates if g.get("pass") is False]
    return "PASS" if not failed else "FAIL"


def _analyze_compiled_prompt(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "compiled_prompt.txt"
    if not path.is_file():
        art = _read_json(run_dir / "compiled_prompt_artifact.json")
        msgs = art.get("messages") or []
        content = str(msgs[0].get("content") or "") if msgs else ""
    else:
        raw = path.read_text(encoding="utf-8")
        try:
            doc = json.loads(raw)
            msgs = doc if isinstance(doc, list) else doc.get("messages") or []
            content = str(msgs[0].get("content") or "") if msgs else raw
        except json.JSONDecodeError:
            content = raw
    ps_count = content.count(PRODUCT_SHAPE_HEADER)
    return {
        "compiled_prompt_tokens_estimate": _estimate_tokens(content),
        "product_shape_block_count": ps_count,
        "pa_core_law_present": "pa_core_law_v1" in content or "pa_truth_oath_v1" in content,
        "headline_marker_present": "HEADLINE_PROMPT_CORE_LAW_V3" in content,
        "competencies_marker_present": "COMPETENCIES_PROMPT_CORE_LAW_V3" in content,
        "unify_ibm_marker_present": "UNIFY_IBM_PROMPT_CORE_LAW_V3" in content,
        "x2_in_static_i0": bool(
            re.search(
                r"<!-- SLOT: I0 -->.*?<!-- SLOT: C0 -->",
                content,
                flags=re.DOTALL,
            )
            and re.search(r"\bx2_[a-z0-9_]+\b", content[content.find("<!-- SLOT: I0 -->") : content.find("<!-- SLOT: C0 -->")])
        ),
    }


def _collect_lane(section: str, *, cli_exit: int) -> dict[str, Any]:
    run_dir = _latest_real_dir(section)
    rec: dict[str, Any] = {
        "section": section,
        "cli_exit_code": cli_exit,
        "run_dir": run_dir.relative_to(_REPO).as_posix() if run_dir else None,
    }
    if not run_dir:
        rec["lane_status"] = "BLOCKED"
        rec["error"] = "no artifacts/apps_rg/runtime_proofs/<section>/real/<run_id>"
        return rec

    x3 = _read_json(run_dir / "x3_disposition.json")
    rec["runtime_generation_status"] = str(x3.get("runtime_generation_status") or "")
    rec["x3_code"] = str(x3.get("x3_code") or "")
    rec["product_quality_status"] = str(x3.get("product_quality_status") or _x2_product_status(run_dir))
    rec["x2_product_status"] = _x2_product_status(run_dir)
    rec["proof_eligible"] = x3.get("proof_eligible")

    tb = _read_json(run_dir / "token_budget_receipt.json")
    rec["token_budget_status"] = tb.get("status")
    rec["dispatch_allowed"] = tb.get("dispatch_allowed")
    if section == "headline" and not tb:
        rec["token_budget_status"] = "EXEMPT"
        rec["token_budget_note"] = (
            "GAP-1: headline has no executive_summary_token_budget gate; "
            "context-window compile only (documented exemption)."
        )
        rec["dispatch_allowed"] = True

    compiled = _analyze_compiled_prompt(run_dir)
    rec.update(compiled)

    real_llm = rec["runtime_generation_status"].upper() == "REAL_LLM"
    markers_ok = rec.get("pa_core_law_present") and rec.get("product_shape_block_count") == 1
    if not real_llm:
        rec["lane_status"] = "BLOCKED"
    elif markers_ok:
        rec["lane_status"] = "PASS"
    else:
        rec["lane_status"] = "PARTIAL"
    return rec


def _rollup_status(lanes: list[dict[str, Any]]) -> str:
    if not lanes:
        return "BLOCKED"
    if all(r.get("lane_status") == "PASS" for r in lanes):
        return "PASS"
    if any(r.get("lane_status") == "PASS" for r in lanes) and any(
        r.get("lane_status") in ("BLOCKED", "PARTIAL") for r in lanes
    ):
        return "PARTIAL"
    if all(r.get("runtime_generation_status", "").upper() == "REAL_LLM" for r in lanes if r.get("run_dir")):
        return "PARTIAL"
    return "BLOCKED"


def _write_reports(payload: dict[str, Any], ts: str) -> tuple[Path, Path]:
    report_dir = _REPO / "docs/reports/apps_rg"
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"sections_pa_core_law_rollout_w6_smoke_{ts}.json"
    md_path = report_dir / "sections_pa_core_law_rollout_w6_smoke.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Sections PA Core-Law Rollout — W6 Runtime Smoke",
        "",
        f"**Generated:** {payload['generated_at_utc']}",
        f"**STATUS:** {payload['status']}",
        "",
        f"**Plan:** [sections-pa-core-law-rollout-c3a8f1.md](.cursor/plans/sections-pa-core-law-rollout-c3a8f1.md)",
        "",
        "## Targeting",
        "",
        f"- Company: {TARGET_COMPANY}",
        f"- Role: {TARGET_ROLE}",
        f"- JD: [brown_brown_svp_it_strategy_innovation_jd.txt](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt)",
        f"- Brief: [brown_brown_svp_it_strategy_innovation_briefing_exec.md](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md)",
        "",
        "## Lane summary",
        "",
        "| section | lane_status | REAL_LLM | x3 | X2 product | token_budget | PRODUCT_SHAPE×1 | pa_core_law | run_dir |",
        "|---------|-------------|----------|-----|------------|--------------|-----------------|-------------|---------|",
    ]
    for r in payload["lanes"]:
        lines.append(
            f"| {r['section']} | {r.get('lane_status','')} | {r.get('runtime_generation_status','')} | "
            f"{r.get('x3_code','')} | {r.get('x2_product_status','')} | {r.get('token_budget_status','')} | "
            f"{r.get('product_shape_block_count','')} | {r.get('pa_core_law_present','')} | "
            f"`{r.get('run_dir','')}` |"
        )
    lines.extend(
        [
            "",
            "## GAP semantics (W6)",
            "",
            "- **GAP-1:** headline `token_budget_status=EXEMPT` (no exec-grade token_budget module).",
            "- **GAP-3:** `x3_code` may be `X3_BLOCK` while `runtime_generation_status=REAL_LLM`; acceptable for PA-dedup DoD.",
            "",
            "## Commands",
            "",
        ]
    )
    for c in payload.get("commands_run") or []:
        lines.append(f"- `{c}`")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ts = _utc_ts()
    commands: list[str] = []
    lanes: list[dict[str, Any]] = []
    for section in W6_SECTIONS:
        cmd = _lane_cmd(section)
        cmd_str = " ".join(cmd)
        commands.append(cmd_str)
        print(f"\n=== W6 smoke: {section} ===", flush=True)
        proc = subprocess.run(cmd, cwd=_REPO, timeout=900)
        lanes.append(_collect_lane(section, cli_exit=proc.returncode))

    status = _rollup_status(lanes)
    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "wave": "W6",
        "plan_id": "sections-pa-core-law-rollout-c3a8f1",
        "commands_run": commands,
        "lanes": lanes,
        "gap_notes": {
            "GAP-1": "headline token budget exempt",
            "GAP-3": "X3_BLOCK with REAL_LLM acceptable for governance closeout",
        },
    }
    json_path, md_path = _write_reports(payload, ts)
    artifact_root = _REPO / f"artifacts/apps_rg/runtime_proofs/core_law_rollout_w6_{ts}"
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "w6_smoke_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nW6 smoke status={status}")
    print(f"Report: {md_path}")
    print(f"Manifest: {artifact_root / 'w6_smoke_manifest.json'}")
    return 0 if status in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
