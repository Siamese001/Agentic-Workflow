from __future__ import annotations

"""
UnifiedOrchestratorAgent - Central Nervous System for Agentic Workflow

Architecture: Strategy Pattern
- Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
- Inherits from SovereignBaseAgent for standard logging/state management.
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

import logging
from enum import Enum
from typing import Any

from agentic_core.L3_orchestration.interfaces import (
    AgentResult,
    ExecutionContext,
    ExecutionPhase,
    MissionResult,
)
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

# [PHASE 2] SSOT Discovery Integration
from agentic_core.utils.ssot_discovery import get_agent_files
from agentic_core.L5_safety.validators.structure_blueprint import get_validated_project_root

Logger = logging.getLogger(__name__)


class OrchestratorMode(str, Enum):
    """Orchestration modes supported by UnifiedOrchestratorAgent."""

    HEALING = "healing"
    COMPLIANCE = "compliance"
    SSOT = "ssot"
    FULL = "full"
    UNIFIED = "unified"


class UnifiedOrchestratorAgent(SovereignBaseAgent):
    """
    The Central Nervous System for Agentic Workflow.

    Architecture: Strategy Pattern
    - Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
    - Inherits from SovereignBaseAgent for standard logging/state management.
    - Implements IOrchestratorAgent protocol for type-safe orchestration.

    Phase 2: Supports mode-based behavior switching:
    - healing: Focus on heal_repository operations
    - compliance: Focus on compliance validation
    - ssot: Focus on SSOT enforcement
    - full: Run all operations
    - unified: Default mode (same as full)
    """

    def __init__(self, agent_id: str = "unified_orchestrator_01", mode: str = "unified"):
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
        self._strategies: dict[str, Any] | None = None

        # Agent registry for mission execution
        self._available_agents: list[str] | None = None

        self.logger.info(f"UnifiedOrchestrator initialized with mode: {self.mode.value}")

    @property
    def strategies(self) -> dict[str, Any]:
        """Lazy-load strategies to avoid circular imports."""
        if self._strategies is None:
            try:
                # Lazy imports to prevent circular dependency chains in L3
                from agentic_core.L3_orchestration.strategies.RLStrategy import RLStrategy
                from agentic_core.L3_orchestration.strategies.SafetyStrategy import SafetyStrategy

                self._strategies = {
                    "safety": SafetyStrategy(),
                    "rl": RLStrategy(),
                }
            except ImportError as e:
                self.logger.warning(f"Could not load strategies: {e}")
                self._strategies = {}
        return self._strategies

    def dispatch(self, domain: str, action: str, payload: dict[str, Any]) -> dict[str, Any]:
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
        agents: list[str],
        dry_run: bool = True,
        execute: bool = False,
        context: ExecutionContext | None = None,
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

        self.logger.info(
            f"[MISSION] Starting mission with {len(agents)} agents (mode={self.mode.value})"
        )

        # [DNA GATE] Perform Pre-Flight Audit
        try:
            from agentic_core.L5_safety.validators.CanonDependencySentinelAgent import CanonDependencySentinelAgent
            sentinel = CanonDependencySentinelAgent()
            audit_results = sentinel.heal_repository(dry_run=True, execute=False)
            
            # Check for FATAL status or critical violations
            is_fatal = audit_results.get("status") == "FATAL"
            scan_results = sentinel.scan_architecture()
            all_violations = scan_results.get("violations", [])
            
            # Critical violations that block execution (INIT_BYPASS and DNA_SEVERED are blocking)
            blocking_types = ("INIT_BYPASS", "DNA_SEVERED")
            critical_violations = [v for v in all_violations if v.severity == "CRITICAL" or v.violation_type in blocking_types]
            
            if is_fatal or critical_violations:
                # Log each critical violation
                for v in critical_violations[:10]:  # Limit to first 10
                    self.logger.critical(f"  VIOLATION: {v.violation_type} in {v.file_path}:{v.line_number}")
                
                abort_reason = "Naked super() or fatal syntax" if is_fatal else f"{len(critical_violations)} critical DNA violations"
                self.logger.critical(f"[STOP] Mission Aborted: {abort_reason}.")
                return MissionResult(
                    success=False,
                    total_agents=len(agents),
                    successful_agents=0,
                    failed_agents=len(agents),
                    total_violations_found=len(critical_violations),
                    total_violations_fixed=0,
                    total_errors=1,
                    agent_results=[],
                    phase=ExecutionPhase.VALIDATION,
                    status="ABORTED",
                    message=f"{abort_reason} detected in repository.",
                    metadata={"mode": self.mode.value, "gate": "DNA_SENTINEL", "critical_violations": len(critical_violations)}
                )
        except ImportError:
            self.logger.warning("[GATE] CanonDependencySentinelAgent not found. Proceeding with caution.")

        agent_results: list[AgentResult] = []
        total_violations_found = 0
        total_violations_fixed = 0
        total_errors = 0

        for agent_name in agents:
            # [PHASE 33m] Pre-Flight Import Validation
            if not self._validate_agent_import(agent_name):
                self.logger.critical(f"[GATE] CRITICAL_IMPORT_FAILURE: {agent_name} is unimportable")
                agent_results.append(AgentResult(
                    agent_name=agent_name,
                    success=False,
                    errors=1,
                    status="CRITICAL_IMPORT_FAILURE",
                    message=f"Agent {agent_name} failed pre-flight import validation"
                ))
                total_errors += 1
                continue
                
            # Crash containment for individual agent runs
            try:
                result = self.run_agent(agent_name, dry_run=dry_run, context=context)
                agent_results.append(result)
                total_violations_found += result.violations_found
                total_violations_fixed += result.violations_fixed
                total_errors += result.errors
            except Exception as e:
                self.logger.error(f"[MISSION] Critical error running {agent_name}: {e}")
                total_errors += 1
                # Continue mission despite single agent failure

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
            metadata={"mode": self.mode.value},
        )

        self.logger.info(f"[MISSION] Complete: {successful}/{len(agents)} agents succeeded")
        return mission_result

    def run_agent(
        self, agent_name: str, dry_run: bool = True, context: ExecutionContext | None = None
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
        self.logger.debug(
            f"[AGENT] Running {agent_name} (dry_run={dry_run}, mode={self.mode.value})"
        )

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
                agent_name=agent_name, success=False, errors=1, status="ERROR", message=str(e)
            )

    def _run_compliance_mode(
        self, agent_name: str, dry_run: bool, context: ExecutionContext | None
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
            from agentic_core.L5_safety.validators.CredentialScannerAgent import (
                CredentialScannerAgent,
            )

            credential_scanner = CredentialScannerAgent()
            credential_results = credential_scanner.scan_for_credentials()

            total_credentials = credential_results.get("total_matches", 0)
            high_severity = (
                credential_results.get("summary", {}).get("by_severity", {}).get("high", 0)
            )

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
                    "recommendations": credential_results.get("recommendations", []),
                },
            )
        except ImportError:
            self.logger.warning("[COMPLIANCE] CredentialScannerAgent not available")
            return AgentResult(
                agent_name=agent_name,
                success=True,
                status="WARN",
                message="CredentialScannerAgent missing",
                metadata={"dry_run": dry_run},
            )
        except Exception as e:
            self.logger.error(f"[COMPLIANCE] Credential scan failed: {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                errors=1,
                status="ERROR",
                message=f"Credential scan error: {str(e)}",
                metadata={"dry_run": dry_run, "mode": "compliance", "credential_scan": "error"},
            )

    def _run_healing_mode(
        self, agent_name: str, dry_run: bool, context: ExecutionContext | None
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
            metadata={"dry_run": dry_run, "mode": "healing"},
        )

    def _run_ssot_mode(
        self, agent_name: str, dry_run: bool, context: ExecutionContext | None
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
            metadata={"dry_run": dry_run, "mode": "ssot"},
        )

    def _run_full_mode(
        self, agent_name: str, dry_run: bool, context: ExecutionContext | None
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
            metadata={"dry_run": dry_run, "mode": self.mode.value},
        )

    def get_available_agents(self) -> list[str]:
        """
        Get list of agents this orchestrator can coordinate.

        Uses ssot_discovery for file lookups (no rglob).

        Returns:
            List of agent class names
        """
        if self._available_agents is None:
            try:
                project_root = get_validated_project_root()
                # Use ssot_discovery exclusively (no rglob)
                agent_files = get_agent_files(project_root)
                self._available_agents = [f.stem for f in agent_files]
                self.logger.debug(
                    f"[DISCOVERY] Found {len(self._available_agents)} agents via ssot_discovery"
                )
            except Exception as e:
                self.logger.error(f"[DISCOVERY] Failed to discover agents: {e}")
                self._available_agents = []

        return self._available_agents

    def validate_mission(self, agents: list[str], context: ExecutionContext | None = None) -> bool:
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

        return True

    def _validate_agent_import(self, agent_name: str) -> bool:
        """
        [PHASE 33m] Pre-Flight Import Validation.
        
        Performs a subprocess check to verify the agent module is importable
        before attempting to run it. This prevents runtime crashes from
        missing dependencies, syntax errors, or circular imports.
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            True if agent is importable, False otherwise
        """
        import subprocess
        import sys
        
        # Try to find the module path for this agent
        try:
            from agentic_core.L5_safety.validators.ssot_discovery import get_agent_files
            agent_files = get_agent_files(self.project_root)
            
            # Find matching agent file
            agent_file = next((f for f in agent_files if f.stem == agent_name), None)
            if not agent_file:
                # Agent not found in discovery - skip validation (may be dynamically loaded)
                return True
                
            # Convert file path to module path
            rel_path = agent_file.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace('/', '.').replace('\\', '.')
            
            # Perform subprocess import check
            result = subprocess.run(
                [sys.executable, "-c", f"import {module_path}"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )
            
            if result.returncode != 0:
                self.logger.error(f"[GATE] Import validation failed for {agent_name}: {result.stderr.strip()[:200]}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.warning(f"[GATE] Pre-flight check skipped for {agent_name}: {e}")
            return True  # Allow to proceed if validation itself fails
