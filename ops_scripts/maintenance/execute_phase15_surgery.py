"""
Surgery Script - Phase 15 Base Layer Purge

[PHASE 15]
Eliminates 'google.genai' from the L2 Base Agent and Cognitive Agent.
Enforces SovereignLLMGateway usage.

Targets:
1. L2ExecutionBase.py (The Base Class)
2. CognitiveDispositionAgent.py (The Architect)
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# 1. L2ExecutionBase (Clean Rewrite)
L2_AGENT_CONTENT = '''from __future__ import annotations

"""
[PHASE 15 REFACTOR] Unified L2 Execution Base Agent.
STRICT COMPLIANCE: SovereignBaseAgent Native. No Vendor SDKs.
"""

import asyncio
import os
import re
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.pinecone_vector_mixin import pinecone_vector_mixin
from agentic_core.mixins.redis_cache_mixin import redis_cache_mixin
from agentic_core.base_agents.timeout_decorator import timeout

load_dotenv()

def get_subatomic_engine() -> Any:
    from agentic_core.L3_orchestration.engine.subatomic_engine import SubAtomicEngineImpl
    return SubAtomicEngineImpl()

@dataclass
class L2ExecutionBase(RedisCacheMixin, PineconeVectorMixin, SovereignBaseAgent):
    """
    Unified L2 base class - Phase 15 Hardened.
    Inherits:
    - SovereignBaseAgent (Config, LLM, Healing, Validation)
    - RedisCacheMixin (L4 State)
    - PineconeVectorMixin (L4 Memory)
    """

    ctx: Any
    enable_gemini: bool = True

    _cache_prefix: str = "l2_execution"
    _namespace: str = "l2_tools"

    name: str = field(init=False)
    role: str = field(init=False)
    _subatomic_engine: Any | None = field(default=None, init=False)

    BANNED_IMPORTS: list[str] = field(
        default_factory=lambda: ["google.genai", "openai", "anthropic"],
        init=False,
    )

    def __post_init__(self) -> None:
        super().__post_init__()
        if not hasattr(self, "name") or not self.name:
            self.name = self.__class__.__name__
        self.role = re.sub("(?<!^)(?=[A-Z])", "_", self.name).lower()

        if self.enable_gemini:
            try:
                self._subatomic_engine = get_subatomic_engine()
            except Exception as e:
                self.log_error(f"Failed to init Sub-Atomic Engine: {e}")

    def can_run(self) -> bool:
        return "CRITICAL_FAIL" not in getattr(self.ctx, "signals", [])

    async def run_with_broadcast(self) -> Any:
        self.ctx._current_agent = self.name
        try:
            return await self.execute()
        except Exception as e:
            self.log_error(f"Execution error: {e}")
            raise

    @abstractmethod
    async def execute(self) -> Any:
        raise NotImplementedError(f"{self.name} must implement async execute()")

    def get_validation_keys(self) -> list[int]:
        return []

    def act(self, plan: list[str]) -> dict[str, Any]:
        return {"status": "act_placeholder", "plan_size": len(plan)}

    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
'''

# 2. CognitiveDispositionAgent (Clean Rewrite)
CDA_CONTENT = '''from __future__ import annotations

"""
[PHASE 15 REFACTOR] Cognitive Disposition Agent.
STRICT COMPLIANCE: Native Sovereign Capabilities.
"""

from typing import Any
from pathlib import Path
from dataclasses import dataclass
import json
import logging

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)

@dataclass
class DispositionDecision:
    action: str
    target_path: str | None = None
    reason: str = ""
    confidence: float = 0.0

class CognitiveDispositionAgent(SovereignBaseAgent):
    """AI-Powered Architectural Triage Agent via Sovereign Gateway."""

    def __init__(self, project_root: Path | None = None, confidence_threshold: float = 0.8):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold

        self.layer_map = {
            "L0_maintenance": "Maintenance",
            "L1_cognition": "Cognitive",
            "L2_execution": "Execution",
            "L3_orchestration": "Orchestration",
            "L4_state": "State",
            "L5_safety": "Safety",
            "L6_observability": "observability",
        }

    async def analyze_violation_async(self, file_path: Path, violation_type: str, context: dict = None) -> DispositionDecision:
        """Analyze violation using Native LLM Gateway."""
        context = context or {}

        cache_key = f"cda:{file_path.name}:{violation_type}"
        cached = self.cache_get(cache_key)
        if cached:
            return DispositionDecision(**cached)

        prompt = self._build_prompt(file_path, violation_type, context)

        try:
            response = await self.llm_generate(
                prompt,
                provider="google",
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            )

            try:
                data = json.loads(response["content"])
            except:
                text = response["content"].replace("```json", "").replace("```", "").strip()
                data = json.loads(text)

            decision = DispositionDecision(
                action=data.get("action", "MANUAL_REVIEW"),
                target_path=data.get("target_path"),
                reason=data.get("reason", "Parsed from LLM"),
                confidence=float(data.get("confidence", 0.0))
            )

            await self.cache_set(cache_key, decision.__dict__, ttl=3600)

            return decision

        except Exception as e:
            Logger.error(f"CDA Analysis failed: {e}")
            return DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {e}")

    def _build_prompt(self, file_path: Path, violation_type: str, context: dict) -> str:
        return f"""
        Analyze File: {file_path.name}
        Violation: {violation_type}
        Context: {json.dumps(context)}

        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.
        Return JSON.
        """
'''


def perform_surgery():
    print("--- STARTING PHASE 15 SURGERY ---")

    targets = [
        ("agentic_core/L2_execution/L2ExecutionBase.py", L2_AGENT_CONTENT),
        ("agentic_core/L5_safety/validators/CognitiveDispositionAgent.py", CDA_CONTENT),
    ]

    for rel_path, content in targets:
        full_path = PROJECT_ROOT / rel_path

        full_path.parent.mkdir(parents=True, exist_ok=True)

        if full_path.exists():
            full_path.rename(full_path.with_suffix(".py.bak_p15"))

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SURGERY COMPLETE] {rel_path}")

    print("--- HUNTING CDA GHOSTS ---")
    for root, _dirs, files in os.walk(PROJECT_ROOT / "agentic_core"):
        if "archived" in root:
            continue

        for file in files:
            if file == "CognitiveDispositionAgent.py":
                found_path = Path(root) / file
                target_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/CognitiveDispositionAgent.py"

                if found_path.resolve() != target_path.resolve():
                    print(f"[GHOST FOUND] {found_path}")
                    archive_dest = (
                        PROJECT_ROOT
                        / "archives/agentic_core_archived"
                        / f"ghost_{file}_{os.urandom(4).hex()}.py"
                    )
                    archive_dest.parent.mkdir(parents=True, exist_ok=True)
                    found_path.rename(archive_dest)
                    print(f" -> Archived to {archive_dest.name}")

    print("--- PHASE 15 SUCCESS ---")


if __name__ == "__main__":
    perform_surgery()
