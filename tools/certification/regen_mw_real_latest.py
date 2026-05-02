"""Regen MW_REAL chain bundle at artifacts/certification/integrated_runtime/mw_real_latest."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_managed_workflow_real_run import (
    run_integrated_managed_workflow_real,
)


def main() -> int:
    out = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "mw_real_latest"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    run_integrated_managed_workflow_real(
        raw_request={"query": "mw real regen", "category": "test"},
        namespace="mw_real_test",
        tenant_id="t:mw-real-regen",
        artifact_dir=out,
    )
    print(f"[regen_mw_real_latest] wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
