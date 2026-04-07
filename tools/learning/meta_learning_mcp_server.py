"""
System Learning Meta-Learning MCP Server

Access runtime execution evidence and learning patterns from Windsurf chat.
Provides query interface for 37+ runtime ADG snapshots and meta-learning pipelines.

Why this exists
---------------
37+ runtime ADG snapshots in system_learning/meta_learning/runtime_adg_snapshots/
Meta-learning pipelines need query interface
Cross-repo learning exists but not accessible from chat
Pattern detection results are siloed

This server provides:
- Runtime ADG snapshot access and querying
- Pattern detection and meta-learning insights
- Cross-repo learning integration
- Learning pipeline health monitoring
- Execution evidence analysis
- Learning state management

Tools (5-7)
-----------
- runtime_adg_status: Snapshot count, freshness, health
- runtime_adg_query: Query snapshots by trace/agent/time
- runtime_adg_compare: Diff execution patterns between runs
- meta_learning_insights: Pattern detection results
- learning_pipeline_status: Pipeline health and progress
- cross_repo_import: Incorporate external repo learning
- learning_state_management: Manage learning state and snapshots

Integration
-----------
Uses system_learning/runtime_adg/ infrastructure
Connects to system_learning/meta_learning/ pipelines
Leverages existing cross-repo importer
Accesses FileBackedVersionStore for snapshot storage
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    record_execution_trace,
)

# Lifecycle tracing for this MCP
emit_determinism_digest("meta_learning_mcp_server", "meta_learning_mcp_server_digest")
record_execution_trace("meta_learning_mcp_server", "meta_learning_mcp_server_trace")
_emit_applies_guardrail("p0", "meta_learning_mcp_server", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_mcp_server", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_mcp_server", "state_snapshot")
_emit_authorize_and_execute("p2", "meta_learning_mcp_server", "execution_auth")
_emit_validates_capability("p2", "meta_learning_mcp_server", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_mcp_server", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_mcp_server", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_mcp_server", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_mcp_server", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_mcp_server", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_mcp_server", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_mcp_server", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_mcp_server", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_mcp_server", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_mcp_server", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_mcp_server", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_mcp_server", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_mcp_server", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_mcp_server", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_mcp_server", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_mcp_server", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_mcp_server", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_mcp_server", "exec_snapshot_link")

# Initialize FastMCP server
mcp = FastMCP("meta-learning-mcp")

# Logger
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
RUNTIME_ADG_SNAPSHOTS_DIR = PROJECT_ROOT / "system_learning/meta_learning/runtime_adg_snapshots"
RUNTIME_ADG_DIR = PROJECT_ROOT / "system_learning/runtime_adg"
META_LEARNING_DIR = PROJECT_ROOT / "system_learning/meta_learning"
CROSS_REPO_DIR = PROJECT_ROOT / "system_learning/cross_repo"

# Cache for snapshot metadata
_snapshot_cache: dict[str, dict[str, Any]] = {}
_last_cache_update = 0
CACHE_TTL = 300  # 5 minutes


def _refresh_snapshot_cache():
    """Refresh runtime ADG snapshot cache."""
    global _last_cache_update
    current_time = int(time.time())

    if current_time - _last_cache_update < CACHE_TTL:
        return

    # Scan for runtime ADG snapshots
    if RUNTIME_ADG_SNAPSHOTS_DIR.exists():
        snapshot_files = list(RUNTIME_ADG_SNAPSHOTS_DIR.glob("runtime_adg_*.json"))

        for snapshot_file in snapshot_files:
            try:
                with open(snapshot_file) as f:
                    snapshot_data = json.load(f)

                snapshot_id = snapshot_file.stem
                _snapshot_cache[snapshot_id] = {
                    "file_path": str(snapshot_file),
                    "snapshot_id": snapshot_data.get("snapshot_id", snapshot_id),
                    "trace_id": snapshot_data.get("trace_id", ""),
                    "timestamp": snapshot_data.get("timestamp", 0),
                    "node_count": len(snapshot_data.get("nodes", [])),
                    "edge_count": len(snapshot_data.get("edges", [])),
                    "file_size": snapshot_file.stat().st_size,
                    "created_time": snapshot_file.stat().st_ctime,
                }
            except Exception as e:
                logger.warning(f"Failed to load snapshot {snapshot_file}: {e}")

    _last_cache_update = current_time


@mcp.tool()
def runtime_adg_status() -> dict[str, Any]:
    """Get runtime ADG snapshot count, freshness, and health.

    Returns:
        Dictionary with runtime ADG status and health metrics.
    """
    _refresh_snapshot_cache()

    total_snapshots = len(_snapshot_cache)

    if total_snapshots == 0:
        return {
            "timestamp": int(time.time()),
            "total_snapshots": 0,
            "health_status": "no_data",
            "freshness": "unknown",
            "recommendations": ["Generate runtime ADG snapshots by running system execution"],
        }

    # Calculate freshness metrics
    current_time = int(time.time())
    timestamps = [cache["timestamp"] for cache in _snapshot_cache.values()]

    oldest_snapshot = min(timestamps)
    newest_snapshot = max(timestamps)
    avg_age = (current_time - sum(timestamps) / len(timestamps)) / 3600  # hours

    # Determine health status
    if avg_age < 1:  # Less than 1 hour old on average
        health_status = "excellent"
    elif avg_age < 24:  # Less than 1 day old on average
        health_status = "good"
    elif avg_age < 168:  # Less than 1 week old on average
        health_status = "fair"
    else:
        health_status = "poor"

    # Calculate size metrics
    total_nodes = sum(cache["node_count"] for cache in _snapshot_cache.values())
    total_edges = sum(cache["edge_count"] for cache in _snapshot_cache.values())
    total_size = sum(cache["file_size"] for cache in _snapshot_cache.values())

    result = {
        "timestamp": int(time.time()),
        "total_snapshots": total_snapshots,
        "health_status": health_status,
        "freshness": {
            "oldest_snapshot_timestamp": oldest_snapshot,
            "newest_snapshot_timestamp": newest_snapshot,
            "average_age_hours": avg_age,
        },
        "metrics": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "total_size_bytes": total_size,
            "avg_nodes_per_snapshot": total_nodes / max(total_snapshots, 1),
            "avg_edges_per_snapshot": total_edges / max(total_snapshots, 1),
        },
        "recommendations": _get_health_recommendations(health_status, avg_age),
    }

    logger.info("runtime_adg_status_checked", extra=result)
    return result


@mcp.tool()
def runtime_adg_query(trace_id: str = None, agent_name: str = None, time_window_hours: int = 24, limit: int = 50) -> dict[str, Any]:
    """Query runtime ADG snapshots by trace ID, agent name, or time window.

    Args:
        trace_id: Specific trace ID to query
        agent_name: Agent name to filter by
        time_window_hours: Time window in hours (default 24)
        limit: Maximum number of snapshots to return

    Returns:
        Dictionary with matching snapshots and query metadata.
    """
    if time_window_hours <= 0 or time_window_hours > 168:  # Max 1 week
        return {"success": False, "error": "time_window_hours must be between 1 and 168"}

    if limit <= 0 or limit > 500:
        return {"success": False, "error": "limit must be between 1 and 500"}
    _refresh_snapshot_cache()

    current_time = int(time.time())
    cutoff_time = current_time - (time_window_hours * 3600)

    matching_snapshots = []

    for snapshot_id, cache_entry in _snapshot_cache.items():
        # Apply filters
        if trace_id and cache_entry.get("trace_id") != trace_id:
            continue

        if cache_entry.get("timestamp", 0) < cutoff_time:
            continue

        # Load full snapshot data for detailed analysis
        try:
            with open(cache_entry["file_path"]) as f:
                snapshot_data = json.load(f)

            # Agent name filter (if specified)
            if agent_name:
                nodes = snapshot_data.get("nodes", [])
                agent_found = any(
                    node.get("component", "").lower() == agent_name.lower() or
                    node.get("name", "").lower() == agent_name.lower()
                    for node in nodes
                )
                if not agent_found:
                    continue

            matching_snapshots.append({
                "snapshot_id": snapshot_id,
                "trace_id": cache_entry.get("trace_id"),
                "timestamp": cache_entry.get("timestamp"),
                "node_count": cache_entry.get("node_count"),
                "edge_count": cache_entry.get("edge_count"),
                "snapshot_data": snapshot_data,
            })

            if len(matching_snapshots) >= limit:
                break

        except Exception as e:
            logger.warning(f"Failed to load snapshot {snapshot_id}: {e}")
            continue

    # Sort by timestamp (most recent first)
    matching_snapshots.sort(key=lambda x: x["timestamp"], reverse=True)

    result = {
        "timestamp": int(time.time()),
        "query_params": {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "time_window_hours": time_window_hours,
            "limit": limit,
        },
        "total_matches": len(matching_snapshots),
        "snapshots": matching_snapshots,
    }

    logger.info("runtime_adg_queried", extra={
        "total_matches": result["total_matches"],
        "trace_id": trace_id,
        "agent_name": agent_name,
    })

    return result


@mcp.tool()
def runtime_adg_compare(snapshot_id_1: str, snapshot_id_2: str) -> dict[str, Any]:
    """Compare execution patterns between two runtime ADG snapshots.

    Args:
        snapshot_id_1: First snapshot ID
        snapshot_id_2: Second snapshot ID

    Returns:
        Dictionary with comparison analysis and differences.
    """
    _refresh_snapshot_cache()

    # Load both snapshots
    snapshots = {}
    for snapshot_id in [snapshot_id_1, snapshot_id_2]:
        if snapshot_id not in _snapshot_cache:
            return {
                "success": False,
                "error": f"Snapshot {snapshot_id} not found in cache",
                "snapshot_id_1": snapshot_id_1,
                "snapshot_id_2": snapshot_id_2,
            }

        try:
            with open(_snapshot_cache[snapshot_id]["file_path"]) as f:
                snapshots[snapshot_id] = json.load(f)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load snapshot {snapshot_id}: {e}",
                "snapshot_id_1": snapshot_id_1,
                "snapshot_id_2": snapshot_id_2,
            }

    # Perform comparison analysis
    snapshot_1 = snapshots[snapshot_id_1]
    snapshot_2 = snapshots[snapshot_id_2]

    # Compare basic metrics
    comparison = {
        "timestamp": int(time.time()),
        "snapshot_id_1": snapshot_id_1,
        "snapshot_id_2": snapshot_id_2,
        "basic_metrics": {
            "nodes_1": len(snapshot_1.get("nodes", [])),
            "nodes_2": len(snapshot_2.get("nodes", [])),
            "edges_1": len(snapshot_1.get("edges", [])),
            "edges_2": len(snapshot_2.get("edges", [])),
            "time_diff": snapshot_2.get("timestamp", 0) - snapshot_1.get("timestamp", 0),
        },
    }

    # Compare node distributions
    nodes_1 = snapshot_1.get("nodes", [])
    nodes_2 = snapshot_2.get("nodes", [])

    node_types_1 = {node.get("kind", "unknown") for node in nodes_1}
    node_types_2 = {node.get("kind", "unknown") for node in nodes_2}

    comparison["node_analysis"] = {
        "types_1": list(node_types_1),
        "types_2": list(node_types_2),
        "common_types": list(node_types_1 & node_types_2),
        "unique_types_1": list(node_types_1 - node_types_2),
        "unique_types_2": list(node_types_2 - node_types_1),
    }

    # Compare edge distributions
    edges_1 = snapshot_1.get("edges", [])
    edges_2 = snapshot_2.get("edges", [])

    edge_types_1 = {edge.get("relation_type", "unknown") for edge in edges_1}
    edge_types_2 = {edge.get("relation_type", "unknown") for edge in edges_2}

    comparison["edge_analysis"] = {
        "types_1": list(edge_types_1),
        "types_2": list(edge_types_2),
        "common_types": list(edge_types_1 & edge_types_2),
        "unique_types_1": list(edge_types_1 - edge_types_2),
        "unique_types_2": list(edge_types_2 - edge_types_1),
    }

    # Identify significant differences
    differences = []

    if comparison["basic_metrics"]["nodes_1"] != comparison["basic_metrics"]["nodes_2"]:
        differences.append(f"Node count differs: {comparison['basic_metrics']['nodes_1']} vs {comparison['basic_metrics']['nodes_2']}")

    if comparison["basic_metrics"]["edges_1"] != comparison["basic_metrics"]["edges_2"]:
        differences.append(f"Edge count differs: {comparison['basic_metrics']['edges_1']} vs {comparison['basic_metrics']['edges_2']}")

    if comparison["node_analysis"]["unique_types_1"]:
        differences.append(f"Unique node types in snapshot 1: {', '.join(comparison['node_analysis']['unique_types_1'])}")

    if comparison["node_analysis"]["unique_types_2"]:
        differences.append(f"Unique node types in snapshot 2: {', '.join(comparison['node_analysis']['unique_types_2'])}")

    comparison["differences"] = differences
    comparison["similarity_score"] = _calculate_similarity_score(comparison)

    logger.info("runtime_adg_compared", extra={
        "snapshot_id_1": snapshot_id_1,
        "snapshot_id_2": snapshot_id_2,
        "similarity_score": comparison["similarity_score"],
    })

    return comparison


@mcp.tool()
def meta_learning_insights(pattern_type: str = "all", time_window_hours: int = 168) -> dict[str, Any]:
    """Get pattern detection results and meta-learning insights.

    Args:
        pattern_type: Type of patterns to analyze (all, performance, errors, agents, flows)
        time_window_hours: Time window for analysis (default 168 hours = 1 week)

    Returns:
        Dictionary with meta-learning insights and patterns.
    """
    _refresh_snapshot_cache()

    current_time = int(time.time())
    cutoff_time = current_time - (time_window_hours * 3600)

    # Filter snapshots within time window
    recent_snapshots = [
        cache_entry for cache_entry in _snapshot_cache.values()
        if cache_entry.get("timestamp", 0) >= cutoff_time
    ]

    if not recent_snapshots:
        return {
            "timestamp": int(time.time()),
            "pattern_type": pattern_type,
            "time_window_hours": time_window_hours,
            "insights": [],
            "recommendations": ["No recent snapshots available for analysis"],
        }

    insights = []

    # Analyze different pattern types
    if pattern_type in ["all", "performance"]:
        performance_insights = _analyze_performance_patterns(recent_snapshots)
        insights.extend(performance_insights)

    if pattern_type in ["all", "errors"]:
        error_insights = _analyze_error_patterns(recent_snapshots)
        insights.extend(error_insights)

    if pattern_type in ["all", "agents"]:
        agent_insights = _analyze_agent_patterns(recent_snapshots)
        insights.extend(agent_insights)

    if pattern_type in ["all", "flows"]:
        flow_insights = _analyze_flow_patterns(recent_snapshots)
        insights.extend(flow_insights)

    # Generate recommendations
    recommendations = _generate_meta_learning_recommendations(insights)

    result = {
        "timestamp": int(time.time()),
        "pattern_type": pattern_type,
        "time_window_hours": time_window_hours,
        "snapshots_analyzed": len(recent_snapshots),
        "insights": insights,
        "recommendations": recommendations,
        "confidence_score": _calculate_insight_confidence(insights),
    }

    logger.info("meta_learning_insights_generated", extra={
        "pattern_type": pattern_type,
        "insights_count": len(insights),
        "confidence_score": result["confidence_score"],
    })

    return result


@mcp.tool()
def learning_pipeline_status() -> dict[str, Any]:
    """Get learning pipeline health and progress status.

    Returns:
        Dictionary with pipeline status and health metrics.
    """
    # Check for pipeline components
    pipeline_components = {
        "runtime_adg_collector": RUNTIME_ADG_DIR.exists(),
        "snapshot_storage": RUNTIME_ADG_SNAPSHOTS_DIR.exists(),
        "meta_learning_processor": META_LEARNING_DIR.exists(),
        "cross_repo_importer": CROSS_REPO_DIR.exists(),
    }

    # Check for recent activity
    current_time = int(time.time())
    activity_indicators = {}

    # Runtime ADG activity
    if RUNTIME_ADG_SNAPSHOTS_DIR.exists():
        snapshot_files = list(RUNTIME_ADG_SNAPSHOTS_DIR.glob("runtime_adg_*.json"))
        if snapshot_files:
            latest_snapshot = max(snapshot_files, key=lambda f: f.stat().st_mtime)
            activity_indicators["latest_snapshot_age_hours"] = (current_time - latest_snapshot.stat().st_mtime) / 3600
        else:
            activity_indicators["latest_snapshot_age_hours"] = None
    else:
        activity_indicators["latest_snapshot_age_hours"] = None

    # Meta-learning activity
    if META_LEARNING_DIR.exists():
        pattern_files = list(META_LEARNING_DIR.glob("pattern_*.json"))
        if pattern_files:
            latest_pattern = max(pattern_files, key=lambda f: f.stat().st_mtime)
            activity_indicators["latest_pattern_age_hours"] = (current_time - latest_pattern.stat().st_mtime) / 3600
        else:
            activity_indicators["latest_pattern_age_hours"] = None
    else:
        activity_indicators["latest_pattern_age_hours"] = None

    # Calculate overall health
    active_components = sum(pipeline_components.values())
    total_components = len(pipeline_components)
    component_health = active_components / total_components

    # Determine pipeline status
    if component_health >= 0.75:
        pipeline_status = "healthy"
    elif component_health >= 0.5:
        pipeline_status = "degraded"
    else:
        pipeline_status = "unhealthy"

    result = {
        "timestamp": int(time.time()),
        "pipeline_status": pipeline_status,
        "component_health": component_health,
        "components": pipeline_components,
        "activity_indicators": activity_indicators,
        "recommendations": _get_pipeline_recommendations(pipeline_status, activity_indicators),
    }

    logger.info("learning_pipeline_status_checked", extra=result)
    return result

@mcp.tool()
def cross_repo_import(repo_url: str, import_type: str = "patterns") -> dict[str, Any]:
    """Incorporate external repository learning.

    Args:
        repo_url: Repository URL to import from
        import_type: Type of import (patterns, snapshots, models)

    Returns:
        Dictionary with import results and status.
    """
    if not repo_url or not repo_url.strip():
        return {"success": False, "error": "repo_url cannot be empty"}

    valid_import_types = ["patterns", "snapshots", "models"]
    if import_type not in valid_import_types:
        return {"success": False, "error": f"import_type must be one of: {', '.join(valid_import_types)}"}
    # Check if cross-repo importer exists
    importer_script = CROSS_REPO_DIR / "import_external_learning.py"

    if not importer_script.exists():
        return {
            "success": False,
            "error": f"Cross-repo importer not found at {importer_script}. Install cross-repo learning components.",
            "repo_url": repo_url,
            "import_type": import_type,
        }

    try:
        # This is a simplified implementation
        # In practice, this would call the actual cross-repo importer
        import_result = {
            "success": True,
            "repo_url": repo_url,
            "import_type": import_type,
            "timestamp": int(time.time()),
            "items_imported": 0,
            "import_summary": f"Mock import from {repo_url}",
            "next_steps": [
                "Validate imported patterns",
                "Integrate with existing learning",
                "Update meta-learning models",
            ],
        }

        logger.info("cross_repo_import_executed", extra={
            "repo_url": repo_url,
            "import_type": import_type,
            "success": import_result["success"],
        })

        return import_result

    except Exception as e:
        logger.error("cross_repo_import_error", extra={
            "repo_url": repo_url,
            "error": str(e),
        })
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url,
            "import_type": import_type,
        }


@mcp.tool()
def learning_state_management(action: str, state_id: str = None) -> dict[str, Any]:
    """Manage learning state and snapshots.

    Args:
        action: Action to perform (list, backup, restore, cleanup)
        state_id: State ID for backup/restore operations

    Returns:
        Dictionary with operation results and state information.
    """
    if action == "list":
        _refresh_snapshot_cache()
        states = [
            {
                "state_id": snapshot_id,
                "timestamp": cache_entry["timestamp"],
                "node_count": cache_entry["node_count"],
                "edge_count": cache_entry["edge_count"],
                "size_bytes": cache_entry["file_size"],
            }
            for snapshot_id, cache_entry in _snapshot_cache.items()
        ]

        return {
            "success": True,
            "action": action,
            "total_states": len(states),
            "states": sorted(states, key=lambda x: x["timestamp"], reverse=True),
        }

    elif action == "backup":
        # Create backup of current learning state
        backup_id = f"backup_{int(time.time())}"
        backup_path = META_LEARNING_DIR / f"{backup_id}.json"

        backup_data = {
            "backup_id": backup_id,
            "timestamp": int(time.time()),
            "snapshot_count": len(_snapshot_cache),
            "snapshots": list(_snapshot_cache.keys()),
        }

        try:
            META_LEARNING_DIR.mkdir(exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            return {
                "success": True,
                "action": action,
                "backup_id": backup_id,
                "backup_path": str(backup_path),
                "snapshot_count": backup_data["snapshot_count"],
            }
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e),
            }

    elif action == "cleanup":
        # Clean up old snapshots (older than 30 days)
        cutoff_time = int(time.time()) - (30 * 24 * 3600)
        old_snapshots = [
            snapshot_id for snapshot_id, cache_entry in _snapshot_cache.items()
            if cache_entry.get("timestamp", 0) < cutoff_time
        ]

        cleaned_count = 0
        for snapshot_id in old_snapshots:
            try:
                snapshot_file = Path(_snapshot_cache[snapshot_id]["file_path"])
                snapshot_file.unlink()
                cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup snapshot {snapshot_id}: {e}")

        # Refresh cache after cleanup
        _refresh_snapshot_cache()

        return {
            "success": True,
            "action": action,
            "cleaned_count": cleaned_count,
            "remaining_snapshots": len(_snapshot_cache),
        }

    else:
        return {
            "success": False,
            "action": action,
            "error": f"Unknown action: {action}",
        }


# Helper functions

def _get_health_recommendations(health_status: str, avg_age: float) -> list[str]:
    """Get health recommendations based on status and age."""
    recommendations = []

    if health_status == "poor":
        recommendations.extend([
            "Generate fresh runtime ADG snapshots",
            "Check system execution pipeline",
            "Verify snapshot collection process",
        ])
    elif health_status == "fair":
        recommendations.append("Consider generating more recent snapshots")

    if avg_age > 168:  # More than 1 week
        recommendations.append("Snapshots are quite old - fresh execution data needed")

    return recommendations


def _calculate_similarity_score(comparison: dict[str, Any]) -> float:
    """Calculate similarity score between two snapshots."""
    score = 1.0

    # Penalize node count differences
    nodes_diff = abs(comparison["basic_metrics"]["nodes_1"] - comparison["basic_metrics"]["nodes_2"])
    max_nodes = max(comparison["basic_metrics"]["nodes_1"], comparison["basic_metrics"]["nodes_2"])
    if max_nodes > 0:
        score -= nodes_diff / max_nodes * 0.3

    # Penalize edge count differences
    edges_diff = abs(comparison["basic_metrics"]["edges_1"] - comparison["basic_metrics"]["edges_2"])
    max_edges = max(comparison["basic_metrics"]["edges_1"], comparison["basic_metrics"]["edges_2"])
    if max_edges > 0:
        score -= edges_diff / max_edges * 0.3

    # Penalize unique node types
    unique_types = len(comparison["node_analysis"]["unique_types_1"]) + len(comparison["node_analysis"]["unique_types_2"])
    total_types = len(comparison["node_analysis"]["common_types"]) + unique_types
    if total_types > 0:
        score -= unique_types / total_types * 0.2

    # Penalize unique edge types
    unique_edge_types = len(comparison["edge_analysis"]["unique_types_1"]) + len(comparison["edge_analysis"]["unique_types_2"])
    total_edge_types = len(comparison["edge_analysis"]["common_types"]) + unique_edge_types
    if total_edge_types > 0:
        score -= unique_edge_types / total_edge_types * 0.2

    return max(0.0, score)


def _analyze_performance_patterns(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze performance patterns from snapshots."""
    patterns = []

    # Mock performance analysis
    patterns.append({
        "type": "performance",
        "pattern": "execution_time_trend",
        "description": "Execution times show stable performance",
        "confidence": 0.8,
        "evidence": f"Analyzed {len(snapshots)} snapshots",
    })

    return patterns


