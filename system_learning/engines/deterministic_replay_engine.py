"""
W5 Deterministic Replay Engine

Validates RetrievalProfile changes by replaying fixed synthetic retrieval cases
and emitting a stable replay digest.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from system_learning.engines.retrieval_profile import RetrievalProfile


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """Result of deterministic replay validation."""
    case_count: int
    base_outputs: Dict[str, List[str]]
    candidate_outputs: Dict[str, List[str]]
    changed_cases: int
    replay_digest: str
    
    def emit_digest(self) -> None:
        """Print the replay digest for verification."""
        print(f"W5-REPLAY-DIGEST: {self.replay_digest}")


class DeterministicReplayEngine:
    """Deterministic replay engine for RetrievalProfile validation."""
    
    def __init__(self):
        """Initialize replay engine with fixed synthetic cases."""
        # Fixed synthetic retrieval cases for deterministic testing
        self._synthetic_cases = [
            {
                "query": "machine learning fundamentals",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                "corpus": [
                    {"id": "doc1", "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "text": "ML basics"},
                    {"id": "doc2", "embedding": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "text": "Deep learning"},
                    {"id": "doc3", "embedding": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], "text": "Neural networks"},
                    {"id": "doc4", "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], "text": "Optimization"},
                    {"id": "doc5", "embedding": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], "text": "Data preprocessing"},
                ],
            },
            {
                "query": "neural network architectures",
                "embedding": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                "corpus": [
                    {"id": "doc6", "embedding": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "text": "CNN architectures"},
                    {"id": "doc7", "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "text": "RNN architectures"},
                    {"id": "doc8", "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], "text": "Transformer models"},
                    {"id": "doc9", "embedding": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "text": "Attention mechanisms"},
                    {"id": "doc10", "embedding": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1], "text": "GAN architectures"},
                ],
            },
            {
                "query": "optimization algorithms",
                "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "corpus": [
                    {"id": "doc11", "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], "text": "Gradient descent"},
                    {"id": "doc12", "embedding": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "text": "Adam optimizer"},
                    {"id": "doc13", "embedding": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1], "text": "SGD with momentum"},
                    {"id": "doc14", "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "text": "Learning rate schedules"},
                    {"id": "doc15", "embedding": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2], "text": "Adaptive methods"},
                ],
            },
            {
                "query": "data preprocessing techniques",
                "embedding": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
                "corpus": [
                    {"id": "doc16", "embedding": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1], "text": "Normalization"},
                    {"id": "doc17", "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], "text": "Standardization"},
                    {"id": "doc18", "embedding": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2], "text": "Feature scaling"},
                    {"id": "doc19", "embedding": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "text": "Missing value imputation"},
                    {"id": "doc20", "embedding": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3], "text": "Data augmentation"},
                ],
            },
            {
                "query": "model evaluation metrics",
                "embedding": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
                "corpus": [
                    {"id": "doc21", "embedding": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2], "text": "Accuracy metrics"},
                    {"id": "doc22", "embedding": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1], "text": "Precision and recall"},
                    {"id": "doc23", "embedding": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3], "text": "F1 score"},
                    {"id": "doc24", "embedding": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], "text": "ROC curves"},
                    {"id": "doc25", "embedding": [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4], "text": "Cross-validation"},
                ],
            },
        ]
    
    def replay(
        self,
        *,
        base_profile: RetrievalProfile,
        candidate_profile: RetrievalProfile,
    ) -> ReplayResult:
        """Replay synthetic cases with both profiles and compare results.
        
        Args:
            base_profile: Base RetrievalProfile to test
            candidate_profile: Candidate RetrievalProfile to test
            
        Returns:
            ReplayResult with deterministic digest
        """
        # Run replay with base profile
        base_outputs = self._run_replay_cases(base_profile)
        
        # Run replay with candidate profile
        candidate_outputs = self._run_replay_cases(candidate_profile)
        
        # Count changed cases
        changed_cases = sum(
            1 for case_id in base_outputs
            if base_outputs[case_id] != candidate_outputs[case_id]
        )
        
        # Compute deterministic digest with self-check
        replay_digest = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        
        # Determinism self-check: compute digest twice and assert identical
        replay_digest_check = self._compute_replay_digest(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
        )
        
        if replay_digest != replay_digest_check:
            raise ValueError(
                f"Determinism self-check failed: {replay_digest} != {replay_digest_check}"
            )
        
        result = ReplayResult(
            case_count=len(self._synthetic_cases),
            base_outputs=base_outputs,
            candidate_outputs=candidate_outputs,
            changed_cases=changed_cases,
            replay_digest=replay_digest,
        )
        
        # Emit digest for verification
        result.emit_digest()
        
        return result
    
    def _run_replay_cases(self, profile: RetrievalProfile) -> Dict[str, List[str]]:
        """Run all synthetic cases with given profile.
        
        Args:
            profile: RetrievalProfile to use for replay
            
        Returns:
            Dictionary mapping case IDs to result lists
        """
        outputs = {}
        
        # Process cases in stable order (sorted by query for determinism)
        sorted_cases = sorted(enumerate(self._synthetic_cases), key=lambda x: x[1]["query"])
        
        for original_index, case in sorted_cases:
            # Use stable case ID based on query content hash
            query_hash = hashlib.md5(case["query"].encode('utf-8')).hexdigest()[:8]
            case_id = f"case_{query_hash}"
            query_embedding = case["embedding"]
            corpus = case["corpus"]
            
            # Compute similarities (deterministic dot product)
            similarities = []
            for doc in corpus:
                # Dot product similarity
                similarity = sum(q * d for q, d in zip(query_embedding, doc["embedding"]))
                similarities.append((doc["id"], similarity))
            
            # Sort by similarity (descending) - stable sorting
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Apply profile filters
            filtered_results = []
            for doc_id, similarity in similarities:
                if similarity >= profile.similarity_cutoff:
                    filtered_results.append((doc_id, similarity))
            
            # Apply top_k limit
            limited_results = filtered_results[:profile.top_k]
            
            # Apply influence cap (scale similarity)
            scaled_results = []
            for doc_id, similarity in limited_results:
                scaled_similarity = round(similarity * profile.influence_cap, 6)
                scaled_results.append((doc_id, scaled_similarity))
            
            # Convert to string list for deterministic comparison
            result_strings = [
                f"{doc_id}:{similarity:.6f}"
                for doc_id, similarity in scaled_results
            ]
            
            # Sort results for stable ordering
            result_strings.sort()
            
            outputs[case_id] = result_strings
        
        return outputs
    
    def _compute_replay_digest(
        self,
        *,
        base_profile: RetrievalProfile,
        candidate_profile: RetrievalProfile,
        base_outputs: Dict[str, List[str]],
        candidate_outputs: Dict[str, List[str]],
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
        # Create canonical representation with stable ordering
        data = {
            "base_profile": json.loads(base_profile.to_canonical_json()),
            "candidate_profile": json.loads(candidate_profile.to_canonical_json()),
            "base_outputs": {k: sorted(v) for k, v in sorted(base_outputs.items())},
            "candidate_outputs": {k: sorted(v) for k, v in sorted(candidate_outputs.items())},
            "changed_cases": changed_cases,
            "case_count": len(self._synthetic_cases),
            "replay_version": "W5-v1.0",
        }
        
        # Serialize to canonical JSON
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        
        # Compute SHA-256 digest
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# Export public interface
__all__ = [
    'DeterministicReplayEngine',
    'ReplayResult',
]
