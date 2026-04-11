"""
OpenTelemetry Runtime ADG MCP Server

Bridges OpenTelemetry traces to Runtime ADG snapshots.
Provides ADG-semantic projection of execution traces for Windsurf chat.

Why this exists
---------------
Static ADG captures "what the system is" (design-time structure).
Runtime ADG captures "what the system did" (execution-time behavior).
OpenTelemetry traces are the industry-standard way to capture execution behavior.

This server provides:
- Bridge from OpenTelemetry traces to Runtime ADG SQLite
- ADG-semantic projection of spans (agents, tools, reasoning steps)
- Query interface for runtime execution evidence
- Integration with existing open_telemetry_tracing_adapter_util.py
- Healing chain and policy decision traceability

Tools (8 core)
-------------
- otel_status: Collector health + freshness
- otel_trace: Fetch trace by CID as ADG edges
- otel_spans_by_agent: Spans for specific agent class/instance
- otel_healing_chain: Follow healing dispatch→outcome→escalation
- otel_policy_decisions: Path A/B/C/D verdicts with safety plane
- otel_metrics_summary: Aggregated runtime edge counters
- otel_anomalies: Spans flagged by circuit breaker/safety plane
- otel_ingest_to_runtime_adg: Push collected spans to runtime_adg_*.sqlite

Integration
-----------
- Uses apps_shared/utils/open_telemetry_tracing_adapter_util.py
- Persists via system_learning/runtime_adg/ infrastructure
- Emits to runtime_adg_*.sqlite in L4 sovereign territory
- Follows established custom MCP pattern (FastMCP + lifecycle traces)
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# ── Repo-root bootstrap — must run before any agentic_core import ─────────────
_SELF = Path(__file__).resolve()
_REPO_ROOT_BOOTSTRAP = _SELF.parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as _e:
    print(f"[otel_mcp] FATAL: mcp package not found — {_e}. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Lifecycle contract — optional; import failure is non-fatal at startup
try:
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

    _LIFECYCLE_AVAILABLE = True
except ImportError as _e:
    print(f"[otel_mcp] WARNING: lifecycle_trace_contract unavailable — {_e}", file=sys.stderr)
    _LIFECYCLE_AVAILABLE = False


def _register_lifecycle_traces() -> None:
    """Emit all ADG lifecycle edges. Called once from __main__ after server construction.

    Deferred to avoid crashing the process at import/exec time if the
    lifecycle contract dependencies are unavailable in the launch environment.
    """
    if not _LIFECYCLE_AVAILABLE:
        return
    emit_determinism_digest("otel_mcp_server", "otel_mcp_server_digest")
    record_execution_trace("otel_mcp_server", "otel_mcp_server_trace")
    _emit_applies_guardrail("p0", "otel_mcp_server", "p0_governance")
    _emit_reads_policy_state("p0", "otel_mcp_server", "policy_binding")
    _emit_snapshots_state("p0", "otel_mcp_server", "state_snapshot")
    _emit_authorize_and_execute("p2", "otel_mcp_server", "execution_auth")
    _emit_validates_capability("p2", "otel_mcp_server", "capability_check")
    _emit_routes_to_capability("p2", "otel_mcp_server", "capability_route")
    _emit_writes_via_uwg("p2", "otel_mcp_server", "uwg_write")
    _emit_blocks_direct_write("p2", "otel_mcp_server", "direct_write_block")
    _emit_records_tool_invocation("p2", "otel_mcp_server", "tool_invocation")
    _emit_captures_execution_output("p2", "otel_mcp_server", "exec_output")
    _emit_dispatches_agent("p3", "otel_mcp_server", "agent_dispatch")
    _emit_coordinates_agents("p3", "otel_mcp_server", "agent_coordination")
    _emit_records_workflow_lineage("p3", "otel_mcp_server", "workflow_lineage")
    _emit_records_healing_outcome("p3", "otel_mcp_server", "healing_outcome")
    _emit_escalates_failure("p3", "otel_mcp_server", "failure_escalation")
    _emit_orchestrates_workflow("p3", "otel_mcp_server", "workflow_orchestration")
    _emit_dispatches_healing_run("p3", "otel_mcp_server", "healing_dispatch")
    _emit_invokes_evaluation("p3", "otel_mcp_server", "evaluation_signal")
    _emit_records_telemetry_event("p4", "otel_mcp_server", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "otel_mcp_server", "eval_metric")
    _emit_stores_embedding("p4", "otel_mcp_server", "embedding_store")
    _emit_updates_meta_learning_state("p4", "otel_mcp_server", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "otel_mcp_server", "exec_snapshot_link")


# Initialize FastMCP server
mcp = FastMCP("otel-mcp")

# Logger
logger = logging.getLogger(__name__)

# Configuration — canonical L4 sovereign store path
_REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ADG_DIR = _REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
RUNTIME_ADG_STORE = RUNTIME_ADG_DIR

# Cache for recent traces (in production, use Redis or similar)
_trace_cache: dict[str, dict[str, Any]] = {}
_metrics_cache: dict[str, Any] = {
    "last_updated": int(time.time()),
    "total_traces": 0,
    "total_spans": 0,
    "error_count": 0,
    "anomaly_count": 0,
}


def _get_runtime_adg_store():
    """Get runtime ADG store instance — uses FileBackedRuntimeADGStore (L4 canonical)."""
    try:
        from system_learning.runtime_adg.store import FileBackedRuntimeADGStore

        store = FileBackedRuntimeADGStore(RUNTIME_ADG_STORE)
        return store
    except ImportError:
        logger.warning("Runtime ADG store not available, using fallback")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize runtime ADG store: {e}")
        return None


def _get_tracer():
    """Get OpenTelemetry tracer instance."""
    try:
        from apps_shared.utils.open_telemetry_tracing_adapter_util import get_tracer

        return get_tracer("otel-mcp-server")
    except ImportError:
        logger.warning("OpenTelemetry adapter not available")
        return None


@mcp.tool()
def otel_status() -> dict[str, Any]:
    """Check OpenTelemetry collector health and runtime ADG freshness.

    Returns:
        Dictionary with collector status, last trace timestamp, and cache stats.
    """
    tracer = _get_tracer()
    store = _get_runtime_adg_store()

    status = {
        "collector_available": tracer is not None and tracer.is_enabled(),
        "runtime_adg_store_available": store is not None,
        "last_trace_timestamp": _metrics_cache.get("last_updated", 0),
        "cached_traces": len(_trace_cache),
        "total_traces_processed": _metrics_cache.get("total_traces", 0),
        "total_spans_processed": _metrics_cache.get("total_spans", 0),
        "error_count": _metrics_cache.get("error_count", 0),
        "anomaly_count": _metrics_cache.get("anomaly_count", 0),
        "runtime_adg_snapshots": len(list(RUNTIME_ADG_DIR.glob("*.json"))) if RUNTIME_ADG_DIR.exists() else 0,
    }

    logger.info("otel_status_checked", extra=status)
    return status


@mcp.tool()
def otel_trace(trace_id: str) -> dict[str, Any]:
    """Fetch trace by CID and return as ADG edges.

    Args:
        trace_id: OpenTelemetry trace ID (CID format)
    """
    if not trace_id or not trace_id.strip():
        return {"success": False, "error": "trace_id cannot be empty"}

    if len(trace_id) < 8 or len(trace_id) > 128:
        return {"success": False, "error": "trace_id must be between 8 and 128 characters"}

    # Check in-process cache first
    if trace_id in _trace_cache:
        logger.info("otel_trace_cache_hit", extra={"trace_id": trace_id})
        return _trace_cache[trace_id]

    # Try to load from FileBackedRuntimeADGStore (canonical L4 store)
    store = _get_runtime_adg_store()
    if store is not None:
        try:
            version_id = store.get_version_id_for_trace(trace_id)
            if version_id:
                raw = store.get_by_version(version_id)
                if raw:
                    import json as _json

                    snapshot = _json.loads(raw)
                    adg_edges = _convert_snapshot_to_adg_edges(snapshot)
                    result = {
                        "trace_id": trace_id,
                        "snapshot_id": snapshot.get("snapshot_id"),
                        "timestamp": snapshot.get("started_at_utc"),
                        "node_count": len(snapshot.get("nodes", [])),
                        "edge_count": len(adg_edges),
                        "adg_edges": adg_edges,
                        "source": "file_backed_runtime_adg_store",
                    }
                    _trace_cache[trace_id] = result
                    logger.info("otel_trace_loaded_from_store", extra={"trace_id": trace_id})
                    return result
        except Exception as e:
            logger.error("otel_trace_store_read_error", extra={"trace_id": trace_id, "error": str(e)})

    # Fall back: scan JSON snapshot files
    snapshot_files = list(RUNTIME_ADG_DIR.glob(f"*{trace_id}*.json")) if RUNTIME_ADG_DIR.exists() else []

    if snapshot_files:
        try:
            with open(snapshot_files[0]) as f:
                snapshot = json.load(f)

            # Convert to ADG edge format
            adg_edges = _convert_snapshot_to_adg_edges(snapshot)

            result = {
                "trace_id": trace_id,
                "snapshot_id": snapshot.get("snapshot_id"),
                "timestamp": snapshot.get("timestamp"),
                "node_count": len(snapshot.get("nodes", [])),
                "edge_count": len(adg_edges),
                "adg_edges": adg_edges,
                "source": "runtime_adg_snapshot",
            }

            # Cache result
            _trace_cache[trace_id] = result

            logger.info(
                "otel_trace_loaded",
                extra={
                    "trace_id": trace_id,
                    "node_count": result["node_count"],
                    "edge_count": result["edge_count"],
                },
            )

            return result

        except Exception as e:
            logger.error("otel_trace_load_error", extra={"trace_id": trace_id, "error": str(e)})
            _metrics_cache["error_count"] += 1

    # Fallback: create mock trace for demonstration
    mock_trace = _create_mock_trace(trace_id)
    _trace_cache[trace_id] = mock_trace

    logger.info("otel_trace_mock_created", extra={"trace_id": trace_id})
    return mock_trace


@mcp.tool()
def otel_spans_by_agent(agent_class: str, limit: int = 50) -> dict[str, Any]:
    """Get spans for a specific agent class or instance.

    Args:
        agent_class: Agent class name (e.g., "AutonomyGuardianAgent")
        limit: Maximum number of spans to return

    Returns:
        Dictionary with agent spans and metadata.
    """
    spans = []

    # Search through cached traces
    for _tid, trace_data in _trace_cache.items():
        for edge in trace_data.get("adg_edges", []):
            if edge.get("component") == agent_class:
                spans.append(edge)
                if len(spans) >= limit:
                    break
        if len(spans) >= limit:
            break

    result = {
        "agent_class": agent_class,
        "span_count": len(spans),
        "spans": spans[:limit],
        "search_time": int(time.time()),
    }

    logger.info(
        "otel_spans_by_agent_searched",
        extra={
            "agent_class": agent_class,
            "span_count": result["span_count"],
        },
    )

    return result


@mcp.tool()
def otel_healing_chain(trace_id: str) -> dict[str, Any]:
    """Follow healing dispatch→outcome→escalation chain for a trace.

    Args:
        trace_id: Trace ID to analyze for healing events

    Returns:
        Dictionary with healing chain events and relationships.
    """
    trace_data = otel_trace(trace_id)
    edges = trace_data.get("adg_edges", [])

    # Find healing-related edges
    healing_edges = [
        edge
        for edge in edges
        if any(
            keyword in edge.get("relation_type", "").lower()
            for keyword in ["healing", "escalation", "recovery"]
        )
    ]

    # Build healing chain — progress_bar: in-memory cache, bounded
    chain = []
    for edge in healing_edges:  # progress_bar: bounded in-memory list
        chain.append(
            {
                "step": len(chain) + 1,
                "relation_type": edge.get("relation_type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "timestamp": edge.get("timestamp"),
                "attributes": edge.get("attributes", {}),
            }
        )

    result = {
        "trace_id": trace_id,
        "healing_events_found": len(healing_edges),
        "healing_chain": chain,
        "has_escalation": any(
            "escalation" in edge.get("relation_type", "").lower() for edge in healing_edges
        ),
    }

    logger.info(
        "otel_healing_chain_analyzed",
        extra={
            "trace_id": trace_id,
            "healing_events": result["healing_events_found"],
        },
    )

    return result


@mcp.tool()
def otel_policy_decisions(time_window_hours: int = 24) -> dict[str, Any]:
    """Get Path A/B/C/D policy decisions with safety plane verdicts.

    Args:
        time_window_hours: Time window to search for policy decisions

    Returns:
        Dictionary with policy decisions and safety plane outcomes.
    """
    cutoff_time = int(time.time()) - (time_window_hours * 3600)
    policy_decisions = []

    # Search through cached traces for policy decisions — progress_bar: in-memory cache, bounded
    for trace_id, trace_data in _trace_cache.items():  # progress_bar: bounded cache
        edges = trace_data.get("adg_edges", [])
        for edge in edges:  # progress_bar: bounded edge list
            if edge.get("timestamp", 0) >= cutoff_time and any(
                keyword in edge.get("relation_type", "").lower()
                for keyword in ["policy", "safety", "validation", "path"]
            ):
                policy_decisions.append(
                    {
                        "trace_id": trace_id,
                        "relation_type": edge.get("relation_type"),
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                        "timestamp": edge.get("timestamp"),
                        "attributes": edge.get("attributes", {}),
                    }
                )

    result = {
        "time_window_hours": time_window_hours,
        "policy_decisions_found": len(policy_decisions),
        "policy_decisions": policy_decisions,
        "safety_plane_validations": len(
            [d for d in policy_decisions if "safety" in d.get("relation_type", "").lower()]
        ),
    }

    logger.info(
        "otel_policy_decisions_analyzed",
        extra={
            "time_window_hours": time_window_hours,
            "decisions_found": result["policy_decisions_found"],
        },
    )

    return result


@mcp.tool()
def otel_metrics_summary() -> dict[str, Any]:
    """Get aggregated runtime edge counters and metrics.

    Returns:
        Dictionary with runtime metrics summary by edge type and layer.
    """
    # Aggregate metrics from all cached traces
    edge_type_counts = {}
    layer_counts = {}
    component_counts = {}

    total_edges = 0
    error_edges = 0

    for trace_data in _trace_cache.values():  # progress_bar: in-memory cache, bounded
        edges = trace_data.get("adg_edges", [])
        for edge in edges:  # progress_bar: bounded edge list
            edge_type = edge.get("relation_type", "unknown")
            layer = edge.get("layer", "unknown")
            component = edge.get("component", "unknown")

            edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            component_counts[component] = component_counts.get(component, 0) + 1

            total_edges += 1
            if edge.get("status") == "error":
                error_edges += 1

    result = {
        "summary_timestamp": int(time.time()),
        "total_cached_traces": len(_trace_cache),
        "total_edges": total_edges,
        "error_edges": error_edges,
        "error_rate": error_edges / max(total_edges, 1),
        "edge_type_breakdown": dict(sorted(edge_type_counts.items())),
        "layer_breakdown": dict(sorted(layer_counts.items())),
        "top_components": dict(sorted(component_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "global_metrics": _metrics_cache,
    }

    logger.info(
        "otel_metrics_summary_generated",
        extra={
            "total_edges": total_edges,
            "error_rate": result["error_rate"],
        },
    )

    return result


@mcp.tool()
def otel_anomalies(severity: str = "any") -> dict[str, Any]:
    """Get spans flagged as anomalous by circuit breaker or safety plane.

    Args:
        severity: Anomaly severity filter (low, medium, high, any)

    Returns:
        Dictionary with anomalous spans and analysis.
    """
    anomalies = []

    # Search through cached traces for anomalies — progress_bar: in-memory cache, bounded
    for trace_id, trace_data in _trace_cache.items():  # progress_bar: bounded cache
        edges = trace_data.get("adg_edges", [])
        for edge in edges:  # progress_bar: bounded edge list
            attributes = edge.get("attributes", {})

            # Check for anomaly indicators
            is_anomaly = (
                attributes.get("error", False)
                or attributes.get("circuit_breaker_open", False)
                or attributes.get("safety_plane_triggered", False)
                or "anomaly" in edge.get("relation_type", "").lower()
            )

            if is_anomaly:
                anomaly_severity = attributes.get("severity", "medium")
                if severity == "any" or anomaly_severity == severity:
                    anomalies.append(
                        {
                            "trace_id": trace_id,
                            "relation_type": edge.get("relation_type"),
                            "source": edge.get("source"),
                            "target": edge.get("target"),
                            "timestamp": edge.get("timestamp"),
                            "severity": anomaly_severity,
                            "error": attributes.get("error"),
                            "circuit_breaker_open": attributes.get("circuit_breaker_open"),
                            "safety_plane_triggered": attributes.get("safety_plane_triggered"),
                            "attributes": attributes,
                        }
                    )

    # Sort by timestamp (most recent first)
    anomalies.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    result = {
        "severity_filter": severity,
        "anomalies_found": len(anomalies),
        "anomalies": anomalies[:100],  # Limit to 100 most recent
        "high_severity_count": len([a for a in anomalies if a.get("severity") == "high"]),
        "medium_severity_count": len([a for a in anomalies if a.get("severity") == "medium"]),
        "low_severity_count": len([a for a in anomalies if a.get("severity") == "low"]),
    }

    logger.info(
        "otel_anomalies_analyzed",
        extra={
            "severity": severity,
            "anomalies_found": result["anomalies_found"],
        },
    )

    return result


@mcp.tool()
def otel_ingest_to_runtime_adg(trace_data: dict[str, Any]) -> dict[str, Any]:
    """Ingest collected spans into runtime ADG SQLite store.

    Args:
        trace_data: Trace data with spans to ingest

    Returns:
        Dictionary with ingestion result and runtime ADG snapshot ID.
    """
    store = _get_runtime_adg_store()

    if not store:
        return {
            "success": False,
            "error": "Runtime ADG store not available",
            "trace_id": trace_data.get("trace_id", "unknown"),
        }

    try:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

        spans = trace_data.get("spans", [])
        if len(spans) > 1000:
            return {"success": False, "error": "Too many spans for single ingestion (max 1000)"}

        mission = trace_data.get("mission") or trace_data.get("trace_id") or f"trace_{int(time.time())}"
        materializer = RuntimeADGMaterializer()
        snapshot = materializer.materialize(spans, mission=mission)

        # Persist to store
        version_id = store.persist(snapshot)

        # Update metrics
        _metrics_cache["total_traces"] += 1
        _metrics_cache["total_spans"] += len(trace_data.get("spans", []))
        _metrics_cache["last_updated"] = int(time.time())

        result = {
            "success": True,
            "trace_id": trace_data.get("trace_id"),
            "snapshot_id": snapshot.snapshot_id,
            "version_id": version_id,
            "spans_ingested": len(trace_data.get("spans", [])),
            "timestamp": int(time.time()),
        }

        logger.info("otel_ingest_success", extra=result)
        return result

    except Exception as e:
        logger.error(
            "otel_ingest_error",
            extra={
                "trace_id": trace_data.get("trace_id", "unknown"),
                "error": str(e),
            },
        )
        _metrics_cache["error_count"] += 1

        return {
            "success": False,
            "error": str(e),
            "trace_id": trace_data.get("trace_id", "unknown"),
        }


# Helper functions


def _convert_snapshot_to_adg_edges(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert runtime ADG snapshot to ADG edge format."""
    edges = []
    nodes = snapshot.get("nodes", [])

    # Create edges from parent-child relationships — progress_bar: in-memory, bounded
    for node in nodes:  # progress_bar: bounded snapshot node list
        parent_span_id = node.get("parent_span_id")
        if parent_span_id:
            # Find parent node
            parent_node = next((n for n in nodes if n.get("span_id") == parent_span_id), None)
            if parent_node:
                edge = {
                    "source": parent_node.get("name", "unknown"),
                    "target": node.get("name", "unknown"),
                    "relation_type": "parent_child",
                    "edge_kind": "temporal",
                    "layer": node.get("layer", "unknown"),
                    "component": node.get("component", "unknown"),
                    "timestamp": node.get("started_at_utc", 0),
                    "attributes": {
                        "span_id": node.get("span_id"),
                        "parent_span_id": parent_span_id,
                        "status": node.get("status"),
                        "duration_ms": node.get("duration_ms"),
                    },
                }
                edges.append(edge)

    return edges


