"""Shim - re-exports from agentic_core.utils.workflow_engines.policies for backward compatibility."""

try:
    from agentic_core.utils.workflow_engines.policies import *  # noqa: F401,F403
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "evaluation.chunking.policies requires agentic_core.utils.workflow_engines.policies "
        "to be importable in this environment."
    ) from exc
