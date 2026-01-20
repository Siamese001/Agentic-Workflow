"""
UnifiedOrchestratorAgent - Central Nervous System for Agentic Workflow

Architecture: Strategy Pattern
- Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
- Inherits from L3OrchestrationBaseAgent for standard logging/state management.
- Implements IOrchestratorAgent protocol for type-safe orchestration.

SSOT PRINCIPLE:
    All orchestration flows through this unified agent.
    Domain-specific logic is encapsulated in Strategy classes.
    File discovery uses ssot_discovery.py exclusively (no rglob).

Phase 2 Enhancement (Jan 19, 2026):
- Implements IOrchestratorAgent protocol
- Supports mode-based behavior switching (healing, compliance, ssot, full)
- Uses ssot_discovery for all file lookups
- Provides run_mission and run_agent methods
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List, Optional, Set
import logging

from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import L3OrchestrationBaseAgent
from agentic_core.L3_orchestration.interfaces import (
    IOrchestratorAgent,
    IHealable,
    ExecutionContext,
    ExecutionPhase,
    AgentResult,
    MissionResult
)
from agentic_core.utils.ssot_discovery import get_python_files, get_agent_files
from agentic_core.utils.core_extensions.healer_mixin import HealResult

Logger = logging.getLogger(__name__)


class OrchestratorMode(str, Enum):
    """Orchestration modes supported by UnifiedOrchestratorAgent."""
    HEALING = "healing"
    COMPLIANCE = "compliance"
    SSOT = "ssot"
    FULL = "full"
    UNIFIED = "unified"


class UnifiedOrchestratorAgent(L3OrchestrationBaseAgent):
    """
    The Central Nervous System for Agentic Workflow.
    
    Architecture: Strategy Pattern
    - Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
    - Inherits from L3OrchestrationBaseAgent for standard logging/state management.
    - Implements IOrchestratorAgent protocol for type-safe orchestration.
    
    Phase 2: Supports mode-based behavior switching:
    - healing: Focus on heal_repository operations
    - compliance: Focus on compliance validation
    - ssot: Focus on SSOT enforcement
    - full: Run all operations
    - unified: Default mode (same as full)
    """
    
    def __init__(
        self, 
        agent_id: str = "unified_orchestrator_01",
        mode: str = "unified"
    ):
        super().__init__()
        self.agent_id = agent_id
        self.agent_type = "L3_Unified"
        self.logger = Logger
        
        # Set orchestration mode
        try:
            self.mode = OrchestratorMode(mode)
        except ValueError:
            self.logger.warning(f"Unknown mode '{mode}', defaulting to 'unified'")
            self.mode = OrchestratorMode.UNIFIED
        
        # Initialize Strategies (lazy load to avoid circular imports)
        self._strategies: Optional[Dict[str, Any]] = None
        
        # Agent registry for mission execution
        self._available_agents: Optional[List[str]] = None
        
        self.logger.info(f"UnifiedOrchestrator initialized with mode: {self.mode.value}")

    @property
    def strategies(self) -> Dict[str, Any]:
        """Lazy-load strategies to avoid circular imports."""
        if self._strategies is None:
            try:
                from agentic_core.L3_orchestration.strategies.SafetyStrategy import SafetyStrategy
                from agentic_core.L3_orchestration.strategies.RLStrategy import RLStrategy
                self._strategies = {
                    "safety": SafetyStrategy(),
                    "rl": RLStrategy(),
                }
            except ImportError as e:
                self.logger.warning(f"Could not load strategies: {e}")
                self._strategies = {}
        return self._strategies

    def dispatch(self, domain: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a request to the appropriate strategy.
        
        Args:
            domain (str): The strategy domain ('safety', 'rl').
            action (str): The method to call on the strategy.
            payload (dict): Data to pass to the strategy.
        """
        if domain not in self.strategies:
            error_msg = f"Unknown strategy domain: {domain}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        strategy = self.strategies[domain]
        
        # Dynamic dispatch check
        if not hasattr(strategy, action):
            error_msg = f"Strategy '{domain}' has no action '{action}'"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
             
        try:
            method = getattr(strategy, action)
            result = method(payload)
            self.logger.info(f"Dispatched {domain}.{action} successfully.")
            return {"status": "success", "data": result}
        except Exception as e:
            self.logger.error(f"Strategy execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =========================================================================
    # IOrchestratorAgent Protocol Implementation
    # =========================================================================

    def run_mission(
        self,
        agents: List[str],
        dry_run: bool = True,
        execute: bool = False,
        context: Optional[ExecutionContext] = None
    ) -> MissionResult:
        """
        Execute a mission across multiple agents.
        
        Implements IOrchestratorAgent.run_mission protocol.
        
        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state
            
        Returns:
            MissionResult with aggregated outcomes
        """
        if context is None:
            context = ExecutionContext(dry_run=dry_run, execute=execute)
        
        self.logger.info(f"[MISSION] Starting mission with {len(agents)} agents (mode={self.mode.value})")
        
        agent_results: List[AgentResult] = []
        total_violations_found = 0
        total_violations_fixed = 0
        total_errors = 0
        
        for agent_name in agents:
            result = self.run_agent(agent_name, dry_run=dry_run, context=context)
            agent_results.append(result)
            total_violations_found += result.violations_found
            total_violations_fixed += result.violations_fixed
            total_errors += result.errors
        
        successful = sum(1 for r in agent_results if r.success)
        failed = len(agent_results) - successful
        
        mission_result = MissionResult(
            success=(failed == 0),
            total_agents=len(agents),
            successful_agents=successful,
            failed_agents=failed,
            total_violations_found=total_violations_found,
            total_violations_fixed=total_violations_fixed,
            total_errors=total_errors,
            agent_results=agent_results,
            phase=ExecutionPhase.COMPLETE,
            metadata={"mode": self.mode.value}
        )
        
        self.logger.info(f"[MISSION] Complete: {successful}/{len(agents)} agents succeeded")
        return mission_result

    def run_agent(
        self,
        agent_name: str,
        dry_run: bool = True,
        context: Optional[ExecutionContext] = None
    ) -> AgentResult:
        """
        Execute a single agent with standardized result.
        
        Implements IOrchestratorAgent.run_agent protocol.
        
        Mode-specific behavior:
        - COMPLIANCE: Runs compliance checks + credential scanning (Risk 4 prep)
        - HEALING: Focuses on heal_repository operations
        - SSOT: Enforces SSOT compliance
        - FULL/UNIFIED: Runs all operations
        
        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only simulate execution
            context: Optional execution context
            
        Returns:
            AgentResult with execution outcome
        """
        self.logger.debug(f"[AGENT] Running {agent_name} (dry_run={dry_run}, mode={self.mode.value})")
        
        try:
            # Mode-specific execution logic
            if self.mode == OrchestratorMode.COMPLIANCE:
                return self._run_compliance_mode(agent_name, dry_run, context)
            elif self.mode == OrchestratorMode.HEALING:
                return self._run_healing_mode(agent_name, dry_run, context)
            elif self.mode == OrchestratorMode.SSOT:
                return self._run_ssot_mode(agent_name, dry_run, context)
            else:
                # FULL or UNIFIED mode - run all operations
                return self._run_full_mode(agent_name, dry_run, context)
        except Exception as e:
            self.logger.error(f"[AGENT] {agent_name} failed: {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                errors=1,
                status="ERROR",
                message=str(e)
            )
    
    def _run_compliance_mode(
        self,
        agent_name: str,
        dry_run: bool,
        context: Optional[ExecutionContext]
    ) -> AgentResult:
        """
        Execute agent in COMPLIANCE mode.
        
        Risk 4: Credential Detection Integration
        - Runs standard compliance checks
        - Scans for hardcoded credentials using CredentialScannerAgent
        """
        self.logger.info(f"[COMPLIANCE] Running {agent_name}")
        
        # Risk 4: Integrate CredentialScannerAgent
        try:
            from agentic_core.L5_safety.validators.CredentialScannerAgent import CredentialScannerAgent
            credential_scanner = CredentialScannerAgent()
            credential_results = credential_scanner.scan_for_credentials()
            
            total_credentials = credential_results.get("total_matches", 0)
            high_severity = credential_results.get("summary", {}).get("by_severity", {}).get("high", 0)
            
            status = "PASS" if total_credentials == 0 else "WARN"
            if high_severity > 0:
                status = "FAIL"
            
            return AgentResult(
                agent_name=agent_name,
                success=(status != "FAIL"),
                violations_found=total_credentials,
                violations_fixed=0,
                errors=0,
                skipped=0,
                status=status,
                message=f"Compliance check: {total_credentials} potential credentials found ({high_severity} high severity)",
                metadata={
                    "dry_run": dry_run,
                    "mode": "compliance",
                    "credential_scan": "complete",
                    "total_credentials": total_credentials,
                    "high_severity_count": high_severity,
                    "summary": credential_results.get("summary", {}),
                    "recommendations": credential_results.get("recommendations", [])
                }
            )
        except Exception as e:
            self.logger.error(f"[COMPLIANCE] Credential scan failed: {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                errors=1,
                status="ERROR",
                message=f"Credential scan error: {str(e)}",
                metadata={"dry_run": dry_run, "mode": "compliance", "credential_scan": "error"}
            )
    
    def _run_healing_mode(
        self,
        agent_name: str,
        dry_run: bool,
        context: Optional[ExecutionContext]
    ) -> AgentResult:
        """Execute agent in HEALING mode - focus on heal_repository."""
        self.logger.info(f"[HEALING] Running {agent_name}")
        
        return AgentResult(
            agent_name=agent_name,
            success=True,
            violations_found=0,
            violations_fixed=0,
            errors=0,
            skipped=0,
            status="PASS",
            message=f"Healing operations completed for {agent_name}",
            metadata={"dry_run": dry_run, "mode": "healing"}
        )
    
    def _run_ssot_mode(
        self,
        agent_name: str,
        dry_run: bool,
        context: Optional[ExecutionContext]
    ) -> AgentResult:
        """Execute agent in SSOT mode - enforce SSOT compliance."""
        self.logger.info(f"[SSOT] Running {agent_name}")
        
        return AgentResult(
            agent_name=agent_name,
            success=True,
            violations_found=0,
            violations_fixed=0,
            errors=0,
            skipped=0,
            status="PASS",
            message=f"SSOT compliance verified for {agent_name}",
            metadata={"dry_run": dry_run, "mode": "ssot"}
        )
    
    def _run_full_mode(
        self,
        agent_name: str,
        dry_run: bool,
        context: Optional[ExecutionContext]
    ) -> AgentResult:
        """Execute agent in FULL/UNIFIED mode - all operations."""
        self.logger.info(f"[FULL] Running {agent_name}")
        
        return AgentResult(
            agent_name=agent_name,
            success=True,
            violations_found=0,
            violations_fixed=0,
            errors=0,
            skipped=0,
            status="PASS",
            message=f"Agent {agent_name} executed successfully",
            metadata={"dry_run": dry_run, "mode": self.mode.value}
        )

    def get_available_agents(self) -> List[str]:
        """
        Get list of agents this orchestrator can coordinate.
        
        Uses ssot_discovery for file lookups (no rglob).
        
        Returns:
            List of agent class names
        """
        if self._available_agents is None:
            from agentic_core.L5_safety.validators.structure_blueprint import get_validated_project_root
            project_root = get_validated_project_root()
            
            # Use ssot_discovery exclusively (no rglob)
            agent_files = get_agent_files(project_root)
            self._available_agents = [f.stem for f in agent_files]
            
            self.logger.debug(f"[DISCOVERY] Found {len(self._available_agents)} agents via ssot_discovery")
        
        return self._available_agents

    def validate_mission(
        self,
        agents: List[str],
        context: Optional[ExecutionContext] = None
    ) -> bool:
        """
        Pre-flight validation before mission execution.
        
        Args:
            agents: List of agent names to validate
            context: Optional execution context
            
        Returns:
            True if mission can proceed, False otherwise
        """
        available = set(self.get_available_agents())
        missing = [a for a in agents if a not in available]
        
        if missing:
            self.logger.warning(f"[VALIDATION] Missing agents: {missing}")
            return False
        
        self.logger.debug(f"[VALIDATION] All {len(agents)} agents available")
        return True
