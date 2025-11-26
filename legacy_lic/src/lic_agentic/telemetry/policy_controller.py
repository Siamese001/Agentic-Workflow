"""Telemetry policy controller for adaptive tuning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


@dataclass(frozen=True)
class PolicyUpdate:
    """Return value describing the latest policy adjustments."""

    budget_multiplier: float
    temperature_cap: float
    tot_branches: int
    tool_weights: Dict[str, float]


class PolicyController:
    """Maintain bounded policy parameters using telemetry feedback."""

    TARGET_LATENCY_MS = 3500
    TARGET_PASS_RATE = 0.85

    def __init__(self) -> None:
        self.budget_multiplier = 1.0
        self.temperature_cap = 0.5
        self.tot_branches = 3
        self.tool_weights: Dict[str, float] = {}
        self._latency_error_integral = 0.0
        self._registered_quarantine: Dict[str, bool] = {}

    def register_tool(self, tool_id: str, *, quarantined: bool = False) -> None:
        if tool_id not in self.tool_weights:
            self.tool_weights[tool_id] = 1.0
        self._registered_quarantine[tool_id] = quarantined

    def promote_tool(self, tool_id: str) -> None:
        if tool_id in self._registered_quarantine:
            self._registered_quarantine[tool_id] = False

    def set_quarantine(self, tool_id: str) -> None:
        if tool_id in self._registered_quarantine:
            self._registered_quarantine[tool_id] = True

    def quarantine_status(self, tool_id: str) -> bool:
        return self._registered_quarantine.get(tool_id, False)

    def update(self, *, latency_p95_ms: int, qa_pass_rate: float, token_drift: float = 0.0, tool_success_rates: Mapping[str, float] | None = None) -> PolicyUpdate:
        """Update policy settings based on telemetry samples."""

        error = self.TARGET_LATENCY_MS - max(latency_p95_ms, 0)
        self._latency_error_integral = _clamp(
            self._latency_error_integral + error * 0.001,
            -0.5,
            0.5,
        )

        if latency_p95_ms > self.TARGET_LATENCY_MS:
            penalty = 0.05 + max(0.0, -self._latency_error_integral)
            self.budget_multiplier -= penalty
        elif latency_p95_ms < self.TARGET_LATENCY_MS * 0.75:
            boost = 0.04 + max(0.0, self._latency_error_integral)
            self.budget_multiplier += boost

        self.budget_multiplier = _clamp(self.budget_multiplier, 0.7, 1.3)

        if qa_pass_rate < self.TARGET_PASS_RATE:
            self.temperature_cap -= 0.05
            self.tot_branches -= 1
        elif qa_pass_rate > 0.92:
            self.temperature_cap += 0.03
            if self.tot_branches < 4:
                self.tot_branches += 1

        if token_drift > 0.1:
            self.tot_branches -= 1

        self.temperature_cap = _clamp(self.temperature_cap, 0.2, 0.7)
        self.tot_branches = int(_clamp(float(self.tot_branches), 1, 4))

        if tool_success_rates:
            for tool_id, success in tool_success_rates.items():
                if tool_id not in self.tool_weights:
                    self.tool_weights[tool_id] = 1.0
                adjustment = 1 + _clamp(success - self.TARGET_PASS_RATE, -0.1, 0.1)
                self.tool_weights[tool_id] = _clamp(
                    self.tool_weights[tool_id] * adjustment,
                    0.1,
                    3.0,
                )

        for tool_id, quarantined in list(self._registered_quarantine.items()):
            if quarantined:
                self.tool_weights[tool_id] = _clamp(self.tool_weights[tool_id], 0.1, 0.6)
            else:
                self.tool_weights[tool_id] = _clamp(self.tool_weights[tool_id], 0.1, 3.0)

        return PolicyUpdate(
            budget_multiplier=self.budget_multiplier,
            temperature_cap=self.temperature_cap,
            tot_branches=self.tot_branches,
            tool_weights=dict(self.tool_weights),
        )
