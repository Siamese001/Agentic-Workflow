"""RG healing orchestrator — subclasses ``BaseHealingOrchestrator``."""

from dataclasses import dataclass

from apps_shared.reasoning.BaseHealingOrchestrator import BaseHealingOrchestrator


@dataclass
class RgHealingOrchestrator(BaseHealingOrchestrator):
    """Self-healing loop façade for RG (meta-learning hooks in base)."""


__all__ = ["RgHealingOrchestrator"]
