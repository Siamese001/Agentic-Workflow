"""Ecosystem Intelligence - Cross-system architectural awareness and boundary detection.

This module provides ecosystem intelligence capabilities that enable
agents to understand and navigate complex multi-system architectures.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import networkx as nx
from tqdm import tqdm

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase2.contextual_engine import ContextualIntelligenceEngine, AnalysisResult

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Types of systems in the ecosystem."""

    MONOLITH = "monolith"
    MICROSERVICE = "microservice"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    GATEWAY = "gateway"
    EVENT_BUS = "event_bus"


class BoundaryType(Enum):
    """Types of architectural boundaries."""

    API_BOUNDARY = "api_boundary"
    DATABASE_BOUNDARY = "database_boundary"
    SERVICE_BOUNDARY = "service_boundary"
    DOMAIN_BOUNDARY = "domain_boundary"
    TEAM_BOUNDARY = "team_boundary"
    DEPLOYMENT_BOUNDARY = "deployment_boundary"


@dataclass
class SystemBoundary:
    """Represents an architectural boundary between systems."""

    boundary_id: str
    boundary_type: BoundaryType
    source_system: str
    target_system: str
    interface_type: str
    coupling_strength: float  # 0.0 to 1.0
    data_flow_direction: str  # unidirectional, bidirectional
    protocols: List[str]
    security_level: str  # public, internal, restricted
    governance_rules: List[str]
    health_status: str = "healthy"


@dataclass
class EcosystemNode:
    """Represents a node in the ecosystem graph."""

    node_id: str
    system_type: SystemType
    repository: str
    service_name: Optional[str]
    domain: str
    team: str
    dependencies: List[str]
    dependents: List[str]
    boundaries: List[str]
    health_metrics: Dict[str, float]
    governance_compliance: float  # 0.0 to 1.0


@dataclass
class EcosystemAnalysis:
    """Result of ecosystem-wide analysis."""

    ecosystem_nodes: Dict[str, EcosystemNode]
    system_boundaries: Dict[str, SystemBoundary]
    cross_system_dependencies: Dict[str, List[str]]
    architectural_hotspots: List[str]
    governance_violations: List[Dict[str, Any]]
    health_summary: Dict[str, float]
    recommendations: List[str]
    confidence_score: float
    execution_time_seconds: float = 0.0


