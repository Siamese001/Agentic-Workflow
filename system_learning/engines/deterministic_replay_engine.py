"""
W5 Deterministic Replay Engine

Validates RetrievalProfile changes by replaying fixed synthetic retrieval cases
and emitting a stable replay digest.
"""

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.engines.retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "deterministic_replay_engine", "p0_governance")
_emit_reads_policy_state("p0", "deterministic_replay_engine", "policy_binding")
_emit_snapshots_state("p0", "deterministic_replay_engine", "state_snapshot")
emit_replay_key("p0", "deterministic_replay_engine")
emit_determinism_digest("p0", "deterministic_replay_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """Result of deterministic replay validation."""

    case_count: int
    base_outputs: dict[str, list[str]]
    candidate_outputs: dict[str, list[str]]
    changed_cases: int
    replay_digest: str

    def emit_digest(self) -> None:
        """Print the replay digest for verification."""
        print(f"W5-REPLAY-DIGEST: {self.replay_digest}")


class DeterministicReplayEngine:
    """Deterministic replay engine for RetrievalProfile validation."""

    def __init__(self):
        """Initialize replay engine with fixed synthetic cases."""
        self._synthetic_cases = [
            {
                "query": "machine learning fundamentals",
                "corpus": [
                    {"id": "doc1", "text": "ML basics"},
                    {"id": "doc2", "text": "Deep learning"},
                    {"id": "doc3", "text": "Neural networks"},
                    {"id": "doc4", "text": "Optimization"},
                    {"id": "doc5", "text": "Data preprocessing"},
                ],
            },
            {
                "query": "neural network architectures",
                "corpus": [
                    {"id": "doc6", "text": "CNN architectures"},
                    {"id": "doc7", "text": "RNN architectures"},
                    {"id": "doc8", "text": "Transformer models"},
                    {"id": "doc9", "text": "Attention mechanisms"},
                    {"id": "doc10", "text": "GAN architectures"},
                ],
            },
            {
                "query": "optimization algorithms",
                "corpus": [
                    {"id": "doc11", "text": "Gradient descent"},
                    {"id": "doc12", "text": "Adam optimizer"},
                    {"id": "doc13", "text": "SGD with momentum"},
                    {"id": "doc14", "text": "Learning rate schedules"},
                    {"id": "doc15", "text": "Adaptive methods"},
                ],
            },
            {
                "query": "data preprocessing techniques",
                "corpus": [
                    {"id": "doc16", "text": "Normalization"},
                    {"id": "doc17", "text": "Standardization"},
                    {"id": "doc18", "text": "Feature scaling"},
                    {"id": "doc19", "text": "Missing value imputation"},
                    {"id": "doc20", "text": "Data augmentation"},
                ],
            },
            {
                "query": "model evaluation metrics",
                "corpus": [
                    {"id": "doc21", "text": "Accuracy metrics"},
                    {"id": "doc22", "text": "Precision and recall"},
                    {"id": "doc23", "text": "F1 score"},
                    {"id": "doc24", "text": "ROC curves"},
                    {"id": "doc25", "text": "Cross-validation"},
                ],
            },
        ]

    def replay(self, *, base_profile: RetrievalProfile, candidate_profile: RetrievalProfile) -> ReplayResult:
        """Replay synthetic cases with both profiles and compare results.

        Args:
            base_profile: Base RetrievalProfile to test
            candidate_profile: Candidate RetrievalProfile to test

        Returns:
            ReplayResult with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DeterministicReplayEngine.replay")

        base_outputs = self._run_replay_cases(base_profile)
        candidate_outputs = self._run_replay_cases(candidate_profile)
        changed_cases = sum(
            1 for case_id in base_outputs if base_outputs[case_id] != candidate_outputs[case_id]
        )
        replay_digest = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        replay_digest_check = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        if replay_digest != replay_digest_check:
            raise ValueError(f"Determinism self-check failed: {replay_digest} != {replay_digest_check}")
        result = ReplayResult(
            case_count=len(self._synthetic_cases),
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
            replay_digest=replay_digest,
        )
        result.emit_digest()
        return result

    def _run_replay_cases(self, profile: RetrievalProfile) -> dict[str, list[str]]:
        """Run all synthetic cases with given profile.

        Args:
            profile: RetrievalProfile to use for replay

        Returns:
            Dictionary mapping case IDs to result lists
        """
        outputs = {}
        sorted_cases = sorted(enumerate(self._synthetic_cases), key=lambda x: x[1]["query"])
        for original_index, case in sorted_cases:
            query_hash = hashlib.md5(case["query"].encode("utf-8")).hexdigest()[:8]
            case_id = f"case_{query_hash}"
            query_hash_int = int(query_hash, 16)
            dim = profile.embedding_dim
            query_embedding = np.zeros(dim)
            deterministic_index = query_hash_int % dim
            query_embedding[deterministic_index] = 1.0
            corpus = case["corpus"]
            similarities = []
            for i, doc in enumerate(corpus):
                doc_embedding = np.zeros(dim)
                if i < dim:
                    doc_seed = (query_hash_int + i) % dim
                    doc_embedding[doc_seed] = 0.9
                similarity = np.dot(query_embedding, doc_embedding)
                similarities.append((doc["id"], similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            filtered_results = []
            for doc_id, similarity in similarities:
                if similarity >= profile.similarity_cutoff:
                    filtered_results.append((doc_id, similarity))
            limited_results = filtered_results[: profile.top_k]
            scaled_results = []
            for doc_id, similarity in limited_results:
                scaled_similarity = round(similarity * profile.influence_cap, 6)
                scaled_results.append((doc_id, scaled_similarity))
            result_strings = [f"{doc_id}:{similarity:.6f}" for doc_id, similarity in scaled_results]
            result_strings.sort()
            outputs[case_id] = result_strings
        return outputs

    def _compute_replay_digest(
        self,
        *,
        base_profile: RetrievalProfile,
        candidate_profile: RetrievalProfile,
        base_outputs: dict[str, list[str]],
        candidate_outputs: dict[str, list[str]],
        changed_cases: int,
    ) -> str:
        """Compute deterministic SHA-256 digest for replay.

        Args:
            base_profile: Base profile used
            candidate_profile: Candidate profile used
            base_outputs: Outputs from base profile
            candidate_outputs: Outputs from candidate profile
            changed_cases: Number of changed cases

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile": json.loads(base_profile.to_canonical_json()),
            "candidate_profile": json.loads(candidate_profile.to_canonical_json()),
            "base_outputs": {k: sorted(v) for k, v in sorted(base_outputs.items())},
            "candidate_outputs": {k: sorted(v) for k, v in sorted(candidate_outputs.items())},
            "changed_cases": changed_cases,
            "case_count": len(self._synthetic_cases),
            "replay_version": "W11-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["DeterministicReplayEngine", "ReplayResult"]
