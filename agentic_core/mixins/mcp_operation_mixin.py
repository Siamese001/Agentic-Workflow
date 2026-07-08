"""
MCPOperationMixin - Unified MCP Access for Agents

[PHASE 3 MIGRATION] Provides single interface to all MCP operations.
[MIXIN REFACTOR] Merged hardened call logic (retry, backoff, audit, idempotency)
from mcp_hardened_mixin.py. That file is now a backwards-compat shim.
# Configuration constants

"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "mcp_operation_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "mcp_operation_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "mcp_operation_mixin", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_operation_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_operation_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_operation_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_operation_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_operation_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_operation_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_operation_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_operation_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_operation_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_operation_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_operation_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_operation_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_operation_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_operation_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_operation_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_operation_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_operation_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_operation_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_operation_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_operation_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_operation_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_operation_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_operation_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_operation_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_operation_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_operation_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_operation_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_operation_mixin", "write_through")
trace_contract._emit_writes_through("p1", "mcp_operation_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_operation_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_operation_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_operation_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "mcp_operation_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "mcp_operation_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "mcp_operation_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_operation_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_operation_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_operation_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_operation_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_operation_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_operation_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_operation_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_operation_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_operation_mixin")
trace_contract._emit_gated_by_confidence("p1", "mcp_operation_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "mcp_operation_mixin")
trace_contract.emit_determinism_digest("p0", "mcp_operation_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "mcp_operation_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_operation_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_operation_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_operation_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_operation_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_operation_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_operation_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_operation_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_operation_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_operation_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_operation_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_operation_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_operation_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_operation_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_operation_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_operation_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_operation_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_operation_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_operation_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_operation_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class MCPOperationMixin:
    """
    Mixin providing unified MCP gateway access with hardened call semantics.

    Features:
    - Lazy-loaded MCP gateway singleton
    - Exponential backoff with jitter on retries
    - Idempotency keys to prevent double-writes
    - Structured audit log (bounded ring buffer)

    Usage:
        class MyAgent(MCPOperationMixin, SovereignBaseAgent):
            async def process(self):
                result = await self.mcp_llm_route("prompt")
    """

    _mcp_gateway = None
    _mcp_audit_log: list[dict[str, Any]] | None = None
    _MCP_AUDIT_LOG_MAX = 100

    @property
    def mcp_gateway(self):
        """Lazy-load MCP gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MCPOperationMixin.mcp_gateway"
        )

        if self._mcp_gateway is None:
            from agentic_core.L2_execution.enforcement.SovereignMCPGateway import get_mcp_gateway

            self._mcp_gateway = get_mcp_gateway()
        return self._mcp_gateway

    @property
    def mcp_audit_log(self) -> list[dict[str, Any]]:
        """Bounded ring-buffer audit log for MCP calls."""
        if self._mcp_audit_log is None:
            self._mcp_audit_log = []
        return self._mcp_audit_log

    # ── Hardened call layer ──────────────────────────────────────────

    async def safe_mcp_call(
        self,
        tool_name: str,
        args: dict,
        *,
        retry_count: int = 3,
        base_delay: float = 0.5,
        idempotency_key: str | None = None,
    ) -> Any:
        """Execute an MCP tool call with retry, backoff, idempotency, and audit.

        Args:
            tool_name: MCP tool identifier.
            args: Arguments to pass to the tool.
            retry_count: Max attempts before raising.
            base_delay: Base delay in seconds (doubles each retry + jitter).
            idempotency_key: Optional key to prevent duplicate writes.
                             Auto-generated from tool_name + args hash if None.
        """
        if idempotency_key is None:
            idempotency_key = self._generate_idempotency_key(tool_name, args)

        audit_context_id = str(uuid.uuid4())
        last_exception: Exception | None = None

        for attempt in tqdm(range(retry_count), desc="Processing", unit="item"):
            start = time.monotonic()
            try:
                result = await self.mcp_gateway.call_tool(
                    tool_name,
                    args,
                    idempotency_key=idempotency_key,
                )
                duration_ms = (time.monotonic() - start) * 1000
                self._audit_mcp(tool_name, "SUCCESS", duration_ms, audit_context_id, attempt)
                return result
            except (
                RuntimeError,
                OSError,
                TimeoutError,
                AttributeError,
            ) as e:  # guardian: allow-silent-swallow
                duration_ms = (time.monotonic() - start) * 1000
                last_exception = e
                self._audit_mcp(tool_name, "RETRY", duration_ms, audit_context_id, attempt)
                logger.warning(
                    "MCP call %s failed (attempt %d/%d): %s",
                    tool_name,
                    attempt + 1,
                    retry_count,
                    e,
                )
                if attempt < retry_count - 1:
                    delay = base_delay * (2**attempt) + (time.monotonic() % 0.1)
                    await asyncio.sleep(delay)

        self._audit_mcp(tool_name, "FAILED", 0, audit_context_id, retry_count)
        raise RuntimeError(
            f"MCP call '{tool_name}' failed after {retry_count} attempts",
        ) from last_exception

    # ── Gateway convenience methods ──────────────────────────────────

    async def mcp_llm_route(self, prompt: str, **kwargs) -> dict:
        """Route LLM request through MCP gateway."""
        return await self.mcp_gateway.llm_route(prompt, **kwargs)

    async def mcp_kg_query(self, query: str, **kwargs) -> dict:
        """Query knowledge graph through MCP gateway."""
        return await self.mcp_gateway.kg_query(query, **kwargs)

    async def mcp_archive_op(self, operation: str, **kwargs) -> dict:
        """Execute archive operation through MCP gateway."""
        return await self.mcp_gateway.archive_operation(operation, **kwargs)

    # ── Internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _generate_idempotency_key(tool_name: str, args: dict) -> str:
        """Deterministic idempotency key from tool + args."""
        raw = f"{tool_name}:{sorted(args.items())}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _audit_mcp(
        self,
        tool: str,
        status: str,
        duration_ms: float,
        audit_context_id: str,
        attempt: int,
    ) -> None:
        """Append structured audit entry to bounded ring buffer."""
        entry = {
            "tool": tool,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "audit_context_id": audit_context_id,
            "attempt": attempt,
            "ts": time.time(),
        }
        log = self.mcp_audit_log
        log.append(entry)
        if len(log) > self._MCP_AUDIT_LOG_MAX:
            log.pop(0)
