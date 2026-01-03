import numpy as np
import requests
from typing import Dict, Optional

# Use the canonical base for metric-related agents (observed pattern in MetricsAgent/BenchmarkingAgent)
# If no specific base exists, fall back to a lightweight object; adjust if your MetricsAgent inherits something specific
class CoverageAgent:
    def __init__(
        self,
        layers: list[str] = None,
        threshold_entropy: float = 2.4,  # Tune after baseline: log2(12) ≈ 3.58 max for ~12 major territories
        dashboard_api_url: str = "http://localhost:8000/api/metrics",  # Match your running dashboard backend
        intervention_mode: str = "report",  # "report" | "bias_routing" | "inject_tasks"
    ):
        self.name = "CoverageAgent"
        self.layers = layers or [
            "L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_state", "L5_safety", "config", "schemas", "prompt_governance",
            "observability", "utils", "apps_rg", "apps_lic", "apps_shared"
        ]  # SSOT-derived major territories from blueprint
        self.threshold_entropy = threshold_entropy
        self.dashboard_api_url = dashboard_api_url
        self.intervention_mode = intervention_mode

    def _fetch_metrics(self) -> Optional[Dict[str, int]]:
        """Pull layer activation counts from dashboard backend."""
        try:
            response = requests.get(self.dashboard_api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Expected format example: {"layer_counts": {"L3_orchestration": 320, "apps_rg": 180, ...}}
            return data.get("layer_counts", {})
        except Exception as e:
            print(f"[{self.name}] Metrics fetch failed: {e}")
            return None

    def _compute_proportions(self, counts: Dict[str, int]) -> Dict[str, float]:
        total = sum(counts.values())
        if total == 0:
            return {layer: 0.0 for layer in self.layers}
        return {layer: counts.get(layer, 0) / total for layer in self.layers}

    def _shannon_entropy(self, proportions: Dict[str, float]) -> float:
        props = np.array([p for p in proportions.values() if p > 0])
        if len(props) == 0:
            return 0.0
        return float(-np.sum(props * np.log2(props)))  # Base-2 for interpretability

    def act(self) -> str:
        """Primary actuation method — call periodically from orchestrator/metrics coordinator."""
        counts = self._fetch_metrics()
        if not counts:
            return f"{self.name}: No metrics available."

        proportions = self._compute_proportions(counts)
        entropy = self._shannon_entropy(proportions)

        report = (
            f"{self.name}: Current entropy = {entropy:.2f} / {np.log2(len(self.layers)):.2f} "
            f"(threshold {self.threshold_entropy:.2f}). "
            f"Proportions: { {k: f'{v:.1%}' for k, v in proportions.items() if v > 0} }"
        )

        if entropy < self.threshold_entropy:
            underrepresented = min(proportions, key=proportions.get)
            warning = (
                f"IMBALANCE DETECTED — Underrepresented: {underrepresented} "
                f"({proportions[underrepresented]:.1%}). Recommend corrective action."
            )
            report += " " + warning

            # Optional intervention hooks (extend based on your event/system)
            if self.intervention_mode == "bias_routing":
                # Example: publish to shared state / event bus for orchestrator to bias next routing
                self._publish_bias(underrepresented)
            elif self.intervention_mode == "inject_tasks":
                self._inject_synthetic_task(underrepresented)

            # Always log for compliance/audit trail
            self._log_violation(entropy, underrepresented)
        else:
            report += " Coverage balanced."

        return report

    # === Extension points (implement according to your shared runtime) ===
    def _publish_bias(self, layer: str):
        # Placeholder — integrate with your orchestrator's routing bias mechanism
        pass

    def _inject_synthetic_task(self, layer: str):
        # Placeholder — queue a no-op task that forces activation of the layer
        pass

    def _log_violation(self, entropy: float, layer: str):
        # Placeholder — append to compliance ledger or emit telemetry event
        pass
