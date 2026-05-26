#!/usr/bin/env python3
"""Fast apps_rg contract harness — skips live CLI subprocess lanes (~minutes each).

Set APPS_RG_CONTRACT_HARNESS_FAST=1 and run structural/YAML/in-process tests only.
For live qwen_vllm lane proof, use run_contract_harness_live.py.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Track B filtered slice without live CLI modules.
DEFAULT_K = (
    "(competencies or prompt_judge or product_shape or executive_summary_x2 "
    "or unify_bullets or ibm_bullets or unify_narrative or ibm_narrative) "
    "and not contract_harness_live"
)

W5_SPOT = [
    "tests/_apps_contract/test_apps_rg_no_inline_prompt_authority.py",
    "tests/_apps_contract/test_apps_rg_srfs_w2_canonical_threading.py",
    "tests/_apps_contract/test_apps_rg_srfs_w5_prompt_hierarchy.py",
    "tests/_apps_contract/test_exec_summary_section_pipeline.py",
    "tests/_apps_contract/test_apps_rg_manual_section_review.py",
    "tests/_apps_contract/test_resume_section_treatment_profile.py",
    "tests/_apps_contract/test_pa_binding_role_tiering.py",
    "tests/_apps_contract/test_commercial_medium_claim_output_containment.py",
]


def _env() -> dict[str, str]:
    env = {
        **os.environ,
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": str(REPO),
        "APPS_RG_CONTRACT_HARNESS_FAST": "1",
        "APPS_RG_L2_PROVIDER_MODE": "live_allowed",
        "PYTEST_APPS_RG_LIVE_L2": "1",
    }
    chroma = REPO / "data" / "cache" / "chromadb"
    if chroma.is_dir():
        env["CHROMA_PERSIST_DIR"] = str(chroma.resolve())
    return env


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "spot").strip().lower()
    env = _env()
    base = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "pytest_timeout",
        "-q",
        "--tb=short",
        "--timeout=120",
        "-o",
        "addopts=",
    ]

    if mode == "spot":
        cmd = [*base, *W5_SPOT]
    elif mode == "slice":
        cmd = [*base, "tests/_apps_contract/", "-k", DEFAULT_K]
    else:
        print(f"usage: {sys.argv[0]} [spot|slice]", file=sys.stderr)
        return 2

    print("APPS_RG_CONTRACT_HARNESS_FAST=1 — live CLI lanes skipped", flush=True)
    proc = subprocess.run(cmd, cwd=REPO, env=env, check=False)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
