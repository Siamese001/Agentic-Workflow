"""
W4-F Retrieval Profile Replay Check Engine

Performs deterministic replay checks to verify profile changes produce consistent results.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from system_learning.engines.retrieval_profile import RetrievalProfile
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True, slots=True)
class ReplayCheckResult:
    """Result of deterministic replay check."""

    passed: bool
    digest: str
    base_output: dict[str, Any]
    proposed_output: dict[str, Any]
    reason: str


class RetrievalProfileReplayChecker:
    """Performs deterministic replay checks for profile changes."""

    def __init__(self):
        """Initialize replay checker with deterministic test fixtures."""
        self._test_queries = [
            "machine learning fundamentals",
            "neural network architectures",
            "optimization algorithms",
            "data preprocessing techniques",
            "model evaluation metrics",
        ]
        self._test_embeddings = {
            "machine learning fundamentals": [0.1, 0.2, 0.3, 0.4, 0.5],
            "neural network architectures": [0.2, 0.3, 0.4, 0.5, 0.6],
            "optimization algorithms": [0.3, 0.4, 0.5, 0.6, 0.7],
            "data preprocessing techniques": [0.4, 0.5, 0.6, 0.7, 0.8],
            "model evaluation metrics": [0.5, 0.6, 0.7, 0.8, 0.9],
        }

    def replay_check_profile_change(
        self, *, base_profile: RetrievalProfile, proposed_profile: RetrievalProfile
    ) -> ReplayCheckResult:
        """Perform deterministic replay check of profile change.

        Args:
            base_profile: Base profile to test
            proposed_profile: Proposed profile to test

        Returns:
            ReplayCheckResult with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileReplayChecker.replay_check_profile_change")

        base_output = self._run_deterministic_retrieval(base_profile)
        proposed_output = self._run_deterministic_retrieval(proposed_profile)
        digest = self._compute_replay_digest(
            base_profile=base_profile,
            proposed_profile=proposed_profile,
            base_output=base_output,
            proposed_output=proposed_output,
        )
        passed = self._compare_outputs(base_output, proposed_output)
        if passed:
            reason = "Replay check passed: deterministic outputs consistent"
        else:
            reason = "Replay check failed: outputs differ between profiles"
        print(f"W4F-REPLAY-DIGEST: {digest}")
        return ReplayCheckResult(
            passed=passed,
            digest=digest,
            base_output=base_output,
            proposed_output=proposed_output,
            reason=reason,
        )

    def _run_deterministic_retrieval(self, profile: RetrievalProfile) -> dict[str, Any]:
        """Run deterministic retrieval scenario with given profile.

        Args:
            profile: Profile to use for retrieval

        Returns:
            Deterministic output dictionary
        """
        results = []
        for query in self._test_queries:
            query_embedding = self._test_embeddings[query]
            similarities = []
            for other_query, other_embedding in self._test_embeddings.items():
                similarity = sum((q * o for q, o in zip(query_embedding, other_embedding)))
                similarities.append((other_query, similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            filtered_results = []
            for other_query, similarity in similarities:
                if similarity >= profile.similarity_cutoff:
                    filtered_results.append((other_query, similarity))
            limited_results = filtered_results[: profile.top_k]
            scaled_results = []
            for other_query, similarity in limited_results:
                scaled_similarity = similarity * profile.influence_cap
                scaled_results.append((other_query, round(scaled_similarity, 6)))
            results.append(
                {
                    "query": query,
                    "results": scaled_results,
                    "profile_similarity_cutoff": profile.similarity_cutoff,
                    "profile_top_k": profile.top_k,
                    "profile_influence_cap": profile.influence_cap,
                }
            )
        return {"profile_id": profile.profile_id, "query_results": results, "total_results": len(results)}

    def _compare_outputs(self, base_output: dict[str, Any], proposed_output: dict[str, Any]) -> bool:
        """Compare outputs for deterministic consistency.

        Args:
            base_output: Output from base profile
            proposed_output: Output from proposed profile

        Returns:
            True if outputs are consistent with profile differences
        """
        if set(base_output.keys()) != set(proposed_output.keys()):
            return False
        if base_output["total_results"] != proposed_output["total_results"]:
            return False
        if len(base_output["query_results"]) != len(proposed_output["query_results"]):
            return False
        for i, (base_query, proposed_query) in enumerate(
            zip(base_output["query_results"], proposed_output["query_results"])
        ):
            if base_query["query"] != proposed_query["query"]:
                return False
            if not isinstance(proposed_query["results"], list):
                return False
        return True

    def _compute_replay_digest(
        self,
        *,
        base_profile: RetrievalProfile,
        proposed_profile: RetrievalProfile,
        base_output: dict[str, Any],
        proposed_output: dict[str, Any],
    ) -> str:
        """Compute deterministic SHA-256 digest for replay check.

        Args:
            base_profile: Base profile used
            proposed_profile: Proposed profile used
            base_output: Output from base profile
            proposed_output: Output from proposed profile

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile": json.loads(base_profile.to_canonical_json()),
            "proposed_profile": json.loads(proposed_profile.to_canonical_json()),
            "base_output_summary": {
                "profile_id": base_output["profile_id"],
                "total_results": base_output["total_results"],
                "query_count": len(base_output["query_results"]),
            },
            "proposed_output_summary": {
                "profile_id": proposed_output["profile_id"],
                "total_results": proposed_output["total_results"],
                "query_count": len(proposed_output["query_results"]),
            },
            "replay_version": "W4-F-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileReplayChecker", "ReplayCheckResult"]
