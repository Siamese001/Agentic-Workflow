"""W5 — verify canonical executive_summary judge-regen run artifact checklist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "run_manifest.json",
    "compiled_prompt_artifact.json",
    "provider_request.json",
    "provider_response.json",
    "judge_remediation_cycles.json",
    "candidate_pool_summary.json",
    "x2_gate_outputs.json",
    "x1d_llm_judge_outputs.json",
    "x3_disposition.json",
    "section_metric_receipt.json",
    "publish_integrity_receipt.json",
)


def _resolve_run_dir(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    return p


def verify_run_dir(run_dir: Path) -> dict:
    missing = [name for name in REQUIRED_ARTIFACTS if not (run_dir / name).is_file()]
    result: dict = {
        "schema": "executive_summary_judge_regen_w5_verify_v1",
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/")
        if run_dir.is_relative_to(ROOT)
        else str(run_dir).replace("\\", "/"),
        "missing_artifacts": missing,
        "passed": not missing,
    }
    cycles_p = run_dir / "judge_remediation_cycles.json"
    if cycles_p.is_file():
        try:
            cycles = json.loads(cycles_p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result["cycles_parse_error"] = str(exc)
            result["passed"] = False
        else:
            schema_version = cycles.get("schema_version")
            result["cycles_schema_version"] = schema_version
            result["cycles_schema"] = cycles.get("schema")
            result["regen_outcome"] = cycles.get("regen_outcome")
            result["final_publish_baseline"] = cycles.get("final_publish_baseline")
            if schema_version != 2:
                result["schema_version_ok"] = False
                result["passed"] = False
            else:
                result["schema_version_ok"] = True
            for cycle in cycles.get("cycles") or []:
                if not isinstance(cycle, dict):
                    continue
                if cycle.get("accepted") and cycle.get("publish_eligible") is False:
                    if cycle.get("reject_gate") in (
                        "trigger_judge_regression",
                        "trigger_judge_unknown",
                    ):
                        result["brown_regression_guard_ok"] = True
    integrity_p = run_dir / "publish_integrity_receipt.json"
    if integrity_p.is_file():
        try:
            integrity = json.loads(integrity_p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result["integrity_parse_error"] = str(exc)
            result["passed"] = False
        else:
            pub = integrity.get("published_candidate_digest")
            src = integrity.get("final_artifact_digest_source")
            result["publish_integrity_match"] = bool(pub and pub == src)
            if not result["publish_integrity_match"]:
                result["passed"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_dir",
        help="Run directory (e.g. artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--write-receipt",
        default="",
        help="Optional path under repo to write JSON receipt",
    )
    args = parser.parse_args()
    run_dir = _resolve_run_dir(args.artifact_dir)
    if not run_dir.is_dir():
        print(json.dumps({"passed": False, "error": f"not a directory: {run_dir}"}, indent=2))
        return 2
    report = verify_run_dir(run_dir)
    if args.write_receipt:
        out = _resolve_run_dir(args.write_receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
