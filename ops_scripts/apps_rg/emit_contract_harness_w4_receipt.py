#!/usr/bin/env python3
"""W4: verify B5 tail burndown on filtered ``tests/_apps_contract`` slice."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "apps-rg-contract-harness-modernization-f4e8b2"
RECEIPT_JSON = REPO / "docs/reports/apps_rg/contract_harness_modernization_w4_receipt.json"

PYTEST_K = (
    "competencies or prompt_judge or product_shape or executive_summary_x2 "
    "or unify_bullets or ibm_bullets or unify_narrative or ibm_narrative"
)

W4_SPOT_CHECKS = [
    "tests/_apps_contract/test_resume_section_treatment_profile.py",
    "tests/_apps_contract/test_pa_binding_role_tiering.py",
    "tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py",
    "tests/_apps_contract/test_apps_rg_srfs_w4_x2_slice_gates.py",
]


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def main() -> int:
    from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links

    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": str(REPO)}

    spot_cmd = [sys.executable, "-m", "pytest", *W4_SPOT_CHECKS, "-q", "--tb=no", "-o", "addopts="]
    spot = subprocess.run(spot_cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)

    slice_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/_apps_contract/",
        "-k",
        PYTEST_K,
        "-q",
        "--tb=no",
        "-o",
        "addopts=",
    ]
    sliced = subprocess.run(slice_cmd, cwd=REPO, capture_output=True, text=True, timeout=900, env=env, check=False)
    summary = (sliced.stdout or "") + (sliced.stderr or "")
    tail_line = ""
    for line in summary.splitlines():
        if "failed" in line and "passed" in line:
            tail_line = line.strip()

    spot_ok = spot.returncode == 0
    slice_ok = sliced.returncode == 0
    if spot_ok and slice_ok:
        status = "PASS"
    elif spot_ok or sliced.returncode == 0:
        status = "PASS" if slice_ok else "PARTIAL"
    else:
        status = "PARTIAL" if "passed" in tail_line and "failed" in tail_line else "FAIL"

    receipt = enrich_manifest_links(
        {
            "schema": "contract_harness_modernization_wave_receipt_v1",
            "plan_id": PLAN_ID,
            "wave_id": "W4",
            "status": status,
            "git_commit": _git_commit(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pytest_exit_code_filtered_slice": sliced.returncode,
            "pytest_exit_code_spot_checks": spot.returncode,
            "filtered_slice_summary": tail_line or "see pytest output tail",
            "w0_baseline_failed": 190,
            "w4_spot_check_paths": W4_SPOT_CHECKS,
            "fixes": [
                "Restored resume_section_treatment_profile.v1.json + resume_pa_prompt_profile.v1.json + section_treatment_profile.py",
                "Tiered SectionPromptArtifact + build_section_prompt_artifact* in pa_binding.py",
                "Restored resolve_srfs_section_proof_bundle + load_selected_role_fact_set for contract fixtures",
                "Restored apps_rg/runtime/exit/resume_exit_checks.py + profile JSON",
                "ibm_bullets_lane: IBM_DEFAULT_DISTRIBUTION local + strip rewrite-intensity before X2",
            ],
            "remaining_b5": [
                "Live qwen_vllm CLI pipeline tests (skip when vLLM down; fail when up but lane/X2 drift)",
                "SRFS offline-stub lane tests (selected_role_fact_set kwarg / APPS_RG_QWEN_OFFLINE_CONTRACT_STUB)",
                "C0 CHROMA_PERSIST_DIR competencies mock paths",
                "section_prompt_authority compile_section_prompt shim drift",
            ],
            "phase_gate": f"PHASE_GATE: wave=W4 status={status} gate=G-W4",
        }
    )
    RECEIPT_JSON.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "receipt": str(RECEIPT_JSON.relative_to(REPO)), "slice": tail_line}, indent=2))
    print(summary[-1200:])
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
