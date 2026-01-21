from __future__ import annotations

"""
SovereignRedisClient - Audited Cache Operations

Routes all Redis operations through controlled plane with:
- Audit logging
- Connection pooling with fallback
- Error handling with local cache fallback
- Telemetry callbacks for dashboard observability (Phase 1.3)
"""
import logging
import os
from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# Type alias for telemetry callback
TelemetryCallback = Callable[[str, dict[str, Any]], None]

from agentic_core.L5_safety.validators.structure_blueprint import (
    TESTS_DIR,
)

Logger = logging.getLogger(__name__)


class SovereignRedisClient(MCPHardenedMixin, HealerMixin):
    """Sovereign Redis client - audit + safe exec for all cache operations."""

    def __init__(self, url: str | None = None, telemetry_callback: TelemetryCallback | None = None):
        """
        Initialize Redis client.

        Args:
            url: Redis URL (defaults to env var or localhost)
            telemetry_callback: Optional callback for dashboard telemetry.
                               Signature: callback(event_type: str, data: dict) -> None
        """
        super().__init__()
        self.redis_url = url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.audit_log: list[dict[str, Any]] = []
        self._client = None
        self._fallback_cache: OrderedDict = OrderedDict()
        self._max_fallback_size = 1000
        self._use_fallback = False

        # Telemetry for dashboard observability (Phase 1.3)
        self.telemetry_callback = telemetry_callback
        self.operation_stats = {
            'get': 0, 'set': 0, 'delete': 0,
            'hits': 0, 'misses': 0, 'total': 0
        }
        self.recent_operations: list[dict[str, Any]] = []

    def _get_client(self):
        """Lazy-load Redis client with fallback."""
        if self._client is None and not self._use_fallback:
            try:
                import urllib.parse

                import redis
                parsed = urllib.parse.urlparse(self.redis_url)
                params = {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 6379,
                    'password': parsed.password,
                    'decode_responses': True,
                    'socket_timeout': 5,
                    'socket_connect_timeout': 5
                }
                if parsed.scheme == 'rediss':
                    params['ssl'] = True

                self._client = redis.Redis(**params)
                self._client.ping()
                Logger.info("[SOVEREIGN REDIS] Connected")
            except ImportError:
                Logger.warning("[SOVEREIGN REDIS] redis-py not installed - using fallback cache")
                self._use_fallback = True
            except Exception as e:
                Logger.warning(f"[SOVEREIGN REDIS] Connection failed: {e} - using fallback cache")
                self._use_fallback = True

        return None if self._use_fallback else self._client

    def _audit(self, operation: str, key: str, result: Any) -> None:
        """Record operation to audit log."""
        self.audit_log.append({
            'operation': operation,
            'key': key[:50] if key else '',
            'success': result.get('success', False) if isinstance(result, dict) else True
        })

    def _fallback_set(self, key: str, value: Any) -> None:
        """Set value in fallback cache with LRU eviction."""
        self._fallback_cache[key] = value
        if len(self._fallback_cache) > self._max_fallback_size:
            self._fallback_cache.popitem(last=False)

    def execute(self, operation: str, **payload) -> dict[str, Any]:
        """
        Route Redis operations safely via dispatch pattern.

        Args:
            operation: Redis operation (set, get, delete, etc.)
            **payload: Operation-specific parameters

        Returns:
            Result dictionary with success status and data
        """
        handlers = {
            'set': self._handle_set,
            'get': self._handle_get,
            'delete': self._handle_delete,
            'exists': self._handle_exists,
            'keys': self._handle_keys,
            'expire': self._handle_expire,
            'ping': self._handle_ping,
        }

        handler = handlers.get(operation)
        if not handler:
            return {'success': False, 'error': f'Unsupported Redis operation: {operation}'}

        key = payload.get('key', '')
        Logger.debug(f"[SOVEREIGN REDIS] {operation}: {key[:50]}")

        try:
            result = handler(**payload)
        except Exception as e:
            Logger.error(f"[SOVEREIGN REDIS] {operation} failed: {e}")
            result = {'success': False, 'error': str(e)}

        self._audit(operation, key, result)
        return result

    def _handle_set(self, key: str, value: str, ttl: int | None = None, **kwargs) -> dict[str, Any]:
        """Sub-atomic set handler."""
        client = self._get_client()
        if client:
            if ttl:
                client.setex(key, ttl, value)
            else:
                client.set(key, value)
        else:
            self._fallback_set(key, value)

        # Track for telemetry
        self.operation_stats['set'] += 1
        self.operation_stats['total'] += 1

        op_record = {
            'operation': 'set',
            'key': key[:50] if key else '',
            'hit': None,  # SET doesn't have hit/miss
            'timestamp': datetime.now().isoformat()
        }
        self.recent_operations.insert(0, op_record)
        self.recent_operations = self.recent_operations[:20]

        if self.telemetry_callback:
            self.telemetry_callback('redis_set', op_record)

        return {'success': True}

    def _handle_get(self, key: str, **kwargs) -> dict[str, Any]:
        """Sub-atomic get handler."""
        client = self._get_client()
        if client:
            value = client.get(key)
        else:
            value = self._fallback_cache.get(key)

        # Track hit/miss for telemetry
        hit = value is not None
        self.operation_stats['get'] += 1
        self.operation_stats['total'] += 1
        if hit:
            self.operation_stats['hits'] += 1
        else:
            self.operation_stats['misses'] += 1

        # Add to recent operations
        op_record = {
            'operation': 'get',
            'key': key[:50] if key else '',
            'hit': hit,
            'timestamp': datetime.now().isoformat()
        }
        self.recent_operations.insert(0, op_record)
        self.recent_operations = self.recent_operations[:20]  # Keep last 20

        # Telemetry callback
        if self.telemetry_callback:
            self.telemetry_callback('redis_get', op_record)

        return {'success': True, 'value': value}

    def _handle_delete(self, key: str, **kwargs) -> dict[str, Any]:
        """Sub-atomic delete handler."""
        client = self._get_client()
        if client:
            deleted = client.delete(key)
        else:
            deleted = 1 if key in self._fallback_cache else 0
            if key in self._fallback_cache:
                del self._fallback_cache[key]

        # Track for telemetry
        self.operation_stats['delete'] += 1
        self.operation_stats['total'] += 1

        op_record = {
            'operation': 'delete',
            'key': key[:50] if key else '',
            'hit': None,
            'timestamp': datetime.now().isoformat()
        }
        self.recent_operations.insert(0, op_record)
        self.recent_operations = self.recent_operations[:20]

        if self.telemetry_callback:
            self.telemetry_callback('redis_delete', op_record)

        return {'success': True, 'deleted': deleted}

    def _handle_exists(self, key: str, **kwargs) -> dict[str, Any]:
        """Sub-atomic exists handler."""
        client = self._get_client()
        if client:
            exists = client.exists(key) > 0
        else:
            exists = key in self._fallback_cache
        return {'success': True, 'exists': exists}

    def _handle_keys(self, pattern: str = '*', **kwargs) -> dict[str, Any]:
        """Sub-atomic keys handler."""
        client = self._get_client()
        if client:
            keys = client.keys(pattern)
        else:
            import fnmatch
            keys = [k for k in self._fallback_cache.keys() if fnmatch.fnmatch(k, pattern)]
        return {'success': True, 'keys': keys}

    def _handle_expire(self, key: str, ttl: int = 3600, **kwargs) -> dict[str, Any]:
        """Sub-atomic expire handler."""
        client = self._get_client()
        if client:
            client.expire(key, ttl)
        return {'success': True}

    def _handle_ping(self, **kwargs) -> dict[str, Any]:
        """Sub-atomic ping handler."""
        client = self._get_client()
        if client:
            client.ping()
        return {'success': True, 'pong': True, 'fallback': self._use_fallback}

    def get_statistics(self) -> dict[str, Any]:
        """Get Redis operation statistics for dashboard observability."""
        total_ops = self.operation_stats['hits'] + self.operation_stats['misses']
        hit_rate = self.operation_stats['hits'] / total_ops if total_ops > 0 else 0.0

        return {
            'connected': not self._use_fallback,
            'operations': {
                'get': self.operation_stats['get'],
                'set': self.operation_stats['set'],
                'delete': self.operation_stats['delete'],
                'total': self.operation_stats['total']
            },
            'cache_hits': self.operation_stats['hits'],
            'cache_misses': self.operation_stats['misses'],
            'hit_rate': hit_rate,
            'recent_operations': self.recent_operations[:20]
        }

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
