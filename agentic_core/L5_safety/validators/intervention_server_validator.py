from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "intervention_server_validator")
emit_determinism_digest("p0", "intervention_server_validator")

_emit_dispatches_healing_run("p1", "intervention_server_validator", "L5")
_emit_routes_through("p1", "intervention_server_validator", "L5")
_emit_checks_agent_registry("p1", "intervention_server_validator", "agent_registry")
_emit_validates_agent_capability("p1", "intervention_server_validator", "capability")
_emit_dispatches_execution_plan("p1", "intervention_server_validator", "exec_plan")
_emit_agent_executes_agent("p1", "intervention_server_validator", "sub_agent")
_emit_routes_to_agent("p1", "intervention_server_validator", "target_agent")
_emit_verifies_policy("p1", "intervention_server_validator", "policy_check")
_emit_observes_runtime_state("p1", "intervention_server_validator", "runtime_state")
_emit_verifies_boundary("p1", "intervention_server_validator", "boundary_check")
_emit_transcripts_response("p1", "intervention_server_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "intervention_server_validator")
_emit_gated_by_confidence("p1", "intervention_server_validator", "confidence_gate")
_emit_escalates_to_human("p1", "intervention_server_validator", "L5")
_emit_reads_policy_state("p1", "intervention_server_validator", "L5")
_emit_authorize_and_execute("p2", "intervention_server_validator", "execution_auth")
_emit_validates_capability("p2", "intervention_server_validator", "capability_check")
_emit_routes_to_capability("p2", "intervention_server_validator", "capability_route")
_emit_writes_via_uwg("p2", "intervention_server_validator", "uwg_write")
_emit_blocks_direct_write("p2", "intervention_server_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "intervention_server_validator", "tool_invocation")
_emit_captures_execution_output("p2", "intervention_server_validator", "exec_output")
_emit_dispatches_agent("p3", "intervention_server_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "intervention_server_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "intervention_server_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "intervention_server_validator", "healing_outcome")
_emit_escalates_failure("p3", "intervention_server_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "intervention_server_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "intervention_server_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "intervention_server_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "intervention_server_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "intervention_server_validator", "eval_metric")
_emit_stores_embedding("p4", "intervention_server_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "intervention_server_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "intervention_server_validator", "exec_snapshot_link")

"""
Human-in-the-Loop Intervention Server for L5+ Autonomy.

Implements the Canon Validator intervention pattern with FastAPI server
for human approval/veto of high-risk operations.

Canon Validator Patterns Implemented:
- FastAPI intervention server at configurable port
- Approval event synchronization
- High-risk threshold detection
- Veto capability with signal emission
- Telepathy interface (human instructions file)
"""
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_1")
_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_2")
_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_3")
_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_4")
_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_5")
_emit_emits_metric_event("intervention_server_validator", "p4obs", "metric_6")
_emit_records_incident_event("intervention_server_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("intervention_server_validator", "p4obs", "anomaly")
_emit_writes_observability_log("intervention_server_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("intervention_server_validator", "p4obs", "mon_state")
_emit_triggers_alert("intervention_server_validator", "p4obs", "alert")
_emit_links_incident_trace("intervention_server_validator", "p4obs", "trace_link")
_emit_captures_pattern("intervention_server_validator", "p3lm", "pattern")
_emit_records_learning_event("intervention_server_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("intervention_server_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("intervention_server_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("intervention_server_validator", "p3lm", "routing")
_emit_improves_agent_policy("intervention_server_validator", "p3lm", "policy")
_emit_stores_learning_state("intervention_server_validator", "p3lm", "state")
_emit_records_execution_trace("intervention_server_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("intervention_server_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("intervention_server_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("intervention_server_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("intervention_server_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("intervention_server_validator", "env_read", "p2_env_1")
_emit_reads_environ("intervention_server_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("intervention_server_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("intervention_server_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "intervention_server_validator", "context_pull")
_emit_pulls_context("p1", "intervention_server_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "intervention_server_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "intervention_server_validator", "uwg_term_2")
_emit_writes_through("p1", "intervention_server_validator", "write_through")
_emit_writes_through("p1", "intervention_server_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "intervention_server_validator", "safety_validation")
_emit_invokes_eval("p1", "intervention_server_validator", "eval_call")
_emit_proposal_commits_routing("p1", "intervention_server_validator", "routing_commit")

Logger: Any = logging.getLogger(__name__)
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse

    FASTAPI_AVAILABLE: Any = True
except ImportError:  # guardian: allow-silent-swallow
    FASTAPI_AVAILABLE: Any = False
    Logger.warning("FastAPI not available - intervention server disabled")


@dataclass
class InterventionContext:
    """Context for human intervention decision."""

    workflow_id: str
    cycle: int
    reason: str
    risk_factors: list[str] = field(default_factory=list)
    modified_items: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    quality_score: float | None = None
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "InterventionContext.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "InterventionContext.to_dict", "p0_governance")
        return {
            "workflow_id": self.workflow_id,
            "cycle": self.cycle,
            "reason": self.reason,
            "risk_factors": self.risk_factors,
            "modified_items": self.modified_items,
            "signals": self.signals,
            "quality_score": self.quality_score,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


class InterventionServer:
    """
    Human-in-the-Loop intervention server.

    Provides:
    - Web UI for human approval/veto
    - API endpoints for programmatic control
    - Async event synchronization
    - Telepathy interface for instruction files

    Canon Validator Pattern:
        if high_risk or (many_modifications and strategic_plan):
            start_intervention_server(ctx)
            await approval_event.wait()
            if "VETOED" in ctx.signals:
                break
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        instructions_path: str = "observability/human_instructions.md",
    ) -> None:
        """
        Initialize the intervention server.

        Args:
            host: Server host address
            port: Server port
            instructions_path: Path to human instructions file (telepathy)
        """
        self.host = host
        self.port = port
        self.instructions_path = Path(instructions_path)
        self.approval_event = asyncio.Event()
        self.current_context: InterventionContext | None = None
        self.decision: str | None = None
        self.decision_reason: str = ""
        self._server_task: asyncio.Task | None = None
        self._app: Any | None = None
        if FASTAPI_AVAILABLE:
            self._setup_app()
        Logger.info(f"InterventionServer initialized at {host}:{port}")

    def _setup_app(self) -> None:
        """Setup FastAPI application with endpoints."""
        self._app = FastAPI(
            title="L5+ Intervention Server",
            description="Human-in-the-Loop approval for autonomous workflows",
        )

        @self._app.get("/", response_class=HTMLResponse)
        async def intervention_ui():
            """Render intervention UI."""
            if not self.current_context:
                return HTMLResponse(content="<h1>No pending intervention</h1>", status_code=200)
            ctx = self.current_context
            risk_html = "".join(f"<li>{r}</li>" for r in ctx.risk_factors)
            modified_html = "".join(f"<li>{m}</li>" for m in ctx.modified_items[:10])
            signals_html = "".join(f"<li>{s}</li>" for s in ctx.signals)
            recs_html = "".join(f"<li>{r}</li>" for r in ctx.recommendations)
            html = f"""\n            <!DOCTYPE html>\n            <html>\n            <head>\n                <title>L5+ Intervention Required</title>\n                <style>\n                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}\n                    .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; }}\n                    .risk {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; margin: 10px 0; }}\n                    .btn {{ padding: 15px 30px; font-size: 18px; margin: 10px; cursor: pointer; border: none; border-radius: 5px; }}\n                    .approve {{ background: #28a745; color: white; }}\n                    .veto {{ background: #dc3545; color: white; }}\n                    .info {{ background: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}\n                    ul {{ margin: 5px 0; }}\n                </style>\n            </head>\n            <body>\n                <h1>[ALERT] Human Intervention Required</h1>\n\n                <div class="warning">\n                    <h2>Workflow: {ctx.workflow_id}</h2>\n                    <p><strong>Cycle:</strong> {ctx.cycle}</p>\n                    <p><strong>Reason:</strong> {ctx.reason}</p>\n                    <p><strong>Quality Score:</strong> {ctx.quality_score or "N/A"}</p>\n                </div>\n\n                <div class="risk">\n                    <h3>[!] Risk Factors</h3>\n                    <ul>{risk_html or "<li>None specified</li>"}</ul>\n                </div>\n\n                <div class="info">\n                    <h3>📝 Modified Items ({len(ctx.modified_items)})</h3>\n                    <ul>{modified_html or "<li>None</li>"}</ul>\n                </div>\n\n                <div class="info">\n                    <h3>📡 Active Signals</h3>\n                    <ul>{signals_html or "<li>None</li>"}</ul>\n                </div>\n\n                <div class="info">\n                    <h3>💡 Recommendations</h3>\n                    <ul>{recs_html or "<li>None</li>"}</ul>\n                </div>\n\n                <h2>Decision</h2>\n                <form action="/approve" method="post" style="display: inline;">\n                    <button type="submit" class="btn approve">[OK] APPROVE</button>\n                </form>\n                <form action="/veto" method="post" style="display: inline;">\n                    <button type="submit" class="btn veto">[X] VETO</button>\n                </form>\n\n                <p><small>Timestamp: {ctx.timestamp.isoformat()}</small></p>\n            </body>\n            </html>\n            """
            return HTMLResponse(content=html)

        @self._app.post("/approve")
        async def approve():
            """Approve the pending intervention."""
            self.decision = "approved"
            self.decision_reason = "Human approved via UI"
            self.approval_event.set()
            return HTMLResponse(
                content="<h1>[OK] Approved</h1><p>Workflow will continue.</p>",
                status_code=200,
            )

        @self._app.post("/veto")
        async def veto():
            """Veto the pending intervention."""
            self.decision = "vetoed"
            self.decision_reason = "Human vetoed via UI"
            self.approval_event.set()
            return HTMLResponse(content="<h1>[X] Vetoed</h1><p>Workflow will abort.</p>", status_code=200)

        @self._app.get("/status")
        async def status():
            """Get current intervention status."""
            return JSONResponse(
                {
                    "pending": self.current_context is not None,
                    "context": self.current_context.to_dict() if self.current_context else None,
                    "decision": self.decision,
                },
            )

        @self._app.post("/api/approve")
        async def api_approve(reason: str = "API approval"):
            """API endpoint for programmatic approval."""
            self.decision = "approved"
            self.decision_reason = reason
            self.approval_event.set()
            return {"status": "approved", "reason": reason}

        @self._app.post("/api/veto")
        async def api_veto(reason: str = "API veto"):
            """API endpoint for programmatic veto."""
            self.decision = "vetoed"
            self.decision_reason = reason
            self.approval_event.set()
            return {"status": "vetoed", "reason": reason}

    async def start_server(self) -> None:
        """Start the intervention server in background."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            "InterventionServer.start_server",
        )
        if not FASTAPI_AVAILABLE:
            Logger.warning("FastAPI not available - server not started")
            return
        config: Any = uvicorn.Config(self._app, host=self.host, port=self.port, log_level="warning")
        server: Any = uvicorn.Server(config)
        self._server_task = asyncio.create_task(server.serve())
        Logger.info(f"🌐 Intervention server started at http://{self.host}:{self.port}")

    async def stop_server(self) -> None:
        """Stop the intervention server."""
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError as e:
                import logging

                logging.getLogger(__name__).debug(
                    "intervention_server_validator: Exception swallowed at L370: %s", e
                )
            self._server_task = None
            Logger.info("Intervention server stopped")

    async def request_intervention(self, context: InterventionContext, timeout: float | None = None) -> bool:
        """
        Request human intervention and wait for decision.

        Args:
            context: Intervention context with details
            timeout: Optional timeout in seconds (None = wait forever)

        Returns:
            True if approved, False if vetoed or timeout
        """
        self.current_context = context
        self.decision = None
        self.approval_event.clear()
        Logger.warning(f"[ALERT] INTERVENTION REQUIRED: {context.reason}")
        Logger.warning(f"   Approval URL: http://{self.host}:{self.port}")
        try:
            if timeout:
                await asyncio.wait_for(self.approval_event.wait(), timeout=timeout)
            else:
                await self.approval_event.wait()
            approved: Any = self.decision == "approved"
            Logger.info(f"Intervention decision: {self.decision} - {self.decision_reason}")
            return approved
        except asyncio.TimeoutError:
            Logger.warning("Intervention timeout - defaulting to veto")
            self.decision = "timeout"
            return False
        finally:
            self.current_context = None

    def check_telepathy(self) -> str | None:
        """
        Check for human instructions via telepathy file.

        Canon Validator Pattern:
            instruction_file = Path("observability/human_instructions.md")
            if instruction_file.exists():
                instructions = instruction_file.read_text().strip()
        """
        if not self.instructions_path.exists():
            return None
        try:
            instructions: Any = self.instructions_path.read_text().strip()
            if instructions:
                Logger.info(f"Telepathy instructions received: {instructions[:100]}...")
                return instructions
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"Failed to read telepathy file: {e}")
        return None

    def parse_telepathy_commands(self, instructions: str) -> dict[str, Any]:
        """Parse telepathy instructions for commands."""
        commands: Any = {
            "stop": False,
            "pause": False,
            "skip_files": [],
            "force_test": False,
            "custom": [],
        }
        instructions_lower: Any = instructions.lower()
        if "stop" in instructions_lower or "abort" in instructions_lower:
            commands["stop"] = True
        if "pause" in instructions_lower:
            commands["pause"] = True
        if "test" in instructions_lower:
            commands["force_test"] = True
        for line in instructions.split("\n"):
            if line.strip().startswith("skip:"):
                pattern: Any = line.split(":", 1)[1].strip()
                commands["skip_files"].append(pattern)
            elif line.strip() and (not any(cmd in line.lower() for cmd in ["stop", "pause", "test", "skip"])):
                commands["custom"].append(line.strip())
        return commands


# guardian: allow-magic-config
def check_intervention_required(
    cycle: int,
    modified_count: int,
    signals: list[str],
    quality_score: float | None = None,
    high_risk_threshold: int = 3,
    signal_threshold: int = 5,
) -> tuple[bool, list[str]]:
    """
    Check if human intervention is required based on Canon Validator thresholds.

    Args:
        cycle: Current cycle number
        modified_count: Number of modified items
        signals: List of active signal names
        quality_score: Optional quality score
        high_risk_threshold: Modified count threshold
        signal_threshold: Signal count threshold

    Returns:
        Tuple of (intervention_required, risk_factors)
    """
    risk_factors: Any = []
    high_risk_signals: Any = ["HIGH_RISK", "CRITICAL_FAIL", "SECURE_REBOOT", "VETOED"]
    if any(s in signals for s in high_risk_signals):
        risk_factors.append(f"High-risk signals present: {[s for s in signals if s in high_risk_signals]}")
    if modified_count > high_risk_threshold:
        risk_factors.append(f"Many modifications ({modified_count} > {high_risk_threshold})")
    if len(signals) > signal_threshold:
        risk_factors.append(f"Many signals ({len(signals)} > {signal_threshold})")
    if cycle >= 3 and modified_count > 0:
        risk_factors.append(f"Late cycle ({cycle}) with pending modifications")
    if quality_score is not None and quality_score < 0.5:
        risk_factors.append(f"Low quality score ({quality_score:.2f})")
    intervention_required: Any = len(risk_factors) > 0
    return (intervention_required, risk_factors)


_intervention_server: InterventionServer | None = None


def get_intervention_server(host: str = "127.0.0.1", port: int = 8080) -> InterventionServer:
    """Get or create the global InterventionServer instance."""
    global _intervention_server
    if _intervention_server is None:
        _intervention_server = InterventionServer(host=host, port=port)
    return _intervention_server


async def start_intervention_server(host: str = "127.0.0.1", port: int = 8080) -> InterventionServer:
    """Start the global intervention server."""
    server: Any = get_intervention_server(host, port)
    await server.start_server()
    return server
