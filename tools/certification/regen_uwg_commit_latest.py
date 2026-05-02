"""Regen UWG_COMMIT_PATH chain bundle at artifacts/certification/integrated_runtime/uwg_commit_latest."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_uwg_commit_run import (
    run_integrated_uwg_commit,
)


def main() -> int:
    out = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "uwg_commit_latest"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    run_integrated_uwg_commit(
        raw_request={"query": "uwg commit path regen", "category": "test"},
        namespace="uwg_commit_test",
        tenant_id="t:uwg-commit-regen",
        artifact_dir=out,
    )
    print(f"[regen_uwg_commit_latest] wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
