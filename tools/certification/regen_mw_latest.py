"""Regenerate artifacts/certification/integrated_runtime/mw_latest/ bundle.

One-shot driver for the structural-only MANAGED_WORKFLOW entry point.
Produces a fresh MW chain under ``mw_latest/`` so the CI verifiers
(dispatching on ``chain_kind``) can run against a known-good MW run.

Use after any change affecting the MW emitter, MW chain linkage, or
static DAG registry.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MW_LATEST = (
    REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "mw_latest"
)


def main() -> int:
    from agentic_core.runtime.entrypoints.integrated_managed_workflow_run import (
        run_integrated_managed_workflow,
    )

    if MW_LATEST.exists():
        shutil.rmtree(MW_LATEST)
    MW_LATEST.mkdir(parents=True, exist_ok=True)

    # Structural-only MW runs are fixture-mode by construction: L2 is
    # noop, no real tool/model invocation. Declare that upfront so the
    # spine verifier does not fail-close on production-only invariants.
    os.environ.setdefault("AGENTIC_CORE_RUNTIME_MODE", "fixture")
    os.environ.setdefault("AGENTIC_CORE_FIXTURE_MODE", "1")

    result = run_integrated_managed_workflow(
        {"body_text": "mw demo request", "transport": "api"},
        namespace="mw_demo",
        tenant_id="",
        artifact_dir=MW_LATEST,
    )

    print(
        f"[regen_mw_latest] entrypoint_used="
        f"{result['integrated_runtime_entrypoint_used']}"
    )
    print(f"  run_id={result['run_id']}")
    print(f"  artifact_dir={MW_LATEST.relative_to(REPO_ROOT)}")
    print(f"  chain_kind={result['chain_kind']}")
    print(f"  dag_id={result['dag_id']}")
    print(f"  dag_sha256={result['dag_sha256']}")
    print(f"  artifact_count={len(result['artifact_hashes'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
