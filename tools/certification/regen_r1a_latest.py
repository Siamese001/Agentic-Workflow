"""Regenerate the R1A_EXACT_CACHE chain bundle.

Writes to ``artifacts/certification/integrated_runtime/r1a_latest/``.
Drives the production-grade R1A entrypoint with a deterministic
exact-cache hit (cached query == live query, byte-identical).
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
    REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "r1a_latest"
)


def main() -> int:
    from agentic_core.L0_routing.reasoning.route_gates import canonical_request_hash
    from agentic_core.L4_state.utils.memory.l1_exact_cache import (
        get_global_l1_cache,
    )
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    from agentic_core.runtime.entrypoints.integrated_exact_cache_run import (
        run_integrated_exact_cache,
    )
    from tools.certification.safety.deterministic_proof_stage import (
        DeterministicProofStage,
    )
    from tools.certification.safety.veto_orchestrator import VetoOrchestrator

    if LATEST.exists():
        shutil.rmtree(LATEST)
    LATEST.mkdir(parents=True, exist_ok=True)

    # R1A: D1 exact-cache hit. The L1ExactCache key is
    # ``canonical_request_hash(request)`` — we seed it directly so the
    # runtime D1 lookup hits and selects R1A (not R1B's D2 semantic).
    user_q = "What is the capital of France?"
    namespace = "test_w2_r1a_exact"

    request = {
        "body_text": user_q,
        "namespace": namespace,
        "tenant_id": "",
        "policy_hash": "no-policy",
    }
    request_hash = canonical_request_hash(request)

    # Enable D1 BEFORE seeding so the hash is computed under the same
    # gate semantics as the runtime lookup.
    os.environ["EXACT_CACHE_D1_ENABLED"] = "1"
    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    os.environ.setdefault("AGENTIC_CORE_RUNTIME_MODE", "fixture")

    # Seed L1ExactCache: cache.set(query, response) keys by
    # _generate_key(query) so we pass the canonical_request_hash as the
    # query — the runtime check passes the same value as the lookup key.
    l1 = get_global_l1_cache()
    l1.set(
        request_hash,
        json.dumps(
            {"text": "Paris.", "answer": "Paris.", "cached_query_text": user_q},
            separators=(",", ":"),
        ),
    )

    # Also seed the semantic cache so D2 can fall through if D1 is
    # disabled in any nested call site (defensive).
    cache = SemanticCacheManager.get_instance()
    cache.learn(
        json.dumps(request, sort_keys=True, separators=(",", ":")),
        namespace,
        {"text": "Paris.", "answer": "Paris.", "cached_query_text": user_q},
    )
    proof = VetoOrchestrator(
        stages=[DeterministicProofStage(verdicts={(user_q, user_q): "SAFE"})]
    )

    result = run_integrated_exact_cache(
        {"body_text": user_q, "transport": "api"},
        namespace=namespace,
        tenant_id="",
        artifact_dir=LATEST,
        veto_orchestrator=proof,
    )

    print(
        f"[regen_r1a_latest] entrypoint_used={result.integrated_runtime_entrypoint_used}"
    )
    print(f"  run_id={result.run_id}")
    print(f"  artifact_dir={LATEST.relative_to(REPO_ROOT)}")
    print(f"  artifact_count={len(result.artifact_hashes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
