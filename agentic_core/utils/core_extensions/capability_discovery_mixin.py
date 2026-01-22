from __future__ import annotations
"""
[PHASE 23] CapabilityDiscoveryMixin - Registry Pattern for Agent Capabilities.

Publishes agent capabilities to Redis upon async startup.
Enables dynamic discovery of agents that can perform specific tasks.

Key Design Decisions:
1. Capability registration is declarative (can be called in __init__)
2. Actual Redis registration happens in startup() (async-safe)
3. Uses Redis Sets for fast intersection lookups
4. Implements LifecycleMixin for proper async resource management

Registry Structure (Redis):
    - cap:{capability_name} -> Set of agent_ids that provide this capability
    - agent:{agent_id}:caps -> Set of capabilities this agent provides
    - agent:{agent_id}:meta -> Hash with agent metadata

Usage:
    class HealerAgent(CapabilityDiscoveryMixin, SovereignBaseAgent):
        def __init__(self):
            super().__init__()
            self.register_capability("heal_syntax")
            self.register_capability("heal_imports")

        async def startup(self):
            await super().startup()  # Registers capabilities with Redis

[SSOT] Capability discovery for agent orchestration.
"""


import logging
import os
import time
from typing import Any

Logger = logging.getLogger(__name__)


class CapabilityDiscoveryMixin:
    """
    [PHASE 23] Publishes capabilities to Redis upon async startup.

    Implements the Registry Pattern for dynamic agent discovery.
    Requires LifecycleMixin for proper async initialization.

    Capability Types:
        - heal_*: Healing capabilities (syntax, imports, structure)
        - validate_*: Validation capabilities (layer, naming, contract)
        - detect_*: Detection capabilities (drift, leak, deadlock)
        - execute_*: Execution capabilities (task, workflow, pipeline)

    Discovery Patterns:
        - find_providers(capability): Find all agents with a capability
        - find_common_providers(caps): Find agents with ALL specified capabilities
        - get_agent_capabilities(agent_id): Get all capabilities of an agent

    Attributes:
        _capabilities: Set of registered capabilities
        _agent_id: Unique identifier for this agent instance
        _registry_connected: Whether Redis registry is available
    """

    _capabilities: set[str]
    _agent_id: str
    _registry_connected: bool = False
    _redis_client: Any = None

    # Redis key prefixes
    CAPABILITY_PREFIX = "cap:"
    AGENT_PREFIX = "agent:"
    CAPABILITY_SUFFIX = ":caps"
    META_SUFFIX = ":meta"

    # TTL for capability registrations (1 hour default, refreshed on heartbeat)
    REGISTRATION_TTL = 3600

    def __init__(self, *args, agent_id: str | None = None, **kwargs):
        """
        Initialize capability discovery.

        Args:
            agent_id: Optional unique identifier. If not provided, uses class name + timestamp.
        """
        super().__init__(*args, **kwargs)

        self._capabilities = set()
        self._agent_id = agent_id or f"{self.__class__.__name__}_{int(time.time() * 1000)}"
        self._registry_connected = False
        self._redis_client = None

        Logger.debug(
            f"[{self.__class__.__name__}] Capability discovery initialized: {self._agent_id}"
        )

    def register_capability(self, capability: str) -> None:
        """
        Declarative capability registration.

        Can be called in __init__ - actual Redis registration happens in startup().

        Args:
            capability: Capability name (e.g., "heal_syntax", "validate_layer")
        """
        self._capabilities.add(capability)
        Logger.debug(f"[{self._agent_id}] Registered capability: {capability}")

    def unregister_capability(self, capability: str) -> None:
        """
        Remove a capability from this agent.

        Args:
            capability: Capability to remove
        """
        self._capabilities.discard(capability)
        Logger.debug(f"[{self._agent_id}] Unregistered capability: {capability}")

    async def _do_startup(self) -> None:
        """
        Register capabilities with Redis on startup.

        Called by LifecycleMixin.startup().
        """
        # Call parent startup if exists
        if hasattr(super(), "_do_startup"):
            await super()._do_startup()

        if not self._capabilities:
            Logger.debug(f"[{self._agent_id}] No capabilities to register")
            return

        # Try to connect to Redis
        await self._connect_registry()

        if self._registry_connected:
            await self._publish_capabilities()

    async def _connect_registry(self) -> None:
        """Connect to Redis registry."""
        try:
            import redis.asyncio as redis

            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self._redis_client = redis.from_url(redis_url, decode_responses=True)

            # Test connection
            await self._redis_client.ping()
            self._registry_connected = True

            Logger.info(f"[{self._agent_id}] Connected to capability registry")

        except ImportError:
            Logger.warning(f"[{self._agent_id}] redis.asyncio not available, registry disabled")
            self._registry_connected = False
        except Exception as e:
            Logger.warning(f"[{self._agent_id}] Registry connection failed: {e}")
            self._registry_connected = False

    async def _publish_capabilities(self) -> None:
        """Publish capabilities to Redis."""
        if not self._registry_connected or not self._redis_client:
            return

        try:
            pipe = self._redis_client.pipeline()

            # Register each capability
            for cap in self._capabilities:
                cap_key = f"{self.CAPABILITY_PREFIX}{cap}"
                pipe.sadd(cap_key, self._agent_id)
                pipe.expire(cap_key, self.REGISTRATION_TTL)

            # Register agent's capability list
            agent_caps_key = f"{self.AGENT_PREFIX}{self._agent_id}{self.CAPABILITY_SUFFIX}"
            pipe.delete(agent_caps_key)  # Clear old capabilities
            if self._capabilities:
                pipe.sadd(agent_caps_key, *self._capabilities)
                pipe.expire(agent_caps_key, self.REGISTRATION_TTL)

            # Register agent metadata
            agent_meta_key = f"{self.AGENT_PREFIX}{self._agent_id}{self.META_SUFFIX}"
            pipe.hset(
                agent_meta_key,
                mapping={
                    "class": self.__class__.__name__,
                    "registered_at": str(time.time()),
                    "capability_count": str(len(self._capabilities)),
                },
            )
            pipe.expire(agent_meta_key, self.REGISTRATION_TTL)

            await pipe.execute()

            Logger.info(
                f"[{self._agent_id}] Published {len(self._capabilities)} capabilities: "
                f"{', '.join(sorted(self._capabilities))}"
            )

        except Exception as e:
            Logger.error(f"[{self._agent_id}] Failed to publish capabilities: {e}")

    async def _do_shutdown(self) -> None:
        """Unregister capabilities on shutdown."""
        # Call parent shutdown if exists
        if hasattr(super(), "_do_shutdown"):
            await super()._do_shutdown()

        if self._registry_connected and self._redis_client:
            await self._unpublish_capabilities()
            await self._redis_client.close()

    async def _unpublish_capabilities(self) -> None:
        """Remove capabilities from Redis."""
        if not self._registry_connected or not self._redis_client:
            return

        try:
            pipe = self._redis_client.pipeline()

            # Remove from each capability set
            for cap in self._capabilities:
                cap_key = f"{self.CAPABILITY_PREFIX}{cap}"
                pipe.srem(cap_key, self._agent_id)

            # Remove agent's capability list
            agent_caps_key = f"{self.AGENT_PREFIX}{self._agent_id}{self.CAPABILITY_SUFFIX}"
            pipe.delete(agent_caps_key)

            # Remove agent metadata
            agent_meta_key = f"{self.AGENT_PREFIX}{self._agent_id}{self.META_SUFFIX}"
            pipe.delete(agent_meta_key)

            await pipe.execute()

            Logger.info(f"[{self._agent_id}] Unpublished capabilities")

        except Exception as e:
            Logger.warning(f"[{self._agent_id}] Failed to unpublish capabilities: {e}")

    async def find_providers(self, capability: str) -> list[str]:
        """
        Find all agents that provide a capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agent IDs that provide this capability
        """
        if not self._registry_connected or not self._redis_client:
            return []

        try:
            cap_key = f"{self.CAPABILITY_PREFIX}{capability}"
            providers = await self._redis_client.smembers(cap_key)
            return list(providers)
        except Exception as e:
            Logger.warning(f"[{self._agent_id}] Provider lookup failed: {e}")
            return []

    async def find_common_providers(self, capabilities: list[str]) -> list[str]:
        """
        Find agents that provide ALL specified capabilities.

        Uses Redis SINTER for efficient set intersection.

        Args:
            capabilities: List of required capabilities

        Returns:
            List of agent IDs that provide all capabilities
        """
        if not self._registry_connected or not self._redis_client:
            return []

        if not capabilities:
            return []

        try:
            cap_keys = [f"{self.CAPABILITY_PREFIX}{cap}" for cap in capabilities]
            providers = await self._redis_client.sinter(*cap_keys)
            return list(providers)
        except Exception as e:
            Logger.warning(f"[{self._agent_id}] Common provider lookup failed: {e}")
            return []

    async def get_agent_capabilities(self, agent_id: str) -> set[str]:
        """
        Get all capabilities of a specific agent.

        Args:
            agent_id: Agent to query

        Returns:
            Set of capabilities
        """
        if not self._registry_connected or not self._redis_client:
            return set()

        try:
            agent_caps_key = f"{self.AGENT_PREFIX}{agent_id}{self.CAPABILITY_SUFFIX}"
            caps = await self._redis_client.smembers(agent_caps_key)
            return set(caps)
        except Exception as e:
            Logger.warning(f"[{self._agent_id}] Capability lookup failed: {e}")
            return set()

    async def heartbeat(self) -> None:
        """
        Refresh capability registrations.

        Call periodically to prevent TTL expiration.
        """
        if self._registry_connected:
            await self._publish_capabilities()

    def get_discovery_stats(self) -> dict[str, Any]:
        """Get capability discovery statistics."""
        return {
            "agent_id": self._agent_id,
            "capabilities": sorted(self._capabilities),
            "capability_count": len(self._capabilities),
            "registry_connected": self._registry_connected,
        }
