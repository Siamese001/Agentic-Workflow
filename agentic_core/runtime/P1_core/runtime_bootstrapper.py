import logging
from typing import Any, Optional, Protocol, Dict, List

# THE SOVEREIGN IMPORTS: This is the ONLY file that can reach across all layers.
from agentic_core.L0_maintenance.logs.telemetry_recorder import TelemetryRecorder
from agentic_core.L1_cognition.thought_engine.structured_engine import StructuredEngine
from agentic_core.L1_cognition.boundaries.semantic_gatekeeper import SemanticGatekeeper
from agentic_core.L2_execution.action_handlers.sandbox import DockerSandbox
from agentic_core.L2_execution.tool_registry.mcp_manager import MCPConnectionManager
from agentic_core.L3_orchestration.fission_logic.fission_manager import FissionManager
from agentic_core.L3_orchestration.workflow_engines.supreme_court import SupremeCourt
from agentic_core.L4_state.session_manager.disk_adapter import LocalDiskAdapter
from agentic_core.L4_state.audit_trails.genealogy import GenealogyRegistry
from agentic_core.L5_safety.guardrails.pii_vault import PIIVault
from agentic_core.L5_safety.guardrails.membrane import InputMembrane
from agentic_core.L5_safety.guardrails.airlock import AirlockProtocol
from agentic_core.L5_safety.validators.cost_governor import CostGovernor
from agentic_core.L5_safety.validators.constitutional_overseer import ConstitutionalOverseer
from agentic_core.runtime.P1_core.subatomic_hop import SubatomicHop

LOGGER = logging.getLogger(__name__)

class RuntimeBootstrapper:
    """
    The Sovereign Assembler.
    Responsible for instantiating the 13 Pillars and injecting them into the Hop.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._registry = {} # Singleton cache for heavy runtime objects

    def assemble_hop(self, role: str) -> SubatomicHop:
        """Assembles a 100% Gravity-Compliant Hop with all 13 injected tools."""
        LOGGER.info(f"Bootstrapper: Assembling Sovereign Hop for role -> {role}")

        return SubatomicHop(
            role=role,
            config=self.config,
            # L0: Monitoring
            telemetry=self._get_tool("telemetry", lambda: TelemetryRecorder(self.config)),
            # L1: Cognition
            structured_engine=self._get_tool("engine", lambda: StructuredEngine(self.config)),
            gatekeeper=self._get_tool("gatekeeper", lambda: SemanticGatekeeper(self.config)),
            # L2: Execution
            sandbox=self._get_tool("sandbox", lambda: DockerSandbox(self.config)),
            mcp_manager=self._get_tool("mcp", lambda: MCPConnectionManager(self.config)),
            # L3: Orchestration
            supreme_court=self._get_tool("court", lambda: SupremeCourt(self.config)),
            # L4: State
            storage=self._get_tool("storage", lambda: LocalDiskAdapter(self.config)),
            genealogy=self._get_tool("genealogy", lambda: GenealogyRegistry(self.config)),
            # L5: Safety (The Shield)
            pii_vault=self._get_tool("pii", lambda: PIIVault(self.config)),
            membrane=self._get_tool("membrane", lambda: InputMembrane(self.config)),
            airlock=self._get_tool("airlock", lambda: AirlockProtocol(self.config)),
            cost_governor=self._get_tool("governor", lambda: CostGovernor(self.config)),
            overseer=self._get_tool("overseer", lambda: ConstitutionalOverseer(self.config))
        )

    def _get_tool(self, key: str, constructor_func) -> Any:
        if key not in self._registry:
            self._registry[key] = constructor_func()
        return self._registry[key]