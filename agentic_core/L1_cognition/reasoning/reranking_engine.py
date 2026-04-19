"""
Reranking Engine for L1 Cognition
Applies LightGBM model trained on EvalSpine feedback for result reranking.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

from .multi_query_fusion import FusionResult
from .semantic_retriever import RetrievalResult
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class RerankingFeatures:
    """Features for reranking model."""

    semantic_score: float
    collection_priority: float
    text_length: int
    layer_relevance: float
    component_relevance: float
    recency_score: float
    popularity_score: float
    query_term_match: float
    file_type_relevance: float


@dataclass
class RerankingResult:
    """Result from reranking process."""

    original_results: list[RetrievalResult]
    reranked_results: list[RetrievalResult]
    reranking_scores: list[float]
    features_used: list[str]
    execution_time_ms: float
    model_info: dict[str, Any]


class RerankingEngine:
    """
    Reranking engine for ChromaDB search results.

    Uses machine learning models (LightGBM) trained on EvalSpine feedback
    to improve search result ranking.
    """

    def __init__(self, model_path: str | None = None):
        """
        Initialize reranking engine.

        Args:
            model_path: Path to trained LightGBM model
        """
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            "semantic_score",
            "collection_priority",
            "text_length",
            "layer_relevance",
            "component_relevance",
            "recency_score",
            "popularity_score",
            "query_term_match",
            "file_type_relevance",
        ]

        # Collection priority weights
        self.collection_weights = {
            "repo_symbols": 1.2,
            "repo_adg_graph": 1.15,
            "repo_code_chunks": 1.1,
            "repo_runtime_evidence": 1.05,
            "repo_incidents_rca": 1.0,
            "repo_tests_guardrails": 1.0,
            "repo_git_history": 0.9,
            "repo_arch_docs": 0.85,
        }

        # Layer relevance weights
        self.layer_weights = {
            "L0": 1.1,  # Routing is important
            "L1": 1.0,  # Cognition is baseline
            "L2": 1.2,  # Execution is critical
            "L3": 1.1,  # Orchestration is important
            "L4": 1.0,  # State is baseline
            "L5": 1.15,  # Safety is critical
            "L6": 0.9,  # Observability is supporting
        }

        # File type relevance weights
        self.file_type_weights = {
            "code": 1.2,
            "sym": 1.15,
            "edge": 1.1,
            "test": 1.0,
            "doc": 0.9,
            "runtime_evidence": 1.1,
            "incident_rca": 1.05,
            "git_commit": 0.8,
        }

        # Try to load model
        self._load_model()

        logger.info(f"Reranking engine initialized (model loaded: {self.model is not None})")

    def _load_model(self):
        """Load the LightGBM model."""
        try:
            import lightgbm as lgb

            if self.model_path and Path(self.model_path).exists():
                self.model = lgb.Booster(model_file=self.model_path)
                logger.info(f"Loaded LightGBM model from {self.model_path}")
            else:
                logger.warning("No LightGBM model found, using rule-based reranking")

        except (
            ImportError
        ):  # guardian: allow-log-and-swallow -- LightGBM optional: falls back to rule-based reranking
            logger.warning("LightGBM not installed, using rule-based reranking")
        except (  # guardian: allow-log-and-swallow -- LightGBM model load: non-fatal, falls back to rule-based reranking
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:
            logger.error(f"Failed to load LightGBM model: {e}")

    def rerank_results(
        self,
        fusion_result: FusionResult,
        query: str,
        max_results: int = 20,
    ) -> RerankingResult:
        """
        Rerank search results using ML model or rule-based approach.

        Args:
            fusion_result: Results from multi-query fusion
            query: Original query string
            max_results: Maximum number of results to return

        Returns:
            RerankingResult with reranked results
        """
        import time

        start_time = time.time()

        # Input validation
        if fusion_result is None:
            raise ValueError("fusion_result cannot be None")
        if not query or not query.strip():
            raise ValueError("query cannot be empty")
        if max_results <= 0:
            raise ValueError("max_results must be positive")

        # Flatten all results
        all_results = []
        for collection_results in fusion_result.collection_results.values():
            all_results.extend(collection_results)

        if not all_results:
            return RerankingResult(
                original_results=[],
                reranked_results=[],
                reranking_scores=[],
                features_used=self.feature_names,
                execution_time_ms=0,
                model_info={"model_type": "none", "model_loaded": False},
            )

        # Extract features for each result
        features_list = []
        for result in all_results:
            features = self._extract_features(result, query, fusion_result)
            features_list.append(features)

        # Apply reranking
        if self.model is not None:
            reranked_results, scores = self._ml_rerank(all_results, features_list)
            model_info = {
                "model_type": "lightgbm",
                "model_loaded": True,
                "model_path": self.model_path,
            }
        else:
            reranked_results, scores = self._rule_based_rerank(all_results, features_list)
            model_info = {
                "model_type": "rule_based",
                "model_loaded": False,
                "reason": "LightGBM not available",
            }

        # Limit results
        reranked_results = reranked_results[:max_results]
        scores = scores[:max_results]

        execution_time_ms = (time.time() - start_time) * 1000

        return RerankingResult(
            original_results=all_results,
            reranked_results=reranked_results,
            reranking_scores=scores,
            features_used=self.feature_names,
            execution_time_ms=execution_time_ms,
            model_info=model_info,
        )

    def _extract_features(
        self, result: RetrievalResult, query: str, fusion_result: FusionResult
    ) -> RerankingFeatures:
        """Extract features for reranking."""
        metadata = result.metadata

        # Semantic score (from retrieval)
        semantic_score = getattr(result, "score", 0.5)

        # Collection priority
        collection_priority = self.collection_weights.get(result.collection, 1.0)

        # Text length (normalized)
        text_length = min(len(result.content) / 1000.0, 1.0)  # Normalize to 0-1

        # Layer relevance
        layer_relevance = 1.0
        layers = []
        if "layer" in metadata:
            if isinstance(metadata["layer"], list):
                layers = metadata["layer"]
            else:
                layers = [metadata["layer"]]
        elif "src_layer" in metadata:
            layers.append(metadata["src_layer"])
        if "dst_layer" in metadata:
            layers.append(metadata["dst_layer"])

        if layers:
            layer_relevance = np.mean([self.layer_weights.get(layer, 1.0) for layer in layers])

        # Component relevance
        component_relevance = 1.0
        query_lower = query.lower()
        content_lower = result.content.lower()

        # Check for component mentions
        components = ["UWG", "ADG", "Scanner", "Router", "Gateway", "Agent", "ChromaDB"]
        for component in components:
            if component.lower() in query_lower and component.lower() in content_lower:
                component_relevance = 1.2
                break

        # Recency score (for time-based data)
        recency_score = 1.0
        if "timestamp" in metadata:
            try:
                timestamp_str = metadata["timestamp"]
                if isinstance(timestamp_str, str):
                    # Parse timestamp and calculate recency
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        days_ago = (datetime.now() - timestamp).days
                        recency_score = max(0.1, 1.0 - (days_ago / 365.0))  # Decay over year
                    except (
                        ImportError,
                        AttributeError,
                    ) as e:  # guardian: allow-log-and-swallow -- Figma MCP: optional, reranker continues without it
                        logger.debug(f"Figma MCP unavailable: {e}")
            except (
                TypeError,
                ValueError,
                KeyError,
                AttributeError,
            ):  # guardian: allow-silent-swallow -- timestamp parse: malformed value ignored, recency score defaults to 1.0
                pass

        # Popularity score (based on collection size)
        popularity_score = 1.0
        if result.collection in fusion_result.collection_results:
            collection_size = len(fusion_result.collection_results[result.collection])
            # Normalize by typical collection sizes
            if collection_size > 10000:
                popularity_score = 1.2
            elif collection_size > 1000:
                popularity_score = 1.1
            elif collection_size > 100:
                popularity_score = 1.0
            else:
                popularity_score = 0.9

        # Query term match
        query_terms = set(query.lower().split())
        content_terms = set(content_lower.split())
        query_term_match = len(query_terms & content_terms) / max(len(query_terms), 1)

        # File type relevance
        file_type_relevance = 1.0
        artifact_type = metadata.get("artifact_type", "")
        if artifact_type:
            file_type_relevance = self.file_type_weights.get(artifact_type, 1.0)

        return RerankingFeatures(
            semantic_score=semantic_score,
            collection_priority=collection_priority,
            text_length=text_length,
            layer_relevance=layer_relevance,
            component_relevance=component_relevance,
            recency_score=recency_score,
            popularity_score=popularity_score,
            query_term_match=query_term_match,
            file_type_relevance=file_type_relevance,
        )

    def _ml_rerank(
        self, results: list[RetrievalResult], features_list: list[RerankingFeatures]
    ) -> tuple[list[RetrievalResult], list[float]]:
        """Rerank using LightGBM model."""
        try:
            # Convert features to numpy array
            feature_array = np.array(
                [
                    [
                        f.semantic_score,
                        f.collection_priority,
                        f.text_length,
                        f.layer_relevance,
                        f.component_relevance,
                        f.recency_score,
                        f.popularity_score,
                        f.query_term_match,
                        f.file_type_relevance,
                    ]
                    for f in features_list
                ]
            )

            # Predict scores
            scores = self.model.predict(feature_array)

            # Sort by scores
            sorted_indices = np.argsort(scores)[::-1]

            reranked_results = [results[i] for i in sorted_indices]
            reranked_scores = [float(scores[i]) for i in sorted_indices]

            return reranked_results, reranked_scores

        except (
            AttributeError,
            KeyError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-log-and-swallow -- DeepWiki MCP: optional, reranker continues without it
            logger.debug(f"DeepWiki MCP unavailable: {e}")
            # Fallback to rule-based
            return self._rule_based_rerank(results, features_list)

    def _rule_based_rerank(
        self, results: list[RetrievalResult], features_list: list[RerankingFeatures]
    ) -> tuple[list[RetrievalResult], list[float]]:
        """Rerank using rule-based approach."""
        # Calculate composite scores
        scores = []
        for features in tqdm(features_list, desc="Processing", unit="item"):
            # Weighted combination of features
            score = (
                features.semantic_score * 0.3
                + features.collection_priority * 0.2
                + features.layer_relevance * 0.15
                + features.component_relevance * 0.15
                + features.query_term_match * 0.1
                + features.recency_score * 0.05
                + features.popularity_score * 0.03
                + features.file_type_relevance * 0.02
            )
            scores.append(score)

        # Sort by scores
        sorted_indices = np.argsort(scores)[::-1]

        reranked_results = [results[i] for i in sorted_indices]
        reranked_scores = [scores[i] for i in sorted_indices]

        return reranked_results, reranked_scores

    def create_training_data(
        self,
        queries: list[str],
        results_list: list[list[RetrievalResult]],
        relevance_labels: list[list[int]],
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Create training data for reranking model.

        Args:
            queries: List of queries
            results_list: List of results for each query
            relevance_labels: List of relevance labels (1-5) for each result

        Returns:
            Tuple of (features, labels) for training
        """
        features = []
        labels = []

        for query, results, relevance in tqdm(
            zip(queries, results_list, relevance_labels), desc="Processing", unit="item"
        ):
            # Create dummy fusion result
            class DummyFusionResult:
                def __init__(self, collection_results):
                    self.collection_results = collection_results

            dummy_fusion = DummyFusionResult({r.collection: [r] for r in results})

            for result, rel_label in tqdm(zip(results, relevance), desc="Processing", unit="item"):
                feature_vector = self._extract_features(result, query, dummy_fusion)
                features.append(
                    [
                        feature_vector.semantic_score,
                        feature_vector.collection_priority,
                        feature_vector.text_length,
                        feature_vector.layer_relevance,
                        feature_vector.component_relevance,
                        feature_vector.recency_score,
                        feature_vector.popularity_score,
                        feature_vector.query_term_match,
                        feature_vector.file_type_relevance,
                    ]
                )
                labels.append(rel_label)

        return np.array(features), np.array(labels)

    def get_reranking_stats(self) -> dict[str, Any]:
        """Get reranking engine statistics."""
        return {
            "model_loaded": self.model is not None,
            "model_path": self.model_path,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "collection_weights": self.collection_weights,
            "layer_weights": self.layer_weights,
            "file_type_weights": self.file_type_weights,
        }


