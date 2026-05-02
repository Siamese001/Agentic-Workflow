"""Regen R4_SINGLE_ACTION chain bundle at artifacts/certification/integrated_runtime/r4_latest."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_single_action_run import (
    run_integrated_single_action,
)


def main() -> int:
    out = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "r4_latest"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    run_integrated_single_action(
        raw_request={"query": "r4 single action regen", "category": "test"},
        namespace="r4_single_action_test",
        tenant_id="t:r4-regen",
        artifact_dir=out,
    )
    print(f"[regen_r4_latest] wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