class EcosystemIntelligenceEngine:
    """Ecosystem intelligence engine for cross-system architectural awareness."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize ecosystem intelligence engine.

        Args:
            contextual_engine: Contextual intelligence engine for base analysis
        """
        self.contextual_engine = contextual_engine

        # Ecosystem graph
        self.ecosystem_graph = nx.DiGraph()

        # System registry
        self.system_registry: Dict[str, EcosystemNode] = {}
        self.boundary_registry: Dict[str, SystemBoundary] = {}

        # Analysis cache
        self.ecosystem_cache: Dict[str, EcosystemAnalysis] = {}

        # Boundary detection patterns
        self.boundary_patterns = self._initialize_boundary_patterns()

        # Health thresholds
        self.health_thresholds = {
            "dependency_complexity": 0.7,
            "coupling_strength": 0.8,
            "governance_compliance": 0.9,
            "system_stability": 0.8,
        }

        logger.info("EcosystemIntelligenceEngine initialized")

    def analyze_ecosystem(self, scope: Optional[List[str]] = None) -> EcosystemAnalysis:
        """Perform comprehensive ecosystem analysis.

        Args:
            scope: Optional list of repositories/systems to analyze (None for full ecosystem)

        Returns:
            EcosystemAnalysis with comprehensive ecosystem insights
        """
        start_time = time.time()

        logger.info("Starting comprehensive ecosystem analysis")

        # Build ecosystem graph
        self._build_ecosystem_graph(scope)

        # Detect system boundaries
        boundaries = self._detect_system_boundaries()

        # Analyze cross-system dependencies
        cross_system_deps = self._analyze_cross_system_dependencies()

        # Identify architectural hotspots
        hotspots = self._identify_architectural_hotspots()

        # Check governance compliance
        violations = self._check_governance_compliance()

        # Calculate health metrics
        health_summary = self._calculate_ecosystem_health()

        # Generate recommendations
        recommendations = self._generate_ecosystem_recommendations(
            boundaries, cross_system_deps, hotspots, violations, health_summary
        )

        # Calculate confidence score
        confidence_score = self._calculate_ecosystem_confidence()

        analysis = EcosystemAnalysis(
            ecosystem_nodes=self.system_registry,
            system_boundaries=boundaries,
            cross_system_dependencies=cross_system_deps,
            architectural_hotspots=hotspots,
            governance_violations=violations,
            health_summary=health_summary,
            recommendations=recommendations,
            confidence_score=confidence_score,
            execution_time_seconds=time.time() - start_time,
        )

        # Cache analysis
        cache_key = f"ecosystem_analysis_{hash(str(scope))}"
        self.ecosystem_cache[cache_key] = analysis

        logger.info(f"Ecosystem analysis completed in {analysis.execution_time_seconds:.3f}s")

        return analysis

    def detect_boundary_violations(self, context: ArchitecturalContext) -> List[Dict[str, Any]]:
        """Detect boundary violations for a given context.

        Args:
            context: Architectural context to check for violations

        Returns:
            List of boundary violations detected
        """
        violations = []

        for module in tqdm(context.target_modules, desc="boundary modules", unit="module", leave=False):
            # Check if module crosses system boundaries
            module_boundaries = self._get_module_boundaries(module)

            for boundary in tqdm(module_boundaries, desc="  boundaries", unit="boundary", leave=False):
                boundary_info = self.boundary_registry.get(boundary)
                if not boundary_info:
                    continue

                # Check if action violates boundary rules
                if self._violates_boundary_rules(context, boundary_info):
                    violations.append(
                        {
                            "type": "boundary_violation",
                            "module": module,
                            "boundary": boundary,
                            "boundary_type": boundary_info.boundary_type.value,
                            "violation_type": "rule_breach",
                            "severity": self._calculate_violation_severity(boundary_info),
                            "recommendation": f"Respect {boundary_info.boundary_type.value} boundary rules",
                        }
                    )

        return violations

    def get_ecosystem_impact(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Get ecosystem-wide impact analysis for proposed changes.

        Args:
            context: Architectural context for impact analysis

        Returns:
            Ecosystem-wide impact analysis
        """
        impact_analysis = {
            "direct_impact": [],
            "indirect_impact": [],
            "cross_system_impact": [],
            "boundary_impact": [],
            "risk_assessment": "low",
        }

        # Analyze direct impact
        for module in tqdm(context.target_modules, desc="impact modules", unit="module", leave=False):
            if module in self.system_registry:
                node = self.system_registry[module]
                impact_analysis["direct_impact"].append(
                    {
                        "module": module,
                        "system_type": node.system_type.value,
                        "dependents": node.dependents,
                        "criticality": self._calculate_module_criticality(node),
                    }
                )

        # Analyze cross-system impact
        cross_system_modules = set()
        for module in context.target_modules:
            boundaries = self._get_module_boundaries(module)
            for boundary in boundaries:
                boundary_info = self.boundary_registry.get(boundary)
                if boundary_info:
                    cross_system_modules.add(boundary_info.source_system)
                    cross_system_modules.add(boundary_info.target_system)

        impact_analysis["cross_system_impact"] = list(cross_system_modules)

        # Assess overall risk
        if len(impact_analysis["cross_system_impact"]) > 3:
            impact_analysis["risk_assessment"] = "high"
        elif len(impact_analysis["cross_system_impact"]) > 1:
            impact_analysis["risk_assessment"] = "medium"

        return impact_analysis

    def _build_ecosystem_graph(self, scope: Optional[List[str]]) -> None:
        """Build the ecosystem graph from available data."""
        # This would integrate with actual ecosystem data sources
        # For now, create a mock ecosystem graph

        self.ecosystem_graph.clear()
        self.system_registry.clear()

        # Mock ecosystem nodes
        mock_systems = [
            {
                "node_id": "user_service",
                "system_type": SystemType.MICROSERVICE,
                "repository": "user-service",
                "service_name": "user-service",
                "domain": "user_management",
                "team": "identity_team",
                "dependencies": ["auth_service", "database"],
                "dependents": ["order_service", "notification_service"],
            },
            {
                "node_id": "order_service",
                "system_type": SystemType.MICROSERVICE,
                "repository": "order-service",
                "service_name": "order-service",
                "domain": "order_management",
                "team": "commerce_team",
                "dependencies": ["user_service", "payment_service", "inventory_service"],
                "dependents": ["shipping_service"],
            },
            {
                "node_id": "auth_service",
                "system_type": SystemType.MICROSERVICE,
                "repository": "auth-service",
                "service_name": "auth-service",
                "domain": "authentication",
                "team": "identity_team",
                "dependencies": ["database"],
                "dependents": ["user_service", "order_service"],
            },
        ]

        # Create ecosystem nodes
        for system_data in tqdm(mock_systems, desc="ecosystem nodes", unit="system", leave=False):
            node = EcosystemNode(
                node_id=system_data["node_id"],
                system_type=system_data["system_type"],
                repository=system_data["repository"],
                service_name=system_data["service_name"],
                domain=system_data["domain"],
                team=system_data["team"],
                dependencies=system_data["dependencies"],
                dependents=system_data["dependents"],
                boundaries=[],
                health_metrics={"stability": 0.9, "performance": 0.8, "availability": 0.95},
                governance_compliance=0.85,
            )

            self.system_registry[node.node_id] = node
            self.ecosystem_graph.add_node(node.node_id, **node.__dict__)

        # Add edges for dependencies
        for node in self.system_registry.values():
            for dep in node.dependencies:
                if dep in self.system_registry:
                    self.ecosystem_graph.add_edge(node.node_id, dep, relationship="depends_on")

    def _detect_system_boundaries(self) -> Dict[str, SystemBoundary]:
        """Detect architectural boundaries in the ecosystem."""
        boundaries = {}

        # Detect API boundaries
        api_boundaries = self._detect_api_boundaries()
        boundaries.update(api_boundaries)

        # Detect database boundaries
        db_boundaries = self._detect_database_boundaries()
        boundaries.update(db_boundaries)

        # Detect service boundaries
        service_boundaries = self._detect_service_boundaries()
        boundaries.update(service_boundaries)

        # Update boundary registry
        self.boundary_registry = boundaries

        return boundaries

    def _detect_api_boundaries(self) -> Dict[str, SystemBoundary]:
        """Detect API boundaries between systems."""
        boundaries = {}

        # Mock API boundary detection
        boundary_pairs = [
            ("user_service", "order_service"),
            ("auth_service", "user_service"),
            ("order_service", "payment_service"),
        ]

        for source, target in tqdm(boundary_pairs, desc="API boundaries", unit="pair", leave=False):
            boundary_id = f"api_boundary_{source}_{target}"
            boundary = SystemBoundary(
                boundary_id=boundary_id,
                boundary_type=BoundaryType.API_BOUNDARY,
                source_system=source,
                target_system=target,
                interface_type="REST_API",
                coupling_strength=0.6,
                data_flow_direction="bidirectional",
                protocols=["HTTP", "HTTPS"],
                security_level="internal",
                governance_rules=["api_versioning", "authentication_required", "rate_limiting"],
            )
            boundaries[boundary_id] = boundary

        return boundaries

    def _detect_database_boundaries(self) -> Dict[str, SystemBoundary]:
        """Detect database boundaries between systems."""
        boundaries = {}

        # Mock database boundary detection
        boundary_pairs = [
            ("user_service", "database"),
            ("order_service", "database"),
            ("auth_service", "database"),
        ]

        for source, target in tqdm(boundary_pairs, desc="DB boundaries", unit="pair", leave=False):
            boundary_id = f"db_boundary_{source}_{target}"
            boundary = SystemBoundary(
                boundary_id=boundary_id,
                boundary_type=BoundaryType.DATABASE_BOUNDARY,
                source_system=source,
                target_system=target,
                interface_type="DATABASE_CONNECTION",
                coupling_strength=0.8,
                data_flow_direction="bidirectional",
                protocols=["SQL", "Connection_Pool"],
                security_level="restricted",
                governance_rules=["connection_pooling", "transaction_management", "data_encryption"],
            )
            boundaries[boundary_id] = boundary

        return boundaries

    def _detect_service_boundaries(self) -> Dict[str, SystemBoundary]:
        """Detect service boundaries between systems."""
        boundaries = {}

        # Mock service boundary detection
        boundary_pairs = [("user_service", "notification_service"), ("order_service", "shipping_service")]

        for source, target in tqdm(boundary_pairs, desc="svc boundaries", unit="pair", leave=False):
            boundary_id = f"service_boundary_{source}_{target}"
            boundary = SystemBoundary(
                boundary_id=boundary_id,
                boundary_type=BoundaryType.SERVICE_BOUNDARY,
                source_system=source,
                target_system=target,
                interface_type="EVENT_DRIVEN",
                coupling_strength=0.3,
                data_flow_direction="unidirectional",
                protocols=["Message_Queue", "Event_Bus"],
                security_level="internal",
                governance_rules=["event_schema", "async_processing", "error_handling"],
            )
            boundaries[boundary_id] = boundary

        return boundaries

    def _analyze_cross_system_dependencies(self) -> Dict[str, List[str]]:
        """Analyze cross-system dependencies."""
        cross_system_deps = defaultdict(list)

        for node in self.system_registry.values():
            for dep in node.dependencies:
                if dep in self.system_registry:
                    # Check if dependency crosses system boundaries
                    if node.system_type != self.system_registry[dep].system_type:
                        cross_system_deps[node.node_id].append(dep)

        return dict(cross_system_deps)

    def _identify_architectural_hotspots(self) -> List[str]:
        """Identify architectural hotspots in the ecosystem."""
        hotspots = []

        # High coupling hotspots
        for node in self.system_registry.values():
            if len(node.dependencies) > 5 or len(node.dependents) > 10:
                hotspots.append(f"High coupling: {node.node_id}")

        # Boundary violation hotspots
        for boundary in self.boundary_registry.values():
            if boundary.coupling_strength > 0.8:
                hotspots.append(f"Tight coupling boundary: {boundary.boundary_id}")

        # Governance compliance hotspots
        for node in self.system_registry.values():
            if node.governance_compliance < 0.7:
                hotspots.append(f"Low compliance: {node.node_id}")

        return hotspots

    def _check_governance_compliance(self) -> List[Dict[str, Any]]:
        """Check governance compliance across the ecosystem."""
        violations = []

        for node in tqdm(self.system_registry.values(), desc="compliance nodes", unit="node", leave=False):
            if node.governance_compliance < self.health_thresholds["governance_compliance"]:
                violations.append(
                    {
                        "type": "governance_violation",
                        "node": node.node_id,
                        "compliance_score": node.governance_compliance,
                        "severity": "high" if node.governance_compliance < 0.5 else "medium",
                        "recommendation": "Improve governance compliance for this system",
                    }
                )

        return violations

    def _calculate_ecosystem_health(self) -> Dict[str, float]:
        """Calculate overall ecosystem health metrics."""
        health_metrics = {
            "overall_health": 0.0,
            "average_compliance": 0.0,
            "system_stability": 0.0,
            "boundary_health": 0.0,
        }

        if not self.system_registry:
            return health_metrics

        # Calculate average compliance
        compliance_scores = [node.governance_compliance for node in self.system_registry.values()]
        health_metrics["average_compliance"] = sum(compliance_scores) / len(compliance_scores)

        # Calculate system stability
        stability_scores = [
            node.health_metrics.get("stability", 0.5) for node in self.system_registry.values()
        ]
        health_metrics["system_stability"] = sum(stability_scores) / len(stability_scores)

        # Calculate boundary health
        if self.boundary_registry:
            boundary_scores = [
                1.0 - boundary.coupling_strength for boundary in self.boundary_registry.values()
            ]
            health_metrics["boundary_health"] = sum(boundary_scores) / len(boundary_scores)

        # Calculate overall health
        health_metrics["overall_health"] = (
            health_metrics["average_compliance"] * 0.4
            + health_metrics["system_stability"] * 0.3
            + health_metrics["boundary_health"] * 0.3
        )

        return health_metrics

    def _generate_ecosystem_recommendations(
        self,
        boundaries: Dict[str, SystemBoundary],
        cross_system_deps: Dict[str, List[str]],
        hotspots: List[str],
        violations: List[Dict[str, Any]],
        health_summary: Dict[str, float],
    ) -> List[str]:
        """Generate ecosystem improvement recommendations."""
        recommendations = []

        # Health-based recommendations
        if health_summary["overall_health"] < 0.8:
            recommendations.append(
                "Overall ecosystem health below threshold: implement health improvement plan"
            )

        if health_summary["average_compliance"] < 0.9:
            recommendations.append("Governance compliance below target: strengthen governance processes")

        # Hotspot-based recommendations
        if hotspots:
            recommendations.append(f"Address {len(hotspots)} architectural hotspots identified")

        # Violation-based recommendations
        if violations:
            recommendations.append(f"Resolve {len(violations)} governance violations")

        # Boundary-based recommendations
        tight_boundaries = [b for b in boundaries.values() if b.coupling_strength > 0.8]
        if tight_boundaries:
            recommendations.append(f"Reduce coupling in {len(tight_boundaries)} tight boundaries")

        # Cross-system dependency recommendations
        if len(cross_system_deps) > 10:
            recommendations.append(
                "High cross-system dependency complexity: consider architectural simplification"
            )

        return recommendations

    def _calculate_ecosystem_confidence(self) -> float:
        """Calculate confidence in ecosystem analysis."""
        base_confidence = 0.7

        # Adjust based on data completeness
        if len(self.system_registry) > 5:
            base_confidence += 0.1

        # Adjust based on boundary detection
        if len(self.boundary_registry) > 3:
            base_confidence += 0.1

        return min(1.0, base_confidence)

    def _get_module_boundaries(self, module: str) -> List[str]:
        """Get boundaries associated with a module."""
        boundaries = []

        # This would integrate with actual module-boundary mapping
        # For now, return mock boundaries
        if "user" in module.lower():
            boundaries.append("api_boundary_user_service_order_service")
            boundaries.append("db_boundary_user_service_database")
        elif "order" in module.lower():
            boundaries.append("api_boundary_order_service_payment_service")
            boundaries.append("db_boundary_order_service_database")

        return boundaries

    def _violates_boundary_rules(self, context: ArchitecturalContext, boundary: SystemBoundary) -> bool:
        """Check if context violates boundary rules."""
        # Mock boundary rule checking
        if boundary.security_level == "restricted" and context.action_type in ["write_file", "delete_file"]:
            return True

        if boundary.coupling_strength > 0.8 and context.action_type in ["modify_module", "refactor"]:
            return True

        return False

    def _calculate_violation_severity(self, boundary: SystemBoundary) -> str:
        """Calculate severity of boundary violation."""
        if boundary.security_level == "restricted":
            return "critical"
        elif boundary.coupling_strength > 0.8:
            return "high"
        elif boundary.coupling_strength > 0.6:
            return "medium"
        else:
            return "low"

    def _calculate_module_criticality(self, node: EcosystemNode) -> str:
        """Calculate criticality of a module."""
        if len(node.dependents) > 10:
            return "critical"
        elif len(node.dependents) > 5:
            return "high"
        elif len(node.dependents) > 2:
            return "medium"
        else:
            return "low"

    def _initialize_boundary_patterns(self) -> Dict[str, Any]:
        """Initialize boundary detection patterns."""
        return {
            "api_patterns": ["rest_api", "graphql", "grpc"],
            "database_patterns": ["sql", "nosql", "connection_pool"],
            "service_patterns": ["message_queue", "event_bus", "rpc"],
            "security_levels": ["public", "internal", "restricted"],
        }

    def get_ecosystem_statistics(self) -> Dict[str, Any]:
        """Get ecosystem intelligence statistics."""
        return {
            "total_systems": len(self.system_registry),
            "total_boundaries": len(self.boundary_registry),
            "system_types": {
                system_type.value: len(
                    [n for n in self.system_registry.values() if n.system_type == system_type]
                )
                for system_type in SystemType
            },
            "boundary_types": {
                boundary_type.value: len(
                    [b for b in self.boundary_registry.values() if b.boundary_type == boundary_type]
                )
                for boundary_type in BoundaryType
            },
            "average_coupling": sum(b.coupling_strength for b in self.boundary_registry.values())
            / len(self.boundary_registry)
            if self.boundary_registry
            else 0.0,
            "cached_analyses": len(self.ecosystem_cache),
        }
