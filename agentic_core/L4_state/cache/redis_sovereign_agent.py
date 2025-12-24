#!/usr/bin/env python3
"""
RedisSovereignAgent - Eternal Sovereign Gateway to Redis
"""

import redis
import hashlib
from redis.connection import ConnectionPool
from pathlib import Path
from typing import Dict
from agentic_core.config.P1_core.sovereign_env import get_env

class RedisSovereignAgent:
    """
    Sovereign Redis controller — hardened, monitored, eternal.
    """
    _instance = None

    def __new__(cls, project_root: Path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(project_root)
        return cls._instance

    def _init(self, project_root: Path):
        env = get_env(project_root)
        
        # Hardened Pool: Prevent connection leaks
        connection_kwargs = {
            "max_connections": 20,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "socket_keepalive": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "ssl": env.REDIS_SSL,
        }
        if env.REDIS_PASSWORD:
            connection_kwargs["password"] = env.REDIS_PASSWORD

        self.pool = ConnectionPool.from_url(env.REDIS_URL, **connection_kwargs)
        self.client = redis.Redis(connection_pool=self.pool)

        # Fail-fast check
        try:
            self.client.ping()
        except Exception as e:
            raise ConnectionError(f"[L6 CRITICAL] Redis gateway failed: {e}")

    def get_client(self) -> redis.Redis:
        return self.client

    def invalidate_file_cache(self, file_path: Path):
        """Wipes old embeddings if the file has evolved"""
        try:
            content = file_path.read_bytes()
            # We use a partial hash in the key to find related embeddings
            content_hash = hashlib.sha256(content).hexdigest()[:16]
            pattern = f"pc_embed:*{content_hash}*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass 

    def invalidate_by_path(self, file_path: Path):
        """
        Invalidate cache by exact file path (for moves/deletes).
        Ensures no 'ghost' embeddings remain for a path that no longer exists.
        """
        try:
            # Normalize path for key matching
            rel_path = str(file_path.relative_to(Path(".").resolve())).replace("/", "_")
            pattern = f"pc_embed:*:*{rel_path}*"
            keys = self.client.keys(pattern)
            
            if keys:
                deleted = self.client.delete(*keys)
                print(f"   [CACHE] Purged {deleted} ghost entries for: {file_path.name}")
        except Exception as e:
            # Non-critical, don't break the healer
            print(f"   [!] Cache invalidation failed for {file_path}: {e}") 

    async def execute(self, ctx=None):
        info = self.client.info()
        mem = info.get("used_memory_human", "0B")
        print(f"   [OK] RedisSovereignAgent: Healthy. Memory: {mem}")
        if ctx:
            ctx.report("RedisCache", 1, True, f"Redis online ({mem})")
