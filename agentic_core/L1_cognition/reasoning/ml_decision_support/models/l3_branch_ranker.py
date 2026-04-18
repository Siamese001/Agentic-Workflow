"""
L3 DAG Branch Ranker

LambdaMART model for ranking DAG branches based on execution priority,
resource efficiency, and workflow optimization criteria.
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
from ..features.l3_features import L3FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class L3BranchRanker(BaseMLModel):
    """
    LambdaMART model for L3 DAG branch ranking.

    Reranks DAG branches based on:
    - Branch complexity and execution probability
    - Resource requirements and availability
    - Conflict indicators and escalation priority
    - Workflow depth and dependency structure
    - Historical success rates and timing criticality
    - Parallel execution potential

    Always operates in advisory mode - L3 retains final orchestration authority.
    """

    def __init__(self, model_file_path: Path | None = None):
        if lgb is None:
            raise ImportError("LightGBM is required for L3BranchRanker")

        super().__init__(
            model_name="l3_branch_ranker",
            model_version="1.0",
            model_type="lambdamart",
            prediction_type=PredictionType.RANKING,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = L3FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.model = None
        self.feature_names = None
        self.feature_importances = None

        # Default thresholds
        self.threshold_config = {
            "ranking_threshold": 0.5,
            "top_k_branches": 10,
            "min_score": 0.1,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the LambdaMART model from file."""
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
        Predict ranking score for a DAG branch.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Ranking score prediction with full metadata
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
                prediction=0.3,  # Low default ranking score
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # LambdaMART prediction (ranking score)
            ranking_score = self.model.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Ensure score is in valid range
            ranking_score = float(np.clip(ranking_score, 0.0, 1.0))

            # Calculate confidence based on prediction characteristics
            confidence = self._calculate_ranking_confidence(feature_vector, ranking_score)

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("ranking_threshold", 0.5)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=ranking_score,
                    confidence=confidence,
                    threshold_used=threshold_used,
                ),
            )

            # Determine final decision mode
            final_decision_mode = decision_mode
            if not passes_threshold or ranking_score < self.threshold_config.get("min_score", 0.1):
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=ranking_score,
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
                    "ranking_score": ranking_score,
                    "is_above_threshold": passes_threshold,
                    "ranking_position": None,  # Will be set during batch ranking
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as e:
            # Prediction failed
            return self.create_prediction(
                prediction=0.3,
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def rank_branches(
        self,
        branches: list[dict[str, Any]],
        dag_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rank a list of DAG branches based on execution priority.

        Args:
            branches: List of DAG branches to rank
            dag_context: DAG-wide context information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            top_k: Maximum number of branches to return

        Returns:
            Ranked list of branches with scores
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        max_branches = top_k or self.threshold_config.get("top_k_branches", 10)

        # Predict ranking scores for each branch
        branch_scores = []

        for i, branch in tqdm(enumerate(branches), desc="Processing", unit="item"):
            # Create context for this branch
            context = {
                "branch": branch,
                "dag": dag_context,
                "other_branches": [b for j, b in enumerate(branches) if j != i],
                "resources": dag_context.get("resources", {}),
                "history": dag_context.get("history", {}),
                "trace_id": f"{trace_id}_branch_{i}",
            }

            # Extract features
            extraction_result = self.feature_extractor.extract_features(
                context=context,
                trace_id=f"{trace_id}_branch_{i}",
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
                    trace_id=f"{trace_id}_branch_{i}",
                    replay_key=replay_key,
                    policy_hash=policy_hash,
                )

                branch_scores.append(
                    {
                        "branch": branch,
                        "original_index": i,
                        "ranking_score": prediction.prediction,
                        "confidence": prediction.confidence,
                        "top_features": prediction.top_features,
                        "decision_mode": prediction.decision_mode,
                        "prediction_metadata": prediction.model_metadata,
                    }
                )
            else:
                # Feature extraction failed - give low score
                branch_scores.append(
                    {
                        "branch": branch,
                        "original_index": i,
                        "ranking_score": 0.1,
                        "confidence": 0.0,
                        "top_features": [],
                        "decision_mode": DecisionMode.BLOCKED,
                        "prediction_metadata": {"error": "Feature extraction failed"},
                    }
                )

        # Sort by ranking score (descending)
        branch_scores.sort(key=lambda x: x["ranking_score"], reverse=True)

        # Update ranking positions
        for rank, branch_score in enumerate(branch_scores[:max_branches]):
            branch_score["ranking_position"] = rank + 1

        # Return top branches
        return branch_scores[:max_branches]

    def get_execution_order(
        self,
        branches: list[dict[str, Any]],
        dag_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        respect_dependencies: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get optimal execution order for branches considering dependencies.

        Args:
            branches: List of DAG branches
            dag_context: DAG-wide context
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash
            respect_dependencies: Whether to respect dependency constraints

        Returns:
            Ordered list of branches for execution
        """
        # First rank all branches
        ranked_branches = self.rank_branches(
            branches=branches,
            dag_context=dag_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not respect_dependencies:
            return ranked_branches

        # Apply dependency-aware ordering
        ordered_branches = []
        remaining_branches = ranked_branches.copy()
        processed_branches = set()

        while remaining_branches:
            # Find branches with no unprocessed dependencies
            ready_branches = []

            for branch_score in tqdm(remaining_branches, desc="Processing", unit="item"):
                branch = branch_score["branch"]
                dependencies = branch.get("dependencies", [])

                # Check if all dependencies are processed
                deps_satisfied = True
                for dep in dependencies:
                    if dep not in processed_branches:
                        deps_satisfied = False
                        break

                if deps_satisfied:
                    ready_branches.append(branch_score)

            if not ready_branches:
                # Circular dependency - take highest priority remaining branch
                ready_branches = [remaining_branches[0]]

            # Add highest priority ready branch
            selected_branch = ready_branches[0]
            ordered_branches.append(selected_branch)
            processed_branches.add(selected_branch["branch"].get("id", selected_branch["original_index"]))

            # Remove from remaining
            remaining_branches.remove(selected_branch)

        return ordered_branches

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

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as e:
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

        except (TypeError, ValueError) as e:
            return None

    def _calculate_ranking_confidence(self, feature_vector: np.ndarray, ranking_score: float) -> float:
        """Calculate confidence score for ranking prediction."""
        # For LambdaMART, confidence is based on:
        # 1. Ranking score magnitude
        # 2. Feature vector characteristics
        # 3. Model certainty (based on leaf node consistency)

        # Base confidence from ranking score
        if ranking_score > 0.7:
            base_confidence = 0.8  # High confidence for high scores
        elif ranking_score > 0.4:
            base_confidence = 0.6  # Medium confidence for moderate scores
        elif ranking_score > 0.2:
            base_confidence = 0.4  # Lower confidence for low scores
        else:
            base_confidence = 0.3  # Low confidence for very low scores

        # Adjust based on feature vector characteristics
        feature_variance = np.var(feature_vector)
        variance_factor = min(0.2, feature_variance / 10.0)  # Boost confidence for varied features

        # Adjust based on feature completeness
        non_zero_features = np.count_nonzero(feature_vector)
        completeness_factor = min(0.1, non_zero_features / len(feature_vector) * 0.1)

        confidence = base_confidence + variance_factor + completeness_factor
        return round(min(1.0, max(0.0, confidence)), 3)

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for LambdaMART."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for LambdaMART
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
        Train the LambdaMART model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
            lgb_params: LightGBM hyperparameters
        """
        # Extract features and labels
        X = []
        y = []
        group = []  # For LambdaMART ranking

        current_group = []
        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]  # Ranking score or relevance
            query_id = example.get("query_id", 0)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(float(label))
            current_group.append(1)

            # Start new group when query_id changes
            if example != training_data[-1]:  # Not the last example
                next_example = training_data[training_data.index(example) + 1]
                if next_example.get("query_id", 0) != query_id:
                    group.extend(current_group)
                    current_group = []

        # Add the last group
        if current_group:
            group.extend(current_group)

        X = np.array(X)
        y = np.array(y)

        # Default LambdaMART parameters
        default_params = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "random_state": 42,
            "label_gain": [0, 1, 3, 7, 15, 31, 63, 127],  # LambdaMART label gains
        }

        # Merge with provided parameters
        params = {**default_params, **(lgb_params or {})}

        # Create LightGBM dataset with group information
        train_data = lgb.Dataset(X, label=y, group=group)

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
        branch: dict[str, Any],
        dag_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict ranking score from context (convenience method).

        Args:
            branch: DAG branch to score
            dag_context: DAG-wide context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Ranking score prediction
        """
        # Create context
        context = {
            "branch": branch,
            "dag": dag_context,
            "other_branches": dag_context.get("other_branches", []),
            "resources": dag_context.get("resources", {}),
            "history": dag_context.get("history", {}),
            "trace_id": trace_id,
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
