"""
C0 Retrieval Reranker

LightGBM model for reranking retrieved documents based on relevance,
quality, and usage patterns to improve retrieval precision.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

from ..config.model_registry import DecisionMode
from ..features.c0_features import C0FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class C0RetrievalReranker(BaseMLModel):
    """
    LightGBM model for C0 retrieval reranking.

    Reranks retrieved documents based on:
    - Query-document similarity and semantic match
    - Document quality (authority, completeness, reliability)
    - Temporal factors (recency, currency)
    - Usage patterns and popularity
    - System performance (cache efficiency)
    - Domain-specific relevance signals

    Always operates in advisory mode - final ranking decisions remain with C0.
    """

    def __init__(self, model_file_path: Path | None = None):
        if lgb is None:
            raise ImportError("LightGBM is required for C0RetrievalRanker")

        super().__init__(
            model_name="c0_retrieval_reranker",
            model_version="1.0",
            model_type="lightgbm",
            prediction_type=PredictionType.REGRESSION,  # Predict relevance score
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = C0FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.model = None
        self.feature_names = None
        self.feature_importances = None

        # Default thresholds
        self.threshold_config = {
            "score_threshold": 0.5,
            "min_relevance": 0.3,
            "max_documents": 100,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the LightGBM model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.model = model_data.get("model")
            self.feature_names = model_data.get("feature_names", [])
            self.feature_importances = model_data.get("feature_importances", [])
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            if self.model is None:
                raise ValueError("No model found in saved file")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        if self.model is None:
            raise RuntimeError("No model to save")

        model_data = {
            "model": self.model,
            "feature_names": self.feature_names,
            "feature_importances": self.feature_importances,
            "threshold_config": self.threshold_config,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "feature_schema_digest": self.feature_schema.schema_digest,
                "saved_at": datetime.now().isoformat(),
                "lightgbm_params": getattr(self.model, "params", {}),
            },
        }

        safe_pickle_dump(model_data, model_file_path)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict relevance score for document reranking.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Relevance score prediction with full metadata
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Preprocess features
        processed_features, preprocessing_steps = self.preprocess_features(model_input.features)
        model_input.preprocessing_applied = preprocessing_steps

        # Extract features in correct order
        feature_vector = self._extract_feature_vector(processed_features)

        if feature_vector is None:
            # Failed to extract features
            return self.create_prediction(
                prediction=0.3,  # Low default relevance
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # LightGBM prediction
            relevance_score = self.model.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Ensure score is in valid range
            relevance_score = float(np.clip(relevance_score, 0.0, 1.0))

            # Calculate confidence based on prediction certainty
            confidence = self._calculate_prediction_confidence(feature_vector, relevance_score)

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("score_threshold", 0.5)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=relevance_score,
                    confidence=confidence,
                    threshold_used=threshold_used,
                ),
            )

            # Determine final decision mode
            final_decision_mode = decision_mode
            if not passes_threshold or relevance_score < self.threshold_config.get("min_relevance", 0.3):
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=relevance_score,
                confidence=confidence,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=final_decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            # Add prediction metadata
            prediction.model_metadata.update(
                {
                    "prediction_time_ms": prediction_time * 1000,
                    "feature_vector_length": len(feature_vector),
                    "preprocessing_steps": preprocessing_steps,
                    "relevance_score": relevance_score,
                    "is_above_threshold": passes_threshold,
                    "ranking_position": None,  # Will be set during batch ranking
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Prediction failed
            return self.create_prediction(
                prediction=0.3,
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def rerank_documents(
        self,
        query: dict[str, Any],
        documents: list[dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        max_documents: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rerank a list of documents based on relevance scores.

        Args:
            query: Query information
            documents: List of documents to rerank
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            max_documents: Maximum number of documents to return

        Returns:
            Reranked list of documents with scores
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        max_docs = max_documents or self.threshold_config.get("max_documents", 100)

        # Predict relevance for each document
        document_scores = []

        for i, document in tqdm(enumerate(documents), desc="Processing", unit="item"):
            # Create context for this document
            context = {
                "query": query,
                "document": document,
                "cache_stats": document.get("cache_stats", {}),
                "domain": query.get("domain", "general"),
                "domain_terms": query.get("domain_terms", []),
                "technical_terms": query.get("technical_terms", []),
            }

            # Extract features
            extraction_result = self.feature_extractor.extract_features(
                context=context,
                trace_id=f"{trace_id}_doc_{i}",
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            if extraction_result.success:
                # Validate input
                model_input = self.validate_input(extraction_result.features)
                model_input.feature_provenance = extraction_result.provenance

                # Make prediction
                prediction = self.predict(
                    model_input=model_input,
                    trace_id=f"{trace_id}_doc_{i}",
                    replay_key=replay_key,
                    policy_hash=policy_hash,
                )

                document_scores.append(
                    {
                        "document": document,
                        "original_index": i,
                        "relevance_score": prediction.prediction,
                        "confidence": prediction.confidence,
                        "top_features": prediction.top_features,
                        "decision_mode": prediction.decision_mode,
                        "prediction_metadata": prediction.model_metadata,
                    }
                )
            else:
                # Feature extraction failed - give low score
                document_scores.append(
                    {
                        "document": document,
                        "original_index": i,
                        "relevance_score": 0.1,
                        "confidence": 0.0,
                        "top_features": [],
                        "decision_mode": DecisionMode.BLOCKED,
                        "prediction_metadata": {"error": "Feature extraction failed"},
                    }
                )

        # Sort by relevance score (descending)
        document_scores.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Update ranking positions
        for rank, doc_score in enumerate(document_scores[:max_docs]):
            doc_score["ranking_position"] = rank + 1

        # Return top documents
        return document_scores[:max_docs]

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.feature_importances:
            return []

        try:
            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in tqdm(
                enumerate(zip(feature_names, self.feature_importances)), desc="Processing", unit="item"
            ):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": float(importance),
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                        "relative_importance": float(importance / max(self.feature_importances))
                        if max(self.feature_importances) > 0
                        else 0.0,
                    }
                )

            # Sort by importance
            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature["rank"] = i + 1

            # Return top 10 features
            return feature_importance[:10]

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Failed to compute importance
            return []

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        if not self.feature_names:
            return None

        try:
            feature_vector = []
            for feature_name in tqdm(self.feature_names, desc="Processing", unit="item"):
                value = features.get(feature_name, 0.0)  # Default to 0 if missing

                # Convert to numeric
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0

                feature_vector.append(float(value))

            return np.array(feature_vector)

        except (TypeError, ValueError):
            return None

    def _calculate_prediction_confidence(self, feature_vector: np.ndarray, prediction: float) -> float:
        """Calculate confidence score for prediction."""
        # For LightGBM, we can use prediction proximity to decision boundary
        # and feature vector characteristics

        # Base confidence from prediction magnitude
        if prediction > 0.7 or prediction < 0.3:
            base_confidence = 0.8  # High confidence for extreme scores
        elif prediction > 0.6 or prediction < 0.4:
            base_confidence = 0.6  # Medium confidence
        else:
            base_confidence = 0.4  # Lower confidence for ambiguous scores

        # Adjust based on feature vector characteristics
        feature_variance = np.var(feature_vector)
        variance_factor = min(0.2, feature_variance / 10.0)  # Boost confidence for varied features

        # Adjust based on feature completeness
        non_zero_features = np.count_nonzero(feature_vector)
        completeness_factor = min(0.1, non_zero_features / len(feature_vector) * 0.1)

        confidence = base_confidence + variance_factor + completeness_factor
        return round(min(1.0, max(0.0, confidence)), 3)

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for LightGBM."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for LightGBM
        for key, value in tqdm(processed_features.items(), desc="Processing", unit="item"):
            # Ensure all features are numeric
            if isinstance(value, str):
                try:
                    processed_features[key] = float(value)
                    preprocessing_steps.append(f"string_to_numeric_{key}")
                except ValueError:
                    processed_features[key] = 0.0
                    preprocessing_steps.append(f"string_to_default_{key}")
            elif not isinstance(value, (int, float)):
                processed_features[key] = 0.0
                preprocessing_steps.append(f"non_numeric_to_default_{key}")

        return processed_features, preprocessing_steps

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        feature_names: list[str],
        training_data_digest: str = "",
        lgb_params: dict[str, Any] | None = None,
    ) -> None:
        """
        Train the LightGBM model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
            lgb_params: LightGBM hyperparameters
        """
        # Extract features and labels
        X = []
        y = []

        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]  # Relevance score (0-1)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(float(label))

        X = np.array(X)
        y = np.array(y)

        # Default LightGBM parameters
        default_params = {
            "objective": "regression",
            "metric": "rmse",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "random_state": 42,
        }

        # Merge with provided parameters
        params = {**default_params, **(lgb_params or {})}

        # Create LightGBM dataset
        train_data = lgb.Dataset(X, label=y)

        # Train model
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[train_data],
            callbacks=[lgb.log_evaluation(10)],
        )

        # Store feature names and importance
        self.feature_names = feature_names
        self.feature_importances = self.model.feature_importance()

        # Store training digest
        self._training_data_digest = training_data_digest

        self.is_loaded = True

    def predict_from_context(
        self,
        query: dict[str, Any],
        document: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict relevance from context (convenience method).

        Args:
            query: Query information
            document: Document to score
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Relevance score prediction
        """
        # Create context
        context = {
            "query": query,
            "document": document,
            "cache_stats": document.get("cache_stats", {}),
            "domain": query.get("domain", "general"),
            "domain_terms": query.get("domain_terms", []),
            "technical_terms": query.get("technical_terms", []),
        }

        # Extract features
        extraction_result = self.feature_extractor.extract_features(
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            # Feature extraction failed
            return self.create_prediction(
                prediction=0.3,
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        return self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
            decision_mode=decision_mode,
        )