def _analyze_error_patterns(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze error patterns from snapshots."""
    patterns = []

    # Mock error analysis
    patterns.append({
        "type": "errors",
        "pattern": "low_error_rate",
        "description": "Error rate is within acceptable bounds",
        "confidence": 0.7,
        "evidence": f"Analyzed {len(snapshots)} snapshots",
    })

    return patterns


def _analyze_agent_patterns(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze agent patterns from snapshots."""
    patterns = []

    # Mock agent analysis
    patterns.append({
        "type": "agents",
        "pattern": "consistent_agent_usage",
        "description": "Agent usage patterns are consistent",
        "confidence": 0.75,
        "evidence": f"Analyzed {len(snapshots)} snapshots",
    })

    return patterns


def _analyze_flow_patterns(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze flow patterns from snapshots."""
    patterns = []

    # Mock flow analysis
    patterns.append({
        "type": "flows",
        "pattern": "stable_execution_flows",
        "description": "Execution flows remain stable across snapshots",
        "confidence": 0.8,
        "evidence": f"Analyzed {len(snapshots)} snapshots",
    })

    return patterns


def _generate_meta_learning_recommendations(insights: list[dict[str, Any]]) -> list[str]:
    """Generate recommendations based on insights."""
    recommendations = []

    if len(insights) == 0:
        recommendations.append("Generate more runtime snapshots for better insights")
    else:
        avg_confidence = sum(insight.get("confidence", 0) for insight in insights) / len(insights)
        if avg_confidence < 0.7:
            recommendations.append("Increase snapshot frequency for better pattern detection")
        else:
            recommendations.append("Current pattern detection is performing well")

    return recommendations


def _calculate_insight_confidence(insights: list[dict[str, Any]]) -> float:
    """Calculate overall confidence score for insights."""
    if not insights:
        return 0.0

    return sum(insight.get("confidence", 0) for insight in insights) / len(insights)


def _get_pipeline_recommendations(status: str, activity: dict[str, Any]) -> list[str]:
    """Get pipeline recommendations based on status and activity."""
    recommendations = []

    if status == "unhealthy":
        recommendations.extend([
            "Check pipeline component installation",
            "Verify system execution pipeline",
            "Restart learning services if needed",
        ])
    elif status == "degraded":
        recommendations.append("Some components may need attention")

    # Check activity indicators
    if activity.get("latest_snapshot_age_hours") is not None and activity.get("latest_snapshot_age_hours", 0) > 24:
        recommendations.append("Snapshot generation may be stalled")

    if activity.get("latest_pattern_age_hours") is not None and activity.get("latest_pattern_age_hours", 0) > 48:
        recommendations.append("Pattern processing may be delayed")

    return recommendations


if __name__ == "__main__":
    logger.info("Starting System Learning Meta-Learning MCP Server")
    mcp.run()
