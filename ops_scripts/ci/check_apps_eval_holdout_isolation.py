"""CI gate: holdout suites require release-gate authorization."""

from __future__ import annotations

import json
import os
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "apps_eval" / "registry" / "suites.yaml"
HOLDOUT_ROOTS = [
    ROOT / "apps_eval" / "fixtures" / "holdout" / "apps_rg",
    ROOT / "apps_eval" / "fixtures" / "holdout" / "apps_lic",
]


def main() -> int:
    failures: list[str] = []
    suites = json.loads(REGISTRY.read_text(encoding="utf-8"))["suites"]
    holdout_suites = {key: value for key, value in suites.items() if value.get("split") == "holdout"}
    if set(holdout_suites) != {"apps_rg.holdout.resume_generation", "apps_lic.holdout.outreach_message"}:
        failures.append(f"unexpected holdout suites: {sorted(holdout_suites)}")
    for suite_id, suite in holdout_suites.items():
        if suite.get("scenarios") != []:
            failures.append(f"{suite_id} must not list development-readable holdout scenarios")
    for root in HOLDOUT_ROOTS:
        visible = sorted(path.name for path in root.iterdir()) if root.exists() else []
        if visible != ["README.md"]:
            failures.append(f"{root.relative_to(ROOT).as_posix()} must contain README.md only, got {visible}")

    original = os.environ.pop("APPS_EVAL_RELEASE_GATE", None)
    try:
        try:
            run_eval(EvalRequest(suite_id="apps_rg.holdout.resume_generation", out_dir="artifacts/apps_eval/holdout_probe"))
            failures.append("holdout run did not require APPS_EVAL_RELEASE_GATE=1")
        except PermissionError:
            pass
    finally:
        if original is not None:
            os.environ["APPS_EVAL_RELEASE_GATE"] = original

    if failures:
        print("apps_eval holdout isolation gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: apps_eval holdout suites are isolated behind release-gate authorization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