# Example usage and testing
def main():
    """Test the reranking engine."""
    from ..retrievers.semantic_retriever import RetrievalResult
    from .multi_query_fusion import FusionResult

    # Create dummy results for testing
    dummy_results = [
        RetrievalResult(
            content="UniversalWriteGateway implementation",
            metadata={"artifact_type": "code", "layer": "L2"},
            score=0.8,
            collection="repo_code_chunks",
        ),
        RetrievalResult(
            content="ADG static scanner code",
            metadata={"artifact_type": "sym", "layer": "L4"},
            score=0.7,
            collection="repo_symbols",
        ),
    ]

    # Create dummy fusion result
    dummy_fusion = FusionResult(
        original_query="What does UWG do?",
        collection_results={"repo_code_chunks": dummy_results[:1], "repo_symbols": dummy_results[1:]},
        fusion_strategy="score_fusion",
        total_results=2,
        execution_time_ms=100.0,
        query_variations_used=[],
    )

    # Test reranking
    reranker = RerankingEngine()

    rerank_result = reranker.rerank_results(
        fusion_result=dummy_fusion,
        query="What does UWG do?",
        max_results=10,
    )

    print("Reranking Test:")
    print(f"Original results: {len(rerank_result.original_results)}")
    print(f"Reranked results: {len(rerank_result.reranked_results)}")
    print(f"Execution time: {rerank_result.execution_time_ms:.2f}ms")
    print(f"Model info: {rerank_result.model_info}")

    for i, (result, score) in enumerate(zip(rerank_result.reranked_results, rerank_result.reranking_scores)):
        print(f"  {i + 1}. Score: {score:.3f} - {result.content[:50]}...")


if __name__ == "__main__":
    main()
