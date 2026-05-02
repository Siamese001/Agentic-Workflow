"""Regenerate artifacts/certification/integrated_runtime/latest/ bundle.

One-shot script. Drives the production entry point
``run_integrated_safe_reuse`` with the same SAFE-allow fixture used by
``tests/runtime/test_integrated_runtime_entrypoint_safe_reuse.py`` and
points ``artifact_dir`` at ``latest/`` so the canonical bundle on disk
reflects the current entrypoint behavior.

Use after any change to the entrypoint that affects emitted artifacts
(e.g., authority-binding field additions for RTC-REQ-015).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"


def main() -> int:
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
        run_integrated_safe_reuse,
    )
    from tools.certification.safety.deterministic_proof_stage import (
        DeterministicProofStage,
    )
    from tools.certification.safety.veto_orchestrator import VetoOrchestrator

    # Clean previous bundle
    if LATEST.exists():
        shutil.rmtree(LATEST)
    LATEST.mkdir(parents=True, exist_ok=True)

    user_q = "What is the capital of France?"
    cached_q = "Tell me the capital of France."
    namespace = "test_w2_allow"

    cache = SemanticCacheManager.get_instance()
    ctx = json.dumps(
        {
            "body_text": user_q,
            "namespace": namespace,
            "tenant_id": "",
            "policy_hash": "no-policy",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    cache.learn(
        ctx,
        namespace,
        {
            "text": "Paris.",
            "answer": "Paris.",
            "cached_query_text": cached_q,
        },
    )

    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    # This regen run uses DeterministicProofStage, which the
    # SyntheticTraceDetector classifies as fixture mode. Declare the
    # mode upfront so verify_spine_proof_bundle's production-only
    # invariant (no fixture/mock/synthetic flags when
    # runtime_mode=production) does not fail-close on a legitimate
    # structural fixture run.
    os.environ.setdefault("AGENTIC_CORE_RUNTIME_MODE", "fixture")
    proof = VetoOrchestrator(
        stages=[DeterministicProofStage(verdicts={(user_q, cached_q): "SAFE"})]
    )

    result = run_integrated_safe_reuse(
        {"body_text": user_q, "transport": "api"},
        namespace=namespace,
        tenant_id="",
        artifact_dir=LATEST,
        veto_orchestrator=proof,
    )

    print(f"[regen_integrated_runtime_latest] entrypoint_used={result.integrated_runtime_entrypoint_used}")
    print(f"  run_id={result.run_id}")
    print(f"  artifact_dir={LATEST.relative_to(REPO_ROOT)}")
    print(f"  artifact count={len(result.artifact_hashes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
