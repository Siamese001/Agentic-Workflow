"""Integrations package for apps_research."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "ExecutionAdapter": "apps_research.integrations.execution_adapter",
    "ExecutionRequest": "apps_research.integrations.execution_adapter",
    "GovernedExecutionSeam": "apps_research.integrations.execution_adapter",
    "GovernedRunRecord": "apps_research.integrations.execution_adapter",
    "ObservabilityAdapter": "apps_research.integrations.observability_adapter",
    "GovernedResearchRun": "apps_research.integrations.governed_research_run",
    "GovernedE2ERunRecord": "apps_research.integrations.governed_research_run",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module 'apps_research.integrations' has no attribute {name!r}")
    module = import_module(module_path)
    return getattr(module, name)
