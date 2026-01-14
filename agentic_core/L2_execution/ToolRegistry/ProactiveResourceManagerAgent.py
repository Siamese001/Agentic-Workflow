from __future__ import annotations
"""
Proactive Resource Manager - L2 Execution Enhancement

Monitors and predicts resource usage for healing operations.
Automatically adjusts healing budgets and prevents resource exhaustion.
"""
import asyncio
import logging
import os
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin
Logger: Any = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Tracks resource usage metrics."""
    timestamp: datetime
    healing_attempts: int
    success_rate: float
    avg_rounds_per_heal: float
    files_in_queue: int
    estimated_time_remaining: float
    budget_utilization: float

@dataclass
class ResourceThreshold:
    """Resource usage thresholds."""
    max_healing_per_file: int = 8
    global_healing_budget: int = 50
    max_concurrent_heals: int = 5
    budget_warning_threshold: float = 0.8
    budget_critical_threshold: float = 0.95
    min_success_rate: float = 0.3

class ProactiveResourceManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Manages healing resources proactively to prevent exhaustion.
    
    Features:
    - Real-time resource monitoring
    - Predictive budget allocation
    - Automatic scaling based on success rates
    - Priority-based healing queue
    - Resource exhaustion prevention
    """

    def __init__(self, thresholds: Optional[ResourceThreshold]=None) -> None:
        """Initialize the resource manager."""
        self.thresholds = thresholds or ResourceThreshold()
        self.file_healing_counts: Dict[str, int] = {}
        self.global_healing_count: int = 0
        self.active_healings: int = 0
        self.healing_queue: deque = deque()
        self.metrics_history: deque = deque(maxlen=100)
        self.success_history: deque = deque(maxlen=50)
        self.priority_weights: Dict[int, float] = self._initialize_priority_weights()
        self._last_adjustment: datetime = datetime.now()
        self.base_global_budget = self.thresholds.global_healing_budget
        self.current_global_budget = self.base_global_budget
        self.mutation_active = True
        self.mutation_cycle = 180
        self._mutation_task = None
        self.l1_learner = None
        Logger.info('Proactive Resource Manager initialized')

    def awaken(self, learner_instance: Any=None) -> Any:
        """L2: Wake with injected L1 wisdom"""
        self.l1_learner = learner_instance
        if self.mutation_active and (not self._mutation_task):
            self._mutation_task = asyncio.create_task(self.l1_guided_mutation_cycle())
            Logger.info('L2: Resource-aware mutation engine awakened with L1 guidance')

    def _initialize_priority_weights(self) -> Dict[int, float]:
        """Initialize priority weights for different Violation keys."""
        return {0: 1.0, 6: 1.0, 40: 0.9, 42: 0.8, 49: 0.9, 50: 0.95}

    def can_attempt_healing(self, file_path: str, violation_key: int) -> Tuple[bool, str]:
        """
        Check if healing can be attempted for a file.
        
        Args:
            file_path: Path to file
            violation_key: Canon key
        Returns:
            Tuple of (can_heal, reason)
        """
        if self.global_healing_count >= self.thresholds.global_healing_budget:
            return (False, f'Global healing budget exhausted ({self.global_healing_count}/{self.thresholds.global_healing_budget})')
        file_count: Any = self.file_healing_counts.get(file_path, 0)
        if file_count >= self.thresholds.max_healing_per_file:
            return (False, f'Per-file healing limit reached ({file_count}/{self.thresholds.max_healing_per_file})')
        if self.active_healings >= self.thresholds.max_concurrent_heals:
            return (False, f'Max concurrent healings reached ({self.active_healings}/{self.thresholds.max_concurrent_heals})')
        budget_utilization: Any = self.global_healing_count / self.thresholds.global_healing_budget
        if budget_utilization >= self.thresholds.budget_critical_threshold:
            priority: Any = self.priority_weights.get(violation_key, 0.5)
            if priority < 0.8:
                return (False, f'Budget critical ({budget_utilization:.1%}), only high-priority violations allowed')
        if len(self.success_history) >= 10:
            recent_success_rate: Any = sum(self.success_history) / len(self.success_history)
            if recent_success_rate < self.thresholds.min_success_rate:
                return (False, f'Success rate too low ({recent_success_rate:.1%}), pausing healing')
        return (True, 'OK')

    def record_healing_attempt(self, file_path: str, violation_key: int, success: bool, rounds_taken: int) -> Any:
        """
        Record a healing attempt.
        
        Args:
            file_path: Path to healed file
            violation_key: Canon key
            success: Whether healing succeeded
            rounds_taken: Number of rounds taken
        """
        self.file_healing_counts[file_path] = self.file_healing_counts.get(file_path, 0) + 1
        self.global_healing_count += 1
        self.success_history.append(1 if success else 0)
        self._record_metrics()
        if success:
            Logger.info(f'Healing success: {os.path.basename(file_path)} (Key {violation_key}, {rounds_taken} rounds)')
        else:
            Logger.warning(f'Healing failed: {os.path.basename(file_path)} (Key {violation_key})')
        self._check_and_adjust_thresholds()

    def start_healing(self, file_path: str) -> Any:
        """Mark a healing operation as started."""
        self.active_healings += 1
        Logger.debug(f'Active healings: {self.active_healings}')

    def end_healing(self, file_path: str) -> Any:
        """Mark a healing operation as ended."""
        self.active_healings = max(0, self.active_healings - 1)
        Logger.debug(f'Active healings: {self.active_healings}')

    def _record_metrics(self) -> Any:
        """Record current resource metrics."""
        success_rate = 0.0
        if self.success_history:
            success_rate = sum(self.success_history) / len(self.success_history)
        avg_rounds = 3.0
        budget_utilization = self.global_healing_count / self.thresholds.global_healing_budget
        metrics = ResourceMetrics(timestamp=datetime.now(), healing_attempts=self.global_healing_count, success_rate=success_rate, avg_rounds_per_heal=avg_rounds, files_in_queue=len(self.healing_queue), estimated_time_remaining=len(self.healing_queue) * avg_rounds * 2.0, budget_utilization=budget_utilization)
        self.metrics_history.append(metrics)

    def _check_and_adjust_thresholds(self) -> Any:
        """Automatically adjust thresholds based on performance."""
        if datetime.now() - self._last_adjustment < timedelta(minutes=5):
            return
        if len(self.success_history) < 20:
            return
        recent_success_rate = sum(self.success_history) / len(self.success_history)
        if recent_success_rate > 0.8:
            old_budget = self.thresholds.global_healing_budget
            self.thresholds.global_healing_budget = min(100, int(old_budget * 1.2))
            if self.thresholds.global_healing_budget != old_budget:
                Logger.info(f'Increased global budget: {old_budget} → {self.thresholds.global_healing_budget}')
        elif recent_success_rate < 0.4:
            old_budget = self.thresholds.global_healing_budget
            self.thresholds.global_healing_budget = max(20, int(old_budget * 0.8))
            if self.thresholds.global_healing_budget != old_budget:
                Logger.warning(f'Decreased global budget: {old_budget} → {self.thresholds.global_healing_budget}')
        self._last_adjustment = datetime.now()

    def get_priority_score(self, file_path: str, violation_key: int) -> float:
        """
        Calculate priority score for a healing Task.
        
        Args:
            file_path: Path to file
            violation_key: Canon key
            
        Returns:
            Priority score (higher = more important)
        """
        base_priority: Any = self.priority_weights.get(violation_key, 0.5)
        file_attempts: Any = self.file_healing_counts.get(file_path, 0)
        attempt_penalty: Any = 0.1 * file_attempts
        budget_utilization: Any = self.global_healing_count / self.thresholds.global_healing_budget
        urgency_boost: Any = 0.0
        if budget_utilization > 0.7:
            urgency_boost: Any = 0.2 if base_priority > 0.8 else -0.2
        return max(0.0, min(1.0, base_priority - attempt_penalty + urgency_boost))

    def add_to_queue(self, file_path: str, violation_key: int, violation_details: str) -> Any:
        """
        Add a healing Task to the priority queue.
        
        Args:
            file_path: Path to file
            violation_key: Canon key
            violation_details: Violation description
        """
        priority: Any = self.get_priority_score(file_path, violation_key)
        Task: Any = {'file_path': file_path, 'violation_key': violation_key, 'violation_details': violation_details, 'priority': priority, 'queued_at': datetime.now()}
        inserted: Any = False
        for i, existing_task in enumerate(self.healing_queue):
            if priority > existing_task['priority']:
                self.healing_queue.insert(i, Task)
                inserted: Any = True
                break
        if not inserted:
            self.healing_queue.append(Task)
        Logger.debug(f'Added to queue: {os.path.basename(file_path)} (Key {violation_key}, Priority {priority:.2f})')

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next healing Task from the queue."""
        while self.healing_queue:
            Task: Any = self.healing_queue.popleft()
            can_heal, reason = self.can_attempt_healing(Task['file_path'], Task['violation_key'])
            if can_heal:
                return Task
            else:
                Logger.debug(f'Skipping Task: {reason}')
        return None

    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status."""
        budget_utilization: Any = self.global_healing_count / self.thresholds.global_healing_budget
        status: Any = 'HEALTHY'
        if budget_utilization >= self.thresholds.budget_critical_threshold:
            status: Any = 'CRITICAL'
        elif budget_utilization >= self.thresholds.budget_warning_threshold:
            status: Any = 'WARNING'
        success_rate: Any = 0.0
        if self.success_history:
            success_rate: Any = sum(self.success_history) / len(self.success_history)
        return {'status': status, 'global_healing_count': self.global_healing_count, 'global_budget': self.thresholds.global_healing_budget, 'budget_utilization': budget_utilization, 'active_healings': self.active_healings, 'queue_length': len(self.healing_queue), 'success_rate': success_rate, 'files_with_attempts': len(self.file_healing_counts)}

    def reset_counters(self) -> Any:
        """Reset healing counters (for new validation runs)."""
        self.file_healing_counts.clear()
        self.global_healing_count = 0
        self.active_healings = 0
        self.healing_queue.clear()
        Logger.info('Resource counters reset')

    async def l1_guided_mutation_cycle(self) -> Any:
        """L2: Accept resource recommendations from L1 with confidence-based dampening"""
        Logger.info('L2: L1-guided mutation cycle active')
        while self.mutation_active:
            try:
                await asyncio.sleep(300)
                if len(self.success_history) >= 10:
                    success_rate: Any = sum(self.success_history) / len(self.success_history)
                    avg_rounds: Any = 2.0
                    old_budget: Any = self.current_global_budget
                    if success_rate > 0.85 and avg_rounds < 2:
                        new_budget: Any = min(self.base_global_budget * 2, self.current_global_budget + 10)
                    elif success_rate < 0.5:
                        safety_floor: Any = int(self.base_global_budget * 0.2)
                        new_budget: Any = max(safety_floor, self.current_global_budget - 15)
                    else:
                        new_budget: Any = self.current_global_budget
                    if new_budget != old_budget:
                        self.current_global_budget = new_budget
                        self.thresholds.global_healing_budget = new_budget
                        Logger.info(f'L2 MUTATION: Budget adjusted {old_budget} → {new_budget} (success_rate={success_rate:.1%})')
                if self.l1_learner:
                    try:
                        rec: Any = None
                        if rec and rec.get('confidence', 0) > 0.5:
                            if rec['mutation'] == 'increase_critical_budget':
                                increase: Any = rec.get('suggested_global_increase', 5)
                                old_budget: Any = self.current_global_budget
                                self.current_global_budget += increase
                                self.thresholds.global_healing_budget = self.current_global_budget
                                Logger.info(f"L2: Applied L1 Recommendation: +{increase} budget (confidence={rec['confidence']:.1%})")
                            elif rec['mutation'] == 'decrease_budget':
                                decrease: Any = rec.get('suggested_global_decrease', 5)
                                safety_floor: Any = int(self.base_global_budget * 0.2)
                                old_budget: Any = self.current_global_budget
                                self.current_global_budget = max(safety_floor, self.current_global_budget - decrease)
                                self.thresholds.global_healing_budget = self.current_global_budget
                                Logger.info(f"L2: Applied L1 Recommendation: -{decrease} budget (confidence={rec['confidence']:.1%})")
                    except Exception as e:
                        Logger.debug(f'L2: L1 guidance unavailable: {e}')
                await self.persist_mutation_state()
                Logger.debug('L2: L1-guided mutation cycle completed')
            except Exception as e:
                Logger.error(f'L2 Mutation cycle error: {e}')
                await asyncio.sleep(60)

    async def persist_mutation_state(self) -> Any:
        """L2: Atomic state persistence for resource policies"""
        import json
        import tempfile
        from pathlib import Path
        try:
            state_path: Any = Path('.canon_memory/resource_state.json')
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state: Any = {'current_global_budget': self.current_global_budget, 'base_global_budget': self.base_global_budget, 'mutation_active': self.mutation_active, 'last_updated': datetime.now().isoformat()}
            with tempfile.NamedTemporaryFile('w', delete=False, dir=state_path.parent, encoding='utf-8') as tf:
                json.dump(state, tf, indent=2)
                temp_name: Any = tf.name
            import os
            os.replace(temp_name, state_path)
            Logger.debug('L2: Resource state persisted atomically')
        except Exception as e:
            Logger.error(f'L2: Failed to persist resource state: {e}')

    def get_recommendations(self) -> List[str]:
        """Get resource management recommendations."""
        recommendations: Any = []
        status: Any = self.get_resource_status()
        if status['budget_utilization'] > 0.9:
            recommendations.append('CRITICAL: Healing budget nearly exhausted. Consider increasing budget or focusing on high-priority violations.')
        if status['success_rate'] < 0.4 and len(self.success_history) >= 10:
            recommendations.append('WARNING: Low healing success rate. Review healing strategies or reduce complexity of fixes.')
        if status['queue_length'] > 20:
            recommendations.append('INFO: Large healing queue. Consider parallel healing or increasing max_concurrent_heals.')
        if status['active_healings'] >= self.thresholds.max_concurrent_heals:
            recommendations.append('INFO: Max concurrent healings reached. Queue is processing at capacity.')
        return recommendations

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

def create_proactive_resource_manager(thresholds: Optional[ResourceThreshold]=None) -> ProactiveResourceManagerAgent:
    """Factory function to create proactive resource manager."""
    return ProactiveResourceManagerAgent(thresholds=thresholds)
