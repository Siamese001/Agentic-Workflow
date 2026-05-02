"""Regen R3_GROUNDED_READ chain bundle at artifacts/certification/integrated_runtime/r3_latest."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_grounded_read_run import (
    run_integrated_grounded_read,
)


def main() -> int:
    out = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "r3_latest"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    run_integrated_grounded_read(
        raw_request={"query": "what does the L7 auditability plane emit", "category": "factual"},
        namespace="r3_grounded_read_test",
        tenant_id="t:r3-regen",
        artifact_dir=out,
        query="what does the L7 auditability plane emit",
    )
    print(f"[regen_r3_latest] wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
