"""R1A_EXACT_CACHE — integrated runtime entrypoint.

Drives the same governed cache-reuse spine as R1B but with EXACT-match
cache-key semantics rather than semantic-similarity reuse:

  R1B: ``d2_similarity`` is between 0.0 and 1.0; allow when it crosses
       the cache-policy threshold AND the safety veto agrees.
  R1A: cached query text is byte-identical to the live query, so
       ``d2_similarity == 1.0`` (exact) — there is no semantic
       interpolation, no veto-required substitution, and no near-miss
       reuse.

The chain artifacts are the same shape as R1B (so verifiers reuse
verify_integrated_runtime_*); the chain_kind tag distinguishes them
("R1A_EXACT_CACHE" vs "R1B"). The route_contract carries
``route_family="R1A_EXACT_CACHE"``. R1A may not borrow R1B's artifacts —
each R1A run has its own run_id / request_id / trace_root and its own
HOW trace + Fort Knox L7 evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
    SemanticCacheManager,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "R1A_EXACT_CACHE"
ROUTE_FAMILY = "R1A_EXACT_CACHE"


def run_integrated_exact_cache(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    artifact_dir: Path | str,
    veto_orchestrator: Any | None = None,
) -> IntegratedRunResult:
    """Drive the integrated R1A exact-cache runtime end-to-end.

    The caller MUST have seeded the cache with a query whose cached_query_text
    is byte-identical to ``raw_request['body_text']``. This entrypoint
    asserts the resulting safe-reuse decision reports d2_similarity==1.0;
    if not, the chain still emits but the verifier will fail-closed.
    """
    return run_integrated_safe_reuse(
        raw_request,
        namespace=namespace,
        tenant_id=tenant_id,
        artifact_dir=artifact_dir,
        veto_orchestrator=veto_orchestrator,
        chain_kind=CHAIN_KIND,
        route_family_override=ROUTE_FAMILY,
        extra_route_contract_fields={
            "route_family_proof_class": "REAL_RUNTIME",
            "exact_cache_match_required": True,
        },
    )


__all__ = ["run_integrated_exact_cache", "CHAIN_KIND", "ROUTE_FAMILY"]
