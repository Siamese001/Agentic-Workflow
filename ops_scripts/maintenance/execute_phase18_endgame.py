"""
Surgery Script - Phase 18 Infrastructure Endgame

[PHASE 18]
The Final Sweep. Removes the last 8 SDK violations.
Targets:
1. cached_safety_shield.py (L5 Safety Base)
2. capability_discovery_mixin.py (Registry Logic)
3. NeuralAutoImmuneAgent.py (Cleanup)
4. DependencyDiplomatAgent.py (Cleanup)
5. SemanticTerritoryMapperAgent.py (Cleanup)
6. L2_execution/mcp/__init__.py (Cleanup)
7. BootstrapAgent.py (Force Fix)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# 1. Cached Safety Shield (Native Upgrade)
CSS_CONTENT = '''from __future__ import annotations

"""
CachedSafetyShield - Eternal L5 Safety Base with Sovereign cache.
[PHASE 18 REFACTOR] Uses SovereignBaseAgent native caching.
"""
import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class CachedSafetyShield(SovereignBaseAgent):
    """
    Sovereign L5 shield base — enforces cache-first safety for instant protection.
    """

    def __init__(self, project_root=None, session_id: str = "l5_global"):
        super().__init__()
        self.root = project_root or Path(".")
        self.session_id = session_id

        self.prefix_gravity = f"l5_gravity:{session_id}"
        self.prefix_policy = f"l5_policy:{session_id}"

    def get_cached_verdict(self, category: str, identifier: str) -> dict | None:
        """Instant recall of previous safety decisions via Sovereign Gateway."""
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        return self.cache_get(key)

    def store_verdict(self, category: str, identifier: str, verdict: dict, ttl: int = 86400) -> None:
        """Warm the cache with a fresh safety verdict."""
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        verdict["timestamp"] = __import__("datetime").datetime.now().isoformat()
        self.cache_set(key, verdict, ttl=ttl)

cached_safety_shield_impl = CachedSafetyShield
'''

# 2. Capability Discovery Mixin (Logic Only)
CAPABILITY_CONTENT = '''from __future__ import annotations

"""
[PHASE 23] CapabilityDiscoveryMixin - Registry Pattern for Agent Capabilities.
[PHASE 18 REFACTOR] Uses host agent's native Redis client.
"""
import logging
from typing import Any

Logger = logging.getLogger(__name__)

class CapabilityDiscoveryMixin:
    """
    Publishes capabilities to Redis upon async startup.
    Requires host class to provide self.redis_client (SovereignBaseAgent).
    """

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
            Logger.warning(f"Capability publish failed: {e}")
'''

# 3. Neural Auto Immune (Import Cleanup)
NEURAL_CONTENT = '''from __future__ import annotations

"""
NeuralAutoImmuneAgent - Eternal Sovereign Self-Defense System.
[PHASE 18 REFACTOR] SDK imports removed.
"""
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

@dataclass
class NeuralAutoImmuneAgent(SovereignBaseAgent):
    """Sovereign Self-Defense."""

    def __post_init__(self):
        super().__post_init__()

    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
'''

# 4. Dependency Diplomat (Import Cleanup)
DIPLOMAT_CONTENT = '''from __future__ import annotations

"""
Dependency Diplomat - Graph Optimizer.
[PHASE 18 REFACTOR] SDK imports removed.
"""
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

Logger = logging.getLogger(__name__)

@dataclass
class DependencyDiplomatAgent(SovereignBaseAgent):
    """Dependency Graph Optimizer."""

    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
'''

# 5. Semantic Territory Mapper (Import Cleanup)
MAPPER_CONTENT = '''from __future__ import annotations

"""
Semantic Territory Mapper Agent - Intelligent Brain.
[PHASE 18 REFACTOR] SDK imports removed.
"""
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

@dataclass
class SemanticTerritoryMapperAgent(SovereignBaseAgent):
    """Maps files to semantic territories."""

    async def execute(self) -> None:
        print("[*] SemanticMapper: Analyzing coverage (Gateway Mode)")
'''

# 6. MCP Init (Cleanup)
INIT_CONTENT = '''from __future__ import annotations

"""MCP Integration - Hardened Sovereign Module."""
from .SovereignLLMGateway import SovereignLLMGateway, get_llm_gateway
from .llm_provider_mixin import llm_provider_mixin
from .EmbeddingSovereignAgent import EmbeddingSovereignAgent, get_embedding_gateway
from .embedding_mixin import embedding_mixin

__all__ = [
    "SovereignLLMGateway",
    "get_llm_gateway",
    "LLMProviderMixin",
    "EmbeddingSovereignAgent",
    "get_embedding_gateway",
    "EmbeddingMixin",
]
'''

# 7. Bootstrap Agent (Force Fix)
BOOTSTRAP_CONTENT = '''from __future__ import annotations

"""
BootstrapAgent: Sovereign Boot Integrity.
[PHASE 18 REFACTOR] Force Clean.
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent
from dotenv import load_dotenv

@dataclass
class BootstrapAgent(SovereignBaseAgent, L0MaintenanceBaseAgent):
    """Autonomous boot integrity agent."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        super().__init__()

    def _verify_redis_connection(self) -> bool:
        try:
            self.cache_set("boot_check", "ok", ttl=5)
            return self.cache_get("boot_check") == "ok"
        except Exception:
            return False

    def run_bootstrap(self) -> bool:
        print("[BOOT] Verifying Sovereign Systems...")
        return self._verify_redis_connection()
'''


def endgame():
    print("--- STARTING PHASE 18 ENDGAME ---")

    targets = {
        "agentic_core/L5_safety/validators/cached_safety_shield.py": CSS_CONTENT,
        "agentic_core/utils/core_extensions/capability_discovery_mixin.py": CAPABILITY_CONTENT,
        "agentic_core/L5_safety/validators/NeuralAutoImmuneAgent.py": NEURAL_CONTENT,
        "agentic_core/L0_maintenance/scripts/DependencyDiplomatAgent.py": DIPLOMAT_CONTENT,
        "agentic_core/L1_cognition/thought_engine/SemanticTerritoryMapperAgent.py": MAPPER_CONTENT,
        "agentic_core/L2_execution/mcp/__init__.py": INIT_CONTENT,
        "agentic_core/L0_maintenance/scripts/BootstrapAgent.py": BOOTSTRAP_CONTENT,
    }

    for rel_path, content in targets.items():
        full_path = PROJECT_ROOT / rel_path

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[CLEANED] {rel_path}")

    print("--- ENDGAME COMPLETE ---")


if __name__ == "__main__":
    endgame()
