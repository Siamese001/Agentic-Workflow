import logging
from typing import Dict, Any

# Standardizing our L5 Safety Imports
from agentic_core.L5_safety.guardrails.membrane import InputMembrane
from agentic_core.L5_safety.guardrails.airlock import AirlockProtocol
# ... previous imports (Telemetry, Storage, etc.) remain ...
from agentic_core.L0_maintenance.logs.telemetry_recorder import TelemetryRecorder
from agentic_core.L1_cognition.thought_engine.structured_engine import StructuredEngine
from agentic_core.L2_execution.action_handlers.sandbox import DockerSandbox
from agentic_core.L2_execution.tool_registry.mcp_manager import MCPConnectionManager
from agentic_core.L3_orchestration.fission_logic.fission_manager import FissionManager
from agentic_core.L4_state.validation_context.audit_trails import GenealogyRegistry
from agentic_core.L4_state.session_manager.disk_adapter import LocalDiskAdapter
from agentic_core.L5_safety.guardrails.pii_vault import PIIVault
from agentic_core.L5_safety.validators.cost_governor import CostGovernor
from agentic_core.L5_safety.validators.constitutional_overseer import ConstitutionalOverseer

LOGGER = logging.getLogger(__name__)

class RuntimeBootstrapper:
    """
    The Sovereign Assembler.
    Updated to provide REAL L5 Safety Guardrails to the Runtime.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._registry = {}

    def assemble_hop(self, role: str) -> 'SubatomicHop':
        """Assembles a 100% compliant SubatomicHop with Real Safety Tools."""
        
        # We're pulling the 'Pure' class here to avoid circularity at the top level
        from agentic_core.runtime.P1_core.subatomic_hop import SubatomicHop

        return SubatomicHop(
            role=role,
            config=self.config,
            # Persistence & State (L4)
            storage=self._get_tool("storage", lambda: self._init_storage()),
            genealogy=self._get_tool("genealogy", lambda: self._init_genealogy()),
            
            # THE SHIELD: Real L5 Logic (No more mocks)
            membrane=self._get_tool("membrane", lambda: InputMembrane(self.config)),
            airlock=self._get_tool("airlock", lambda: AirlockProtocol(self.config)),
            
            # Security & Governance (L5)
            pii_vault=self._get_tool("pii", lambda: self._init_pii()),
            cost_governor=self._get_tool("governor", lambda: self._init_governor()),
            overseer=self._get_tool("overseer", lambda: self._init_overseer()),
            
            # The Rest of the Stack...
            sandbox=self._get_tool("sandbox", lambda: self._init_sandbox()),
            mcp_manager=self._get_tool("mcp", lambda: self._init_mcp()),
            structured_engine=self._get_tool("engine", lambda: self._init_engine()),
            telemetry=self._get_tool("telemetry", lambda: self._init_telemetry()),
            
            # Logic Anchors
            supreme_court=self.config.get("supreme_court_instance"), # Still L3
            gatekeeper=self.config.get("gatekeeper_instance")        # Still L1
        )

    def _get_tool(self, key: str, constructor_func) -> Any:
        if key not in self._registry:
            self._registry[key] = constructor_func()
        return self._registry[key]

    # ... [Internal init helpers for L0-L5 go here] ...
    def _init_storage(self):
        return LocalDiskAdapter(self.config)
    
    def _init_genealogy(self):
        return GenealogyRegistry(self.config)
    
    def _init_pii(self):
        return PIIVault(self.config)
    
    def _init_governor(self):
        return CostGovernor(self.config)
    
    def _init_overseer(self):
        return ConstitutionalOverseer(self.config)
    
    def _init_sandbox(self):
        return DockerSandbox(self.config)
    
    def _init_mcp(self):
        return MCPConnectionManager(self.config)
    
    def _init_engine(self):
        return StructuredEngine(self.config)
    
    def _init_telemetry(self):
        return TelemetryRecorder(self.config)
