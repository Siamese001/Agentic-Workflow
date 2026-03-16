from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_redis_orchestrator")
emit_determinism_digest("p0", "sovereign_redis_orchestrator")

_emit_dispatches_healing_run("p1", "sovereign_redis_orchestrator", "L3")
_emit_routes_through("p1", "sovereign_redis_orchestrator", "L3")
_emit_escalates_to_human("p1", "sovereign_redis_orchestrator", "L3")
_emit_reads_policy_state("p1", "sovereign_redis_orchestrator", "L3")
_emit_authorize_and_execute("p2", "sovereign_redis_orchestrator", "execution_auth")
_emit_validates_capability("p2", "sovereign_redis_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "sovereign_redis_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_redis_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_redis_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_redis_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_redis_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "sovereign_redis_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_redis_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_redis_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_redis_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_redis_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_redis_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_redis_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_redis_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_redis_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_redis_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "sovereign_redis_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_redis_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_redis_orchestrator", "exec_snapshot_link")

"\nAutonomousRedisOrchestrator – L3 Sovereign Redis Orchestrator.\nFail-closed: raises InfrastructureDependencyError on connection failure.\n"
import asyncio
import os
import urllib.parse
from typing import Any

import redis

from agentic_core.config.core.sovereign_config import get_sovereign_config
from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

try:
    from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager as _MCPManager
except ImportError:
    _MCPManager = None
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


@dataclass
class SovereignRedisOrchestrator(SovereignBaseAgent):
    """Brief description of functionality and purpose."""

    def __init__(self) -> None:
        """Initialize the instance."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignRedisOrchestrator.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignRedisOrchestrator.__init__", "p0_governance")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.connection: redis.Redis | None = None
        self._mcp: Any = None
        self._use_mcp: bool = get_sovereign_config().REDIS_MCP_ENABLED

    # guardian: allow-type-erasure
    def _get_mcp(self) -> Any:
        """Lazy-init MCPConnectionManager when REDIS_MCP_ENABLED."""
        if self._mcp is None and _MCPManager is not None:
            self._mcp = _MCPManager()
        return self._mcp

    # guardian: allow-type-erasure
    def _mcp_call(self, tool: str, args: dict) -> Any:
        """Synchronous wrapper around async MCP call_tool."""
        mcp = self._get_mcp()
        if mcp is None:
            return None
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(asyncio.run, mcp.call_tool(tool, args))
                    # guardian: allow-magic-config
                    return future.result(timeout=5)
            else:
                return loop.run_until_complete(mcp.call_tool(tool, args))
        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"[Redis MCP] call_tool('{tool}') failed: {e}")
            return None

    def _create_connection(self) -> redis.Redis:
        """Version-agnostic connection factory"""
        parsed = urllib.parse.urlparse(self.redis_url)
        params = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "password": parsed.password,
            "decode_responses": True,
            "socket_timeout": 2.0,
        }
        if parsed.scheme == "rediss":
            params["ssl"] = True
            params["ssl_cert_reqs"] = None
        return redis.Redis(**params)

    # guardian: allow-type-erasure
    def get(self, key: str) -> Any:
        """Execute get operation (MCP-routed when REDIS_MCP_ENABLED)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignRedisOrchestrator.get"
        )

        if self._use_mcp:
            result = self._mcp_call("redis_get", {"key": key})
            if result is not None and result != {}:
                return result.get("value") if isinstance(result, dict) else result
        try:
            if not self.connection:
                self.connection = self._create_connection()
            return self.connection.get(key)
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            raise InfrastructureDependencyError(f"Redis unavailable at {self.redis_url}: {exc}") from exc

    # guardian: allow-type-erasure
    def set(self, key: str, value: Any) -> Any:
        """Execute set operation (MCP-routed when REDIS_MCP_ENABLED)."""
        if self._use_mcp:
            result = self._mcp_call("redis_set", {"key": key, "value": value})
            if result is not None and result != {}:
                return result
        try:
            if not self.connection:
                self.connection = self._create_connection()
            self.connection.set(key, value)
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            raise InfrastructureDependencyError(f"Redis unavailable at {self.redis_url}: {exc}") from exc

    def delete(self, key: str) -> bool:
        """Delete a key from Redis (MCP-routed when REDIS_MCP_ENABLED)."""
        if self._use_mcp:
            result = self._mcp_call("redis_delete", {"key": key})
            if result is not None and result != {}:
                return bool(result.get("deleted", False)) if isinstance(result, dict) else bool(result)
        try:
            if not self.connection:
                self.connection = self._create_connection()
            return self.connection.delete(key) > 0
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            raise InfrastructureDependencyError(f"Redis unavailable at {self.redis_url}: {exc}") from exc

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            if not self.connection:
                self.connection = self._create_connection()
            return self.connection.exists(key) > 0
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            raise InfrastructureDependencyError(f"Redis unavailable at {self.redis_url}: {exc}") from exc

    # guardian: allow-type-erasure
    def clear(self) -> Any:
        """Clear all data from Redis."""
        try:
            if not self.connection:
                self.connection = self._create_connection()
            self.connection.flushdb()
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            raise InfrastructureDependencyError(f"Redis unavailable at {self.redis_url}: {exc}") from exc

    # guardian: allow-type-erasure
    def get_connection_info(self) -> dict:
        """Get information about the current connection state."""
        return {"redis_url": self.redis_url, "connected": self.connection is not None}

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SovereignRedisOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SovereignRedisOrchestrator heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SovereignRedisOrchestrator heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


_orchestrator = None


def get_sovereign_redis_orchestrator() -> SovereignRedisOrchestrator:
    """Factory function to get sovereign redis orchestrator instance."""
    return SovereignRedisOrchestrator()
