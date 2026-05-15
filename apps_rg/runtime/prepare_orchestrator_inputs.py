"""Validate job-description and briefing files for `orchestrate_full_resume`.

This helper **does not** read, write, or require a base resume path. The orchestrator
uses the canonical default ``apps_rg/resume/base/amit_ayer_base_resume_v1.json`` unless
``--base-resume`` overrides it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apps_rg.runtime.orchestrate_full_resume import CANONICAL_BASE_RESUME_REPO_REL, find_repo_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate JD/briefing inputs for orchestrate_full_resume (no base resume I/O)."
    )
    parser.add_argument("--job-description", type=Path, required=True, dest="jd_path")
    parser.add_argument("--briefing", type=Path, required=True, dest="briefing_path")
    parser.add_argument(
        "--emit-json",
        action="store_true",
        help="Print only JSON (paths repo-relative where possible)",
    )
    args = parser.parse_args(argv)

    repo = find_repo_root()
    jd = args.jd_path if args.jd_path.is_absolute() else (repo / args.jd_path)
    br = args.briefing_path if args.briefing_path.is_absolute() else (repo / args.briefing_path)
    jd_r = jd.resolve()
    br_r = br.resolve()
    for label, path in (("job-description", jd_r), ("briefing", br_r)):
        if not path.is_file():
            sys.stderr.write(f"prepare_orchestrator_inputs: missing {label} file: {path}\n")
            return 2
        if path.stat().st_size == 0:
            sys.stderr.write(f"prepare_orchestrator_inputs: empty {label} file: {path}\n")
            return 2
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            sys.stderr.write(f"prepare_orchestrator_inputs: whitespace-only {label} file: {path}\n")
            return 2

    def _repo_rel(target: Path) -> str:
        try:
            return target.relative_to(repo.resolve()).as_posix()
        except ValueError:
            return target.resolve().as_posix()

    suggested = (
        "python -m apps_rg.runtime.orchestrate_full_resume "
        "--provider qwen_vllm "
        "--x1d-judges gemini_pro,openai_chatgpt,anthropic_claude "
        "--allow-non-allow-exit-zero "
        f"--job-description {_repo_rel(jd_r)} "
        f"--briefing {_repo_rel(br_r)}"
    )
    payload = {
        "job_description_repo_relative": _repo_rel(jd_r),
        "briefing_repo_relative": _repo_rel(br_r),
        "canonical_base_resume_repo_relative_note": CANONICAL_BASE_RESUME_REPO_REL.as_posix(),
        "suggested_cli": suggested,
    }
    if args.emit_json:
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return 0

    sys.stdout.write("Validated inputs (base resume unchanged; use orchestrator default or --base-resume).\n")
    sys.stdout.write(f"  job-description: {_repo_rel(jd_r)}\n")
    sys.stdout.write(f"  briefing:        {_repo_rel(br_r)}\n\n")
    sys.stdout.write("Suggested command:\n\n")
    sys.stdout.write(suggested + "\n\n")
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
