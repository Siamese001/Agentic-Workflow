#!/usr/bin/env python3
"""Run Brown executive_summary until all model-backed X1D judges pass (bounded)."""
from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "artifacts/apps_rg/runtime_proofs/executive_summary/real"
MAX_ATTEMPTS = int(os.environ.get("BROWN_JUDGE_PASS_MAX_RUNS", "5"))


def all_pass(run_dir: Path) -> bool:
    p = run_dir / "x1d_llm_judge_outputs.json"
    if not p.is_file():
        return False
    judges = json.loads(p.read_text(encoding="utf-8")).get("judges") or []
    mb = [j for j in judges if j.get("evaluator_mode") == "MODEL_BACKED"]
    return bool(mb) and all(
        j.get("pass") is True and j.get("provider_status") == "MODEL_BACKED_PASS"
        for j in mb
    )


def latest_dir() -> Path | None:
    dirs = sorted(ROOT.glob("exec_summary_*"), key=lambda x: x.stat().st_mtime, reverse=True)
    return dirs[0] if dirs else None


def main() -> int:
    cmd = [
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
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt",
        "--provider",
        "qwen_vllm",
        "--allow-non-allow-exit-zero",
        "--manual-brief",
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
    ]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"=== attempt {attempt} ===", flush=True)
        old_argv = sys.argv[:]
        old_cwd = Path.cwd()
        exit_code = 1
        try:
            os.chdir(REPO)
            sys.argv = list(cmd[1:])
            runpy.run_module("apps_rg", run_name="__main__", alter_sys=True)
            exit_code = 0
        except SystemExit as exc:
            exit_code = int(exc.code) if isinstance(exc.code, int) else 1
        finally:
            os.chdir(old_cwd)
            sys.argv = old_argv
        run_dir = latest_dir()
        name = run_dir.name if run_dir else None
        print(f"exit={exit_code} run_dir={name}", flush=True)
        if run_dir and all_pass(run_dir):
            print("ALL_JUDGES_PASS", flush=True)
            for j in json.loads((run_dir / "x1d_llm_judge_outputs.json").read_text(encoding="utf-8"))[
                "judges"
            ]:
                if j.get("evaluator_mode") == "MODEL_BACKED":
                    print(
                        f"  {j['provider_key']}: score={j.get('score')} "
                        f"pass={j.get('pass')} status={j.get('provider_status')}",
                        flush=True,
                    )
            cycles_path = run_dir / "judge_remediation_cycles.json"
            if cycles_path.is_file():
                c = json.loads(cycles_path.read_text(encoding="utf-8"))
                print(
                    f"  cycles.max={c.get('max_cycles')} stopped={c.get('stopped_reason')}",
                    flush=True,
                )
            print(f"artifact_dir={run_dir}", flush=True)
            return 0
    print("GAVE_UP_NO_ALL_PASS", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
