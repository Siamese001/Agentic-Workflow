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

Logger = logging.getLogger(__name__)


class SovereignRedisClient:
    """Sovereign Redis client - audit + safe exec for all cache operations."""
    
    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis client.
        
        Args:
            url: Redis URL (defaults to env var or localhost)
        """
        self.redis_url = url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.audit_log: List[Dict[str, Any]] = []
        self._client = None
        self._fallback_cache: OrderedDict = OrderedDict()
        self._max_fallback_size = 1000
        self._use_fallback = False
    
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
        Route Redis operations safely.
        
        Args:
            operation: Redis operation (set, get, delete, etc.)
            **payload: Operation-specific parameters
        
        Returns:
            Result dictionary with success status and data
        """
        key = payload.get('key', '')
        Logger.debug(f"[SOVEREIGN REDIS] {operation}: {key[:50]}")
        
        client = self._get_client()
        
        try:
            if operation == 'set':
                value = payload.get('value', '')
                ttl = payload.get('ttl')
                
                if client:
                    if ttl:
                        client.setex(key, ttl, value)
                    else:
                        client.set(key, value)
                else:
                    self._fallback_set(key, value)
                
                result = {'success': True}
            
            elif operation == 'get':
                if client:
                    value = client.get(key)
                else:
                    value = self._fallback_cache.get(key)
                
                result = {'success': True, 'value': value}
            
            elif operation == 'delete':
                if client:
                    deleted = client.delete(key)
                else:
                    deleted = 1 if key in self._fallback_cache else 0
                    if key in self._fallback_cache:
                        del self._fallback_cache[key]
                
                result = {'success': True, 'deleted': deleted}
            
            elif operation == 'exists':
                if client:
                    exists = client.exists(key) > 0
                else:
                    exists = key in self._fallback_cache
                
                result = {'success': True, 'exists': exists}
            
            elif operation == 'keys':
                pattern = payload.get('pattern', '*')
                if client:
                    keys = client.keys(pattern)
                else:
                    import fnmatch
                    keys = [k for k in self._fallback_cache.keys() if fnmatch.fnmatch(k, pattern)]
                
                result = {'success': True, 'keys': keys}
            
            elif operation == 'expire':
                ttl = payload.get('ttl', 3600)
                if client:
                    client.expire(key, ttl)
                result = {'success': True}
            
            elif operation == 'ping':
                if client:
                    client.ping()
                result = {'success': True, 'pong': True, 'fallback': self._use_fallback}
            
            else:
                result = {'success': False, 'error': f'Unsupported Redis operation: {operation}'}
        
        except Exception as e:
            Logger.error(f"[SOVEREIGN REDIS] {operation} failed: {e}")
            result = {'success': False, 'error': str(e)}
        
        self._audit(operation, key, result)
        return result
