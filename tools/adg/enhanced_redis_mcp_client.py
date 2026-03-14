"""
Enhanced Redis MCP Client with HASH and SET support for ADG queries.

This client extends the basic Redis MCP functionality to support:
- HASH operations (hget, hgetall, hkeys, hvals)
- SET operations (smembers, scard)
- ADG-specific query helpers
- Graceful fallback to direct Redis when MCP tools fail
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EnhancedRedisMCPClient:
    """Enhanced Redis client that works with MCP tools and falls back to direct Redis.
    
    The standard MCP Redis tools only support STRING operations. This client
    provides HASH and SET operations needed for ADG cache queries.
    """
    
    def __init__(self, use_direct_redis: bool = True):
        """Initialize the enhanced client.
        
        Args:
            use_direct_redis: If True, fall back to direct Redis connection
                            when MCP tools can't handle the operation.
        """
        self.use_direct_redis = use_direct_redis
        self._direct_client = None
        
    def _get_direct_client(self):
        """Get a direct Redis client for fallback operations."""
        if self._direct_client is None and self.use_direct_redis:
            try:
                import redis
                self._direct_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=0, 
                    decode_responses=True
                )
                self._direct_client.ping()
                logger.debug("Direct Redis client connected")
            except Exception as exc:
                logger.warning(f"Direct Redis client failed: {exc}")
                self._direct_client = None
        return self._direct_client
    
    def get_string(self, key: str) -> Optional[str]:
        """Get a STRING value using MCP Redis tool."""
        try:
            from mcp9_get import mcp9_get
            return mcp9_get(key=key)
        except ImportError:
            logger.warning("mcp9_get not available")
            return None
        except Exception as exc:
            logger.warning(f"MCP get failed for {key}: {exc}")
            return None
    
    def get_hash(self, key: str) -> Optional[Dict[str, str]]:
        """Get a HASH value - falls back to direct Redis since MCP doesn't support HASH."""
        # Try direct Redis first since MCP can't handle HASH
        client = self._get_direct_client()
        if client:
            try:
                result = client.hgetall(key)
                logger.debug(f"Direct Redis HASH get: {key} -> {len(result)} fields")
                return result
            except Exception as exc:
                logger.warning(f"Direct Redis HASH get failed for {key}: {exc}")
                return None
        
        logger.error(f"Cannot retrieve HASH {key}: both MCP and direct Redis failed")
        return None
    
    def get_set(self, key: str) -> Optional[List[str]]:
        """Get a SET value - falls back to direct Redis since MCP doesn't support SET."""
        # Try direct Redis first since MCP can't handle SET
        client = self._get_direct_client()
        if client:
            try:
                result = list(client.smembers(key))
                logger.debug(f"Direct Redis SET get: {key} -> {len(result)} members")
                return result
            except Exception as exc:
                logger.warning(f"Direct Redis SET get failed for {key}: {exc}")
                return None
        
        logger.error(f"Cannot retrieve SET {key}: both MCP and direct Redis failed")
        return None
    
    def get_adg_meta(self) -> Optional[Dict[str, str]]:
        """Get ADG metadata hash."""
        return self.get_hash('adg:meta')
    
    def get_adg_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get ADG snapshot (STRING type - works with MCP)."""
        snapshot_str = self.get_string('adg:snapshot')
        if snapshot_str:
            try:
                return json.loads(snapshot_str)
            except json.JSONDecodeError as exc:
                logger.warning(f"Failed to parse ADG snapshot JSON: {exc}")
        return None
    
    def get_adg_nodes_by_layer(self, layer: str) -> Optional[List[str]]:
        """Get node IDs for a specific layer."""
        return self.get_set(f'adg:nodes:by_layer:{layer}')
    
    def get_adg_nodes_by_file(self, file_path: str) -> Optional[List[str]]:
        """Get node IDs for a specific file path."""
        return self.get_set(f'adg:nodes:by_file:{file_path}')
    
    def get_adg_edge_fan_out(self, node_id: str, relation_type: str) -> Optional[List[str]]:
        """Get fan-out edges from a node."""
        return self.get_set(f'adg:edge:{node_id}:{relation_type}')
    
    def get_adg_edge_fan_in(self, node_id: str, relation_type: str) -> Optional[List[str]]:
        """Get fan-in edges to a node."""
        return self.get_set(f'adg:edge:in:{node_id}:{relation_type}')
    
    def get_adg_violations(self) -> Optional[List[Dict[str, Any]]]:
        """Get ADG violations list."""
        client = self._get_direct_client()
        if client:
            try:
                violations = client.lrange('adg:violations', 0, -1)
                return [json.loads(v) for v in violations if v]
            except Exception as exc:
                logger.warning(f"Failed to get ADG violations: {exc}")
        return None
    
    def get_adg_drift_score(self) -> Optional[str]:
        """Get drift score composite."""
        return self.get_string('adg:drift:score')
    
    def get_adg_drift_subscores(self) -> Optional[Dict[str, str]]:
        """Get drift score subscores."""
        return self.get_hash('adg:drift:subscores')
    
    def get_adg_drift_uncovered(self) -> Optional[List[str]]:
        """Get uncovered production modules."""
        client = self._get_direct_client()
        if client:
            try:
                return client.lrange('adg:drift:uncovered', 0, -1)
            except Exception as exc:
                logger.warning(f"Failed to get drift uncovered: {exc}")
        return None
    
    def get_adg_drift_orphan_tests(self) -> Optional[List[str]]:
        """Get orphan/dead test modules."""
        client = self._get_direct_client()
        if client:
            try:
                return client.lrange('adg:drift:orphan_tests', 0, -1)
            except Exception as exc:
                logger.warning(f"Failed to get drift orphan tests: {exc}")
        return None
    
    def get_adg_layer_stats(self) -> Dict[str, int]:
        """Get comprehensive ADG layer statistics."""
        stats = {}
        
        # Get layer distribution from snapshot
        snapshot = self.get_adg_snapshot()
        if snapshot and 'by_layer' in snapshot:
            stats.update(snapshot['by_layer'])
        
        # Get additional metadata
        meta = self.get_adg_meta()
        if meta:
            stats['total_nodes'] = int(meta.get('node_count', 0))
            stats['total_edges'] = int(meta.get('edge_count', 0))
            stats['timestamp'] = meta.get('timestamp', 'unknown')
        
        return stats
    
    def check_adg_cache_health(self) -> Dict[str, Any]:
        """Check ADG cache health and availability."""
        health = {
            'mcp_available': False,
            'direct_redis_available': False,
            'adg_keys_count': 0,
            'adg_meta_available': False,
            'adg_snapshot_available': False,
            'cache_freshness_hours': None,
            'errors': []
        }
        
        # Check MCP availability
        try:
            from mcp9_get import mcp9_get
            test_key = 'adg:snapshot'
            result = mcp9_get(key=test_key)
            health['mcp_available'] = True
            health['adg_snapshot_available'] = result is not None
        except ImportError:
            health['errors'].append('MCP Redis tools not available')
        except Exception as exc:
            health['errors'].append(f'MCP Redis error: {exc}')
        
        # Check direct Redis availability
        client = self._get_direct_client()
        if client:
            health['direct_redis_available'] = True
            try:
                # Count ADG keys
                adg_keys = client.keys('adg:*')
                health['adg_keys_count'] = len(adg_keys)
                
                # Check metadata
                meta = self.get_adg_meta()
                health['adg_meta_available'] = meta is not None
                
                # Calculate cache freshness
                if meta and 'ingested_at' in meta:
                    import time
                    try:
                        ingest_time = float(meta['ingested_at'])
                        current_time = time.time()
                        health['cache_freshness_hours'] = (current_time - ingest_time) / 3600
                    except (ValueError, TypeError):
                        pass
                        
            except Exception as exc:
                health['errors'].append(f'Direct Redis error: {exc}')
        else:
            health['errors'].append('Direct Redis not available')
        
        return health
    
    def query_adg_with_fallback(self, query_type: str, **kwargs) -> Any:
        """Execute ADG query with automatic fallback between MCP and direct Redis.
        
        Args:
            query_type: Type of query ('meta', 'snapshot', 'layer_nodes', etc.)
            **kwargs: Query-specific parameters
            
        Returns:
            Query result or None if all methods fail
        """
        # Map query types to methods
        query_map = {
            'meta': self.get_adg_meta,
            'snapshot': self.get_adg_snapshot,
            'layer_nodes': lambda: self.get_adg_nodes_by_layer(kwargs.get('layer', '')),
            'file_nodes': lambda: self.get_adg_nodes_by_file(kwargs.get('file_path', '')),
            'fan_out': lambda: self.get_adg_edge_fan_out(kwargs.get('node_id', ''), kwargs.get('relation_type', '')),
            'fan_in': lambda: self.get_adg_edge_fan_in(kwargs.get('node_id', ''), kwargs.get('relation_type', '')),
            'violations': self.get_adg_violations,
            'drift_score': self.get_adg_drift_score,
            'drift_subscores': self.get_adg_drift_subscores,
            'drift_uncovered': self.get_adg_drift_uncovered,
            'drift_orphan_tests': self.get_adg_drift_orphan_tests,
            'layer_stats': self.get_adg_layer_stats,
        }
        
        if query_type not in query_map:
            logger.error(f"Unknown query type: {query_type}")
            return None
        
        try:
            result = query_map[query_type]()
            if result is not None:
                logger.debug(f"ADG query {query_type} succeeded")
                return result
        except Exception as exc:
            logger.warning(f"ADG query {query_type} failed: {exc}")
        
        logger.error(f"ADG query {query_type} failed completely")
        return None


# Singleton instance for easy access
_enhanced_client: Optional[EnhancedRedisMCPClient] = None


def get_enhanced_redis_client() -> EnhancedRedisMCPClient:
    """Get the singleton enhanced Redis MCP client."""
    global _enhanced_client
    if _enhanced_client is None:
        _enhanced_client = EnhancedRedisMCPClient()
    return _enhanced_client


def reset_enhanced_client() -> None:
    """Reset the singleton client (for testing)."""
    global _enhanced_client
    _enhanced_client = None


if __name__ == "__main__":
    # Demo usage
    client = get_enhanced_redis_client()
    
    print("=== ADG Cache Health ===")
    health = client.check_adg_cache_health()
    for key, value in health.items():
        print(f"{key}: {value}")
    
    print("\n=== ADG Metadata ===")
    meta = client.get_adg_meta()
    if meta:
        print(f"Timestamp: {meta.get('timestamp')}")
        print(f"Node count: {meta.get('node_count')}")
        print(f"Edge count: {meta.get('edge_count')}")
    
    print("\n=== Layer Stats ===")
    stats = client.get_adg_layer_stats()
    for layer, count in stats.items():
        if isinstance(count, int):
            print(f"{layer}: {count}")
    
    print("\n=== Sample Query: L0 Nodes ===")
    l0_nodes = client.get_adg_nodes_by_layer('L0')
    if l0_nodes:
        print(f"L0 has {len(l0_nodes)} nodes")
        print(f"Sample: {l0_nodes[:3]}")
