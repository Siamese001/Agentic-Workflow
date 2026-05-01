"""
Graph-aware routing capabilities for L0 routing layer.

Uses ADG graph analysis to make intelligent routing decisions based on
dependency patterns, layer boundaries, and system topology.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sys

# Add tools to path for graph utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools"))

from tools.adg.analysis.sqlite_direct import GraphQueryHelper
from tools.adg.analysis.duckdb_integration import create_duckdb_analyzer

logger = logging.getLogger(__name__)


class GraphAwareRouter:
    """L0 router with graph-based decision making."""

    def __init__(self, adg_snapshot_path: str):
        """
        Initialize graph-aware router.

        Args:
            adg_snapshot_path: Path to ADG SQLite snapshot
        """
        self.graph_helper = GraphQueryHelper(adg_snapshot_path)
        self.duckdb_analyzer = create_duckdb_analyzer(adg_snapshot_path)
        self._routing_cache = {}

    def route_request(self, request_type: str, target_module: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request using graph-based analysis.

        Args:
            request_type: Type of request (e.g., 'execute', 'query', 'analyze')
            target_module: Target module name
            context: Additional context for routing decision

        Returns:
            Routing decision with path and rationale
        """
        cache_key = f"{request_type}:{target_module}"
        if cache_key in self._routing_cache:
            return self._routing_cache[cache_key]

        # Analyze target module in graph context
        target_analysis = self._analyze_target_module(target_module)

        # Determine optimal routing path
        routing_decision = self._determine_routing_path(request_type, target_analysis, context)

        # Cache the decision
        self._routing_cache[cache_key] = routing_decision

        return routing_decision

    def _analyze_target_module(self, target_module: str) -> Dict[str, Any]:
        """Analyze target module within graph context."""
        try:
            # Find target node(s)
            target_nodes = self.graph_helper.find_nodes_by_name(target_module)

            if not target_nodes:
                return {"error": f"Module {target_module} not found in ADG"}

            # Get primary target node
            primary_node = target_nodes[0]
            node_id = primary_node["id"]

            # Analyze dependencies and impact
            fan_in = self.graph_helper.get_fan_in(node_id, relation_types=["imports", "calls"])
            fan_out = self.graph_helper.get_fan_out(node_id, relation_types=["imports", "calls"])

            # Check layer boundaries
            layer_info = primary_node.get("layer", "unknown")

            # Identify critical paths
            critical_paths = self._identify_critical_paths(node_id)

            return {
                "node_id": node_id,
                "module_name": target_module,
                "layer": layer_info,
                "fan_in": fan_in,
                "fan_out": fan_out,
                "critical_paths": critical_paths,
                "risk_assessment": self._assess_risk(fan_in, fan_out, layer_info),
            }

        except Exception as e:  # guardian: allow-broad-exception -- ADG query failure: non-fatal; returns error dict so caller can degrade gracefully
            logger.error(f"Failed to analyze target module {target_module}: {e}")
            return {"error": str(e)}

    def _determine_routing_path(
        self, request_type: str, target_analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine optimal routing path based on graph analysis."""
        if "error" in target_analysis:
            return {
                "routing_decision": "error",
                "reason": target_analysis["error"],
                "suggested_action": "fallback_to_default_routing",
            }

        layer = target_analysis["layer"]
        risk = target_analysis["risk_assessment"]

        # Routing logic based on layer and request type
        if request_type == "execute":
            if layer == "L2_execution":
                if risk["level"] == "high":
                    return {
                        "routing_decision": "execute_with_safeguards",
                        "path": "L2_execution_with_monitoring",
                        "reason": f"High-risk execution module ({risk['reason']})",
                        "safeguards": ["enhanced_logging", "circuit_breaker", "timeout_enforcement"],
                    }
                else:
                    return {
                        "routing_decision": "direct_execute",
                        "path": "L2_execution_direct",
                        "reason": "Standard execution module with acceptable risk",
                    }

            elif layer == "L3_orchestration":
                return {
                    "routing_decision": "orchestrated_execute",
                    "path": "L3_orchestration_coordinated",
                    "reason": "Orchestration layer requires coordination",
                }

            else:
                return {
                    "routing_decision": "cross_layer_execute",
                    "path": f"cross_layer_{layer}_to_L2",
                    "reason": f"Cross-layer execution from {layer} to L2",
                }

        elif request_type == "query":
            # For queries, prefer read-optimized paths
            if layer in ["L4_state", "L6_observability"]:
                return {
                    "routing_decision": "direct_query",
                    "path": f"{layer}_read_optimized",
                    "reason": f"Read-optimized path for {layer}",
                }
            else:
                return {
                    "routing_decision": "standard_query",
                    "path": "generic_query_path",
                    "reason": "Standard query path for non-optimized layer",
                }

        else:
            return {
                "routing_decision": "default_routing",
                "path": "standard_path",
                "reason": f"No specific routing logic for request_type={request_type}",
            }

    def _identify_critical_paths(self, node_id: int) -> List[Dict[str, Any]]:
        """Identify critical paths involving this node."""
        try:
            # Use materialized views for critical path analysis
            critical_paths = self.graph_helper.execute_query(
                """
                SELECT
                    src_id,
                    tgt_id,
                    relation_type,
                    path_criticality_score
                FROM mv_critical_path_blast_radius
                WHERE src_id = ? OR tgt_id = ?
                ORDER BY path_criticality_score DESC
                LIMIT 10
            """,
                [node_id, node_id],
            )

            return critical_paths

        except Exception as e:  # guardian: allow-broad-exception -- critical path query failure: non-fatal; empty list signals no paths found
            logger.warning(f"Could not identify critical paths: {e}")
            return []

    def _assess_risk(self, fan_in: List[Dict], fan_out: List[Dict], layer: str) -> Dict[str, Any]:
        """Assess risk level based on graph metrics."""
        fan_in_count = len(fan_in)
        fan_out_count = len(fan_out)

        # Risk factors
        high_fan_in = fan_in_count > 20
        high_fan_out = fan_out_count > 15
        critical_layer = layer in ["L0_routing", "L5_safety", "L3_orchestration"]

        risk_score = 0
        risk_factors = []

        if high_fan_in:
            risk_score += 2
            risk_factors.append(f"high_fan_in ({fan_in_count})")

        if high_fan_out:
            risk_score += 2
            risk_factors.append(f"high_fan_out ({fan_out_count})")

        if critical_layer:
            risk_score += 3
            risk_factors.append(f"critical_layer ({layer})")

        # Determine risk level
        if risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "level": risk_level,
            "score": risk_score,
            "factors": risk_factors,
            "fan_in_count": fan_in_count,
            "fan_out_count": fan_out_count,
        }

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics and performance metrics."""
        try:
            # Use DuckDB for routing analytics
            layer_stats = self.duckdb_analyzer.get_layer_distribution()

            return {
                "cache_size": len(self._routing_cache),
                "layer_distribution": layer_stats,
                "routing_health": "healthy",
            }

        except Exception as e:  # guardian: allow-broad-exception -- routing stats query failure: non-fatal; returns error dict
            logger.error(f"Failed to get routing statistics: {e}")
            return {"error": str(e)}

    def invalidate_cache(self):
        """Invalidate routing cache."""
        self._routing_cache.clear()
        logger.info("Routing cache invalidated")

    def close(self):
        """Clean up resources."""
        self.graph_helper.close()
        self.duckdb_analyzer.close()


# Singleton instance for L0 routing
_graph_router = None


def get_graph_router(adg_snapshot_path: Optional[str] = None) -> GraphAwareRouter:
    """Get or create graph router singleton."""
    global _graph_router

    if _graph_router is None:
        if adg_snapshot_path is None:
            raise ValueError("ADG snapshot path required for first initialization")
        _graph_router = GraphAwareRouter(adg_snapshot_path)

    return _graph_router


def route_with_graph_awareness(
    request_type: str, target_module: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function for graph-aware routing.

    Args:
        request_type: Type of request
        target_module: Target module name
        context: Additional context

    Returns:
        Routing decision
    """
    router = get_graph_router()
    return router.route_request(request_type, target_module, context)
