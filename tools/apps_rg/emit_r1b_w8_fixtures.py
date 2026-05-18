"""Emit W8 post-Exit R1B ingestion eligibility fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_post_exit_ingest import evaluate_post_exit_ingestion


def _raw_request() -> dict:
    return {
        "target_company": "Acme",
        "target_role": "VP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "resume_digest_w8",
        "jd_hash": "jd_digest_w8",
        "brief_hash": "brief_digest_w8",
    }


def _write_exit_bundle(
    run_dir: Path,
    *,
    x3_code: str = "X3_ALLOW",
    proof_eligible: bool = True,
    runtime_status: str = "REAL_LLM",
    include_final_resume: bool = True,
    include_section_output: bool = True,
    write_x3: bool = True,
    prompt_hash: str = "prompt_w8",
    gate_hash: str = "gate_w8",
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run_w8_fixture",
                "section_id": "executive_summary",
                "proof_eligible": proof_eligible,
                "runtime_generation_status": runtime_status,
                "prompt_profile_hash": prompt_hash,
                "gate_profile_hash": gate_hash,
            }
        ),
        encoding="utf-8",
    )
    if write_x3:
        (run_dir / "x3_disposition.json").write_text(
            json.dumps(
                {
                    "x3_code": x3_code,
                    "proof_eligible": proof_eligible,
                    "runtime_generation_status": runtime_status,
                    "proceed_to_runtime": True,
                    "pass": x3_code in ("X3_ALLOW", "X3C", "X3D", "EXIT_OK"),
                }
            ),
            encoding="utf-8",
        )
    if include_final_resume:
        (run_dir / "generated_resume.json").write_text('{"sections": []}', encoding="utf-8")
    if include_section_output:
        (run_dir / "l2_output.json").write_text('{"text": "summary"}', encoding="utf-8")
        (run_dir / "x2_gate_outputs.json").write_text('{"x2_failed": 0}', encoding="utf-8")


def main() -> int:
    import os

    os.environ["APPS_RG_R1B_SKIP_UWG"] = "1"
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w8_fixtures"
    scratch = out / "_scratch"
    if scratch.exists():
        import shutil

        shutil.rmtree(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    cases = {
        "accepted_post_exit_ingestion": ("run_accepted", {}),
        "rejected_mock_runtime_ingestion": (
            "run_mock",
            {"runtime_status": "OFFLINE_CONTRACT_STUB"},
        ),
        "rejected_missing_x3_ingestion": ("run_no_x3", {"write_x3": False}),
        "rejected_missing_proof_chunks_ingestion": (
            "run_no_chunks",
            {"include_final_resume": False, "include_section_output": False},
        ),
        "rejected_missing_required_digest_ingestion": ("run_no_digest", {}),
    }

    raw = _raw_request()
    for fixture_name, (subdir, kwargs) in cases.items():
        run_dir = scratch / subdir
        _write_exit_bundle(run_dir, **kwargs)
        request = raw if "digest" not in fixture_name else {"target_company": "Acme", "target_role": "VP"}
        payload = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=request)
        (out / f"{fixture_name}.json").write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"W8 fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
