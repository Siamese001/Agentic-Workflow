from __future__ import annotations

"CapabilityDiscoveryMixin - Registry Pattern."
import logging

Logger = logging.getLogger(__name__)


class CapabilityDiscoveryMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._capabilities = set()
        self.AGENT_PREFIX = "agent:"
        self.CAPABILITY_SUFFIX = ":caps"

    async def register_capability(self, capability: str) -> None:
        self._capabilities.add(capability)

    async def _publish_capabilities(self) -> None:
        client = getattr(self, "redis_client", None)
        if not client:
            return
        try:
            agent_id = getattr(self, "name", "unknown_agent")
            key = f"{self.AGENT_PREFIX}{agent_id}{self.CAPABILITY_SUFFIX}"
            if self._capabilities:
                await client.sadd(key, *self._capabilities)
                await client.expire(key, 3600)
        except Exception as e:
            raise
            Logger.warning(f"Capability publish failed: {e}")
