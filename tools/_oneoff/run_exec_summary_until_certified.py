#!/usr/bin/env python3
"""Run executive_summary (Brown targeting) until CERTIFIED or max attempts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROOFS_ROOT = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary" / "real"
JD = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"


def _max_attempts() -> int:
    raw = os.environ.get("EXEC_SUMMARY_CERT_LOOP_MAX", "8").strip()
    try:
        return max(1, min(20, int(raw)))
    except ValueError:
        return 8


def _latest_run_dir(before: set[str]) -> Path | None:
    if not PROOFS_ROOT.is_dir():
        return None
    candidates = [
        p
        for p in PROOFS_ROOT.iterdir()
        if p.is_dir() and p.name.startswith("exec_summary_") and p.name not in before
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _judge_summary(run_dir: Path) -> dict[str, object]:
    path = run_dir / "x1d_llm_judge_outputs.json"
    if not path.is_file():
        return {"pass_count": 0, "judges": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    judges = data.get("judges") or []
    rows = []
    pass_count = 0
    for j in judges:
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        ok = (
            j.get("provider_status") == "MODEL_BACKED_PASS"
            and j.get("pass") is True
            and not j.get("decisive_failure")
        )
        if ok:
            pass_count += 1
        rows.append(
            {
                "provider": j.get("provider_key"),
                "score": j.get("score"),
                "pass": ok,
                "inferred_dims": j.get("dimension_verdicts_inferred"),
            }
        )
    return {"pass_count": pass_count, "judges": rows}


def _certified(run_dir: Path) -> tuple[bool, dict[str, object]]:
    cli = run_dir / "cli_section_execution_report.json"
    x3_path = run_dir / "x3_disposition.json"
    out: dict[str, object] = {"run_dir": str(run_dir)}
    if cli.is_file():
        cli_body = json.loads(cli.read_text(encoding="utf-8"))
        out["operator_status"] = cli_body.get("operator_status")
        out["certified"] = cli_body.get("certified")
        out["draft_ready"] = cli_body.get("draft_ready")
        out["process_exit_code"] = cli_body.get("process_exit_code")
    if x3_path.is_file():
        x3 = json.loads(x3_path.read_text(encoding="utf-8"))
        out["x3_code"] = x3.get("x3_code")
        out["x3_pass"] = x3.get("pass")
    js = _judge_summary(run_dir)
    out.update(js)
    certified = bool(out.get("certified")) or (
        out.get("x3_code") == "X3_ALLOW" and out.get("x3_pass") is True
    )
    all_three = int(js.get("pass_count") or 0) >= 3
    return certified and all_three, out


def main() -> int:
    argv = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        "executive_summary",
        "--target-company",
        "Brown & Brown",
        "--target-role",
        "SVP IT Strategy & Innovation",
        "--jd",
        str(JD),
        "--manual-brief",
        str(BRIEF),
    ]
    seen: set[str] = set()
    max_n = _max_attempts()
    receipt_path = REPO / "docs/reports/apps_rg/exec_summary_cert_loop_receipt.json"

    for attempt in range(1, max_n + 1):
        print(f"\n=== exec_summary attempt {attempt}/{max_n} ===", flush=True)
        t0 = time.time()
        proc = subprocess.run(
            argv,
            cwd=str(REPO),
            env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
            capture_output=False,
            timeout=3600,
            check=False,
        )
        elapsed = time.time() - t0
        run_dir = _latest_run_dir(seen)
        if run_dir is None:
            print("BLOCKED: no new exec_summary_* artifact dir", flush=True)
            return 2
        seen.add(run_dir.name)
        ok, summary = _certified(run_dir)
        summary["attempt"] = attempt
        summary["cli_exit_code"] = proc.returncode
        summary["elapsed_s"] = round(elapsed, 1)
        print(json.dumps(summary, indent=2), flush=True)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps({"final": summary, "attempts": attempt, "certified": ok}, indent=2),
            encoding="utf-8",
        )
        if ok:
            print(f"CERTIFIED_PASS: {run_dir.name}", flush=True)
            return 0
        print(f"Not certified yet (exit {proc.returncode}); retrying...", flush=True)

    print(f"FAIL: max attempts {max_n} without CERTIFIED", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
