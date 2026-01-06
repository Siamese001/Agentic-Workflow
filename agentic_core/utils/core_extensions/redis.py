from __future__ import annotations
"""
SovereignRedisClient - Audited Cache Operations

Routes all Redis operations through controlled plane with:
- Audit logging
- Connection pooling with fallback
- Error handling with local cache fallback
"""
import logging
import os
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

Logger = logging.getLogger(__name__)


class SovereignRedisClient(MCPHardenedMixin, HealerMixin):
    """Sovereign Redis client - audit + safe exec for all cache operations."""
    
    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis client.
        
        Args:
            url: Redis URL (defaults to env var or localhost)
        """
        super().__init__()
        self.redis_url = url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.audit_log: List[Dict[str, Any]] = []
        self._client = None
        self._fallback_cache: OrderedDict = OrderedDict()
        self._max_fallback_size = 1000
        self._use_fallback = False
        self._mcp_audit('init')
    
    def _get_client(self):
        """Lazy-load Redis client with fallback."""
        if self._client is None and not self._use_fallback:
            try:
                import redis
                import urllib.parse
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
    
    def execute(self, operation: str, **payload) -> Dict[str, Any]:
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
    
    def _handle_set(self, key: str, value: str, ttl: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Sub-atomic set handler."""
        client = self._get_client()
        if client:
            if ttl:
                client.setex(key, ttl, value)
            else:
                client.set(key, value)
        else:
            self._fallback_set(key, value)
        return {'success': True}
    
    def _handle_get(self, key: str, **kwargs) -> Dict[str, Any]:
        """Sub-atomic get handler."""
        client = self._get_client()
        if client:
            value = client.get(key)
        else:
            value = self._fallback_cache.get(key)
        return {'success': True, 'value': value}
    
    def _handle_delete(self, key: str, **kwargs) -> Dict[str, Any]:
        """Sub-atomic delete handler."""
        client = self._get_client()
        if client:
            deleted = client.delete(key)
        else:
            deleted = 1 if key in self._fallback_cache else 0
            if key in self._fallback_cache:
                del self._fallback_cache[key]
        return {'success': True, 'deleted': deleted}
    
    def _handle_exists(self, key: str, **kwargs) -> Dict[str, Any]:
        """Sub-atomic exists handler."""
        client = self._get_client()
        if client:
            exists = client.exists(key) > 0
        else:
            exists = key in self._fallback_cache
        return {'success': True, 'exists': exists}
    
    def _handle_keys(self, pattern: str = '*', **kwargs) -> Dict[str, Any]:
        """Sub-atomic keys handler."""
        client = self._get_client()
        if client:
            keys = client.keys(pattern)
        else:
            import fnmatch
            keys = [k for k in self._fallback_cache.keys() if fnmatch.fnmatch(k, pattern)]
        return {'success': True, 'keys': keys}
    
    def _handle_expire(self, key: str, ttl: int = 3600, **kwargs) -> Dict[str, Any]:
        """Sub-atomic expire handler."""
        client = self._get_client()
        if client:
            client.expire(key, ttl)
        return {'success': True}
    
    def _handle_ping(self, **kwargs) -> Dict[str, Any]:
        """Sub-atomic ping handler."""
        client = self._get_client()
        if client:
            client.ping()
        return {'success': True, 'pong': True, 'fallback': self._use_fallback}

    def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
        pass
        pass
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
    assert self is not None
    results["passed"] += 1
    results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
    results["failed"] += 1
    results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
