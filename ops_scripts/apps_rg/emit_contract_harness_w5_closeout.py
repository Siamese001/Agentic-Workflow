#!/usr/bin/env python3
"""W5: filtered ``tests/_apps_contract`` gate + closeout receipt."""
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
RECEIPT_JSON = REPO / "docs/reports/apps_rg/contract_harness_modernization_w5_receipt.json"
JUNIT_XML = REPO / "docs/reports/apps_rg/contract_harness_w5_junit.xml"
SLICE_LOG = REPO / "docs/reports/apps_rg/w5_filtered_slice_latest.txt"

PYTEST_K = (
    "competencies or prompt_judge or product_shape or executive_summary_x2 "
    "or unify_bullets or ibm_bullets or unify_narrative or ibm_narrative"
)

W5_SPOT_CHECKS = [
    "tests/_apps_contract/test_apps_rg_no_inline_prompt_authority.py",
    "tests/_apps_contract/test_apps_rg_srfs_w2_canonical_threading.py",
    "tests/_apps_contract/test_apps_rg_srfs_w5_prompt_hierarchy.py",
    "tests/_apps_contract/test_exec_summary_section_pipeline.py::test_in_process_harness_product_shape_gates_pass",
    "tests/_apps_contract/test_apps_rg_manual_section_review.py",
    "tests/_apps_contract/test_resume_section_treatment_profile.py",
    "tests/_apps_contract/test_pa_binding_role_tiering.py",
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


def _qwen_live() -> bool:
    try:
        from tests._apps_contract.lane_cli_common import (  # guardian: allow-layer-violation -- ops closeout probes contract harness live availability
            qwen_live_available,
        )

        return bool(qwen_live_available())
    except Exception:
        return False


def main() -> int:
    from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links

    env = {
        **dict(__import__("os").environ),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": str(REPO),
        "APPS_RG_CONTRACT_HARNESS_FAST": "1",
        "APPS_RG_L2_PROVIDER_MODE": "live_allowed",
        "PYTEST_APPS_RG_LIVE_L2": "1",
    }
    chroma = REPO / "data" / "cache" / "chromadb"
    if chroma.is_dir():
        env["CHROMA_PERSIST_DIR"] = str(chroma.resolve())

    spot_cmd = [sys.executable, "-m", "pytest", *W5_SPOT_CHECKS, "-q", "--tb=no", "-o", "addopts="]
    spot = subprocess.run(spot_cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)

    slice_k = f"({PYTEST_K}) and not contract_harness_live"
    slice_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/_apps_contract/",
        "-k",
        slice_k,
        "--junitxml",
        str(JUNIT_XML),
        "-q",
        "--tb=no",
        "-o",
        "addopts=",
    ]
    try:
        sliced = subprocess.run(
            slice_cmd, cwd=REPO, capture_output=True, text=True, timeout=7200, env=env, check=False
        )
    except subprocess.TimeoutExpired as exc:
        sliced = subprocess.CompletedProcess(
            slice_cmd,
            returncode=124,
            stdout=(exc.stdout or "") if exc.stdout else "",
            stderr=(exc.stderr or "") if exc.stderr else "filtered slice timed out after 7200s",
        )
    summary = (sliced.stdout or "") + (sliced.stderr or "")
    SLICE_LOG.write_text(summary, encoding="utf-8")
    tail_line = ""
    for line in summary.splitlines():
        if "failed" in line and "passed" in line:
            tail_line = line.strip()

    spot_ok = spot.returncode == 0
    slice_ok = sliced.returncode == 0
    qwen_live = _qwen_live()

    slice_timed_out = sliced.returncode == 124
    if spot_ok and slice_ok:
        status = "PASS"
    elif spot_ok and (slice_timed_out or (not slice_ok and qwen_live)):
        status = "PARTIAL"
    elif spot_ok or slice_ok:
        status = "PARTIAL"
    else:
        status = "FAIL"

    manifest: dict = {
        "plan_id": PLAN_ID,
        "wave": "W5",
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "qwen_vllm_live": qwen_live,
        "pytest_k": PYTEST_K,
        "spot_checks": W5_SPOT_CHECKS,
        "spot_exit_code": spot.returncode,
        "filtered_slice_exit_code": sliced.returncode,
        "filtered_slice_summary": tail_line,
        "artifacts": [
            str(RECEIPT_JSON.relative_to(REPO)).replace("\\", "/"),
            str(JUNIT_XML.relative_to(REPO)).replace("\\", "/"),
            str(SLICE_LOG.relative_to(REPO)).replace("\\", "/"),
        ],
        "notes": (
            "Live qwen_vllm subprocess lanes skip when VLLM is unreachable; "
            "in-process harness + YAML/PA contracts must pass for W5 spot checks."
        ),
    }
    if not qwen_live and not slice_ok:
        manifest["blocked_reason"] = "VLLM_BASE_URL unreachable — live CLI contract lanes skipped or failed"

    enrich_manifest_links(manifest)
    RECEIPT_JSON.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
