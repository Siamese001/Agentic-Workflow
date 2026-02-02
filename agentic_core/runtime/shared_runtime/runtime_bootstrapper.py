from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_maintenance.logs.TelemetryRecorder import TelemetryRecorder
from agentic_core.L1_cognition.boundaries.semantic_gatekeeper_validator import semantic_gatekeeper
from agentic_core.L1_cognition.thought_engine.StructuredEngine import StructuredEngine
from agentic_core.L2_execution.action_handlers.sandbox import DockerSandbox
from agentic_core.L2_execution.tool_registry.mcp_manager import MCPConnectionManager

# ARCHIVED IMPORT REMOVED - dependency no longer available
from agentic_core.L3_orchestration.workflow_engines.SupremeCourt import SupremeCourt
from agentic_core.L4_state.audit_trails.genealogy import GenealogyRegistry
from agentic_core.L4_state.session_manager.disk_adapter import LocalDiskAdapter
from agentic_core.L5_safety.guardrails.airlock import AirlockProtocol
from agentic_core.L5_safety.guardrails.membrane import InputMembrane
from agentic_core.L5_safety.guardrails.PiiVault import PIIVault
from agentic_core.L5_safety.validators.constitutional_overseer_validator import ConstitutionalOverseer
from agentic_core.L5_safety.validators.cost_governor_validator import CostGovernor
from agentic_core.runtime.P1_core.SubatomicHop import SubatomicHop

# [SSOT IMPORT] Structure blueprint is the single source of truth

Logger: Any = logging.getLogger(__name__)


class runtime_bootstrapper:
    """
    The Sovereign Assembler.
    Responsible for instantiating the 13 Pillars and injecting them into the Hop.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._registry = {}

    def assemble_hop(self, role: str) -> SubatomicHop:
        """Assembles a 100% Gravity-Compliant Hop with all 13 injected tools."""
        LOGGER.info(f"Bootstrapper: Assembling Sovereign Hop for role -> {role}")
        return SubatomicHop(
            role=role,
            config=self.config,
            telemetry=self._get_tool("telemetry", lambda: TelemetryRecorder(self.config)),
            StructuredEngine=self._get_tool("engine", lambda: StructuredEngine(self.config)),
            gatekeeper=self._get_tool("gatekeeper", lambda: semantic_gatekeeper(self.config)),
            sandbox=self._get_tool("sandbox", lambda: DockerSandbox(self.config)),
            mcp_manager=self._get_tool("mcp", lambda: MCPConnectionManager(self.config)),
            SupremeCourt=self._get_tool("court", lambda: SupremeCourt(self.config)),
            storage=self._get_tool("storage", lambda: LocalDiskAdapter(self.config)),
            genealogy=self._get_tool("genealogy", lambda: GenealogyRegistry(self.config)),
            PiiVault=self._get_tool("pii", lambda: PIIVault(self.config)),
            membrane=self._get_tool("membrane", lambda: InputMembrane(self.config)),
            airlock=self._get_tool("airlock", lambda: AirlockProtocol(self.config)),
            CostGovernor=self._get_tool("governor", lambda: CostGovernor(self.config)),
            overseer=self._get_tool("overseer", lambda: ConstitutionalOverseer(self.config)),
        )

    def _get_tool(self, key: str, constructor_func) -> Any:
        if key not in self._registry:
            self._registry[key] = constructor_func()
        return self._registry[key]
