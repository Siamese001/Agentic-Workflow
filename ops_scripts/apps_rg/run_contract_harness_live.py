#!/usr/bin/env python3
"""Live apps_rg contract harness — subprocess lanes only (serial; do not xdist)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

LIVE_K = "contract_harness_live"
LIVE_PATHS = [
    "tests/_apps_contract/test_ibm_bullets_section_pipeline.py",
    "tests/_apps_contract/test_unify_bullets_section_pipeline.py",
    "tests/_apps_contract/test_unify_narrative_section_pipeline.py",
    "tests/_apps_contract/test_ibm_bullets_runtime_slice.py",
    "tests/_apps_contract/test_unify_narrative_runtime_slice.py",
]


def main() -> int:
    env = {
        **os.environ,
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": str(REPO),
        "APPS_RG_L2_PROVIDER_MODE": "live_allowed",
        "PYTEST_APPS_RG_LIVE_L2": "1",
    }
    env.pop("APPS_RG_CONTRACT_HARNESS_FAST", None)
    chroma = REPO / "data" / "cache" / "chromadb"
    if chroma.is_dir():
        env["CHROMA_PERSIST_DIR"] = str(chroma.resolve())

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *LIVE_PATHS,
        "-m",
        LIVE_K,
        "-q",
        "--tb=short",
        "--timeout=900",
        "-o",
        "addopts=",
    ]
    print("Live contract harness (serial) — expect tens of minutes with vLLM up", flush=True)
    return int(
        subprocess.run(cmd, cwd=REPO, env=env, check=False).returncode
    )


if __name__ == "__main__":
    raise SystemExit(main())
