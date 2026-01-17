from __future__ import annotations
"""
RgHealingOrchestratorAgent – Sovereign Agent (Phase 16 – Dec 30, 2025)
SSOT-compliant location: L0_maintenance/scripts/
Responsible for autonomous self-correction using diagnosed issues and healing strategies.
Pure orchestration with transactional safety – zero direct file mutation outside transaction manager.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# PHASE 2.1: L0 Structural Standardization
from agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent

# Sovereign Hardening Mixins – Phase 33
from agentic_core.patterns.agent_roles.autonomy_mixin import AutonomyMixin
from agentic_core.patterns.agent_roles.adaptive_execution_mixin import AdaptiveExecutionMixin
from agentic_core.patterns.agent_roles.experience_buffer import ExperienceBuffer
from agentic_core.patterns.agent_roles.self_diagnosis_mixin import SelfDiagnosisMixin


class RgHealingOrchestratorAgent(L0MaintenanceBaseAgent, AutonomyMixin,
    AdaptiveExecutionMixin,
    SelfDiagnosisMixin,):
    """
    Sovereign healing engine orchestrator.
    Coordinates diagnosis, strategy selection, transactional application, and audit logging.
    
    Inherits from L0MaintenanceBaseAgent: HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin

    Now hardened with:
      - Proactive initiation (AutonomyMixin)
      - Adaptive execution modes (AdaptiveExecutionMixin)
      - Persistent learning from outcomes (ExperienceBuffer)
      - Self-health monitoring (SelfDiagnosisMixin)
    """

    def __init__(self) -> None:
        self.Logger = logging.getLogger(__name__)

        # === Hardening Initialization ===
        super().__init__()  # Required for cooperative multiple inheritance

        # Experience Buffer for learning
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        self.experience_buffer = ExperienceBuffer(
            path=log_dir / "healing_experience.jsonl",
            max_entries=2000,
        )

        # Mandatory components for self-diagnosis
        self.MANDATORY_COMPONENTS = [
            "strategies",
            "transaction_cls",
            "log_healing_action",
            "experience_buffer",
        ]

        # Load healing infrastructure with graceful degradation
        self._load_healing_components()

    def _load_healing_components(self):
        """Load strategies and transaction manager."""
        try:
            from agentic_core.L0_maintenance.P1_core.healing_strategies import (
                HEALING_STRATEGIES,
                get_strategies_by_priority,
            )
            self.strategies = get_strategies_by_priority()
            self.strategy_map = {s.name: s for s in HEALING_STRATEGIES}
        except ImportError:
            self.strategies = []
            self.strategy_map = {}
            self.Logger.warning("Healing strategies not available")

        try:
            from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
            self.transaction_cls = HealingTransaction
        except ImportError:
            self.transaction_cls = None
            self.Logger.warning("HealingTransaction manager not available")

        try:
            from agentic_core.L6_observability.healing_audit import log_healing_action
            self.log_healing_action = log_healing_action
        except ImportError:
            self.log_healing_action = None
            self.Logger.warning("Healing audit logging not available")

    # === AutonomyMixin Override ===
    async def _detect_action_opportunity(self) -> Optional[Dict[str, Any]]:
        """Proactively detect when healing is needed."""
        # Simple trigger: sovereignty health degradation
        try:
            from agentic_core.L0_maintenance.scripts.metrics_witness import MetricsWitness
            witness = MetricsWitness(Path("."))
            structural_score, _ = witness.calculate_structural_ssot_score()
            healing_score, healing_issues = witness.calculate_healing_resilience_score()

            current_health = (structural_score + healing_score) / 2

            if current_health < 95:
                return {
                    "reason": "sovereignty_degradation_detected",
                    "current_health": current_health,
                    "trigger": "proactive_health_check",
                }
        except Exception as e:
            self.Logger.debug(f"Proactive check failed: {e}")

        return None

    # === AdaptiveExecutionMixin Overrides ===
    async def _execute_conservative(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.Logger.info("Conservative mode: limiting to high-priority fixes only")
        # Filter fixes to priority >= 8
        high_priority = [f for f in context.get("fixes", []) if f.get("priority", 5) >= 8]
        return await self._execute_standard(ctx, fixes=high_priority, **context)

    async def _execute_minimal(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.Logger.warning("Minimal mode: standing by to preserve resources")
        return {
            "mode": "minimal",
            "action": "standby",
            "reason": "high_system_load_or_degradation"
        }

    async def _execute_standard(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        """Standard execution mode - full healing cycle."""
        issues = context.get("issues", [])
        fixes = context.get("fixes", [])
        
        if not fixes and issues:
            fixes = await self.diagnose_and_propose_fixes(issues)
        
        if fixes:
            return await self.apply_fixes_transactionally(fixes)
        return 0

    def _enrich_fix_with_prediction(self, fix: Dict, strategy_name: str) -> Dict:
        """Enrich a fix with prediction data and strategy info.
        
        Args:
            fix: The fix dictionary to enrich.
            strategy_name: Name of the strategy that proposed this fix.
            
        Returns:
            Enriched fix dictionary.
        """
        fix["strategy"] = strategy_name
        prob = self.experience_buffer.predict_success_probability(
            action=fix.get("action", "unknown"),
            target=str(fix.get("file", "unknown"))
        )
        fix["predicted_success"] = prob
        fix["priority"] = fix.get("priority", 5) + (2 if prob > 0.8 else 0)
        return fix

    async def diagnose_and_propose_fixes(self, issues: List[Dict]) -> List[Dict]:
        """Run all strategies to diagnose and collect proposed fixes.
        
        Args:
            issues: List of issue dictionaries to diagnose.
            
        Returns:
            List of proposed fix dictionaries.
        """
        all_fixes = []
        for strategy in self.strategies:
            fixes = await strategy.diagnose(issues)
            if not fixes:
                continue
            enriched = [self._enrich_fix_with_prediction(f, strategy.name) for f in fixes]
            all_fixes.extend(enriched)
            self.Logger.info(f"{strategy.name} proposed {len(fixes)} fixes")
        return all_fixes

    def _record_fix_attempt(self, fix: Dict) -> None:
        """Record a fix attempt to the experience buffer."""
        self.experience_buffer.record({
            "action": fix.get("action"),
            "target": str(fix.get("file")),
            "predicted_success": fix.get("predicted_success", 0.5),
            "attempted": True,
        })

    def _record_fix_outcome(self, fix: Dict, success: bool) -> None:
        """Record a fix outcome to the experience buffer."""
        self.experience_buffer.record({
            "action": fix.get("action"),
            "target": str(fix.get("file")),
            "success": success,
            "strategy": fix.get("strategy"),
            "predicted_success": fix.get("predicted_success", 0.5),
        })

    def _log_proposed_fixes(self, fixes: List[Dict]) -> None:
        """Log proposed fixes when transactional healing is unavailable."""
        self.Logger.warning("Transactional healing unavailable – logging for manual review")
        for fix in sorted(fixes, key=lambda f: f.get("priority", 10)):
            self.Logger.info(f"PROPOSED: {fix['action']} | {fix['reason']} | File: {fix.get('file', 'N/A')}")

    async def _apply_single_fix(self, fix: Dict, tx: Any) -> bool:
        """Apply a single fix with backup and logging.
        
        Returns:
            True if fix was successful.
        """
        file_path = fix.get("file")
        if file_path and file_path != 'N/A':
            path = Path(file_path)
            if path.exists():
                tx.backup(path)

        strategy = self.strategy_map.get(fix.get("strategy"))
        if not strategy:
            self.Logger.warning(f"Strategy '{fix.get('strategy')}' not found – skipping")
            return False

        success = await strategy.apply(fix, ctx=None)
        if self.log_healing_action:
            self.log_healing_action(fix["action"], fix, success)
        self._record_fix_outcome(fix, success)
        return success

    async def apply_fixes_transactionally(self, fixes: List[Dict]) -> int:
        """Apply fixes with full transactional safety and audit trail.
        
        Args:
            fixes: List of fix dictionaries to apply.
            
        Returns:
            Number of fixes successfully applied.
        """
        if not fixes:
            return 0

        for fix in fixes:
            self._record_fix_attempt(fix)

        if self.transaction_cls is None or self.log_healing_action is None:
            self._log_proposed_fixes(fixes)
            return 0

        tx = self.transaction_cls()
        fixes_applied = 0

        try:
            for fix in sorted(fixes, key=lambda f: f.get("priority", 10)):
                if await self._apply_single_fix(fix, tx):
                    fixes_applied += 1

            tx.commit()
            self.Logger.info(f"Healing Complete: {fixes_applied} fixes committed")
            return fixes_applied

        except Exception as e:
            tx.rollback()
            self.Logger.error(f"Healing Aborted: {e} – All changes reverted")
            return fixes_applied

    async def execute_self_correction(self, issues: List[Dict]) -> None:
        """Full sovereign healing cycle."""
        if not issues:
            print("   [L0 HEALING] No structured violations detected for healing.")
            return

        print(f"   [L0 HEALING] Analyzing {len(issues)} violations...")

        fixes = await self.diagnose_and_propose_fixes(issues)
        if not fixes:
            print("   [L0 HEALING] No automated fixes available for current violations")
            return

        print(f"\nfrom agentic_core.utils.mixins import SubatomicTestingMixin\n   [L0 HEALING] Initiating transactional healing for {len(fixes)} fixes...")
        await self.apply_fixes_transactionally(fixes)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L0 maintenance agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L0 maintenance - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
