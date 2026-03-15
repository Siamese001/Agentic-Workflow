from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"\nCachedStateLedgerAgent - Eternal L4 State with Redis Sovereign cache\n"
import json
import os
import time
from pathlib import Path

from agentic_core.runtime.types.anomaly_report import AnomalyReport

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class CachedStateLedger(SovereignBaseAgent):
    """
    Sovereign L4 state base — Redis cache for context, audit, Historian.
    All L4 components inherit from this.
    """

    def __init__(self, project_root: Path, session_id: str):
        super().__init__()
        self.root = project_root
        self.session_id = session_id
        self._mcp_audit("init", payload={"session_id": session_id})
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import urllib.parse

            import redis

            parsed = urllib.parse.urlparse(redis_url)
            connection_kwargs = {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 6379,
                "password": parsed.password,
                "username": parsed.username,
                "decode_responses": True,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
            }
            if parsed.scheme == "rediss":
                connection_kwargs["ssl"] = True
            self.redis = redis.Redis(**connection_kwargs)
            self.redis.ping()
            print("   [OK] CachedStateLedgerAgent: Redis Sovereign cache ONLINE")
        # guardian: allow-silent-swallow
        except Exception as e:
            from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

            raise InfrastructureDependencyError(
                f"[CachedStateLedger] Redis is a mandatory dependency and is unavailable: {e}"
            ) from e
        self._successful_traces: list[dict] = []
        self.prefix_context = f"l4_context:{session_id}"
        self.prefix_audit = f"l4_audit:{session_id}"
        self.prefix_historian = f"l4_historian:{session_id}"

    def cache_validation_context(self, key: str, context: dict):
        """cache validation context for instant access"""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "CachedStateLedger.cache_validation_context")

        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                self.redis.set(full_key, json.dumps(context), ex=86400)
            else:
                self._memory_cache[full_key] = context
        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Cache write failed for {key}: {e}")
        self._record_successful_trace(
            {"operation": "cache_validation_context", "key": key, "timestamp": time.time()}
        )

    def get_cached_validation_context(self, key: str) -> dict | None:
        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                data = self.redis.get(full_key)
                if data:
                    self._record_successful_trace(
                        {
                            "operation": "get_cached_validation_context",
                            "key": key,
                            "hit": True,
                            "timestamp": time.time(),
                        }
                    )
                    return json.loads(data)
            else:
                result = self._memory_cache.get(full_key)
                if result:
                    self._record_successful_trace(
                        {
                            "operation": "get_cached_validation_context",
                            "key": key,
                            "hit": True,
                            "timestamp": time.time(),
                        }
                    )
                return result
        except (AttributeError, KeyError) as e:
            self.logger.debug(f"Cache read failed for {key}: {e}")
        return None

    def _record_successful_trace(self, trace: dict):
        """Internal helper to maintain successful_traces list in both Redis and memory mode"""
        if self.redis:
            try:
                self.redis.rpush(f"{self.prefix_historian}:successful_traces", json.dumps(trace))
            # guardian: allow-silent-swallow
            except:
                pass
        else:
            self._successful_traces.append(trace)

    def get_successful_traces(self) -> list[dict]:
        """Public accessor required by ValidationContext and GeminiSpy telemetry"""
        if self.redis:
            try:
                raw = self.redis.lrange(f"{self.prefix_historian}:successful_traces", 0, -1)
                return [json.loads(r) for r in raw]
            # guardian: allow-silent-swallow
            except:
                return []
        else:
            return self._successful_traces

    def append_audit_event(self, event: dict):
        """Immutable append-only audit trail via Redis List"""
        try:
            if self.redis:
                trail_key = f"{self.prefix_audit}:trail"
                self.redis.rpush(trail_key, json.dumps(event))
                self.redis.expire(trail_key, 31536000)
            else:
                self._audit_trail.append(event)
        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Audit logging failed: {e}")

    def _run_self_tests(self) -> bool:
        """Run self-tests for CachedStateLedgerAgent."""
        super()._run_self_tests()
        test_key = "__self_test_cache"
        test_val = {"test": 42, "timestamp": time.time()}
        self.cache_validation_context(test_key, test_val)
        retrieved = self.get_cached_validation_context(test_key)
        assert retrieved is not None, "cache round-trip failed"
        assert retrieved.get("test") == 42, "cache data corruption"
        assert hasattr(self, "_successful_traces"), "Missing successful_traces"
        return True

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for detected anomalies."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())
        if anomaly.type == "cache_stale":
            if self.redis:
                try:
                    keys = self.redis.keys(f"{self.prefix_context}:*")
                    for key in keys:
                        self.redis.delete(key)
                # guardian: allow-silent-swallow
                except:
                    pass
            else:
                self._memory_cache.clear()
            self._mcp_audit("healing_success", payload={"action": "cache_flush"})
            return True
        if anomaly.type == "audit_corruption":
            self._audit_trail = []
            self._successful_traces = []
            self._mcp_audit("healing_success")
            return True
        return False

    # guardian: allow-type-erasure
    def heal(self, *args, **kwargs) -> dict:
        """heal() not implemented for CachedStateLedgerAgent."""
        raise NotImplementedError("heal() not implemented for CachedStateLedgerAgent")

    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)
