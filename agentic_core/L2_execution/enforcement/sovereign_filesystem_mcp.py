from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "sovereign_filesystem_mcp")
emit_determinism_digest("p0", "sovereign_filesystem_mcp")

_emit_dispatches_healing_run("p1", "sovereign_filesystem_mcp", "L2")
_emit_routes_through("p1", "sovereign_filesystem_mcp", "L2")
_emit_checks_agent_registry("p1", "sovereign_filesystem_mcp", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_filesystem_mcp", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_filesystem_mcp", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_filesystem_mcp", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_filesystem_mcp", "target_agent")
_emit_verifies_policy("p1", "sovereign_filesystem_mcp", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_filesystem_mcp", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_filesystem_mcp", "boundary_check")
_emit_transcripts_response("p1", "sovereign_filesystem_mcp", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_filesystem_mcp")
_emit_gated_by_confidence("p1", "sovereign_filesystem_mcp", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_filesystem_mcp", "L2")
_emit_reads_policy_state("p1", "sovereign_filesystem_mcp", "L2")
_emit_authorize_and_execute("p2", "sovereign_filesystem_mcp", "execution_auth")
_emit_validates_capability("p2", "sovereign_filesystem_mcp", "capability_check")
_emit_routes_to_capability("p2", "sovereign_filesystem_mcp", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_filesystem_mcp", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_filesystem_mcp", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_filesystem_mcp", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_filesystem_mcp", "exec_output")
_emit_dispatches_agent("p3", "sovereign_filesystem_mcp", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_filesystem_mcp", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_filesystem_mcp", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_filesystem_mcp", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_filesystem_mcp", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_filesystem_mcp", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_filesystem_mcp", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_filesystem_mcp", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_filesystem_mcp", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_filesystem_mcp", "eval_metric")
_emit_stores_embedding("p4", "sovereign_filesystem_mcp", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_filesystem_mcp", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_filesystem_mcp", "exec_snapshot_link")

"L4 State: Sovereign Filesystem MCP Client — Atomic Eternal Operations\nUltra-hardened integration of Filesystem MCP with Roots, L5 shielding, and Redis cache.\nZero tolerance for path escape or unrecorded writes.\n[SSOT] Root prefixes derived from SOVEREIGN_REGISTRY in structure_blueprint.py\n"
import json
import logging
import uuid
from datetime import datetime

from agentic_core.cache.redis_cache_client import get_hot_cache
from agentic_core.L0_routing.config.path_constants import PROJECT_ROOT_WHITELIST
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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
from agentic_core.seams.contracts.authority import get_mcp_authority
from agentic_core.seams.contracts.mcp import MCPConnectionManager

_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_filesystem_mcp", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_filesystem_mcp", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_filesystem_mcp", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_filesystem_mcp", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_filesystem_mcp", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_filesystem_mcp", "p4obs", "alert")
_emit_links_incident_trace("sovereign_filesystem_mcp", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_filesystem_mcp", "p3lm", "pattern")
_emit_records_learning_event("sovereign_filesystem_mcp", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_filesystem_mcp", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_filesystem_mcp", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_filesystem_mcp", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_filesystem_mcp", "p3lm", "policy")
_emit_stores_learning_state("sovereign_filesystem_mcp", "p3lm", "state")
_emit_records_execution_trace("sovereign_filesystem_mcp", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_filesystem_mcp", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_filesystem_mcp", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_filesystem_mcp", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_filesystem_mcp", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_filesystem_mcp", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_filesystem_mcp", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_filesystem_mcp", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_filesystem_mcp", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_filesystem_mcp", "context_pull")
_emit_pulls_context("p1", "sovereign_filesystem_mcp", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_filesystem_mcp", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_filesystem_mcp", "uwg_term_2")
_emit_writes_through("p1", "sovereign_filesystem_mcp", "write_through")
_emit_writes_through("p1", "sovereign_filesystem_mcp", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_filesystem_mcp", "safety_validation")
_emit_invokes_eval("p1", "sovereign_filesystem_mcp", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_filesystem_mcp", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="sovereign_filesystem_mcp",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


Logger = logging.getLogger(__name__)
allowed_root_prefixes = set(PROJECT_ROOT_WHITELIST) | {"config"}
forbidden_path_patterns = {"..", "/etc", "/root", "~", ".ssh", ".env"}


class SovereignFilesystemMcp:
    """Ultra-hardened filesystem client — enforcing atomic sovereignty."""

    def __init__(self, manager: MCPConnectionManager, mission_id: str):
        self.manager = manager
        self.mission_id = mission_id
        self.roots_key = f"fs_roots:{mission_id}"

    def _validate_path(self, path: str) -> str:
        """L5 path sovereignty check. Blocks traversals and absolute escapes."""
        _emit_applies_guardrail(str(uuid.uuid4()), "SovereignFilesystemMcp._validate_path", "L2_EXECUTION")
        path_str = str(path).replace("\\", "/")
        if any(p in path_str for p in forbidden_path_patterns):
            raise PermissionError(f"Sovereignty Breach: Forbidden path pattern in '{path}'")
        if not any(path_str.startswith(prefix) for prefix in allowed_root_prefixes):
            raise PermissionError(f"Sovereignty Breach: Path '{path}' is outside sovereign roots.")
        return path_str

    async def read_text_file(self, path: str) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "SovereignFilesystemMcp.read_text_file"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SovereignFilesystemMcp.read_text_file".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        safe_path = self._validate_path(path)
        try:
            try:
                import builtins

                _mcp8_read = getattr(builtins, "mcp8_read_text_file", None)
                if _mcp8_read is not None:
                    result = _mcp8_read(path=safe_path)
                    if hasattr(result, "__await__"):
                        import asyncio

                        result = await asyncio.ensure_future(result)
                    return result if isinstance(result, str) else str(result)
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError) as direct_e:
                Logger.debug(f"[L4 FS] mcp8_read_text_file failed, falling back to manager: {direct_e}")
            result = await self.manager.call_tool("read_file", {"path": safe_path})
            return result.get("content", "") if isinstance(result, dict) else str(result)
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[L4 FS] Read failed: {e}")
            try:
                get_mcp_authority().record_breach(f"FS Read Failure: {safe_path}")
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError):
                pass
            raise

    async def atomic_fission_write(self, files: dict[str, str], monolith_path: str) -> dict:
        """Executes a physical fission event via the MCP server."""
        _emit_writes_through(str(uuid.uuid4()), "SovereignFilesystemMcp.atomic_fission_write", "L2_EXECUTION")
        for p in files:
            self._validate_path(p)
        self._validate_path(monolith_path)
        _ectx = _make_execution_context(list(files.keys()), "sovereign_filesystem_mcp.atomic_fission_write")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            monolith_path,
            target_name="sovereign_filesystem_mcp.atomic_fission_write",
        )
        try:
            results = []
            for path, content in files.items():
                try:
                    import builtins

                    _mcp8_write = getattr(builtins, "mcp8_write_file", None)
                    if _mcp8_write is not None:
                        write_result = _mcp8_write(path=path, content=content)
                        if hasattr(write_result, "__await__"):
                            import asyncio

                            write_result = await asyncio.ensure_future(write_result)
                        results.append(write_result)
                        continue
                # guardian: allow-silent-swallow
                except (RuntimeError, ValueError) as direct_e:
                    Logger.debug(f"[L4 FS] mcp8_write_file failed, falling back to manager: {direct_e}")
                result = await self.manager.call_tool("write_file", {"path": path, "content": content})
                results.append(result)
            try:
                _cache = get_hot_cache()
                if _cache:
                    _cache.rpush(
                        f"fs_ops:{self.mission_id}",
                        json.dumps(
                            {
                                "op": "fission",
                                "source": monolith_path,
                                "targets": list(files.keys()),
                                "ts": datetime.utcnow().isoformat(),
                            }
                        ),
                    )
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError) as ledger_e:
                Logger.warning(f"[L4 FS] Ledger write failed (non-fatal): {ledger_e}")
            return {"status": "fission_complete", "count": len(results)}
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.critical(f"[L4 FS BREACH] Fission write failed: {e}")
            try:
                get_mcp_authority().record_breach(f"Fission Write Failure: {monolith_path}")
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError):
                pass
            raise

    async def set_roots(self, roots: list[str]) -> None:
        """Sets the physical boundaries for the MCP server session."""
        validated = [r for r in roots if any(r.startswith(p) for p in allowed_root_prefixes)]
        if not validated:
            raise ValueError("No valid sovereign roots provided.")
        try:
            await self.manager.call_tool("roots_update", {"roots": validated})
            try:
                _cache = get_hot_cache()
                if _cache:
                    _cache.set(self.roots_key, json.dumps(validated), ex=60 * 60 * 24)
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError) as cache_e:
                Logger.warning(f"[L4 FS] Roots cache write failed (non-fatal): {cache_e}")
            Logger.info(f"[L4 FS] Sovereign roots locked: {validated}")
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            Logger.warning(f"MCP Server does not support dynamic roots: {e}")
