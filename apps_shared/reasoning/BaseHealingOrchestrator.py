"""BaseHealingOrchestrator — Shared meta-learning healing loop for LIC and RG domains.

Extracted from LicHealingOrchestrator and RgHealingOrchestrator (2026-03-11, P3-B).
Both app orchestrators subclass this and inherit:
  - ml_heal_with_learning_enhanced()
  - orchestrate_healing_cycle()
  - _apply_healing_strategy()
Domain-specific orchestrators override _collect_cycle_results_key() for stats keying.
"""
from __future__ import annotations
import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

@dataclass
class BaseHealingOrchestrator(SovereignBaseAgent):
    """Shared meta-learning healing orchestration skeleton.

    Subclasses must implement:
    - `heal(violation)` — domain-specific single-violation healer
    - `_cycle_results_key()` — string key for cycle pattern caching (e.g. "healing_cycle")

    Subclasses may override:
    - `_execute_healing(incident)` — if LIC-style incident dispatch is needed
    """
    cycle_results: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize healing orchestrator and register in knowledge graph."""
        super().__post_init__()
        self._register_in_knowledge_graph()

    def _register_in_knowledge_graph(self) -> None:
        """Register this orchestrator as an entity in the Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(agent_name=self.__class__.__name__, agent_type='HealingOrchestrator', observations=[f'HealingOrchestrator {self.__class__.__name__} initialized'])
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f'[{self.__class__.__name__}] KG registration skipped: {e}')

    def heal_repository(self, dry_run: bool=False, execute: bool=False, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Heal a single violation. Override in subclasses."""
        violation_type = violation.get('type', 'unknown')
        return {'status': 'skipped', 'details': f'{self.__class__.__name__} heal() not yet implemented for {violation_type}', 'artifacts': [], 'errors': []}

    def _cycle_results_key(self) -> str:
        """Return the pattern cache key prefix for this orchestrator's cycles."""
        return 'healing_cycle'

    def ml_heal_with_learning_enhanced(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Enhanced healing with full meta-learning integration.

        Uses guardrails for depth checking, pattern retrieval for strategy
        selection, and pattern storage for successful fixes.
        """
        violation_str = json.dumps(violation, sort_keys=True)
        violation_id = hashlib.sha256(violation_str.encode()).hexdigest()[:16]
        if not self.guardrails_check_healing_depth(violation_id):
            Logger.warning(f'[{self.__class__.__name__}] Healing depth limit reached for {violation_id}')
            return {'status': 'skipped', 'violation_id': violation_id, 'reason': 'healing_depth_limit_reached'}
        self.guardrails_increment_healing_depth(violation_id)
        try:
            # guardian: allow-magic-config
            similar_patterns = self.retrieve_healing_patterns(violation, top_k=3)
            strategy = None
            if similar_patterns:
                best_pattern = max(similar_patterns, key=lambda p: getattr(p, 'success_count', 0), default=None)
                if best_pattern:
                    strategy = getattr(best_pattern, 'healing_strategy', None)
                    Logger.info(f"[{self.__class__.__name__}] Using learned strategy from pattern with {getattr(best_pattern, 'success_count', 0)} successes")
            result = self._apply_healing_strategy(violation, strategy) if strategy else self.heal(violation)
            if result.get('status') == 'fixed':
                self.store_healing_pattern(violation, result)
                self.guardrails_reset_healing_depth(violation_id)
                Logger.info(f'[{self.__class__.__name__}] Healing successful, pattern stored')
            return {'status': result.get('status', 'error'), 'violation_id': violation_id, 'used_learned_strategy': strategy is not None}
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f'[{self.__class__.__name__}] Enhanced healing failed: {e}')
            return {'status': 'error', 'violation_id': violation_id, 'reason': str(e)}

    def _apply_healing_strategy(self, violation: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
        """Apply a learned healing strategy to a violation."""
        action = strategy.get('action', 'default')
        Logger.debug(f'[{self.__class__.__name__}] Applying strategy action: {action}')
        return self.heal(violation, strategy_hint=strategy)

    def orchestrate_healing_cycle(self, violations: list[dict[str, Any]]) -> dict[str, Any]:
        """Orchestrate a full healing cycle for multiple violations."""
        results: dict[str, Any] = {'total': len(violations), 'fixed': 0, 'skipped': 0, 'errors': 0, 'details': []}
        for violation in violations:
            result = self.ml_heal_with_learning_enhanced(violation)
            results['details'].append(result)
            if result['status'] == 'fixed':
                results['fixed'] += 1
            elif result['status'] == 'skipped':
                results['skipped'] += 1
            else:
                results['errors'] += 1
        if results['fixed'] > 0:
            cycle_pattern = {'total': results['total'], 'fixed': results['fixed'], 'success_rate': results['fixed'] / results['total']}
            self.cache_pattern_with_metadata(self._cycle_results_key(), f'cycle_{len(self.cycle_results)}', cycle_pattern)
            self.cycle_results.append(results)
        self._persist_healing_cycle(results)
        return results

    def _persist_healing_cycle(self, results: dict[str, Any]) -> None:
        """Persist healing cycle outcomes to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            total = results.get('total', 0)
            fixed = results.get('fixed', 0)
            errors = results.get('errors', 0)
            cycle_idx = len(self.cycle_results)
            obs = f'HealingCycle={cycle_idx} total={total} fixed={fixed} errors={errors} success_rate={fixed / total:.2f}' if total > 0 else f'HealingCycle={cycle_idx} total=0'
            bridge.add_observation(entity_name=self.__class__.__name__, observation=obs)
            if fixed > 0:
                bridge.create_relation(from_entity=self.__class__.__name__, to_entity='HealingCycle', relation_type='HEALED')
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f'[{self.__class__.__name__}] KG healing cycle persistence skipped: {e}')
        self._verify_dashboard_after_healing(results)

    def _verify_dashboard_after_healing(self, results: dict[str, Any]) -> None:
        """Trigger Playwright MCP dashboard verification after a healing cycle."""
        import asyncio
        fixed = results.get('fixed', 0)
        if fixed == 0:
            return
        try:
            from agentic_core.L6_observability.dashboards.verify_dashboard_e2e_playwright_util import mcp_verify_dashboard
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(asyncio.run, mcp_verify_dashboard())
                        # guardian: allow-magic-config
                        verification = future.result(timeout=30)
                else:
                    verification = loop.run_until_complete(mcp_verify_dashboard())
            # guardian: allow-silent-swallow
            except Exception:
                verification = {}
            if verification.get('success'):
                Logger.info(f'[{self.__class__.__name__}] Dashboard verification passed after healing')
            else:
                Logger.warning(f"[{self.__class__.__name__}] Dashboard verification flagged issues: {verification.get('errors', [])}")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f'[{self.__class__.__name__}] Dashboard verification skipped: {e}')
