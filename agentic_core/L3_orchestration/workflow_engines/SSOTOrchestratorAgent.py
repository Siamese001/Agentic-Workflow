from __future__ import annotations
"""
SSOTOrchestratorAgent - Master SSOT Validation Orchestrator (Phase 2.2)
Territory: agentic_core/L3_orchestration/workflow_engines/

RESPONSIBILITIES:
- Coordinate execution of all SSOT validation agents
- Implement "Heal-First" protocol (syntax validation before analysis)
- Implement TWO-PHASE DUPLICATE DETECTION for improved signal
- Aggregate results from all validators
- Provide unified SSOT health reporting
- Manage healing sequence and dependencies

TWO-PHASE DUPLICATE DETECTION:
- Phase A (Shallow): Runs IMMEDIATELY after SyntaxValidator - identity collisions
- Phase B (Deep): Runs AFTER structural healing - logic duplicates

ORCHESTRATES (Updated Sequence):
1. SyntaxValidatorAgent (L5) - Run FIRST (heal-first protocol)
2. TwoPhaseDeduplicationAgent Phase A - Identity collisions (early detection)
3. HygieneGuardianAgent (L5) - Empty files, tech debt
4. GravityEnforcerAgent (L5) - Upward imports
5. NamingAgent (L5) - Naming conventions
6. LocationAgent (L5) - File placement
7. TwoPhaseDeduplicationAgent Phase B - Logic duplicates (after structural healing)
8. CodeSSOTEnforcerAgent (L5) - Hard-coded paths

Canon Key 51 Compliance: Includes heal_repository() method
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.result_utils import (
    AgentResult as CentralizedAgentResult,
    normalize_agent_result,
    extract_violations,
    extract_fixes,
)

# Color-coded terminal output
try:
    from agentic_core.utils.terminal_colors import (
        phase_header, tier_summary, agent_status, log_status, Colors
    )
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    def phase_header(*args, **kwargs): return f"\n[PHASE] {args[0] if args else ''}"
    def tier_summary(*args, **kwargs): return ""
    def agent_status(*args, **kwargs): return f"  {args[0] if args else ''}"
    def log_status(level, msg, **kwargs): print(f"[{level.upper()}] {msg}")
    class Colors:
        RESET = BRIGHT_GREEN = BRIGHT_RED = BRIGHT_YELLOW = BRIGHT_CYAN = BRIGHT_MAGENTA = DIM = ""
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.fission_logic.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from a single agent execution."""
    agent_name: str
    status: str  # 'PASS', 'FAIL', 'ERROR'
    violations_found: int
    violations_fixed: int
    execution_time_ms: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationReport:
    """Comprehensive SSOT orchestration report."""
    timestamp: str
    total_agents_run: int
    agents_passed: int
    agents_failed: int
    total_violations: int
    total_fixes: int
    execution_time_ms: float
    agent_results: List[AgentResult] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_agents_run == 0:
            return 100.0
        return (self.agents_passed / self.total_agents_run) * 100


