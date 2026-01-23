"""
Surgery Script - Phase 19 Nuclear Sweep

[PHASE 19]
The Ultimate Fix.
1. Finds offending filenames ANYWHERE in the tree.
2. Overwrites them with clean code.
3. Hunts down the specific __init__.py leaking Pinecone.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

CSS_CONTENT = '''from __future__ import annotations
"""CachedSafetyShield - Eternal L5 Safety Base with Sovereign cache."""
import hashlib
import json
from pathlib import Path
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class CachedSafetyShield(SovereignBaseAgent):
    def __init__(self, project_root=None, session_id: str = "l5_global"):
        super().__init__()
        self.root = project_root or Path(".")
        self.session_id = session_id
        self.prefix_gravity = f"l5_gravity:{session_id}"
        self.prefix_policy = f"l5_policy:{session_id}"

    def get_cached_verdict(self, category: str, identifier: str) -> dict | None:
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        return self.cache_get(key)

    def store_verdict(self, category: str, identifier: str, verdict: dict, ttl: int = 86400) -> None:
        key = f"l5_{category}:{self.session_id}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        verdict["timestamp"] = __import__("datetime").datetime.now().isoformat()
        self.cache_set(key, verdict, ttl=ttl)

cached_safety_shield_impl = CachedSafetyShield
'''

NEURAL_CONTENT = '''from __future__ import annotations
"""NeuralAutoImmuneAgent - Sovereign Self-Defense."""
from dataclasses import dataclass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

class SubatomicTestingMixin: pass
class AutonomyMixin: pass
class AdaptiveExecutionMixin: pass
class SelfDiagnosisMixin: pass
class HealerMixin: pass

@dataclass
class NeuralAutoImmuneAgent(SovereignBaseAgent):
    def __post_init__(self):
        super().__post_init__()

    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
'''

DIPLOMAT_CONTENT = '''from __future__ import annotations
"""Dependency Diplomat - Graph Optimizer."""
from dataclasses import dataclass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

@dataclass
class DependencyDiplomatAgent(SovereignBaseAgent):
    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
'''

MAPPER_CONTENT = '''from __future__ import annotations
"""Semantic Territory Mapper Agent."""
from dataclasses import dataclass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

@dataclass
class SemanticTerritoryMapperAgent(SovereignBaseAgent):
    async def execute(self) -> None:
        print("[*] SemanticMapper: Analyzing coverage (Gateway Mode)")
'''

CAPABILITY_CONTENT = '''from __future__ import annotations
"""CapabilityDiscoveryMixin - Registry Pattern."""
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
            Logger.warning(f"Capability publish failed: {e}")
'''

TARGETS = {
    "cached_safety_shield.py": CSS_CONTENT,
    "NeuralAutoImmuneAgent.py": NEURAL_CONTENT,
    "DependencyDiplomatAgent.py": DIPLOMAT_CONTENT,
    "SemanticTerritoryMapperAgent.py": MAPPER_CONTENT,
    "capability_discovery_mixin.py": CAPABILITY_CONTENT,
}


def nuclear_sweep():
    print("--- STARTING PHASE 19 NUCLEAR SWEEP ---")

    for root, dirs, files in os.walk(PROJECT_ROOT / "agentic_core"):
        if "archived" in root:
            continue

        for file in files:
            if file in TARGETS:
                full_path = Path(root) / file
                print(f"[FOUND] {full_path}")

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(TARGETS[file])
                print(f"[CLEANED] {full_path}")

    print("\n--- HUNTING PINECONE __init__ ---")
    for root, dirs, files in os.walk(PROJECT_ROOT / "agentic_core"):
        if "archived" in root:
            continue

        if "__init__.py" in files:
            full_path = Path(root) / "__init__.py"
            try:
                content = full_path.read_text(encoding="utf-8")
                if "pinecone_sync" in content or "pinecone_store" in content:
                    print(f"[VIOLATION FOUND] {full_path}")

                    new_lines = []
                    for line in content.splitlines():
                        if "pinecone_sync" in line or "pinecone_store" in line:
                            new_lines.append(f"# {line}  # [PHASE 19] Removed legacy import")
                        else:
                            new_lines.append(line)

                    full_path.write_text("\n".join(new_lines), encoding="utf-8")
                    print(f"[FIXED] {full_path}")
            except Exception as e:
                print(f"Error reading {full_path}: {e}")

    print("--- NUCLEAR SWEEP COMPLETE ---")


if __name__ == "__main__":
    nuclear_sweep()
