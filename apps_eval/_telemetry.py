"""Resilient telemetry shim for standalone apps_eval usage."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable


class LayerSegment(StrEnum):
    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"
    L5_POLICY = "L5_POLICY"
    L6_OBSERVABILITY = "L6_OBSERVABILITY"


def _noop(*args: Any, **kwargs: Any) -> None:
    return None


def __getattr__(name: str) -> Callable[..., None]:
    if name.startswith("_emit_") or name.startswith("emit_"):
        return _noop
    raise AttributeError(name)
