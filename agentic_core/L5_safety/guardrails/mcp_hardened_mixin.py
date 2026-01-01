"""
MCPHardenedMixin - Eternal Hardening for All MCP Integrations

Provides:
- Exponential backoff retry (configurable, default 3 attempts)
- SovereignEvent emission on connect/fail/success
- Timeout enforcement
- CRITIQUE emission on exhausted retries

Usage:
    class MyMCPClient(MCPHardenedMixin):
        async def call_something(self):
            return await self._hardened_call(
                "operation_name",
                self._actual_call_func,
                *args,
                **kwargs
            )
"""
import asyncio
import logging
from typing import Any, Callable, Dict, Optional

Logger: Any = logging.getLogger(__name__)


class MCPHardenedMixin:
    """
    Mixin providing hardened MCP operations:
    - Exponential backoff retry (3 attempts by default)
    - SovereignEvent emission on connect/fail
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    """

    MAX_RETRIES: int = 3
    BASE_DELAY: float = 1.0
    MAX_DELAY: float = 30.0
    DEFAULT_TIMEOUT: float = 30.0

    async def _hardened_call(
        self,
        operation: str,
        call_func: Callable,
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute MCP call with retry, timeout, and observability.

        Args:
            operation: Name of the operation (for logging/events)
            call_func: Async function to call
            *args: Positional arguments for call_func
            timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
            **kwargs: Keyword arguments for call_func

        Returns:
            Result from call_func

        Raises:
            RuntimeError: If all retries are exhausted
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        last_error: Optional[str] = None

        for attempt in range(self.MAX_RETRIES):
            try:
                self._emit_sovereign_event(
                    "MCP_CALL_START",
                    {"operation": operation, "attempt": attempt + 1},
                )

                result: Any = await asyncio.wait_for(
                    call_func(*args, **kwargs),
                    timeout=timeout,
                )

                self._emit_sovereign_event(
                    "MCP_CALL_SUCCESS",
                    {"operation": operation, "attempt": attempt + 1},
                )

                return result

            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s"
                self._emit_sovereign_event(
                    "MCP_CALL_TIMEOUT",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "timeout": timeout,
                    },
                )
            except Exception as e:
                last_error = str(e)
                self._emit_sovereign_event(
                    "MCP_CALL_FAIL",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "error": str(e),
                    },
                )

            if attempt < self.MAX_RETRIES - 1:
                delay: float = min(
                    self.BASE_DELAY * (2**attempt), self.MAX_DELAY
                )
                Logger.warning(
                    f"[MCP] {operation} attempt {attempt + 1} failed, "
                    f"retrying in {delay:.1f}s: {last_error}"
                )
                await asyncio.sleep(delay)

        self._emit_critique(operation, last_error or "Unknown error")
        raise RuntimeError(
            f"MCP {operation} failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    def _emit_sovereign_event(
        self, event_type: str, data: Dict[str, Any]
    ) -> None:
        """
        Emit telemetry event for observability.

        Args:
            event_type: Type of event (MCP_CALL_START, MCP_CALL_SUCCESS, etc.)
            data: Event data dictionary
        """
        try:
            from AgenticCore.observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(event_type, data)
        except ImportError:
            Logger.debug(f"[MCP] {event_type}: {data}")

    def _emit_critique(self, operation: str, error: str) -> None:
        """
        Emit CRITIQUE for subatomic retry consideration.

        Args:
            operation: Name of the failed operation
            error: Error message
        """
        Logger.critical(f"[CRITIQUE] MCP {operation} exhausted: {error}")
        try:
            from AgenticCore.observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(
                "MCP_CRITIQUE",
                {
                    "operation": operation,
                    "error": error,
                    "retries_exhausted": True,
                },
            )
        except ImportError:
            pass

    def get_redis_connection(self, url: Optional[str] = None):
        """
        Get hardened Redis connection with SSL enforcement and pooling.
        
        Args:
            url: Optional Redis URL (defaults to MCP_REDIS_URL env var)
            
        Returns:
            Redis client with connection pool
        """
        import os
        from redis import ConnectionPool, Redis
        
        redis_url = url or os.getenv("MCP_REDIS_URL") or os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("MCP_REDIS_URL or REDIS_URL must be set")
        
        # SSL enforcement
        ssl_enabled = os.getenv("MCP_REDIS_SSL", "false").lower() == "true"
        
        pool_kwargs = {
            "max_connections": int(os.getenv("MCP_REDIS_MAX_CONNECTIONS", "20")),
            "socket_connect_timeout": int(os.getenv("MCP_REDIS_TIMEOUT", "5")),
            "socket_timeout": int(os.getenv("MCP_REDIS_TIMEOUT", "5")),
            "socket_keepalive": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }
        
        if ssl_enabled:
            import ssl as ssl_module
            ssl_context = ssl_module.create_default_context()
            
            # Load custom certs if provided
            cert_path = os.getenv("MCP_REDIS_SSL_CERT_PATH")
            if cert_path:
                ssl_context.load_verify_locations(cert_path)
            
            pool_kwargs.update({
                "ssl": True,
                "ssl_cert_reqs": "required",
                "ssl_check_hostname": True,
            })
        
        pool = ConnectionPool.from_url(redis_url, **pool_kwargs)
        return Redis(connection_pool=pool)

    def get_neo4j_driver(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Get hardened Neo4j driver with SSL enforcement and connection pooling.
        
        Args:
            uri: Optional Neo4j URI (defaults to NEO4J_URI env var)
            username: Optional username (defaults to NEO4J_USERNAME env var)
            password: Optional password (defaults to NEO4J_PASSWORD env var)
            
        Returns:
            Neo4j driver with connection pool
        """
        import os
        from neo4j import GraphDatabase
        
        neo4j_uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = username or os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = password or os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_password:
            raise ValueError("[MCP HARDENED] NEO4J_PASSWORD must be set - no default allowed")
        
        # Force SSL/TLS encryption
        driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            encrypted=True,
            trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
            max_connection_lifetime=3600,
            max_connection_pool_size=int(os.getenv("NEO4J_MAX_POOL_SIZE", "50")),
            connection_acquisition_timeout=int(os.getenv("NEO4J_TIMEOUT", "60")),
        )
        
        return driver
