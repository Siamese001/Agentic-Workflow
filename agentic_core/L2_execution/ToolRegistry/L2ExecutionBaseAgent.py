from __future__ import annotations

"""
[PHASE 17 REFACTOR] Unified L2 Execution Base Agent.
STRICT COMPLIANCE: SovereignBaseAgent Native. No Vendor SDKs.
"""
import re
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

load_dotenv()


def get_subatomic_engine() -> Any:
    from agentic_core.L3_orchestration.fission_logic.subatomic_engine import SubAtomicEngineImpl

    return SubAtomicEngineImpl()


@dataclass
class L2ExecutionBaseAgent(SovereignBaseAgent):
    """Unified L2 base class - Phase 17 Hardened."""

    ctx: Any
    enable_gemini: bool = True
    _cache_prefix: str = "l2_execution"
    _namespace: str = "l2_tools"
    name: str = field(init=False)
    role: str = field(init=False)
    _subatomic_engine: Any | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not hasattr(self, "name") or not self.name:
            self.name = self.__class__.__name__
        self.role = re.sub("(?<!^)(?=[A-Z])", "_", self.name).lower()
        if self.enable_gemini:
            try:
                self._subatomic_engine = get_subatomic_engine()
            except Exception:
                pass

    def can_run(self) -> bool:
        return "CRITICAL_FAIL" not in getattr(self.ctx, "signals", [])

    async def run_with_broadcast(self) -> Any:
        self.ctx._current_agent = self.name
        return await self.execute()

    @abstractmethod
    async def execute(self) -> Any:
        raise NotImplementedError()

    def get_validation_keys(self) -> list[int]:
        return []

    def act(self, plan: list[str]) -> dict[str, Any]:
        return {"status": "act_placeholder"}

    @timeout(300)
    def heal_repository(self, **kwargs) -> dict[str, int]:
        return super().heal_repository(**kwargs)
