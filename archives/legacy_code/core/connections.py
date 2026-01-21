"""
Swarm Network Connections - Hardened Architecture

Manages the connection pool for Redis Stack and Qdrant
with strict retry logic and fail-fast behavior.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.exceptions import MemorySyncError, SwarmInitializationError
from core.qdrant_cache import QdrantCache
from core.semantic_gatekeeper import SemanticGatekeeper, get_gatekeeper

from schemas.canon_models import CanonEntry

logger = logging.getLogger(__name__)


class SwarmNetwork:
    """
    Singleton connection manager for the Hardened Swarm.

    Manages Redis Stack and Qdrant connections with exponential backoff
    retry logic. Fails entire swarm startup if connections cannot be
    established.
    """

    _instance: Optional['SwarmNetwork'] = None
    _initialized: bool = False

    def __new__(cls) -> 'SwarmNetwork':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the swarm network connections."""
        if SwarmNetwork._initialized:
            return

        self.redis_host = "localhost"
        self.redis_port = 6379
        self.qdrant_host = "localhost"
        self.qdrant_port = 6333

        # Connection objects
        self.gatekeeper: Optional[SemanticGatekeeper] = None
        self.qdrant_cache: Optional[QdrantCache] = None

        # Connection state
        self._connected = False
        self._connection_attempts = 0
        self._max_attempts = 5
        self._backoff_factor = 2

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "retry_count": 0
        }

        SwarmNetwork._initialized = True
        logger.info("SwarmNetwork singleton created")

    def connect(self, force_retry: bool = False) -> bool:
        """
        Establish connections to Redis and Qdrant.

        Args:
            force_retry: Whether to force reconnection attempts

        Returns:
            True if connections successful

        Raises:
            SwarmInitializationError: If connections cannot be established
        """
        if self._connected and not force_retry:
            return True

        self._connection_attempts = 0

        # Try to connect with exponential backoff
        while self._connection_attempts < self._max_attempts:
            try:
                self._connection_attempts += 1

                # Initialize SemanticGatekeeper (includes Redis)
                logger.info(
                    f"Connection attempt {self._connection_attempts}/{self._max_attempts}")
                self.gatekeeper = get_gatekeeper()

                # Initialize Qdrant cache
                self.qdrant_cache = QdrantCache(
                    host=self.qdrant_host,
                    port=self.qdrant_port,
                    index_name="canon-l2"
                )

                # Verify connections
                self._verify_connections()

                self._connected = True
                logger.info(
                    f"SwarmNetwork connected successfully on attempt {self._connection_attempts}")
                return True

            except Exception as e:
logger.error(
                    f"Connection attempt {self._connection_attempts} failed: {e}")

                if self._connection_attempts < self._max_attempts:
                    # Exponential backoff
                    delay = self._backoff_factor ** (
                        self._connection_attempts - 1)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    self.metrics["retry_count"] += 1
                else:
                    raise SwarmInitializationError(
                        f"Failed to connect after {self._max_attempts} attempts",
                        failed_component="SwarmNetwork",
                        context={"last_error": str(e)}
                    )

        return False

    def _verify_connections(self):
        """Verify that both Redis and Qdrant are accessible."""
        # Test Redis connection
        try:
            # Simple ping to Redis through gatekeeper
            self.gatekeeper.redis.ping()
            logger.debug("Redis connection verified")
        except Exception as e:
raise MemorySyncError(
                "Redis connection failed",
                operation="ping",
                backend="redis",
                retry_count=self._connection_attempts,
                context={"error": str(e)}
            )

        # Test Qdrant connection
        try:
            # Simple collection check
            self.qdrant_cache.client.get_collections()
            logger.debug("Qdrant connection verified")
        except Exception as e:
