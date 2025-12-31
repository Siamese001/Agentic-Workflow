"""
HealingOrchestrator – Sovereign Agent (Phase 16 – Dec 30, 2025)
SSOT-compliant location: L0_maintenance/scripts/
Responsible for autonomous self-correction using diagnosed issues and healing strategies.
Pure orchestration with transactional safety – zero direct file mutation outside transaction manager.
"""

from typing import List, Dict, Any
from pathlib import Path
import logging


class HealingOrchestrator:
    """
    Sovereign healing engine orchestrator.
    Coordinates diagnosis, strategy selection, transactional application, and audit logging.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
            self.logger.warning("Healing strategies not available")

        try:
            from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
            self.transaction_cls = HealingTransaction
        except ImportError:
            self.transaction_cls = None
            self.logger.warning("HealingTransaction manager not available")

        try:
            from agentic_core.observability.healing_audit import log_healing_action
            self.log_healing_action = log_healing_action
        except ImportError:
            self.log_healing_action = None
            self.logger.warning("Healing audit logging not available")

    async def diagnose_and_propose_fixes(self, issues: List[Dict]) -> List[Dict]:
        """Run all strategies to diagnose and collect proposed fixes."""
        all_fixes = []
        for strategy in self.strategies:
            fixes = await strategy.diagnose(issues)
            if fixes:
                for fix in fixes:
                    fix["strategy"] = strategy.name
                all_fixes.extend(fixes)
                self.logger.info(f"{strategy.name} proposed {len(fixes)} fixes")
        return all_fixes

    async def apply_fixes_transactionally(self, fixes: List[Dict]) -> int:
        """Apply fixes with full transactional safety and audit trail."""
        if not fixes:
            return 0

        if self.transaction_cls is None or self.log_healing_action is None:
            self.logger.warning("Transactional healing unavailable – logging for manual review")
            for fix in sorted(fixes, key=lambda f: f.get("priority", 10)):
                self.logger.info(f"PROPOSED: {fix['action']} | {fix['reason']} | File: {fix.get('file', 'N/A')}")
            return 0

        tx = self.transaction_cls()
        fixes_applied = 0

        try:
            for fix in sorted(fixes, key=lambda f: f.get("priority", 10)):
                file_path = fix.get("file")
                if file_path and file_path != 'N/A':
                    path = Path(file_path)
                    if path.exists():
                        tx.backup(path)

                strategy = self.strategy_map.get(fix.get("strategy"))
                if not strategy:
                    self.logger.warning(f"Strategy '{fix.get('strategy')}' not found – skipping")
                    continue

                success = await strategy.apply(fix, ctx=None)
                self.log_healing_action(fix["action"], fix, success) if self.log_healing_action else None

                if success:
                    fixes_applied += 1

            tx.commit()
            self.logger.info(f"Healing Complete: {fixes_applied} fixes committed")
            return fixes_applied

        except Exception as e:
            tx.rollback()
            self.logger.error(f"Healing Aborted: {e} – All changes reverted")
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

        print(f"\n   [L0 HEALING] Initiating transactional healing for {len(fixes)} fixes...")
        await self.apply_fixes_transactionally(fixes)
