"""Synthetic safety simulator."""

import random

from simulations.models.safety_simulation import (
    SafetySimMetrics,
    SafetySimRequest,
    SafetySimResult,
)
from simulations.utils import model_to_payload


class SafetySimulator:
    """Simulates safety assessments."""

    async def run(self, request: SafetySimRequest) -> SafetySimResult:
        base_risk = 0.2 if len(request.text) < 100 else 0.4
        pii_risk = round(min(1.0, base_risk + random.uniform(0.0, 0.4)), 3)
        injection_risk = round(min(1.0, 0.1 + random.uniform(0.0, 0.5)), 3)
        bias_risk = round(max(0.0, 0.05 + random.uniform(0.0, 0.4)), 3)
        metrics = SafetySimMetrics(
            pii_risk=pii_risk,
            injection_risk=injection_risk,
            bias_risk=bias_risk,
        )
        snippet = request.text[:100]
        return SafetySimResult(
            simulation_id=request.simulation_id,
            success=True,
            metrics=model_to_payload(metrics),
            details={"text_snippet": snippet},
        )
