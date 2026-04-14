"""
L3 Feature Extractor

Extracts features for L3 DAG branch ranking model including
branch complexity, execution probability, resource requirements,
conflict indicators, escalation priority, and workflow lineage.
"""

from datetime import datetime
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor
from tqdm import tqdm


class L3FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L3 DAG branch ranking.

    Extracts deterministic features for branch ranking:
    - Branch complexity and structure metrics
    - Execution probability and success rates
    - Resource requirements and constraints
    - Conflict detection and resolution indicators
    - Escalation priority and urgency
    - Workflow lineage and dependencies
    - Performance and timing characteristics
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l3_branch_ranker")
        if not schema:
            # Create schema for L3 branch ranker
            schema = self._create_l3_schema()
        super().__init__(schema)

    def _create_l3_schema(self) -> FeatureSchema:
        """Create feature schema for L3 branch ranker."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="branch_complexity_score",
                feature_type=FeatureType.NUMERIC,
                description="Complexity score of DAG branch",
                provenance="dag.branch.complexity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="execution_probability",
                feature_type=FeatureType.NUMERIC,
                description="Probability of successful execution",
                provenance="branch.execution.probability",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="resource_requirement_score",
                feature_type=FeatureType.NUMERIC,
                description="Resource requirements (CPU, memory, time)",
                provenance="branch.resources.requirement_score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="conflict_indicator",
                feature_type=FeatureType.NUMERIC,
                description="Potential conflicts with other branches",
                provenance="branch.conflicts.indicator",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="escalation_priority",
                feature_type=FeatureType.NUMERIC,
                description="Priority for escalation if needed",
                provenance="branch.escalation.priority",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="workflow_depth",
                feature_type=FeatureType.NUMERIC,
                description="Depth of branch in workflow hierarchy",
                provenance="workflow.branch.depth",
                validation_rules={"min_value": 1, "max_value": 10},
            ),
            FeatureDefinition(
                name="dependency_count",
                feature_type=FeatureType.NUMERIC,
                description="Number of dependencies for this branch",
                provenance="branch.dependencies.count",
                validation_rules={"min_value": 0, "max_value": 50},
            ),
            FeatureDefinition(
                name="historical_success_rate",
                feature_type=FeatureType.NUMERIC,
                description="Historical success rate for similar branches",
                provenance="history.branch.success_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="timing_criticality",
                feature_type=FeatureType.NUMERIC,
                description="Timing criticality of branch execution",
                provenance="branch.timing.criticality",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="parallel_execution_potential",
                feature_type=FeatureType.NUMERIC,
                description="Potential for parallel execution",
                provenance="branch.parallel.potential",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
        ]

        return FeatureSchema(
            schema_name="l3_branch_ranker",
            schema_version="1.0",
            description="Features for L3 DAG branch ranking model",
            features=features,
        )

    def _register_extraction_functions(self) -> None:
        """Register L3-specific feature extraction functions."""
        self.register_extraction_function("branch_complexity_score", self._extract_branch_complexity_score)
        self.register_extraction_function("execution_probability", self._extract_execution_probability)
        self.register_extraction_function(
            "resource_requirement_score", self._extract_resource_requirement_score
        )
        self.register_extraction_function("conflict_indicator", self._extract_conflict_indicator)
        self.register_extraction_function("escalation_priority", self._extract_escalation_priority)
        self.register_extraction_function("workflow_depth", self._extract_workflow_depth)
        self.register_extraction_function("dependency_count", self._extract_dependency_count)
        self.register_extraction_function("historical_success_rate", self._extract_historical_success_rate)
        self.register_extraction_function("timing_criticality", self._extract_timing_criticality)
        self.register_extraction_function(
            "parallel_execution_potential", self._extract_parallel_execution_potential
        )

    def _extract_branch_complexity_score(self, context: dict[str, Any]) -> float:
        """Extract branch complexity score (0.0-1.0)."""
        branch = context.get("branch", {})
        dag = context.get("dag", {})

        # Direct complexity score if provided
        if "complexity_score" in branch:
            return float(branch["complexity_score"])

        # Calculate from branch characteristics
        complexity_indicators = {
            "node_count": 0.3,
            "edge_count": 0.2,
            "conditional_logic": 0.25,
            "nested_depth": 0.15,
            "data_flow_complexity": 0.1,
        }

        score = 0.0

        # Node count contribution
        nodes = branch.get("nodes", [])
        if nodes:
            node_score = min(1.0, len(nodes) / 20.0)  # Normalize to 20 nodes
            score += complexity_indicators["node_count"] * node_score

        # Edge count contribution
        edges = branch.get("edges", [])
        if edges:
            edge_score = min(1.0, len(edges) / 30.0)  # Normalize to 30 edges
            score += complexity_indicators["edge_count"] * edge_score

        # Conditional logic contribution
        conditional_nodes = [node for node in nodes if node.get("type") in ["if", "switch", "try"]]
        if conditional_nodes:
            conditional_score = min(1.0, len(conditional_nodes) / 5.0)  # Normalize to 5 conditionals
            score += complexity_indicators["conditional_logic"] * conditional_score

        # Nested depth contribution
        max_depth = self._calculate_max_depth(nodes)
        depth_score = min(1.0, max_depth / 5.0)  # Normalize to 5 levels
        score += complexity_indicators["nested_depth"] * depth_score

        # Data flow complexity
        data_flows = branch.get("data_flows", [])
        if data_flows:
            flow_score = min(1.0, len(data_flows) / 10.0)  # Normalize to 10 data flows
            score += complexity_indicators["data_flow_complexity"] * flow_score

        return round(min(1.0, score), 3)

    def _extract_execution_probability(self, context: dict[str, Any]) -> float:
        """Extract execution probability (0.0-1.0)."""
        branch = context.get("branch", {})

        # Direct probability if provided
        if "execution_probability" in branch:
            return float(branch["execution_probability"])

        # Calculate from branch conditions and dependencies
        base_probability = 0.8  # Base probability

        # Adjust for preconditions
        preconditions = branch.get("preconditions", [])
        if preconditions:
            satisfied_preconditions = sum(1 for pc in preconditions if pc.get("satisfied", False))
            precondition_factor = satisfied_preconditions / len(preconditions)
            base_probability *= 0.5 + 0.5 * precondition_factor  # Scale between 0.5-1.0

        # Adjust for branch guards
        guards = branch.get("guards", [])
        if guards:
            guard_probability = 1.0
            for guard in guards:
                guard_prob = guard.get("probability", 1.0)
                guard_probability *= guard_prob
            base_probability *= guard_probability

        # Adjust for resource availability
        resources = context.get("resources", {})
        required_resources = branch.get("required_resources", {})

        resource_factor = 1.0
        for resource, amount in required_resources.items():
            available = resources.get(resource, 0)
            if available > 0:
                resource_factor *= min(1.0, available / amount)
            else:
                resource_factor *= 0.1  # Heavy penalty for missing resources

        base_probability *= resource_factor

        return round(max(0.0, min(1.0, base_probability)), 3)

    def _extract_resource_requirement_score(self, context: dict[str, Any]) -> float:
        """Extract resource requirement score (0.0-1.0)."""
        branch = context.get("branch", {})
        resources = context.get("system_resources", {})

        # Direct score if provided
        if "resource_requirement_score" in branch:
            return float(branch["resource_requirement_score"])

        # Calculate from resource requirements
        required_resources = branch.get("required_resources", {})

        if not required_resources:
            return 0.1  # Low requirement if no resources specified

        # Resource weights
        resource_weights = {
            "cpu": 0.3,
            "memory": 0.25,
            "storage": 0.2,
            "network": 0.15,
            "gpu": 0.1,
        }

        total_requirement = 0.0
        total_weight = 0.0

        for resource, amount in tqdm(required_resources.items(), desc="Processing", unit="item"):
            weight = resource_weights.get(resource, 0.1)

            # Normalize amount (assuming amounts are in standard units)
            if resource == "cpu":
                normalized_amount = min(1.0, amount / 8.0)  # 8 cores as max
            elif resource == "memory":
                normalized_amount = min(1.0, amount / 32768.0)  # 32GB as max
            elif resource == "storage":
                normalized_amount = min(1.0, amount / 1024.0)  # 1TB as max
            elif resource == "network":
                normalized_amount = min(1.0, amount / 1000.0)  # 1Gbps as max
            elif resource == "gpu":
                normalized_amount = min(1.0, amount / 4.0)  # 4 GPUs as max
            else:
                normalized_amount = min(1.0, amount / 100.0)  # Generic normalization

            total_requirement += normalized_amount * weight
            total_weight += weight

        if total_weight > 0:
            requirement_score = total_requirement / total_weight
        else:
            requirement_score = 0.1

        return round(requirement_score, 3)

    def _extract_conflict_indicator(self, context: dict[str, Any]) -> float:
        """Extract conflict indicator (0.0-1.0)."""
        branch = context.get("branch", {})
        other_branches = context.get("other_branches", [])

        # Direct indicator if provided
        if "conflict_indicator" in branch:
            return float(branch["conflict_indicator"])

        # Calculate from potential conflicts
        conflicts = []

        # Resource conflicts
        required_resources = branch.get("required_resources", {})
        for other_branch in tqdm(other_branches, desc="Processing", unit="item"):
            other_resources = other_branch.get("required_resources", {})

            for resource, amount in tqdm(required_resources.items(), desc="Processing", unit="item"):
                if resource in other_resources:
                    # Check if resources overlap significantly
                    overlap_ratio = min(amount, other_resources[resource]) / max(
                        amount, other_resources[resource]
                    )
                    if overlap_ratio > 0.5:  # 50% overlap threshold
                        conflicts.append(
                            {
                                "type": "resource",
                                "resource": resource,
                                "overlap": overlap_ratio,
                                "branch": other_branch.get("id", "unknown"),
                            }
                        )

        # Data dependency conflicts
        data_dependencies = branch.get("data_dependencies", [])
        for other_branch in tqdm(other_branches, desc="Processing", unit="item"):
            other_data_deps = other_branch.get("data_dependencies", [])

            for dep in tqdm(data_dependencies, desc="Processing", unit="item"):
                for other_dep in tqdm(other_data_deps, desc="Processing", unit="item"):
                    if dep.get("data_id") == other_dep.get("data_id"):
                        # Check for conflicting access patterns
                        if (
                            dep.get("access_type") == "write" and other_dep.get("access_type") == "write"
                        ) or (dep.get("access_type") == "write" and other_dep.get("access_type") == "read"):
                            conflicts.append(
                                {
                                    "type": "data_dependency",
                                    "data_id": dep.get("data_id"),
                                    "branch": other_branch.get("id", "unknown"),
                                }
                            )

        # Calculate conflict score
        if not conflicts:
            return 0.0

        # Weight conflicts by type and severity
        conflict_weights = {
            "resource": 0.4,
            "data_dependency": 0.6,
        }

        total_conflict_score = 0.0
        for conflict in conflicts:
            weight = conflict_weights.get(conflict["type"], 0.5)

            if conflict["type"] == "resource":
                severity = conflict.get("overlap", 0.5)
            else:
                severity = 1.0  # Data dependency conflicts are severe

            total_conflict_score += weight * severity

        # Normalize by number of potential conflicts
        max_possible_conflicts = len(other_branches) * 2  # Max 2 conflicts per branch
        normalized_score = min(1.0, total_conflict_score / max_possible_conflicts)

        return round(normalized_score, 3)

    def _extract_escalation_priority(self, context: dict[str, Any]) -> float:
        """Extract escalation priority (0.0-1.0)."""
        branch = context.get("branch", {})

        # Direct priority if provided
        if "escalation_priority" in branch:
            return float(branch["escalation_priority"])

        # Calculate from branch characteristics
        priority_indicators = {
            "business_criticality": 0.4,
            "deadline_urgency": 0.3,
            "error_handling": 0.2,
            "stakeholder_level": 0.1,
        }

        score = 0.0

        # Business criticality
        criticality = branch.get("business_criticality", "low")
        criticality_scores = {"low": 0.1, "medium": 0.5, "high": 0.8, "critical": 1.0}
        score += priority_indicators["business_criticality"] * criticality_scores.get(criticality, 0.1)

        # Deadline urgency
        deadline = branch.get("deadline")
        if deadline:
            try:
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))

                time_to_deadline = (deadline - datetime.now()).total_seconds()
                if time_to_deadline < 0:
                    urgency_score = 1.0  # Overdue
                elif time_to_deadline < 3600:  # Less than 1 hour
                    urgency_score = 0.9
                elif time_to_deadline < 86400:  # Less than 1 day
                    urgency_score = 0.7
                elif time_to_deadline < 604800:  # Less than 1 week
                    urgency_score = 0.4
                else:
                    urgency_score = 0.1

                score += priority_indicators["deadline_urgency"] * urgency_score
            except ValueError:
                pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow

        # Error handling requirements
        error_handling = branch.get("error_handling", {})
        if error_handling.get("requires_escalation", False):
            score += priority_indicators["error_handling"]

        # Stakeholder level
        stakeholders = branch.get("stakeholders", [])
        if stakeholders:
            stakeholder_levels = {"user": 0.3, "manager": 0.6, "executive": 0.9, "external": 1.0}
            max_level = 0.1
            for stakeholder in stakeholders:
                level = stakeholder_levels.get(stakeholder.get("level", "user"), 0.3)
                max_level = max(max_level, level)
            score += priority_indicators["stakeholder_level"] * max_level

        return round(min(1.0, score), 3)

    def _extract_workflow_depth(self, context: dict[str, Any]) -> int:
        """Extract workflow depth (1-10)."""
        branch = context.get("branch", {})

        # Direct depth if provided
        if "workflow_depth" in branch:
            return int(branch["workflow_depth"])

        # Calculate from branch hierarchy
        depth = self._calculate_max_depth(branch.get("nodes", []))
        return max(1, min(10, depth))

    def _extract_dependency_count(self, context: dict[str, Any]) -> int:
        """Extract dependency count (0-50)."""
        branch = context.get("branch", {})

        # Direct count if provided
        if "dependency_count" in branch:
            return int(branch["dependency_count"])

        # Calculate from dependencies
        dependencies = branch.get("dependencies", [])
        data_dependencies = branch.get("data_dependencies", [])

        total_dependencies = len(dependencies) + len(data_dependencies)
        return max(0, min(50, total_dependencies))

    def _extract_historical_success_rate(self, context: dict[str, Any]) -> float:
        """Extract historical success rate (0.0-1.0)."""
        branch = context.get("branch", {})
        history = context.get("history", {})

        # Direct rate if provided
        if "historical_success_rate" in branch:
            return float(branch["historical_success_rate"])

        # Calculate from historical executions
        similar_branches = history.get("similar_branches", [])
        if similar_branches:
            success_count = sum(1 for sb in similar_branches if sb.get("success", False))
            success_rate = success_count / len(similar_branches)
            return round(success_rate, 3)

        return 0.5  # Default if no history

    def _extract_timing_criticality(self, context: dict[str, Any]) -> float:
        """Extract timing criticality (0.0-1.0)."""
        branch = context.get("branch", {})

        # Direct criticality if provided
        if "timing_criticality" in branch:
            return float(branch["timing_criticality"])

        # Calculate from timing constraints
        timing_constraints = branch.get("timing_constraints", {})

        if not timing_constraints:
            return 0.1  # Low criticality if no constraints

        criticality_score = 0.0

        # Execution time limit
        time_limit = timing_constraints.get("max_execution_time_seconds")
        if time_limit:
            if time_limit < 60:  # Less than 1 minute
                criticality_score += 0.4
            elif time_limit < 300:  # Less than 5 minutes
                criticality_score += 0.3
            elif time_limit < 1800:  # Less than 30 minutes
                criticality_score += 0.2
            else:
                criticality_score += 0.1

        # Real-time requirements
        if timing_constraints.get("real_time", False):
            criticality_score += 0.4

        # Synchronization requirements
        sync_requirements = timing_constraints.get("synchronization", [])
        if sync_requirements:
            criticality_score += min(0.2, len(sync_requirements) * 0.1)

        return round(min(1.0, criticality_score), 3)

    def _extract_parallel_execution_potential(self, context: dict[str, Any]) -> float:
        """Extract parallel execution potential (0.0-1.0)."""
        branch = context.get("branch", {})

        # Direct potential if provided
        if "parallel_execution_potential" in branch:
            return float(branch["parallel_execution_potential"])

        # Calculate from branch structure
        nodes = branch.get("nodes", [])

        if not nodes:
            return 0.0

        # Analyze node dependencies
        independent_nodes = 0
        total_nodes = len(nodes)

        for node in nodes:
            dependencies = node.get("dependencies", [])
            if not dependencies:  # No dependencies = can run in parallel
                independent_nodes += 1

        # Calculate parallel potential
        parallel_ratio = independent_nodes / total_nodes if total_nodes > 0 else 0.0

        # Boost for branches with explicit parallel sections
        parallel_sections = branch.get("parallel_sections", [])
        if parallel_sections:
            parallel_boost = min(0.3, len(parallel_sections) * 0.1)
            parallel_ratio += parallel_boost

        return round(min(1.0, parallel_ratio), 3)

    def _calculate_max_depth(self, nodes: list[dict[str, Any]]) -> int:
        """Calculate maximum depth of nested nodes."""
        if not nodes:
            return 0

        max_depth = 0
        for node in nodes:
            node_depth = node.get("depth", 1)
            child_nodes = node.get("children", [])
            if child_nodes:
                child_depth = self._calculate_max_depth(child_nodes)
                node_depth += child_depth
            max_depth = max(max_depth, node_depth)

        return max_depth
