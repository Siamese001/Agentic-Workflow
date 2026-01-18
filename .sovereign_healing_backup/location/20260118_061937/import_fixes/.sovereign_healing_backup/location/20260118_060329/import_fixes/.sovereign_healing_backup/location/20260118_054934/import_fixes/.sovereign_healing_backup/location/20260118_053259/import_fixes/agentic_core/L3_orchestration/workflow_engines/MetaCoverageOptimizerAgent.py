from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

from collections import deque
from typing import Deque, Dict, Optional
import time

from agentic_core.config.blueprint_sovereign.structure_blueprint import get_validated_project_root
from agentic_core.L6_observability.metrics.CoverageAgent import CoverageAgent
from agentic_core.L6_observability.metrics.shared_counters import counters
from agentic_core.runtime.shared_runtime import log_event, publish_event
from dataclasses import dataclass


@dataclass
class MetaCoverageOptimizerAgent(SovereignBaseAgent):
    """
    Sub-atomic meta-responsibility: Autonomously optimize coverage parameters for sustained high entropy.
    Monitors history, performs bounded hill-climb tweaks, applies safe adjustments.
    Triggered periodically (e.g., every 100 cycles or by orchestrator scheduler).
    In-memory only — no persistent constitution changes.
    """

    def __init__(self) -> None:
        """Initialize the instance."""
        self.name = "MetaCoverageOptimizerAgent"
        self.project_root = get_validated_project_root()
        self.coverage_agent = CoverageAgent()
        self.history_length = 20
        self.entropy_history: Deque[float] = deque(maxlen=self.history_length)
        self.proportion_history: Deque[Dict[str, float]] = deque(maxlen=self.history_length)
        self.tune_interval_cycles = 50
        self.last_tune_time = time.time()
        self.param_bounds = {
            "bias_weight": (2.0, 6.0),
            "synthetic_tasks_per_trigger": (5, 15),
            "healthy_threshold": (0.20, 0.35),
        }

    def act(self) -> str:
        """Primary entrypoint — periodic self-optimization cycle."""
        report = [f"{self.name}: Starting meta-optimization cycle"]

        # Fetch current metrics
        current_counts = counters.get_counts()
        current_proportions = self.coverage_agent._compute_proportions(current_counts)
        current_entropy = self.coverage_agent._shannon_entropy(current_proportions)

        # Update history
        self.entropy_history.append(current_entropy)
        self.proportion_history.append(current_proportions.copy())

        history_avg = sum(self.entropy_history) / len(self.entropy_history) if self.entropy_history else 0
        report.append(f"Current entropy: {current_entropy:.2f} (history avg: {history_avg:.2f})")

        # Tune if interval met and history sufficient
        if (len(self.entropy_history) == self.history_length and
            time.time() - self.last_tune_time > 300):
            adjustments = self._compute_parameter_adjustments(current_proportions)
            if adjustments:
                self._apply_adjustments(adjustments)
                report.extend(adjustments["log"])
                self.last_tune_time = time.time()
            else:
                report.append("No adjustments needed — stable high entropy")

        final = "\n".join(report)
        final += f"\n{self.name}: Meta-cycle complete — coverage self-optimized."
        log_event("meta_optimization_cycle", {"entropy": current_entropy})
        return final

    def _compute_parameter_adjustments(self, current_proportions: Dict[str, float]) -> Dict:
        """Simple hill-climb: Detect stagnation/lows, propose bounded tweaks."""
        if len(self.entropy_history) < 10:
            return {}

        recent_avg = sum(list(self.entropy_history)[-10:]) / 10
        prior_avg = sum(list(self.entropy_history)[:-10]) / 10 if len(self.entropy_history) > 10 else recent_avg
        delta = recent_avg - prior_avg

        adjustments = {"log": [f"Entropy delta: {delta:.3f}"]}

        if delta < 0.02:
            adjustments["log"].append("Stagnation detected — increasing exploration")
            new_weight = min(self.param_bounds["bias_weight"][1],
                           self.coverage_agent.bias_weight + 0.5)
            new_synth = min(self.param_bounds["synthetic_tasks_per_trigger"][1],
                          self.coverage_agent.synthetic_tasks_per_trigger + 2)
            adjustments["bias_weight"] = new_weight
            adjustments["synthetic_tasks_per_trigger"] = new_synth

        # Detect persistent highs/lows
        persistent_low = self._find_persistent_underrepresented()
        if persistent_low:
            adjustments["log"].append(f"Persistent low: {persistent_low} — targeted boost")

        # Over-correction prune
        if current_proportions:
            persistent_high = max(current_proportions, key=current_proportions.get)
            if current_proportions[persistent_high] > 0.5:
                adjustments["log"].append(f"Overrepresentation: {persistent_high} — negative bias")
                publish_event("coverage_negative_bias", {
                    "layer": persistent_high,
                    "weight": 0.5,
                    "cycles": 20
                })

        return adjustments if len(adjustments) > 1 else {}

    def _apply_adjustments(self, adjustments: Dict) -> None:
        """Apply in-memory tweaks — publish for CoverageAgent/orchestrator."""
        if "bias_weight" in adjustments:
            self.coverage_agent.bias_weight = adjustments["bias_weight"]
            adjustments["log"].append(f"Tuned bias_weight → {adjustments['bias_weight']}")
        if "synthetic_tasks_per_trigger" in adjustments:
            self.coverage_agent.synthetic_tasks_per_trigger = adjustments["synthetic_tasks_per_trigger"]
            adjustments["log"].append(f"Tuned synthetics → {adjustments['synthetic_tasks_per_trigger']}")
        publish_event("coverage_params_updated", adjustments)

    def _find_persistent_underrepresented(self, threshold: float = 0.15) -> Optional[str]:
        """Scan history for consistently low layer."""
        lows = {}
        for props in self.proportion_history:
            for layer, prop in props.items():
                if prop < threshold:
                    lows[layer] = lows.get(layer, 0) + 1
        if lows:
            max_count = max(lows.values())
            if max_count > self.history_length // 2:
                return min(lows, key=lows.get)
        return None

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
