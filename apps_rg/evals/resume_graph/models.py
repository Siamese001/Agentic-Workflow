"""Data models and shared evaluation errors."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


class EvaluationDataError(ValueError):
    """Raised when evidence cannot support a valid evaluation."""


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


@dataclass(frozen=True)
class IsotonicModel:
    """A deterministic piecewise-linear representation of a PAV fit."""

    x_values: tuple[float, ...]
    y_values: tuple[float, ...]

    def predict_one(self, score: float) -> float:
        if not _is_number(score):
            raise EvaluationDataError("proof score must be finite")
        value = float(score)
        if value <= self.x_values[0]:
            return self.y_values[0]
        if value >= self.x_values[-1]:
            return self.y_values[-1]
        for index in range(1, len(self.x_values)):
            right_x = self.x_values[index]
            if value <= right_x:
                left_x = self.x_values[index - 1]
                left_y = self.y_values[index - 1]
                right_y = self.y_values[index]
                portion = (value - left_x) / (right_x - left_x)
                return left_y + portion * (right_y - left_y)
        raise AssertionError("unreachable isotonic interpolation state")

    def predict(self, scores: Sequence[float]) -> tuple[float, ...]:
        return tuple(self.predict_one(score) for score in scores)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "method": "deterministic_isotonic_pav_v1",
            "x_values": list(self.x_values),
            "y_values": list(self.y_values),
        }
