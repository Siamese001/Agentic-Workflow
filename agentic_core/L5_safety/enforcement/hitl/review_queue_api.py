"""Human Review Queue API — REST endpoints for HITL checkpoint management.

Provides HTTP API for human reviewers to interact with pending HITL checkpoints:
- GET /api/v1/hitl/checkpoints — List pending checkpoints
- GET /api/v1/hitl/checkpoints/<id> — Get checkpoint details
- POST /api/v1/hitl/checkpoints/<id>/decision — Submit human decision
- GET /api/v1/hitl/metrics — Get HITL system metrics
- POST /api/v1/hitl/batch/decide — Batch decision processing

Reference: docs/reference/HITL/HITL Implementations v2.md
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify, request

from agentic_core.L5_safety.enforcement.hitl.hitl_escalation_activator import (
    EscalationRequest,
    get_hitl_escalation_activator,
)
from agentic_core.L5_safety.enforcement.hitl.hitl_graph import (
    HITLDecisionType,
    HITLGraph,
    HITLRuntimeRecorder,
)
from tqdm import tqdm

# Lazy import to avoid L5->L_TOOLS gravity violation
_runtime_graph = None


def _get_runtime_graph():
    global _runtime_graph
    if _runtime_graph is None:
        from agentic_core.adg.runtime.event_graph import RuntimeGraph

        _runtime_graph = RuntimeGraph()
    return _runtime_graph


logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage (replace with persistent storage in production)
_hitl_graph = HITLGraph()

# Runtime graph is lazy-initialized on first use
_rt_graph = None


def _ensure_rt_graph():
    global _rt_graph
    if _rt_graph is None:
        _rt_graph = _get_runtime_graph()
    return _rt_graph


def _serialize_checkpoint(cp: Any) -> dict[str, Any]:
    """Serialize checkpoint to JSON-compatible dict."""
    return {
        "checkpoint_id": cp.checkpoint_id,
        "agent_id": cp.agent_id,
        "run_id": cp.run_id,
        "violation_id": cp.violation_id,
        "confidence": cp.confidence,
        "context": cp.context,
        "created_at": cp.created_at,
        "resolved": cp.resolved,
    }


def _serialize_decision(d: Any) -> dict[str, Any]:
    """Serialize decision to JSON-compatible dict."""
    return {
        "checkpoint_id": d.checkpoint_id,
        "decision": d.decision.value,
        "reviewer": d.reviewer,
        "rationale": d.rationale,
        "decided_at": d.decided_at,
        "override_value": d.override_value,
    }


@app.route("/api/v1/hitl/health", methods=["GET"])
def health_check() -> tuple[Any, int]:
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "hitl-review-queue",
            "version": "1.0.0",
        }
    ), 200


@app.route("/api/v1/hitl/checkpoints", methods=["GET"])
def list_checkpoints() -> tuple[Any, int]:
    """List all HITL checkpoints with optional filtering.

    Query parameters:
    - status: "pending" or "resolved"
    - agent_id: Filter by agent
    - limit: Maximum results (default 50)
    """
    status_filter = request.args.get("status")
    agent_filter = request.args.get("agent_id")
    limit = request.args.get("limit", 50, type=int)

    checkpoints = _hitl_graph.checkpoints

    if status_filter == "pending":
        checkpoints = [cp for cp in checkpoints if not cp.resolved]
    elif status_filter == "resolved":
        checkpoints = [cp for cp in checkpoints if cp.resolved]

    if agent_filter:
        checkpoints = [cp for cp in checkpoints if cp.agent_id == agent_filter]

    checkpoints = checkpoints[-limit:]

    return jsonify(
        {
            "checkpoints": [_serialize_checkpoint(cp) for cp in checkpoints],
            "total": len(_hitl_graph.checkpoints),
            "pending": _hitl_graph.pending_count,
            "resolved": _hitl_graph.resolved_count,
        }
    ), 200


@app.route("/api/v1/hitl/checkpoints/<checkpoint_id>", methods=["GET"])
def get_checkpoint(checkpoint_id: str) -> tuple[Any, int]:
    """Get details of a specific checkpoint."""
    checkpoint = _hitl_graph.checkpoint_by_id(checkpoint_id)

    if checkpoint is None:
        return jsonify({"error": "Checkpoint not found"}), 404

    decisions = _hitl_graph.decisions_for(checkpoint_id)

    return jsonify(
        {
            "checkpoint": _serialize_checkpoint(checkpoint),
            "decisions": [_serialize_decision(d) for d in decisions],
        }
    ), 200


@app.route("/api/v1/hitl/checkpoints/<checkpoint_id>/decision", methods=["POST"])
def submit_decision(checkpoint_id: str) -> tuple[Any, int]:
    """Submit a human decision for a checkpoint.

    Request body:
    {
        "decision": "approve" | "reject" | "override" | "defer",
        "reviewer": "human:name",
        "rationale": "Reason for decision",
        "override_value": any (optional, for override decisions)
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing request body"}), 400

    decision_str = data.get("decision")
    reviewer = data.get("reviewer")
    rationale = data.get("rationale", "")
    override_value = data.get("override_value")

    if not decision_str or not reviewer:
        return jsonify({"error": "Missing required fields: decision, reviewer"}), 400

    try:
        decision_type = HITLDecisionType(decision_str)
    except ValueError:
        return jsonify(
            {
                "error": f"Invalid decision: {decision_str}. Must be one of: approve, reject, override, defer",
            }
        ), 400

    checkpoint = _hitl_graph.checkpoint_by_id(checkpoint_id)
    if checkpoint is None:
        return jsonify({"error": "Checkpoint not found"}), 404

    if checkpoint.resolved:
        return jsonify({"error": "Checkpoint already resolved"}), 409

    # Record the decision
    recorder = HITLRuntimeRecorder(_ensure_rt_graph(), _hitl_graph, agent_id=checkpoint.agent_id)
    recorder.decide(
        checkpoint_id=checkpoint_id,
        decision=decision_str,
        reviewer=reviewer,
        rationale=rationale,
        override_value=override_value,
    )

    logger.info(
        "HITL decision submitted: checkpoint=%s decision=%s reviewer=%s",
        checkpoint_id,
        decision_str,
        reviewer,
    )

    return jsonify(
        {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "decision": decision_str,
            "reviewer": reviewer,
        }
    ), 200


@app.route("/api/v1/hitl/metrics", methods=["GET"])
def get_metrics() -> tuple[Any, int]:
    """Get HITL system metrics."""
    dist = _hitl_graph.decision_distribution()

    return jsonify(
        {
            "total_checkpoints": len(_hitl_graph.checkpoints),
            "pending": _hitl_graph.pending_count,
            "resolved": _hitl_graph.resolved_count,
            "decision_distribution": dist,
        }
    ), 200


@app.route("/api/v1/hitl/batch/decide", methods=["POST"])
def batch_decide() -> tuple[Any, int]:
    """Process batch decisions.

    Request body:
    {
        "decisions": [
            {
                "checkpoint_id": "cp-xxx",
                "decision": "approve",
                "reviewer": "human:name",
                "rationale": "Reason"
            },
            ...
        ]
    }
    """
    data = request.get_json()

    if not data or "decisions" not in data:
        return jsonify({"error": "Missing decisions array"}), 400

    decisions = data["decisions"]
    results = []

    for dec_data in tqdm(decisions, desc="Processing", unit="item"):
        checkpoint_id = dec_data.get("checkpoint_id")
        decision_str = dec_data.get("decision")
        reviewer = dec_data.get("reviewer")
        rationale = dec_data.get("rationale", "")
        override_value = dec_data.get("override_value")

        if not checkpoint_id or not decision_str or not reviewer:
            results.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "success": False,
                    "error": "Missing required fields",
                }
            )
            continue

        checkpoint = _hitl_graph.checkpoint_by_id(checkpoint_id)
        if checkpoint is None:
            results.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "success": False,
                    "error": "Checkpoint not found",
                }
            )
            continue

        if checkpoint.resolved:
            results.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "success": False,
                    "error": "Checkpoint already resolved",
                }
            )
            continue

        try:
            decision_type = HITLDecisionType(decision_str)
        except ValueError:
            results.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "success": False,
                    "error": f"Invalid decision: {decision_str}",
                }
            )
            continue

        # Record the decision
        recorder = HITLRuntimeRecorder(_ensure_rt_graph(), _hitl_graph, agent_id=checkpoint.agent_id)
        recorder.decide(
            checkpoint_id=checkpoint_id,
            decision=decision_str,
            reviewer=reviewer,
            rationale=rationale,
            override_value=override_value,
        )

        results.append(
            {
                "checkpoint_id": checkpoint_id,
                "success": True,
                "decision": decision_str,
            }
        )

    return jsonify(
        {
            "processed": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
        }
    ), 200


@app.route("/api/v1/hitl/escalations", methods=["GET"])
def list_escalations() -> tuple[Any, int]:
    """List current escalations from the escalation activator."""
    activator = get_hitl_escalation_activator()

    pending = activator.pending()
    resolved = activator.resolved()

    def serialize_escalation(req: EscalationRequest) -> dict[str, Any]:
        return {
            "trace_id": req.trace_id,
            "agent": req.agent,
            "module": req.module,
            "trigger_reason": req.trigger_reason,
            "priority": req.priority.value,
            "proposed_action": req.proposed_action,
            "policy_hash": req.policy_hash,
            "resolved": req.resolved,
            "resolution": req.resolution,
        }

    return jsonify(
        {
            "pending": [serialize_escalation(r) for r in pending],
            "resolved": [serialize_escalation(r) for r in resolved],
            "pending_count": len(pending),
            "resolved_count": len(resolved),
        }
    ), 200


def create_app() -> Flask:
    """Application factory for testing."""
    return app


def run_server(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
    """Run the HITL review queue API server."""
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting HITL Review Queue API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()
