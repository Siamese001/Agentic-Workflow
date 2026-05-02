"""Regenerate the UWG_BLOCK_PATH chain bundle.

Writes to
``artifacts/certification/integrated_runtime/uwg_block_latest/``.

This regen drives a real blocked commit through DurableWriteGateway
inside the integrated-runtime chain (NOT a fixture test). The chain
emits the standard 20 R1B-shaped artifacts plus the two integrated
extras: ``commit_request.json`` and ``uwg_blocked_commit_receipt.json``.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LATEST = (
    REPO_ROOT
    / "artifacts"
    / "certification"
    / "integrated_runtime"
    / "uwg_block_latest"
)


def main() -> int:
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    from agentic_core.runtime.entrypoints.integrated_uwg_block_run import (
        run_integrated_uwg_block,
    )
    from tools.certification.safety.deterministic_proof_stage import (
        DeterministicProofStage,
    )
    from tools.certification.safety.veto_orchestrator import VetoOrchestrator

    if LATEST.exists():
        shutil.rmtree(LATEST)
    LATEST.mkdir(parents=True, exist_ok=True)

    user_q = "What is the capital of France?"
    cached_q = "Tell me the capital of France."
    namespace = "test_w2_uwg_block"

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
        {"text": "Paris.", "answer": "Paris.", "cached_query_text": cached_q},
    )

    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    os.environ.setdefault("AGENTIC_CORE_RUNTIME_MODE", "fixture")
    proof = VetoOrchestrator(
        stages=[DeterministicProofStage(verdicts={(user_q, cached_q): "SAFE"})]
    )

    result = run_integrated_uwg_block(
        {"body_text": user_q, "transport": "api"},
        namespace=namespace,
        tenant_id="",
        artifact_dir=LATEST,
        veto_orchestrator=proof,
        attempting_surface="L0",
        target_surface="memory",
        block_reason="non_uwg_surface_attempted_direct_write",
    )

    print(
        f"[regen_uwg_block_latest] entrypoint_used="
        f"{result.integrated_runtime_entrypoint_used}"
    )
    print(f"  run_id={result.run_id}")
    print(f"  artifact_dir={LATEST.relative_to(REPO_ROOT)}")
    print(f"  artifact_count={len(result.artifact_hashes)} (+ 2 UWG-block extras)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
