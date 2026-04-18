"""
C1 Query Optimizer

Gradient Boosting model for query optimization including
execution plan analysis, index recommendations, performance tuning,
and query rewrite suggestions.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    GradientBoostingClassifier = None
    StandardScaler = None
    Pipeline = None

from ..config.model_registry import DecisionMode
from ..features.c1_features import C1FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class C1QueryOptimizer(BaseMLModel):
    """
    Gradient Boosting model for C1 query optimization.

    Optimizes queries based on:
    - Query complexity and structure analysis
    - Execution plan optimization recommendations
    - Index usage and effectiveness scoring
    - Resource intensity and performance metrics
    - Cache optimization and hit rate improvement
    - Join optimization and query rewrite suggestions
    """

    # Optimization action mapping
    OPTIMIZATION_MAPPING = {
        0: "Add_Index",
        1: "Rewrite_Query",
        2: "Optimize_Joins",
        3: "Add_Caching",
        4: "Update_Statistics",
        5: "Partition_Table",
        6: "Materialize_View",
        7: "No_Optimization",
    }

    # Reverse mapping
    REVERSE_OPTIMIZATION_MAPPING = {v: k for k, v in OPTIMIZATION_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if GradientBoostingClassifier is None:
            raise ImportError("scikit-learn is required for C1QueryOptimizer")

        super().__init__(
            model_name="c1_query_optimizer",
            model_version="1.0",
            model_type="gradient_boosting",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = C1FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.OPTIMIZATION_MAPPING.values())

        # Default thresholds
        self.threshold_config = {
            "complexity_threshold": 0.6,
            "performance_threshold": 0.5,
            "optimization_threshold": 0.7,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Gradient Boosting model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "threshold_config": self.threshold_config,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "class_names": self.class_names,
                "feature_schema_digest": self.feature_schema.schema_digest,
                "saved_at": datetime.now().isoformat(),
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
        Predict query optimization action.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Query optimization prediction with full metadata
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
                prediction="No_Optimization",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Gradient Boosting prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to optimization action name
            predicted_action = self.OPTIMIZATION_MAPPING.get(int(predicted_class), "No_Optimization")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("optimization_threshold", 0.7)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_action,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_action,
                confidence=confidence,
                probability_distribution=prob_distribution,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=decision_mode,
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
                    "raw_prediction_class": predicted_class,
                    "class_probabilities": [float(p) for p in probabilities],
                    "thresholds_passed": passes_threshold,
                    "optimization_action": predicted_action,
                    "requires_optimization": predicted_action != "No_Optimization",
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Prediction failed
            return self.create_prediction(
                prediction="No_Optimization",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def optimize_query(
        self,
        query_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get comprehensive query optimization recommendations.

        Args:
            query_context: Query metrics and context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive query optimization recommendations
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=query_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "optimization_action": "No_Optimization",
                "confidence": 0.0,
                "reason": "Feature extraction failed",
                "recommendations": ["Check query data availability"],
            }

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        prediction = self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Generate detailed recommendations
        recommendations = self._generate_optimization_recommendations(
            action=prediction.prediction,
            context=query_context,
            features=extraction_result.features,
        )

        # Generate optimized query if applicable
        optimized_query = self._generate_optimized_query(
            action=prediction.prediction,
            original_query=query_context.get("query", ""),
            context=query_context,
        )

        # Calculate expected performance improvement
        performance_impact = self._calculate_performance_impact(
            action=prediction.prediction,
            context=query_context,
            features=extraction_result.features,
        )

        return {
            "optimization_action": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_factors": prediction.top_features,
            "recommendations": recommendations,
            "optimized_query": optimized_query,
            "performance_impact": performance_impact,
            "implementation_effort": self._estimate_implementation_effort(prediction.prediction),
            "risk_assessment": self._assess_optimization_risk(prediction.prediction, query_context),
        }

    def analyze_query_plan(
        self,
        query_plan: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze query execution plan and provide insights.

        Args:
            query_plan: Query execution plan data
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Query plan analysis and recommendations
        """
        # Extract plan features
        plan_features = self._extract_plan_features(query_plan)

        # Generate insights
        insights = []

        # Scan type analysis
        scan_types = [op.get("operation_type") for op in query_plan.get("operations", [])]
        table_scans = [st for st in scan_types if st == "Table Scan"]

        if table_scans:
            insights.append(
                {
                    "type": "performance_issue",
                    "severity": "high",
                    "description": f"{len(table_scans)} table scans detected - consider adding indexes",
                    "recommendation": "Add appropriate indexes to avoid full table scans",
                }
            )

        # Join order analysis
        join_operations = [
            op for op in query_plan.get("operations", []) if "Join" in op.get("operation_type", "")
        ]

        if len(join_operations) > 3:
            insights.append(
                {
                    "type": "complexity_issue",
                    "severity": "medium",
                    "description": f"Complex join with {len(join_operations)} operations",
                    "recommendation": "Consider query rewrite or materialized views",
                }
            )

        # Cost analysis
        total_cost = sum(op.get("cost", 0) for op in query_plan.get("operations", []))

        if total_cost > 1000:
            insights.append(
                {
                    "type": "cost_issue",
                    "severity": "high",
                    "description": f"High execution cost: {total_cost:.2f}",
                    "recommendation": "Optimize query structure and add indexes",
                }
            )

        # Generate optimization suggestions
        suggestions = self._generate_plan_suggestions(query_plan, insights)

        return {
            "plan_analysis": {
                "total_cost": total_cost,
                "operation_count": len(query_plan.get("operations", [])),
                "table_scans": len(table_scans),
                "join_operations": len(join_operations),
            },
            "insights": insights,
            "suggestions": suggestions,
            "optimization_priority": self._determine_optimization_priority(insights),
        }

    def recommend_indexes(
        self,
        query_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Generate index recommendations based on query analysis.

        Args:
            query_context: Query context including tables and predicates
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Index recommendations with impact analysis
        """
        query = query_context.get("query", "")
        tables = query_context.get("tables", [])
        predicates = query_context.get("predicates", [])

        recommendations = []

        # Analyze WHERE clauses for index candidates
        for predicate in tqdm(predicates, desc="Processing", unit="item"):
            column = predicate.get("column")
            table = predicate.get("table")
            operator = predicate.get("operator")

            if column and table:
                # Determine index type based on operator
                if operator in ["=", "IN"]:
                    index_type = "B-Tree"
                elif operator in [">", "<", ">=", "<=", "BETWEEN"]:
                    index_type = "B-Tree"
                elif operator in ["LIKE", "ILIKE"]:
                    index_type = "B-Tree" if not predicate.get("pattern", "").startswith("%") else "Full-Text"
                else:
                    index_type = "B-Tree"

                # Calculate potential impact
                selectivity = predicate.get("selectivity", 0.1)  # Default 10% selectivity
                if selectivity < 0.1:
                    impact = "High"
                elif selectivity < 0.3:
                    impact = "Medium"
                else:
                    impact = "Low"

                recommendations.append(
                    {
                        "table": table,
                        "column": column,
                        "index_type": index_type,
                        "operator": operator,
                        "selectivity": selectivity,
                        "impact": impact,
                        "estimated_improvement": self._estimate_index_improvement(selectivity),
                        "recommendation": f"Create {index_type} index on {table}.{column}",
                    }
                )

        # Analyze JOIN conditions
        join_conditions = query_context.get("join_conditions", [])

        for join in tqdm(join_conditions, desc="Processing", unit="item"):
            left_table = join.get("left_table")
            left_column = join.get("left_column")
            right_table = join.get("right_table")
            right_column = join.get("right_column")

            if left_table and left_column and right_table and right_column:
                # Recommend foreign key indexes
                recommendations.append(
                    {
                        "table": left_table,
                        "column": left_column,
                        "index_type": "B-Tree",
                        "purpose": "foreign_key",
                        "impact": "High",
                        "estimated_improvement": 0.3,
                        "recommendation": f"Create index on {left_table}.{left_column} for join optimization",
                    }
                )

                recommendations.append(
                    {
                        "table": right_table,
                        "column": right_column,
                        "index_type": "B-Tree",
                        "purpose": "foreign_key",
                        "impact": "High",
                        "estimated_improvement": 0.3,
                        "recommendation": f"Create index on {right_table}.{right_column} for join optimization",
                    }
                )

        # Sort by impact and remove duplicates
        unique_recommendations = {}
        for rec in recommendations:
            key = f"{rec['table']}.{rec['column']}"
            if key not in unique_recommendations or rec["impact"] == "High":
                unique_recommendations[key] = rec

        final_recommendations = list(unique_recommendations.values())
        final_recommendations.sort(
            key=lambda x: {"High": 3, "Medium": 2, "Low": 1}[x["impact"]], reverse=True
        )

        return {
            "recommendations": final_recommendations[:10],  # Top 10 recommendations
            "total_recommendations": len(final_recommendations),
            "high_impact_count": len([r for r in final_recommendations if r["impact"] == "High"]),
            "estimated_overall_improvement": sum(
                r.get("estimated_improvement", 0) for r in final_recommendations[:5]
            ),
        }

    def _generate_optimization_recommendations(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> list[str]:
        """Generate action-specific optimization recommendations."""
        recommendations = []

        if action == "Add_Index":
            recommendations.extend(
                [
                    "Create appropriate indexes for frequently queried columns",
                    "Analyze WHERE clause predicates for index candidates",
                    "Consider composite indexes for multi-column queries",
                    "Monitor index usage and effectiveness",
                ]
            )
        elif action == "Rewrite_Query":
            recommendations.extend(
                [
                    "Restructure query for better performance",
                    "Eliminate unnecessary subqueries and CTEs",
                    "Use appropriate join types and order",
                    "Optimize WHERE clauses and predicates",
                ]
            )
        elif action == "Optimize_Joins":
            recommendations.extend(
                [
                    "Review and optimize join operations",
                    "Ensure proper join order based on table sizes",
                    "Consider join hints if necessary",
                    "Add indexes on foreign key columns",
                ]
            )
        elif action == "Add_Caching":
            recommendations.extend(
                [
                    "Implement query result caching",
                    "Cache frequently accessed data",
                    "Consider application-level caching",
                    "Monitor cache hit rates",
                ]
            )
        elif action == "Update_Statistics":
            recommendations.extend(
                [
                    "Update table statistics for better query plans",
                    "Run ANALYZE on modified tables",
                    "Consider automatic statistics updates",
                    "Monitor query plan changes",
                ]
            )
        elif action == "Partition_Table":
            recommendations.extend(
                [
                    "Implement table partitioning for large tables",
                    "Choose appropriate partitioning strategy",
                    "Consider partition pruning benefits",
                    "Monitor partition performance",
                ]
            )
        elif action == "Materialize_View":
            recommendations.extend(
                [
                    "Create materialized views for complex queries",
                    "Schedule regular view refreshes",
                    "Monitor view performance and usage",
                    "Consider incremental maintenance",
                ]
            )
        else:  # No_Optimization
            recommendations.extend(
                [
                    "Query is already optimally structured",
                    "Continue monitoring query performance",
                    "Maintain current indexes and statistics",
                    "Regular performance reviews recommended",
                ]
            )

        # Add context-specific recommendations
        complexity_score = features.get("query_complexity_score", 0)
        if complexity_score > 0.7:
            recommendations.append("High complexity query - consider breaking into smaller queries")

        cache_hit_rate = features.get("cache_hit_rate", 0)
        if cache_hit_rate < 0.5:
            recommendations.append("Low cache hit rate - implement query caching")

        return recommendations

    def _generate_optimized_query(
        self, action: str, original_query: str, context: dict[str, Any]
    ) -> str | None:
        """Generate optimized query based on action."""
        if not original_query or action == "No_Optimization":
            return None

        # Simplified query optimization (real implementation would use SQL parser)
        optimized_query = original_query

        if action == "Rewrite_Query":
            # Basic rewrite suggestions
            if "SELECT *" in original_query:
                # Suggest specific columns
                tables = context.get("tables", [])
                if tables:
                    optimized_query = original_query.replace(
                        "SELECT *", f"SELECT specific_columns FROM {tables[0]}"
                    )

        elif action == "Optimize_Joins":
            # Basic join optimization hints
            if "JOIN" in original_query.upper():
                optimized_query += " /*+ USE_NL */"  # Add join hint

        return optimized_query if optimized_query != original_query else None

    def _calculate_performance_impact(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Calculate expected performance impact of optimization."""
        # Base impact estimates by action type
        impact_estimates = {
            "Add_Index": {
                "execution_time_improvement": 0.6,
                "cpu_reduction": 0.4,
                "io_reduction": 0.7,
            },
            "Rewrite_Query": {
                "execution_time_improvement": 0.4,
                "cpu_reduction": 0.3,
                "io_reduction": 0.2,
            },
            "Optimize_Joins": {
                "execution_time_improvement": 0.5,
                "cpu_reduction": 0.4,
                "io_reduction": 0.3,
            },
            "Add_Caching": {
                "execution_time_improvement": 0.8,
                "cpu_reduction": 0.6,
                "io_reduction": 0.9,
            },
            "Update_Statistics": {
                "execution_time_improvement": 0.2,
                "cpu_reduction": 0.1,
                "io_reduction": 0.1,
            },
            "Partition_Table": {
                "execution_time_improvement": 0.3,
                "cpu_reduction": 0.2,
                "io_reduction": 0.4,
            },
            "Materialize_View": {
                "execution_time_improvement": 0.7,
                "cpu_reduction": 0.5,
                "io_reduction": 0.6,
            },
            "No_Optimization": {
                "execution_time_improvement": 0.0,
                "cpu_reduction": 0.0,
                "io_reduction": 0.0,
            },
        }

        base_impact = impact_estimates.get(action, impact_estimates["No_Optimization"])

        # Adjust based on current performance
        current_performance = context.get("performance", {})
        execution_time = current_performance.get("execution_time", 1000)

        # Higher impact for slower queries
        if execution_time > 5000:  # > 5 seconds
            performance_multiplier = 1.5
        elif execution_time > 1000:  # > 1 second
            performance_multiplier = 1.2
        else:
            performance_multiplier = 1.0

        # Adjust impact
        adjusted_impact = base_impact.copy()
        for key in adjusted_impact:
            adjusted_impact[key] *= performance_multiplier

        return adjusted_impact

    def _estimate_implementation_effort(self, action: str) -> str:
        """Estimate implementation effort for optimization action."""
        effort_estimates = {
            "Add_Index": "Low",
            "Rewrite_Query": "Medium",
            "Optimize_Joins": "Medium",
            "Add_Caching": "Medium",
            "Update_Statistics": "Low",
            "Partition_Table": "High",
            "Materialize_View": "High",
            "No_Optimization": "None",
        }

        return effort_estimates.get(action, "Medium")

    def _assess_optimization_risk(self, action: str, context: dict[str, Any]) -> str:
        """Assess implementation risk for optimization action."""
        # Base risk levels
        risk_levels = {
            "Add_Index": "Low",
            "Rewrite_Query": "Medium",
            "Optimize_Joins": "Medium",
            "Add_Caching": "Low",
            "Update_Statistics": "Low",
            "Partition_Table": "High",
            "Materialize_View": "Medium",
            "No_Optimization": "None",
        }

        base_risk = risk_levels.get(action, "Medium")

        # Adjust risk based on system criticality
        system_criticality = context.get("system", {}).get("criticality", "medium")

        if system_criticality == "high" and action in ["Partition_Table", "Rewrite_Query"]:
            return "High"
        elif system_criticality == "low":
            return "Low"

        return base_risk

    def _extract_plan_features(self, query_plan: dict[str, Any]) -> dict[str, float]:
        """Extract features from query execution plan."""
        operations = query_plan.get("operations", [])

        features = {
            "operation_count": len(operations),
            "total_cost": sum(op.get("cost", 0) for op in operations),
            "table_scans": len([op for op in operations if op.get("operation_type") == "Table Scan"]),
            "index_scans": len([op for op in operations if "Index Scan" in op.get("operation_type", "")]),
            "join_operations": len([op for op in operations if "Join" in op.get("operation_type", "")]),
        }

        return features

    def _generate_plan_suggestions(
        self, query_plan: dict[str, Any], insights: list[dict[str, Any]]
    ) -> list[str]:
        """Generate suggestions based on plan analysis."""
        suggestions = []

        # Add suggestions based on insights
        for insight in insights:
            if insight.get("recommendation"):
                suggestions.append(insight["recommendation"])

        # Add general suggestions
        operations = query_plan.get("operations", [])
        total_cost = sum(op.get("cost", 0) for op in operations)

        if total_cost > 1000:
            suggestions.append("Consider query restructuring to reduce execution cost")

        table_scans = len([op for op in operations if op.get("operation_type") == "Table Scan"])
        if table_scans > 0:
            suggestions.append(f"Add indexes to eliminate {table_scans} table scan(s)")

        return suggestions

    def _determine_optimization_priority(self, insights: list[dict[str, Any]]) -> str:
        """Determine optimization priority based on insights."""
        high_severity = len([i for i in insights if i.get("severity") == "high"])
        medium_severity = len([i for i in insights if i.get("severity") == "medium"])

        if high_severity > 0:
            return "High"
        elif medium_severity > 2:
            return "Medium"
        else:
            return "Low"

    def _estimate_index_improvement(self, selectivity: float) -> float:
        """Estimate performance improvement from index based on selectivity."""
        # Higher improvement for lower selectivity (more selective predicates)
        if selectivity < 0.01:
            return 0.8  # 80% improvement
        elif selectivity < 0.05:
            return 0.6  # 60% improvement
        elif selectivity < 0.1:
            return 0.4  # 40% improvement
        elif selectivity < 0.3:
            return 0.2  # 20% improvement
        else:
            return 0.1  # 10% improvement

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # Get feature importances from Gradient Boosting
            gb_model = self.pipeline.named_steps["classifier"]
            importances = gb_model.feature_importances_

            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in tqdm(
                enumerate(zip(feature_names, importances)), desc="Processing", unit="item"
            ):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": float(importance),
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                        "relative_importance": float(importance / max(importances))
                        if max(importances) > 0
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
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            return np.array(feature_vector)

        except (TypeError, ValueError):
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Gradient Boosting."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Gradient Boosting
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
    ) -> None:
        """
        Train the Gradient Boosting model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Extract features and labels
        X = []
        y = []

        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]

            # Convert optimization type string to class index
            if isinstance(label, str):
                label = self.REVERSE_OPTIMIZATION_MAPPING.get(label, 7)  # Default to No_Optimization
            else:
                label = int(label)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        # Create pipeline with scaling and Gradient Boosting
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    GradientBoostingClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42,
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X, y)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