raise MemorySyncError(
                "Qdrant connection failed",
                operation="get_collections",
                backend="qdrant",
                retry_count=self._connection_attempts,
                context={"error": str(e)}
            )

    def consult_canon(
        self,
        query_vector: List[float],
        agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[CanonEntry]]:
        """
        Consult the Canon for a given query.

        Args:
            query_vector: Embedding vector to search for
            agent_id: ID of the consulting agent
            context: Additional context for the query

        Returns:
            Tuple of (is_safe, matching_pattern)

        Raises:
            CanonViolationError: If pattern has failures
            MemorySyncError: If consultation fails
        """
        if not self._connected:
            raise MemorySyncError(
                "SwarmNetwork not connected",
                operation="consult_canon",
                backend="both"
            )

        self.metrics["total_queries"] += 1

        try:
            # Use SemanticGatekeeper for consultation
            planned_action = context.get(
                "action", f"Agent {agent_id} consultation")
            code = context.get("code")
            policy_key = context.get("policy_key")

            is_safe, pattern = self.gatekeeper.consult_canon(
                planned_action=planned_action,
                code=code,
                policy_key=policy_key,
                context=context
            )

            # Check for pattern failures
            if pattern and pattern.failure_count > 0:
                raise CanonViolationError(
                    f"Pattern has {pattern.failure_count} failures",
                    violation_type="pattern_failure",
                    agent_id=agent_id,
                    pattern_id=str(pattern.id),
                    context={
                        "failure_count": pattern.failure_count,
                        "success_count": pattern.success_count
                    }
                )

            # Update metrics
            if pattern:
                self.metrics["cache_hits"] += 1
            else:
                self.metrics["cache_misses"] += 1

            # Log consultation
            self._log_consultation(agent_id, is_safe, pattern, context)

            return is_safe, pattern

        except CanonViolationError:
raise
        except Exception as e:
self.metrics["errors"] += 1
            raise MemorySyncError(
                f"Canon consultation failed: {e}",
                operation="consult_canon",
                backend="both",
                context={"agent_id": agent_id}
            )

    def record_outcome(
        self,
        pattern_id: str,
        success: bool,
        agent_id: str,
        latency_ms: Optional[int] = None,
        error_trace: Optional[str] = None
    ):
        """
        Record execution outcome for meta-learning.

        Args:
            pattern_id: ID of the pattern used
            success: Whether execution was successful
            agent_id: ID of the executing agent
            latency_ms: Execution latency
            error_trace: Error trace if failed
        """
        if not self._connected:
            logger.warning("Cannot record outcome: SwarmNetwork not connected")
            return

        try:
            # Use SemanticGatekeeper to record pattern
            self.gatekeeper.record_pattern(
                action=f"Agent {agent_id} execution",
                code="",  # Will be retrieved from pattern
                policy_key="agent_execution",
                agent_name=agent_id,
                pattern_type="agent_task",
                files_touched=1,
                latency_ms=latency_ms or 0,
                success=success,
                project_tag="swarm_execution",
                error_trace=error_trace
            )

            logger.debug(
                f"Recorded outcome for pattern {pattern_id}: {'SUCCESS' if success else 'FAILURE'}")

        except Exception as e:
logger.error(f"Failed to record outcome: {e}")
            self.metrics["errors"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get connection and performance metrics."""
        if self.gatekeeper:
            latency_stats = self.gatekeeper.get_latency_stats()
            self.metrics.update({
                "latency_stats": latency_stats
            })

        return {
            "connected": self._connected,
            "connection_attempts": self._connection_attempts,
            "metrics": self.metrics.copy(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _log_consultation(
        self,
        agent_id: str,
        is_safe: bool,
        pattern: Optional[CanonEntry],
        context: Optional[Dict[str, Any]]
    ):
        """Log consultation details in structured format."""
        log_entry = {
            "event": "canon_consultation",
            "agent_id": agent_id,
            "is_safe": is_safe,
            "pattern_found": pattern is not None,
            "timestamp": datetime.utcnow().isoformat()
        }

        if pattern:
            log_entry.update({
                "pattern_id": str(pattern.id),
                "failure_count": pattern.failure_count,
                "success_count": pattern.success_count
            })

        if context:
            log_entry["context"] = context

        logger.info(json.dumps(log_entry))

    def disconnect(self):
        """Disconnect from all services."""
        if self.gatekeeper:
            self.gatekeeper.shutdown()

        self._connected = False
        logger.info("SwarmNetwork disconnected")

    @classmethod
    def get_instance(cls) -> 'SwarmNetwork':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton (for testing)."""
        if cls._instance:
            cls._instance.disconnect()
        cls._instance = None
        cls._initialized = False
