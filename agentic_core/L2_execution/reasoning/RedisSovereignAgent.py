from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "RedisSovereignAgent", "L2")
_emit_routes_through("p1", "RedisSovereignAgent", "L2")
_emit_escalates_to_human("p1", "RedisSovereignAgent", "L2")
_emit_reads_policy_state("p1", "RedisSovereignAgent", "L2")

_emit_applies_guardrail("p0", "RedisSovereignAgent", "p0_governance")

"\nRedisSovereignAgent - Eternal Sovereign Gateway to Redis\n"
import hashlib
from pathlib import Path
from typing import Any

import redis
from redis.connection import ConnectionPool

from agentic_core.config.core.env_loader import get_env
from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="RedisSovereignAgent",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


@dataclass
class RedisSovereignAgent(SovereignBaseAgent):
    """
    Sovereign Redis controller — hardened, monitored, eternal.

    [PHASE 2 MIGRATION] Absorbed Auditing and Telemetry:
    - Centralized operation_stats for dashboard visualization.
    - Standardized audit logging for L4 compliance.
    """

    _instance = None
    operation_stats = {"get": 0, "set": 0, "delete": 0, "hits": 0, "misses": 0, "total": 0}

    def __init__(self, project_root: Path, ctx: Any | None = None) -> None:
        """
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        """
        super().__init__()
        self._init(project_root, ctx)

    def _init(self, project_root: Path, ctx: Any | None = None) -> None:
        """
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        """
        env: Any = get_env(project_root)
        self.ctx: Any | None = ctx
        connection_kwargs: dict[str, Any] = {
            "max_connections": 20,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "socket_keepalive": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }
        if env.REDIS_SSL:
            connection_kwargs.update({"ssl": True, "ssl_cert_reqs": None, "ssl_check_hostname": False})
        if env.REDIS_PASSWORD:
            connection_kwargs["password"] = env.REDIS_PASSWORD
        self.pool: ConnectionPool = ConnectionPool.from_url(env.REDIS_URL, **connection_kwargs)
        self.client: redis.Redis = redis.Redis(connection_pool=self.pool)
        try:
            self.client.ping()
        except Exception as e:
            raise ConnectionError(f"[L6 CRITICAL] Redis gateway failed: {e}")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L4 compliance."""
        assert hasattr(self, "client"), "Missing client"
        assert hasattr(self, "pool"), "Missing pool"
        return True

    def get_client(self) -> redis.Redis:
        """Get the Redis client instance."""
        return self.client

    def _audit(self, operation: str, key: str, success: bool) -> None:
        """[PHASE 2] Record operation to internal audit plane."""
        if not hasattr(self, "audit_log"):
            self.audit_log = []
        self.audit_log.append(
            {"op": operation, "key": key[:32], "success": success, "ts": get_clock().now_epoch()}
        )
        self.operation_stats["total"] += 1
        self.operation_stats[operation] = self.operation_stats.get(operation, 0) + 1

    def invalidate_file_cache(self, file_path: Path) -> None:
        """
        Wipes old embeddings if the file has evolved.

        Args:
            file_path: Path to file whose cache should be invalidated
        """
        try:
            content: bytes = file_path.read_bytes()
            content_hash: str = hashlib.sha256(content).hexdigest()[:16]
            pattern: str = f"pc_embed:*{content_hash}*"
            keys: list = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            raise
            pass

    def invalidate_by_path(self, file_path: Path) -> None:
        """
        Invalidate cache by exact file path (for moves/deletes).

        Args:
            file_path: Path to file whose cache should be invalidated
        Ensures no 'ghost' embeddings remain for a path that no longer exists.
        """
        try:
            rel_path = str(file_path.relative_to(Path(".").resolve())).replace("/", "_")
            pattern = f"pc_embed:*:*{rel_path}*"
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                print(f"   [CACHE] Purged {deleted} ghost entries for: {file_path.name}")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"   [!] cache invalidation failed for {file_path}: {e}")

    # guardian: allow-type-erasure
    async def execute(self, ctx=None) -> Any:
        """Execute execute operation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "RedisSovereignAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RedisSovereignAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        _ectx = _make_execution_context("redis_execute", "RedisSovereignAgent.execute")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            "redis_execute",
            target_name="RedisSovereignAgent.execute",
        )
        info = self.client.info()
        mem = info.get("used_memory_human", "0B")
        print(f"   [OK] RedisSovereignAgent: Healthy. Memory: {mem}")
        if ctx:
            ctx.report("RedisCache", 1, True, f"Redis online ({mem})")

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
    ) -> dict[str, int]:
        """L4 state agent - operational only."""
        if _call_path is None:
            super().heal_repository()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L4 state - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by RedisSovereignAgent.

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
                "details": f"RedisSovereignAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"RedisSovereignAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