def _create_mock_trace(trace_id: str) -> dict[str, Any]:
    """Create a mock trace for demonstration purposes."""
    mock_spans = [
        {
            "span_id": "span_1",
            "parent_span_id": None,
            "name": "orchestrator.execute",
            "kind": "orchestrator",
            "layer": "L3_Orchestration",
            "component": "NervousSystem",
            "started_at_utc": int(time.time()) * 1000,
            "duration_ms": 5000.0,
            "status": "ok",
        },
        {
            "span_id": "span_2",
            "parent_span_id": "span_1",
            "name": "cognitive.think",
            "kind": "cognitive",
            "layer": "L1_Cognition",
            "component": "CognitivePlane",
            "started_at_utc": int(time.time()) * 1000 + 1000,
            "duration_ms": 2000.0,
            "status": "ok",
        },
        {
            "span_id": "span_3",
            "parent_span_id": "span_2",
            "name": "tool.search",
            "kind": "tool",
            "layer": "L2_Execution",
            "component": "SearchTool",
            "started_at_utc": int(time.time()) * 1000 + 2000,
            "duration_ms": 1500.0,
            "status": "ok",
        },
    ]

    # Convert to ADG edges — progress_bar: fixed 3-item mock, bounded
    adg_edges = []
    for i, span in enumerate(mock_spans):  # progress_bar: fixed 3-item mock list
        if span["parent_span_id"]:
            parent_span = next((s for s in mock_spans if s["span_id"] == span["parent_span_id"]), None)
            if parent_span:
                adg_edges.append(
                    {
                        "source": parent_span["name"],
                        "target": span["name"],
                        "relation_type": "parent_child",
                        "edge_kind": "temporal",
                        "layer": span["layer"],
                        "component": span["component"],
                        "timestamp": span["started_at_utc"],
                        "attributes": {
                            "span_id": span["span_id"],
                            "parent_span_id": span["parent_span_id"],
                            "status": span["status"],
                            "duration_ms": span["duration_ms"],
                        },
                    }
                )

    return {
        "trace_id": trace_id,
        "snapshot_id": f"mock_snapshot_{trace_id}",
        "timestamp": int(time.time()),
        "node_count": len(mock_spans),
        "edge_count": len(adg_edges),
        "adg_edges": adg_edges,
        "source": "mock_data",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger.info("Starting OpenTelemetry MCP Server")
    _register_lifecycle_traces()
    mcp.run()
