"""
Graph-aware safety monitoring for L5 safety layer.

Uses ADG graph analysis to identify safety-critical paths, monitor
system-wide risk, and enforce safety policies across the architecture.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import sys
from dataclasses import dataclass
from enum import Enum
import time

# Add tools to path for graph utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools"))

from tools.adg.analysis.sqlite_direct import GraphQueryHelper
from tools.adg.analysis.duckdb_integration import create_duckdb_analyzer

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety criticality levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SafetyViolation:
    """Safety violation detected by graph analysis."""

    violation_id: str
    violation_type: str
    severity: SafetyLevel
    affected_nodes: List[int]
    description: str
    mitigation_required: bool
    timestamp: float


class GraphAwareSafetyMonitor:
    """L5 safety monitor with graph-based risk assessment."""

    def __init__(self, adg_snapshot_path: str):
        """
        Initialize graph-aware safety monitor.

        Args:
            adg_snapshot_path: Path to ADG SQLite snapshot
        """
        self.graph_helper = GraphQueryHelper(adg_snapshot_path)
        self.duckdb_analyzer = create_duckdb_analyzer(adg_snapshot_path)
        self._safety_policies = self._load_safety_policies()
        self._active_violations = {}
        self._risk_cache = {}
        self._last_risk_assessment = 0

    def assess_system_safety(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Assess overall system safety using graph analysis.

        Args:
            force_refresh: Force refresh of cached risk assessment

        Returns:
            Comprehensive safety assessment
        """
        current_time = time.time()

        # Cache risk assessment for 60 seconds
        if not force_refresh and current_time - self._last_risk_assessment < 60:
            return self._risk_cache.get("last_assessment", {"error": "No cached assessment"})

        try:
            # Analyze safety-critical paths
            critical_paths = self._identify_safety_critical_paths()

            # Check for safety violations
            violations = self._detect_safety_violations()

            # Assess layer-specific risks
            layer_risks = self._assess_layer_risks()

            # Analyze dependency risks
            dependency_risks = self._analyze_dependency_risks()

            # Calculate overall safety score
            safety_score = self._calculate_safety_score(critical_paths, violations, layer_risks)

            assessment = {
                "timestamp": current_time,
                "safety_score": safety_score,
                "critical_paths": critical_paths,
                "violations": violations,
                "layer_risks": layer_risks,
                "dependency_risks": dependency_risks,
                "recommendations": self._generate_safety_recommendations(violations, layer_risks),
            }

            # Cache the assessment
            self._risk_cache["last_assessment"] = assessment
            self._last_risk_assessment = current_time

            return assessment

        except Exception as e:
            logger.error(f"Failed to assess system safety: {e}")
            return {"error": str(e), "timestamp": current_time}

    def _identify_safety_critical_paths(self) -> List[Dict[str, Any]]:
        """Identify safety-critical paths in the system."""
        try:
            # Query for safety-critical nodes and paths
            critical_nodes = self.graph_helper.execute_query("""
                SELECT
                    n.id,
                    n.adg_name,
                    n.layer,
                    n.node_type,
                    COUNT(DISTINCT e.src_id) as fan_in,
                    COUNT(DISTINCT e.tgt_id) as fan_out
                FROM nodes n
                JOIN edges e ON n.id = e.src_id OR n.id = e.tgt_id
                WHERE n.layer IN ('L0_routing', 'L5_safety', 'L3_orchestration')
                OR n.adg_name LIKE '%safety%'
                OR n.adg_name LIKE '%guard%'
                OR n.adg_name LIKE '%policy%'
                GROUP BY n.id, n.adg_name, n.layer, n.node_type
                HAVING fan_in > 5 OR fan_out > 5
                ORDER BY (fan_in * fan_out) DESC
            """)

            critical_paths = []
            for node in critical_nodes:
                node_id = node[0]

                # Get paths involving this critical node
                paths = self.graph_helper.execute_query(
                    """
                    SELECT
                        src_id,
                        tgt_id,
                        relation_type,
                        path_criticality_score
                    FROM mv_critical_path_blast_radius
                    WHERE src_id = ? OR tgt_id = ?
                    ORDER BY path_criticality_score DESC
                    LIMIT 5
                """,
                    [node_id, node_id],
                )

                critical_paths.append(
                    {
                        "node_id": node_id,
                        "node_name": node[1],
                        "layer": node[2],
                        "node_type": node[3],
                        "fan_in": node[4],
                        "fan_out": node[5],
                        "criticality_score": sum(p[3] for p in paths) if paths else 0,
                        "paths": paths,
                    }
                )

            return critical_paths

        except Exception as e:
            logger.error(f"Failed to identify safety-critical paths: {e}")
            return []

    def _detect_safety_violations(self) -> List[SafetyViolation]:
        """Detect safety violations using graph analysis."""
        violations = []

        try:
            # Check for unsafe exception handling
            unsafe_exceptions = self._detect_unsafe_exception_handling()
            violations.extend(unsafe_exceptions)

            # Check for security boundary violations
            security_violations = self._detect_security_violations()
            violations.extend(security_violations)

            # Check for state consistency violations
            state_violations = self._detect_state_consistency_violations()
            violations.extend(state_violations)

            # Check for execution boundary violations
            execution_violations = self._detect_execution_boundary_violations()
            violations.extend(execution_violations)

            return violations

        except Exception as e:
            logger.error(f"Failed to detect safety violations: {e}")
            return []

    def _detect_unsafe_exception_handling(self) -> List[SafetyViolation]:
        """Detect unsafe exception handling patterns."""
        violations = []

        try:
            # Query for broad exception handlers in critical paths
            unsafe_handlers = self.graph_helper.execute_query("""
                SELECT
                    n.id,
                    n.adg_name,
                    n.layer,
                    n.file_path
                FROM nodes n
                JOIN violations v ON n.id = v.node_id
                WHERE v.violation_type = 'broad_exception_catch'
                AND n.layer IN ('L0_routing', 'L5_safety', 'L3_orchestration')
            """)

            for handler in unsafe_handlers:
                violation = SafetyViolation(
                    violation_id=f"unsafe_exception_{handler[0]}",
                    violation_type="unsafe_exception_handling",
                    severity=SafetyLevel.HIGH,
                    affected_nodes=[handler[0]],
                    description=f"Broad exception handler in critical layer {handler[2]}: {handler[1]}",
                    mitigation_required=True,
                    timestamp=time.time(),
                )
                violations.append(violation)

        except Exception as e:
            logger.warning(f"Could not detect unsafe exception handling: {e}")

        return violations

    def _detect_security_violations(self) -> List[SafetyViolation]:
        """Detect security boundary violations."""
        violations = []

        try:
            # Check for cross-layer violations that breach security
            security_breaches = self.graph_helper.execute_query("""
                SELECT
                    e.src_id,
                    e.tgt_id,
                    n1.layer as src_layer,
                    n2.layer as tgt_layer,
                    n1.adg_name as src_name,
                    n2.adg_name as tgt_name
                FROM edges e
                JOIN nodes n1 ON e.src_id = n1.id
                JOIN nodes n2 ON e.tgt_id = n2.id
                WHERE e.relation_type = 'imports'
                AND (
                    (n1.layer = 'L1_cognition' AND n2.layer = 'L5_safety') OR
                    (n1.layer = 'L2_execution' AND n2.layer = 'L5_safety') OR
                    (n1.layer = 'L4_state' AND n2.layer = 'L1_cognition')
                )
            """)

            for breach in security_breaches:
                violation = SafetyViolation(
                    violation_id=f"security_breach_{breach[0]}_{breach[1]}",
                    violation_type="security_boundary_violation",
                    severity=SafetyLevel.CRITICAL,
                    affected_nodes=[breach[0], breach[1]],
                    description=f"Security boundary violation: {breach[4]} ({breach[2]}) -> {breach[5]} ({breach[3]})",
                    mitigation_required=True,
                    timestamp=time.time(),
                )
                violations.append(violation)

        except Exception as e:
            logger.warning(f"Could not detect security violations: {e}")

        return violations

    def _detect_state_consistency_violations(self) -> List[SafetyViolation]:
        """Detect state consistency violations."""
        violations = []

        try:
            # Check for state nodes with inconsistent access patterns
            state_inconsistency = self.graph_helper.execute_query("""
                SELECT
                    n.id,
                    n.adg_name,
                    COUNT(DISTINCT CASE WHEN e.relation_type = 'writes_to' THEN e.src_id END) as writers,
                    COUNT(DISTINCT CASE WHEN e.relation_type = 'reads_from' THEN e.src_id END) as readers
                FROM nodes n
                JOIN edges e ON n.id = e.tgt_id
                WHERE n.layer = 'L4_state'
                GROUP BY n.id, n.adg_name
                HAVING writers > 3 OR readers > 10
            """)

            for state_node in state_inconsistency:
                violation = SafetyViolation(
                    violation_id=f"state_inconsistency_{state_node[0]}",
                    violation_type="state_consistency_risk",
                    severity=SafetyLevel.MEDIUM,
                    affected_nodes=[state_node[0]],
                    description=f"State node {state_node[1]} has {state_node[2]} writers and {state_node[3]} readers",
                    mitigation_required=state_node[2] > 5,  # Critical if >5 writers
                    timestamp=time.time(),
                )
                violations.append(violation)

        except Exception as e:
            logger.warning(f"Could not detect state consistency violations: {e}")

        return violations

    def _detect_execution_boundary_violations(self) -> List[SafetyViolation]:
        """Detect execution boundary violations."""
        violations = []

        try:
            # Check for execution boundary crossings that bypass safety
            execution_violations = self.graph_helper.execute_query("""
                SELECT
                    e.src_id,
                    e.tgt_id,
                    n1.layer as src_layer,
                    n2.layer as tgt_layer,
                    n1.adg_name as src_name,
                    n2.adg_name as tgt_name
                FROM edges e
                JOIN nodes n1 ON e.src_id = n1.id
                JOIN nodes n2 ON e.tgt_id = n2.id
                WHERE e.relation_type = 'calls'
                AND n1.layer = 'L2_execution'
                AND n2.layer NOT IN ('L2_execution', 'L3_orchestration', 'L5_safety')
                AND n2.adg_name NOT LIKE '%test%'
            """)

            for violation in execution_violations:
                safety_violation = SafetyViolation(
                    violation_id=f"execution_boundary_{violation[0]}_{violation[1]}",
                    violation_type="execution_boundary_violation",
                    severity=SafetyLevel.HIGH,
                    affected_nodes=[violation[0], violation[1]],
                    description=f"Execution boundary violation: {violation[4]} calling {violation[5]} outside approved layers",
                    mitigation_required=True,
                    timestamp=time.time(),
                )
                violations.append(safety_violation)

        except Exception as e:
            logger.warning(f"Could not detect execution boundary violations: {e}")

        return violations

    def _assess_layer_risks(self) -> Dict[str, Any]:
        """Assess risks by architectural layer."""
        try:
            layer_analysis = self.duckdb_analyzer.get_layer_distribution()

            layer_risks = {}
            for layer_info in layer_analysis.get("layer_distribution", []):
                layer = layer_info["layer"]
                node_count = layer_info["node_count"]

                # Calculate risk score based on node count and complexity
                if node_count > 100:
                    risk_level = SafetyLevel.HIGH
                elif node_count > 50:
                    risk_level = SafetyLevel.MEDIUM
                else:
                    risk_level = SafetyLevel.LOW

                # Additional risk factors for critical layers
                if layer in ["L0_routing", "L5_safety"]:
                    risk_level = SafetyLevel(max(risk_level.value, SafetyLevel.HIGH.value))

                layer_risks[layer] = {
                    "risk_level": risk_level.value,
                    "node_count": node_count,
                    "complexity_score": min(node_count / 100, 1.0),
                }

            return layer_risks

        except Exception as e:
            logger.error(f"Failed to assess layer risks: {e}")
            return {}

    def _analyze_dependency_risks(self) -> Dict[str, Any]:
        """Analyze dependency-related risks."""
        try:
            import_patterns = self.duckdb_analyzer.analyze_import_patterns()

            high_risk_dependencies = []
            for pattern in import_patterns.get("import_patterns", []):
                source_layer = pattern["source_layer"]
                target_layer = pattern["target_layer"]
                import_count = pattern["import_count"]

                # High-risk dependency patterns
                if (
                    source_layer in ["L1_cognition", "L2_execution"]
                    and target_layer in ["L0_routing", "L5_safety"]
                    and import_count > 5
                ):
                    high_risk_dependencies.append(
                        {
                            "source_layer": source_layer,
                            "target_layer": target_layer,
                            "import_count": import_count,
                            "risk_reason": f"High-count imports ({import_count}) from lower to higher security layer",
                        }
                    )

            return {
                "high_risk_dependencies": high_risk_dependencies,
                "total_import_patterns": len(import_patterns.get("import_patterns", [])),
            }

        except Exception as e:
            logger.error(f"Failed to analyze dependency risks: {e}")
            return {}

    def _calculate_safety_score(
        self, critical_paths: List[Dict], violations: List[SafetyViolation], layer_risks: Dict[str, Any]
    ) -> float:
        """Calculate overall safety score (0-100)."""
        base_score = 100.0

        # Deduct points for violations
        for violation in violations:
            if violation.severity == SafetyLevel.CRITICAL:
                base_score -= 20
            elif violation.severity == SafetyLevel.HIGH:
                base_score -= 10
            elif violation.severity == SafetyLevel.MEDIUM:
                base_score -= 5
            else:
                base_score -= 2

        # Deduct points for layer risks
        for layer, risk_info in layer_risks.items():
            if risk_info["risk_level"] == SafetyLevel.HIGH:
                base_score -= 5
            elif risk_info["risk_level"] == SafetyLevel.MEDIUM:
                base_score -= 2

        # Deduct points for critical path complexity
        if len(critical_paths) > 20:
            base_score -= 10
        elif len(critical_paths) > 10:
            base_score -= 5

        return max(0.0, min(100.0, base_score))

    def _generate_safety_recommendations(
        self, violations: List[SafetyViolation], layer_risks: Dict[str, Any]
    ) -> List[str]:
        """Generate safety recommendations based on analysis."""
        recommendations = []

        # Violation-based recommendations
        critical_violations = [v for v in violations if v.severity == SafetyLevel.CRITICAL]
        if critical_violations:
            recommendations.append(
                "URGENT: Address {} critical safety violations immediately".format(len(critical_violations))
            )

        high_violations = [v for v in violations if v.severity == SafetyLevel.HIGH]
        if high_violations:
            recommendations.append(
                "HIGH: Address {} high-severity safety violations".format(len(high_violations))
            )

        # Layer-based recommendations
        high_risk_layers = [
            layer for layer, risk in layer_risks.items() if risk["risk_level"] == SafetyLevel.HIGH
        ]
        if high_risk_layers:
            recommendations.append(
                "Review and reduce complexity in high-risk layers: {}".format(", ".join(high_risk_layers))
            )

        # General recommendations
        if len(violations) > 10:
            recommendations.append("Consider implementing automated safety monitoring and enforcement")

        if not recommendations:
            recommendations.append("System safety posture is acceptable - continue monitoring")

        return recommendations

    def _load_safety_policies(self) -> Dict[str, Any]:
        """Load safety policies (placeholder for future implementation)."""
        return {
            "max_fan_in_critical": 20,
            "max_fan_out_critical": 15,
            "forbidden_layer_crossings": [
                ("L1_cognition", "L5_safety"),
                ("L2_execution", "L5_safety"),
                ("L4_state", "L1_cognition"),
            ],
            "required_safety_layers": ["L0_routing", "L5_safety"],
        }

    def get_active_violations(self) -> Dict[str, SafetyViolation]:
        """Get currently active safety violations."""
        return self._active_violations.copy()

    def close(self):
        """Clean up resources."""
        self.graph_helper.close()
        self.duckdb_analyzer.close()


# Singleton instance for L5 safety
_safety_monitor = None


def get_safety_monitor(adg_snapshot_path: Optional[str] = None) -> GraphAwareSafetyMonitor:
    """Get or create safety monitor singleton."""
    global _safety_monitor

    if _safety_monitor is None:
        if adg_snapshot_path is None:
            raise ValueError("ADG snapshot path required for first initialization")
        _safety_monitor = GraphAwareSafetyMonitor(adg_snapshot_path)

    return _safety_monitor