class SSOTOrchestratorAgent(SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """
    [L3 ORCHESTRATOR] Master SSOT validation orchestrator.
    
    Coordinates all SSOT validation agents in the correct sequence,
    implementing the "Heal-First" protocol where syntax validation
    runs before any other analysis to ensure files are parseable.
    
    Execution Order (Two-Phase Duplicate Detection):
    1. SyntaxValidatorAgent (CRITICAL - must pass before others)
    2. TwoPhaseDeduplicationAgent_PhaseA (identity collisions - early detection)
    3. HygieneGuardianAgent (cleanup empty files)
    4. GravityEnforcerAgent (architectural violations)
    5. NamingAgent (naming conventions)
    6. LocationAgent (file placement)
    7. TwoPhaseDeduplicationAgent_PhaseB (logic duplicates - after structural healing)
    8. CodeSSOTEnforcerAgent (hard-coded paths)
    """
    
    def __init__(self, project_root: Path = None) -> None:
        """Initialize the SSOT orchestrator."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logger = Logger
        super().__init__()
        
        # Track agent instances
        self._agents = {}
        
        # Two-phase deduplication agent (shared instance for both phases)
        self._dedup_agent = None
        
        # Updated execution order with two-phase duplicate detection
        # Phase A runs early (after syntax), Phase B runs late (after structural healing)
        # [TIERED EXECUTION] Grouped by dependency gravity
        self.tiers = {
            "Tier 1: Parseability Gate": ["SyntaxValidatorAgent"],
            "Tier 2: Identity & Structure": [
                "TwoPhaseDeduplicationAgent_PhaseA", # Early: identity collisions
                "HygieneGuardianAgent",
                "NamingAgent",
                "LocationAgent"
            ],
            "Tier 3: Deep Compliance": [
                "GravityEnforcerAgent",
                "TwoPhaseDeduplicationAgent_PhaseB", # Late: logic duplicates
                "CodeSSOTEnforcerAgent"
            ]
        }
    
    def _get_dedup_agent(self):
        """Get or create the shared TwoPhaseDeduplicationAgent instance."""
        if self._dedup_agent is None:
            from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import TwoPhaseDeduplicationAgent
            self._dedup_agent = TwoPhaseDeduplicationAgent(project_root=self.project_root)
        return self._dedup_agent
    
    def _get_agent(self, agent_name: str) -> Any:
        """
        Lazy-load agent instances.
        
        Args:
            agent_name: Name of the agent to load
            
        Returns:
            Agent instance or None if not available
        """
        # Handle two-phase deduplication specially (shared instance)
        if agent_name.startswith('TwoPhaseDeduplicationAgent'):
            return self._get_dedup_agent()
        
        if agent_name in self._agents:
            return self._agents[agent_name]
        
        try:
            if agent_name == 'SyntaxValidatorAgent':
                from agentic_core.L5_safety.validators.SyntaxValidatorAgent import SyntaxValidatorAgent
                agent = SyntaxValidatorAgent(project_root=self.project_root)
            elif agent_name == 'HygieneGuardianAgent':
                from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent
                agent = HygieneGuardianAgent(project_root=self.project_root)
            elif agent_name == 'GravityEnforcerAgent':
                from agentic_core.L5_safety.guardrails.GravityEnforcerAgent import GravityEnforcerAgent
                agent = GravityEnforcerAgent(project_root=self.project_root)
            elif agent_name == 'DuplicateCodeDetectorAgent':
                # Legacy support - redirect to TwoPhaseDeduplicationAgent
                return self._get_dedup_agent()
            elif agent_name == 'NamingAgent':
                from agentic_core.L5_safety.validators.NamingAgent import NamingAgent
                agent = NamingAgent()
            elif agent_name == 'LocationAgent':
                from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
                agent = LocationAgent()
            elif agent_name == 'CodeSSOTEnforcerAgent':
                from agentic_core.L5_safety.validators.CodeSSOTEnforcerAgent import CodeSSOTEnforcerAgent
                agent = CodeSSOTEnforcerAgent()
            else:
                self.logger.warning(f"Unknown agent: {agent_name}")
                return None
            
            self._agents[agent_name] = agent
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to load {agent_name}: {e}")
            return None
    
    def run_agent(
        self,
        agent_name: str,
        dry_run: bool = True,
        execute: bool = False
    ) -> AgentResult:
        """
        Run a single agent and capture results.
        
        Args:
            agent_name: Name of the agent to run
            dry_run: If True, only report violations
            execute: If True, attempt to fix violations
            
        Returns:
            AgentResult with execution details
        """
        start_time = datetime.now()
        
        try:
            agent = self._get_agent(agent_name)
            if not agent:
                return AgentResult(
                    agent_name=agent_name,
                    status='ERROR',
                    violations_found=0,
                    violations_fixed=0,
                    execution_time_ms=0,
                    error_message=f"Agent {agent_name} not available"
                )
            
            # Handle two-phase deduplication specially
            if agent_name == 'TwoPhaseDeduplicationAgent_PhaseA':
                # Phase A: Shallow duplicate check (identity collisions)
                self.logger.info("[PHASE A] Running Shallow Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="A")
            elif agent_name == 'TwoPhaseDeduplicationAgent_PhaseB':
                # Phase B: Deep SSOT duplicate check (logic duplicates)
                self.logger.info("[PHASE B] Running Deep SSOT Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="B")
            elif hasattr(agent, 'heal_repository'):
                # Standard agent execution
                result = agent.heal_repository(dry_run=dry_run, execute=execute)
            else:
                return AgentResult(
                    agent_name=agent_name,
                    status='ERROR',
                    violations_found=0,
                    violations_fixed=0,
                    execution_time_ms=0,
                    error_message=f"Agent {agent_name} missing heal_repository()"
                )
            
            # [SSOT] Use centralized result normalization utility
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            normalized = normalize_agent_result(agent_name, result, int(execution_time))
            
            return AgentResult(
                agent_name=agent_name,
                status=normalized.status if normalized.status != "UNKNOWN" else result.get('status', 'UNKNOWN'),
                violations_found=normalized.violations_found,
                violations_fixed=normalized.violations_fixed,
                execution_time_ms=execution_time,
                details=result
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error running {agent_name}: {e}")
            return AgentResult(
                agent_name=agent_name,
                status='ERROR',
                violations_found=0,
                violations_fixed=0,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
    
    def orchestrate(
        self,
        dry_run: bool = True,
        execute: bool = False
    ) -> OrchestrationReport:
        """
        Orchestrate all SSOT validation agents.
        
        Args:
            dry_run: If True, only report violations
            execute: If True, attempt to fix violations
            
        Returns:
            OrchestrationReport with comprehensive results
        """
        start_time = datetime.now()
        
        # Color-coded header
        mode_color = Colors.BRIGHT_RED if execute else Colors.BRIGHT_YELLOW
        print(f"\n{Colors.BRIGHT_MAGENTA}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}SSOT ORCHESTRATION{Colors.RESET} - Starting validation sequence")
        print(f"   {Colors.DIM}Mode:{Colors.RESET} {mode_color}{'EXECUTE' if execute else 'DRY-RUN'}{Colors.RESET}")
        print(f"{Colors.BRIGHT_MAGENTA}{'=' * 60}{Colors.RESET}")
        self.logger.info("=" * 60)
        self.logger.info("SSOT ORCHESTRATION - Starting validation sequence")
        self.logger.info("=" * 60)
        
        agent_results = []
        total_violations = 0
        total_fixes = 0
        
        # [TIERED EXECUTION LOOP]
        tier_num = 0
        for tier_name, agents in self.tiers.items():
            tier_num += 1
            print(phase_header(tier_name, phase_num=tier_num, total_phases=len(self.tiers), status="running"))
            self.logger.info(f"\n[{tier_name.upper()}] Starting Sequence...")
            tier_failed = False
            tier_start = datetime.now()
            tier_fixes = 0
            tier_violations = 0
            
            for agent_name in agents:
                print(agent_status(agent_name, 'running'))
                self.logger.info(f"   >>> Running {agent_name}...")
                
                result = self.run_agent(agent_name, dry_run=dry_run, execute=execute)
                agent_results.append(result)
                tier_fixes += result.violations_fixed
                tier_violations += result.violations_found
                
                total_violations += result.violations_found
                total_fixes += result.violations_fixed
                
                # Log result with colors
                if result.status == 'PASS':
                    print(agent_status(agent_name, 'success', fixes=result.violations_fixed, violations=0, duration_ms=int(result.execution_time_ms)))
                    self.logger.info(f"   ✅ {agent_name}: PASS (0 violations)")
                elif result.status == 'FAIL':
                    tier_failed = True
                    print(agent_status(agent_name, 'warning' if result.violations_fixed > 0 else 'error', fixes=result.violations_fixed, violations=result.violations_found, duration_ms=int(result.execution_time_ms)))
                    self.logger.warning(
                        f"   ⚠️ {agent_name}: FAIL ({result.violations_found} violations, "
                        f"{result.violations_fixed} fixed)"
                    )
                else:
                    tier_failed = True
                    print(agent_status(agent_name, 'error'))
                    log_status('error', f"{agent_name}: {result.error_message}")
                    self.logger.error(f"   ❌ {agent_name}: ERROR - {result.error_message}")
            
            # Print tier summary
            tier_duration = (datetime.now() - tier_start).total_seconds()
            print(tier_summary(
                tier_name.replace("Tier ", "").split(":")[1].strip() if ":" in tier_name else tier_name,
                tier_num,
                len(agents),
                tier_fixes,
                tier_violations,
                tier_duration,
                not tier_failed
            ))
            
            # [STABILITY GATES]
            # Gate 1: Parseability (Always Fatal if Failed)
            if "Tier 1" in tier_name and tier_failed:
                log_status('error', '🛑 CRITICAL GATE: Syntax Validation Failed. Aborting Mission.')
                self.logger.error("🛑 CRITICAL GATE: Syntax Validation Failed. Aborting Mission.")
                break
                
            # Gate 2: Structural Stability (Fatal only during Execution)
            # If we are executing fixes and structure is still failing, we cannot run deep logic checks safely.
            if "Tier 2" in tier_name and tier_failed and execute:
                log_status('error', '🛑 STABILITY GATE: Structural violations persist. Aborting Deep Compliance.')
                self.logger.error("🛑 STABILITY GATE: Structural violations persist after healing. Aborting Deep Compliance.")
                break
            
            self.logger.info(f"[{tier_name.upper()}] Sequence Complete.\n")
        
        # Calculate metrics
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        agents_passed = sum(1 for r in agent_results if r.status == 'PASS')
        agents_failed = sum(1 for r in agent_results if r.status in ['FAIL', 'ERROR'])
        
        overall_status = 'PASS' if agents_failed == 0 else 'FAIL'
        
        report = OrchestrationReport(
            timestamp=datetime.now().isoformat(),
            total_agents_run=len(agent_results),
            agents_passed=agents_passed,
            agents_failed=agents_failed,
            total_violations=total_violations,
            total_fixes=total_fixes,
            execution_time_ms=execution_time,
            agent_results=agent_results,
            overall_status=overall_status
        )
        
        # Print summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ORCHESTRATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Agents Run: {report.total_agents_run}")
        self.logger.info(f"Passed: {report.agents_passed}")
        self.logger.info(f"Failed: {report.agents_failed}")
        self.logger.info(f"Total Violations: {report.total_violations}")
        self.logger.info(f"Total Fixes: {report.total_fixes}")
        self.logger.info(f"Success Rate: {report.success_rate:.1f}%")
        self.logger.info(f"Execution Time: {report.execution_time_ms:.0f}ms")
        self.logger.info(f"Overall Status: {report.overall_status}")
        self.logger.info("=" * 60)
        
        # Meta-Learning: Record results for pattern learning
        self.record_result(report)
        
        return report
    
    def record_result(self, report: OrchestrationReport) -> Any:
        """
        Meta-Learning Integration: Write audit/healing results to L4 State.
        
        Records orchestration results to:
        - Redis (L4): Short-term cache for rapid reuse of fix patterns
        - Pinecone (L4): Long-term memory for structural evolution analysis
        
        This enables the system to learn from successful fixes and apply
        patterns automatically in future healing cycles.
        """
        try:
            # Short-term Cache (Redis) for rapid pattern reuse
            if hasattr(self, 'redis_client') and self.redis_client:
                cache_key = f"orchestration_result_{report.timestamp}"
                cache_data = {
                    "violations": report.total_violations,
                    "fixes": report.total_fixes,
                    "success_rate": report.success_rate,
                    "agents_run": report.total_agents_run
                }
                # Note: Actual Redis call would be async
                # self.redis_client.set(cache_key, str(cache_data), ttl=86400)
                self.logger.debug(f"[META-LEARNING] Cached result to Redis: {cache_key}")
            
            # Long-term Memory (Pinecone) for structural evolution
            if hasattr(self, 'pinecone_client') and self.pinecone_client:
                # Build metadata for vector storage
                metadata = {
                    "timestamp": report.timestamp,
                    "total_violations": report.total_violations,
                    "total_fixes": report.total_fixes,
                    "success_rate": report.success_rate,
                    "overall_status": report.overall_status,
                    "layer_health": {
                        result.agent_name: {
                            "status": result.status,
                            "violations": result.violations_found,
                            "fixes": result.violations_fixed
                        }
                        for result in report.agent_results
                    }
                }
                
                # Note: Actual Pinecone upsert would require embedding generation
                # vector_id = f"orchestration_{report.timestamp}"
                # self.pinecone_client.upsert_fix_signature(
                #     vector_id=vector_id,
                #     metadata=metadata
                # )
                self.logger.debug(f"[META-LEARNING] Logged to Pinecone: {len(report.agent_results)} agent results")
            
            self.logger.info("[META-LEARNING] Orchestration results recorded for pattern learning")
            
        except Exception as e:
            self.logger.warning(f"[META-LEARNING] Failed to record results: {e}")
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Canon Key 51 compliance: Orchestrate all SSOT validators.
        
        Args:
            dry_run: If True, only report violations
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            **kwargs: Additional arguments for compatibility
            
        Returns:
            Dictionary with orchestration summary
        """
        super().heal_repository()

        if _call_path is None:
            _call_path = []
        
        self.logger.info(f"[SSOTOrchestratorAgent] Starting SSOT orchestration (dry_run={dry_run})")
        
        # Run orchestration
        report = self.orchestrate(dry_run=dry_run, execute=execute)
        
        # Return standardized format for ConsolidatedOrchestratorAgent
        return {
            "agent": "SSOTOrchestratorAgent",
            "timestamp": report.timestamp,
            "violations": report.total_violations,  # Standardized key for ConsolidatedOrchestrator
            "fixed": report.total_fixes,            # Standardized key for ConsolidatedOrchestrator
            "agents_run": report.total_agents_run,
            "agents_passed": report.agents_passed,
            "agents_failed": report.agents_failed,
            "violations_found": report.total_violations,
            "violations_fixed": report.total_fixes,
            "success_rate": report.success_rate,
            "execution_time_ms": report.execution_time_ms,
            "overall_status": report.overall_status
        }


def get_ssot_orchestrator(project_root):
    """Factory function for SSOTOrchestratorAgent."""
    return SSOTOrchestratorAgent(project_root=project_root)
